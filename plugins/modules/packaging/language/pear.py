#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Afterburn <https://github.com/afterburn>
# Copyright (c) 2013, Aaron Bull Schaefer <aaron@elasticdog.com>
# Copyright (c) 2015, Jonathan Lestrelin <jonathan.lestrelin@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pear
short_description: Manage pear/pecl packages
description:
    - Manage PHP packages with the pear package manager.
author:
    - Jonathan Lestrelin (@jle64) <jonathan.lestrelin@gmail.com>
options:
    name:
        type: str
        description:
            - Name of the package to install, upgrade, or remove.
        required: true
        aliases: [pkg]
    state:
        type: str
        description:
            - Desired state of the package.
        default: "present"
        choices: ["present", "installed", "latest", "absent", "removed"]
    executable:
        type: path
        description:
            - Path to the pear executable.
    prompts:
        description:
            - List of regular expressions that can be used to detect prompts during pear package installation to answer the expected question.
            - Prompts will be processed in the same order as the packages list.
            - You can optionnally specify an answer to any question in the list.
            - If no answer is provided, the list item will only contain the regular expression.
            - "To specify an answer, the item will be a dict with the regular expression as key and the answer as value C(my_regular_expression: 'an_answer')."
            - You can provide a list containing items with or without answer.
            - A prompt list can be shorter or longer than the packages list but will issue a warning.
            - If you want to specify that a package will not need prompts in the middle of a list,  C(null).
        type: list
        elements: raw
        version_added: 0.2.0
'''

EXAMPLES = r'''
- name: Install pear package
  community.general.pear:
    name: Net_URL2
    state: present

- name: Install pecl package
  community.general.pear:
    name: pecl/json_post
    state: present

- name: Install pecl package with expected prompt
  community.general.pear:
    name: pecl/apcu
    state: present
    prompts:
        - (.*)Enable internal debugging in APCu \[no\]

- name: Install pecl package with expected prompt and an answer
  community.general.pear:
    name: pecl/apcu
    state: present
    prompts:
        - (.*)Enable internal debugging in APCu \[no\]: "yes"

- name: Install multiple pear/pecl packages at once with prompts.
    Prompts will be processed on the same order as the packages order.
    If there is more prompts than packages, packages without prompts will be installed without any prompt expected.
    If there is more packages than prompts, additionnal prompts will be ignored.
  community.general.pear:
    name: pecl/gnupg, pecl/apcu
    state: present
    prompts:
      - I am a test prompt because gnupg doesnt asks anything
      - (.*)Enable internal debugging in APCu \[no\]: "yes"

- name: Install multiple pear/pecl packages at once skipping the first prompt.
    Prompts will be processed on the same order as the packages order.
    If there is more prompts than packages, packages without prompts will be installed without any prompt expected.
    If there is more packages than prompts, additionnal prompts will be ignored.
  community.general.pear:
    name: pecl/gnupg, pecl/apcu
    state: present
    prompts:
      - null
      - (.*)Enable internal debugging in APCu \[no\]: "yes"

- name: Upgrade package
  community.general.pear:
    name: Net_URL2
    state: latest

- name: Remove packages
  community.general.pear:
    name: Net_URL2,pecl/json_post
    state: absent
'''

import os

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.basic import AnsibleModule


def get_local_version(pear_output):
    """Take pear remoteinfo output and get the installed version"""
    lines = pear_output.split('\n')
    for line in lines:
        if 'Installed ' in line:
            installed = line.rsplit(None, 1)[-1].strip()
            if installed == '-':
                continue
            return installed
    return None


def _get_pear_path(module):
    if module.params['executable'] and os.path.isfile(module.params['executable']):
        result = module.params['executable']
    else:
        result = module.get_bin_path('pear', True, [module.params['executable']])
    return result


def get_repository_version(pear_output):
    """Take pear remote-info output and get the latest version"""
    lines = pear_output.split('\n')
    for line in lines:
        if 'Latest ' in line:
            return line.rsplit(None, 1)[-1].strip()
    return None


def query_package(module, name, state="present"):
    """Query the package status in both the local system and the repository.
    Returns a boolean to indicate if the package is installed,
    and a second boolean to indicate if the package is up-to-date."""
    if state == "present":
        lcmd = "%s info %s" % (_get_pear_path(module), name)
        lrc, lstdout, lstderr = module.run_command(lcmd, check_rc=False)
        if lrc != 0:
            # package is not installed locally
            return False, False

        rcmd = "%s remote-info %s" % (_get_pear_path(module), name)
        rrc, rstdout, rstderr = module.run_command(rcmd, check_rc=False)

        # get the version installed locally (if any)
        lversion = get_local_version(rstdout)

        # get the version in the repository
        rversion = get_repository_version(rstdout)

        if rrc == 0:
            # Return True to indicate that the package is installed locally,
            # and the result of the version number comparison
            # to determine if the package is up-to-date.
            return True, (lversion == rversion)

        return False, False


def remove_packages(module, packages):
    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        installed, updated = query_package(module, package)
        if not installed:
            continue

        cmd = "%s uninstall %s" % (_get_pear_path(module), package)
        rc, stdout, stderr = module.run_command(cmd, check_rc=False)

        if rc != 0:
            module.fail_json(msg="failed to remove %s: %s" % (package, to_text(stdout + stderr)))

        remove_c += 1

    if remove_c > 0:

        module.exit_json(changed=True, msg="removed %s package(s)" % remove_c)

    module.exit_json(changed=False, msg="package(s) already absent")


def install_packages(module, state, packages, prompts):
    install_c = 0
    has_prompt = bool(prompts)
    default_stdin = "\n"

    if has_prompt:
        nb_prompts = len(prompts)
        nb_packages = len(packages)

        if nb_prompts > 0 and (nb_prompts != nb_packages):
            if nb_prompts > nb_packages:
                diff = nb_prompts - nb_packages
                msg = "%s packages to install but %s prompts to expect. %s prompts will be ignored" % (to_text(nb_packages), to_text(nb_prompts), to_text(diff))
            else:
                diff = nb_packages - nb_prompts
                msg = "%s packages to install but only %s prompts to expect. %s packages won't be expected to have a prompt" \
                    % (to_text(nb_packages), to_text(nb_prompts), to_text(diff))
            module.warn(msg)

        # Preparing prompts answer according to item type
        tmp_prompts = []
        for _item in prompts:
            # If the current item is a dict then we expect it's key to be the prompt regex and it's value to be the answer
            # We also expect here that the dict only has ONE key and the first key will be taken
            if isinstance(_item, dict):
                key = list(_item.keys())[0]
                answer = _item[key] + "\n"

                tmp_prompts.append((key, answer))
            elif not _item:
                tmp_prompts.append((None, default_stdin))
            else:
                tmp_prompts.append((_item, default_stdin))
        prompts = tmp_prompts
    for i, package in enumerate(packages):
        # if the package is installed and state == present
        # or state == latest and is up-to-date then skip
        installed, updated = query_package(module, package)
        if installed and (state == 'present' or (state == 'latest' and updated)):
            continue

        if state == 'present':
            command = 'install'

        if state == 'latest':
            command = 'upgrade'

        if has_prompt and i < len(prompts):
            prompt_regex = prompts[i][0]
            data = prompts[i][1]
        else:
            prompt_regex = None
            data = default_stdin

        cmd = "%s %s %s" % (_get_pear_path(module), command, package)
        rc, stdout, stderr = module.run_command(cmd, check_rc=False, prompt_regex=prompt_regex, data=data, binary_data=True)
        if rc != 0:
            module.fail_json(msg="failed to install %s: %s" % (package, to_text(stdout + stderr)))

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="installed %s package(s)" % (install_c))

    module.exit_json(changed=False, msg="package(s) already installed")


def check_packages(module, packages, state):
    would_be_changed = []
    for package in packages:
        installed, updated = query_package(module, package)
        if ((state in ["present", "latest"] and not installed) or
                (state == "absent" and installed) or
                (state == "latest" and not updated)):
            would_be_changed.append(package)
    if would_be_changed:
        if state == "absent":
            state = "removed"
        module.exit_json(changed=True, msg="%s package(s) would be %s" % (
            len(would_be_changed), state))
    else:
        module.exit_json(change=False, msg="package(s) already %s" % state)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['pkg'], required=True),
            state=dict(default='present', choices=['present', 'installed', "latest", 'absent', 'removed']),
            executable=dict(default=None, required=False, type='path'),
            prompts=dict(default=None, required=False, type='list', elements='raw'),
        ),
        supports_check_mode=True)

    p = module.params

    # normalize the state parameter
    if p['state'] in ['present', 'installed']:
        p['state'] = 'present'
    elif p['state'] in ['absent', 'removed']:
        p['state'] = 'absent'

    if p['name']:
        pkgs = p['name'].split(',')

        pkg_files = []
        for i, pkg in enumerate(pkgs):
            pkg_files.append(None)

        if module.check_mode:
            check_packages(module, pkgs, p['state'])

        if p['state'] in ['present', 'latest']:
            install_packages(module, p['state'], pkgs, p["prompts"])
        elif p['state'] == 'absent':
            remove_packages(module, pkgs)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Giovanni Sciortino (@giovannisciortino)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: rhsm_repository
short_description: Manage RHSM repositories using the subscription-manager command
description:
  - Manage (Enable/Disable) RHSM repositories to the Red Hat Subscription
    Management entitlement platform using the C(subscription-manager) command.
author: Giovanni Sciortino (@giovannisciortino)
notes:
  - In order to manage RHSM repositories the system must be already registered
    to RHSM manually or using the Ansible M(community.general.redhat_subscription) module.
  - It is possible to interact with C(subscription-manager) only as root,
    so root permissions are required to successfully run this module.

requirements:
  - subscription-manager
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  state:
    description:
      - If state is equal to present or disabled, indicates the desired
        repository state.
      - |
        Please note that V(present) and V(absent) are deprecated, and will be
        removed in community.general 10.0.0; please use V(enabled) and
        V(disabled) instead.
    choices: [present, enabled, absent, disabled]
    default: "enabled"
    type: str
  name:
    description:
      - The ID of repositories to enable.
      - To operate on several repositories this can accept a comma separated
        list or a YAML list.
    required: true
    type: list
    elements: str
  purge:
    description:
      - Disable all currently enabled repositories that are not not specified in O(name).
        Only set this to V(true) if passing in a list of repositories to the O(name) field.
        Using this with C(loop) will most likely not have the desired result.
    type: bool
    default: false
'''

EXAMPLES = '''
- name: Enable a RHSM repository
  community.general.rhsm_repository:
    name: rhel-7-server-rpms

- name: Disable all RHSM repositories
  community.general.rhsm_repository:
    name: '*'
    state: disabled

- name: Enable all repositories starting with rhel-6-server
  community.general.rhsm_repository:
    name: rhel-6-server*
    state: enabled

- name: Disable all repositories except rhel-7-server-rpms
  community.general.rhsm_repository:
    name: rhel-7-server-rpms
    purge: true
'''

RETURN = '''
repositories:
  description:
    - The list of RHSM repositories with their states.
    - When this module is used to change the repository states, this list contains the updated states after the changes.
  returned: success
  type: list
'''

import os
from fnmatch import fnmatch
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule


class Rhsm(object):
    def __init__(self, module):
        self.module = module
        self.rhsm_bin = self.module.get_bin_path('subscription-manager', required=True)
        self.rhsm_kwargs = {
            'environ_update': dict(LANG='C', LC_ALL='C', LC_MESSAGES='C'),
            'expand_user_and_vars': False,
            'use_unsafe_shell': False,
        }

    def run_repos(self, arguments):
        """
        Execute `subscription-manager repos` with arguments and manage common errors
        """
        rc, out, err = self.module.run_command(
            [self.rhsm_bin, 'repos'] + arguments,
            **self.rhsm_kwargs
        )

        if rc == 0 and out == 'This system has no repositories available through subscriptions.\n':
            self.module.fail_json(msg='This system has no repositories available through subscriptions')
        elif rc == 1:
            self.module.fail_json(msg='subscription-manager failed with the following error: %s' % err)
        else:
            return rc, out, err

    def list_repositories(self):
        """
        Generate RHSM repository list and return a list of dict
        """
        rc, out, err = self.run_repos(['--list'])

        repo_id = ''
        repo_name = ''
        repo_url = ''
        repo_enabled = ''

        repo_result = []
        for line in out.splitlines():
            # ignore lines that are:
            # - empty
            # - "+---------[...]" -- i.e. header
            # - "    Available Repositories [...]" -- i.e. header
            if line == '' or line[0] == '+' or line[0] == ' ':
                continue

            if line.startswith('Repo ID: '):
                repo_id = line[9:].lstrip()
                continue

            if line.startswith('Repo Name: '):
                repo_name = line[11:].lstrip()
                continue

            if line.startswith('Repo URL: '):
                repo_url = line[10:].lstrip()
                continue

            if line.startswith('Enabled: '):
                repo_enabled = line[9:].lstrip()

                repo = {
                    "id": repo_id,
                    "name": repo_name,
                    "url": repo_url,
                    "enabled": True if repo_enabled == '1' else False
                }

                repo_result.append(repo)

        return repo_result


def repository_modify(module, rhsm, state, name, purge=False):
    name = set(name)
    current_repo_list = rhsm.list_repositories()
    updated_repo_list = deepcopy(current_repo_list)
    matched_existing_repo = {}
    for repoid in name:
        matched_existing_repo[repoid] = []
        for idx, repo in enumerate(current_repo_list):
            if fnmatch(repo['id'], repoid):
                matched_existing_repo[repoid].append(repo)
                # Update current_repo_list to return it as result variable
                updated_repo_list[idx]['enabled'] = True if state == 'enabled' else False

    changed = False
    results = []
    diff_before = ""
    diff_after = ""
    rhsm_arguments = []

    for repoid in matched_existing_repo:
        if len(matched_existing_repo[repoid]) == 0:
            results.append("%s is not a valid repository ID" % repoid)
            module.fail_json(results=results, msg="%s is not a valid repository ID" % repoid)
        for repo in matched_existing_repo[repoid]:
            if state in ['disabled', 'absent']:
                if repo['enabled']:
                    changed = True
                    diff_before += "Repository '%s' is enabled for this system\n" % repo['id']
                    diff_after += "Repository '%s' is disabled for this system\n" % repo['id']
                results.append("Repository '%s' is disabled for this system" % repo['id'])
                rhsm_arguments += ['--disable', repo['id']]
            elif state in ['enabled', 'present']:
                if not repo['enabled']:
                    changed = True
                    diff_before += "Repository '%s' is disabled for this system\n" % repo['id']
                    diff_after += "Repository '%s' is enabled for this system\n" % repo['id']
                results.append("Repository '%s' is enabled for this system" % repo['id'])
                rhsm_arguments += ['--enable', repo['id']]

    # Disable all enabled repos on the system that are not in the task and not
    # marked as disabled by the task
    if purge:
        enabled_repo_ids = set(repo['id'] for repo in updated_repo_list if repo['enabled'])
        matched_repoids_set = set(matched_existing_repo.keys())
        difference = enabled_repo_ids.difference(matched_repoids_set)
        if len(difference) > 0:
            for repoid in difference:
                changed = True
                diff_before.join("Repository '{repoid}'' is enabled for this system\n".format(repoid=repoid))
                diff_after.join("Repository '{repoid}' is disabled for this system\n".format(repoid=repoid))
                results.append("Repository '{repoid}' is disabled for this system".format(repoid=repoid))
                rhsm_arguments.extend(['--disable', repoid])
            for updated_repo in updated_repo_list:
                if updated_repo['id'] in difference:
                    updated_repo['enabled'] = False

    diff = {'before': diff_before,
            'after': diff_after,
            'before_header': "RHSM repositories",
            'after_header': "RHSM repositories"}

    if not module.check_mode and changed:
        rc, out, err = rhsm.run_repos(rhsm_arguments)
        results = out.splitlines()
    module.exit_json(results=results, changed=changed, repositories=updated_repo_list, diff=diff)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='list', elements='str', required=True),
            state=dict(choices=['enabled', 'disabled', 'present', 'absent'], default='enabled'),
            purge=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    if os.getuid() != 0:
        module.fail_json(
            msg="Interacting with subscription-manager requires root permissions ('become: true')"
        )

    rhsm = Rhsm(module)

    name = module.params['name']
    state = module.params['state']
    purge = module.params['purge']

    if state in ['present', 'absent']:
        replacement = 'enabled' if state == 'present' else 'disabled'
        module.deprecate(
            'state=%s is deprecated; please use state=%s instead' % (state, replacement),
            version='10.0.0',
            collection_name='community.general',
        )

    repository_modify(module, rhsm, state, name, purge)


if __name__ == '__main__':
    main()

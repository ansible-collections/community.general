#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Kevin Brebanov <https://github.com/kbrebanov>
# Based on pacman (Afterburn <https://github.com/afterburn>, Aaron Bull Schaefer <aaron@elasticdog.com>)
# and apt (Matthew Williams <matthew@flowroute.com>) modules.
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: apk
short_description: Manages apk packages
description:
  - Manages C(apk) packages for Alpine Linux.
author: "Kevin Brebanov (@kbrebanov)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  available:
    description:
      - During upgrade, reset versioned world dependencies and change logic to prefer replacing or downgrading packages (instead
        of holding them) if the currently installed package is no longer available from any repository.
    type: bool
    default: false
  name:
    description:
      - A package name, like V(foo), or multiple packages, like V(foo,bar).
      - Do not include additional whitespace when specifying multiple packages as a string. Prefer YAML lists over comma-separating
        multiple package names.
    type: list
    elements: str
  no_cache:
    description:
      - Do not use any local cache path.
    type: bool
    default: false
    version_added: 1.0.0
  repository:
    description:
      - A package repository or multiple repositories. Unlike with the underlying apk command, this list overrides the system
        repositories rather than supplement them.
    type: list
    elements: str
  state:
    description:
      - Indicates the desired package(s) state.
      - V(present) ensures the package(s) is/are present. V(installed) can be used as an alias.
      - V(absent) ensures the package(s) is/are absent. V(removed) can be used as an alias.
      - V(latest) ensures the package(s) is/are present and the latest version(s).
    default: present
    choices: ["present", "absent", "latest", "installed", "removed"]
    type: str
  update_cache:
    description:
      - Update repository indexes. Can be run with other steps or on its own.
    type: bool
    default: false
  upgrade:
    description:
      - Upgrade all installed packages to their latest version.
    type: bool
    default: false
  world:
    description:
      - Use a custom world file when checking for explicitly installed packages. The file is used only when a value is provided
        for O(name), and O(state) is set to V(present) or V(latest).
    type: str
    default: /etc/apk/world
    version_added: 5.4.0
notes:
  - O(name) and O(upgrade) are mutually exclusive.
  - When used with a C(loop:) each package is processed individually, it is much more efficient to pass the list directly
    to the O(name) option.
"""

EXAMPLES = r"""
- name: Update repositories and install foo package
  community.general.apk:
    name: foo
    update_cache: true

- name: Update repositories and install foo and bar packages
  community.general.apk:
    name: foo,bar
    update_cache: true

- name: Remove foo package
  community.general.apk:
    name: foo
    state: absent

- name: Remove foo and bar packages
  community.general.apk:
    name: foo,bar
    state: absent

- name: Install the package foo
  community.general.apk:
    name: foo
    state: present

- name: Install the packages foo and bar
  community.general.apk:
    name: foo,bar
    state: present

- name: Update repositories and update package foo to latest version
  community.general.apk:
    name: foo
    state: latest
    update_cache: true

- name: Update repositories and update packages foo and bar to latest versions
  community.general.apk:
    name: foo,bar
    state: latest
    update_cache: true

- name: Update all installed packages to the latest versions
  community.general.apk:
    upgrade: true

- name: Upgrade / replace / downgrade / uninstall all installed packages to the latest versions available
  community.general.apk:
    available: true
    upgrade: true

- name: Update repositories as a separate step
  community.general.apk:
    update_cache: true

- name: Install package from a specific repository
  community.general.apk:
    name: foo
    state: latest
    update_cache: true
    repository: http://dl-3.alpinelinux.org/alpine/edge/main

- name: Install package without using cache
  community.general.apk:
    name: foo
    state: latest
    no_cache: true

- name: Install package checking a custom world
  community.general.apk:
    name: foo
    state: latest
    world: /etc/apk/world.custom
"""

RETURN = r"""
packages:
  description: A list of packages that have been changed.
  returned: when packages have changed
  type: list
  sample: ["package", "other-package"]
"""

import re
# Import module snippets.
from ansible.module_utils.basic import AnsibleModule


def parse_for_packages(stdout):
    packages = []
    data = stdout.split('\n')
    regex = re.compile(r'^\(\d+/\d+\)\s+\S+\s+(\S+)')
    for l in data:
        p = regex.search(l)
        if p:
            packages.append(p.group(1))
    return packages


def update_package_db(module, exit):
    cmd = APK_PATH + ["update"]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc != 0:
        module.fail_json(msg="could not update package db", stdout=stdout, stderr=stderr)
    elif exit:
        module.exit_json(changed=True, msg='updated repository indexes', stdout=stdout, stderr=stderr)
    else:
        return True


def query_toplevel(module, name, world):
    # world contains a list of top-level packages separated by ' ' or \n
    # packages may contain repository (@) or version (=<>~) separator characters or start with negation !
    regex = re.compile(r'^' + re.escape(name) + r'([@=<>~].+)?$')
    with open(world) as f:
        content = f.read().split()
        for p in content:
            if regex.search(p):
                return True
    return False


def query_package(module, name):
    cmd = APK_PATH + ["-v", "info", "--installed", name]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc == 0:
        return True
    else:
        return False


def query_latest(module, name):
    cmd = APK_PATH + ["version", name]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    search_pattern = r"(%s)-[\d\.\w]+-[\d\w]+\s+(.)\s+[\d\.\w]+-[\d\w]+\s+" % (re.escape(name))
    match = re.search(search_pattern, stdout)
    if match and match.group(2) == "<":
        return False
    return True


def query_virtual(module, name):
    cmd = APK_PATH + ["-v", "info", "--description", name]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    search_pattern = r"^%s: virtual meta package" % (re.escape(name))
    if re.search(search_pattern, stdout):
        return True
    return False


def get_dependencies(module, name):
    cmd = APK_PATH + ["-v", "info", "--depends", name]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    dependencies = stdout.split()
    if len(dependencies) > 1:
        return dependencies[1:]
    else:
        return []


def upgrade_packages(module, available):
    if module.check_mode:
        cmd = APK_PATH + ["upgrade", "--simulate"]
    else:
        cmd = APK_PATH + ["upgrade"]
    if available:
        cmd.append("--available")
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    packagelist = parse_for_packages(stdout)
    if rc != 0:
        module.fail_json(msg="failed to upgrade packages", stdout=stdout, stderr=stderr, packages=packagelist)
    if re.search(r'^OK', stdout):
        module.exit_json(changed=False, msg="packages already upgraded", stdout=stdout, stderr=stderr, packages=packagelist)
    module.exit_json(changed=True, msg="upgraded packages", stdout=stdout, stderr=stderr, packages=packagelist)


def install_packages(module, names, state, world):
    upgrade = False
    to_install = []
    to_upgrade = []
    for name in names:
        # Check if virtual package
        if query_virtual(module, name):
            # Get virtual package dependencies
            dependencies = get_dependencies(module, name)
            for dependency in dependencies:
                if state == 'latest' and not query_latest(module, dependency):
                    to_upgrade.append(dependency)
        else:
            if not query_toplevel(module, name, world):
                to_install.append(name)
            elif state == 'latest' and not query_latest(module, name):
                to_upgrade.append(name)
    if to_upgrade:
        upgrade = True
    if not to_install and not upgrade:
        module.exit_json(changed=False, msg="package(s) already installed")
    packages = to_install + to_upgrade
    if upgrade:
        if module.check_mode:
            cmd = APK_PATH + ["add", "--upgrade", "--simulate"] + packages
        else:
            cmd = APK_PATH + ["add", "--upgrade"] + packages
    else:
        if module.check_mode:
            cmd = APK_PATH + ["add", "--simulate"] + packages
        else:
            cmd = APK_PATH + ["add"] + packages
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    packagelist = parse_for_packages(stdout)
    if rc != 0:
        module.fail_json(msg="failed to install %s" % (packages), stdout=stdout, stderr=stderr, packages=packagelist)
    module.exit_json(changed=True, msg="installed %s package(s)" % (packages), stdout=stdout, stderr=stderr, packages=packagelist)


def remove_packages(module, names):
    installed = []
    for name in names:
        if query_package(module, name):
            installed.append(name)
    if not installed:
        module.exit_json(changed=False, msg="package(s) already removed")
    names = installed
    if module.check_mode:
        cmd = APK_PATH + ["del", "--purge", "--simulate"] + names
    else:
        cmd = APK_PATH + ["del", "--purge"] + names
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    packagelist = parse_for_packages(stdout)
    # Check to see if packages are still present because of dependencies
    for name in installed:
        if query_package(module, name):
            rc = 1
            break
    if rc != 0:
        module.fail_json(msg="failed to remove %s package(s)" % (names), stdout=stdout, stderr=stderr, packages=packagelist)
    module.exit_json(changed=True, msg="removed %s package(s)" % (names), stdout=stdout, stderr=stderr, packages=packagelist)

# ==========================================
# Main control flow.


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'installed', 'absent', 'removed', 'latest']),
            name=dict(type='list', elements='str'),
            no_cache=dict(default=False, type='bool'),
            repository=dict(type='list', elements='str'),
            update_cache=dict(default=False, type='bool'),
            upgrade=dict(default=False, type='bool'),
            available=dict(default=False, type='bool'),
            world=dict(default='/etc/apk/world', type='str'),
        ),
        required_one_of=[['name', 'update_cache', 'upgrade']],
        mutually_exclusive=[['name', 'upgrade']],
        supports_check_mode=True
    )

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    global APK_PATH
    APK_PATH = [module.get_bin_path('apk', required=True)]

    p = module.params

    if p['name'] and any(not name.strip() for name in p['name']):
        module.fail_json(msg="Package name(s) cannot be empty or whitespace-only")

    if p['no_cache']:
        APK_PATH.append("--no-cache")

    # add repositories to the APK_PATH
    if p['repository']:
        for r in p['repository']:
            APK_PATH.extend(["--repository", r, "--repositories-file", "/dev/null"])

    # normalize the state parameter
    if p['state'] in ['present', 'installed']:
        p['state'] = 'present'
    if p['state'] in ['absent', 'removed']:
        p['state'] = 'absent'

    if p['update_cache']:
        update_package_db(module, not p['name'] and not p['upgrade'])

    if p['upgrade']:
        upgrade_packages(module, p['available'])

    if p['state'] in ['present', 'latest']:
        install_packages(module, p['name'], p['state'], p['world'])
    elif p['state'] == 'absent':
        remove_packages(module, p['name'])


if __name__ == '__main__':
    main()

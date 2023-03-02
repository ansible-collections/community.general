#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Florian Paul Azim Hoberg <florian.hoberg@credativ.de>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yum_versionlock
version_added: 2.0.0
short_description: Locks / unlocks a installed package(s) from being updated by yum package manager
description:
  - This module adds installed packages to yum versionlock to prevent the package(s) from being updated.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Package name or a list of package names with optional wildcards.
    type: list
    required: true
    elements: str
  state:
    description:
    - If state is C(present), package(s) will be added to yum versionlock list.
    - If state is C(absent), package(s) will be removed from yum versionlock list.
    choices: [ 'absent', 'present' ]
    type: str
    default: present
notes:
    - Requires yum-plugin-versionlock package on the remote node.
requirements:
- yum
- yum-versionlock
author:
    - Florian Paul Azim Hoberg (@gyptazy)
    - Amin Vakil (@aminvakil)
'''

EXAMPLES = r'''
- name: Prevent Apache / httpd from being updated
  community.general.yum_versionlock:
    state: present
    name: httpd

- name: Prevent multiple packages from being updated
  community.general.yum_versionlock:
    state: present
    name:
    - httpd
    - nginx
    - haproxy
    - curl

- name: Remove lock from Apache / httpd to be updated again
  community.general.yum_versionlock:
    state: absent
    name: httpd
'''

RETURN = r'''
packages:
    description: A list of package(s) in versionlock list.
    returned: success
    type: list
    elements: str
    sample: [ 'httpd' ]
state:
    description: State of package(s).
    returned: success
    type: str
    sample: present
'''

import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from fnmatch import fnmatch

# on DNF-based distros, yum is a symlink to dnf, so we try to handle their different entry formats.
NEVRA_RE_YUM = re.compile(r'^(?P<exclude>!)?(?P<epoch>\d+):(?P<name>.+)-'
                          r'(?P<version>.+)-(?P<release>.+)\.(?P<arch>.+)$')
NEVRA_RE_DNF = re.compile(r"^(?P<exclude>!)?(?P<name>.+)-(?P<epoch>\d+):(?P<version>.+)-"
                          r"(?P<release>.+)\.(?P<arch>.+)$")


class YumVersionLock:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.yum_bin = module.get_bin_path('yum', required=True)

    def get_versionlock_packages(self):
        """ Get an overview of all packages on yum versionlock """
        rc, out, err = self.module.run_command([self.yum_bin, "versionlock", "list"])
        if rc == 0:
            return out
        elif rc == 1 and 'o such command:' in err:
            self.module.fail_json(msg="Error: Please install rpm package yum-plugin-versionlock : " + to_native(err) + to_native(out))
        self.module.fail_json(msg="Error: " + to_native(err) + to_native(out))

    def ensure_state(self, packages, command):
        """ Ensure packages state """
        rc, out, err = self.module.run_command([self.yum_bin, "-q", "versionlock", command] + packages)
        if rc == 0:
            return True
        self.module.fail_json(msg="Error: " + to_native(err) + to_native(out))


def match(entry, name):
    m = NEVRA_RE_YUM.match(entry)
    if not m:
        m = NEVRA_RE_DNF.match(entry)
    if not m:
        return False
    return fnmatch(m.group("name"), name)


def main():
    """ start main program to add/remove a package to yum versionlock"""
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            name=dict(required=True, type='list', elements='str'),
        ),
        supports_check_mode=True
    )

    state = module.params['state']
    packages = module.params['name']
    changed = False

    yum_v = YumVersionLock(module)

    # Get an overview of all packages that have a version lock
    versionlock_packages = yum_v.get_versionlock_packages()

    # Ensure versionlock state of packages
    packages_list = []
    if state in ('present', ):
        command = 'add'
        for single_pkg in packages:
            if not any(match(pkg, single_pkg) for pkg in versionlock_packages.split()):
                packages_list.append(single_pkg)
        if packages_list:
            if module.check_mode:
                changed = True
            else:
                changed = yum_v.ensure_state(packages_list, command)
    elif state in ('absent', ):
        command = 'delete'
        for single_pkg in packages:
            if any(match(pkg, single_pkg) for pkg in versionlock_packages.split()):
                packages_list.append(single_pkg)
        if packages_list:
            if module.check_mode:
                changed = True
            else:
                changed = yum_v.ensure_state(packages_list, command)

    module.exit_json(
        changed=changed,
        meta={
            "packages": packages,
            "state": state
        }
    )


if __name__ == '__main__':
    main()

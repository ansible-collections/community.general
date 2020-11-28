#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Florian Paul Hoberg <florian.hoberg@credativ.de>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yum_versionlock
version_added: 2.0.0
short_description: Locks / Unlocks an installed package(s) from being updated by yum package manager.
description:
     - This module adds installed packages to yum versionlock to prevent the package from being updated.
options:
  name:
    description:
      - Package name or a list of packages.
    type: list
    required: true
    elements: str
  state:
    description:
    - If state is C(present) or C(locked), package(s) will be added to yum versionlock list.
    - If state is C(absent) or C(unlocked), package(s) will be removed from yum versionlock list.
    choices: [ 'absent', 'locked', 'present', 'unlocked' ]
    type: str
    default: present
notes:
    - Requires yum-plugin-versionlock package on the remote node.
    - Supports C(check_mode).
requirements:
- yum
- yum-versionlock
author:
    - Florian Paul Hoberg (@florianpaulhoberg)
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

- name: Unlock Apache / httpd to be updated again
  community.general.yum_versionlock:
    state: absent
    package: httpd
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


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

    def ensure_state(self, package, command):
        """ Ensure package state """
        rc, out, err = self.module.run_command([self.yum_bin, "-q", "versionlock", command, package])
        if rc == 0:
            return True
        self.module.fail_json(msg="Error: " + to_native(err) + to_native(out))


def main():
    """ start main program to add/remove a package to yum versionlock"""
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'locked', 'unlocked', 'absent']),
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
    if state in ('present', 'locked'):
        command = 'add'
        for single_pkg in packages:
            if single_pkg not in versionlock_packages:
                if module.check_mode:
                    changed = True
                    continue
                changed = yum_v.ensure_state(single_pkg, command)
    elif state in ('absent', 'unlocked'):
        command = 'delete'
        for single_pkg in packages:
            if single_pkg in versionlock_packages:
                if module.check_mode:
                    changed = True
                    continue
                changed = yum_v.ensure_state(single_pkg, command)

    module.exit_json(
        changed=changed,
        meta={
            "packages": packages,
            "state": state
        }
    )


if __name__ == '__main__':
    main()

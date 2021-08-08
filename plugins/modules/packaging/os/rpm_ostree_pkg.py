#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Dusty Mabe <dusty@dustymabe.com>
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rpm_ostree_pkg
short_description: Install or uninstall overlay additional packages
version_added: "2.0.0"
description:
    - Install or uninstall overlay additional packages using C(rpm-ostree) command.
options:
    name:
      description:
      - Name of overlay package to install or remove.
      required: true
      type: list
      elements: str
      aliases: [ pkg ]
    state:
      description:
      - State of the overlay package.
      - C(present) simply ensures that a desired package is installed.
      - C(absent) removes the specified package.
      choices: [ 'absent', 'present' ]
      default: 'present'
      type: str
author:
- Dusty Mabe (@dustymabe)
- Abhijeet Kasurde (@Akasurde)
notes:
- Does not support C(check_mode).
'''

EXAMPLES = r'''
- name: Install overlay package
  community.general.rpm_ostree_pkg:
    name: nfs-utils
    state: present

- name: Remove overlay package
  community.general.rpm_ostree_pkg:
    name: nfs-utils
    state: absent
'''

RETURN = r'''
rc:
    description: Return code of rpm-ostree command.
    returned: always
    type: int
    sample: 0
changed:
    description: State changes.
    returned: always
    type: bool
    sample: True
action:
    description: Action performed.
    returned: always
    type: str
    sample: 'install'
packages:
    description: A list of packages specified.
    returned: always
    type: list
    sample: ['nfs-utils']
stdout:
    description: Stdout of rpm-ostree command.
    returned: always
    type: str
    sample: 'Staging deployment...done\n...'
stderr:
    description: Stderr of rpm-ostree command.
    returned: always
    type: str
    sample: ''
cmd:
    description: Full command used for performed action.
    returned: always
    type: str
    sample: 'rpm-ostree uninstall --allow-inactive --idempotent --unchanged-exit-77 nfs-utils'
'''

from ansible.module_utils.basic import AnsibleModule


class RpmOstreePkg:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.state = module.params['state']

    def ensure(self):
        results = dict(
            rc=0,
            changed=False,
            action='',
            packages=[],
            stdout='',
            stderr='',
            cmd='',
        )

        # Ensure rpm-ostree command exists
        cmd = [self.module.get_bin_path('rpm-ostree', required=True)]

        # Decide action to perform
        if self.state in ('present'):
            results['action'] = 'install'
            cmd.append('install')
        elif self.state in ('absent'):
            results['action'] = 'uninstall'
            cmd.append('uninstall')

        # Additional parameters
        cmd.extend(['--allow-inactive', '--idempotent', '--unchanged-exit-77'])
        for pkg in self.params['name']:
            cmd.append(pkg)
            results['packages'].append(pkg)

        rc, out, err = self.module.run_command(cmd)

        results.update(dict(
            rc=rc,
            cmd=' '.join(cmd),
            stdout=out,
            stderr=err,
        ))

        # A few possible options:
        #     - rc=0  - succeeded in making a change
        #     - rc=77 - no change was needed
        #     - rc=?  - error
        if rc == 0:
            results['changed'] = True
        elif rc == 77:
            results['changed'] = False
            results['rc'] = 0
        else:
            self.module.fail_json(msg='non-zero return code', **results)

        self.module.exit_json(**results)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                default="present",
                choices=['absent', 'present']
            ),
            name=dict(
                aliases=["pkg"],
                required=True,
                type='list',
                elements='str',
            ),
        ),
    )

    rpm_ostree_pkg = RpmOstreePkg(module)
    rpm_ostree_pkg.ensure()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# (c) 2017, Arie Bregman <abregman@redhat.com>
#
# This file is a module for Ansible that interacts with Network Manager
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.    If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ip_netns
author: "Arie Bregman (@bregman-arie)"
short_description: Manage network namespaces
requirements: [ ip ]
description:
    - Create or delete network namespaces using the ip command.
options:
    name:
        required: false
        description:
            - Name of the namespace
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the namespace should exist
'''

EXAMPLES = '''
- name: Create a namespace named mario
  community.general.ip_netns:
    name: mario
    state: present

- name: Delete a namespace named luigi
  community.general.ip_netns:
    name: luigi
    state: absent
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text


class Namespace(object):
    """Interface to network namespaces. """

    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']

    def _netns(self, command):
        '''Run ip nents command'''
        return self.module.run_command(['ip', 'netns'] + command)

    def exists(self):
        '''Check if the namespace already exists'''
        rc, out, err = self.module.run_command('ip netns list')
        if rc != 0:
            self.module.fail_json(msg=to_text(err))
        return self.name in out

    def add(self):
        '''Create network namespace'''
        rtc, out, err = self._netns(['add', self.name])

        if rtc != 0:
            self.module.fail_json(msg=err)

    def delete(self):
        '''Delete network namespace'''
        rtc, out, err = self._netns(['del', self.name])
        if rtc != 0:
            self.module.fail_json(msg=err)

    def check(self):
        '''Run check mode'''
        changed = False

        if self.state == 'present' and self.exists():
            changed = True

        elif self.state == 'absent' and self.exists():
            changed = True
        elif self.state == 'present' and not self.exists():
            changed = True

        self.module.exit_json(changed=changed)

    def run(self):
        '''Make the necessary changes'''
        changed = False

        if self.state == 'absent':
            if self.exists():
                self.delete()
                changed = True
        elif self.state == 'present':
            if not self.exists():
                self.add()
                changed = True

        self.module.exit_json(changed=changed)


def main():
    """Entry point."""
    module = AnsibleModule(
        argument_spec={
            'name': {'default': None},
            'state': {'default': 'present', 'choices': ['present', 'absent']},
        },
        supports_check_mode=True,
    )

    network_namespace = Namespace(module)
    if module.check_mode:
        network_namespace.check()
    else:
        network_namespace.run()


if __name__ == '__main__':
    main()

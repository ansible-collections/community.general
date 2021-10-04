#!/usr/bin/python
# -*- coding: utf-8 -*-


# Copyright: (c) 2019, Jon Ellis (@JonEllis0) <ellis.jp@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: sudoers
short_description: Manage Linux sudoers files
description:
    - This module allows for the manipulation of Linux sudoers files
author:
    - "Jon Ellis (@JonEllis0) <ellis.jp@gmail.com>"
options:
    command:
        description:
            - The command allowed by the sudoers rule
            - Multiple can be added by passing a list of commands
        type: list
        elements: str
    group:
        required: false
        description:
            - Name of the group for the sudoers rule
            - (cannot be used in conjunction with user)
        type: str
    name:
        required: true
        description:
            - Name of the sudoers rule
        type: str
    nopassword:
        required: false
        description:
            - Whether a password will be required to run the sudo'd command
        default: true
        type: bool
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the rule should exist or not
        type: str
    user:
        required: false
        description:
            - Name of the user for the sudoers rule
            - (cannot be used in conjunction with group)
        type: str
'''

EXAMPLES = '''
- name: Allow the backup user to sudo /usr/local/bin/backup
  sudoers:
    name: allow-backup
    state: present
    user: backup
    command: /usr/local/bin/backup

- name: Allow the monitoring group to run sudo /usr/local/bin/gather-app-metrics without requiring a password
  sudoers:
    name: monitor-app
    group: monitoring
    command: /usr/local/bin/gather-app-metrics

- name: Allow the alice user to run sudo /bin/systemctl restart my-service or sudo /bin/systemctl reload my-service, but a password is required
  sudoers:
    name: alice-service
    user: alice
    command:
      - /bin/systemctl restart my-service
      - /bin/systemctl reload my-service
    nopassword: false

- name: Revoke the previous sudo grants given to the alice user
  sudoers:
      name: alice-service
      state: absent
'''

from ansible.module_utils.basic import AnsibleModule
import os


class Sudoers (object):

    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.user = module.params.get('user')
        self.group = module.params.get('group')
        self.state = module.params['state']
        self.nopassword = bool(module.params.get('nopassword', True))
        self.file = '/etc/sudoers.d/{filename}'.format(filename=self.name)

        command = module.params['command']
        if isinstance(command, list):
            self.commands = command
        else:
            self.commands = [command]

    def write(self):
        with open(self.file, 'w') as f:
            f.write(self.content())

    def delete(self):
        os.remove(self.file)

    def exists(self):
        return os.path.exists(self.file)

    def matches(self):
        with open(self.file, 'r') as f:
            return f.read() == self.content()

    def content(self):
        if self.user:
            owner = self.user
        elif self.group:
            owner = '%{group}'.format(group=self.group)

        command_str = ', '.join(self.commands)
        nopasswd_str = 'NOPASSWD' if self.nopassword else ''
        return "{owner} ALL={nopasswd}: {command}\n".format(owner=owner, nopasswd=nopasswd_str, command=command_str)

    def check(self):
        try:
            if self.state == 'absent' and self.exists():
                changed = True
            elif self.state == 'present':
                if not self.exists():
                    changed = True
                elif not self.matches():
                    changed = True
                else:
                    changed = False
            else:
                changed = False
        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(changed=changed)

    def run(self):
        changed = False

        try:
            if self.state == 'absent' and self.exists():
                self.delete()
                changed = True
            elif self.state == 'present':
                if not self.exists():
                    self.write()
                    changed = True
                elif not self.matches():
                    self.write()
                    changed = True
                else:
                    changed = False
            else:
                changed = False

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(changed=changed)


def main():
    argument_spec = {
        'command': {
            'type': 'list',
            'elements': 'str',
            'default': [],
        },
        'group': {},
        'name': {
            'required': True,
        },
        'nopassword': {
            'type': 'bool',
            'default': True,
        },
        'state': {
            'default': 'present',
            'choices': ['present', 'absent'],
        },
        'user': {},
    }
    mutually_exclusive = [['user', 'group']]

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
    )

    sudoers = Sudoers(module)

    if module.check_mode:
        sudoers.check()
    else:
        sudoers.run()


if __name__ == '__main__':
    main()

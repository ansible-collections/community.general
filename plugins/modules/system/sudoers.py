#!/usr/bin/python
# -*- coding: utf-8 -*-


# Copyright: (c) 2019, Jon Ellis (@JonEllis) <ellis.jp@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: sudoers
short_description: Manage sudoers files
version_added: "4.3.0"
description:
  - This module allows for the manipulation of sudoers files.
author:
  - "Jon Ellis (@JonEllis) <ellis.jp@gmail.com>"
options:
  commands:
    description:
      - The commands allowed by the sudoers rule.
      - Multiple can be added by passing a list of commands.
    type: list
    elements: str
  group:
    description:
      - The name of the group for the sudoers rule.
      - This option cannot be used in conjunction with I(user).
    type: str
  name:
    required: true
    description:
      - The name of the sudoers rule.
      - This will be used for the filename for the sudoers file managed by this rule.
    type: str
  nopassword:
    description:
      - Whether a password will be required to run the sudo'd command.
    default: true
    type: bool
  sudoers_path:
    description:
      - The path which sudoers config files will be managed in.
    default: /etc/sudoers.d
    type: str
  state:
    default: "present"
    choices:
      - present
      - absent
    description:
      - Whether the rule should exist or not.
    type: str
  user:
    description:
      - The name of the user for the sudoers rule.
      - This option cannot be used in conjunction with I(group).
    type: str
'''

EXAMPLES = '''
- name: Allow the backup user to sudo /usr/local/bin/backup
  community.general.sudoers:
    name: allow-backup
    state: present
    user: backup
    commands: /usr/local/bin/backup

- name: >-
    Allow the monitoring group to run sudo /usr/local/bin/gather-app-metrics
    without requiring a password
  community.general.sudoers:
    name: monitor-app
    group: monitoring
    commands: /usr/local/bin/gather-app-metrics

- name: >-
    Allow the alice user to run sudo /bin/systemctl restart my-service or
    sudo /bin/systemctl reload my-service, but a password is required
  community.general.sudoers:
    name: alice-service
    user: alice
    commands:
      - /bin/systemctl restart my-service
      - /bin/systemctl reload my-service
    nopassword: false

- name: Revoke the previous sudo grants given to the alice user
  community.general.sudoers:
    name: alice-service
    state: absent
'''

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


class Sudoers(object):

    def __init__(self, module):
        self.check_mode = module.check_mode
        self.name = module.params['name']
        self.user = module.params['user']
        self.group = module.params['group']
        self.state = module.params['state']
        self.nopassword = module.params['nopassword']
        self.sudoers_path = module.params['sudoers_path']
        self.file = os.path.join(self.sudoers_path, self.name)
        self.commands = module.params['commands']

    def write(self):
        if self.check_mode:
            return

        with open(self.file, 'w') as f:
            f.write(self.content())

    def delete(self):
        if self.check_mode:
            return

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

        commands_str = ', '.join(self.commands)
        nopasswd_str = 'NOPASSWD:' if self.nopassword else ''
        return "{owner} ALL={nopasswd} {commands}\n".format(owner=owner, nopasswd=nopasswd_str, commands=commands_str)

    def run(self):
        if self.state == 'absent' and self.exists():
            self.delete()
            return True

        if self.exists() and self.matches():
            return False

        self.write()
        return True


def main():
    argument_spec = {
        'commands': {
            'type': 'list',
            'elements': 'str',
        },
        'group': {},
        'name': {
            'required': True,
        },
        'nopassword': {
            'type': 'bool',
            'default': True,
        },
        'sudoers_path': {
            'type': 'str',
            'default': '/etc/sudoers.d',
        },
        'state': {
            'default': 'present',
            'choices': ['present', 'absent'],
        },
        'user': {},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[['user', 'group']],
        supports_check_mode=True,
        required_if=[('state', 'present', ['commands'])],
    )

    sudoers = Sudoers(module)

    try:
        changed = sudoers.run()
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-


# Copyright (c) 2019, Jon Ellis (@JonEllis) <ellis.jp@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: sudoers
short_description: Manage sudoers files
version_added: "4.3.0"
description:
  - This module allows for the manipulation of sudoers files.
author:
  - "Jon Ellis (@JonEllis) <ellis.jp@gmail.com>"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  commands:
    description:
      - The commands allowed by the sudoers rule.
      - Multiple can be added by passing a list of commands.
      - Use V(ALL) for all commands.
    type: list
    elements: str
  group:
    description:
      - The name of the group for the sudoers rule.
      - This option cannot be used in conjunction with O(user).
    type: str
  name:
    required: true
    description:
      - The name of the sudoers rule.
      - This is used for the filename for the sudoers file managed by this rule.
    type: str
  noexec:
    description:
      - Whether a command is prevented to run further commands itself.
    default: false
    type: bool
    version_added: 8.4.0
  nopassword:
    description:
      - Whether a password is not required when command is run with sudo.
    default: true
    type: bool
  setenv:
    description:
      - Whether to allow keeping the environment when command is run with sudo.
    default: false
    type: bool
    version_added: 6.3.0
  host:
    description:
      - Specify the host the rule is for.
    default: ALL
    type: str
    version_added: 6.2.0
  runas:
    description:
      - Specify the target user the command(s) runs as.
    type: str
    version_added: 4.7.0
  sudoers_path:
    description:
      - The path which sudoers config files are managed in.
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
      - This option cannot be used in conjunction with O(group).
    type: str
  validation:
    description:
      - If V(absent), the sudoers rule is added without validation.
      - If V(detect) and C(visudo) is available, then the sudoers rule is validated by C(visudo).
      - If V(required), C(visudo) must be available to validate the sudoers rule.
    type: str
    default: detect
    choices: [absent, detect, required]
    version_added: 5.2.0
"""

EXAMPLES = r"""
- name: Allow the backup user to sudo /usr/local/bin/backup
  community.general.sudoers:
    name: allow-backup
    state: present
    user: backup
    commands: /usr/local/bin/backup

- name: Allow the bob user to run any commands as alice with sudo -u alice
  community.general.sudoers:
    name: bob-do-as-alice
    state: present
    user: bob
    runas: alice
    commands: ALL

- name: >-
    Allow the monitoring group to run sudo /usr/local/bin/gather-app-metrics
    without requiring a password on the host called webserver
  community.general.sudoers:
    name: monitor-app
    group: monitoring
    host: webserver
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

- name: Allow alice to sudo /usr/local/bin/upload and keep env variables
  community.general.sudoers:
    name: allow-alice-upload
    user: alice
    commands: /usr/local/bin/upload
    setenv: true

- name: >-
    Allow alice to sudo /usr/bin/less but prevent less from
    running further commands itself
  community.general.sudoers:
    name: allow-alice-restricted-less
    user: alice
    commands: /usr/bin/less
    noexec: true
"""

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


class Sudoers(object):

    FILE_MODE = 0o440

    def __init__(self, module):
        self.module = module

        self.check_mode = module.check_mode
        self.name = module.params['name']
        self.user = module.params['user']
        self.group = module.params['group']
        self.state = module.params['state']
        self.noexec = module.params['noexec']
        self.nopassword = module.params['nopassword']
        self.setenv = module.params['setenv']
        self.host = module.params['host']
        self.runas = module.params['runas']
        self.sudoers_path = module.params['sudoers_path']
        self.file = os.path.join(self.sudoers_path, self.name)
        self.commands = module.params['commands']
        self.validation = module.params['validation']

    def write(self):
        if self.check_mode:
            return

        with open(self.file, 'w') as f:
            f.write(self.content())

        os.chmod(self.file, self.FILE_MODE)

    def delete(self):
        if self.check_mode:
            return

        os.remove(self.file)

    def exists(self):
        return os.path.exists(self.file)

    def matches(self):
        with open(self.file, 'r') as f:
            content_matches = f.read() == self.content()

        current_mode = os.stat(self.file).st_mode & 0o777
        mode_matches = current_mode == self.FILE_MODE

        return content_matches and mode_matches

    def content(self):
        if self.user:
            owner = self.user
        elif self.group:
            owner = '%{group}'.format(group=self.group)

        commands_str = ', '.join(self.commands)
        noexec_str = 'NOEXEC:' if self.noexec else ''
        nopasswd_str = 'NOPASSWD:' if self.nopassword else ''
        setenv_str = 'SETENV:' if self.setenv else ''
        runas_str = '({runas})'.format(runas=self.runas) if self.runas is not None else ''
        return "{owner} {host}={runas}{noexec}{nopasswd}{setenv} {commands}\n".format(
            owner=owner,
            host=self.host,
            runas=runas_str,
            noexec=noexec_str,
            nopasswd=nopasswd_str,
            setenv=setenv_str,
            commands=commands_str
        )

    def validate(self):
        if self.validation == 'absent':
            return

        visudo_path = self.module.get_bin_path('visudo', required=self.validation == 'required')
        if visudo_path is None:
            return

        check_command = [visudo_path, '-c', '-f', '-']
        rc, stdout, stderr = self.module.run_command(check_command, data=self.content())

        if rc != 0:
            self.module.fail_json(msg='Failed to validate sudoers rule:\n{stdout}'.format(stdout=stdout or stderr), stdout=stdout, stderr=stderr)

    def run(self):
        if self.state == 'absent':
            if self.exists():
                self.delete()
                return True
            else:
                return False

        self.validate()

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
        'noexec': {
            'type': 'bool',
            'default': False,
        },
        'nopassword': {
            'type': 'bool',
            'default': True,
        },
        'setenv': {
            'type': 'bool',
            'default': False,
        },
        'host': {
            'type': 'str',
            'default': 'ALL',
        },
        'runas': {
            'type': 'str',
            'default': None,
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
        'validation': {
            'default': 'detect',
            'choices': ['absent', 'detect', 'required']
        },
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

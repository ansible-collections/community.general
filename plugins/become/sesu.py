# -*- coding: utf-8 -*-
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: sesu
    short_description: CA Privileged Access Manager
    description:
        - This become plugins allows your remote/login user to execute commands as another user via the sesu utility.
    author: ansible (@nekonyuu)
    options:
        become_user:
            description: User you 'become' to execute the task
            default: ''
            ini:
              - section: privilege_escalation
                key: become_user
              - section: sesu_become_plugin
                key: user
            vars:
              - name: ansible_become_user
              - name: ansible_sesu_user
            env:
              - name: ANSIBLE_BECOME_USER
              - name: ANSIBLE_SESU_USER
        become_exe:
            description: sesu executable
            default: sesu
            ini:
              - section: privilege_escalation
                key: become_exe
              - section: sesu_become_plugin
                key: executable
            vars:
              - name: ansible_become_exe
              - name: ansible_sesu_exe
            env:
              - name: ANSIBLE_BECOME_EXE
              - name: ANSIBLE_SESU_EXE
        become_flags:
            description: Options to pass to sesu
            default: -H -S -n
            ini:
              - section: privilege_escalation
                key: become_flags
              - section: sesu_become_plugin
                key: flags
            vars:
              - name: ansible_become_flags
              - name: ansible_sesu_flags
            env:
              - name: ANSIBLE_BECOME_FLAGS
              - name: ANSIBLE_SESU_FLAGS
        become_pass:
            description: Password to pass to sesu
            required: false
            vars:
              - name: ansible_become_password
              - name: ansible_become_pass
              - name: ansible_sesu_pass
            env:
              - name: ANSIBLE_BECOME_PASS
              - name: ANSIBLE_SESU_PASS
            ini:
              - section: sesu_become_plugin
                key: password
'''

from ansible.plugins.become import BecomeBase


class BecomeModule(BecomeBase):

    name = 'community.general.sesu'

    prompt = 'Please enter your password:'
    fail = missing = ('Sorry, try again with sesu.',)

    def build_become_command(self, cmd, shell):
        super(BecomeModule, self).build_become_command(cmd, shell)

        if not cmd:
            return cmd

        become = self.get_option('become_exe')

        flags = self.get_option('become_flags')
        user = self.get_option('become_user')
        return '%s %s %s -c %s' % (become, flags, user, self._build_success_command(cmd, shell))

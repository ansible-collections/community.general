# -*- coding: utf-8 -*-
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: machinectl
short_description: Systemd's machinectl privilege escalation
description:
  - This become plugins allows your remote/login user to execute commands as another user using the C(machinectl) utility.
author: Ansible Core Team
options:
  become_user:
    description: User you 'become' to execute the task.
    type: string
    default: ''
    ini:
      - section: privilege_escalation
        key: become_user
      - section: machinectl_become_plugin
        key: user
    vars:
      - name: ansible_become_user
      - name: ansible_machinectl_user
    env:
      - name: ANSIBLE_BECOME_USER
      - name: ANSIBLE_MACHINECTL_USER
  become_exe:
    description: C(machinectl) executable.
    type: string
    default: machinectl
    ini:
      - section: privilege_escalation
        key: become_exe
      - section: machinectl_become_plugin
        key: executable
    vars:
      - name: ansible_become_exe
      - name: ansible_machinectl_exe
    env:
      - name: ANSIBLE_BECOME_EXE
      - name: ANSIBLE_MACHINECTL_EXE
  become_flags:
    description: Options to pass to C(machinectl).
    type: string
    default: ''
    ini:
      - section: privilege_escalation
        key: become_flags
      - section: machinectl_become_plugin
        key: flags
    vars:
      - name: ansible_become_flags
      - name: ansible_machinectl_flags
    env:
      - name: ANSIBLE_BECOME_FLAGS
      - name: ANSIBLE_MACHINECTL_FLAGS
  become_pass:
    description: Password for C(machinectl).
    type: string
    required: false
    vars:
      - name: ansible_become_password
      - name: ansible_become_pass
      - name: ansible_machinectl_pass
    env:
      - name: ANSIBLE_BECOME_PASS
      - name: ANSIBLE_MACHINECTL_PASS
    ini:
      - section: machinectl_become_plugin
        key: password
notes:
  - When not using this plugin with user V(root), it only works correctly with a polkit rule which will alter the behaviour
    of machinectl. This rule must alter the prompt behaviour to ask directly for the user credentials, if the user is allowed
    to perform the action (take a look at the examples section). If such a rule is not present the plugin only work if it
    is used in context with the root user, because then no further prompt will be shown by machinectl.
  - This become plugin does not work when connection pipelining is enabled. With ansible-core 2.19+, using it automatically
    disables pipelining. On ansible-core 2.18 and before, pipelining must explicitly be disabled by the user.
"""

EXAMPLES = r"""
# A polkit rule needed to use the module with a non-root user.
# See the Notes section for details.
/etc/polkit-1/rules.d/60-machinectl-fast-user-auth.rules: |-
  polkit.addRule(function(action, subject) {
    if(action.id == "org.freedesktop.machine1.host-shell" &&
      subject.isInGroup("wheel")) {
        return polkit.Result.AUTH_SELF_KEEP;
    }
  });
"""

from re import compile as re_compile

from ansible.plugins.become import BecomeBase
from ansible.module_utils._text import to_bytes


ansi_color_codes = re_compile(to_bytes(r'\x1B\[[0-9;]+m'))


class BecomeModule(BecomeBase):

    name = 'community.general.machinectl'

    prompt = 'Password: '
    fail = ('==== AUTHENTICATION FAILED ====',)
    success = ('==== AUTHENTICATION COMPLETE ====',)
    require_tty = True  # see https://github.com/ansible-collections/community.general/issues/6932

    # See https://github.com/ansible/ansible/issues/81254,
    # https://github.com/ansible/ansible/pull/78111
    pipelining = False

    @staticmethod
    def remove_ansi_codes(line):
        return ansi_color_codes.sub(b"", line)

    def build_become_command(self, cmd, shell):
        super(BecomeModule, self).build_become_command(cmd, shell)

        if not cmd:
            return cmd

        become = self.get_option('become_exe')

        flags = self.get_option('become_flags')
        user = self.get_option('become_user')
        return f'{become} -q shell {flags} {user}@ {self._build_success_command(cmd, shell)}'

    def check_success(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_success(b_output)

    def check_incorrect_password(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_incorrect_password(b_output)

    def check_missing_password(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_missing_password(b_output)

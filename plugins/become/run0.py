# -*- coding: utf-8 -*-
# Copyright (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: run0
    short_description: Systemd's run0
    description:
        - This become plugins allows your remote/login user to execute commands as another user via the C(run0) utility.
    author:
        - Thomas Sjögren (@konstruktoid)
    version_added: '9.0.0'
    options:
        become_user:
            description: User you 'become' to execute the task.
            default: root
            ini:
              - section: privilege_escalation
                key: become_user
              - section: run0_become_plugin
                key: user
            vars:
              - name: ansible_become_user
              - name: ansible_run0_user
            env:
              - name: ANSIBLE_BECOME_USER
              - name: ANSIBLE_RUN0_USER
            type: string
        become_exe:
            description: The C(run0) executable.
            default: run0
            ini:
              - section: privilege_escalation
                key: become_exe
              - section: run0_become_plugin
                key: executable
            vars:
              - name: ansible_become_exe
              - name: ansible_run0_exe
            env:
              - name: ANSIBLE_BECOME_EXE
              - name: ANSIBLE_RUN0_EXE
            type: string
        become_flags:
            description: Options to pass to run0.
            default: ''
            ini:
              - section: privilege_escalation
                key: become_flags
              - section: run0_become_plugin
                key: flags
            vars:
              - name: ansible_become_flags
              - name: ansible_run0_flags
            env:
              - name: ANSIBLE_BECOME_FLAGS
              - name: ANSIBLE_RUN0_FLAGS
            type: string
    notes:
      - This plugin will only work when a polkit rule is in place.
"""

EXAMPLES = r"""
# An example polkit rule that allows the user 'ansible' in the 'wheel' group
# to execute commands using run0 without authentication.
/etc/polkit-1/rules.d/60-run0-fast-user-auth.rules: |
  polkit.addRule(function(action, subject) {
    if(action.id == "org.freedesktop.systemd1.manage-units" &&
      subject.isInGroup("wheel") &&
      subject.user == "ansible") {
        return polkit.Result.YES;
    }
  });
"""

from re import compile as re_compile

from ansible.plugins.become import BecomeBase
from ansible.module_utils._text import to_bytes

ansi_color_codes = re_compile(to_bytes(r"\x1B\[[0-9;]+m"))


class BecomeModule(BecomeBase):

    name = "community.general.run0"

    prompt = "Password: "
    fail = ("==== AUTHENTICATION FAILED ====",)
    success = ("==== AUTHENTICATION COMPLETE ====",)
    require_tty = (
        True  # see https://github.com/ansible-collections/community.general/issues/6932
    )

    @staticmethod
    def remove_ansi_codes(line):
        return ansi_color_codes.sub(b"", line)

    def build_become_command(self, cmd, shell):
        super().build_become_command(cmd, shell)

        if not cmd:
            return cmd

        become = self.get_option("become_exe")
        flags = self.get_option("become_flags")
        user = self.get_option("become_user")

        return (
            f"{become} --user={user} {flags} {self._build_success_command(cmd, shell)}"
        )

    def check_success(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_success(b_output)

    def check_incorrect_password(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_incorrect_password(b_output)

    def check_missing_password(self, b_output):
        b_output = self.remove_ansi_codes(b_output)
        return super().check_missing_password(b_output)

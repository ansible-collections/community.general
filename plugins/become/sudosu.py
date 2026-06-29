# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: sudosu
short_description: Run tasks using sudo su -
description:
  - This become plugin allows your remote/login user to execute commands as another user using the C(sudo) and C(su) utilities
    combined.
author:
  - Dag Wieers (@dagwieers)
version_added: 2.4.0
options:
  become_user:
    description: User you 'become' to execute the task.
    type: string
    default: root
    ini:
      - section: privilege_escalation
        key: become_user
      - section: sudo_become_plugin
        key: user
    vars:
      - name: ansible_become_user
      - name: ansible_sudo_user
    env:
      - name: ANSIBLE_BECOME_USER
      - name: ANSIBLE_SUDO_USER
  become_flags:
    description: Options to pass to C(sudo).
    type: string
    default: -H -S -n
    ini:
      - section: privilege_escalation
        key: become_flags
      - section: sudo_become_plugin
        key: flags
    vars:
      - name: ansible_become_flags
      - name: ansible_sudo_flags
    env:
      - name: ANSIBLE_BECOME_FLAGS
      - name: ANSIBLE_SUDO_FLAGS
  become_pass:
    description: Password to pass to C(sudo).
    type: string
    required: false
    vars:
      - name: ansible_become_password
      - name: ansible_become_pass
      - name: ansible_sudo_pass
    env:
      - name: ANSIBLE_BECOME_PASS
      - name: ANSIBLE_SUDO_PASS
    ini:
      - section: sudo_become_plugin
        key: password
  alt_method:
    description:
      - Whether to use an alternative method to call C(su). Instead of running C(su -l user /path/to/shell -c command), it
        runs C(su -l user -c command).
      - Use this when the default one is not working on your system.
    required: false
    type: boolean
    ini:
      - section: community.general.sudosu
        key: alternative_method
    vars:
      - name: ansible_sudosu_alt_method
    env:
      - name: ANSIBLE_SUDOSU_ALT_METHOD
    version_added: 9.2.0
"""


from ansible.plugins.become import BecomeBase


class BecomeModule(BecomeBase):
    name = "community.general.sudosu"

    # messages for detecting prompted password issues
    fail = ("Sorry, try again.",)
    missing = ("Sorry, a password is required to run sudo", "sudo: a password is required")

    def build_become_command(self, cmd, shell):
        super().build_become_command(cmd, shell)

        if not cmd:
            return cmd

        becomecmd = "sudo"

        flags = self.get_option("become_flags") or ""
        prompt = ""
        if self.get_option("become_pass"):
            self.prompt = f"[sudo via ansible, key={self._id}] password:"
            if flags:  # this could be simplified, but kept as is for now for backwards string matching
                flags = flags.replace("-n", "")
            prompt = f'-p "{self.prompt}"'

        user = self.get_option("become_user") or ""
        if user:
            user = f"{user}"

        if self.get_option("alt_method"):
            return f"{becomecmd} {flags} {prompt} su -l {user} -c {self._build_success_command(cmd, shell, True)}"
        else:
            return f"{becomecmd} {flags} {prompt} su -l {user} {self._build_success_command(cmd, shell)}"

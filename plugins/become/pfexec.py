# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: pfexec
short_description: Profile based execution
description:
  - This become plugins allows your remote/login user to execute commands as another user using the C(pfexec) utility.
author: Ansible Core Team
options:
  become_user:
    description:
      - User you 'become' to execute the task.
      - This plugin ignores this setting as pfexec uses its own C(exec_attr) to figure this out, but it is supplied here for
        Ansible to make decisions needed for the task execution, like file permissions.
    type: string
    default: root
    ini:
      - section: privilege_escalation
        key: become_user
      - section: pfexec_become_plugin
        key: user
    vars:
      - name: ansible_become_user
      - name: ansible_pfexec_user
    env:
      - name: ANSIBLE_BECOME_USER
      - name: ANSIBLE_PFEXEC_USER
  become_exe:
    description: C(pfexec) executable.
    type: string
    default: pfexec
    ini:
      - section: privilege_escalation
        key: become_exe
      - section: pfexec_become_plugin
        key: executable
    vars:
      - name: ansible_become_exe
      - name: ansible_pfexec_exe
    env:
      - name: ANSIBLE_BECOME_EXE
      - name: ANSIBLE_PFEXEC_EXE
  become_flags:
    description: Options to pass to C(pfexec).
    type: string
    default: -H -S -n
    ini:
      - section: privilege_escalation
        key: become_flags
      - section: pfexec_become_plugin
        key: flags
    vars:
      - name: ansible_become_flags
      - name: ansible_pfexec_flags
    env:
      - name: ANSIBLE_BECOME_FLAGS
      - name: ANSIBLE_PFEXEC_FLAGS
  become_pass:
    description: C(pfexec) password.
    type: string
    required: false
    vars:
      - name: ansible_become_password
      - name: ansible_become_pass
      - name: ansible_pfexec_pass
    env:
      - name: ANSIBLE_BECOME_PASS
      - name: ANSIBLE_PFEXEC_PASS
    ini:
      - section: pfexec_become_plugin
        key: password
  wrap_exe:
    description: Toggle to wrap the command C(pfexec) calls in C(shell -c) or not.
    default: false
    type: bool
    ini:
      - section: pfexec_become_plugin
        key: wrap_execution
    vars:
      - name: ansible_pfexec_wrap_execution
    env:
      - name: ANSIBLE_PFEXEC_WRAP_EXECUTION
notes:
  - This plugin ignores O(become_user) as pfexec uses its own C(exec_attr) to figure this out.
"""

from ansible.plugins.become import BecomeBase


class BecomeModule(BecomeBase):
    name = "community.general.pfexec"

    def build_become_command(self, cmd, shell):
        super().build_become_command(cmd, shell)

        if not cmd:
            return cmd

        exe = self.get_option("become_exe")

        flags = self.get_option("become_flags")
        noexe = not self.get_option("wrap_exe")
        return f"{exe} {flags} {self._build_success_command(cmd, shell, noexe=noexe)}"

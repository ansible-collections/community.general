# -*- coding: utf-8 -*-
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: ksu
short_description: Kerberos substitute user
description:
  - This become plugins allows your remote/login user to execute commands as another user using the C(ksu) utility.
author: Ansible Core Team
options:
  become_user:
    description: User you 'become' to execute the task.
    type: string
    ini:
      - section: privilege_escalation
        key: become_user
      - section: ksu_become_plugin
        key: user
    vars:
      - name: ansible_become_user
      - name: ansible_ksu_user
    env:
      - name: ANSIBLE_BECOME_USER
      - name: ANSIBLE_KSU_USER
    required: true
  become_exe:
    description: C(ksu) executable.
    type: string
    default: ksu
    ini:
      - section: privilege_escalation
        key: become_exe
      - section: ksu_become_plugin
        key: executable
    vars:
      - name: ansible_become_exe
      - name: ansible_ksu_exe
    env:
      - name: ANSIBLE_BECOME_EXE
      - name: ANSIBLE_KSU_EXE
  become_flags:
    description: Options to pass to C(ksu).
    type: string
    default: ''
    ini:
      - section: privilege_escalation
        key: become_flags
      - section: ksu_become_plugin
        key: flags
    vars:
      - name: ansible_become_flags
      - name: ansible_ksu_flags
    env:
      - name: ANSIBLE_BECOME_FLAGS
      - name: ANSIBLE_KSU_FLAGS
  become_pass:
    description: C(ksu) password.
    type: string
    required: false
    vars:
      - name: ansible_ksu_pass
      - name: ansible_become_pass
      - name: ansible_become_password
    env:
      - name: ANSIBLE_BECOME_PASS
      - name: ANSIBLE_KSU_PASS
    ini:
      - section: ksu_become_plugin
        key: password
  prompt_l10n:
    description:
      - List of localized strings to match for prompt detection.
      - If empty we will use the built in one.
    type: list
    elements: string
    default: []
    ini:
      - section: ksu_become_plugin
        key: localized_prompts
    vars:
      - name: ansible_ksu_prompt_l10n
    env:
      - name: ANSIBLE_KSU_PROMPT_L10N
"""

import re

from ansible.module_utils.common.text.converters import to_bytes
from ansible.plugins.become import BecomeBase


class BecomeModule(BecomeBase):

    name = 'community.general.ksu'

    # messages for detecting prompted password issues
    fail = ('Password incorrect',)
    missing = ('No password given',)

    def check_password_prompt(self, b_output):
        ''' checks if the expected password prompt exists in b_output '''

        prompts = self.get_option('prompt_l10n') or ["Kerberos password for .*@.*:"]
        b_prompt = b"|".join(to_bytes(p) for p in prompts)

        return bool(re.match(b_prompt, b_output))

    def build_become_command(self, cmd, shell):

        super(BecomeModule, self).build_become_command(cmd, shell)

        # Prompt handling for ``ksu`` is more complicated, this
        # is used to satisfy the connection plugin
        self.prompt = True

        if not cmd:
            return cmd

        exe = self.get_option('become_exe')

        flags = self.get_option('become_flags')
        user = self.get_option('become_user')
        return f'{exe} {user} {flags} -e {self._build_success_command(cmd, shell)} '

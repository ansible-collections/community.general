# -*- coding: utf-8 -*-
# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: ksusu
    short_description: Kerberos substitute (ksu) user followed by substitute user (su)
    description:
        - This become plugins allows your remote/login user to execute commands as another user by calling C(su) through the C(ksu) utility.
    author:
        - Ed Schaller (@schallee)
    version_added: 6.2.0
    options:
        become_user_ksu:
            description: User you use with C(ksu) to run C(su).
            default: root
            ini:
              - section: privilege_escalation
                key: become_user_ksu
              - section: ksusu_become_plugin
                key: user_ksu
            vars:
              - name: ansible_become_user_ksu
              - name: ansible_ksusu_user_ksu
            env:
              - name: ANSIBLE_BECOME_USER_KSU
              - name: ANSIBLE_KSUSU_USER_KSU
            required: False
        become_user:
            description: User you 'become' to execute the task.
            default: root
            ini:
              - section: privilege_escalation
                key: become_user
              - section: privilege_escalation
                key: become_user_su
              - section: ksusu_become_plugin
                key: user
              - section: ksusu_become_plugin
                key: user_su
            vars:
              - name: ansible_become_user
              - name: ansible_become_user_su
              - name: ansible_ksusu_user
              - name: ansible_ksusu_user_su
            env:
              - name: ANSIBLE_BECOME_USER
              - name: ANSIBLE_KSUSU_USER_SU
            required: False
        become_exe_ksu:
            description: C(ksu) executable.
            default: ksu
            ini:
              - section: privilege_escalation
                key: become_exe_ksu
              - section: ksusu_become_plugin
                key: executable_ksu
            vars:
              - name: ansible_become_exe_ksu
              - name: ansible_ksusu_exe_ksu
            env:
              - name: ANSIBLE_BECOME_EXE_KSU
              - name: ANSIBLE_KSU_EXE_KSU
        become_exe_su:
            description: Absolute path to the C(su) executable.
            default: /bin/su
            ini:
              - section: privilege_escalation
                key: become_exe_su
              - section: ksusu_become_plugin
                key: executable_su
            vars:
              - name: ansible_become_exe_su
              - name: ansible_ksusu_exe_su
            env:
              - name: ANSIBLE_BECOME_EXE
              - name: ANSIBLE_BECOME_EXE_SU
              - name: ANSIBLE_KSUSU_EXE_SU
        become_flags_ksu:
            description: Options to pass to C(ksu).
            default: '-Z -q'
            ini:
              - section: privilege_escalation
                key: become_flags_ksu
              - section: ksusu_become_plugin
                key: flags_ksu
            vars:
              - name: ansible_become_flags_ksu
              - name: ansible_ksusu_flags_ksu
            env:
              - name: ANSIBLE_BECOME_FLAGS_KSU
              - name: ANSIBLE_KSU_FLAGS_KSU
        become_flags:
            description: Options to pass to C(su).
            default: ''
            ini:
              - section: privilege_escalation
                key: become_flags
              - section: privilege_escalation
                key: become_flags_su
              - section: ksusu_become_plugin
                key: flags_su
            vars:
              - name: ansible_become_flags
              - name: ansible_become_flags_su
              - name: ansible_ksusu_flags
              - name: ansible_ksusu_flags_su
            env:
              - name: ANSIBLE_BECOME_FLAGS
              - name: ANSIBLE_BECOME_FLAGS_SU
              - name: ANSIBLE_KSU_FLAGS_SU
        become_pass:
            description: C(ksu) password.
            required: False
            vars:
              - name: ansible_ksusu_pass
              - name: ansible_become_pass
              - name: ansible_become_password
            env:
              - name: ANSIBLE_BECOME_PASS
              - name: ANSIBLE_KSUSU_PASS
            ini:
              - section: ksusu_become_plugin
                key: password
        prompt_l10n:
            description:
                - List of localized strings to match for prompt detection.
            default: ['Kerberos password for .*@.*:']
            default: ['Kerberos password for .*@.*:']
            ini:
              - section: ksusu_become_plugin
                key: localized_prompts
            vars:
              - name: ansible_ksusu_prompt_l10n
            env:
              - name: ANSIBLE_KSUSU_PROMPT_L10N
"""

import re

from ansible.module_utils.common.text.converters import to_bytes
from ansible.plugins.become import BecomeBase


class BecomeModule(BecomeBase):

    name = 'community.general.ksusu'

    # messages for detecting prompted password issues
    fail = ('Password incorrect',)
    missing = ('No password given',)

    def check_password_prompt(self, b_output):
        ''' checks if the expected password prompt exists in b_output '''

        prompts = self.get_option('prompt_l10n')
        b_prompt = b"|".join(to_bytes(p) for p in prompts)

        return bool(re.match(b_prompt, b_output))

    def build_become_command(self, cmd, shell):

        super(BecomeModule, self).build_become_command(cmd, shell)

        # Prompt handling for ``ksu`` is more complicated, this
        # is used to satisfy the connection plugin
        self.prompt = True

        if not cmd:
            return cmd

        # defaults come from above via configuration manager
        exe_ksu = self.get_option('become_exe_ksu')
        exe_su = self.get_option('become_exe_su')
        flags_ksu = self.get_option('become_flags_ksu')
        flags_su = self.get_option('become_flags')
        user_ksu = self.get_option('become_user_ksu')
        user_su = self.get_option('become_user')

        return '%s %s %s -e %s -l %s %s %s ' % (exe_ksu, user_ksu, flags_ksu, exe_su, flags_su, user_su, self._build_success_command(cmd, shell))

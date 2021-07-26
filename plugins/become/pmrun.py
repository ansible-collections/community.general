# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: pmrun
    short_description: Privilege Manager run
    description:
        - This become plugins allows your remote/login user to execute commands as another user via the pmrun utility.
    author: Ansible Core Team
    options:
        become_exe:
            description: Sudo executable
            default: pmrun
            ini:
              - section: privilege_escalation
                key: become_exe
              - section: pmrun_become_plugin
                key: executable
            vars:
              - name: ansible_become_exe
              - name: ansible_pmrun_exe
            env:
              - name: ANSIBLE_BECOME_EXE
              - name: ANSIBLE_PMRUN_EXE
        become_flags:
            description: Options to pass to pmrun
            default: ''
            ini:
              - section: privilege_escalation
                key: become_flags
              - section: pmrun_become_plugin
                key: flags
            vars:
              - name: ansible_become_flags
              - name: ansible_pmrun_flags
            env:
              - name: ANSIBLE_BECOME_FLAGS
              - name: ANSIBLE_PMRUN_FLAGS
        become_pass:
            description: pmrun password
            required: False
            vars:
              - name: ansible_become_password
              - name: ansible_become_pass
              - name: ansible_pmrun_pass
            env:
              - name: ANSIBLE_BECOME_PASS
              - name: ANSIBLE_PMRUN_PASS
            ini:
              - section: pmrun_become_plugin
                key: password
    notes:
      - This plugin ignores the become_user supplied and uses pmrun's own configuration to select the user.
'''

from ansible.plugins.become import BecomeBase
from ansible.module_utils.six.moves import shlex_quote


class BecomeModule(BecomeBase):

    name = 'community.general.pmrun'
    prompt = 'Enter UPM user password:'

    def build_become_command(self, cmd, shell):
        super(BecomeModule, self).build_become_command(cmd, shell)

        if not cmd:
            return cmd

        become = self.get_option('become_exe')

        flags = self.get_option('become_flags')
        return '%s %s %s' % (become, flags, shlex_quote(self._build_success_command(cmd, shell)))

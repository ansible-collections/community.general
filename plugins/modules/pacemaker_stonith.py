#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_stonith
short_description: Manage pacemaker STONITH
author:
  - Dexter Le (@munchtoast)
version_added: 11.1.0
description:
  - This module can manage STONITH in a Pacemaker cluster using the pacemaker CLI.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicate desired state for cluster STONITH.
    choices: [ present, absent, enabled, disabled ]
    default: present
    type: str
  name:
    description:
      - Specify the STONITH name to create.
    required: true
    type: str
  stonith_type:
    description:
      - Specify the STONITH device type
    type: str
  stonith_options:
    description:
      - Specify the STONITH option to create.
    type: list
    elements: str
    default: []
  stonith_operations:
    description:
      - List of operations to associate with STONITH.
    type: list
    elements: dict
    default: []
    suboptions:
      operation_action:
        description:
          - Operation action to associate with STONITH.
        type: str
      operation_options:
        description:
          - Operation option to associate with action.
        type: list
        elements: str
  stonith_metas:
    description:
      - List of meta to associate with STONITH.
    type: list
    elements: str
  stonith_argument:
    description:
      - Action to associate with STONITH.
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to STONITH.
        type: str
        choices: [ group, before, after ]
      argument_options:
        description:
          - Options to associate with STONITH action.
        type: list
        elements: str
  agent_validation:
    description:
      - enabled agent validation for STONITH creation.
    type: bool
    default: false
  wait:
    description:
      - Timeout period for polling the STONITH creation.
    type: int
    default: 300
'''

EXAMPLES = '''
---
- name: Create pacemaker STONITH
  hosts: localhost
  gather_facts: false
  tasks:
  - name: Create virtual-ip STONITH
    community.general.pacemaker_stonith:
      state: present
      name: virtual-stonith
      stonith_type: fence_virt
      stonith_options:
        - "pcmk_host_list=f1"
      stonith_operations:
        - operation_action: monitor
          operation_options:
            - "interval=30s"
'''

RETURN = '''
cluster_stonith:
    description: The cluster STONITH output message.
    type: str
    sample: ""
    returned: always
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner


class PacemakerStonith(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=[
                'present', 'absent', 'enabled', 'disabled']),
            name=dict(type='str', required=True),
            stonith_type=dict(type='str'),
            stonith_options=dict(type='list', elements='str', default=list()),
            stonith_operations=dict(type='list', elements='dict', default=list(), options=dict(
                operation_action=dict(type='str'),
                operation_options=dict(type='list', elements='str'),
            )),
            stonith_metas=dict(type='list', elements='str'),
            stonith_argument=dict(type='dict', options=dict(
                argument_action=dict(type='str', choices=['before', 'after', 'group']),
                argument_options=dict(type='list', elements='str'),
            )),
            agent_validation=dict(type='bool', default=False),
            wait=dict(type='int', default=300),
        ),
        required_if=[('state', 'present', ['stonith_type', 'stonith_options'])],
        supports_check_mode=True
    )

    use_old_vardict = False
    default_state = "present"

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module, cli_action='stonith')
        self.vars.set('previous_value', self._get())
        self.vars.set('value', self.vars.previous_value, change=True, diff=True)

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise('pcs failed with error (rc={0}): {1}'.format(rc, err))
            out = out.rstrip()
            return None if out == "" else out
        return process

    def _get(self):
        with self.runner('state name', output_process=self._process_command_output(False)) as ctx:
            return ctx.run(state='status')

    def _fmt_stonith_resource(self):
        return dict([("resource_name", self.vars.stonith_type)])

    # TODO: Pluralize operation_options in separate PR and remove this helper fmt function
    def _fmt_stonith_operations(self):
        modified_stonith_operations = []
        for stonith_operation in self.vars.stonith_operations:
            modified_stonith_operations.append(dict([("operation_action", stonith_operation.get('operation_action')),
                                                    ("operation_option", stonith_operation.get('operation_options'))]))
        return modified_stonith_operations

    def state_absent(self):
        with self.runner('state name', output_process=self._process_command_output(True, "does not exist"), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_present(self):
        with self.runner(
                'state name resource_type resource_option resource_operation resource_meta resource_argument agent_validation wait',
                output_process=self._process_command_output(True, "already exists"),
                check_mode_skip=True) as ctx:
            ctx.run(resource_type=self._fmt_stonith_resource(),
                    resource_option=self.vars.stonith_options,
                    resource_operation=self._fmt_stonith_operations(),
                    resource_meta=self.vars.stonith_metas,
                    resource_argument=self.vars.stonith_argument)
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_enabled(self):
        with self.runner('state name', output_process=self._process_command_output(True, "Starting"), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_disabled(self):
        with self.runner('state name', output_process=self._process_command_output(True, "Stopped"), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd


def main():
    PacemakerStonith.execute()


if __name__ == '__main__':
    main()

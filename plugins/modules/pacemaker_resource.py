#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: pacemaker_resource
short_description: Manage pacemaker resources
author:
  - Dexter Le (@munchtoast)
version_added: 10.5.0
description:
  - This module can manage resources in a Pacemaker cluster using the pacemaker CLI.
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
      - Indicate desired state for cluster resource.
    choices: [present, absent, enabled, disabled]
    default: present
    type: str
  name:
    description:
      - Specify the resource name to create.
    required: true
    type: str
  resource_type:
    description:
      - Resource type to create.
    type: dict
    suboptions:
      resource_name:
        description:
          - Specify the resource type name.
        type: str
      resource_standard:
        description:
          - Specify the resource type standard.
        type: str
      resource_provider:
        description:
          - Specify the resource type providers.
        type: str
  resource_option:
    description:
      - Specify the resource option to create.
    type: list
    elements: str
    default: []
  resource_operation:
    description:
      - List of operations to associate with resource.
    type: list
    elements: dict
    default: []
    suboptions:
      operation_action:
        description:
          - Operation action to associate with resource.
        type: str
      operation_option:
        description:
          - Operation option to associate with action.
        type: list
        elements: str
  resource_meta:
    description:
      - List of meta to associate with resource.
    type: list
    elements: str
  resource_argument:
    description:
      - Action to associate with resource.
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to resource.
        type: str
        choices: [clone, master, group, promotable]
      argument_option:
        description:
          - Options to associate with resource action.
        type: list
        elements: str
  wait:
    description:
      - Timeout period for polling the resource creation.
    type: int
    default: 300
"""

EXAMPLES = r"""
---
- name: Create pacemaker resource
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create virtual-ip resource
      community.general.pacemaker_resource:
        state: present
        name: virtual-ip
        resource_type:
          resource_name: IPaddr2
        resource_option:
          - "ip=[192.168.2.1]"
        resource_argument:
          argument_action: group
          argument_option:
            - master
        resource_operation:
          - operation_action: monitor
            operation_option:
              - interval=20
"""

RETURN = r"""
cluster_resources:
  description: The cluster resource output message.
  type: str
  sample: "Assumed agent name ocf:heartbeat:IPaddr2 (deduced from IPaddr2)"
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner


class PacemakerResource(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=[
                'present', 'absent', 'enabled', 'disabled']),
            name=dict(type='str', required=True),
            resource_type=dict(type='dict', options=dict(
                resource_name=dict(type='str'),
                resource_standard=dict(type='str'),
                resource_provider=dict(type='str'),
            )),
            resource_option=dict(type='list', elements='str', default=list()),
            resource_operation=dict(type='list', elements='dict', default=list(), options=dict(
                operation_action=dict(type='str'),
                operation_option=dict(type='list', elements='str'),
            )),
            resource_meta=dict(type='list', elements='str'),
            resource_argument=dict(type='dict', options=dict(
                argument_action=dict(type='str', choices=['clone', 'master', 'group', 'promotable']),
                argument_option=dict(type='list', elements='str'),
            )),
            wait=dict(type='int', default=300),
        ),
        required_if=[('state', 'present', ['resource_type', 'resource_option'])],
        supports_check_mode=True,
    )
    use_old_vardict = False
    default_state = "present"

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module, cli_action='resource')
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

    def state_absent(self):
        with self.runner('state name', output_process=self._process_command_output(True, "does not exist"), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_present(self):
        with self.runner(
                'state name resource_type resource_option resource_operation resource_meta resource_argument wait',
                output_process=self._process_command_output(True, "already exists"),
                check_mode_skip=True) as ctx:
            ctx.run()
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
    PacemakerResource.execute()


if __name__ == '__main__':
    main()

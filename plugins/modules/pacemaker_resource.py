#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_resource
short_description: Manage pacemaker resources
author:
  - Dexter Le (@munchtoast)
version_added: 10.3.0
description:
  - This module can manage resources to a pacemaker cluster from Ansible using
    the pacemaker cli.
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
    choices: [ present, absent ]
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
      - Actions to associate with resource.
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to resource.
        type: str
        choices: [ clone, master, group, promotable ]
      argument_option:
        description:
          - Options to associate with resource action.
        type: list
        elements: str
  disabled:
    description:
      - Specify argument to disable resource.
    type: bool
    default: false
  wait:
    description:
      - Timeout period for polling the resource creation.
    type: int
    default: 300
'''

EXAMPLES = '''
---
- name: Create pacemaker resource
  hosts: localhost
  gather_facts: false
  tasks:
  - name: Create virtual-ip resource
    community.general.pacemaker_resource:
      state: create
      name: virtual-ip
      resource_type:
        resource_name: IPaddr2
      resource_option:
        - "ip=[192.168.1.2]"
      resource_argument:
        argument_action: group
        argument_option:
          - master
      resource_operation:
        - operation_action: monitor
          operation_option:
            - interval=20
'''

RETURN = '''
cluster_resources:
    description: The cluster resource output message.
    type: str
    sample: "Assumed agent name ocf:heartbeat:IPaddr2 (deduced from IPaddr2)"
    returned: always
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner


class PacemakerResource(StateModuleHelper):
    change_params = ('name', )
    diff_params = ('name', )
    output_params = ('status')
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=[
                'present', 'absent']),
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
                argument_action=dict(type='str', choices=[
                                   'clone', 'master', 'group', 'promotable']),
                argument_option=dict(type='list', elements='str'),
            )),
            disabled=dict(type='bool', default=False),
            wait=dict(type='int', default=300),
        ),
        required_if=[('state', 'present', ['resource_type', 'resource_option'])],
        required_together=[('state', 'present', ['resource_type', 'resource_option'])],
        supports_check_mode=True
    )
    use_old_vardict = False
    default_state = "present"

    def process_command_output(self, rc, out, err):
        if err.rstrip() == self.does_not:
            return None
        if rc or len(err):
            self.do_raise(
                'pcs failed with error (rc={0}): {1}'.format(rc, err))

        result = out.rstrip()
        if "Value is an array with" in result:
            result = result.split("\n")
            result.pop(0)
            result.pop(0)

        return result

    # Builds list with command to run
    def _build_resource_operation(self):
        cmd = []
        for op in self.vars.resource_operation:
            cmd.append("op")
            cmd.append(op.get('operation_action'))
            for operation_option in op.get('operation_option'):
                cmd.append(operation_option)

        return cmd

    def _build_resource_meta(self):
        return ["meta {0}".format(m) for m in self.vars.resource_meta]

    def _build_resource_argument(self):
        cmd = []
        if self.vars.resource_argument.get('argument_action') == 'group':
            cmd.append('--group')
        else:
            cmd.append(self.vars.resource_argument.get('argument_action'))
        return cmd + list(self.vars.resource_argument.get('argument_option'))

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.does_not = 'Pacemaker resource "{0}" does not exist or cannot be created'.format(
            self.vars.name)
        self.vars.set('previous_status', self._get())
        self.vars.set_meta('status', initial_value=self.vars.previous_status)

    def _get(self):
        with self.runner('state name', output_process=self.process_command_output) as ctx:
            return ctx.run(state='status', name=self.vars.name)

    def state_absent(self):
        with self.runner('state name', check_mode_skip=True) as ctx:
            ctx.run(state=self.vars.state, name=self.vars.name)
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd
        self.vars.value = None

    def state_present(self):
        # Build out our command lists here
        self.vars.set('resource_type', self.vars.resource_type.get('resource_standard') +
                      self.vars.resource_type.get('provider') + self.vars.resource_type.get('resource_name'))
        self.vars.set('resource_option', self.vars.resource_option)
        self.vars.set('resource_operation', self._build_resource_operation)
        self.vars.set('resource_meta', self._build_resource_meta)
        self.vars.set('resource_argument', self._build_resource_argument)

        with self.runner(
                'state name resource_type resource_option resource_operation resource_meta resource_argument disabled wait',
                check_mode_skip=True) as ctx:
            ctx.run(
                state=self.vars.state,
                name=self.vars.name,
                resource_type=self.vars.resource_type,
                resource_option=self.vars.resource_option,
                resource_operation=self.vars.resource_operation,
                resource_meta=self.vars.resource_meta,
                resource_argument=self.resource_argument,
                disabled=self.vars.disabled,
                wait=self.vars.wait)


def main():
    PacemakerResource.execute()


if __name__ == '__main__':
    main()

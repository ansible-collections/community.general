#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Mathieu Bultel <mbultel@redhat.com>
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
      - Indicate which actions to take for resources
    choices: [ create, delete, status ]
    required: true
    type: str
  name:
    description:
      - Specify the resource name to create
    aliases: [ resource_id ]
    required: true
    type: str
  resource_type:
    description:
      - Resource type to create
    aliases: [ type ]
    type: dict
    suboptions:
      resource_name:
        description:
          - Resource type name
        type: str
      resource_standard:
        description:
          - Resource type standard
        type: str
      resource_provider:
        description:
          - Resource type provider
        type: str
  resource_option:
    description:
      - Resource option to create
    aliases: [ option ]
    type: list
    elements: str
    default: []
  resource_operation:
    description:
      - List of operations to associate with resource
    aliases: [ op ]
    type: list
    elements: dict
    default: []
    suboptions:
      operation_action:
        description:
          - Operation action to associate with resource
        type: str
      operation_option:
        description:
          - Operation option to associate with action
        type: list
        elements: str
  resource_meta:
    description:
      - List of meta to associate with resource
    type: list
    elements: str
  resource_argument:
    description:
      - Actions to associate with resource
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to resource
        type: str
        choices: [ clone, master, group, promotable ]
      argument_option:
        description:
          - Option to associate with resource action
        type: list
        elements: str
  disabled:
    description:
      - Argument to disable resource
    type: bool
    default: false
  wait:
    description:
      - Integer to determine poll on resource creation
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
changed:
    description: true if the cluster resource state has changed
    type: bool
    returned: always
out:
    description: The output of the resource state of the cluster.
    type: str
    sample: 'out: [["  Assumed agent name ocf:heartbeat:IPaddr2 (deduced from IPaddr2)"]]}'
    returned: always
rc:
    description: exit code of the module
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule


def get_cluster_resource_status(module, name):
    cmd = "pcs status resources %s" % name
    rc, out, err = module.run_command(cmd)
    status = []
    for o in out.splitlines():
        status.append(o.split(':'))
    return rc, status


def delete_cluster_resource(module, name):
    cmd = "pcs resource delete %s" % name
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(
            msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))
    status = []
    for o in out.splitlines():
        status.append(o.split(':'))
    return status


def create_cluster_resource(module, resource_name,
                            resource_type, resource_option, resource_operation,
                            resource_meta, resource_argument, disabled,
                            wait):
    cmd = "pcs resource create %s " % resource_name

    if resource_type.get('resource_standard') is not None:
        cmd += "%s:" % resource_type.get('resource_standard')
        cmd += "%s:" % resource_type.get('resource_provider') if resource_type.get('resource_provider') is not None else ""
    cmd += "%s " % resource_type.get('resource_name')

    if resource_option is not None:
        for option in resource_option:
            cmd += "%s " % option

    if resource_operation is not None:
        for op in resource_operation:
            cmd += "op %s " % op.get('operation_action')
            for operation_option in op.get('operation_option'):
                cmd += "%s " % operation_option

    if resource_meta is not None:
        for m in resource_meta:
            cmd += "meta %s " % m

    if resource_argument is not None:
        if resource_argument.get('argument_action') == "group":
            cmd += "--"
        cmd += "%s " % resource_argument.get('argument_action')
        for option_argument in resource_argument.get('argument_option'):
            cmd += "%s " % option_argument

    cmd += "--disabled " if disabled else ""
    cmd += "--wait=%d" % wait if wait > 0 else ""

    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(
            msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))
    status = []
    for o in out.splitlines():
        status.append(o.split(':'))
    return status


def main():
    argument_spec = dict(
        state=dict(type='str', choices=[
                   'create', 'delete', 'status'], required=True),
        name=dict(type='str', aliases=['resource_id'], required=True),
        resource_type=dict(type='dict', aliases=['type'], options=dict(
            resource_name=dict(type='str', default=None),
            resource_standard=dict(type='str', default=None),
            resource_provider=dict(type='str', default=None),
        )),
        resource_option=dict(type='list', elements='str', default=list(), aliases=['option']),
        resource_operation=dict(type='list', elements='dict', default=list(), aliases=['op'], options=dict(
            operation_action=dict(type='str', default=None),
            operation_option=dict(type='list', elements='str', default=None),
        )),
        resource_meta=dict(type='list', elements='str', default=None),
        resource_argument=dict(type='dict', default=None, options=dict(
            argument_action=dict(type='str', default=None, choices=['clone', 'master', 'group', 'promotable']),
            argument_option=dict(type='list', elements='str', default=None),
        )),
        disabled=dict(type='bool', default=False),
        wait=dict(type='int', default=300),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    state = module.params['state']
    resource_name = module.params['name']
    resource_type = module.params['resource_type']
    resource_option = module.params['resource_option']
    resource_operation = module.params['resource_operation']
    resource_meta = module.params['resource_meta']
    resource_argument = module.params['resource_argument']
    disabled = module.params['disabled']
    wait = module.params['wait']

    if state in ['create']:
        if module.check_mode:
            module.exit_json(changed=True)
        rc, initial_cluster_resource_state = get_cluster_resource_status(
            module, resource_name)
        if rc:
            create_cluster_resource(module, resource_name, resource_type, resource_option,
                                    resource_operation, resource_meta, resource_argument, disabled, wait)
        else:
            module.exit_json(changed=False, out=initial_cluster_resource_state)
        rc, final_cluster_resource_state = get_cluster_resource_status(
            module, resource_name)
        if not rc:
            module.exit_json(changed=True, out=final_cluster_resource_state)
        else:
            module.fail_json(
                msg="Failed to create cluster resource: %s" % final_cluster_resource_state)

    if state in ['status']:
        if module.check_mode:
            module.exit_json(changed=False)
        rc, cluster_resource_state = get_cluster_resource_status(module, resource_name)
        if not rc:
            module.exit_json(changed=False, out=cluster_resource_state)
        else:
            module.fail_json(
                msg="Failed to obtain cluster resource status")

    if state in ['delete']:
        rc, initial_cluster_resource_state = get_cluster_resource_status(
            module, resource_name)
        if not rc:
            if module.check_mode:
                module.exit_json(changed=True)
            delete_cluster_resource(module, resource_name)
        else:
            module.exit_json(changed=False, out=initial_cluster_resource_state)
        rc, final_cluster_resource_state = get_cluster_resource_status(
            module, resource_name)
        if not rc:
            module.fail_json(
                msg="Failed to delete cluster resource: %s" % final_cluster_resource_state)
        else:
            module.exit_json(changed=True, out=final_cluster_resource_state)


if __name__ == '__main__':
    main()

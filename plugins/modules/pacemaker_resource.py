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
      name:
        description:
          - Resource type name
        type: str
      standard:
        description:
          - Resource type standard
        type: str
      provider:
        description:
          - Resource type provider
        type: str
  resource_option:
    description:
      - Resource option to create
    aliases: [ option ]
    type: str
  operation:
    description:
      - List of operations to associate with resource
    aliases: [ op ]
    type: list
    elements: dict
    default: []
    suboptions:
      action:
        description:
          - Operation action to associate with resource
        type: str
      option:
        description:
          - Operation option to associate with action
        type: str
  meta:
    description:
      - List of meta to associate with resource
    type: list
    elements: str
  action:
    description:
      - Actions to associate with resource
    type: dict
    default: {}
    suboptions:
      state:
        description:
          - State to apply to resource
        type: str
        choices: [ clone, master ]
      option:
        description:
          - Option to associate with resource action
        type: str
  group:
    description:
      - Group to associate with resource
    type: str
  order:
    description:
    - Order to associate with resource
    type: dict
    default: {}
    suboptions:
      state:
        description:
          - Order state to associate with resource
        type: str
        choices: [ before, after ]
      resource_id:
        description:
          - Other resource to associate created resource based on order
        type: str
  bundle:
    description:
      - Bundle to associate with resource
    type: str
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
        name: IPaddr2
      resource_option: "ip=[192.168.1.2]"
      group: master
'''

RETURN = '''
changed:
    description: true if the cluster resource state has changed
    type: bool
    returned: always
out:
    description: The output of the current state of the cluster. It return a
                 list of the nodes state.
    type: str
    sample: 'out: [["  overcloud-controller-0", " Online"]]}'
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


def create_cluster_resource(module, name,
                            resource_type, resource_option, operation,
                            meta, action, group,
                            order, bundle, disabled,
                            wait):
    cmd = "pcs resource create %s " % name

    if resource_type.get('standard') is not None:
        cmd += "%s:" % resource_type.get('standard')
        cmd += "%s:" % resource_type.get('provider') if resource_type.get('provider') is not None else ""
    cmd += "%s " % resource_type.get('name')

    if resource_option is not None:
        for option in resource_option:
            cmd += "%s " % option

    if operation is not None:
        for op in operation:
            cmd += "op %s " % op.get('action')
            cmd += "%s " % op.get('option') if op.get('option') is not None else ""

    if meta is not None:
        for m in meta:
            cmd += "meta %s " % m

    if action:
        cmd += "%s " % action.get('state')
        if action.get('option') is not None:
            for option in action.get('option'):
                cmd += "%s " % option

    cmd += "--group %s " % group if group is not None else ""
    cmd += "%s %s " % (order.get('state'),
                       order.get('resource_id')) if not order else ""
    cmd += "bundle %s " % bundle if bundle is not None else ""
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
        # TODO don't know if it makes sense to have this as "name"
        name=dict(type='str', aliases=['resource_id'], required=True),
        resource_type=dict(type='dict', aliases=['type'], options=dict(
            name=dict(type='str', default=None),
            standard=dict(type='str', default=None),
            provider=dict(type='str', default=None),
        )),
        resource_option=dict(type='list', elements='str', default=list(), aliases=['option']),
        operation=dict(type='list', elements='dict', default=list(), aliases=['op'], options=dict(
            action=dict(type='str', default=None),
            option=dict(type='str', default=None),
        )),
        meta=dict(type='list', elements='str', default=None),
        action=dict(type='dict', default=dict(), options=dict(
            state=dict(type='str',
                       choices=['clone', 'master']),
            option=dict(type='list', elements='str', default=list()), #This should actually be a list of str
        )),
        group=dict(type='str', default=None),
        order=dict(type='dict', default=dict(), options=dict(
            state=dict(type='str',
                       choices=['before', 'after']),
            resource_id=dict(type='str', default=None),
        )),
        bundle=dict(type='str', default=None),
        disabled=dict(type='bool', default=False),
        wait=dict(type='int', default=300),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    state = module.params['state']
    name = module.params['name']
    resource_type = module.params['resource_type']
    resource_option = module.params['resource_option']
    operation = module.params['operation']
    meta = module.params['meta']
    action = module.params['action']
    group = module.params['group']
    order = module.params['order']
    bundle = module.params['bundle']
    disabled = module.params['disabled']
    wait = module.params['wait']

    if state in ['create']:
        if module.check_mode:
            module.exit_json(changed=True)
        rc, initial_cluster_resource_state = get_cluster_resource_status(
            module, name)
        if rc:
            create_cluster_resource(module, name, resource_type, resource_option,
                                    operation, meta, action, group, order, bundle, disabled, wait)
        else:
            module.exit_json(changed=False, out=initial_cluster_resource_state)
        rc, final_cluster_resource_state = get_cluster_resource_status(
            module, name)
        if not rc:
            module.exit_json(changed=True, out=final_cluster_resource_state)
        else:
            module.fail_json(
                msg="Failed to create cluster resource: %s" % final_cluster_resource_state)

    if state in ['status']:
        if module.check_mode:
            module.exit_json(changed=False)
        rc, cluster_resource_state = get_cluster_resource_status(module, name)
        if not rc:
            module.exit_json(changed=False, out=cluster_resource_state)
        else:
            module.fail_json(
                msg="Failed to obtain cluster resource status")

    if state in ['delete']:
        rc, initial_cluster_resource_state = get_cluster_resource_status(
            module, name)
        if not rc:
            if module.check_mode:
                module.exit_json(changed=True)
            delete_cluster_resource(module, name)
        else:
            module.exit_json(changed=False, out=initial_cluster_resource_state)
        rc, final_cluster_resource_state = get_cluster_resource_status(
            module, name)
        if not rc:
            module.fail_json(
                msg="Failed to delete cluster resource: %s" % final_cluster_resource_state)
        else:
            module.exit_json(changed=True, out=final_cluster_resource_state)


if __name__ == '__main__':
    main()

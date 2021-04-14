#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Hani Audah <ht.audah@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_resource
short_description: Manage pacemaker resources
author:
- Hani Audah (@haudah)
description:
   - This module can manage pacemaker resources from Ansible using
     the pacemaker cli.
options:
    state:
      description:
        - Indicate desired state of the resource
      choices: [ present, absent, disabled, enabled ]
      type: str
    name:
      description:
        - The unique name that will be used to identify this resource after creation.
      type: str
    attributes:
      description:
        - The resource attributes to be assigned to the resource
      type: str
    operations:
      description:
        - Used to specify the intervals and/or timeouts for monitoring, start, and stop
          operations on a resource.
      type: dict
    force:
      description:
        - Force the change of the stonith device creation/deletion
      type: bool
      default: 'yes'
'''
EXAMPLES = '''
---
- name: Create resource
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Create resource
    community.general.pacemaker_resource:
      state: present
      operations:
        start:
          interval: 0
          timeout: 10
        monitor:
          interval: 30
      location_constraints:
        - node: node1
          score: 5
'''

RETURN = '''
changed:
    description: True if the stonith device state has changed
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

import time, re

from ansible.module_utils.basic import AnsibleModule


_RESOURCE_NOT_FOUND = "Error: unable to find resource"

def create_resource_constraints(module, resource_name, constraints):
    # Get all existing location constraints
    cmd = "pcs constraint location show %s" % resource_name
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get location constraints for specified resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    existing_constraints = re.findall(r'Node: (\S+) \(score:.*?\)', out)
    # parse constraints into same format
    constraints = [(constraint.node, constraint.score) for constraint in constraints]
    # check if constraints are equivalent
    for existing_constraint in existing_constraints:
        # remove constraint from requested list
        if existing_constraint in constraints:
            constraints.remove(existing_constraint)
    if len(constraints) == 0:
        return False
    cmd = "pcs constraint location %s prefers %s" % (resource_name, " ".join(["%s=%s" % (x,y) for x,y in constraints])
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to create location constraint for specified resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True

def create_resource(module, name, resource_type, attributes, operations):
    exists = True
    cmd = "pcs resource config %s" % name
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        # Any error other than 'resource not found' should fail
        if not out.startswith(_RESOURCE_NOT_FOUND):
            module.fail_json(msg="Failed to get resource configuration.\nCommand: `%s`\nError: %s" % (cmd, err))
        # The resource doesn't exist, so it needs to be created with the specified attributes
        exists = False
    else:
        # if the device already exists, check its current attributes
        match_object = re.search(r'Resource:(?:.*?)\(class=(.*?)\sprovider=(.*?)\stype=(.*?)\)', out)
        existing_resource_type = "%s:%s:%s" % (match_object.group(1), match_object.group(2), match_object.group(3))
        if existing_resource_type != resource_type:
            module.fail_json(msg="A resource of a different type exists with the same name")

        match_object = re.search(r'Attributes: (.*?)\n', out)
        existing_attributes = match_object.group(1).strip().split(' ')
        existing_operations = re.findall(r'(monitor|start|stop) interval=(\d+)s', out)

        for attribute in existing_attributes:
            attribute_tuple = attribute.split('=')
            attribute_key = attribute_tuple[0]
            # remove single and double quotes from value for a proper comparison
            attribute_value = attribute_tuple[1].strip("'").strip('"')
            if attribute_key in attributes:
                if attribute_value == attributes[attribute_key]:
                    del attributes[attribute_key]

        for existing_operation in existing_operations:
            # check if it matches a requested operation
            for oper_key, oper_value in list(operations.items()):
                if existing_operation[0] == oper_key and existing_operation[1] == oper_value:
                    del operations[oper_key]

    if exists and len(attributes) == 0 and len(operations) == 0:
        # nothing needs to be done
        return False
    command_key = "update %s" % (name,) if exists else "create %s %s" % (name, resource_type)
    # this is for the resource attributes
    command_attributes = ["%s='%s'" % (key, val) for key, val in attributes.items()]
    command_attributes = " ".join(command_options)
    # and this is for the operations
    command_operations = ["%s interval=%ss" % (key, val) for key, val in operations.items()]
    command_operations = "op " + " ".join(command_operations)
    cmd = "pcs resource %s %s" % (command_key, command_attributes)
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to create or update resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def destroy_resource(module, name)
    exists = True
    cmd = "pcs resource config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        # Any error other than 'resource not found' should fail
        if not out.startswith(_RESOURCE_NOT_FOUND):
            module.fail_json(msg="Failed to get resource configuration.\nCommand: `%s`\nError: %s" % (cmd, err))
        # The resource doesn't exist, so nothing needs to be done
        return False

    cmd = "pcs resource remove %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to delete resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def enable_resource(module, name):
    cmd = "pcs resource config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get resource configuration.\nCommand: `%s`\nError: %s" % (cmd, err))

    # check if already enabled
    match_object = re.search(r'Meta Attrs: (.*)?target-role=Stopped', out)
    if match_object is None:
        # it's already enabled
        return False

    cmd = "pcs resource enable %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to enable resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def disable_resource(module, name):
    cmd = "pcs resource config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get resource configuration.\nCommand: `%s`\nError: %s" % (cmd, err))

    # check if already disabled
    match_object = re.search(r'Meta Attrs: (.*)?target-role=Stopped', out)
    if not(match_object is None):
        # it's already disabled
        return False

    cmd = "pcs resource disable %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to disable resource.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def main():
    argument_spec = dict(
        state=dict(type='str', choices=['present', 'absent', 'enabled', 'disabled']),
        name=dict(type='str'),
        type=dict(type='str'),
        force=dict(type='bool', default=True),
        attributes=dict(type='dict'),
        operations=dict(type='dict', options=dict(
            monitor=dict(type='dict', options=dict(
                timeout=dict(type='int'),
                interval=dict(type='int'),
            )),
            start=dict(type='dict', options=dict(
                timeout=dict(type='int'),
                interval=dict(type='int'),
            )),
            stop=dict(type='dict', options=dict(
                timeout=dict(type='int'),
                interval=dict(type='int'),
            )),
        )),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    name = module.params['name']
    type = module.params['type']
    state = module.params['state']
    force = module.params['force']
    attributes = module.params['attributes']
    operations = module.params['operations']

    if state == 'absent':
        # just delete the device if it exists
        changed = destroy_resource(module, name)
    elif state == 'present':
        # make sure it exists with the same configuration
        changed = create_resource(module, name, type, fencing_options)
        changed = changed or create_resource_constraints(module, name
    elif state == 'enabled':
        # Just enable the device if it exists
        changed = enable_resource(module, name)
    elif state == 'disabled':
        changed = disable_resource(module, name)
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()



#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Hani Audah <ht.audah@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_resource_group
short_description: Manage pacemaker resource groups
author:
- Hani Audah (@haudah)
description:
   - This module can manage pacemaker resource groups from Ansible using
     the pacemaker cli.
options:
    state:
      description:
        - Indicate desired state of the resource
      choices: [ present, absent ]
      type: str
    node:
      description:
        - Specify which node of the cluster you want to manage. None == the
          cluster status itself, 'all' == check the status of all nodes.
      type: str
    timeout:
      description:
        - Timeout when the module should considered that the action has failed
      default: 300
      type: int
    force:
      description:
        - Force the change of the stonith device creation/deletion
      type: bool
      default: 'yes'
'''
EXAMPLES = '''
---
- name: Create stonith device
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Create stonith device
    community.general.pacemaker_stonith_device:
      state: present
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

def create_resource_group(module, name, resources):
    cmd = "pcs resource group list"
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get resource group list.\nCommand: `%s`\nError: %s" % (cmd, err))
    # check if the group already exists
    match_object = re.search(r'%s: ((?: \S+)+)' % name, out)
    if match_object is None:
        # the resource group doesn't already exist; just create it with the specified order of resources
        cmd = "pcs resource group add %s %s" % (name, " --before ".join(resources))
        rc, out, err = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed to create or update resource.\nCommand: `%s`\nError: %s" % (cmd, err))
        return True

    # the resource group exists, so just check if order is not already correct
    existing_resources = match_object.group(1).strip().split(" ")
    correct_order = True
    if len(existing_resources) != len(resources):
        correct_order = False
    for existing_resource,resource in zip(existing_resources, resources):
        if existing_resource != resource:
            correct_order = False
            break

    if not correct_order:
        # just "recreate" the resource group with the correct order
        cmd = "pcs resource group add %s %s" % (name, " --before ".join(resources))
        rc, out, err = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed to create or update resource.\nCommand: `%s`\nError: %s" % (cmd, err))
        return True

    # otherwise the resources already exist in the correct order, and nothing needs to be changed
    return False


def main():
    argument_spec = dict(
        state=dict(type='str', choices=['present', 'absent', 'enabled', 'disabled']),
        name=dict(type='str'),
        type=dict(type='str'),
        timeout=dict(type='int', default=300),
        force=dict(type='bool', default=True),
        attributes=dict(type='dict'),
        operations=dict(type='dict', options=dict(
            monitor=dict(type='int'),
            start=dict(type='int'),
            stop=dict(type='int'),
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
    timeout = module.params['timeout']
    attributes = module.params['attributes']
    operations = module.params['operations']

    if state == 'absent':
        # just delete the device if it exists
        changed = destroy_resource(module, name)
    elif state == 'present':
        # make sure it exists with the same configuration
        changed = create_resource(module, name, type, fencing_options)
    elif state == 'enabled':
        # Just enable the device if it exists
        changed = disable_stonith_device(module, name)
    elif state == 'disabled':
        changed = enable_stonith_device(module, name)
    module.exit_json(changed=True, out=cluster_state)


if __name__ == '__main__':
    main()




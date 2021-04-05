#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Hani Audah <ht.audah@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_stonith_device
short_description: Manage pacemaker stonith devices
author:
- Hani Audah (@haudah)
description:
   - This module can manage pacemaker stonith devices from Ansible using
     the pacemaker cli.
options:
    state:
      description:
        - Indicate desired state of the stonith device
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


_PCS_CLUSTER_DOWN = "Error: cluster is not currently running on this node"
_STONITH_NOT_FOUND = "Error: unable to find resource"


def create_stonith_device(module, name, device_type, fencing_options):
    exists = True
    cmd = "pcs stonith config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        # Any error other than 'resource not found' should fail
        if not out.startswith(_STONITH_NOT_FOUND):
            module.fail_json(msg="Failed to get cluster configuration.\nCommand: `%s`\nError: %s" % (cmd, err))
        # The device doesn't exist, so it needs to be created with the specified options
        exists = False
    else:
        # if the device already exists, check its current options
        match_object = re.search(r'Resource: %s \(class=stonith type=(.*?)\)', out)
        existing_device_type = match_object.group(1).strip()
        if existing_device_type != device_type:
            module.fail_json(msg="A stonith device of a different type exists with the same name")
        match_object = search(r'Attributes: (.*?)\n', out)
        existing_options = match_object.group(1).strip().split(' ')

        for option in existing_options:
            option_tuple = option.split('=')
            option_key = option_tuple[0]
            # remove single and double quotes from value for a proper comparison
            option_value = option_tuple[1].strip("'").strip('"')
            if option_key in fencing_options:
                if option_value == fencing_options[option_key]:
                    del fencing_options[option_key]

    if exists and len(fencing_options) == 0:
        # nothing needs to be done
        return False
    command_key = "update %s" % (name,) if exists else "create %s %s" % (name, device_type)
    command_options = ["%s='%s'" % (key, val) for key, val in fencing_options.items()]
    command_options = " ".join(command_options)
    cmd = "pcs stonith %s %s" % (command_key, command_options)
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to create or update stonith device.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def destroy_stonith_device(module, name)
    exists = True
    cmd = "pcs stonith config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        # Any error other than 'resource not found' should fail
        if not out.startswith(_STONITH_NOT_FOUND):
            module.fail_json(msg="Failed to get cluster configuration.\nCommand: `%s`\nError: %s" % (cmd, err))
        # The device doesn't exist, so nothing needs to be done
        return False

    cmd = "pcs stonith remove %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to delete stonith device.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def enable_stonith_device(module, name):
    cmd = "pcs stonith config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get stonith device configuration.\nCommand: `%s`\nError: %s" % (cmd, err))

    # check if already enabled
    match_object = re.search(r'Meta Attrs: (.*)?target-role=Stopped', out)
    if match_object is None:
        # it's already enabled
        return False

    cmd = "pcs stonith enable %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to enable stonith device.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def disable_stonith_device(module, name):
    cmd = "pcs stonith config %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get stonith device configuration.\nCommand: `%s`\nError: %s" % (cmd, err))

    # check if already disabled
    match_object = re.search(r'Meta Attrs: (.*)?target-role=Stopped', out)
    if not(match_object is None):
        # it's already disabled
        return False

    cmd = "pcs stonith disable %s" % (name,)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to disable stonith device.\nCommand: `%s`\nError: %s" % (cmd, err))
    return True


def main():
    argument_spec = dict(
        state=dict(type='str', choices=['present', 'absent', 'enabled', 'disabled']),
        name=dict(type='str'),
        type=dict(type='str'),
        timeout=dict(type='int', default=300),
        force=dict(type='bool', default=True),
        fencing_options=dict(type='dict'),
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
    fencing_options = module.params['fencing_options']

    if state == 'absent':
        # just delete the device if it exists
        changed = destroy_stonith_device(module, name)
    elif state == 'present':
        # make sure it exists with the same configuration
        changed = create_stonith_device(module, name, type, fencing_options)
    elif state == 'enabled':
        # Just enable the device if it exists
        changed = disable_stonith_device(module, name)
    elif state == 'disabled':
        changed = enable_stonith_device(module, name)
    module.exit_json(changed=True, out=cluster_state)


if __name__ == '__main__':
    main()


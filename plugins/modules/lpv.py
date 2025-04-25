#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Klention Mali <klention@gmail.com>
# Based on lvol module by Jeroen Hoekx <jeroen.hoekx@dsquare.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: lpv
short_description: Manage LVM Physical Volumes
description:
  - Creates, resizes or removes LVM Physical Volumes.
author:
  - Klention Mali (@klention)
options:
  device:
    description:
      - Path to the block device to manage.
    type: str
    required: true
  state:
    description:
      - Control if the physical volume exists.
    type: str
    choices: [ present, absent ]
    default: present
  force:
    description:
      - Force dangerous operations (equivalent to C(pvcreate -f) or C(pvremove -ff)).
    type: bool
    default: false
  resize:
    description:
      - Resize PV to device size when state=present.
    type: bool
    default: false
notes:
  - Requires LVM2 utilities installed on the target system.
  - Device path must exist when creating a PV.
'''

EXAMPLES = r'''
- name: Creating physical volume on /dev/sdb
  community.general.lpv:
    device: /dev/sdb

- name: Resizing existing PV
  community.general.lpv:
    device: /dev/sdb
    resize: true

- name: Removing physical volume that is not part of any volume group
  community.general.lpv:
    device: /dev/sdb
    state: absent

- name: Force removing physical volume that is already part of a volume group
  community.general.lpv:
    device: /dev/sdb
    force: true
    state: absent
'''

RETURN = r'''
msg:
  description: Execution status message
  returned: always
  type: str
'''

import os
from ansible.module_utils.basic import AnsibleModule

def get_pv_status(module, device):
    """Check if the device is already a PV."""
    cmd = ['pvs', '--noheadings', '--readonly', device]
    return module.run_command(cmd)[0] == 0

def get_pv_size(module, device):
    """Get current PV size in bytes."""
    cmd = ['pvs', '--noheadings', '--nosuffix', '--units', 'b', '-o', 'pv_size', device]
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to get PV size: %s" % err)
    return int(out.strip())

def rescan_device(module, device):
    """Perform storage rescan for the device."""
    # Extract the base device name (e.g., /dev/sdb -> sdb)
    base_device = os.path.basename(device)
    rescan_path = f"/sys/block/{base_device}/device/rescan"
    
    if os.path.exists(rescan_path):
        try:
            with open(rescan_path, 'w') as f:
                f.write('1')
            return True
        except IOError as e:
            module.warn(f"Failed to rescan device {device}: {str(e)}")
            return False
    else:
        module.warn(f"Rescan path not found for device {device}")
        return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            force=dict(type='bool', default=False),
            resize=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    device = module.params['device']
    state = module.params['state']
    force = module.params['force']
    resize = module.params['resize']
    changed = False
    actions = []

    # Validate device existence for present state
    if state == 'present' and not os.path.exists(device):
        module.fail_json(msg="Device %s not found" % device)

    is_pv = get_pv_status(module, device)

    if state == 'present':
        # Create PV if needed
        if not is_pv:
            if module.check_mode:
                changed = True
                actions.append('created')
            else:
                cmd = ['pvcreate']
                if force:
                    cmd.append('-f')
                cmd.append(device)
                rc, out, err = module.run_command(cmd)
                if rc != 0:
                    module.fail_json(msg="Failed to create PV: %s" % err)
                changed = True
                actions.append('created')
            is_pv = True

        # Handle resizing
        if resize and is_pv:
            if not module.check_mode:
                # Perform device rescan if each time
                if rescan_device(module, device):
                    actions.append('rescanned')
                original_size = get_pv_size(module, device)
                rc, out, err = module.run_command(['pvresize', device])
                if rc != 0:
                    module.fail_json(msg="PV resize failed: %s" % err)
                new_size = get_pv_size(module, device)
                if new_size != original_size:
                    changed = True
                    actions.append('resized')
            else:
                # In check mode, assume resize would change
                changed = True
                actions.append('would be resized')

    elif state == 'absent':
        if is_pv:
            if module.check_mode:
                changed = True
                actions.append('would be removed')
            else:
                cmd = ['pvremove']
                if force:
                    cmd.extend(['-ff', '-y'])
                else:
                    cmd.append('-y')
                cmd.append(device)
                rc, out, err = module.run_command(cmd)
                if rc != 0:
                    module.fail_json(msg="Failed to remove PV: %s" % err)
                changed = True
                actions.append('removed')

    # Generate final message
    if not actions:
        msg = "No changes needed for PV %s" % device
    else:
        msg = "PV %s: %s" % (device, ', '.join(actions))

    module.exit_json(changed=changed, msg=msg)

if __name__ == '__main__':
    main()

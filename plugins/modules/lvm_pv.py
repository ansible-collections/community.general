#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Klention Mali <klention@gmail.com>
# Based on lvol module by Jeroen Hoekx <jeroen.hoekx@dsquare.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: lvm_pv
short_description: Manage LVM Physical Volumes
version_added: "11.0.0"
description:
  - Creates, resizes, removes LVM PVs, or moves data between them.
author:
  - Klention Mali (@klention)
options:
  device:
    description:
      - Path to the block device to manage.
      - Source device when O(state=move).
    type: path
    required: true
  state:
    description:
      - Control if the physical volume exists or if data should be move.
    type: str
    choices: [present, absent, move]
    default: present
  force:
    description:
      - Force the operation.
      - When O(state=present) (creating a PV), this uses C(pvcreate -f) to force creation.
      - When O(state=absent) (removing a PV), this uses C(pvremove -ff) to force removal even if part of a volume group.
    type: bool
    default: false
  resize:
    description:
      - Resize PV to device size when O(state=present).
    type: bool
    default: false
  dest_device:
    description:
      - Path to the destination block device when moving data (O(state=move)).
    type: path
notes:
  - Requires LVM2 utilities installed on the target system.
  - Device paths must exist when creating a PV or moving data.
  - For O(state=move), source and destination PVs must be in the same volume group.
  - When moving data, the destination PV must have enough free space to accommodate the source PV's allocated extents.
"""

EXAMPLES = r"""
- name: Creating physical volume on /dev/sdb
  community.general.lvm_pv:
    device: /dev/sdb

- name: Creating and resizing (if needed) physical volume
  community.general.lvm_pv:
    device: /dev/sdb
    resize: true

- name: Removing physical volume that is not part of any volume group
  community.general.lvm_pv:
    device: /dev/sdb
    state: absent

- name: Force removing physical volume that is already part of a volume group
  community.general.lvm_pv:
    device: /dev/sdb
    force: true
    state: absent

- name: Moving data from /dev/sdb to /dev/sdc (both in same VG)
  community.general.lvm_pv:
    device: /dev/sdb
    dest_device: /dev/sdc
    state: move
"""

RETURN = r"""
"""


import os
from ansible.module_utils.basic import AnsibleModule


def get_pv_status(module, device):
    """Check if the device is already a PV."""
    cmd = ['pvs', '--noheadings', '--readonly', device]
    return module.run_command(cmd)[0] == 0


def get_pv_size(module, device):
    """Get current PV size in bytes."""
    cmd = ['pvs', '--noheadings', '--nosuffix', '--units', 'b', '-o', 'pv_size', device]
    rc, out, err = module.run_command(cmd, check_rc=True)
    return int(out.strip())


def get_pv_vg(module, device):
    """Get the VG name of a PV."""
    cmd = ['pvs', '--noheadings', '-o', 'vg_name', device]
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to get VG for device %s: %s" % (device, err))
    vg = out.strip()
    return None if vg == '' else vg


def get_pv_allocated_pe(module, device):
    """Get count of allocated physical extents in a PV."""
    cmd = ['pvs', '--noheadings', '-o', 'pv_pe_alloc_count', device]
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to get allocated PE count for device %s: %s" % (device, err))
    try:
        return int(out.strip())
    except ValueError:
        module.fail_json(msg="Invalid allocated PE count for device %s: %s" % (device, out))


def get_pv_total_pe(module, device):
    """Get total number of physical extents in a PV."""
    cmd = ['pvs', '--noheadings', '-o', 'pv_pe_count', device]
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to get total PE count for device %s: %s" % (device, err))
    try:
        return int(out.strip())
    except ValueError:
        module.fail_json(msg="Invalid total PE count for device %s: %s" % (device, out))


def get_pv_free_pe(module, device):
    """Calculate free physical extents in a PV."""
    total_pe = get_pv_total_pe(module, device)
    allocated_pe = get_pv_allocated_pe(module, device)
    return total_pe - allocated_pe


def rescan_device(module, device):
    """Perform storage rescan for the device."""
    # Extract the base device name (e.g., /dev/sdb -> sdb)
    base_device = os.path.basename(device)
    rescan_path = "/sys/block/{0}/device/rescan".format(base_device)

    if os.path.exists(rescan_path):
        try:
            with open(rescan_path, 'w') as f:
                f.write('1')
            return True
        except IOError as e:
            module.warn("Failed to rescan device {0}: {1}".format(device, str(e)))
            return False
    else:
        module.warn("Rescan path not found for device {0}".format(device))
        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type='path', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent', 'move']),
            force=dict(type='bool', default=False),
            resize=dict(type='bool', default=False),
            dest_device=dict(type='path'),
        ),
        supports_check_mode=True,
        required_if=[
            ['state', 'move', ['dest_device']],
        ],
    )

    device = module.params['device']
    state = module.params['state']
    force = module.params['force']
    resize = module.params['resize']
    dest_device = module.params['dest_device']
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
                actions.append('would be created')
            else:
                cmd = ['pvcreate']
                if force:
                    cmd.append('-f')
                cmd.append(device)
                rc, out, err = module.run_command(cmd, check_rc=True)
                changed = True
                actions.append('created')
            is_pv = True

        # Handle resizing
        elif resize and is_pv:
            if module.check_mode:
                # In check mode, assume resize would change
                changed = True
                actions.append('would be resized')
            else:
                # Perform device rescan if each time
                if rescan_device(module, device):
                    actions.append('rescanned')
                original_size = get_pv_size(module, device)
                rc, out, err = module.run_command(['pvresize', device], check_rc=True)
                new_size = get_pv_size(module, device)
                if new_size != original_size:
                    changed = True
                    actions.append('resized')

    elif state == 'absent':
        if is_pv:
            if module.check_mode:
                changed = True
                actions.append('would be removed')
            else:
                cmd = ['pvremove', '-y']
                if force:
                    cmd.append('-ff')
                cmd.append(device)
                rc, out, err = module.run_command(cmd, check_rc=True)
                changed = True
                actions.append('removed')

    elif state == 'move':
        if not os.path.exists(device):
            module.fail_json(msg="Source device %s not found" % device)
        if not os.path.exists(dest_device):
            module.fail_json(msg="Destination device %s not found" % dest_device)
        if device == dest_device:
            module.fail_json(msg="Source and destination devices must be different")

        if not get_pv_status(module, device):
            module.fail_json(msg="Source device %s is not a PV" % device)
        if not get_pv_status(module, dest_device):
            module.fail_json(msg="Destination device %s is not a PV" % dest_device)

        vg_src = get_pv_vg(module, device)
        vg_dest = get_pv_vg(module, dest_device)
        if vg_src != vg_dest:
            module.fail_json(
                msg="Source and destination must be in the same VG. Source VG: '%s', Destination VG: '%s'." % (vg_src, vg_dest)
            )

        allocated = get_pv_allocated_pe(module, device)
        if allocated == 0:
            actions.append('no allocated extents to move')
        else:
            # Check if destination has enough free space
            free_pe_dest = get_pv_free_pe(module, dest_device)
            if free_pe_dest < allocated:
                module.fail_json(
                    msg="Destination device %s has only %d free physical extents, but source device %s has %d allocated extents. Not enough space." % 
                    (dest_device, free_pe_dest, device, allocated)
                )

            if module.check_mode:
                changed = True
                actions.append('would move data from %s to %s' % (device, dest_device))
            else:
                cmd = ['pvmove']
                rc, out, err = module.run_command(cmd + [device, dest_device], check_rc=True)
                changed = True
                actions.append('moved data from %s to %s' % (device, dest_device))

    if actions:
        msg = "PV %s: %s" % (device, ', '.join(actions))
    else:
        msg = "No changes needed for PV %s" % device
    module.exit_json(changed=changed, msg=msg)


if __name__ == '__main__':
    main()

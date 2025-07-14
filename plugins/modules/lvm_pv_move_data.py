#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Klention Mali <klention@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: lvm_pv_move_data
short_description: Move data between LVM Physical Volumes (PVs)
version_added: "11.2.0"
description:
  - Moves data from one LVM Physical Volume (PV) to another.
author:
  - Klention Mali (@klention)
options:
  source:
    description:
      - Path to the source block device to move data from.
      - Must be an existing PV.
    type: path
    required: true
  destination:
    description:
      - Path to the destination block device to move data to.
      - Must be an existing PV with enough free space.
    type: path
    required: true
notes:
  - Requires LVM2 utilities installed on the target system.
  - Both source and destination devices must exist.
  - Both source and destination PVs must be in the same volume group.
  - The destination PV must have enough free space to accommodate the source PV's allocated extents.
"""

EXAMPLES = r"""
- name: Moving data from /dev/sdb to /dev/sdc
  community.general.lvm_pv_move_data:
    source: /dev/sdb
    destination: /dev/sdc
"""

RETURN = r"""
"""


import os
from ansible.module_utils.basic import AnsibleModule


def get_pv_status(module, device):
    """Check if the device is already a PV."""
    cmd = ['pvs', '--noheadings', '--readonly', device]
    return module.run_command(cmd)[0] == 0


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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            source=dict(type='path', required=True),
            destination=dict(type='path', required=True),
        ),
        supports_check_mode=True,
    )

    source = module.params['source']
    destination = module.params['destination']
    changed = False
    actions = []

    # Validate device existence
    if not os.path.exists(source):
        module.fail_json(msg="Source device %s not found" % source)
    if not os.path.exists(destination):
        module.fail_json(msg="Destination device %s not found" % destination)
    if source == destination:
        module.fail_json(msg="Source and destination devices must be different")

    # Check both are PVs
    if not get_pv_status(module, source):
        module.fail_json(msg="Source device %s is not a PV" % source)
    if not get_pv_status(module, destination):
        module.fail_json(msg="Destination device %s is not a PV" % destination)

    # Check both are in the same VG
    vg_src = get_pv_vg(module, source)
    vg_dest = get_pv_vg(module, destination)
    if vg_src != vg_dest:
        module.fail_json(
            msg="Source and destination must be in the same VG. Source VG: '%s', Destination VG: '%s'." % (vg_src, vg_dest)
        )

    # Check source has data to move
    allocated = get_pv_allocated_pe(module, source)
    if allocated == 0:
        actions.append('no allocated extents to move')
    else:
        # Check destination has enough free space
        free_pe_dest = get_pv_free_pe(module, destination)
        if free_pe_dest < allocated:
            module.fail_json(
                msg="Destination device %s has only %d free physical extents, but source device %s has %d allocated extents. Not enough space." %
                (destination, free_pe_dest, source, allocated)
            )

        if module.check_mode:
            changed = True
            actions.append('would move data from %s to %s' % (source, destination))
        else:
            cmd = ['pvmove', source, destination]
            rc, out, err = module.run_command(cmd, check_rc=True)
            changed = True
            actions.append('moved data from %s to %s' % (source, destination))

    if actions:
        msg = "PV data move: %s" % ', '.join(actions)
    else:
        msg = "No data to move from %s" % source
    module.exit_json(changed=changed, msg=msg)


if __name__ == '__main__':
    main()

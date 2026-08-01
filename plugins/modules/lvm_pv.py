#!/usr/bin/python

# Copyright (c) 2025, Klention Mali <klention@gmail.com>
# Based on lvol module by Jeroen Hoekx <jeroen.hoekx@dsquare.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: lvm_pv
short_description: Manage LVM Physical Volumes
version_added: "11.0.0"
description:
  - Creates, resizes or removes LVM Physical Volumes.
author:
  - Klention Mali (@klention)
options:
  device:
    description:
      - Path to the block device to manage.
    type: path
    required: true
  state:
    description:
      - Control if the physical volume exists.
    type: str
    choices: [present, absent]
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
notes:
  - Requires LVM2 utilities installed on the target system.
  - Device path must exist when creating a PV.
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
"""

RETURN = r"""
"""


import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._lvm import (
    pvcreate_runner,
    pvremove_runner,
    pvresize_runner,
    pvs_runner,
)


def rescan_device(module, device):
    """Perform storage rescan for the device."""
    base_device = os.path.basename(device)
    is_partition = f"/sys/class/block/{base_device}/partition"

    # Determine parent device if partition exists
    parent_device = base_device
    if os.path.exists(is_partition):
        parent_device = (
            base_device.rpartition("p")[0] if base_device.startswith("nvme") else base_device.rstrip("0123456789")
        )

    # Determine rescan path
    rescan_path = (
        f"/sys/block/{parent_device}/device/{'rescan_controller' if base_device.startswith('nvme') else 'rescan'}"
    )

    if os.path.exists(rescan_path):
        try:
            with open(rescan_path, "w") as f:
                f.write("1")
            return True
        except OSError as e:
            module.warn(f"Failed to rescan device {device}: {e!s}")
    else:
        module.warn(f"Rescan path does not exist for device {device}")
        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type="path", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            force=dict(type="bool", default=False),
            resize=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    device = module.params["device"]
    state = module.params["state"]
    resize = module.params["resize"]
    changed = False
    actions = []

    pvs = pvs_runner(module)
    pvcreate = pvcreate_runner(module)
    pvresize = pvresize_runner(module)
    pvremove = pvremove_runner(module)

    def get_pv_status():
        with pvs("noheadings readonly devices", check_rc=False) as ctx:
            rc, dummy, dummy = ctx.run(devices=[device])
        return rc == 0

    def get_pv_size():
        with pvs("noheadings nosuffix readonly units fields devices") as ctx:
            dummy, out, dummy = ctx.run(units="b", fields="pv_size", devices=[device])
        return int(out.strip())

    # Validate device existence for present state
    if state == "present" and not os.path.exists(device):
        module.fail_json(msg=f"Device {device} not found")

    is_pv = get_pv_status()

    if state == "present":
        # Create PV if needed
        if not is_pv:
            if module.check_mode:
                changed = True
                actions.append("would be created")
            else:
                pvcreate("force device", check_rc=True).run()
                changed = True
                actions.append("created")
            is_pv = True

        # Handle resizing
        elif resize and is_pv:
            if module.check_mode:
                # In check mode, assume resize would change
                changed = True
                actions.append("would be resized")
            else:
                # Perform device rescan each time
                if rescan_device(module, device):
                    actions.append("rescanned")
                original_size = get_pv_size()
                pvresize("device", check_rc=True).run()
                new_size = get_pv_size()
                if new_size != original_size:
                    changed = True
                    actions.append("resized")

    elif state == "absent":
        if is_pv:
            if module.check_mode:
                changed = True
                actions.append("would be removed")
            else:
                pvremove("force device", check_rc=True).run()
                changed = True
                actions.append("removed")

    # Generate final message
    if actions:
        msg = f"PV {device}: {', '.join(actions)}"
    else:
        msg = f"No changes needed for PV {device}"
    module.exit_json(changed=changed, msg=msg)


if __name__ == "__main__":
    main()

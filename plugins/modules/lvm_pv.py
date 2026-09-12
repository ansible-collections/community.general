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
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
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
  zero:
    description:
      - Control whether the first 4 sectors of the device are wiped when creating the PV.
      - Only applied when creating a new PV; has no effect on a PV that already exists.
    type: bool
    version_added: 13.5.0
  metadatasize:
    description:
      - Approximate amount of space to reserve for VG metadata on the PV, for example V(128k) or V(1m).
      - Only applied when creating a new PV; the metadata area size cannot be changed afterwards.
    type: str
    version_added: 13.5.0
  dataalignment:
    description:
      - Align the start of the PV data area to a multiple of this value, for example V(1m).
      - Only applied when creating a new PV; cannot be changed afterwards.
    type: str
    version_added: 13.5.0
  pvmetadatacopies:
    description:
      - Number of metadata areas to reserve on the PV for storing VG metadata.
      - Only applied when creating a new PV; cannot be changed afterwards.
    type: int
    choices: [0, 1, 2]
    version_added: 13.5.0
  metadataignore:
    description:
      - Whether metadata areas on the PV are ignored, meaning LVM does not store VG metadata on it.
      - Applied when creating a new PV, and enforced on existing PVs using C(pvchange).
    type: bool
    version_added: 13.5.0
  allocatable:
    description:
      - Whether the PV can be used for allocation of physical extents.
      - Managed using C(pvchange). LVM only supports this once the PV is part of a volume group; the module fails if
        the PV is still an orphan (not yet part of any volume group).
    type: bool
    version_added: 13.5.0
  tags:
    description:
      - List of tags that must be set on the PV.
      - Tags present on the PV but not listed here are removed; tags listed here but not yet present are added.
      - Managed using C(pvchange). LVM only supports tags once the PV is part of a volume group; the module fails if
        the PV is still an orphan (not yet part of any volume group).
    type: list
    elements: str
    version_added: 13.5.0
notes:
  - Requires LVM2 utilities installed on the target system.
  - Device path must exist when creating a PV.
  - O(zero), O(metadatasize), O(dataalignment), and O(pvmetadatacopies) only take effect when the PV is created; they
    are ignored for a PV that already exists.
  - O(metadataignore) detection on an existing PV relies on comparing the number of metadata areas on the PV with the
    number in use, so it is only meaningful when the PV has at least one metadata area.
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

- name: Creating a physical volume with custom metadata layout
  community.general.lvm_pv:
    device: /dev/sdb
    metadatasize: 128m
    dataalignment: 1m
    pvmetadatacopies: 2

- name: Creating a physical volume without wiping existing signatures and with no metadata areas
  community.general.lvm_pv:
    device: /dev/sdb
    zero: false
    pvmetadatacopies: 0

- name: Setting tags and excluding a physical volume from allocation (PV must already be part of a VG)
  community.general.lvm_pv:
    device: /dev/sdb
    allocatable: false
    tags:
      - fast_disks
      - site_a
"""

RETURN = r"""
"""


import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._lvm import (
    pvchange_runner,
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
            zero=dict(type="bool"),
            metadatasize=dict(type="str"),
            dataalignment=dict(type="str"),
            pvmetadatacopies=dict(type="int", choices=[0, 1, 2]),
            metadataignore=dict(type="bool"),
            allocatable=dict(type="bool"),
            tags=dict(type="list", elements="str"),
        ),
        supports_check_mode=True,
    )

    device = module.params["device"]
    state = module.params["state"]
    resize = module.params["resize"]
    metadataignore = module.params["metadataignore"]
    allocatable = module.params["allocatable"]
    tags = module.params["tags"]
    changed = False
    actions = []

    pvs = pvs_runner(module)
    pvcreate = pvcreate_runner(module)
    pvchange = pvchange_runner(module)
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

    def get_pv_attrs():
        fields = "pv_attr,pv_tags,pv_mda_count,pv_mda_used_count"
        with pvs("noheadings readonly fields separator devices") as ctx:
            dummy, out, dummy = ctx.run(fields=fields, separator="|", devices=[device])
        attr, tags_str, mda_count, mda_used_count = (p.strip() for p in out.strip().split("|"))
        return dict(
            allocatable=attr[:1] == "a",
            tags=[t for t in tags_str.split(",") if t],
            metadataignore=int(mda_count) > 0 and int(mda_used_count) == 0,
        )

    # Validate device existence for present state
    if state == "present" and not os.path.exists(device):
        module.fail_json(msg=f"Device {device} not found")

    is_pv = get_pv_status()
    just_created = False

    if state == "present":
        # Create PV if needed
        if not is_pv:
            if module.check_mode:
                changed = True
                actions.append("would be created")
                just_created = True
            else:
                pvcreate(
                    "force zero metadatasize dataalignment pvmetadatacopies metadataignore device", check_rc=True
                ).run()
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

        # Manage live attributes (allocatable, metadataignore, tags) via pvchange
        if is_pv and (allocatable is not None or metadataignore is not None or tags is not None):
            if module.check_mode and just_created:
                # The PV does not exist yet in check mode, so its current attributes cannot be queried
                actions.append("attributes would be set")
            else:
                current = get_pv_attrs()

                change_allocatable = None
                if allocatable is not None and current["allocatable"] != allocatable:
                    change_allocatable = allocatable

                change_metadataignore = None
                if metadataignore is not None and current["metadataignore"] != metadataignore:
                    change_metadataignore = metadataignore

                to_add = to_del = None
                if tags is not None:
                    current_tags = set(current["tags"])
                    desired_tags = set(tags)
                    to_add = sorted(desired_tags - current_tags)
                    to_del = sorted(current_tags - desired_tags)

                if change_allocatable is not None or change_metadataignore is not None or to_add or to_del:
                    if module.check_mode:
                        changed = True
                        actions.append("attributes would be changed")
                    else:
                        pvchange("allocatable metadataignore addtag deltag device", check_rc=True).run(
                            allocatable=change_allocatable,
                            metadataignore=change_metadataignore,
                            addtag=to_add,
                            deltag=to_del,
                        )
                        changed = True
                        actions.append("attributes changed")

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

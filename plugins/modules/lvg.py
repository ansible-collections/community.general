#!/usr/bin/python

# Copyright (c) 2013, Alexander Bulimov <lazywolf0@gmail.com>
# Based on lvol module by Jeroen Hoekx <jeroen.hoekx@dsquare.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author:
  - Alexander Bulimov (@abulimov)
module: lvg
short_description: Configure LVM volume groups
description:
  - This module creates, removes or resizes volume groups.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  vg:
    description:
      - The name of the volume group.
    type: str
    required: true
  pvs:
    description:
      - List of comma-separated devices to use as physical devices in this volume group.
      - Required when creating or resizing volume group.
      - The module runs C(pvcreate) if needed.
      - This parameter defines the B(desired state) of the physical volumes in the volume group.
        When the volume group already exists, physical volumes not listed here are removed from it by default.
        To add physical volumes without removing existing unlisted ones, set O(remove_extra_pvs=false).
    type: list
    elements: str
  pesize:
    description:
      - The size of the physical extent. O(pesize) must be a power of 2 of at least 1 sector (where the sector size is the
        largest sector size of the PVs currently used in the VG), or at least 128KiB.
      - O(pesize) can be optionally suffixed by a UNIT (k/K/m/M/g/G), default unit is megabyte.
    type: str
    default: "4"
  pv_options:
    description:
      - Additional options to pass to C(pvcreate) when creating the volume group.
    type: str
    default: ''
  pvresize:
    description:
      - If V(true), resize the physical volume to the maximum available size.
    type: bool
    default: false
    version_added: '0.2.0'
  vg_options:
    description:
      - Additional options to pass to C(vgcreate) when creating the volume group.
    type: str
    default: ''
  state:
    description:
      - Control if the volume group exists and its state.
      - The states V(active) and V(inactive) implies V(present) state. Added in 7.1.0.
      - If V(active) or V(inactive), the module manages the VG's logical volumes current state. The module also handles the
        VG's autoactivation state if supported unless when creating a volume group and the autoactivation option specified
        in O(vg_options).
    type: str
    choices: [absent, present, active, inactive]
    default: present
  force:
    description:
      - If V(true), allows to remove volume group with logical volumes.
    type: bool
    default: false
  reset_vg_uuid:
    description:
      - Whether the volume group's UUID is regenerated.
      - This is B(not idempotent). Specifying this parameter always results in a change.
    type: bool
    default: false
    version_added: 7.1.0
  reset_pv_uuid:
    description:
      - Whether the volume group's physical volumes' UUIDs are regenerated.
      - This is B(not idempotent). Specifying this parameter always results in a change.
    type: bool
    default: false
    version_added: 7.1.0
  remove_extra_pvs:
    description:
      - Remove physical volumes from the volume group which are not in O(pvs).
    type: bool
    default: true
    version_added: 10.4.0
seealso:
  - module: community.general.filesystem
  - module: community.general.lvol
  - module: community.general.parted
notes:
  - This module does not modify PE size for already present volume group.
"""

EXAMPLES = r"""
- name: Create a volume group on top of /dev/sda1 with physical extent size = 32MB
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sda1
    pesize: 32

- name: Create a volume group on top of /dev/sdb with physical extent size = 128KiB
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sdb
    pesize: 128K

# If, for example, we already have VG vg.services on top of /dev/sdb1,
# this VG will be extended by /dev/sdc5.  Or if vg.services was created on
# top of /dev/sda5, we first extend it with /dev/sdb1 and /dev/sdc5,
# and then reduce by /dev/sda5.
- name: Create or resize a volume group on top of /dev/sdb1 and /dev/sdc5.
  community.general.lvg:
    vg: vg.services
    pvs:
      - /dev/sdb1
      - /dev/sdc5

- name: Remove a volume group with name vg.services
  community.general.lvg:
    vg: vg.services
    state: absent

- name: Create a volume group on top of /dev/sda3 and resize the volume group /dev/sda3 to the maximum possible
  community.general.lvg:
    vg: resizableVG
    pvs: /dev/sda3
    pvresize: true

- name: Deactivate a volume group
  community.general.lvg:
    state: inactive
    vg: vg.services

- name: Activate a volume group
  community.general.lvg:
    state: active
    vg: vg.services

- name: Add new PVs to volume group without removing existing ones
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sdb1,/dev/sdc1
    remove_extra_pvs: false
    state: present

- name: Reset a volume group UUID
  community.general.lvg:
    state: inactive
    vg: vg.services
    reset_vg_uuid: true

- name: Reset both volume group and pv UUID
  community.general.lvg:
    state: inactive
    vg: vg.services
    pvs:
      - /dev/sdb1
      - /dev/sdc5
    reset_vg_uuid: true
    reset_pv_uuid: true
"""

import itertools
import os
import shlex

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._lvm import (
    pvchange_runner,
    pvcreate_runner,
    pvresize_runner,
    pvs_runner,
    vgchange_runner,
    vgcreate_runner,
    vgextend_runner,
    vgreduce_runner,
    vgremove_runner,
    vgs_runner,
)

VG_AUTOACTIVATION_OPT = "--setautoactivation"


def parse_vgs(data):
    vgs = []
    for line in data.splitlines():
        parts = line.strip().split(";")
        vgs.append(
            {
                "name": parts[0],
                "pv_count": int(parts[1]),
                "lv_count": int(parts[2]),
            }
        )
    return vgs


def find_mapper_device_name(module, dm_device):
    dmsetup_cmd = module.get_bin_path("dmsetup", True)
    mapper_prefix = "/dev/mapper/"
    rc, dm_name, err = module.run_command([dmsetup_cmd, "info", "-C", "--noheadings", "-o", "name", dm_device])
    if rc != 0:
        module.fail_json(msg="Failed executing dmsetup command.", rc=rc, err=err)
    mapper_device = mapper_prefix + dm_name.rstrip()
    return mapper_device


def parse_pvs(module, data):
    pvs = []
    dm_prefix = "/dev/dm-"
    for line in data.splitlines():
        parts = line.strip().split(";")
        if parts[0].startswith(dm_prefix):
            parts[0] = find_mapper_device_name(module, parts[0])
        pvs.append(
            {
                "name": parts[0],
                "vg_name": parts[1],
            }
        )
    return pvs


def find_vg(module, vg, vgs):
    if not vg:
        return None
    with vgs("noheadings separator fields", check_rc=True) as ctx:
        dummy, current_vgs, dummy = ctx.run(separator=";", fields="vg_name,pv_count,lv_count")
    return next((test_vg for test_vg in parse_vgs(current_vgs) if test_vg["name"] == vg), None)


def is_autoactivation_supported(module, vg_cmd):
    dummy, vgchange_opts, dummy = module.run_command([vg_cmd, "--help"], check_rc=True)
    return VG_AUTOACTIVATION_OPT in vgchange_opts


def activate_vg(module, vg, active, vgs, vgchange):
    changed = False
    vgchange_cmd = module.get_bin_path("vgchange", True)
    vgs_fields = ["lv_attr"]

    autoactivation_enabled = False
    autoactivation_supported = is_autoactivation_supported(module=module, vg_cmd=vgchange_cmd)

    if autoactivation_supported:
        vgs_fields.append("autoactivation")

    with vgs("noheadings separator fields vg", check_rc=True) as ctx:
        dummy, current_vg_lv_states, dummy = ctx.run(separator=";", fields=",".join(vgs_fields), vg=[vg])

    lv_active_count = 0
    lv_inactive_count = 0

    for line in current_vg_lv_states.splitlines():
        parts = line.strip().split(";")
        if parts[0][4] == "a":
            lv_active_count += 1
        else:
            lv_inactive_count += 1
        if autoactivation_supported:
            autoactivation_enabled = autoactivation_enabled or parts[1] == "enabled"

    activate_flag = None
    if active and lv_inactive_count > 0:
        activate_flag = True
    elif not active and lv_active_count > 0:
        activate_flag = False

    # Extra logic necessary because vgchange returns error when autoactivation is already set
    if autoactivation_supported:
        if active and not autoactivation_enabled:
            if module.check_mode:
                changed = True
            else:
                vgchange("setautoactivation vg", check_rc=True).run(setautoactivation=True, vg=[vg])
                changed = True
        elif not active and autoactivation_enabled:
            if module.check_mode:
                changed = True
            else:
                vgchange("setautoactivation vg", check_rc=True).run(setautoactivation=False, vg=[vg])
                changed = True

    if activate_flag is not None:
        if module.check_mode:
            changed = True
        else:
            vgchange("activate vg", check_rc=True).run(activate=activate_flag, vg=[vg])
            changed = True

    return changed


def get_vgcreate_setautoactivation(module, state, vg_options_str):
    if state not in ["active", "inactive"]:
        return None
    if VG_AUTOACTIVATION_OPT in vg_options_str:
        return None
    vgcreate_cmd = module.get_bin_path("vgcreate", True)
    if not is_autoactivation_supported(module=module, vg_cmd=vgcreate_cmd):
        return None
    return state == "active"


def get_pv_values_for_resize(module, device, pvs):
    with pvs("noheadings nosuffix units separator fields devices", check_rc=True) as ctx:
        dummy, pv_values, dummy = ctx.run(
            units="b", separator=";", fields="dev_size,pv_size,pe_start,vg_extent_size", devices=[device]
        )

    values = pv_values.strip().split(";")
    dev_size = int(values[0])
    pv_size = int(values[1])
    pe_start = int(values[2])
    vg_extent_size = int(values[3])

    return (dev_size, pv_size, pe_start, vg_extent_size)


def resize_pv(module, device, pvs, pvresize):
    changed = False
    dev_size, pv_size, pe_start, vg_extent_size = get_pv_values_for_resize(module=module, device=device, pvs=pvs)
    if (dev_size - (pe_start + pv_size)) > vg_extent_size:
        if module.check_mode:
            changed = True
        else:
            # If there is a missing pv on the machine, versions of pvresize rc indicates failure.
            with pvresize("device") as ctx:
                rc, out, err = ctx.run(device=[device])
            dummy, new_pv_size, dummy, dummy = get_pv_values_for_resize(module=module, device=device, pvs=pvs)
            if pv_size == new_pv_size:
                module.fail_json(msg="Failed executing pvresize command.", rc=rc, err=err, out=out)
            else:
                changed = True

    return changed


def reset_uuid_pv(module, device, pvs, pvchange):
    changed = False
    with pvs("noheadings fields devices", check_rc=True) as ctx:
        dummy, orig_uuid, dummy = ctx.run(fields="uuid", devices=[device])

    if module.check_mode:
        changed = True
    else:
        # If there is a missing pv on the machine, pvchange rc indicates failure.
        with pvchange("uuid device") as ctx:
            pvchange_rc, pvchange_out, pvchange_err = ctx.run(uuid=True, device=[device])
        with pvs("noheadings fields devices", check_rc=True) as ctx:
            dummy, new_uuid, dummy = ctx.run(fields="uuid", devices=[device])
        if orig_uuid.strip() == new_uuid.strip():
            module.fail_json(
                msg=f"PV ({device}) UUID change failed", rc=pvchange_rc, err=pvchange_err, out=pvchange_out
            )
        else:
            changed = True

    return changed


def reset_uuid_vg(module, vg, vgchange):
    changed = False
    if module.check_mode:
        changed = True
    else:
        vgchange("uuid vg", check_rc=True).run(uuid=True, vg=[vg])
        changed = True

    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vg=dict(type="str", required=True),
            pvs=dict(type="list", elements="str"),
            pesize=dict(type="str", default="4"),
            pv_options=dict(type="str", default=""),
            pvresize=dict(type="bool", default=False),
            vg_options=dict(type="str", default=""),
            state=dict(type="str", default="present", choices=["absent", "present", "active", "inactive"]),
            force=dict(type="bool", default=False),
            reset_vg_uuid=dict(type="bool", default=False),
            reset_pv_uuid=dict(type="bool", default=False),
            remove_extra_pvs=dict(type="bool", default=True),
        ),
        required_if=[
            ["reset_pv_uuid", True, ["pvs"]],
        ],
        supports_check_mode=True,
    )

    vg = module.params["vg"]
    state = module.params["state"]
    force = module.boolean(module.params["force"])
    do_pvresize = module.boolean(module.params["pvresize"])
    pvoptions = shlex.split(module.params["pv_options"])
    reset_vg_uuid = module.boolean(module.params["reset_vg_uuid"])
    reset_pv_uuid = module.boolean(module.params["reset_pv_uuid"])
    remove_extra_pvs = module.boolean(module.params["remove_extra_pvs"])

    pvs = pvs_runner(module)
    pvcreate = pvcreate_runner(module)
    pvchange = pvchange_runner(module)
    pvresize = pvresize_runner(module)
    vgs = vgs_runner(module)
    vgcreate = vgcreate_runner(module)
    vgchange = vgchange_runner(module)
    vgextend = vgextend_runner(module)
    vgreduce = vgreduce_runner(module)
    vgremove = vgremove_runner(module)

    this_vg = find_vg(module=module, vg=vg, vgs=vgs)
    present_state = state in ["present", "active", "inactive"]
    pvs_required = present_state and this_vg is None
    changed = False

    dev_list = []
    if module.params["pvs"]:
        dev_list = list(module.params["pvs"])
    elif pvs_required:
        module.fail_json(msg="No physical volumes given.")

    # LVM always uses real paths not symlinks so replace symlinks with actual path
    for idx, dev in enumerate(dev_list):
        dev_list[idx] = os.path.realpath(dev)

    if present_state:
        # check given devices
        for test_dev in dev_list:
            if not os.path.exists(test_dev):
                module.fail_json(msg=f"Device {test_dev} not found.")

        # get pv list
        if dev_list:
            pvs_filter_pv_name = " || ".join(f"pv_name = {x}" for x in itertools.chain(dev_list, module.params["pvs"]))
            pvs_filter_vg_name = f"vg_name = {vg}"
            pvs_select = f"{pvs_filter_pv_name} || {pvs_filter_vg_name}"
        else:
            pvs_select = None

        with pvs("noheadings separator fields select", check_rc=True) as ctx:
            dummy, current_pvs, dummy = ctx.run(separator=";", fields="pv_name,vg_name", select=pvs_select)

        # check pv for devices
        pv_list = parse_pvs(module, current_pvs)
        used_pvs = [pv for pv in pv_list if pv["name"] in dev_list and pv["vg_name"] and pv["vg_name"] != vg]
        if used_pvs:
            module.fail_json(msg=f"Device {used_pvs[0]['name']} is already in {used_pvs[0]['vg_name']} volume group.")

    if this_vg is None:
        if present_state:
            setautoactivation = get_vgcreate_setautoactivation(
                module=module, state=state, vg_options_str=module.params["vg_options"]
            )
            # create VG
            if module.check_mode:
                changed = True
            else:
                # create PV
                for current_dev in dev_list:
                    pvcreate("pv_options force device", check_rc=True).run(
                        pv_options=pvoptions, force=True, device=[current_dev]
                    )
                    changed = True
                vgcreate("vg_options pesize setautoactivation vg pvs", check_rc=True).run(
                    vg_options=shlex.split(module.params["vg_options"]),
                    setautoactivation=setautoactivation,
                    pvs=dev_list,
                )
                changed = True
    else:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            else:
                if this_vg["lv_count"] == 0 or force:
                    # remove VG
                    vgremove("force vg", check_rc=True).run(force=True, vg=[vg])
                    module.exit_json(changed=True)
                else:
                    module.fail_json(msg=f"Refuse to remove non-empty volume group {vg} without force=true")
        # activate/deactivate existing VG
        elif state == "active":
            changed = activate_vg(module=module, vg=vg, active=True, vgs=vgs, vgchange=vgchange)
        elif state == "inactive":
            changed = activate_vg(module=module, vg=vg, active=False, vgs=vgs, vgchange=vgchange)

        # reset VG uuid
        if reset_vg_uuid:
            changed = reset_uuid_vg(module=module, vg=vg, vgchange=vgchange) or changed

        # resize VG
        if dev_list:
            current_devs = [os.path.realpath(pv["name"]) for pv in pv_list if pv["vg_name"] == vg]
            devs_to_remove = list(set(current_devs) - set(dev_list))
            devs_to_add = list(set(dev_list) - set(current_devs))

            if not remove_extra_pvs:
                devs_to_remove = []

            if current_devs:
                if present_state:
                    for device in current_devs:
                        if do_pvresize:
                            changed = resize_pv(module=module, device=device, pvs=pvs, pvresize=pvresize) or changed
                        if reset_pv_uuid:
                            changed = reset_uuid_pv(module=module, device=device, pvs=pvs, pvchange=pvchange) or changed

            if devs_to_add or devs_to_remove:
                if module.check_mode:
                    changed = True
                else:
                    if devs_to_add:
                        # create PV
                        for current_dev in devs_to_add:
                            pvcreate("pv_options force device", check_rc=True).run(
                                pv_options=pvoptions, force=True, device=[current_dev]
                            )
                            changed = True
                        # add PV to our VG
                        vgextend("vg pvs", check_rc=True).run(vg=[vg], pvs=devs_to_add)
                        changed = True

                    # remove some PV from our VG
                    if devs_to_remove:
                        vgreduce("force vg pvs", check_rc=True).run(force=True, vg=[vg], pvs=devs_to_remove)
                        changed = True

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()

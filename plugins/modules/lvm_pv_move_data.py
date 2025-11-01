#!/usr/bin/python

# Copyright (c) 2025, Klention Mali <klention@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations


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
  auto_answer:
    description:
      - Answer yes to all prompts automatically.
    type: bool
    default: false
  atomic:
    description:
      - Makes the C(pvmove) operation atomic, ensuring that all affected LVs are moved to the destination PV,
        or none are if the operation is aborted.
    type: bool
    default: true
  autobackup:
    description:
      - Automatically backup metadata before changes (strongly advised!).
    type: bool
    default: true
requirements:
  - LVM2 utilities
  - Both O(source) and O(destination) devices must exist, and the PVs must be in the same volume group.
  - The O(destination) PV must have enough free space to accommodate the O(source) PV's allocated extents.
  - Verbosity is automatically controlled by Ansible's verbosity level (using multiple C(-v) flags).
"""

EXAMPLES = r"""
- name: Moving data from /dev/sdb to /dev/sdc
  community.general.lvm_pv_move_data:
    source: /dev/sdb
    destination: /dev/sdc
"""

RETURN = r"""
actions:
  description: List of actions performed during module execution.
  returned: success
  type: list
  elements: str
  sample: [
    "moved data from /dev/sdb to /dev/sdc",
    "no allocated extents to move",
    "would move data from /dev/sdb to /dev/sdc"
  ]
"""


import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


def main():
    module = AnsibleModule(
        argument_spec=dict(
            source=dict(type="path", required=True),
            destination=dict(type="path", required=True),
            auto_answer=dict(type="bool", default=False),
            atomic=dict(type="bool", default=True),
            autobackup=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    pvs_runner = CmdRunner(
        module,
        command="pvs",
        arg_formats=dict(
            noheadings=cmd_runner_fmt.as_fixed("--noheadings"),
            readonly=cmd_runner_fmt.as_fixed("--readonly"),
            vg_name=cmd_runner_fmt.as_fixed("-o", "vg_name"),
            pv_pe_alloc_count=cmd_runner_fmt.as_fixed("-o", "pv_pe_alloc_count"),
            pv_pe_count=cmd_runner_fmt.as_fixed("-o", "pv_pe_count"),
            device=cmd_runner_fmt.as_list(),
        ),
    )

    source = module.params["source"]
    destination = module.params["destination"]
    changed = False
    actions = []
    result = {"changed": False}

    # Validate device existence
    if not os.path.exists(source):
        module.fail_json(msg=f"Source device {source} not found")
    if not os.path.exists(destination):
        module.fail_json(msg=f"Destination device {destination} not found")
    if source == destination:
        module.fail_json(msg="Source and destination devices must be different")

    def run_pvs_command(arguments, device):
        with pvs_runner(arguments) as ctx:
            rc, out, err = ctx.run(device=device)
            if rc != 0:
                module.fail_json(
                    msg=f"Command failed: {err}",
                    stdout=out,
                    stderr=err,
                    rc=rc,
                    cmd=ctx.cmd,
                    arguments=arguments,
                    device=device,
                )
            return out.strip()

    def is_pv(device):
        with pvs_runner("noheadings readonly device", check_rc=False) as ctx:
            rc, out, err = ctx.run(device=device)
        return rc == 0

    if not is_pv(source):
        module.fail_json(msg=f"Source device {source} is not a PV")
    if not is_pv(destination):
        module.fail_json(msg=f"Destination device {destination} is not a PV")

    vg_src = run_pvs_command("noheadings vg_name device", source)
    vg_dest = run_pvs_command("noheadings vg_name device", destination)
    if vg_src != vg_dest:
        module.fail_json(
            msg=f"Source and destination must be in the same VG. Source VG: '{vg_src}', Destination VG: '{vg_dest}'."
        )

    def get_allocated_pe(device):
        try:
            return int(run_pvs_command("noheadings pv_pe_alloc_count device", device))
        except ValueError:
            module.fail_json(msg=f"Invalid allocated PE count for device {device}")

    allocated = get_allocated_pe(source)
    if allocated == 0:
        actions.append("no allocated extents to move")
    else:
        # Check destination has enough free space
        def get_total_pe(device):
            try:
                return int(run_pvs_command("noheadings pv_pe_count device", device))
            except ValueError:
                module.fail_json(msg=f"Invalid total PE count for device {device}")

        def get_free_pe(device):
            return get_total_pe(device) - get_allocated_pe(device)

        free_pe_dest = get_free_pe(destination)
        if free_pe_dest < allocated:
            module.fail_json(
                msg=(
                    f"Destination device {destination} has only {int(free_pe_dest)} free physical extents, but "
                    f"source device {source} has {int(allocated)} allocated extents. Not enough space."
                )
            )

        if module.check_mode:
            changed = True
            actions.append(f"would move data from {source} to {destination}")
        else:
            pvmove_runner = CmdRunner(
                module,
                command="pvmove",
                arg_formats=dict(
                    auto_answer=cmd_runner_fmt.as_bool("-y"),
                    atomic=cmd_runner_fmt.as_bool("--atomic"),
                    autobackup=cmd_runner_fmt.as_fixed("--autobackup", "y" if module.params["autobackup"] else "n"),
                    verbosity=cmd_runner_fmt.as_func(lambda v: [f"-{'v' * v}"] if v > 0 else []),
                    source=cmd_runner_fmt.as_list(),
                    destination=cmd_runner_fmt.as_list(),
                ),
            )

            verbosity = module._verbosity
            with pvmove_runner("auto_answer atomic autobackup verbosity source destination") as ctx:
                rc, out, err = ctx.run(verbosity=verbosity, source=source, destination=destination)
                result["stdout"] = out
                result["stderr"] = err

            changed = True
            actions.append(f"moved data from {source} to {destination}")

    result["changed"] = changed
    result["actions"] = actions
    if actions:
        result["msg"] = f"PV data move: {', '.join(actions)}"
    else:
        result["msg"] = f"No data to move from {source}"

    module.exit_json(**result)


if __name__ == "__main__":
    main()

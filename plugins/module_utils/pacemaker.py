# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

_state_map = {
    "present": "create",
    "absent": "remove",
    "cloned": "clone",
    "status": "status",
    "enabled": "enable",
    "disabled": "disable",
    "online": "start",
    "offline": "stop",
    "maintenance": "set",
    "config": "config",
    "cleanup": "cleanup",
}


def fmt_resource_type(value):
    return [
        ":".join(
            value[k] for k in ["resource_standard", "resource_provider", "resource_name"] if value.get(k) is not None
        )
    ]


def fmt_resource_operation(value):
    cmd = []
    for op in value:
        cmd.append("op")
        cmd.append(op.get("operation_action"))
        for operation_option in op.get("operation_option"):
            cmd.append(operation_option)

    return cmd


def fmt_resource_argument(value):
    return ["--group" if value["argument_action"] == "group" else value["argument_action"]] + value["argument_option"]


def get_pacemaker_maintenance_mode(runner):
    with runner("cli_action config") as ctx:
        rc, out, err = ctx.run(cli_action="property")
        maint_mode_re = re.compile(r"maintenance-mode.*true", re.IGNORECASE)
        maintenance_mode_output = [line for line in out.splitlines() if maint_mode_re.search(line)]
        return bool(maintenance_mode_output)


def pacemaker_runner(module, **kwargs):
    runner_command = ["pcs"]
    runner = CmdRunner(
        module,
        command=runner_command,
        arg_formats=dict(
            cli_action=cmd_runner_fmt.as_list(),
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            resource_type=cmd_runner_fmt.as_func(fmt_resource_type),
            resource_option=cmd_runner_fmt.as_list(),
            resource_operation=cmd_runner_fmt.as_func(fmt_resource_operation),
            resource_meta=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("meta"),
            resource_argument=cmd_runner_fmt.as_func(fmt_resource_argument),
            resource_clone_ids=cmd_runner_fmt.as_list(),
            resource_clone_meta=cmd_runner_fmt.as_list(),
            apply_all=cmd_runner_fmt.as_bool("--all"),
            agent_validation=cmd_runner_fmt.as_bool("--agent-validation"),
            wait=cmd_runner_fmt.as_opt_eq_val("--wait"),
            config=cmd_runner_fmt.as_fixed("config"),
            force=cmd_runner_fmt.as_bool("--force"),
            version=cmd_runner_fmt.as_fixed("--version"),
            output_format=cmd_runner_fmt.as_opt_eq_val("--output-format"),
        ),
        **kwargs,
    )
    return runner

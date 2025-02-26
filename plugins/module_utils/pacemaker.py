# -*- coding: utf-8 -*-
# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


_state_map = {
    "present": "create",
    "absent": "remove",
    "status": "status",
    "enabled": "enable",
    "disabled": "disable"
}


def fmt_resource_type(value):
    return [value[k] for k in ['resource_standard', 'resource_provider', 'resource_name'] if value.get(k) is not None]


def fmt_resource_operation(value):
    cmd = []
    for op in value:
        cmd.append("op")
        cmd.append(op.get('operation_action'))
        for operation_option in op.get('operation_option'):
            cmd.append(operation_option)

    return cmd


def fmt_resource_argument(value):
    return ['--group' if value['argument_action'] == 'group' else value['argument_action']] + value['argument_option']


def pacemaker_runner(module, cli_action, **kwargs):
    runner = CmdRunner(
        module,
        command=['pcs', cli_action],
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            resource_type=cmd_runner_fmt.as_func(fmt_resource_type),
            resource_option=cmd_runner_fmt.as_list(),
            resource_operation=cmd_runner_fmt.as_func(fmt_resource_operation),
            resource_meta=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("meta"),
            resource_argument=cmd_runner_fmt.as_func(fmt_resource_argument),
            wait=cmd_runner_fmt.as_opt_eq_val("--wait"),
        ),
        **kwargs
    )
    return runner

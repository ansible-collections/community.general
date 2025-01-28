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
    "status": "status"
}

def fmt_resource_type(value):
    cmd = []
    for key in ['resource_standard', 'resource_provider', 'resource_name']:
        if value.get(key) is not None:
            cmd.append(value.get(key))
    return cmd

def fmt_resource_operation(value):
    cmd = []
    for op in value:
        cmd.append("op")
        cmd.append(op.get('operation_action'))
        for operation_option in op.get('operation_option'):
            cmd.append(operation_option)

    return cmd

def fmt_resource_argument(value):
    cmd = []
    if value.get('argument_action') == 'group':
        cmd.append('--group')
    else:
        cmd.append(value.get('argument_action'))
    return cmd + list(value.get('argument_option'))

def pacemaker_runner(module, **kwargs):
    runner = CmdRunner(
        module,
        command=['pcs', 'resource'],
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            resource_type=cmd_runner_fmt.as_func(fmt_resource_type),
            resource_option=cmd_runner_fmt.as_list(),
            resource_operation=cmd_runner_fmt.as_func(fmt_resource_operation),
            resource_meta=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("meta"),
            resource_argument=cmd_runner_fmt.as_func(fmt_resource_argument),
            disabled=cmd_runner_fmt.as_bool("--disabled"),
            wait=cmd_runner_fmt.as_opt_eq_val("--wait"),
        ),
        **kwargs
    )
    return runner

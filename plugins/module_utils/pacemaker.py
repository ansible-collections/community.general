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

def pacemaker_runner(module, **kwargs):
    runner = CmdRunner(
        module, # This module, does it put it at the end of pcs resource?
        command='pcs resource',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            resource_type=cmd_runner_fmt.as_list(),
            resource_option=cmd_runner_fmt.as_list(),
            resource_operation=cmd_runner_fmt.as_list(),
            resource_meta=cmd_runner_fmt.as_list(),
            resource_argument=cmd_runner_fmt.as_list(),
            disabled=cmd_runner_fmt.as_bool("--disabled"),
            wait=cmd_runner_fmt.as_opt_val("--wait"),
        ),
        **kwargs
    )
    return runner

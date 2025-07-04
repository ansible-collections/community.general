# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


_state_map = {
    "present": "--set",
    "absent": "--unset",
    "get": "--get",
}


def gconftool2_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='gconftool-2',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            key=cmd_runner_fmt.as_list(),
            value_type=cmd_runner_fmt.as_opt_val("--type"),
            value=cmd_runner_fmt.as_list(),
            direct=cmd_runner_fmt.as_bool("--direct"),
            config_source=cmd_runner_fmt.as_opt_val("--config-source"),
            version=cmd_runner_fmt.as_fixed("--version"),
        ),
        **kwargs
    )

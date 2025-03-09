# -*- coding: utf-8 -*-
# Copyright (c) 2025, Marco Noce <nce.marco@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


systemd_info_arg_formats = {
    'version':   cmd_runner_fmt.as_fixed("--version"),
    'list_units': cmd_runner_fmt.as_fixed("list-units"),
    'no_pager':  cmd_runner_fmt.as_fixed("--no-pager"),
    'typ':       cmd_runner_fmt.as_fixed("--type"),
    'types':     cmd_runner_fmt.as_func(lambda v: [",".join(v)] if isinstance(v, list) else [v]),
    'all':       cmd_runner_fmt.as_fixed("--all"),
    'plain':     cmd_runner_fmt.as_fixed("--plain"),
    'no_legend': cmd_runner_fmt.as_fixed("--no-legend"),
    'show':      cmd_runner_fmt.as_fixed("show"),
    'p':         cmd_runner_fmt.as_fixed("-p"),
    'props':     cmd_runner_fmt.as_list(),
    'dashdash':  cmd_runner_fmt.as_fixed("--"),
    'unit':      cmd_runner_fmt.as_list(),
}


default_systemd_info_args_order = "version list_units no_pager typ types all plain no_legend show p props dashdash unit"


def systemd_info_runner(module, command, **kwargs):
    return CmdRunner(
        module,
        command=command,
        arg_formats=systemd_info_arg_formats,
        default_args_order=default_systemd_info_args_order,
        check_rc=True,
        **kwargs
    )

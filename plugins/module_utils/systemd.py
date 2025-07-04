# -*- coding: utf-8 -*-
# Copyright (c) 2025, Marco Noce <nce.marco@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


def systemd_runner(module, command, **kwargs):
    arg_formats = dict(
        version=cmd_runner_fmt.as_fixed("--version"),
        list_units=cmd_runner_fmt.as_fixed(["list-units", "--no-pager"]),
        types=cmd_runner_fmt.as_func(lambda v: [] if not v else ["--type", ",".join(v)]),
        all=cmd_runner_fmt.as_fixed("--all"),
        plain=cmd_runner_fmt.as_fixed("--plain"),
        no_legend=cmd_runner_fmt.as_fixed("--no-legend"),
        show=cmd_runner_fmt.as_fixed("show"),
        props=cmd_runner_fmt.as_func(lambda v: [] if not v else ["-p", ",".join(v)]),
        dashdash=cmd_runner_fmt.as_fixed("--"),
        unit=cmd_runner_fmt.as_list(),
    )

    runner = CmdRunner(
        module,
        command=command,
        arg_formats=arg_formats,
        check_rc=True,
        **kwargs
    )
    return runner

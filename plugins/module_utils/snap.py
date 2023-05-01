# -*- coding: utf-8 -*-
# Copyright (c) 2023, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


_alias_state_map = dict(
    present='alias',
    absent='unalias',
    info='aliases',
)

_state_map = dict(
    present='install',
    absent='remove',
    enabled='enable',
    disabled='disable',
)


def snap_runner(module, **kwargs):
    runner = CmdRunner(
        module,
        "snap",
        arg_formats=dict(
            state_alias=cmd_runner_fmt.as_map(_alias_state_map),  # snap_alias only
            name=cmd_runner_fmt.as_list(),
            alias=cmd_runner_fmt.as_list(),                       # snap_alias only
            state=cmd_runner_fmt.as_map(_state_map),
            _list=cmd_runner_fmt.as_fixed("list"),
            _set=cmd_runner_fmt.as_fixed("set"),
            get=cmd_runner_fmt.as_fixed(["get", "-d"]),
            classic=cmd_runner_fmt.as_bool("--classic"),
            channel=cmd_runner_fmt.as_func(lambda v: [] if v == 'stable' else ['--channel', '{0}'.format(v)]),
            options=cmd_runner_fmt.as_list(),
        ),
        check_rc=False,
        **kwargs
    )
    return runner

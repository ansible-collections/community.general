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


def snap_runner(module, **kwargs):
    runner = CmdRunner(
        module,
        module.get_bin_path("snap"),
        arg_formats=dict(
            state_alias=cmd_runner_fmt.as_map(_alias_state_map),
            name=cmd_runner_fmt.as_list(),
            alias=cmd_runner_fmt.as_list(),
        ),
        check_rc=False,
        **kwargs
    )
    return runner

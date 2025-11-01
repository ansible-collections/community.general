# Copyright (c) 2023, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


def locale_runner(module):
    runner = CmdRunner(
        module,
        command=["locale", "-a"],
        check_rc=True,
    )
    return runner


def locale_gen_runner(module):
    runner = CmdRunner(
        module,
        command="locale-gen",
        arg_formats=dict(
            name=cmd_runner_fmt.as_list(),
            purge=cmd_runner_fmt.as_fixed("--purge"),
        ),
        check_rc=True,
    )
    return runner

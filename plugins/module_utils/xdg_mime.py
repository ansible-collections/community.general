# Copyright (c) 2025, Marcos Alano <marcoshalano@gmail.com>
# Based on gio_mime module. Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


def xdg_mime_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    return CmdRunner(
        module,
        command=["xdg-mime"],
        arg_formats=dict(
            default=cmd_runner_fmt.as_fixed("default"),
            query=cmd_runner_fmt.as_fixed("query"),
            mime_types=cmd_runner_fmt.as_list(),
            handler=cmd_runner_fmt.as_list(),
            version=cmd_runner_fmt.as_fixed("--version"),
        ),
        **kwargs,
    )


def xdg_mime_get(runner: CmdRunner, mime_type) -> str | None:
    def process(rc, out, err) -> str | None:
        if not out.strip():
            return None
        out = out.splitlines()[0]
        return out.split()[-1]

    with runner("query default mime_types", output_process=process) as ctx:
        return ctx.run(mime_types=mime_type)

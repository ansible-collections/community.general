# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


def gio_mime_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    return CmdRunner(
        module,
        command=["gio"],
        arg_formats=dict(
            mime=cmd_runner_fmt.as_fixed("mime"),
            mime_type=cmd_runner_fmt.as_list(),
            handler=cmd_runner_fmt.as_list(),
            version=cmd_runner_fmt.as_fixed("--version"),
        ),
        **kwargs,
    )


def gio_mime_get(runner: CmdRunner, mime_type) -> str | None:
    def process(rc, out, err) -> str | None:
        if err.startswith("No default applications for"):
            return None
        out = out.splitlines()[0]
        return out.split()[-1]

    with runner("mime mime_type", output_process=process) as ctx:
        return ctx.run(mime_type=mime_type)

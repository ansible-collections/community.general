# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import typing as t

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, _ensure_list

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


class PythonRunner(CmdRunner):
    def __init__(
        self,
        module: AnsibleModule,
        command,
        arg_formats=None,
        default_args_order=(),
        check_rc: bool = False,
        force_lang: str = "C",
        path_prefix: list[str] | None = None,
        environ_update: dict[str, str] | None = None,
        python: str = "python",
        venv: str | None = None,
    ) -> None:
        self.python = python
        self.venv = venv
        self.has_venv = venv is not None

        if os.path.isabs(python) or "/" in python:
            self.python = python
        elif venv is not None:
            if path_prefix is None:
                path_prefix = []
            path_prefix.append(os.path.join(venv, "bin"))
            if environ_update is None:
                environ_update = {}
            environ_update["PATH"] = f"{':'.join(path_prefix)}:{os.environ['PATH']}"
            environ_update["VIRTUAL_ENV"] = venv

        python_cmd = [self.python] + _ensure_list(command)

        super().__init__(
            module, python_cmd, arg_formats, default_args_order, check_rc, force_lang, path_prefix, environ_update
        )

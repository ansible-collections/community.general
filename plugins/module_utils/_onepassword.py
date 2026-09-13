# Copyright (c) Ansible project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import os

from ansible_collections.community.general.plugins.module_utils import _cmd_runner_fmt as fmt
from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner


def onepassword_runner(module, command):
    return CmdRunner(
        module,
        command=command,
        arg_formats=dict(
            _account_list=fmt.as_fixed(["account", "list"]),
            _account_get=fmt.as_fixed(["account", "get"]),
            _signin=fmt.as_fixed(["signin", "--raw"]),
            _account_add=fmt.as_fixed(["account", "add", "--raw", "--signin"]),
            _item_get=fmt.as_fixed(["item", "get", "--format", "json"]),
            account=fmt.as_opt_val("--account"),
            address=fmt.as_opt_val("--address"),
            email=fmt.as_opt_val("--email"),
            item_id=fmt.as_list(),
            vault=fmt.as_opt_eq_val("--vault"),
            session=fmt.as_optval("--session="),
        ),
    )


class OnePasswordConfig:
    _config_file_paths = (
        "~/.op/config",
        "~/.config/op/config",
        "~/.config/.op/config",
    )

    def __init__(self) -> None:
        self._config_file_path = ""

    @property
    def config_file_path(self) -> str | None:
        if self._config_file_path:
            return self._config_file_path

        for path in self._config_file_paths:
            realpath = os.path.expanduser(path)
            if os.path.exists(realpath):
                self._config_file_path = realpath
                return self._config_file_path

        return None

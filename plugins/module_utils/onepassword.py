# Copyright (c) Ansible project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import os


class OnePasswordConfig:
    _config_file_paths = (
        "~/.op/config",
        "~/.config/op/config",
        "~/.config/.op/config",
    )

    def __init__(self):
        self._config_file_path = ""

    @property
    def config_file_path(self):
        if self._config_file_path:
            return self._config_file_path

        for path in self._config_file_paths:
            realpath = os.path.expanduser(path)
            if os.path.exists(realpath):
                self._config_file_path = realpath
                return self._config_file_path

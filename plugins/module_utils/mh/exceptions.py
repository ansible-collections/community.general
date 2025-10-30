# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import typing as t

from ansible.module_utils.common.text.converters import to_native


class ModuleHelperException(Exception):
    def __init__(self, msg: str, update_output: dict[str, t.Any] | None = None, *args, **kwargs):
        self.msg: str = to_native(msg or f"Module failed with exception: {self}")
        if update_output is None:
            update_output = {}
        self.update_output: dict[str, t.Any] = update_output
        super().__init__(*args)

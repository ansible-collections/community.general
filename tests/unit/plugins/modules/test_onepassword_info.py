# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
from unittest.mock import PropertyMock

from ansible.module_utils.common.text.converters import to_bytes, to_text

from ansible_collections.community.general.plugins.module_utils._onepassword import OnePasswordConfig
from ansible_collections.community.general.plugins.modules import onepassword_info

from .uthelper import RunCommandMock, TestCaseMock, UTHelper


def _to_text(value):
    if isinstance(value, bytes):
        return to_text(value)
    if isinstance(value, list):
        return [_to_text(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_text(v) for k, v in value.items()}
    return value


class OnePassRunCommandMock(RunCommandMock):
    """run_command() is called with encoding=None and some args as bytes: compare the calls as text."""

    def setup(self, mocker):
        for spec in self.mock_specs:
            spec["out"] = to_bytes(spec["out"])
        super().setup(mocker)

    def check(self, test_case, results):
        call_args_list = [(_to_text(c[0][0]), _to_text(c[1])) for c in self.mock_run_cmd.call_args_list]
        expected_call_args_list = [(spec["command"], spec.get("environ", {})) for spec in self.mock_specs]

        assert self.mock_run_cmd.call_count == len(self.mock_specs), (
            f"{self.mock_run_cmd.call_count} != {len(self.mock_specs)}"
        )
        assert call_args_list == expected_call_args_list


class OnePasswordConfigMock(TestCaseMock):
    name = "onepassword_config"

    def setup(self, mocker):
        config_file_path = self.mock_specs.get("config_file_path")
        mocker.patch.object(
            OnePasswordConfig,
            "config_file_path",
            new_callable=PropertyMock,
            return_value=config_file_path,
        )
        config_file_exists = self.mock_specs.get("config_file_exists", True)
        real_isfile = os.path.isfile
        mocker.patch(
            "os.path.isfile",
            side_effect=lambda path: config_file_exists if path == config_file_path else real_isfile(path),
        )

    def check(self, test_case, results):
        pass


UTHelper.from_module(onepassword_info, __name__, mocks=[OnePassRunCommandMock, OnePasswordConfigMock])

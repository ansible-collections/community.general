# Copyright (c) 2026, Prayas Vadlakonda
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import bundler


def get_run_command_calls(run_command_mock):
    return [" ".join(call[0][0]) for call in run_command_mock.call_args_list]


class TestBundler(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mocker.patch(
            "ansible.module_utils.basic.AnsibleModule.get_bin_path",
            return_value="/usr/bin/bundle",
        )

    @pytest.fixture(autouse=True)
    def _mocker(self, mocker):
        self.mocker = mocker

    def patch_run_command(self, version_output="Bundler version 2.5.0"):
        target = "ansible.module_utils.basic.AnsibleModule.run_command"
        mock = self.mocker.patch(target)
        mock.side_effect = [
            (0, version_output, ""),  # bundle --version
            (0, "Installing gems\n", ""),  # bundle install
        ]
        return mock

    def test_clean_uses_flag_on_bundler_3(self):
        run_command = self.patch_run_command("Bundler version 3.5.0")
        with set_module_args({"state": "present", "clean": True}):
            with pytest.raises(AnsibleExitJson):
                bundler.main()

        calls = get_run_command_calls(run_command)
        assert any("--clean" in c for c in calls)
        assert not any("config set clean" in c for c in calls)

    def test_clean_uses_config_set_on_bundler_4(self):
        target = "ansible.module_utils.basic.AnsibleModule.run_command"
        mock = self.mocker.patch(target)
        mock.side_effect = [
            (0, "Bundler version 4.0.0", ""),  # bundle --version
            (0, "", ""),  # bundle config set clean true
            (0, "Installing gems\n", ""),  # bundle install
        ]
        with set_module_args({"state": "present", "clean": True}):
            with pytest.raises(AnsibleExitJson):
                bundler.main()

        calls = get_run_command_calls(mock)
        assert any("config set clean true" in c for c in calls)
        assert not any("--clean" in c for c in calls)

    def test_clean_false_skips_version_check(self):
        target = "ansible.module_utils.basic.AnsibleModule.run_command"
        mock = self.mocker.patch(target)
        mock.return_value = (0, "Installing gems\n", "")
        with set_module_args({"state": "present", "clean": False}):
            with pytest.raises(AnsibleExitJson):
                bundler.main()

        calls = get_run_command_calls(mock)
        assert not any("--version" in c for c in calls)
        assert not any("--clean" in c for c in calls)
        assert not any("config set clean" in c for c in calls)

    def test_basic_install(self):
        target = "ansible.module_utils.basic.AnsibleModule.run_command"
        mock = self.mocker.patch(target)
        mock.return_value = (0, "Installing gems\n", "")
        with set_module_args({"state": "present"}):
            with pytest.raises(AnsibleExitJson) as exc:
                bundler.main()

        result = exc.value.args[0]
        assert result["changed"] is True
        calls = get_run_command_calls(mock)
        assert any("bundle install" in c for c in calls)

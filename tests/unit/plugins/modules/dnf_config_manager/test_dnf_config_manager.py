# Copyright (c) 2023, Andrew Hyatt <andy@hyatt.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
from unittest.mock import call, patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import dnf_config_manager as dnf_config_manager_module


def fixture(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "fixtures", name)
    with open(path, "r") as file:
        return file.read()


expected_repo_states_crb_enabled = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "crb",
        "rpmfusion-nonfree-updates",
    ],
}

expected_repo_states_crb_disabled = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source", "crb"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "rpmfusion-nonfree-updates",
    ],
}

call_get_repo_states = call(["/usr/bin/dnf", "repolist", "--all", "--verbose"], check_rc=True)
call_disable_crb = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-disabled", "crb"], check_rc=True)
call_enable_crb = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-enabled", "crb"], check_rc=True)


class TestDNFConfigManager(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_run_command = patch("ansible.module_utils.basic.AnsibleModule.run_command")
        self.run_command = self.mock_run_command.start()
        self.mock_path_exists = patch("os.path.exists")
        self.path_exists = self.mock_path_exists.start()
        self.path_exists.return_value = True
        self.module = dnf_config_manager_module
        self.mock_dnf4_repolist_crb_enabled = fixture("mock_dnf4_repolist_crb_enabled.txt")
        self.mock_dnf4_repolist_crb_disabled = fixture("mock_dnf4_repolist_crb_disabled.txt")
        self.mock_dnf4_repolist_no_status = fixture("mock_dnf4_repolist_no_status.txt")
        self.mock_dnf4_repolist_status_before_id = fixture("mock_dnf4_repolist_status_before_id.txt")

    def tearDown(self):
        super().tearDown()
        self.mock_run_command.stop()
        self.mock_path_exists.stop()

    def set_command_mock(self, execute_return=(0, "", ""), execute_side_effect=None):
        self.run_command.reset_mock()
        self.run_command.return_value = execute_return
        self.run_command.side_effect = execute_side_effect

    def execute_module(self, failed=False, changed=False):
        if failed:
            result = self.failed()
            self.assertTrue(result["failed"])
        else:
            result = self.changed(changed)
            self.assertEqual(result["changed"], changed)

        return result

    def failed(self):
        with self.assertRaises(AnsibleFailJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertTrue(result["failed"])
        return result

    def changed(self, changed=False):
        with self.assertRaises(AnsibleExitJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertEqual(result["changed"], changed)
        return result

    def test_get_repo_states(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_crb_enabled, ""))
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(calls=[call_get_repo_states, call_get_repo_states], any_order=False)

    def test_enable_disabled_repo(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, self.mock_dnf4_repolist_crb_disabled, ""), (0, "", ""), (0, self.mock_dnf4_repolist_crb_enabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_disabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], ["crb"])
        expected_calls = [call_get_repo_states, call_enable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_check_mode(self):
        with set_module_args({"name": ["crb"], "state": "enabled", "_ansible_check_mode": True}):
            side_effects = [(0, self.mock_dnf4_repolist_crb_disabled, ""), (0, self.mock_dnf4_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["changed_repos"], ["crb"])
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_disable_enabled_repo(self):
        with set_module_args({"name": ["crb"], "state": "disabled"}):
            side_effects = [(0, self.mock_dnf4_repolist_crb_enabled, ""), (0, "", ""), (0, self.mock_dnf4_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_disabled)
        self.assertEqual(result["changed_repos"], ["crb"])
        expected_calls = [call_get_repo_states, call_disable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_crb_already_enabled(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, self.mock_dnf4_repolist_crb_enabled, ""), (0, self.mock_dnf4_repolist_crb_enabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(calls=[call_get_repo_states, call_get_repo_states], any_order=False)

    def test_get_repo_states_fail_no_status(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_no_status, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed another repo id before next status")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_get_repo_states_fail_status_before_id(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_status_before_id, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed status before repo id")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_failed__unknown_repo_id(self):
        with set_module_args({"name": ["fake"]}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_crb_disabled, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "did not find repo with ID 'fake' in dnf repolist --all --verbose")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_failed_state_change_ineffective(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, self.mock_dnf4_repolist_crb_disabled, ""), (0, "", ""), (0, self.mock_dnf4_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf config-manager failed to make 'crb' enabled")
        expected_calls = [call_get_repo_states, call_enable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

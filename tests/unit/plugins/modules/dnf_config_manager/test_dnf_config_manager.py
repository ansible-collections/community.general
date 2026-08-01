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


expected_states_enabled_repo_dnf4 = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "crb",
        "rpmfusion-nonfree-updates",
    ],
}

expected_states_disabled_repo_dnf4 = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source", "crb"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "rpmfusion-nonfree-updates",
    ],
}

expected_states_enabled_repo_dnf5 = {
    "disabled": [
        "fedora-cisco-openh264-debuginfo",
        "fedora-cisco-openh264-source",
        "fedora-debuginfo",
        "fedora-source",
        "rawhide",
        "rawhide-debuginfo",
        "rawhide-source",
        "updates-debuginfo",
        "updates-source",
        "updates-testing",
        "updates-testing-debuginfo",
        "updates-testing-source",
    ],
    "enabled": [
        "copr:copr.fedorainfracloud.org:phracek:PyCharm",
        "fedora",
        "fedora-cisco-openh264",
        "google-chrome",
        "updates",
    ],
}

expected_states_disabled_repo_dnf5 = {
    "disabled": [
        "copr:copr.fedorainfracloud.org:phracek:PyCharm",
        "fedora-cisco-openh264-debuginfo",
        "fedora-cisco-openh264-source",
        "fedora-debuginfo",
        "fedora-source",
        "rawhide",
        "rawhide-debuginfo",
        "rawhide-source",
        "updates-debuginfo",
        "updates-source",
        "updates-testing",
        "updates-testing-debuginfo",
        "updates-testing-source",
    ],
    "enabled": [
        "fedora",
        "fedora-cisco-openh264",
        "google-chrome",
        "updates",
    ],
}

call_get_dnf_version = call(["/usr/bin/dnf", "--version"], check_rc=True)
call_get_repo_states_dnf4 = call(["/usr/bin/dnf", "repolist", "--all", "--verbose"], check_rc=True)
call_get_repo_states_dnf5 = call(["/usr/bin/dnf", "repo", "info", "--all"], check_rc=True)
call_disable_dnf4 = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-disabled", "crb"], check_rc=True)
call_enable_repo_dnf4 = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-enabled", "crb"], check_rc=True)
call_disable_dnf5 = call(
    ["/usr/bin/dnf", "config-manager", "setopt", "copr:copr.fedorainfracloud.org:phracek:PyCharm.enabled=0"],
    check_rc=True,
)
call_enable_repo_dnf5 = call(
    ["/usr/bin/dnf", "config-manager", "setopt", "copr:copr.fedorainfracloud.org:phracek:PyCharm.enabled=1"],
    check_rc=True,
)


class TestDNFConfigManager(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_run_command = patch("ansible.module_utils.basic.AnsibleModule.run_command")
        self.run_command = self.mock_run_command.start()
        self.mock_get_bin_path = patch("ansible.module_utils.basic.AnsibleModule.get_bin_path")
        self.get_bin_path = self.mock_get_bin_path.start()
        self.get_bin_path.return_value = "/usr/bin/dnf"
        self.module = dnf_config_manager_module
        self.mock_dnf4_version = fixture("mock_dnf4_version.txt")
        self.mock_dnf5_version = fixture("mock_dnf5_version.txt")
        self.mock_dnf4_states_repo_enabled = fixture("mock_dnf4_states_repo_enabled.txt")
        self.mock_dnf4_states_repo_disabled = fixture("mock_dnf4_states_repo_disabled.txt")
        self.mock_dnf5_states_repo_enabled = fixture("mock_dnf5_states_repo_enabled.txt")
        self.mock_dnf5_states_repo_disabled = fixture("mock_dnf5_states_repo_disabled.txt")
        self.mock_dnf4_repolist_no_status = fixture("mock_dnf4_repolist_no_status.txt")
        self.mock_dnf4_repolist_status_before_id = fixture("mock_dnf4_repolist_status_before_id.txt")

    def tearDown(self):
        super().tearDown()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()

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

    def test_get_repo_states_dnf4(self):
        with set_module_args({}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
            ]
            self.set_command_mock(
                execute_side_effect=side_effects, execute_return=(0, self.mock_dnf4_states_repo_enabled, "")
            )
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["changed_repos"], [])

        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf4, call_get_repo_states_dnf4]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_get_repo_states_dnf5(self):
        with set_module_args({}):
            side_effects = [
                (0, self.mock_dnf5_version, ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
            ]
            self.set_command_mock(
                execute_side_effect=side_effects, execute_return=(0, self.mock_dnf5_states_repo_enabled, "")
            )
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["changed_repos"], [])

        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf5, call_get_repo_states_dnf5]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_dnf4(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
                (0, "", ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_states_disabled_repo_dnf4)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["changed_repos"], ["crb"])

        expected_calls = [
            call_get_dnf_version,
            call_get_repo_states_dnf4,
            call_enable_repo_dnf4,
            call_get_repo_states_dnf4,
        ]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_dnf5(self):
        with set_module_args({"name": ["copr:copr.fedorainfracloud.org:phracek:PyCharm"], "state": "enabled"}):
            side_effects = [
                (0, self.mock_dnf5_version, ""),
                (0, self.mock_dnf5_states_repo_disabled, ""),
                (0, "", ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_states_disabled_repo_dnf5)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["changed_repos"], ["copr:copr.fedorainfracloud.org:phracek:PyCharm"])

        expected_calls = [
            call_get_dnf_version,
            call_get_repo_states_dnf5,
            call_enable_repo_dnf5,
            call_get_repo_states_dnf5,
        ]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_check_mode_dnf4(self):
        with set_module_args({"name": ["crb"], "state": "enabled", "_ansible_check_mode": True}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["changed_repos"], ["crb"])

        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf4]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_check_mode_dnf5(self):
        with set_module_args(
            {
                "name": ["copr:copr.fedorainfracloud.org:phracek:PyCharm"],
                "state": "enabled",
                "_ansible_check_mode": True,
            }
        ):
            side_effects = [
                (0, self.mock_dnf5_version, ""),
                (0, self.mock_dnf5_states_repo_disabled, ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["changed_repos"], ["copr:copr.fedorainfracloud.org:phracek:PyCharm"])

        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf5]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_disable_enabled_repo_dnf4(self):
        with set_module_args({"name": ["crb"], "state": "disabled"}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
                (0, "", ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["repo_states_post"], expected_states_disabled_repo_dnf4)
        self.assertEqual(result["changed_repos"], ["crb"])
        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf4, call_disable_dnf4, call_get_repo_states_dnf4]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_disable_enabled_repo_dnf5(self):
        with set_module_args({"name": ["copr:copr.fedorainfracloud.org:phracek:PyCharm"], "state": "disabled"}):
            side_effects = [
                (0, self.mock_dnf5_version, ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
                (0, "", ""),
                (0, self.mock_dnf5_states_repo_disabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["repo_states_post"], expected_states_disabled_repo_dnf5)
        self.assertEqual(result["changed_repos"], ["copr:copr.fedorainfracloud.org:phracek:PyCharm"])
        expected_calls = [call_get_dnf_version, call_get_repo_states_dnf5, call_disable_dnf5, call_get_repo_states_dnf5]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_crb_already_enabled_dnf4(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
                (0, self.mock_dnf4_states_repo_enabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf4)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(
            calls=[call_get_dnf_version, call_get_repo_states_dnf4, call_get_repo_states_dnf4], any_order=False
        )

    def test_crb_already_enabled_dnf5(self):
        with set_module_args({"name": ["copr:copr.fedorainfracloud.org:phracek:PyCharm"], "state": "enabled"}):
            side_effects = [
                (0, self.mock_dnf5_version, ""),
                (1, self.mock_dnf5_states_repo_enabled, ""),
                (0, self.mock_dnf5_states_repo_enabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["repo_states_post"], expected_states_enabled_repo_dnf5)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(
            calls=[call_get_dnf_version, call_get_repo_states_dnf5, call_get_repo_states_dnf5], any_order=False
        )

    def test_get_repo_states_fail_no_status(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_no_status, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed another repo id before next status")
        self.run_command.assert_has_calls(calls=[call_get_dnf_version, call_get_repo_states_dnf4], any_order=False)

    def test_get_repo_states_fail_status_before_id(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_repolist_status_before_id, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed status before repo id")
        self.run_command.assert_has_calls(calls=[call_get_dnf_version, call_get_repo_states_dnf4], any_order=False)

    def test_failed__unknown_repo_id(self):
        with set_module_args({"name": ["fake"]}):
            self.set_command_mock(execute_return=(0, self.mock_dnf4_states_repo_disabled, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "did not find repo with ID 'fake' in dnf repolist --all --verbose")
        self.run_command.assert_has_calls(calls=[call_get_dnf_version, call_get_repo_states_dnf4], any_order=False)

    def test_failed_state_change_ineffective(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [
                (0, self.mock_dnf4_version, ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
                (0, "", ""),
                (0, self.mock_dnf4_states_repo_disabled, ""),
            ]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf config-manager failed to make 'crb' enabled")
        expected_calls = [
            call_get_dnf_version,
            call_get_repo_states_dnf4,
            call_enable_repo_dnf4,
            call_get_repo_states_dnf4,
        ]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

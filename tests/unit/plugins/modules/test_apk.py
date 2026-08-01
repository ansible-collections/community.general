# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest import mock

from ansible_collections.community.general.plugins.modules import apk


class TestApkQueryLatest(unittest.TestCase):
    def setUp(self):
        self.module_names = [
            "bash",
            "g++",
        ]

    @mock.patch("ansible_collections.community.general.plugins.modules.apk.AnsibleModule")
    def test_not_latest(self, mock_module):
        apk.APK_PATH = [""]
        for module_name in self.module_names:
            command_output = f"{module_name}-2.0.0-r1 < 3.0.0-r2 "
            mock_module.run_command.return_value = (0, command_output, None)
            command_result = apk.query_latest(mock_module, module_name)
            self.assertFalse(command_result)

    @mock.patch("ansible_collections.community.general.plugins.modules.apk.AnsibleModule")
    def test_latest(self, mock_module):
        apk.APK_PATH = [""]
        for module_name in self.module_names:
            command_output = f"{module_name}-2.0.0-r1 = 2.0.0-r1 "
            mock_module.run_command.return_value = (0, command_output, None)
            command_result = apk.query_latest(mock_module, module_name)
            self.assertTrue(command_result)


class TestApkParseForPackages(unittest.TestCase):
    def test_no_packages(self):
        stdout = "fetch http://example/APKINDEX.tar.gz\nOK: 8350 MiB in 1692 packages\n"
        self.assertEqual(apk.parse_for_packages(stdout), [])

    def test_apk2_progress_lines(self):
        stdout = (
            "(1/3) Upgrading musl (1.2.4-r1 -> 1.2.4-r2)\n"
            "(2/3) Upgrading busybox (1.36.1-r5 -> 1.36.1-r6)\n"
            "(3/3) Upgrading ca-certificates-bundle (20230506-r0 -> 20240226-r0)\n"
            "OK: 8352 MiB in 1692 packages\n"
        )
        self.assertEqual(
            apk.parse_for_packages(stdout),
            ["musl", "busybox", "ca-certificates-bundle"],
        )

    def test_apk3_padded_progress_lines(self):
        # apk-tools 3 right-aligns the counter with leading spaces.
        stdout = (
            "(  1/126) Upgrading alpine-baselayout-data (3.7.0-r0 -> 3.7.1-r8)\n"
            "( 90/126) Upgrading openssh-sftp-server (10.0_p1-r10 -> 10.2_p1-r0)\n"
            "(126/126) Replacing tzdata (2025b-r0 -> 2025b-r0)\n"
            "OK: 8352 MiB in 1692 packages\n"
        )
        self.assertEqual(
            apk.parse_for_packages(stdout),
            ["alpine-baselayout-data", "openssh-sftp-server", "tzdata"],
        )


class TestApkUpgradePackages(unittest.TestCase):
    def _run_upgrade(self, stdout, rc=0):
        module = mock.Mock()
        module.check_mode = False
        module.run_command.return_value = (rc, stdout, "")
        module.exit_json.side_effect = SystemExit
        module.fail_json.side_effect = SystemExit
        apk.APK_PATH = [""]
        with self.assertRaises(SystemExit):
            apk.upgrade_packages(module, available=False)
        return module

    def test_nothing_to_upgrade(self):
        stdout = "fetch http://example/APKINDEX.tar.gz\nOK: 8350 MiB in 1692 packages\n"
        module = self._run_upgrade(stdout)
        module.exit_json.assert_called_once()
        kwargs = module.exit_json.call_args.kwargs
        self.assertFalse(kwargs["changed"])
        self.assertEqual(kwargs["packages"], [])

    def test_commit_hook_banner_is_not_a_change(self):
        # Regression test for https://github.com/ansible-collections/community.general/issues/12223:
        # a commit hook (mrtest) prints a banner before the "OK:" line, so stdout no longer
        # starts with "OK". Nothing was upgraded, so the module must report changed=False.
        stdout = (
            "Executing post-commit mrtest_nag.sh\n"
            "* \n"
            "* You have installed some packages via mrtest!\n"
            "* These packages are pinned to the MR version and will not be updated by apk.\n"
            "* \n"
            "* .mrtest-97664-alpine=20260529.065046\n"
            "* \n"
            "* To check which packages are pinned, use 'apk info -R .mrtest-xxx'\n"
            "* Use 'mrtest zap' to clean up and allow updating them again.\n"
            "* \n"
            "OK: 8350.4 MiB in 1692 packages\n"
        )
        module = self._run_upgrade(stdout)
        module.exit_json.assert_called_once()
        kwargs = module.exit_json.call_args.kwargs
        self.assertFalse(kwargs["changed"])
        self.assertEqual(kwargs["packages"], [])

    def test_real_upgrade(self):
        stdout = (
            "(1/2) Upgrading musl (1.2.4-r1 -> 1.2.4-r2)\n"
            "(2/2) Upgrading busybox (1.36.1-r5 -> 1.36.1-r6)\n"
            "Executing busybox-1.36.1-r6.trigger\n"
            "OK: 8352 MiB in 1692 packages\n"
        )
        module = self._run_upgrade(stdout)
        module.exit_json.assert_called_once()
        kwargs = module.exit_json.call_args.kwargs
        self.assertTrue(kwargs["changed"])
        self.assertEqual(kwargs["packages"], ["musl", "busybox"])

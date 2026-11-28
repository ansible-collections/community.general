# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules import drweb_info


class TestDrwebCtlInfoModule(unittest.TestCase):
    """Unit tests for the drweb_info module."""

    @classmethod
    def setUpClass(cls):
        cls.mock_ansible_basic = Mock()
        cls.mock_ansible_basic.AnsibleModule = Mock()

        cls.patcher_basic = patch.dict(
            "sys.modules",
            {"ansible.module_utils.basic": cls.mock_ansible_basic},
        )
        cls.patcher_basic.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher_basic.stop()

    def setUp(self):
        self.mock_ansible_basic.AnsibleModule.reset_mock()

        self.mock_module = Mock()
        self.mock_module.params = {}
        self.mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
        self.mock_module.exit_json = Mock()
        self.mock_module.check_mode = False
        self.mock_module.get_bin_path = Mock(return_value="/opt/drweb.com/bin/drweb-ctl")
        self.mock_module.run_command = Mock(return_value=(0, "", ""))

        self.mock_ansible_basic.AnsibleModule.return_value = self.mock_module

    def _setup_module_params(self, **params):
        default_params = {
            "command": "license",
            "parameter": None,
            "lines": 20,
        }
        default_params.update(params)
        self.mock_module.params = default_params

    def _module(self):
        return drweb_info.DrwebCtlInfoModule(
            self.mock_module,
            self.mock_module.get_bin_path.return_value,
        )

    def _command(self, call_number=0):
        return self.mock_module.run_command.call_args_list[call_number].args[0]

    # ---------------------------------------------------------------- license

    def test_license_successful(self):
        self._setup_module_params(command="license")
        self.mock_module.run_command.side_effect = [
            (0, "License: active\nSerial number: ABC-123\nExpires: 2027-01-01\n", ""),
            (0, "Dr.Web for Unix 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["license"]["License"], "active")
        self.assertEqual(result["license"]["Serial number"], "ABC-123")
        self.assertEqual(
            self._command(),
            ["/opt/drweb.com/bin/drweb-ctl", "license"],
        )

    # ---------------------------------------------------------------- appinfo

    def test_appinfo(self):
        self._setup_module_params(command="appinfo")
        self.mock_module.run_command.side_effect = [
            (0, "Application: Dr.Web for Unix\nVersion: 13.0.0\n", ""),
            (0, "Dr.Web for Unix 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["appinfo"]["Version"], "13.0.0")
        self.assertEqual(result["drweb_version"], "13.0.0")

    # --------------------------------------------------------------- baseinfo

    def test_baseinfo_loaded(self):
        self._setup_module_params(command="baseinfo")
        self.mock_module.run_command.side_effect = [
            (0, "Virus base version: 2026.10.01\nRecords: 1234567\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["baseinfo"]["loaded"])

    def test_baseinfo_not_loaded(self):
        self._setup_module_params(command="baseinfo")
        self.mock_module.run_command.side_effect = [
            (0, "Virus databases are not loaded\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["baseinfo"]["loaded"])

    # ---------------------------------------------------------------- threats

    def test_threats(self):
        self._setup_module_params(command="threats")
        self.mock_module.run_command.side_effect = [
            (0, "Threats:\n/tmp/eicar.com | EICAR Test File\n/tmp/bad.exe | Trojan.Win32.Bad\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(len(result["threats"]), 2)
        self.assertIn("EICAR", result["threats"][0])

    # ------------------------------------------------------------- quarantine

    def test_quarantine(self):
        self._setup_module_params(command="quarantine")
        self.mock_module.run_command.side_effect = [
            (0, "Quarantine:\n/tmp/eicar.com\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["quarantine"], ["/tmp/eicar.com"])

    # ----------------------------------------------------------------- cfshow

    def test_cfshow_parameter(self):
        self._setup_module_params(command="cfshow", parameter="Update.LogLevel")
        self.mock_module.run_command.side_effect = [
            (0, "Update.LogLevel = info\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertIn("Update.LogLevel", result["cfvalue"])
        self.assertEqual(
            self._command(),
            ["/opt/drweb.com/bin/drweb-ctl", "cfshow", "Update.LogLevel"],
        )

    def test_cfshow_empty_parameter(self):
        self._setup_module_params(command="cfshow", parameter="")
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'parameter' must not be empty when command=cfshow")

    # --------------------------------------------------------------------- log

    def test_log(self):
        self._setup_module_params(command="log", lines=3)
        self.mock_module.run_command.side_effect = [
            (0, "line1\nline2\nline3\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["log_lines"], ["line1", "line2", "line3"])
        self.assertEqual(
            self._command(),
            ["/opt/drweb.com/bin/drweb-ctl", "log", "-s", "3"],
        )

    def test_log_invalid_lines(self):
        self._setup_module_params(command="log", lines=0)
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'lines' must be greater than zero when command=log")

    # ---------------------------------------------------------------- check_rc

    def test_read_only_uses_check_rc_false(self):
        self._setup_module_params(command="baseinfo")
        self.mock_module.run_command.side_effect = [
            (0, "Virus databases are not loaded\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        self._module().apply()

        call_kwargs = self.mock_module.run_command.call_args_list[0].kwargs
        self.assertEqual(call_kwargs.get("check_rc"), False)

    # -------------------------------------------------------------------- bin

    @patch("ansible_collections.community.general.plugins.modules.drweb_info.AnsibleModule")
    def test_drweb_ctl_not_installed(self, mock_ansible_module):
        mock_module = Mock()

        mock_module.get_bin_path.side_effect = lambda name, required=False: (
            mock_module.fail_json(msg=f"Failed to find required executable '{name}' in PATH")
            if name == "drweb-ctl" and required
            else None
        )
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        with self.assertRaises(SystemExit) as context:
            drweb_info.main()

        self.assertIn("fail_json called", str(context.exception))

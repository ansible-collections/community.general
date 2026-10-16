# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules import drweb_ctl


class TestDrwebCtlModule(unittest.TestCase):
    """Unit tests for the drweb_ctl module."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()

        cls.mock_ansible_basic = Mock()
        cls.mock_ansible_basic.AnsibleModule = Mock()

        cls.patcher_basic = patch.dict(
            "sys.modules",
            {
                "ansible.module_utils.basic": cls.mock_ansible_basic,
            },
        )
        cls.patcher_basic.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher_basic.stop()
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

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

        self.scan_path = os.path.join(
            self.test_dir,
            "scanme",
        )
        os.makedirs(self.scan_path, exist_ok=True)

    def _setup_module_params(self, **params):
        default_params = {
            "name": "test-drweb",
            "command": "license",
            "path": None,
            "parameter": None,
            "value": None,
            "lines": 20,
        }
        default_params.update(params)
        self.mock_module.params = default_params

    def _module(self):
        return drweb_ctl.DrwebCtlModule(
            self.mock_module,
            self.mock_module.get_bin_path.return_value,
        )

    def _command(self, call_number=0):
        return self.mock_module.run_command.call_args_list[call_number].args[0]

    def test_license_successful(self):
        self._setup_module_params(command="license")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "License: active\nSerial number: ABC-123\nExpires: 2027-01-01\n",
                "",
            ),
            (0, "Dr.Web for Unix 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertEqual(result["license"]["License"], "active")
        self.assertEqual(
            result["license"]["Serial number"],
            "ABC-123",
        )
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "license",
            ],
        )

    def test_appinfo(self):
        self._setup_module_params(command="appinfo")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Application: Dr.Web for Unix\nVersion: 13.0.0\n",
                "",
            ),
            (0, "Dr.Web for Unix 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["appinfo"]["Version"], "13.0.0")
        self.assertEqual(result["drweb_version"], "13.0.0")

    def test_baseinfo_loaded(self):
        self._setup_module_params(command="baseinfo")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Virus base version: 2026.10.01\nRecords: 1234567\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["baseinfo"]["loaded"])

    def test_baseinfo_not_loaded(self):
        self._setup_module_params(command="baseinfo")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Virus databases are not loaded\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["baseinfo"]["loaded"])

    def test_update(self):
        self._setup_module_params(command="update")
        self.mock_module.run_command.side_effect = [
            (0, "Update completed\n", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "update",
            ],
        )

    def test_update_in_check_mode(self):
        self._setup_module_params(command="update")
        self.mock_module.check_mode = True

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(
            result["cmd"],
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "update",
            ],
        )
        self.mock_module.run_command.assert_not_called()

    def test_scan_successful(self):
        self._setup_module_params(
            command="scan",
            path=self.scan_path,
        )
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Total: 100 Infected: 2 Suspicious: 1\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["scan_result"]["scanned"], 100)
        self.assertEqual(result["scan_result"]["infected"], 2)
        self.assertEqual(result["scan_result"]["suspicious"], 1)
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "scan",
                self.scan_path,
            ],
        )

    def test_scan_in_check_mode(self):
        self._setup_module_params(
            command="scan",
            path=self.scan_path,
        )
        self.mock_module.check_mode = True

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(
            result["cmd"],
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "scan",
                self.scan_path,
            ],
        )
        self.mock_module.run_command.assert_not_called()

    def test_scan_missing_path(self):
        self._setup_module_params(command="scan", path=None)
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'path' is required when command=scan")

    def test_scan_nonexistent_path(self):
        self._setup_module_params(command="scan", path="/nonexistent/path")
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="Scan path does not exist: /nonexistent/path")

    def test_threats(self):
        self._setup_module_params(command="threats")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Threats:\n/tmp/eicar.com | EICAR Test File\n/tmp/bad.exe | Trojan.Win32.Bad\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(len(result["threats"]), 2)
        self.assertIn("EICAR", result["threats"][0])

    def test_quarantine(self):
        self._setup_module_params(command="quarantine")
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Quarantine:\n/tmp/eicar.com\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(
            result["quarantine"],
            ["/tmp/eicar.com"],
        )

    def test_cfset_changes_value(self):
        self._setup_module_params(
            command="cfset",
            parameter="Update.LogLevel",
            value="debug",
        )
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Update.LogLevel = info\n",
                "",
            ),
            (0, "", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(
            self._command(0),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "cfshow",
                "Update.LogLevel",
            ],
        )
        self.assertEqual(
            self._command(1),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "cfset",
                "Update.LogLevel",
                "debug",
            ],
        )

    def test_cfset_idempotent(self):
        self._setup_module_params(
            command="cfset",
            parameter="Update.LogLevel",
            value="debug",
        )
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Update.LogLevel = debug\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["current_value"], "debug")
        self.assertEqual(
            self._command(0),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "cfshow",
                "Update.LogLevel",
            ],
        )
        self.assertEqual(
            self._command(1),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "--version",
            ],
        )
        self.assertEqual(
            len(self.mock_module.run_command.call_args_list),
            2,
        )

    def test_cfset_in_check_mode_when_value_differs(self):
        self._setup_module_params(
            command="cfset",
            parameter="Update.LogLevel",
            value="debug",
        )
        self.mock_module.check_mode = True
        self.mock_module.run_command.return_value = (
            0,
            "Update.LogLevel = info\n",
            "",
        )

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(result["current_value"], "info")
        self.assertEqual(result["desired_value"], "debug")
        self.assertEqual(
            result["cmd"],
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "cfset",
                "Update.LogLevel",
                "debug",
            ],
        )
        self.assertEqual(
            self.mock_module.run_command.call_count,
            1,
        )

    def test_cfset_in_check_mode_when_value_is_current(self):
        self._setup_module_params(
            command="cfset",
            parameter="Update.LogLevel",
            value="debug",
        )
        self.mock_module.check_mode = True
        self.mock_module.run_command.return_value = (
            0,
            "Update.LogLevel = debug\n",
            "",
        )

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["current_value"], "debug")
        self.assertEqual(
            self.mock_module.run_command.call_count,
            1,
        )

    def test_cfset_missing_parament(self):
        self._setup_module_params(command="cfset", parameter=None, value="debug")
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'parameter' is required when command=cfset")

    def test_cfset_missing_value(self):
        self._setup_module_params(command="cfset", parameter="Update.LogLevel", value=None)
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'value' is required when command=cfset")

    def test_cfshow_parameter(self):
        self._setup_module_params(
            command="cfshow",
            parameter="Update.LogLevel",
        )
        self.mock_module.run_command.side_effect = [
            (
                0,
                "Update.LogLevel = info\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertIn(
            "Update.LogLevel",
            result["cfvalue"],
        )
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "cfshow",
                "Update.LogLevel",
            ],
        )

    def test_reload(self):
        self._setup_module_params(command="reload")
        self.mock_module.run_command.side_effect = [
            (0, "", ""),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "reload",
            ],
        )

    def test_reload_in_check_mode(self):
        self._setup_module_params(command="reload")
        self.mock_module.check_mode = True

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(
            result["cmd"],
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "reload",
            ],
        )
        self.mock_module.run_command.assert_not_called()

    def test_log(self):
        self._setup_module_params(
            command="log",
            lines=3,
        )
        self.mock_module.run_command.side_effect = [
            (
                0,
                "line1\nline2\nline3\n",
                "",
            ),
            (0, "Dr.Web 13.0.0", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(
            result["log_lines"],
            ["line1", "line2", "line3"],
        )
        self.assertEqual(
            self._command(),
            [
                "/opt/drweb.com/bin/drweb-ctl",
                "log",
                "-s",
                "3",
            ],
        )

    def test_log_invalid_lines(self):
        self._setup_module_params(command="log", lines=0)
        with self.assertRaises(Exception) as context:
            self._module().apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="'lines' must be greater than zero when command=log")

    def test_check_mode_read_only(self):
        self._setup_module_params(command="license")
        self.mock_module.check_mode = True

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.mock_module.run_command.assert_not_called()

    @patch("ansible_collections.community.general.plugins.modules.drweb_ctl.AnsibleModule")
    def test_drweb_ctl_not_installed(
        self,
        mock_ansible_module,
    ):
        mock_module = Mock()

        mock_module.get_bin_path.side_effect = lambda name, required=False: (
            mock_module.fail_json(msg=(f"Failed to find required executable '{name}' in PATH"))
            if name == "drweb-ctl" and required
            else None
        )
        mock_module.fail_json.side_effect = SystemExit("fail_json called")
        mock_ansible_module.return_value = mock_module

        with self.assertRaises(SystemExit) as context:
            drweb_ctl.main()

        self.assertIn(
            "fail_json called",
            str(context.exception),
        )

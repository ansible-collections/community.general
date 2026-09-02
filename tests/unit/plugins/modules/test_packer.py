# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules import packer


class TestPackerModule(unittest.TestCase):
    """Unit tests for the packer module."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
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
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        self.mock_ansible_basic.AnsibleModule.reset_mock()
        self.mock_module = Mock()
        self.mock_module.params = {}
        self.mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
        self.mock_module.exit_json = Mock()
        self.mock_module.check_mode = False
        self.mock_module.get_bin_path = Mock(return_value="/usr/local/bin/packer")
        self.mock_module.run_command = Mock(return_value=(0, "", ""))
        self.mock_ansible_basic.AnsibleModule.return_value = self.mock_module
        self.template_path = os.path.join(self.test_dir, "test.pkr.hcl")
        with open(self.template_path, "w") as f:
            f.write('source "null" "test" {\n  communicator = "none"\n}\n\nbuild {\n  sources = ["null.test"]\n}\n')

    def _setup_module_params(self, **params):
        default_params = {
            "name": "test-build",
            "state": "build",
            "template": self.template_path,
            "variables": {},
            "var_files": [],
            "only": None,
            "except_builders": None,
            "force": False,
            "parallel": True,
            "color": False,
            "machine_readable": False,
            "cleanup": False,
            "log_level": "info",
        }
        default_params.update(params)
        self.mock_module.params = default_params

    def _module(self):
        return packer.PackerModule(self.mock_module, self.mock_module.get_bin_path.return_value)

    def _command(self):
        """Return the first run_command call (the main packer command, not version check)."""
        return self.mock_module.run_command.call_args_list[0].args[0]

    def test_init_successful(self):
        self._setup_module_params(state="init")
        self.mock_module.run_command.side_effect = [
            (0, "Plugins installed successfully", ""),
            (0, "Packer v1.9.4", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertIn("Plugins installed", result["stdout"])
        self.assertEqual(self._command(), ["/usr/local/bin/packer", "init", self.template_path])

    def test_build_successful(self):
        self._setup_module_params(state="build")
        self.mock_module.run_command.side_effect = [
            (0, "--> null.test: null artifact\nBuild finished successfully", ""),
            (0, "Packer v1.9.4", ""),
        ]

        result = self._module().apply()

        self.assertTrue(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertEqual(result["artifacts"][0]["type"], "null.test")
        self.assertEqual(result["artifacts"][0]["name"], "null artifact")

    def test_build_with_force(self):
        self._setup_module_params(state="build", force=True)
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        self.assertIn("-force", self._command())

    def test_build_with_only(self):
        self._setup_module_params(state="build", only=["null.test"])
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        self.assertIn("-only", self._command())
        self.assertIn("null.test", self._command())

    def test_build_with_variables(self):
        self._setup_module_params(state="build", variables={"aws_region": "us-west-2", "instance_type": "t2.micro"})
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        command = self._command()
        self.assertIn("-var", command)
        self.assertIn("aws_region=us-west-2", command)
        self.assertIn("instance_type=t2.micro", command)

    def test_build_with_var_files(self):
        var_file = os.path.join(self.test_dir, "vars.pkrvars.hcl")
        with open(var_file, "w") as f:
            f.write('aws_region = "us-west-2"\n')

        self._setup_module_params(state="build", var_files=[var_file])
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        command = self._command()
        self.assertIn("-var-file", command)
        self.assertIn(var_file, command)

    def test_build_with_parallel_disabled(self):
        self._setup_module_params(state="build", parallel=False)
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        self.assertIn("-parallel=false", self._command())

    def test_build_with_color_disabled(self):
        self._setup_module_params(state="build", color=False)
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        self.assertIn("-no-color", self._command())

    def test_build_with_color_enabled(self):
        self._setup_module_params(state="build", color=True)
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        self.assertNotIn("-no-color", self._command())

    def test_build_with_machine_readable(self):
        self._setup_module_params(state="build", machine_readable=True)
        mock_output = "artifact,0,amazon-ebs,ami-12345678\nartifact,1,docker,my-image:latest\n"
        self.mock_module.run_command.side_effect = [
            (0, mock_output, ""),
            (0, "Packer v1.9.4", ""),
        ]

        result = self._module().apply()

        self.assertIn("-machine-readable", self._command())
        self.assertEqual(len(result["artifacts"]), 2)
        self.assertEqual(result["artifacts"][0]["type"], "amazon-ebs")
        self.assertEqual(result["artifacts"][0]["name"], "ami-12345678")
        self.assertEqual(result["artifacts"][1]["type"], "docker")
        self.assertEqual(result["artifacts"][1]["name"], "my-image:latest")

    def test_build_with_log_level(self):
        self._setup_module_params(state="build", log_level="debug")
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        command = self._command()
        self.assertEqual(command[1:3], ["--log-level", "debug"])

    def test_build_in_check_mode(self):
        self._setup_module_params(state="build", color=True)
        self.mock_module.check_mode = True
        self.mock_module.run_command.side_effect = [
            (0, "Template validated successfully", ""),
            (0, "Packer v1.9.4", ""),
        ]

        result = self._module().apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertEqual(self._command()[1], "validate")

    def test_run_command_uses_check_rc(self):
        self._setup_module_params(state="build")
        self.mock_module.run_command.side_effect = [
            (0, "Build finished", ""),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()

        call_kwargs = self.mock_module.run_command.call_args_list[0].kwargs
        self.assertEqual(call_kwargs.get("check_rc"), True)

    def test_build_failure(self):
        self._setup_module_params(state="build")
        self.mock_module.run_command.side_effect = [
            (1, "", "Error: missing required variable"),
            (0, "Packer v1.9.4", ""),
        ]

        self._module().apply()
        call_kwargs = self.mock_module.run_command.call_args_list[0].kwargs
        self.assertEqual(call_kwargs.get("check_rc"), True)

    def test_template_missing(self):
        self._setup_module_params(state="build", template="/nonexistent/template.pkr.hcl")

        with self.assertRaises(Exception):
            self._module().apply()
        self.mock_module.fail_json.assert_called_with(
            msg="Template file/directory does not exist: /nonexistent/template.pkr.hcl"
        )

    def test_var_file_not_exists(self):
        self._setup_module_params(state="build", var_files=["/nonexistent/file.pkrvars.hcl"])

        with self.assertRaises(Exception):
            self._module().apply()
        self.mock_module.fail_json.assert_called_with(msg="Variable file does not exist: /nonexistent/file.pkrvars.hcl")

    @patch("ansible_collections.community.general.plugins.modules.packer.AnsibleModule")
    def test_packer_not_installed(self, mock_ansible_module):
        mock_module = Mock()
        mock_module.get_bin_path.side_effect = lambda name, required=False: (
            mock_module.fail_json(msg=f"Failed to find required executable '{name}' in PATH")
            if name == "packer" and required
            else None
        )
        mock_module.fail_json.side_effect = Exception("fail_json called")
        mock_ansible_module.return_value = mock_module

        with self.assertRaises(Exception) as context:
            packer.main()
        self.assertIn("fail_json called", str(context.exception))


if __name__ == "__main__":
    unittest.main()

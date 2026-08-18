# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


class TestPackerModule(unittest.TestCase):
    """Unit tests for the packer module."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.mock_ansible_basic = Mock()
        cls.mock_ansible_basic.AnsibleModule = Mock()
        cls.mock_converters = Mock()
        cls.mock_converters.to_native = str
        cls.patcher_basic = patch.dict(
            "sys.modules",
            {
                "ansible.module_utils.basic": cls.mock_ansible_basic,
                "ansible.module_utils.common.text.converters": cls.mock_converters,
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
        self.mock_module.get_bin_path = Mock(return_value="/usr/local/bin/packer")
        self.mock_module.warn = Mock()
        self.mock_module.run_command = Mock(return_value=(0, "", ""))
        self.mock_ansible_basic.AnsibleModule.return_value = self.mock_module

        self.template_path = os.path.join(self.test_dir, "test.pkr.hcl")
        with open(self.template_path, "w") as f:
            f.write('source "null" "test" {\n  communicator = "none"\n}\n\nbuild {\n  sources = ["null.test"]\n}\n')

        for module_name in list(sys.modules.keys()):
            if "packer" in module_name and "ansible_collections" in module_name:
                del sys.modules[module_name]

    def tearDown(self):
        pass

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
            "color": True,
            "machine_readable": False,
            "cleanup": False,
            "log_level": "info",
        }
        default_params.update(params)
        self.mock_module.params = default_params

    def test_init_successful(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="init")
        self.mock_module.run_command.return_value = (0, "Plugins installed successfully", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertIn("Plugins installed", result["stdout"])
        self.assertIn("init", result["cmd"])

    def test_build_successful(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build")
        self.mock_module.run_command.return_value = (
            0,
            "--> null.test: null artifact\nBuild finished successfully",
            "",
        )

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertIn("artifacts", result)
        self.assertEqual(result["artifacts"][0]["type"], "null.test")
        self.assertEqual(result["artifacts"][0]["name"], "null artifact")

    def test_build_with_force(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", force=True)
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        cmd = result["cmd"]
        self.assertIn("-force", cmd)

    def test_build_with_only(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", only=["null.test"])
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        cmd = result["cmd"]
        self.assertIn("-only null.test", cmd)

    def test_build_with_variables(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", variables={"aws_region": "us-west-2", "instance_type": "t2.micro"})
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        cmd = result["cmd"]
        self.assertIn("-var aws_region=us-west-2", cmd)
        self.assertIn("-var instance_type=t2.micro", cmd)

    def test_build_with_var_files(self):
        from ansible_collections.community.general.plugins.modules import packer

        var_file = os.path.join(self.test_dir, "vars.pkrvars.hcl")
        with open(var_file, "w") as f:
            f.write('aws_region = "us-west-2"\n')

        self._setup_module_params(state="build", var_files=[var_file])
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        cmd = result["cmd"]
        self.assertIn(f"-var-file {var_file}", cmd)

    def test_build_with_parallel_disabled(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", parallel=False)
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        cmd = result["cmd"]
        self.assertIn("-parallel=false", cmd)

    def test_build_with_color_disabled(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", color=False)
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        cmd = result["cmd"]
        self.assertIn("-no-color", cmd)

    def test_build_with_machine_readable(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", machine_readable=True)
        mock_output = "artifact,0,amazon-ebs,ami-12345678\nartifact,1,docker,my-image:latest\n"
        self.mock_module.run_command.return_value = (0, mock_output, "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertTrue(result["changed"])
        cmd = result["cmd"]
        self.assertIn("-machine-readable", cmd)
        artifacts = result["artifacts"]
        self.assertEqual(len(artifacts), 2)
        self.assertEqual(artifacts[0]["type"], "amazon-ebs")
        self.assertEqual(artifacts[0]["name"], "ami-12345678")
        self.assertEqual(artifacts[1]["type"], "docker")
        self.assertEqual(artifacts[1]["name"], "my-image:latest")

    def test_build_with_log_level(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", log_level="debug")
        self.mock_module.run_command.return_value = (0, "Build finished", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        cmd = result["cmd"]
        self.assertIn("--log-level debug", cmd)

    def test_build_in_check_mode(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build")
        self.mock_module.check_mode = True
        self.mock_module.run_command.return_value = (0, "Template validated successfully", "")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)
        result = packer_module.apply()

        self.assertFalse(result["changed"])
        self.assertEqual(result["rc"], 0)
        self.assertIn("validate", result["cmd"])
        self.assertNotIn("build", result["cmd"])

    def test_build_failure(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build")
        self.mock_module.run_command.return_value = (1, "", "Error: missing required variable")

        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)

        with self.assertRaises(Exception) as context:
            packer_module.apply()
        self.assertIn("fail_json called", str(context.exception))

    def test_template_missing(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", template="/nonexistent/template.pkr.hcl")
        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)

        with self.assertRaises(Exception) as context:
            packer_module.apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(
            msg="Template file/directory does not exist: /nonexistent/template.pkr.hcl"
        )

    def test_var_file_not_exists(self):
        from ansible_collections.community.general.plugins.modules import packer

        self._setup_module_params(state="build", var_files=["/nonexistent/file.pkrvars.hcl"])
        packer_bin = self.mock_module.get_bin_path.return_value
        packer_module = packer.PackerModule(self.mock_module, packer_bin)

        with self.assertRaises(Exception) as context:
            packer_module.apply()
        self.assertIn("fail_json called", str(context.exception))
        self.mock_module.fail_json.assert_called_with(msg="Variable file does not exist: /nonexistent/file.pkrvars.hcl")

    @patch("os.getcwd")
    def test_packer_not_installed(self, mock_getcwd):
        from ansible_collections.community.general.plugins.modules import packer

        mock_getcwd.return_value = self.test_dir

        mock_module_for_test = Mock()
        mock_module_for_test.params = {
            "name": "test",
            "state": "build",
            "template": self.template_path,
            "variables": {},
            "var_files": [],
            "only": None,
            "except_builders": None,
            "force": False,
            "parallel": True,
            "color": True,
            "machine_readable": False,
            "cleanup": False,
            "log_level": "info",
        }
        mock_module_for_test.fail_json = Mock(side_effect=Exception("fail_json called"))
        mock_module_for_test.exit_json = Mock()
        mock_module_for_test.check_mode = False
        mock_module_for_test.warn = Mock()
        mock_module_for_test.run_command = Mock(return_value=(0, "", ""))

        def get_bin_path_side_effect(name, required=False):
            if name == "packer" and required:
                mock_module_for_test.fail_json(msg=f"Failed to find required executable '{name}' in PATH")
            return None

        mock_module_for_test.get_bin_path = Mock(side_effect=get_bin_path_side_effect)

        with patch(
            "ansible_collections.community.general.plugins.modules.packer.AnsibleModule",
            return_value=mock_module_for_test,
        ):
            with self.assertRaises(Exception) as context:
                packer.main()
            self.assertIn("fail_json called", str(context.exception))
            mock_module_for_test.fail_json.assert_called_once()

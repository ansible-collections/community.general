# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch


class TestLogrotateConfig(unittest.TestCase):
    """Unit tests for the logrotate_config module."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
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
        """Clean up after all tests."""
        cls.patcher_basic.stop()
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ansible_basic.AnsibleModule.reset_mock()
        self.mock_module = Mock()
        self.mock_module.params = {}
        self.mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
        self.mock_module.exit_json = Mock()
        self.mock_module.check_mode = False
        self.mock_module.get_bin_path = Mock(return_value="/usr/sbin/logrotate")
        self.mock_module.atomic_move = Mock()
        self.mock_module.warn = Mock()
        self.mock_module.run_command = Mock(return_value=(0, "", ""))
        self.mock_ansible_basic.AnsibleModule.return_value = self.mock_module
        self.config_dir = os.path.join(self.test_dir, "logrotate.d")
        os.makedirs(self.config_dir, exist_ok=True)
        for module_name in list(sys.modules.keys()):
            if "logrotate" in module_name or "ansible_collections.community.general.plugins.modules" in module_name:
                del sys.modules[module_name]

    def tearDown(self):
        """Clean up after test."""
        pass

    def _setup_module_params(self, **params):
        """Helper to set up module parameters."""
        default_params = {
            "name": "test",
            "state": "present",
            "config_dir": self.config_dir,
            "paths": ["/var/log/test/*.log"],
            "rotate_count": 7,
            "compress": True,
            "compression_method": "gzip",
            "delay_compress": False,
            "missing_ok": True,
            "not_if_empty": True,
            "copy_truncate": False,
            "date_ext": False,
            "date_format": "-%Y%m%d",
            "shared_scripts": False,
            "enabled": True,
        }
        default_params.update(params)
        self.mock_module.params = default_params

    def test_create_new_configuration(self):
        """Test creating a new logrotate configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params()
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()) as mock_file:
                    with patch("os.chmod") as mock_chmod:
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            self.assertTrue(result["changed"])
                            self.assertIn("config_file", result)
                            self.assertIn("config_content", result)
                            self.assertEqual(result["enabled_state"], True)
                            mock_file.assert_called_once()
                            mock_chmod.assert_called_once()

    def test_update_existing_configuration(self):
        """Test updating an existing logrotate configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(rotate_count=14)
        config_path = os.path.join(self.config_dir, "test")
        existing_content = """/var/log/test/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}"""

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return True
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("builtins.open", mock_open(read_data=existing_content)):
                with patch("os.remove") as mock_remove:
                    with patch("os.chmod") as mock_chmod:
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            self.assertTrue(result["changed"])
                            self.assertIn("14", result["config_content"])
                            mock_remove.assert_called()
                            mock_chmod.assert_called_once()

    def test_remove_configuration(self):
        """Test removing a logrotate configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(state="absent")
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            return path in (config_path, config_path + ".disabled")

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.remove") as mock_remove:
                logrotate_bin = self.mock_module.get_bin_path.return_value
                config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                result = config.apply()
                self.assertTrue(result["changed"])
                self.assertTrue(mock_remove.called)

    def test_disable_configuration(self):
        """Test disabling a logrotate configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(enabled=False)
        config_path = os.path.join(self.config_dir, "test")
        existing_content = """/var/log/test/*.log {
    daily
    rotate 7
}"""

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return True
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("builtins.open", mock_open(read_data=existing_content)):
                with patch("os.remove"):
                    with patch("os.chmod"):
                        mock_file_write = mock_open()
                        with patch("builtins.open", mock_file_write):
                            with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                                logrotate_bin = self.mock_module.get_bin_path.return_value
                                config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                                result = config.apply()
                        self.assertTrue(result["changed"])
                        self.assertEqual(result["enabled_state"], False)
                        self.assertTrue(result["config_file"].endswith(".disabled"))

    def test_enable_configuration(self):
        """Test enabling a disabled logrotate configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(enabled=True)
        config_path = os.path.join(self.config_dir, "test")
        existing_content = """/var/log/test/*.log {
    daily
    rotate 7
}"""

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path + ".disabled":
                return True
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("builtins.open", mock_open(read_data=existing_content)):
                with patch("os.remove"):
                    with patch("os.chmod"):
                        self.mock_module.atomic_move = Mock()
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            self.assertTrue(result["changed"])
                            self.assertEqual(result["enabled_state"], True)
                            self.assertFalse(result["config_file"].endswith(".disabled"))

    def test_validation_missing_paths(self):
        """Test validation when paths are missing for new configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(paths=None)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_validation_size_and_max_size_exclusive(self):
        """Test validation when both size and max_size are specified."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(size="100M", max_size="200M")
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_check_mode(self):
        """Test that no changes are made in check mode."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params()
        self.mock_module.check_mode = True
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                        logrotate_bin = self.mock_module.get_bin_path.return_value
                        config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                        result = config.apply()
                        self.assertTrue(result["changed"])

    def test_generate_config_with_scripts(self):
        """Test generating configuration with pre/post scripts."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(
            pre_rotate=["echo 'Pre-rotation'"],
            post_rotate=["systemctl reload test", "logger 'Rotation done'"],
            first_action=["echo 'First action'"],
            last_action=["echo 'Last action'"],
        )
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("prerotate", content)
                            self.assertIn("postrotate", content)
                            self.assertIn("firstaction", content)
                            self.assertIn("lastaction", content)
                            self.assertIn("systemctl reload test", content)
                            self.assertIn("echo 'Pre-rotation'", content)

    def test_compression_methods(self):
        """Test different compression methods."""
        from ansible_collections.community.general.plugins.modules import logrotate

        compression_methods = ["gzip", "bzip2", "xz", "zstd", "lzma", "lz4"]
        for method in compression_methods:
            with self.subTest(method=method):
                self._setup_module_params(compression_method=method)
                config_path = os.path.join(self.config_dir, "test")

                def exists_side_effect(path, current_config_path=config_path):
                    if path == self.config_dir:
                        return True
                    elif path == current_config_path:
                        return False
                    return False

                with patch("os.path.exists", side_effect=exists_side_effect):
                    with patch("os.makedirs"):
                        with patch("builtins.open", mock_open()):
                            with patch("os.chmod"):
                                with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                                    logrotate_bin = self.mock_module.get_bin_path.return_value
                                    config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                                    result = config.apply()
                                    content = result["config_content"]
                                    if method != "gzip":
                                        self.assertIn(f"compresscmd /usr/bin/{method}", content)
                                        if method == "zstd" or method == "lz4":
                                            self.assertIn(f"uncompresscmd /usr/bin/{method} -d", content)
                                        else:
                                            uncompress_cmd = f"{method}un{method}"
                                            self.assertIn(f"uncompresscmd /usr/bin/{uncompress_cmd}", content)

    def test_size_based_rotation(self):
        """Test size-based rotation configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(size="100M", rotation_period="daily")
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("size 100M", content)
                            self.assertNotIn("daily", content)

    def test_logrotate_not_installed(self):
        """Test error when logrotate is not installed."""
        from ansible_collections.community.general.plugins.modules import logrotate

        mock_module_for_test = Mock()
        mock_module_for_test.params = {
            "name": "test",
            "state": "present",
            "config_dir": self.config_dir,
            "paths": ["/var/log/test/*.log"],
            "rotate_count": 7,
            "compress": True,
            "compression_method": "gzip",
            "delay_compress": False,
            "missing_ok": True,
            "not_if_empty": True,
            "copy_truncate": False,
            "date_ext": False,
            "date_format": "-%Y%m%d",
            "shared_scripts": False,
            "enabled": True,
        }
        mock_module_for_test.fail_json = Mock(side_effect=Exception("fail_json called"))
        mock_module_for_test.exit_json = Mock()
        mock_module_for_test.check_mode = False

        def get_bin_path_side_effect(name, required=False):
            if name == "logrotate" and required:
                mock_module_for_test.fail_json(msg=f"Failed to find required executable '{name}' in PATH")
            return None

        mock_module_for_test.get_bin_path = Mock(side_effect=get_bin_path_side_effect)
        mock_module_for_test.atomic_move = Mock()
        mock_module_for_test.warn = Mock()
        mock_module_for_test.run_command = Mock(return_value=(0, "", ""))

        with patch(
            "ansible_collections.community.general.plugins.modules.logrotate.AnsibleModule",
            return_value=mock_module_for_test,
        ):
            with self.assertRaises(Exception) as context:
                logrotate.main()

            self.assertIn("fail_json called", str(context.exception))

            mock_module_for_test.get_bin_path.assert_called_once_with("logrotate", required=True)
            mock_module_for_test.fail_json.assert_called_once()

    def test_parse_existing_config_paths(self):
        """Test parsing paths from existing configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(paths=None)
        config_path = os.path.join(self.config_dir, "test")
        existing_content = """/var/log/app1/*.log
{
    daily
    rotate 7
    compress
}"""

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return True
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            mock_file_read = mock_open(read_data=existing_content)
            with patch("builtins.open", mock_file_read):
                with patch("os.remove"):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            self.assertTrue(result["changed"])
                            self.assertIn("/var/log/app1/*.log", result["config_content"])

    def test_no_delay_compress_parameter(self):
        """Test no_delay_compress parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(no_delay_compress=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("nodelaycompress", content)
                            self.assertTrue(result["changed"])

    def test_shred_and_shred_cycles_parameters(self):
        """Test shred and shred_cycles parameters."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(shred=True, shred_cycles=3)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("shred", content)
                            self.assertIn("shredcycles 3", content)
                            self.assertTrue(result["changed"])

    def test_copy_parameter(self):
        """Test copy parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(copy=True, copy_truncate=False)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("copy", content)
                            self.assertNotIn("copytruncate", content)
                            self.assertTrue(result["changed"])

    def test_rename_copy_parameter(self):
        """Test rename_copy parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(rename_copy=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("renamecopy", content)
                            self.assertTrue(result["changed"])

    def test_min_size_parameter(self):
        """Test min_size parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(min_size="100k")
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("minsize 100k", content)
                            self.assertTrue(result["changed"])

    def test_date_yesterday_parameter(self):
        """Test date_yesterday parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(date_ext=True, date_yesterday=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("dateext", content)
                            self.assertIn("dateyesterday", content)
                            self.assertTrue(result["changed"])

    def test_create_old_dir_parameter(self):
        """Test create_old_dir parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(old_dir="/var/log/archives", create_old_dir=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("olddir /var/log/archives", content)
                            self.assertIn("createolddir", content)
                            self.assertTrue(result["changed"])

    def test_start_parameter(self):
        """Test start parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(start=1)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("start 1", content)
                            self.assertTrue(result["changed"])

    def test_syslog_parameter(self):
        """Test syslog parameter."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(syslog=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertIn("syslog", content)
                            self.assertTrue(result["changed"])

    def test_validation_copy_and_copy_truncate_exclusive(self):
        """Test validation when both copy and copy_truncate are specified."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(copy=True, copy_truncate=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_validation_copy_and_rename_copy_exclusive(self):
        """Test validation when both copy and rename_copy are specified."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(copy=True, rename_copy=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_validation_shred_cycles_positive(self):
        """Test validation when shred_cycles is not positive."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(shred_cycles=0)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_validation_start_non_negative(self):
        """Test validation when start is negative."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(start=-1)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_validation_old_dir_and_no_old_dir_exclusive(self):
        """Test validation when both old_dir and no_old_dir are specified."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(old_dir="/var/log/archives", no_old_dir=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
            with self.assertRaises(Exception) as context:
                config.apply()
            self.assertIn("fail_json called", str(context.exception))

    def test_all_new_parameters_together(self):
        """Test all new parameters together in one configuration."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(
            no_delay_compress=True,
            shred=True,
            shred_cycles=3,
            copy=True,
            min_size="100k",
            date_ext=True,
            date_yesterday=True,
            old_dir="/var/log/archives",
            create_old_dir=True,
            start=1,
            syslog=True,
            rename_copy=False,
            copy_truncate=False,
            delay_compress=False,
        )

        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            logrotate_bin = self.mock_module.get_bin_path.return_value
                            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)
                            result = config.apply()
                            content = result["config_content"]
                            self.assertTrue(result["changed"])

                            self.assertIn("nodelaycompress", content)
                            self.assertIn("shred", content)
                            self.assertIn("shredcycles 3", content)
                            self.assertIn("copy", content)
                            self.assertIn("minsize 100k", content)
                            self.assertIn("dateext", content)
                            self.assertIn("dateyesterday", content)
                            self.assertIn("olddir /var/log/archives", content)
                            self.assertIn("createolddir", content)
                            self.assertIn("start 1", content)
                            self.assertIn("syslog", content)

                            lines = [line.strip() for line in content.split("\n")]
                            self.assertNotIn("copytruncate", lines)
                            self.assertNotIn("renamecopy", lines)
                            self.assertNotIn("delaycompress", lines)

    def test_parameter_interactions(self):
        """Test interactions between related parameters."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params(old_dir="/var/log/archives", no_old_dir=True)
        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

            with self.assertRaises(Exception) as context:
                config.apply()

            self.assertIn("fail_json called", str(context.exception))

        self._setup_module_params(copy=True, rename_copy=True)

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

            with self.assertRaises(Exception) as context:
                config.apply()

            self.assertIn("fail_json called", str(context.exception))

        self._setup_module_params(copy=True, copy_truncate=True)

        with patch("os.path.exists", side_effect=exists_side_effect):
            logrotate_bin = self.mock_module.get_bin_path.return_value
            config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

            with self.assertRaises(Exception) as context:
                config.apply()

            self.assertIn("fail_json called", str(context.exception))

    def test_size_format_validation(self):
        """Test validation of size format parameters."""
        from ansible_collections.community.general.plugins.modules import logrotate

        valid_sizes = ["100k", "100M", "1G", "10", "500K", "2M", "3G"]

        for size in valid_sizes:
            with self.subTest(valid_size=size):
                self._setup_module_params(size=size)
                config_path = os.path.join(self.config_dir, "test")

                def exists_side_effect(path, current_config_path=config_path):
                    if path == self.config_dir:
                        return True
                    elif path == current_config_path:
                        return False
                    return False

                with patch("os.path.exists", side_effect=exists_side_effect):
                    with patch("os.makedirs"):
                        with patch("builtins.open", mock_open()):
                            with patch("os.chmod"):
                                with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                                    logrotate_bin = self.mock_module.get_bin_path.return_value
                                    config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

                                    result = config.apply()
                                    self.assertIn(f"size {size}", result["config_content"])

        invalid_sizes = ["100kb", "M100", "1.5G", "abc", "100 MB"]

        for size in invalid_sizes:
            with self.subTest(invalid_size=size):
                self._setup_module_params(size=size)
                config_path = os.path.join(self.config_dir, "test")

                def exists_side_effect(path, current_config_path=config_path):
                    if path == self.config_dir:
                        return True
                    elif path == current_config_path:
                        return False
                    return False

                with patch("os.path.exists", side_effect=exists_side_effect):
                    logrotate_bin = self.mock_module.get_bin_path.return_value
                    config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

                    with self.assertRaises(Exception) as context:
                        config.apply()

                    self.assertIn("fail_json called", str(context.exception))

    def test_max_size_format_validation(self):
        """Test validation of max_size format parameters."""
        from ansible_collections.community.general.plugins.modules import logrotate

        valid_sizes = ["100k", "100M", "1G", "10", "500K", "2M", "3G"]

        for size in valid_sizes:
            with self.subTest(valid_size=size):
                self._setup_module_params(max_size=size)
                config_path = os.path.join(self.config_dir, "test")

                def exists_side_effect(path, current_config_path=config_path):
                    if path == self.config_dir:
                        return True
                    elif path == current_config_path:
                        return False
                    return False

                with patch("os.path.exists", side_effect=exists_side_effect):
                    with patch("os.makedirs"):
                        with patch("builtins.open", mock_open()):
                            with patch("os.chmod"):
                                with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                                    logrotate_bin = self.mock_module.get_bin_path.return_value
                                    config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

                                    result = config.apply()
                                    self.assertIn(f"maxsize {size}", result["config_content"])

        invalid_sizes = ["100kb", "M100", "1.5G", "abc", "100 MB"]

        for size in invalid_sizes:
            with self.subTest(invalid_size=size):
                self._setup_module_params(max_size=size)
                config_path = os.path.join(self.config_dir, "test")

                def exists_side_effect(path, current_config_path=config_path):
                    if path == self.config_dir:
                        return True
                    elif path == current_config_path:
                        return False
                    return False

                with patch("os.path.exists", side_effect=exists_side_effect):
                    logrotate_bin = self.mock_module.get_bin_path.return_value
                    config = logrotate.LogrotateConfig(self.mock_module, logrotate_bin)

                    with self.assertRaises(Exception) as context:
                        config.apply()

                    self.assertIn("fail_json called", str(context.exception))

    def test_logrotate_bin_used_in_apply(self):
        """Test that logrotate binary path is used in apply method."""
        from ansible_collections.community.general.plugins.modules import logrotate

        self._setup_module_params()

        test_logrotate_path = "/usr/local/sbin/logrotate"
        self.mock_module.get_bin_path.return_value = test_logrotate_path

        config_path = os.path.join(self.config_dir, "test")

        def exists_side_effect(path):
            if path == self.config_dir:
                return True
            elif path == config_path:
                return False
            return False

        with patch("os.path.exists", side_effect=exists_side_effect):
            with patch("os.makedirs"):
                with patch("builtins.open", mock_open()):
                    with patch("os.chmod"):
                        with patch.object(logrotate.LogrotateConfig, "_backup_config", create=True):
                            config = logrotate.LogrotateConfig(self.mock_module, test_logrotate_path)
                            config.apply()

                            self.mock_module.run_command.assert_called_once()
                            call_args = self.mock_module.run_command.call_args[0][0]
                            self.assertEqual(call_args[0], test_logrotate_path)


if __name__ == "__main__":
    unittest.main()

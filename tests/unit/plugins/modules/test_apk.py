# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest import mock
import unittest

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

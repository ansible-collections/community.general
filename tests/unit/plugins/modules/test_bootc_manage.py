# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules import bootc_manage
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestBootcManageModule(ModuleTestCase):

    def setUp(self):
        super(TestBootcManageModule, self).setUp()
        self.module = bootc_manage

    def tearDown(self):
        super(TestBootcManageModule, self).tearDown()

    def test_switch_without_image(self):
        """Failure if state is 'switch' but no image provided"""
        with set_module_args({'state': 'switch'}):
            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], "state is switch but all of the following are missing: image")

    def test_switch_with_image(self):
        """Test successful switch with image provided"""
        with set_module_args({'state': 'switch', 'image': 'example.com/image:latest'}):
            with patch('ansible.module_utils.basic.AnsibleModule.run_command') as run_command_mock:
                run_command_mock.return_value = (0, 'Queued for next boot: ', '')
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])

    def test_latest_state(self):
        """Test successful upgrade to the latest state"""
        with set_module_args({'state': 'latest'}):
            with patch('ansible.module_utils.basic.AnsibleModule.run_command') as run_command_mock:
                run_command_mock.return_value = (0, 'Queued for next boot: ', '')
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])

    def test_latest_state_no_change(self):
        """Test no change for latest state"""
        with set_module_args({'state': 'latest'}):
            with patch('ansible.module_utils.basic.AnsibleModule.run_command') as run_command_mock:
                run_command_mock.return_value = (0, 'No changes in ', '')
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()
            self.assertFalse(result.exception.args[0]['changed'])

    def test_switch_image_failure(self):
        """Test failure during image switch"""
        with set_module_args({'state': 'switch', 'image': 'example.com/image:latest'}):
            with patch('ansible.module_utils.basic.AnsibleModule.run_command') as run_command_mock:
                run_command_mock.return_value = (1, '', 'ERROR')
                with self.assertRaises(AnsibleFailJson) as result:
                    self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'ERROR: Command execution failed.')

    def test_latest_state_failure(self):
        """Test failure during upgrade"""
        with set_module_args({'state': 'latest'}):
            with patch('ansible.module_utils.basic.AnsibleModule.run_command') as run_command_mock:
                run_command_mock.return_value = (1, '', 'ERROR')
                with self.assertRaises(AnsibleFailJson) as result:
                    self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'ERROR: Command execution failed.')

# -*- coding: utf-8 -*-
# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.modules import lvg_rename
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleFailJson, AnsibleExitJson, ModuleTestCase, set_module_args)


VGS_OUTPUT = '''\
vg_data_testhost1;XKZ5gn-YhWY-NlrT-QCFN-qmMG-VGT9-7uOmex
vg_sys_testhost2;xgy2SJ-YlYd-fde2-e3oG-zdXL-0xGf-ihqG2H
'''


class TestLvgRename(ModuleTestCase):
    """Tests for lvg_rename internals"""
    module = lvg_rename
    module_path = 'ansible_collections.community.general.plugins.modules.lvg_rename'

    def setUp(self):
        """Prepare mocks for module testing"""
        super(TestLvgRename, self).setUp()

        self.mock_run_responses = {}

        patched_module_get_bin_path = patch('%s.AnsibleModule.get_bin_path' % (self.module_path))
        self.mock_module_get_bin_path = patched_module_get_bin_path.start()
        self.mock_module_get_bin_path.return_value = '/mocpath'
        self.addCleanup(patched_module_get_bin_path.stop)

        patched_module_run_command = patch('%s.AnsibleModule.run_command' % (self.module_path))
        self.mock_module_run_command = patched_module_run_command.start()
        self.addCleanup(patched_module_run_command.stop)

    def test_vg_not_found_by_name(self):
        """When the VG by the specified by vg name not found, the module should exit with error"""
        failed = True
        self.mock_module_run_command.side_effect = [(0, VGS_OUTPUT, '')]
        expected_msg = 'Both current (vg_missing) and new (vg_data_testhost2) VG are missing.'

        module_args = {
            'vg': 'vg_missing',
            'vg_new': 'vg_data_testhost2',
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 1)
        self.assertIs(result.exception.args[0]['failed'], failed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

    def test_vg_not_found_by_uuid(self):
        """When the VG by the specified vg UUID not found, the module should exit with error"""
        failed = True
        self.mock_module_run_command.side_effect = [(0, VGS_OUTPUT, '')]
        expected_msg = 'Both current (Yfj4YG-c8nI-z7w5-B7Fw-i2eM-HqlF-ApFVp0) and new (vg_data_testhost2) VG are missing.'

        module_args = {
            'vg': 'Yfj4YG-c8nI-z7w5-B7Fw-i2eM-HqlF-ApFVp0',
            'vg_new': 'vg_data_testhost2',
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 1)
        self.assertIs(result.exception.args[0]['failed'], failed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

    def test_vg_and_vg_new_both_exists(self):
        """When a VG found for both vg and vg_new options, the module should exit with error"""
        failed = True
        self.mock_module_run_command.side_effect = [(0, VGS_OUTPUT, '')]
        expected_msg = 'The new VG name (vg_sys_testhost2) is already in use.'

        module_args = {
            'vg': 'vg_data_testhost1',
            'vg_new': 'vg_sys_testhost2',
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 1)
        self.assertIs(result.exception.args[0]['failed'], failed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

    def test_vg_needs_renaming(self):
        """When the VG found for vg option and there is no VG for vg_new option,
            the module should call vgrename"""
        changed = True
        self.mock_module_run_command.side_effect = [
            (0, VGS_OUTPUT, ''),
            (0, '  Volume group "vg_data_testhost1" successfully renamed to "vg_data_testhost2"', '')
        ]
        expected_msg = '  Volume group "vg_data_testhost1" successfully renamed to "vg_data_testhost2"'

        module_args = {
            'vg': '/dev/vg_data_testhost1',
            'vg_new': 'vg_data_testhost2',
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 2)
        self.assertIs(result.exception.args[0]['changed'], changed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

    def test_vg_needs_renaming_in_check_mode(self):
        """When running in check mode and the VG found for vg option and there is no VG for vg_new option,
            the module should not call vgrename"""
        changed = True
        self.mock_module_run_command.side_effect = [(0, VGS_OUTPUT, '')]
        expected_msg = 'Running in check mode. The module would rename VG /dev/vg_data_testhost1 to vg_data_testhost2.'

        module_args = {
            'vg': '/dev/vg_data_testhost1',
            'vg_new': 'vg_data_testhost2',
            '_ansible_check_mode': True,
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 1)
        self.assertIs(result.exception.args[0]['changed'], changed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

    def test_vg_needs_no_renaming(self):
        """When the VG not found for vg option and the VG found for vg_new option,
            the module should not call vgrename"""
        changed = False
        self.mock_module_run_command.side_effect = [(0, VGS_OUTPUT, '')]
        expected_msg = 'The new VG (vg_data_testhost1) already exists, nothing to do.'

        module_args = {
            'vg': 'vg_data_testhostX',
            'vg_new': 'vg_data_testhost1',
        }
        with set_module_args(args=module_args):

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertEqual(len(self.mock_module_run_command.mock_calls), 1)
        self.assertIs(result.exception.args[0]['changed'], changed)
        self.assertEqual(result.exception.args[0]['msg'], expected_msg)

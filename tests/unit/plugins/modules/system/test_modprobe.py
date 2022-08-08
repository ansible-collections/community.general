# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat.mock import Mock
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.modules.system.modprobe import Modprobe


class TestLoadModule(ModuleTestCase):
    def setUp(self):
        super(TestLoadModule, self).setUp()

        self.mock_module_loaded = patch(
            'ansible_collections.community.general.plugins.modules.system.modprobe.Modprobe.module_loaded'
        )
        self.mock_run_command = patch('ansible.module_utils.basic.AnsibleModule.run_command')
        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.module_loaded = self.mock_module_loaded.start()
        self.run_command = self.mock_run_command.start()
        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestLoadModule, self).tearDown()
        self.mock_module_loaded.stop()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()

    def test_load_module_success(self):
        set_module_args(dict(
            name='test',
            state='present',
        ))

        module = AnsibleModule(
            argument_spec=dict(
                name=dict(type='str', required=True),
                state=dict(type='str', default='present', choices=['absent', 'present']),
                params=dict(type='str', default=''),
            ),
            supports_check_mode=True,
        )

        self.get_bin_path.side_effect = ['modprobe']
        self.module_loaded.side_effect = [True]
        self.run_command.side_effect = [(0, '', '')]

        modprobe = Modprobe(module)
        modprobe.load_module()

        assert modprobe.result == {
            'changed': True,
            'name': 'test',
            'params': '',
            'state': 'present',
        }

    def test_load_module_unchanged(self):
        set_module_args(dict(
            name='test',
            state='present',
        ))

        module = AnsibleModule(
            argument_spec=dict(
                name=dict(type='str', required=True),
                state=dict(type='str', default='present', choices=['absent', 'present']),
                params=dict(type='str', default=''),
            ),
            supports_check_mode=True,
        )

        module.warn = Mock()

        self.get_bin_path.side_effect = ['modprobe']
        self.module_loaded.side_effect = [False]
        self.run_command.side_effect = [(0, '', ''), (1, '', '')]

        modprobe = Modprobe(module)
        modprobe.load_module()

        module.warn.assert_called_once_with('')


class TestUnloadModule(ModuleTestCase):
    def setUp(self):
        super(TestUnloadModule, self).setUp()

        self.mock_module_loaded = patch(
            'ansible_collections.community.general.plugins.modules.system.modprobe.Modprobe.module_loaded'
        )
        self.mock_run_command = patch('ansible.module_utils.basic.AnsibleModule.run_command')
        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.module_loaded = self.mock_module_loaded.start()
        self.run_command = self.mock_run_command.start()
        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestUnloadModule, self).tearDown()
        self.mock_module_loaded.stop()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()

    def test_unload_module_success(self):
        set_module_args(dict(
            name='test',
            state='absent',
        ))

        module = AnsibleModule(
            argument_spec=dict(
                name=dict(type='str', required=True),
                state=dict(type='str', default='present', choices=['absent', 'present']),
                params=dict(type='str', default=''),
            ),
            supports_check_mode=True,
        )

        self.get_bin_path.side_effect = ['modprobe']
        self.module_loaded.side_effect = [False]
        self.run_command.side_effect = [(0, '', '')]

        modprobe = Modprobe(module)
        modprobe.unload_module()

        assert modprobe.result == {
            'changed': True,
            'name': 'test',
            'params': '',
            'state': 'absent',
        }

    def test_unload_module_failure(self):
        set_module_args(dict(
            name='test',
            state='absent',
        ))

        module = AnsibleModule(
            argument_spec=dict(
                name=dict(type='str', required=True),
                state=dict(type='str', default='present', choices=['absent', 'present']),
                params=dict(type='str', default=''),
            ),
            supports_check_mode=True,
        )

        module.fail_json = Mock()

        self.get_bin_path.side_effect = ['modprobe']
        self.module_loaded.side_effect = [True]
        self.run_command.side_effect = [(1, '', '')]

        modprobe = Modprobe(module)
        modprobe.unload_module()

        dummy_result = {
            'changed': False,
            'name': 'test',
            'state': 'absent',
            'params': '',
        }

        module.fail_json.assert_called_once_with(
            msg='', rc=1, stdout='', stderr='', **dummy_result
        )

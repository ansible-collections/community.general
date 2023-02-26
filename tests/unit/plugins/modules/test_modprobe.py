# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat.mock import Mock
from ansible_collections.community.general.tests.unit.compat.mock import mock_open
from ansible_collections.community.general.plugins.modules.modprobe import Modprobe, build_module


class TestLoadModule(ModuleTestCase):
    def setUp(self):
        super(TestLoadModule, self).setUp()

        self.mock_module_loaded = patch(
            'ansible_collections.community.general.plugins.modules.modprobe.Modprobe.module_loaded'
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

        module = build_module()

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

        module = build_module()

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
            'ansible_collections.community.general.plugins.modules.modprobe.Modprobe.module_loaded'
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

        module = build_module()

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

        module = build_module()

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


class TestModuleIsLoadedPersistently(ModuleTestCase):
    def setUp(self):
        if (sys.version_info[0] == 3 and sys.version_info[1] < 7) or (sys.version_info[0] == 2 and sys.version_info[1] < 7):
            self.skipTest('open_mock doesnt support readline in earlier python versions')

        super(TestModuleIsLoadedPersistently, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestModuleIsLoadedPersistently, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_module_is_loaded(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)
        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data='dummy')) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modules_files'):
                modprobe.modules_files = ['/etc/modules-load.d/dummy.conf']

                assert modprobe.module_is_loaded_persistently

        mocked_file.assert_called_once_with('/etc/modules-load.d/dummy.conf')

    def test_module_is_not_loaded_empty_file(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)
        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data='')) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modules_files'):
                modprobe.modules_files = ['/etc/modules-load.d/dummy.conf']

                assert not modprobe.module_is_loaded_persistently

        mocked_file.assert_called_once_with('/etc/modules-load.d/dummy.conf')

    def test_module_is_not_loaded_no_files(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)
        with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modules_files'):
            modprobe.modules_files = []

            assert not modprobe.module_is_loaded_persistently


class TestPermanentParams(ModuleTestCase):
    def setUp(self):
        if (sys.version_info[0] == 3 and sys.version_info[1] < 7) or (sys.version_info[0] == 2 and sys.version_info[1] < 7):
            self.skipTest('open_mock doesnt support readline in earlier python versions')
        super(TestPermanentParams, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestPermanentParams, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_module_permanent_params_exist(self):

        files_content = [
            'options dummy numdummies=4\noptions dummy dummy_parameter1=6',
            'options dummy dummy_parameter2=5 #Comment\noptions notdummy notdummy_param=5'
        ]
        mock_files_content = [mock_open(read_data=content).return_value for content in files_content]

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open()) as mocked_file:
            mocked_file.side_effect = mock_files_content
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modprobe_files'):
                modprobe.modprobe_files = ['/etc/modprobe.d/dummy1.conf', '/etc/modprobe.d/dummy2.conf']

                assert modprobe.permanent_params == set(['numdummies=4', 'dummy_parameter1=6', 'dummy_parameter2=5'])

    def test_module_permanent_params_empty(self):

        files_content = [
            '',
            ''
        ]
        mock_files_content = [mock_open(read_data=content).return_value for content in files_content]

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data='')) as mocked_file:
            mocked_file.side_effect = mock_files_content
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modprobe_files'):
                modprobe.modprobe_files = ['/etc/modprobe.d/dummy1.conf', '/etc/modprobe.d/dummy2.conf']

                assert modprobe.permanent_params == set()


class TestCreateModuleFIle(ModuleTestCase):
    def setUp(self):
        super(TestCreateModuleFIle, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestCreateModuleFIle, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_create_file(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open()) as mocked_file:
            modprobe.create_module_file()
            mocked_file.assert_called_once_with('/etc/modules-load.d/dummy.conf', 'w')
            mocked_file().write.assert_called_once_with('dummy\n')


class TestCreateModuleOptionsFIle(ModuleTestCase):
    def setUp(self):
        super(TestCreateModuleOptionsFIle, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestCreateModuleOptionsFIle, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_create_file(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            params='numdummies=4',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open()) as mocked_file:
            modprobe.create_module_options_file()
            mocked_file.assert_called_once_with('/etc/modprobe.d/dummy.conf', 'w')
            mocked_file().write.assert_called_once_with('options dummy numdummies=4\n')


class TestDisableOldParams(ModuleTestCase):
    def setUp(self):
        super(TestDisableOldParams, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestDisableOldParams, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_disable_old_params_file_changed(self):
        mock_data = 'options dummy numdummies=4'

        set_module_args(dict(
            name='dummy',
            state='present',
            params='numdummies=4',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data=mock_data)) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modprobe_files'):
                modprobe.modprobe_files = ['/etc/modprobe.d/dummy1.conf']
                modprobe.disable_old_params()
                mocked_file.assert_called_with('/etc/modprobe.d/dummy1.conf', 'w')
                mocked_file().write.assert_called_once_with('#options dummy numdummies=4')

    def test_disable_old_params_file_unchanged(self):
        mock_data = 'options notdummy numdummies=4'

        set_module_args(dict(
            name='dummy',
            state='present',
            params='numdummies=4',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data=mock_data)) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modprobe_files'):
                modprobe.modprobe_files = ['/etc/modprobe.d/dummy1.conf']
                modprobe.disable_old_params()
                mocked_file.assert_called_once_with('/etc/modprobe.d/dummy1.conf')


class TestDisableModulePermanent(ModuleTestCase):
    def setUp(self):
        super(TestDisableModulePermanent, self).setUp()

        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')

        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        """Teardown."""
        super(TestDisableModulePermanent, self).tearDown()

        self.mock_get_bin_path.stop()

    def test_disable_module_permanent_file_changed(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            params='numdummies=4',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data='dummy')) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modules_files'):
                modprobe.modules_files = ['/etc/modules-load.d/dummy.conf']
                modprobe.disable_module_permanent()
                mocked_file.assert_called_with('/etc/modules-load.d/dummy.conf', 'w')
                mocked_file().write.assert_called_once_with('#dummy')

    def test_disable_module_permanent_file_unchanged(self):

        set_module_args(dict(
            name='dummy',
            state='present',
            params='numdummies=4',
            persistent='present'
        ))

        module = build_module()

        self.get_bin_path.side_effect = ['modprobe']

        modprobe = Modprobe(module)

        with patch('ansible_collections.community.general.plugins.modules.modprobe.open', mock_open(read_data='notdummy')) as mocked_file:
            with patch('ansible_collections.community.general.plugins.modules.modprobe.Modprobe.modules_files'):
                modprobe.modules_files = ['/etc/modules-load.d/dummy.conf']
                modprobe.disable_module_permanent()
                mocked_file.assert_called_once_with('/etc/modules-load.d/dummy.conf')

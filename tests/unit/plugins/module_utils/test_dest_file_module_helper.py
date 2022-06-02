# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or
# https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import os
import json

from ansible_collections.community.general.tests.unit.plugins.modules.conftest import patch_ansible_module
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException

from ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file import (
    dest_file_sanity_check,
    check_if_dest_exists,
    check_if_parent_is_writeable,
    check_if_dest_is_readable,
    check_if_dest_is_regular_file,
    DestNotExists,
    DestNotReadable,
    DestNotWriteable,
    DestNotRegularFile,
    ParentNotWriteable,
    CantCreateBackup,
    DestFileModuleHelper)


MODULE_PATH = 'ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file.{}'

FAKE_DEST = '/this/is/a/fake/dest'
FAKE_TEMP_FILE = '/fake/temp/file'
FAKE_DEST_BACKUP = FAKE_DEST + '.bkp'
FAKE_DATA_CURRENT = 'fake data'
FAKE_DATA_CHANGED = 'fake data changed'


FILE_SANITY_CHECK_TEST_CASE = {
    'dest_not_exists_no_create': {
        'allow_creation': False,
        'backup': False,
        'exists': False,
        'writable_parent': False,
        'readable': False,
        'writeable': False,
        'regular_file': False,
        'expect_raise': DestNotExists,
    },
    'dest_not_exists_create_parent_not_writable': {
        'allow_creation': True,
        'backup': False,
        'exists': False,
        'writable_parent': False,
        'readable': False,
        'writeable': False,
        'regular_file': False,
        'expect_raise': ParentNotWriteable,
    },
    'dest_not_exists_create_parent_writable': {
        'allow_creation': True,
        'backup': False,
        'exists': False,
        'writable_parent': True,
        'writeable': False,
        'readable': False,
        'regular_file': False,
        'expect_raise': None,
    },
    'dest_exists_not_readable': {
        'allow_creation': False,
        'backup': False,
        'exists': True,
        'writable_parent': False,
        'readable': False,
        'writeable': False,
        'regular_file': False,
        'expect_raise': DestNotReadable,
    },
    'dest_exists_not_writeable': {
        'allow_creation': False,
        'backup': False,
        'exists': True,
        'writable_parent': False,
        'readable': True,
        'writeable': False,
        'regular_file': False,
        'expect_raise': DestNotWriteable,
    },
    'dest_exists_readable_not_regular_file': {
        'allow_creation': False,
        'backup': False,
        'exists': True,
        'writable_parent': False,
        'readable': True,
        'writeable': True,
        'regular_file': False,
        'expect_raise': DestNotRegularFile,
    },
    'dest_not_exists_create_backup': {
        'allow_creation': True,
        'backup': True,
        'exists': False,
        'writable_parent': True,
        'readable': False,
        'writeable': True,
        'regular_file': False,
        'expect_raise': None,
    },
    'dest_exists_backup_parent_not_writable': {
        'allow_creation': False,
        'backup': True,
        'exists': True,
        'writable_parent': False,
        'readable': True,
        'writeable': True,
        'regular_file': True,
        'expect_raise': CantCreateBackup,
    },
    'dest_exists_backup_parent_writable': {
        'allow_creation': False,
        'backup': True,
        'exists': True,
        'writable_parent': True,
        'readable': True,
        'writeable': True,
        'regular_file': True,
        'expect_raise': None,
    },
}


class TestDestFileSanityCheck():

    @pytest.mark.parametrize(
        'exists,os_stat_side_effect', (
            (False, FileNotFoundError),
            (True, PermissionError),
            (True, None)),
        ids=['dest_not_exists',
             'dest_not_readable',
             'dest_exists_and_readable'])
    def test_check_if_dest_exist(self,
                                 exists, os_stat_side_effect,
                                 mocker):
        mocker.patch('os.stat', return_value=exists,
                     side_effect=os_stat_side_effect)
        assert(check_if_dest_exists(FAKE_DEST) == exists)
        os.stat.assert_called_once_with(FAKE_DEST)

    @pytest.mark.parametrize('expected', ((True), (False)))
    def test_if_parent_not_writeable(self, expected, mocker):
        mocker.patch('os.access', return_value=expected)
        assert(check_if_parent_is_writeable(FAKE_DEST) == expected)
        os.access.assert_called_once_with(os.path.dirname(FAKE_DEST), os.W_OK)

    @pytest.mark.parametrize('expected', ((True), (False)))
    def test_check_if_dest_is_readable(self, expected, mocker):
        mocker.patch('os.access', return_value=expected)
        assert(check_if_dest_is_readable(FAKE_DEST) == expected)
        os.access.assert_called_once_with(FAKE_DEST, os.R_OK)

    @pytest.mark.parametrize('expected', ((True), (False)))
    def test_check_if_dest_is_regular_file(self, expected, mocker):
        mocker.patch('os.path.isfile', return_value=expected)
        assert(check_if_dest_is_regular_file(FAKE_DEST) == expected)
        os.path.isfile.assert_called_once_with(FAKE_DEST)

    @pytest.mark.parametrize(
        'allow_creation, backup, exists, writable_parent, readable, writeable, regular_file, expect_raise',
        (elem.values() for elem in FILE_SANITY_CHECK_TEST_CASE.values()),
        ids=(FILE_SANITY_CHECK_TEST_CASE.keys()))
    def test_check(self, allow_creation, backup, exists, writable_parent, readable, writeable, regular_file, expect_raise, mocker):
        mocker.patch(MODULE_PATH.format('check_if_dest_exists'), return_value=exists)
        mocker.patch(MODULE_PATH.format('check_if_parent_is_writeable'), return_value=writable_parent)
        mocker.patch(MODULE_PATH.format('check_if_dest_is_readable'), return_value=readable)
        mocker.patch(MODULE_PATH.format('check_if_dest_is_writeable'), return_value=writeable)
        mocker.patch(MODULE_PATH.format('check_if_dest_is_regular_file'), return_value=regular_file)
        if expect_raise is None:
            file_will_be_created = dest_file_sanity_check(FAKE_DEST, allow_creation, backup)
            assert((allow_creation and not exists) == file_will_be_created)
        else:
            with pytest.raises(expect_raise):
                dest_file_sanity_check(FAKE_DEST, allow_creation, backup)


TEST_CASE_DEST_FILE_MODULE = [
    [
        {
            'path': FAKE_DEST,
            'allow_creation': True,
            'backup': False,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'dest_not_exists_created',
            'exists': False,
            'changed': True,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': True,
            'backup': True,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'dest_not_exists_created_ensure_no_backup',
            'exists': False,
            'changed': True,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': True,
            'value': FAKE_DATA_CURRENT,
        },
        {
            'id': 'dest_exists_not_chanded',
            'exists': True,
            'changed': False,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': False,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'dest_exists_changed_no_backup',
            'exists': True,
            'changed': True,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': True,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'dest_exists_changed_with_backup',
            'exists': True,
            'changed': True,
            'check_mode': False,
            'backup_file': FAKE_DEST_BACKUP,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': False,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'check_mode_skip',
            'exists': True,
            'changed': True,
            'check_mode': True,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': False,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'sanity_check_raise',
            'exists': False,
            'changed': False,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': True,
            'atomic_move_raise': False,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': False,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'atomic_move_raise_no_backup',
            'exists': False,
            'changed': False,
            'check_mode': False,
            'backup_file': None,
            'sanity_check_raise': False,
            'atomic_move_raise': True,
        },
    ],
    [
        {
            'path': FAKE_DEST,
            'allow_creation': False,
            'backup': True,
            'value': FAKE_DATA_CHANGED,
        },
        {
            'id': 'atomic_move_raise_with_backup',
            'exists': True,
            'changed': False,
            'check_mode': False,
            'backup_file': FAKE_DEST_BACKUP,
            'sanity_check_raise': False,
            'atomic_move_raise': True,
        },
    ],
]


TEST_CASE_DEST_FILE_MODULE_IDS = (item[1]['id']
                                  for item in TEST_CASE_DEST_FILE_MODULE)


class TestDestFileModuleHelper():

    class _FakeDestFileModule(DestFileModuleHelper):

        module = dict(
            argument_spec=dict(
                path=dict(type='path', required=True, aliases=['dest']),
                allow_creation=dict(type='bool', default=True),
                backup=dict(type='bool', default=True),
                value=dict(type='str', required=True),
            ),
            add_file_common_args=True,
        )

        def __write_temp__(self, *args, **kwargs):
            self._tmpfile = self._write_in_tempfile(self.vars['value'])

        def __load_result_data__(self):
            """impement abstract DestFileModuleHelper.__load_result_data__"""
            self.vars.set(self.var_result_data, FAKE_DATA_CURRENT, diff=True)

        def __run__(self):
            self.vars.set(self.var_result_data, self.vars.value)

    @pytest.mark.parametrize('patch_ansible_module, test_case',
                             TEST_CASE_DEST_FILE_MODULE,
                             ids=TEST_CASE_DEST_FILE_MODULE_IDS,
                             indirect=['patch_ansible_module'])
    @pytest.mark.usefixtures('patch_ansible_module')
    def test_fake_dest_file_module(self, test_case, capfd, mocker):

        mock_tempfile_mkstemp = mocker.patch('tempfile.mkstemp', return_value=(1234, FAKE_TEMP_FILE))
        mock_os_write = mocker.patch('os.write')
        mock_os_close = mocker.patch('os.close')
        mock_dest_file_sanity_check = mocker.patch(MODULE_PATH.format('dest_file_sanity_check'))
        mock_atomic_move = mocker.patch(
            'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.atomic_move')
        mock_cleanup = mocker.patch(
            'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.cleanup')
        mock_backup_local = mocker.patch(
            'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.backup_local',
            return_value=FAKE_DEST_BACKUP)
        mock_set_fs_attributes_if_different = mocker.patch(
            'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.set_fs_attributes_if_different',
            side_effect=lambda file_args, changed, diff: changed)

        if test_case['sanity_check_raise']:
            mock_dest_file_sanity_check.side_effect = ModuleHelperException
        else:
            mock_dest_file_sanity_check.return_value = not test_case['exists']
        if test_case['atomic_move_raise']:
            mock_atomic_move.side_effect = OSError

        module = self._FakeDestFileModule()
        with pytest.raises(SystemExit):
            module.module.check_mode = test_case['check_mode']
            module.run()
        result = json.loads(capfd.readouterr().out)

        mock_dest_file_sanity_check.assert_called_once_with(module.vars['path'], module.vars['allow_creation'], module.vars['backup'])
        if test_case['sanity_check_raise'] or test_case['atomic_move_raise']:
            assert(result['failed'])
        if result['failed']:
            assert(test_case['sanity_check_raise'] or test_case['atomic_move_raise'])
            if test_case['atomic_move_raise']:
                if module.vars.get('backup_file'):
                    mock_backup_local.assert_called_once()
                    mock_cleanup.assert_called_with(FAKE_DEST_BACKUP)
                else:
                    mock_backup_local.assert_not_called()
                    with pytest.raises(AssertionError):
                        mock_cleanup.assert_called_with(FAKE_DEST_BACKUP)
                mock_cleanup.assert_any_call(FAKE_TEMP_FILE)
        else:
            assert(module.file_args is not None)
            if module.has_changed() and not test_case['check_mode']:
                mock_tempfile_mkstemp.assert_called_once()
                mock_cleanup.assert_called_with(FAKE_TEMP_FILE)
                mock_os_write.assert_called_once_with(1234, bytes(FAKE_DATA_CHANGED, 'utf-8'))
                mock_os_close.assert_called_once_with(1234)
                mock_atomic_move.assert_called_once_with(FAKE_TEMP_FILE, module.vars['path'])
            else:
                mock_tempfile_mkstemp.assert_not_called()
                mock_cleanup.assert_not_called()
                mock_os_write.assert_not_called()
                mock_os_close.assert_not_called()
                mock_atomic_move.assert_not_called()
            mock_set_fs_attributes_if_different.assert_called_once_with(module.file_args, module.changed, diff={'before': {}, 'after': {}})
            assert(result.get('backup_file') == test_case['backup_file'])
            assert(result['result'] == module.vars['value'])
            assert(result['created'] == (not test_case['exists']))
            assert(result['changed'] == test_case['changed'])

# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import os
from ansible_collections.community.general.tests.unit.plugins.modules.conftest import patch_ansible_module
from ansible_collections.community.general.tests.unit.compat.builtins import BUILTINS
from ansible_collections.community.general.plugins.module_utils.mh.mixins.dest import DestFileChecks
from ansible_collections.community.general.tests.integration.targets.module_helper.library.mdestfile import MDestFile

# Python 2 Compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

DUMMY_DEST = '/dummy/dest/file'
DUMMY_DEST_PARENT = os.path.dirname(DUMMY_DEST)
DUMMY_BACKUP = DUMMY_DEST + '_backup'
DUMMY_TMPF = '/tmp/dummy'
DUMMY_RAW_CONTENT = 'first line\nsecond line\n'.encode('utf-8')

POSSIBLE_DEST_FILE_CASE = {
    'not_exist_parent_not_writeable': {
        'exists': False,
        'is_writeable': False,
        'is_readable': False,
        'is_regular': False,
        'has_writeable_parent': False,
    },
    'not_exist_parent_writeable': {
        'exists': False,
        'is_writeable': False,
        'is_readable': False,
        'is_regular': False,
        'has_writeable_parent': True,
    },
    'exists_parent_not_writeable': {
        'exists': True,
        'is_writeable': True,
        'is_readable': True,
        'is_regular': True,
        'has_writeable_parent': False,
    },
    'is_not_regular_file': {
        'exists': True,
        'is_writeable': True,
        'is_readable': True,
        'is_regular': False,
        'has_writeable_parent': True,
    },
    'not_writeable': {
        'exists': True,
        'is_writeable': False,
        'is_readable': True,
        'is_regular': True,
        'has_writeable_parent': True,
    },
    'not_readable': {
        'exists': True,
        'is_writeable': True,
        'is_readable': False,
        'is_regular': True,
        'has_writeable_parent': True,
    },
    'exists_parent_writeable': {
        'exists': True,
        'is_writeable': True,
        'is_readable': True,
        'is_regular': True,
        'has_writeable_parent': True,
    },
}

CASES_CHECK_DEST_FILE = [
    {
        'id': '010_not_exist_parent_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_exist_parent_not_writeable'],
        'expected_info_result': {
            'can_create': False,
            'can_read': False,
            'can_write': False,
            'can_backup': False,
            'is_regular': False,
        },
    },
    {
        'id': '020_not_exist_parent_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_exist_parent_writeable'],
        'expected_info_result': {
            'can_create': True,
            'can_read': False,
            'can_write': True,
            'can_backup': False,
            'is_regular': False,
        },
    },
    {
        'id': '030_exists_parent_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['exists_parent_not_writeable'],
        'expected_info_result': {
            'can_create': False,
            'can_read': True,
            'can_write': True,
            'can_backup': False,
            'is_regular': True,
        },
    },
    {
        'id': '110_is_not_regular_file',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['is_not_regular_file'],
        'expected_info_result': {
            'can_create': False,
            'can_read': False,
            'can_write': False,
            'can_backup': False,
            'is_regular': False,
        },
    },
    {
        'id': '120_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_writeable'],
        'expected_info_result': {
            'can_create': False,
            'can_read': True,
            'can_write': False,
            'can_backup': True,
            'is_regular': True,
        },
    },
    {
        'id': 'not_readable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_readable'],
        'expected_info_result': {
            'can_create': False,
            'can_read': False,
            'can_write': True,
            'can_backup': False,
            'is_regular': True,
        },
    },
]
CASES_CHECK_DEST_FILE_ID = [item['id'] for item in CASES_CHECK_DEST_FILE]
CASES_CHECK_DEST_FILE_PARAMS = [[item['expected_info_result'], item['param_mock_os']]
                                for item in CASES_CHECK_DEST_FILE]

CASES_CHECK_DEST_FILE_CHECK = [
    {
        'id': '010_not_exists_not_create',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_exist_parent_not_writeable'],
        'param_check': {
            'create': False,
            'backup': False,
        },
        'expect_raise': DestFileChecks.NotExists,
    },
    {
        'id': '020_not_exists_create_parent_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_exist_parent_not_writeable'],
        'param_check': {
            'create': True,
            'backup': False,
        },
        'expect_raise': DestFileChecks.NotCreatable,
    },
    {
        'id': '030_not_exists_create_parent_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_exist_parent_writeable'],
        'param_check': {
            'create': True,
            'backup': False,
        },
        'expect_raise': None,
    },
    {
        'id': '110_dest_exists_not_regular',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['is_not_regular_file'],
        'param_check': {
            'create': False,
            'backup': False,
        },
        'expect_raise': DestFileChecks.NotRegularFile,
    },
    {
        'id': '120_dest_exists_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_writeable'],
        'param_check': {
            'create': False,
            'backup': False,
        },
        'expect_raise': DestFileChecks.NotWriteable,
    },
    {
        'id': '130_dest_exists_not_readeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['not_readable'],
        'param_check': {
            'create': False,
            'backup': False,
        },
        'expect_raise': DestFileChecks.NotReadable,
    },
    {
        'id': '140_dest_exists_ok',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['exists_parent_not_writeable'],
        'param_check': {
            'create': False,
            'backup': False,
        },
        'expect_raise': None,
    },
    {
        'id': '210_backup_parent_not_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['exists_parent_not_writeable'],
        'param_check': {
            'create': False,
            'backup': True,
        },
        'expect_raise': DestFileChecks.CanNotCreateBackup,
    },
    {
        'id': '220_backup_parent_writeable',
        'param_mock_os': POSSIBLE_DEST_FILE_CASE['exists_parent_writeable'],
        'param_check': {
            'create': False,
            'backup': True,
        },
        'expect_raise': None,
    },
]
CASES_CHECK_DEST_FILE_CHECK_ID = [item['id'] for item in CASES_CHECK_DEST_FILE_CHECK]
CASES_CHECK_DEST_FILE_CHECK_PARAMS = [[item['param_check'],
                                       item['expect_raise'],
                                       item['param_mock_os']]
                                      for item in CASES_CHECK_DEST_FILE_CHECK]

CASES_MIXIN_BACKUP_DEST = [
    {
        'id': '010_no_do_bakcup_can_not_backup',
        'module_args': {'path': DUMMY_DEST, 'backup': False},
        'dest_infos': {'can_backup': False},
        'expect_backup_file': None,
    },
    {
        'id': '020_do_backup_can_not_bakcup',
        'module_args': {'path': DUMMY_DEST, 'backup': True},
        'dest_infos': {'can_backup': False},
        'expect_backup_file': None,
    },
    {
        'id': '030_not_do_bakcup_can_backup',
        'module_args': {'path': DUMMY_DEST, 'backup': False},
        'dest_infos': {'can_backup': True},
        'expect_backup_file': None,
    },
    {
        'id': '040_do_backup_can_backup',
        'module_args': {'path': DUMMY_DEST, 'backup': True},
        'dest_infos': {'can_backup': True},
        'expect_backup_file': DUMMY_BACKUP,
    },
]
CASES_MIXIN_BACKUP_DEST_ID = [item['id'] for item in CASES_MIXIN_BACKUP_DEST]
CASES_MIXIN_BACKUP_DEST_PARAM = [[item['module_args'],
                                  item['dest_infos'],
                                  item['expect_backup_file']]
                                 for item in CASES_MIXIN_BACKUP_DEST]

CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST = [
    {
        'id': '010_no_changes',
        'module_args': {'path': DUMMY_DEST, 'mode': '0644', 'owner': 'foo'},
        'changes': {},
    },
    {
        'id': '110_change_mode',
        'module_args': {'path': DUMMY_DEST, 'mode': '0644', 'owner': 'foo'},
        'changes': {'mode': '0755'},
    },
    {
        'id': '120_change_owner',
        'module_args': {'path': DUMMY_DEST, 'mode': '0644', 'owner': 'foo'},
        'changes': {'owner': 'bar'},
    },
    {
        'id': '130_change_owner',
        'module_args': {'path': DUMMY_DEST, 'mode': '0644', 'owner': 'foo'},
        'changes': {'mode': '0755', 'owner': 'bar'},
    },
]
CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST_ID = [item['id']
                                             for item in CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST]
CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST_PARAMS = [[item['module_args'], item['changes']]
                                                 for item in CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST]

CASES_MIXIN_UPDATE_DEST = [
    {
        'id': '010_not_changed_can_not_create',
        'has_changed': False,
        'can_create': False,
        'is_created': False,
    },
    {
        'id': '020_not_changed_can_create',
        'has_changed': False,
        'can_create': True,
        'is_created': False,
    },
    {
        'id': '030_changed_can_not_create',
        'has_changed': True,
        'can_create': False,
        'is_created': False,
    },
    {
        'id': '040_changed_can_create',
        'has_changed': True,
        'can_create': True,
        'is_created': True,
    },
]
CASES_MIXIN_UPDATE_DEST_ID = [item['id'] for item in CASES_MIXIN_UPDATE_DEST]
CASES_MIXIN_UPDATE_DEST_PARAMS = [[item['has_changed'], item['can_create'], item['is_created']]
                                  for item in CASES_MIXIN_UPDATE_DEST]


@pytest.fixture(scope='function')
def _mock_os_for_dest_file(request, mocker):
    def mock_(path, mode):
        if path == DUMMY_DEST and mode == os.R_OK:
            return request.param['is_readable']
        elif path == DUMMY_DEST and mode == os.W_OK:
            return request.param['is_writeable']
        elif path == DUMMY_DEST_PARENT and mode == os.W_OK:
            return request.param['has_writeable_parent']
        else:
            raise ValueError('Unexpected case : path="{0}", mode="{1}"'.format(path, mode))
    mocker.patch('os.access', side_effect=mock_)
    mocker.patch('os.path.isfile', return_value=request.param['is_regular'])
    if request.param['exists']:
        mocker.patch('os.stat', return_value={'st_mode': 0,
                                              'st_ino': 0,
                                              'st_dev': 0,
                                              'st_nlink': 0,
                                              'st_uid': 0,
                                              'st_gid': 0,
                                              'st_size': 0,
                                              'st_atime': 0,
                                              'st_mtime': 0,
                                              'st_ctime': 0})
    else:
        mocker.patch('os.stat', side_effect=FileNotFoundError)


@pytest.mark.parametrize('expected,_mock_os_for_dest_file',
                         CASES_CHECK_DEST_FILE_PARAMS,
                         ids=CASES_CHECK_DEST_FILE_ID,
                         indirect=['_mock_os_for_dest_file'])
@pytest.mark.usefixtures('_mock_os_for_dest_file')
def test_010_check_dest_file_info(expected):
    dest_check = DestFileChecks(DUMMY_DEST)
    assert(dest_check.infos() == expected)


@pytest.mark.parametrize('param,raise_,_mock_os_for_dest_file',
                         CASES_CHECK_DEST_FILE_CHECK_PARAMS,
                         ids=CASES_CHECK_DEST_FILE_CHECK_ID,
                         indirect=['_mock_os_for_dest_file'])
@pytest.mark.usefixtures('_mock_os_for_dest_file')
def test_020_check_dest_file_check(param, raise_):
    dest_check = DestFileChecks(DUMMY_DEST)
    if raise_ is None:
        dest_check.check(param['create'], param['backup'])
    else:
        with pytest.raises(raise_):
            dest_check.check(param['create'], param['backup'])


@pytest.mark.parametrize('patch_ansible_module',
                         [{'path': DUMMY_DEST,
                           'allow_creation': True,
                           'backup': True,
                           'mode': '0644',
                           'owner': 'foo'}],
                         indirect=True)
@pytest.mark.usefixtures('patch_ansible_module')
def test_110_dest_file_mixin_init_module(mocker):
    mocker.patch('ansible_collections.community.general.plugins.module_utils.mh.mixins.dest.DestFileChecks')
    dummy = MDestFile()
    dummy.__init_module__()
    dummy._dest_check.assert_has_calls([mocker.call.check(True, True), mocker.call.infos()])
    assert(isinstance(dummy._dest_infos, mocker.MagicMock))
    assert(dummy._dest_attrs.get('path') == DUMMY_DEST)
    assert(dummy._dest_attrs.get('mode') == '0644')
    assert(dummy._dest_attrs.get('owner') == 'foo')
    assert(dummy.vars['created'] is False)


@pytest.mark.parametrize('patch_ansible_module,raw_content',
                         [[{'path': DUMMY_DEST}, None], [{'path': DUMMY_DEST}, DUMMY_RAW_CONTENT]],
                         ids=['0_dest_not_exists', '1_dest_exists'],
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_120_dest_file_mixin_read_dest(raw_content, mocker):
    if raw_content is None:
        mocker.patch(BUILTINS + '.open', side_effect=FileNotFoundError)
    else:
        mocker.patch(BUILTINS + '.open', mocker.mock_open(read_data=raw_content))
    dummy = MDestFile()
    dummy.__read_dest__()
    open.assert_called_once_with(DUMMY_DEST, 'rb')
    assert(dummy.raw_content == raw_content)


@pytest.mark.parametrize('patch_ansible_module', [{'path': DUMMY_DEST}], indirect=True)
@pytest.mark.usefixtures('patch_ansible_module')
def test_210_write_tempfile(mocker):
    dummy_fd = 1234321
    DUMMY_TMPF = '/tmp/dummy'
    mocker.patch('tempfile.mkstemp', return_value=(dummy_fd, DUMMY_TMPF))
    mocker.patch.multiple('os', write=mocker.DEFAULT, close=mocker.DEFAULT)

    dummy = MDestFile()
    dummy.raw_content = DUMMY_RAW_CONTENT
    dummy._write_temp_file()

    os.write.assert_called_once_with(dummy_fd, DUMMY_RAW_CONTENT)
    os.close.assert_called_once_with(dummy_fd)
    assert(DUMMY_TMPF in dummy.module.cleanup_files)
    assert(dummy._tmpfile == DUMMY_TMPF)


@pytest.mark.parametrize('patch_ansible_module,dest_infos,expected',
                         CASES_MIXIN_BACKUP_DEST_PARAM,
                         ids=CASES_MIXIN_BACKUP_DEST_ID,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_220_backup_dest(dest_infos, expected, mocker):
    dummy = MDestFile()
    mocker.patch.object(dummy.module, 'backup_local', return_value=expected)
    dummy._dest_infos = dest_infos
    dummy._backup_dest()
    assert(dummy.vars.get('backup_file') == expected)


@pytest.mark.parametrize('patch_ansible_module', [{'path': DUMMY_DEST}], indirect=True)
@pytest.mark.parametrize('raise_,backup_file',
                         [[None, None],
                          [None, DUMMY_BACKUP],
                          [Exception(), None],
                          [Exception(), DUMMY_BACKUP]],
                         ids=['0_no_raise_no_bakcup',
                              '1_no_raise_backup',
                              '2_raise_no_backup',
                              '3_raise_backup'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_230_replace_dest_with_temp(raise_, backup_file, mocker):
    dummy = MDestFile()
    mocker.patch.multiple(dummy.module,
                          atomic_move=mocker.MagicMock(side_effect=raise_))
    dummy._tmpfile = DUMMY_TMPF
    dummy.vars.set('backup_file', backup_file)
    try:
        dummy._replace_dest_with_temp()
    except Exception:
        if backup_file is not None:
            assert(DUMMY_BACKUP in dummy.module.cleanup_files)
        else:
            assert(DUMMY_BACKUP not in dummy.module.cleanup_files)
    dummy.module.atomic_move.assert_called_once_with(DUMMY_TMPF, DUMMY_DEST)


@pytest.mark.parametrize('patch_ansible_module,changes',
                         CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST_PARAMS,
                         ids=CASES_MIXIN_UPDATE_DEST_FS_ATTRIBUTEST_ID,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_240_update_dest_fs_attribute(changes, mocker):
    def set_fs_attributes_if_different(file_args, changed, diff):
        for key, val in changes.items():
            diff['after'][key] = val
            if file_args[key] != val:
                changed = True
        return changed
    dummy = MDestFile()
    mocker.patch.object(dummy.module, 'set_fs_attributes_if_different',
                        side_effect=set_fs_attributes_if_different)
    dummy._dest_attrs = dummy.module.load_file_common_arguments(dummy.module.params)
    dummy._update_dest_fs_attributes()
    for key, val in changes.items():
        assert(dummy.vars.meta(key).has_changed is True)
        meta_diff = dummy.vars.meta(key).diff_result
        assert(meta_diff['before'] is dummy._dest_attrs[key])
        assert(meta_diff['after'] is val)
    assert(dummy.changed is bool(changes))


@pytest.mark.parametrize('patch_ansible_module', [{'path': DUMMY_DEST}], indirect=True)
@pytest.mark.parametrize('has_changed,can_create,is_created',
                         CASES_MIXIN_UPDATE_DEST_PARAMS,
                         ids=CASES_MIXIN_UPDATE_DEST_ID)
@pytest.mark.usefixtures('patch_ansible_module')
def test_250_update_dest(has_changed, can_create, is_created, mocker):
    dummy = MDestFile()
    dummy.changed = has_changed
    dummy._dest_infos = {'can_create': can_create}
    dummy.vars.set('created', False)
    mock_ = mocker.MagicMock()
    mock_.attach_mock(mocker.patch.object(dummy, '_write_temp_file'), '_write_temp_file')
    mock_.attach_mock(mocker.patch.object(dummy, '_backup_dest'), '_backup_dest')
    mock_.attach_mock(mocker.patch.object(dummy, '_replace_dest_with_temp'), '_replace_dest_with_temp')
    mock_.attach_mock(mocker.patch.object(dummy, '_update_dest_fs_attributes'), '_update_dest_fs_attributes')
    dummy.__update_dest__()
    assert(dummy.vars['created'] == is_created)
    if is_created:
        mock_.assert_has_calls([
            mocker.call._write_temp_file(),
            mocker.call._backup_dest(),
            mocker.call._replace_dest_with_temp(),
            mocker.call._update_dest_fs_attributes(),
        ])
    else:
        mock_.assert_has_calls([
            mocker.call._update_dest_fs_attributes(),
        ])


@pytest.mark.parametrize('patch_ansible_module',
                         [{'path': DUMMY_DEST, 'value': 'third line'}],
                         indirect=True)
@pytest.mark.usefixtures('patch_ansible_module')
def test_910_run_call(mocker):
    dummy = MDestFile()
    mock_ = mocker.MagicMock()
    mock_.attach_mock(mocker.patch.object(dummy, '__init_module__'), '__init__module__')
    mock_.attach_mock(mocker.patch.object(dummy, '__read_dest__'), '__read_dest__')
    mock_.attach_mock(mocker.patch.object(dummy, '__update_dest__'), '__update_dest__')
    dummy.raw_content = DUMMY_RAW_CONTENT
    with pytest.raises(SystemExit):
        dummy.run()
    assert(dummy.has_changed() is True)
    mock_.assert_has_calls([
        mocker.call.__init__module__(),
        mocker.call.__read_dest__(),
        mocker.call.__update_dest__(),
    ])

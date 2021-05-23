# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules.files import sapcar_extract
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, set_module_args
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    if arg.endswith('SAPCAR_1010-70006178.EXE'):
        return '/tmp/SAPCAR_1010-70006178.EXE'
    else:
        if required:
            fail_json(msg='%r not found !' % arg)


class Testsapcar_extract(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_ensure_command_called(self):
        set_module_args({
            'path': "/tmp/HANA_CLIENT_REV2_00_053_00_LINUX_X86_64.SAR",
            'dest': "/tmp/test2",
            'binary_path': "/tmp/SAPCAR_1010-70006178.EXE"
        })

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = 'configuration updated'
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr  # successful execution

            with self.assertRaises(AnsibleExitJson) as result:
                sapcar_extract.main()
            self.assertFalse(result.exception.args[0]['changed'])  # ensure result is changed

        mock_run_command.assert_called_once_with('/tmp/SAPCAR_1010-70006178.EXE')

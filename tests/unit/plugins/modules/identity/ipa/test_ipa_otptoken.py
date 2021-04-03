# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.ipa import ipa_otptoken


@contextmanager
def patch_ipa(**kwargs):
    """Mock context manager for patching the methods in OTPTokenIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """
    obj = ipa_otptoken.OTPTokenIPAClient
    with patch.object(obj, 'login') as mock_login:
        with patch.object(obj, '_post_json', **kwargs) as mock_post:
            yield mock_login, mock_post


class TestIPAOTPToken(ModuleTestCase):
    def setUp(self):
        super(TestIPAOTPToken, self).setUp()
        self.module = ipa_otptoken

    def _test_base(self, module_args, return_value, mock_calls, changed):
        """Base function that's called by all the other test functions

        module_args (dict):
            Arguments passed to the module

        return_value (dict):
            Mocked return value of OTPTokenIPAClient.otptoken_show, as returned by the IPA API.
            This should be set to the current state. It will be changed to the desired state using the above arguments.
            (Technically, this is the return value of _post_json, but it's only checked by otptoken_show).

        mock_calls (list/tuple of dicts):
            List of calls made to OTPTokenIPAClient._post_json, in order.
            _post_json is called by all of the otptoken_* methods of the class.
            Pass an empty list if no calls are expected.

        changed (bool):
            Whether or not the module is supposed to be marked as changed
        """
        set_module_args(module_args)

        # Run the module
        with patch_ipa(return_value=return_value) as (mock_login, mock_post):
            with self.assertRaises(AnsibleExitJson) as exec_info:
                self.module.main()

        # Verify that the calls to _post_json match what is expected
        expected_call_count = len(mock_calls)
        if expected_call_count > 1:
            # Convert the call dicts to unittest.mock.call instances because `assert_has_calls` only accepts them
            converted_calls = []
            for call_dict in mock_calls:
                converted_calls.append(call(**call_dict))

            mock_post.assert_has_calls(converted_calls)
            self.assertEqual(len(mock_post.mock_calls), expected_call_count)
        elif expected_call_count == 1:
            mock_post.assert_called_once_with(**mock_calls[0])
        else:  # expected_call_count is 0
            mock_post.assert_not_called()

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_add_new_all_default(self):
        """Add a new OTP with all default values"""
        module_args = {
            'uniqueid': 'NewToken1'
        }
        return_value = {}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_add',
                'name': 'NewToken1',
                'item': {'ipatokendisabled': 'FALSE',
                         'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_add_new_all_default_with_aliases(self):
        """Add a new OTP with all default values using alias values"""
        module_args = {
            'name': 'NewToken1'
        }
        return_value = {}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_add',
                'name': 'NewToken1',
                'item': {'ipatokendisabled': 'FALSE',
                         'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_add_new_all_specified(self):
        """Add a new OTP with all default values"""
        module_args = {
            'uniqueid': 'NewToken1',
            'otptype': 'hotp',
            'secretkey': 'VGVzdFNlY3JldDE=',
            'description': 'Test description',
            'owner': 'pinky',
            'enabled': True,
            'notbefore': '20200101010101',
            'notafter': '20900101010101',
            'vendor': 'Acme',
            'model': 'ModelT',
            'serial': 'Number1',
            'state': 'present',
            'algorithm': 'sha256',
            'digits': 6,
            'offset': 10,
            'interval': 30,
            'counter': 30,
        }
        return_value = {}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_add',
                'name': 'NewToken1',
                'item': {'type': 'HOTP',
                         'ipatokenotpkey': 'KRSXG5CTMVRXEZLUGE======',
                         'description': 'Test description',
                         'ipatokenowner': 'pinky',
                         'ipatokendisabled': 'FALSE',
                         'ipatokennotbefore': '20200101010101Z',
                         'ipatokennotafter': '20900101010101Z',
                         'ipatokenvendor': 'Acme',
                         'ipatokenmodel': 'ModelT',
                         'ipatokenserial': 'Number1',
                         'ipatokenotpalgorithm': 'sha256',
                         'ipatokenotpdigits': '6',
                         'ipatokentotpclockoffset': '10',
                         'ipatokentotptimestep': '30',
                         'ipatokenhotpcounter': '30',
                         'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_already_existing_no_change_all_specified(self):
        """Add a new OTP with all values specified but needing no change"""
        module_args = {
            'uniqueid': 'NewToken1',
            'otptype': 'hotp',
            'secretkey': 'VGVzdFNlY3JldDE=',
            'description': 'Test description',
            'owner': 'pinky',
            'enabled': True,
            'notbefore': '20200101010101',
            'notafter': '20900101010101',
            'vendor': 'Acme',
            'model': 'ModelT',
            'serial': 'Number1',
            'state': 'present',
            'algorithm': 'sha256',
            'digits': 6,
            'offset': 10,
            'interval': 30,
            'counter': 30,
        }
        return_value = {'ipatokenuniqueid': 'NewToken1',
                        'type': 'HOTP',
                        'ipatokenotpkey': [{'__base64__': 'VGVzdFNlY3JldDE='}],
                        'description': ['Test description'],
                        'ipatokenowner': ['pinky'],
                        'ipatokendisabled': ['FALSE'],
                        'ipatokennotbefore': ['20200101010101Z'],
                        'ipatokennotafter': ['20900101010101Z'],
                        'ipatokenvendor': ['Acme'],
                        'ipatokenmodel': ['ModelT'],
                        'ipatokenserial': ['Number1'],
                        'ipatokenotpalgorithm': ['sha256'],
                        'ipatokenotpdigits': ['6'],
                        'ipatokentotpclockoffset': ['10'],
                        'ipatokentotptimestep': ['30'],
                        'ipatokenhotpcounter': ['30']}
        mock_calls = [
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            }
        ]
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_already_existing_one_change_all_specified(self):
        """Modify an existing OTP with one value specified needing change"""
        module_args = {
            'uniqueid': 'NewToken1',
            'otptype': 'hotp',
            'secretkey': 'VGVzdFNlY3JldDE=',
            'description': 'Test description',
            'owner': 'brain',
            'enabled': True,
            'notbefore': '20200101010101',
            'notafter': '20900101010101',
            'vendor': 'Acme',
            'model': 'ModelT',
            'serial': 'Number1',
            'state': 'present',
            'algorithm': 'sha256',
            'digits': 6,
            'offset': 10,
            'interval': 30,
            'counter': 30,
        }
        return_value = {'ipatokenuniqueid': 'NewToken1',
                        'type': 'HOTP',
                        'ipatokenotpkey': [{'__base64__': 'VGVzdFNlY3JldDE='}],
                        'description': ['Test description'],
                        'ipatokenowner': ['pinky'],
                        'ipatokendisabled': ['FALSE'],
                        'ipatokennotbefore': ['20200101010101Z'],
                        'ipatokennotafter': ['20900101010101Z'],
                        'ipatokenvendor': ['Acme'],
                        'ipatokenmodel': ['ModelT'],
                        'ipatokenserial': ['Number1'],
                        'ipatokenotpalgorithm': ['sha256'],
                        'ipatokenotpdigits': ['6'],
                        'ipatokentotpclockoffset': ['10'],
                        'ipatokentotptimestep': ['30'],
                        'ipatokenhotpcounter': ['30']}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_mod',
                'name': 'NewToken1',
                'item': {'description': 'Test description',
                         'ipatokenowner': 'brain',
                         'ipatokendisabled': 'FALSE',
                         'ipatokennotbefore': '20200101010101Z',
                         'ipatokennotafter': '20900101010101Z',
                         'ipatokenvendor': 'Acme',
                         'ipatokenmodel': 'ModelT',
                         'ipatokenserial': 'Number1',
                         'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_already_existing_all_valid_change_all_specified(self):
        """Modify an existing OTP with all valid values specified needing change"""
        module_args = {
            'uniqueid': 'NewToken1',
            'otptype': 'hotp',
            'secretkey': 'VGVzdFNlY3JldDE=',
            'description': 'New Test description',
            'owner': 'pinky',
            'enabled': False,
            'notbefore': '20200101010102',
            'notafter': '20900101010102',
            'vendor': 'NewAcme',
            'model': 'NewModelT',
            'serial': 'Number2',
            'state': 'present',
            'algorithm': 'sha256',
            'digits': 6,
            'offset': 10,
            'interval': 30,
            'counter': 30,
        }
        return_value = {'ipatokenuniqueid': 'NewToken1',
                        'type': 'HOTP',
                        'ipatokenotpkey': [{'__base64__': 'VGVzdFNlY3JldDE='}],
                        'description': ['Test description'],
                        'ipatokenowner': ['pinky'],
                        'ipatokendisabled': ['FALSE'],
                        'ipatokennotbefore': ['20200101010101Z'],
                        'ipatokennotafter': ['20900101010101Z'],
                        'ipatokenvendor': ['Acme'],
                        'ipatokenmodel': ['ModelT'],
                        'ipatokenserial': ['Number1'],
                        'ipatokenotpalgorithm': ['sha256'],
                        'ipatokenotpdigits': ['6'],
                        'ipatokentotpclockoffset': ['10'],
                        'ipatokentotptimestep': ['30'],
                        'ipatokenhotpcounter': ['30']}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_mod',
                'name': 'NewToken1',
                'item': {'description': 'New Test description',
                         'ipatokenowner': 'pinky',
                         'ipatokendisabled': 'TRUE',
                         'ipatokennotbefore': '20200101010102Z',
                         'ipatokennotafter': '20900101010102Z',
                         'ipatokenvendor': 'NewAcme',
                         'ipatokenmodel': 'NewModelT',
                         'ipatokenserial': 'Number2',
                         'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_delete_existing_token(self):
        """Delete an existing OTP"""
        module_args = {
            'uniqueid': 'NewToken1',
            'state': 'absent'
        }
        return_value = {'ipatokenuniqueid': 'NewToken1',
                        'type': 'HOTP',
                        'ipatokenotpkey': [{'__base64__': 'KRSXG5CTMVRXEZLUGE======'}],
                        'description': ['Test description'],
                        'ipatokenowner': ['pinky'],
                        'ipatokendisabled': ['FALSE'],
                        'ipatokennotbefore': ['20200101010101Z'],
                        'ipatokennotafter': ['20900101010101Z'],
                        'ipatokenvendor': ['Acme'],
                        'ipatokenmodel': ['ModelT'],
                        'ipatokenserial': ['Number1'],
                        'ipatokenotpalgorithm': ['sha256'],
                        'ipatokenotpdigits': ['6'],
                        'ipatokentotpclockoffset': ['10'],
                        'ipatokentotptimestep': ['30'],
                        'ipatokenhotpcounter': ['30']}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_del',
                'name': 'NewToken1'
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_disable_existing_token(self):
        """Disable an existing OTP"""
        module_args = {
            'uniqueid': 'NewToken1',
            'otptype': 'hotp',
            'enabled': False
        }
        return_value = {'ipatokenuniqueid': 'NewToken1',
                        'type': 'HOTP',
                        'ipatokenotpkey': [{'__base64__': 'KRSXG5CTMVRXEZLUGE======'}],
                        'description': ['Test description'],
                        'ipatokenowner': ['pinky'],
                        'ipatokendisabled': ['FALSE'],
                        'ipatokennotbefore': ['20200101010101Z'],
                        'ipatokennotafter': ['20900101010101Z'],
                        'ipatokenvendor': ['Acme'],
                        'ipatokenmodel': ['ModelT'],
                        'ipatokenserial': ['Number1'],
                        'ipatokenotpalgorithm': ['sha256'],
                        'ipatokenotpdigits': ['6'],
                        'ipatokentotpclockoffset': ['10'],
                        'ipatokentotptimestep': ['30'],
                        'ipatokenhotpcounter': ['30']}
        mock_calls = (
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            },
            {
                'method': 'otptoken_mod',
                'name': 'NewToken1',
                'item': {'ipatokendisabled': 'TRUE',
                          'all': True}
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_delete_not_existing_token(self):
        """Delete a OTP that does not exist"""
        module_args = {
            'uniqueid': 'NewToken1',
            'state': 'absent'
        }
        return_value = {}

        mock_calls = [
            {
                'method': 'otptoken_find',
                'name': None,
                'item': {'all': True,
                         'ipatokenuniqueid': 'NewToken1',
                         'timelimit': '0',
                         'sizelimit': '0'}
            }
        ]

        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_fail_post(self):
        """Fail due to an exception raised from _post_json"""
        set_module_args({
            'uniqueid': 'NewToken1'
        })

        with patch_ipa(side_effect=Exception('ERROR MESSAGE')) as (mock_login, mock_post):
            with self.assertRaises(AnsibleFailJson) as exec_info:
                self.module.main()

        self.assertEqual(exec_info.exception.args[0]['msg'], 'ERROR MESSAGE')


if __name__ == '__main__':
    unittest.main()

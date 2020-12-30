# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.ipa import ipa_pwpolicy


@contextmanager
def patch_ipa(**kwargs):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """
    obj = ipa_pwpolicy.PwPolicyIPAClient
    with patch.object(obj, 'login') as mock_login:
        with patch.object(obj, '_post_json', **kwargs) as mock_post:
            yield mock_login, mock_post


class TestIPAPwPolicy(ModuleTestCase):
    def setUp(self):
        super(TestIPAPwPolicy, self).setUp()
        self.module = ipa_pwpolicy

    def _test_base(self, module_args, return_value, mock_calls, changed):
        """Base function that's called by all the other test functions

        module_args (dict):
            Arguments passed to the module

        return_value (dict):
            Mocked return value of PwPolicyIPAClient.pwpolicy_find, as returned by the IPA API.
            This should be set to the current state. It will be changed to the desired state using the above arguments.
            (Technically, this is the return value of _post_json, but it's only checked by pwpolicy_find).
            An empty dict means that the policy doesn't exist.

        mock_calls (list/tuple of dicts):
            List of calls made to PwPolicyIPAClient._post_json, in order.
            _post_json is called by all of the pwpolicy_* methods of the class.
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

    def test_add(self):
        """Add a new policy"""
        module_args = {
            'group': 'admins',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {}
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'admins'
                }
            },
            {
                'method': 'pwpolicy_add',
                'name': 'admins',
                'item': {
                    'cospriority': '10',
                    'krbmaxpwdlife': '90',
                    'krbminpwdlife': '1',
                    'krbpwdhistorylength': '8',
                    'krbpwdmindiffchars': '3',
                    'krbpwdminlength': '16',
                    'krbpwdmaxfailure': '6',
                    'krbpwdfailurecountinterval': '60',
                    'krbpwdlockoutduration': '600'
                }
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_aliases(self):
        """Same as test_add, but uses the `name` alias for the `group` option"""
        module_args = {
            'name': 'admins',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {}
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'admins'
                }
            },
            {
                'method': 'pwpolicy_add',
                'name': 'admins',
                'item': {
                    'cospriority': '10',
                    'krbmaxpwdlife': '90',
                    'krbminpwdlife': '1',
                    'krbpwdhistorylength': '8',
                    'krbpwdmindiffchars': '3',
                    'krbpwdminlength': '16',
                    'krbpwdmaxfailure': '6',
                    'krbpwdfailurecountinterval': '60',
                    'krbpwdlockoutduration': '600'
                }
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_mod_different_args(self):
        """Policy exists, but some of the args are different and need to be modified"""
        module_args = {
            'group': 'sysops',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '60',
            'minpwdlife': '24',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '12',
            'maxfailcount': '8',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['sysops'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbminpwdlife': ['1'],
            'krbpwdhistorylength': ['8'],
            'krbpwdmindiffchars': ['3'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'krbpwdfailurecountinterval': ['60'],
            'krbpwdlockoutduration': ['600'],
            'dn': 'cn=sysops,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            },
            {
                'method': 'pwpolicy_mod',
                'name': 'sysops',
                'item': {
                    'cospriority': '10',
                    'krbmaxpwdlife': '60',
                    'krbminpwdlife': '24',
                    'krbpwdhistorylength': '8',
                    'krbpwdmindiffchars': '3',
                    'krbpwdminlength': '12',
                    'krbpwdmaxfailure': '8',
                    'krbpwdfailurecountinterval': '60',
                    'krbpwdlockoutduration': '600'
                }
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_mod_missing_args(self):
        """Policy exists, but some of the args aren't set, so need to be added"""
        module_args = {
            'group': 'sysops',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['sysops'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbpwdhistorylength': ['8'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'dn': 'cn=sysops,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            },
            {
                'method': 'pwpolicy_mod',
                'name': 'sysops',
                'item': {
                    'cospriority': '10',
                    'krbmaxpwdlife': '90',
                    'krbminpwdlife': '1',
                    'krbpwdhistorylength': '8',
                    'krbpwdmindiffchars': '3',
                    'krbpwdminlength': '16',
                    'krbpwdmaxfailure': '6',
                    'krbpwdfailurecountinterval': '60',
                    'krbpwdlockoutduration': '600'
                }
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_del(self):
        """Policy exists, and state is absent. Needs to be deleted"""
        module_args = {
            'group': 'sysops',
            'state': 'absent',
            # other arguments are ignored when state is `absent`
            'priority': '10',
            'maxpwdlife': '90',
            'historylength': '8',
            'minlength': '16',
            'maxfailcount': '6'
        }
        return_value = {
            'cn': ['sysops'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbpwdhistorylength': ['8'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'dn': 'cn=sysops,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            },
            {
                'method': 'pwpolicy_del',
                'name': 'sysops',
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_no_change(self):
        """Policy already exists. No changes needed"""
        module_args = {
            'group': 'admins',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['admins'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbminpwdlife': ['1'],
            'krbpwdhistorylength': ['8'],
            'krbpwdmindiffchars': ['3'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'krbpwdfailurecountinterval': ['60'],
            'krbpwdlockoutduration': ['600'],
            'dn': 'cn=admins,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'admins'
                }
            }
        ]
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_del_no_change(self):
        """Policy doesn't exist, and state is absent. No change needed"""
        module_args = {
            'group': 'sysops',
            'state': 'absent',
            # other arguments are ignored when state is `absent`
            'priority': '10',
            'maxpwdlife': '90',
            'historylength': '8',
            'minlength': '16',
            'maxfailcount': '6'
        }
        return_value = {}
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            }
        ]
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_global(self):
        """Modify the global policy"""
        module_args = {
            'maxpwdlife': '60',
            'minpwdlife': '24',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '12',
            'maxfailcount': '8',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['global_policy'],
            'krbmaxpwdlife': ['90'],
            'krbminpwdlife': ['1'],
            'krbpwdmindiffchars': ['3'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'krbpwdfailurecountinterval': ['60'],
            'krbpwdlockoutduration': ['600'],
            'dn': 'cn=global_policy,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = (
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'global_policy'
                }
            },
            {
                'method': 'pwpolicy_mod',
                'name': None,
                'item': {
                    'krbmaxpwdlife': '60',
                    'krbminpwdlife': '24',
                    'krbpwdhistorylength': '8',
                    'krbpwdmindiffchars': '3',
                    'krbpwdminlength': '12',
                    'krbpwdmaxfailure': '8',
                    'krbpwdfailurecountinterval': '60',
                    'krbpwdlockoutduration': '600'
                }
            }
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_global_no_change(self):
        """Global policy already matches the given arguments. No change needed"""
        module_args = {
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['global_policy'],
            'krbmaxpwdlife': ['90'],
            'krbminpwdlife': ['1'],
            'krbpwdhistorylength': ['8'],
            'krbpwdmindiffchars': ['3'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'krbpwdfailurecountinterval': ['60'],
            'krbpwdlockoutduration': ['600'],
            'dn': 'cn=global_policy,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'global_policy'
                }
            }
        ]
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_check_add(self):
        """Add a new policy in check mode. pwpolicy_add shouldn't be called"""
        module_args = {
            '_ansible_check_mode': True,
            'group': 'admins',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '90',
            'minpwdlife': '1',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '16',
            'maxfailcount': '6',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {}
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'admins'
                }
            }
        ]
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_check_mod(self):
        """Modify a policy in check mode. pwpolicy_mod shouldn't be called"""
        module_args = {
            '_ansible_check_mode': True,
            'group': 'sysops',
            'state': 'present',
            'priority': '10',
            'maxpwdlife': '60',
            'minpwdlife': '24',
            'historylength': '8',
            'minclasses': '3',
            'minlength': '12',
            'maxfailcount': '8',
            'failinterval': '60',
            'lockouttime': '600'
        }
        return_value = {
            'cn': ['sysops'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbminpwdlife': ['1'],
            'krbpwdhistorylength': ['8'],
            'krbpwdmindiffchars': ['3'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'krbpwdfailurecountinterval': ['60'],
            'krbpwdlockoutduration': ['600'],
            'dn': 'cn=sysops,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            }
        ]
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_check_del(self):
        """Delete a policy in check mode. pwpolicy_del shouldn't be called"""
        module_args = {
            '_ansible_check_mode': True,
            'group': 'sysops',
            'state': 'absent'
        }
        return_value = {
            'cn': ['sysops'],
            'cospriority': ['10'],
            'krbmaxpwdlife': ['90'],
            'krbpwdhistorylength': ['8'],
            'krbpwdminlength': ['16'],
            'krbpwdmaxfailure': ['6'],
            'dn': 'cn=sysops,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com',
            'objectclass': ['top', 'nscontainer', 'krbpwdpolicy']
        }
        mock_calls = [
            {
                'method': 'pwpolicy_find',
                'name': None,
                'item': {
                    'all': True,
                    'cn': 'sysops'
                }
            }
        ]
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_fail_post(self):
        """Fail due to an exception raised from _post_json"""
        set_module_args({
            'group': 'admins',
            'state': 'absent'
        })

        with patch_ipa(side_effect=Exception('ERROR MESSAGE')) as (mock_login, mock_post):
            with self.assertRaises(AnsibleFailJson) as exec_info:
                self.module.main()

        self.assertEqual(exec_info.exception.args[0]['msg'], 'ERROR MESSAGE')


if __name__ == '__main__':
    unittest.main()

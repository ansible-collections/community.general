# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_realm

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_realm_by_id, create_realm=None, update_realm=None, delete_realm=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_realm.KeycloakAPI
    with patch.object(obj, 'get_realm_by_id', side_effect=get_realm_by_id) as mock_get_realm_by_id:
        with patch.object(obj, 'create_realm', side_effect=create_realm) as mock_create_realm:
            with patch.object(obj, 'update_realm', side_effect=update_realm) as mock_update_realm:
                with patch.object(obj, 'delete_realm', side_effect=delete_realm) as mock_delete_realm:
                    yield mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm


def get_response(object_with_future_response, method, get_id_call_count):
    if callable(object_with_future_response):
        return object_with_future_response()
    if isinstance(object_with_future_response, dict):
        return get_response(
            object_with_future_response[method], method, get_id_call_count)
    if isinstance(object_with_future_response, list):
        call_number = next(get_id_call_count)
        return get_response(
            object_with_future_response[call_number], method, get_id_call_count)
    return object_with_future_response


def build_mocked_request(get_id_user_count, response_dict):
    def _mocked_requests(*args, **kwargs):
        url = args[0]
        method = kwargs['method']
        future_response = response_dict.get(url, None)
        return get_response(future_response, method, get_id_user_count)
    return _mocked_requests


def create_wrapper(text_as_string):
    """Allow to mock many times a call to one address.
    Without this function, the StringIO is empty for the second call.
    """
    def _create_wrapper():
        return StringIO(text_as_string)
    return _create_wrapper


def mock_good_connection():
    token_response = {
        'http://keycloak.url/auth/realms/master/protocol/openid-connect/token': create_wrapper('{"access_token": "alongtoken"}'), }
    return patch(
        'ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url',
        side_effect=build_mocked_request(count(), token_response),
        autospec=True
    )


class TestKeycloakRealm(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealm, self).setUp()
        self.module = keycloak_realm

    def test_create_when_absent(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True
        }
        return_value_absent = [None, {'id': 'realm-name', 'realm': 'realm-name', 'enabled': True}]
        return_value_created = [{
            'code': 201,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True
        }]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_by_id=return_value_absent, create_realm=return_value_created) \
                    as (mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_by_id.mock_calls), 2)
        self.assertEqual(len(mock_create_realm.mock_calls), 1)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present_with_change(self):
        """Update with change a realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': False
        }
        return_value_absent = [
            {
                'id': 'realm-name',
                'realm': 'realm-name',
                'enabled': True
            },
            {
                'id': 'realm-name',
                'realm': 'realm-name',
                'enabled': False
            }
        ]
        return_value_updated = [{
            'code': 201,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': False
        }]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_by_id=return_value_absent, update_realm=return_value_updated) \
                    as (mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_by_id.mock_calls), 2)
        self.assertEqual(len(mock_create_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present_no_change(self):
        """Update without change a realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True
        }
        return_value_absent = [
            {
                'id': 'realm-name',
                'realm': 'realm-name',
                'enabled': True
            },
            {
                'id': 'realm-name',
                'realm': 'realm-name',
                'enabled': True
            }
        ]
        return_value_updated = [{
            'code': 201,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True
        }]
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_by_id=return_value_absent, update_realm=return_value_updated) \
                    as (mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_by_id.mock_calls), 2)
        self.assertEqual(len(mock_create_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_absent(self):
        """Remove an absent realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True,
            'state': 'absent'
        }
        return_value_absent = [None]
        return_value_deleted = [None]
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_by_id=return_value_absent, delete_realm=return_value_deleted) \
                    as (mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_by_id.mock_calls), 1)
        self.assertEqual(len(mock_delete_realm.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_present(self):
        """Remove a present realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'id': 'realm-name',
            'realm': 'realm-name',
            'enabled': True,
            'state': 'absent'
        }
        return_value_absent = [
            {
                'id': 'realm-name',
                'realm': 'realm-name'
            }]
        return_value_deleted = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_by_id=return_value_absent, delete_realm=return_value_deleted) \
                    as (mock_get_realm_by_id, mock_create_realm, mock_update_realm, mock_delete_realm):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_by_id.mock_calls), 1)
        self.assertEqual(len(mock_delete_realm.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

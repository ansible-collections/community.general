# -*- coding: utf-8 -*-

# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules import keycloak_role

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_realm_role, create_realm_role=None, update_realm_role=None, delete_realm_role=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_role.KeycloakAPI
    with patch.object(obj, 'get_realm_role', side_effect=get_realm_role) as mock_get_realm_role:
        with patch.object(obj, 'create_realm_role', side_effect=create_realm_role) as mock_create_realm_role:
            with patch.object(obj, 'update_realm_role', side_effect=update_realm_role) as mock_update_realm_role:
                with patch.object(obj, 'delete_realm_role', side_effect=delete_realm_role) as mock_delete_realm_role:
                    yield mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role


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


class TestKeycloakRealmRole(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealmRole, self).setUp()
        self.module = keycloak_role

    def test_create_when_absent(self):
        """Add a new realm role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'name': 'role-name',
            'description': 'role-description',
        }
        return_value_absent = [
            None,
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            }
        ]
        return_value_created = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_role=return_value_absent, create_realm_role=return_value_created) \
                    as (mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_role.mock_calls), 2)
        self.assertEqual(len(mock_create_realm_role.mock_calls), 1)
        self.assertEqual(len(mock_update_realm_role.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present_with_change(self):
        """Update with change a realm role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'name': 'role-name',
            'description': 'new-role-description',
        }
        return_value_present = [
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            },
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "new-role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            }
        ]
        return_value_updated = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_role=return_value_present, update_realm_role=return_value_updated) \
                    as (mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_role.mock_calls), 2)
        self.assertEqual(len(mock_create_realm_role.mock_calls), 0)
        self.assertEqual(len(mock_update_realm_role.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present_no_change(self):
        """Update without change a realm role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'name': 'role-name',
            'description': 'role-description',
        }
        return_value_present = [
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            },
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            }
        ]
        return_value_updated = [None]
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_role=return_value_present, update_realm_role=return_value_updated) \
                    as (mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_role.mock_calls), 1)
        self.assertEqual(len(mock_create_realm_role.mock_calls), 0)
        self.assertEqual(len(mock_update_realm_role.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_absent(self):
        """Remove an absent realm role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'name': 'role-name',
            'state': 'absent'
        }
        return_value_absent = [None]
        return_value_deleted = [None]
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_role=return_value_absent, delete_realm_role=return_value_deleted) \
                    as (mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_role.mock_calls), 1)
        self.assertEqual(len(mock_delete_realm_role.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_present(self):
        """Remove a present realm role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'name': 'role-name',
            'state': 'absent'
        }
        return_value_absent = [
            {
                "attributes": {},
                "clientRole": False,
                "composite": False,
                "containerId": "realm-name",
                "description": "role-description",
                "id": "90f1cdb6-be88-496e-89c6-da1fb6bc6966",
                "name": "role-name",
            }
        ]
        return_value_deleted = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_role=return_value_absent, delete_realm_role=return_value_deleted) \
                    as (mock_get_realm_role, mock_create_realm_role, mock_update_realm_role, mock_delete_realm_role):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_role.mock_calls), 1)
        self.assertEqual(len(mock_delete_realm_role.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

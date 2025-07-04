# -*- coding: utf-8 -*-

# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules import keycloak_authentication

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_authentication_flow_by_alias=None, copy_auth_flow=None, create_empty_auth_flow=None,
                       get_executions_representation=None, delete_authentication_flow_by_id=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_authentication.KeycloakAPI
    with patch.object(obj, 'get_authentication_flow_by_alias', side_effect=get_authentication_flow_by_alias) \
            as mock_get_authentication_flow_by_alias:
        with patch.object(obj, 'copy_auth_flow', side_effect=copy_auth_flow) \
                as mock_copy_auth_flow:
            with patch.object(obj, 'create_empty_auth_flow', side_effect=create_empty_auth_flow) \
                    as mock_create_empty_auth_flow:
                with patch.object(obj, 'get_executions_representation', return_value=get_executions_representation) \
                        as mock_get_executions_representation:
                    with patch.object(obj, 'delete_authentication_flow_by_id', side_effect=delete_authentication_flow_by_id) \
                            as mock_delete_authentication_flow_by_id:
                        yield mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow, \
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id


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


class TestKeycloakAuthentication(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakAuthentication, self).setUp()
        self.module = keycloak_authentication

    def test_create_auth_flow_from_copy(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'copyFrom': 'first broker login',
            'authenticationExecutions': [
                {
                    'providerId': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                },
            ],
            'state': 'present',
        }
        return_value_auth_flow_before = [{}]
        return_value_copied = [{
            'id': '2ac059fc-c548-414f-9c9e-84d42bd4944e',
            'alias': 'first broker login',
            'description': 'browser based authentication',
            'providerId': 'basic-flow',
            'topLevel': True,
            'builtIn': False,
            'authenticationExecutions': [
                {
                    'authenticator': 'auth-cookie',
                    'requirement': 'ALTERNATIVE',
                    'priority': 10,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
            ],
        }]
        return_value_executions_after = [
            {
                'id': 'b678e30c-8469-40a7-8c21-8d0cda76a591',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Identity Provider Redirector',
                'requirementChoices': ['REQUIRED', 'DISABLED'],
                'configurable': True,
                'providerId': 'identity-provider-redirector',
                'level': 0,
                'index': 0
            },
            {
                'id': 'fdc208e9-c292-48b7-b7d1-1d98315ee893',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Cookie',
                'requirementChoices': [
                    'REQUIRED',
                    'ALTERNATIVE',
                    'DISABLED'
                ],
                'configurable': False,
                'providerId': 'auth-cookie',
                'level': 0,
                'index': 1
            },
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before, copy_auth_flow=return_value_copied,
                                        get_executions_representation=return_value_executions_after) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 1)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 2)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_auth_flow_from_copy_idempotency(self):
        """Add an already existing authentication flow from copy of an other flow to test idempotency"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'copyFrom': 'first broker login',
            'authenticationExecutions': [
                {
                    'providerId': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                },
            ],
            'state': 'present',
        }
        return_value_auth_flow_before = [{
            'id': '71275d5e-e11f-4be4-b119-0abfa87987a4',
            'alias': 'Test create authentication flow copy',
            'description': '',
            'providerId': 'basic-flow',
            'topLevel': True,
            'builtIn': False,
            'authenticationExecutions': [
                {
                    'authenticator': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                    'priority': 0,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
                {
                    'authenticator': 'auth-cookie',
                    'requirement': 'ALTERNATIVE',
                    'priority': 0,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
            ],
        }]
        return_value_executions_after = [
            {
                'id': 'b678e30c-8469-40a7-8c21-8d0cda76a591',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Identity Provider Redirector',
                'requirementChoices': ['REQUIRED', 'DISABLED'],
                'configurable': True,
                'providerId': 'identity-provider-redirector',
                'level': 0,
                'index': 0
            },
            {
                'id': 'fdc208e9-c292-48b7-b7d1-1d98315ee893',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Cookie',
                'requirementChoices': [
                    'REQUIRED',
                    'ALTERNATIVE',
                    'DISABLED'
                ],
                'configurable': False,
                'providerId': 'auth-cookie',
                'level': 0,
                'index': 1
            },
        ]
        changed = False

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before,
                                        get_executions_representation=return_value_executions_after) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 2)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_auth_flow_without_copy(self):
        """Add authentication without copy"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'authenticationExecutions': [
                {
                    'providerId': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                    'authenticationConfig': {
                        'alias': 'name',
                        'config': {
                            'defaultProvider': 'value'
                        },
                    },
                },
            ],
            'state': 'present',
        }
        return_value_auth_flow_before = [{}]
        return_value_created_empty_flow = [
            {
                "alias": "Test of the keycloak_auth module",
                "authenticationExecutions": [],
                "builtIn": False,
                "description": "",
                "id": "513f5baa-cc42-47bf-b4b6-1d23ccc0a67f",
                "providerId": "basic-flow",
                "topLevel": True
            },
        ]
        return_value_executions_after = [
            {
                'id': 'b678e30c-8469-40a7-8c21-8d0cda76a591',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Identity Provider Redirector',
                'requirementChoices': ['REQUIRED', 'DISABLED'],
                'configurable': True,
                'providerId': 'identity-provider-redirector',
                'level': 0,
                'index': 0
            },
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before,
                                        get_executions_representation=return_value_executions_after, create_empty_auth_flow=return_value_created_empty_flow) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 1)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 3)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_auth_flow_adding_exec(self):
        """Update authentication flow by adding execution"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'authenticationExecutions': [
                {
                    'providerId': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                    'authenticationConfig': {
                        'alias': 'name',
                        'config': {
                            'defaultProvider': 'value'
                        },
                    },
                },
            ],
            'state': 'present',
        }
        return_value_auth_flow_before = [{
            'id': '71275d5e-e11f-4be4-b119-0abfa87987a4',
            'alias': 'Test create authentication flow copy',
            'description': '',
            'providerId': 'basic-flow',
            'topLevel': True,
            'builtIn': False,
            'authenticationExecutions': [
                {
                    'authenticator': 'auth-cookie',
                    'requirement': 'ALTERNATIVE',
                    'priority': 0,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
            ],
        }]
        return_value_executions_after = [
            {
                'id': 'b678e30c-8469-40a7-8c21-8d0cda76a591',
                'requirement': 'DISABLED',
                'displayName': 'Identity Provider Redirector',
                'requirementChoices': ['REQUIRED', 'DISABLED'],
                'configurable': True,
                'providerId': 'identity-provider-redirector',
                'level': 0,
                'index': 0
            },
            {
                'id': 'fdc208e9-c292-48b7-b7d1-1d98315ee893',
                'requirement': 'ALTERNATIVE',
                'displayName': 'Cookie',
                'requirementChoices': [
                    'REQUIRED',
                    'ALTERNATIVE',
                    'DISABLED'
                ],
                'configurable': False,
                'providerId': 'auth-cookie',
                'level': 0,
                'index': 1
            },
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before,
                                        get_executions_representation=return_value_executions_after) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 3)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_auth_flow(self):
        """Delete authentication flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'state': 'absent',
        }
        return_value_auth_flow_before = [{
            'id': '71275d5e-e11f-4be4-b119-0abfa87987a4',
            'alias': 'Test create authentication flow copy',
            'description': '',
            'providerId': 'basic-flow',
            'topLevel': True,
            'builtIn': False,
            'authenticationExecutions': [
                {
                    'authenticator': 'auth-cookie',
                    'requirement': 'ALTERNATIVE',
                    'priority': 0,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
            ],
        }]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_auth_flow_idempotency(self):
        """Delete second time authentication flow to test idempotency"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'state': 'absent',
        }
        return_value_auth_flow_before = [{}]
        changed = False

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_force_update_auth_flow(self):
        """Delete authentication flow and create new one"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'alias': 'Test create authentication flow copy',
            'authenticationExecutions': [
                {
                    'providerId': 'identity-provider-redirector',
                    'requirement': 'ALTERNATIVE',
                    'authenticationConfig': {
                        'alias': 'name',
                        'config': {
                            'defaultProvider': 'value'
                        },
                    },
                },
            ],
            'state': 'present',
            'force': 'yes',
        }
        return_value_auth_flow_before = [{
            'id': '71275d5e-e11f-4be4-b119-0abfa87987a4',
            'alias': 'Test create authentication flow copy',
            'description': '',
            'providerId': 'basic-flow',
            'topLevel': True,
            'builtIn': False,
            'authenticationExecutions': [
                {
                    'authenticator': 'auth-cookie',
                    'requirement': 'ALTERNATIVE',
                    'priority': 0,
                    'userSetupAllowed': False,
                    'autheticatorFlow': False
                },
            ],
        }]
        return_value_created_empty_flow = [
            {
                "alias": "Test of the keycloak_auth module",
                "authenticationExecutions": [],
                "builtIn": False,
                "description": "",
                "id": "513f5baa-cc42-47bf-b4b6-1d23ccc0a67f",
                "providerId": "basic-flow",
                "topLevel": True
            },
        ]
        return_value_executions_after = [
            {
                'id': 'b678e30c-8469-40a7-8c21-8d0cda76a591',
                'requirement': 'DISABLED',
                'displayName': 'Identity Provider Redirector',
                'requirementChoices': ['REQUIRED', 'DISABLED'],
                'configurable': True,
                'providerId': 'identity-provider-redirector',
                'level': 0,
                'index': 0
            },
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_authentication_flow_by_alias=return_value_auth_flow_before,
                                        get_executions_representation=return_value_executions_after, create_empty_auth_flow=return_value_created_empty_flow) \
                        as (mock_get_authentication_flow_by_alias, mock_copy_auth_flow, mock_create_empty_auth_flow,
                            mock_get_executions_representation, mock_delete_authentication_flow_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_copy_auth_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_empty_auth_flow.mock_calls), 1)
        self.assertEqual(len(mock_get_executions_representation.mock_calls), 3)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

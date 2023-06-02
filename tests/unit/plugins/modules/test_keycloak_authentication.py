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

from ansible_collections.community.general.plugins.modules import keycloak_authentication

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(
    get_authentication_flow_by_alias=None,
    get_authentication_executions=None,
    update_authentication_flow=None,
    copy_authentication_flow=None,
    create_authentication_flow=None,
    get_realm_info_by_id=None,
    update_realm=None,
    update_authentication_execution=None,
    change_execution_priority=None,
    create_authentication_execution_subflow=None,
    create_authentication_execution_step=None,
    get_authenticator_config=None,
    update_authenticator_config=None,
    create_authenticator_config=None,
    get_required_action=None,
    update_required_action=None,
    register_required_action=None,
    delete_authentication_flow_by_id=None,
    delete_required_action=None,
):
    """
    Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_authentication.KeycloakAPI
    with patch.object(
        obj,
        'get_authentication_flow_by_alias',
        side_effect=get_authentication_flow_by_alias
    ) as mock_get_authentication_flow_by_alias:
        with patch.object(
            obj,
            'get_authentication_executions',
            side_effect=get_authentication_executions
        ) as mock_get_authentication_executions:
            with patch.object(
                obj,
                'update_authentication_flow',
                side_effect=update_authentication_flow
            ) as mock_update_authentication_flow:
                with patch.object(
                    obj,
                    'copy_authentication_flow',
                    side_effect=copy_authentication_flow
                ) as mock_copy_authentication_flow:
                    with patch.object(
                        obj,
                        'create_authentication_flow',
                        side_effect=create_authentication_flow
                    ) as mock_create_authentication_flow:
                        with patch.object(
                            obj,
                            'get_realm_info_by_id',
                            side_effect=get_realm_info_by_id
                        ) as mock_get_realm_info_by_id:
                            with patch.object(
                                obj,
                                'update_realm',
                                side_effect=update_realm
                            ) as mock_update_realm:
                                with patch.object(
                                    obj,
                                    'update_authentication_execution',
                                    side_effect=update_authentication_execution
                                ) as mock_update_authentication_execution:
                                    with patch.object(
                                        obj,
                                        'change_execution_priority',
                                        side_effect=change_execution_priority
                                    ) as mock_change_execution_priority:
                                        with patch.object(
                                            obj,
                                            'create_authentication_execution_subflow',
                                            side_effect=create_authentication_execution_subflow
                                        ) as mock_create_authentication_execution_subflow:
                                            with patch.object(
                                                obj,
                                                'create_authentication_execution_step',
                                                side_effect=create_authentication_execution_step
                                            ) as mock_create_authentication_execution_step:
                                                with patch.object(
                                                    obj,
                                                    'get_authenticator_config',
                                                    side_effect=get_authenticator_config
                                                ) as mock_get_authenticator_config:
                                                    with patch.object(
                                                        obj,
                                                        'update_authenticator_config',
                                                        side_effect=update_authenticator_config
                                                    ) as mock_update_authenticator_config:
                                                        with patch.object(
                                                            obj,
                                                            'create_authenticator_config',
                                                            side_effect=create_authenticator_config
                                                        ) as mock_create_authenticator_config:
                                                            with patch.object(
                                                                obj,
                                                                'get_required_action',
                                                                side_effect=get_required_action
                                                            ) as mock_get_required_action:
                                                                with patch.object(
                                                                    obj,
                                                                    'update_required_action',
                                                                    side_effect=update_required_action
                                                                ) as mock_update_required_action:
                                                                    with patch.object(
                                                                        obj,
                                                                        'register_required_action',
                                                                        side_effect=register_required_action
                                                                    ) as mock_register_required_action:
                                                                        with patch.object(
                                                                            obj,
                                                                            'delete_authentication_flow_by_id',
                                                                            side_effect=delete_authentication_flow_by_id
                                                                        ) as mock_delete_authentication_flow_by_id:
                                                                            with patch.object(
                                                                                obj,
                                                                                'delete_required_action',
                                                                                side_effect=delete_required_action
                                                                            ) as mock_delete_required_action:
                                                                                yield (
                                                                                    mock_get_authentication_flow_by_alias,
                                                                                    mock_get_authentication_executions,
                                                                                    mock_update_authentication_flow,
                                                                                    mock_copy_authentication_flow,
                                                                                    mock_create_authentication_flow,
                                                                                    mock_get_realm_info_by_id,
                                                                                    mock_update_realm,
                                                                                    mock_update_authentication_execution,
                                                                                    mock_change_execution_priority,
                                                                                    mock_create_authentication_execution_subflow,
                                                                                    mock_create_authentication_execution_step,
                                                                                    mock_get_authenticator_config,
                                                                                    mock_update_authenticator_config,
                                                                                    mock_create_authenticator_config,
                                                                                    mock_get_required_action,
                                                                                    mock_update_required_action,
                                                                                    mock_register_required_action,
                                                                                    mock_delete_authentication_flow_by_id,
                                                                                    mock_delete_required_action,
                                                                                )


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

    def test_create_authentication_flow(self):
        """Add a new authentication flow."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "bind_flow": "clientAuthenticationFlow",
            "execution": {
                "authenticationFlow": False,
                "displayName": "Reset Password",
                "providerId": "reset-password",
                "requirement": "REQUIRED",
            },
            "flow": {
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
            },
            "realm": "master",
            "state": "present",
        }

        return_value_authentication_flow = [
            {},
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [],
            },
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [
                    {
                        "authenticator": "reset-password",
                        "requirement": "REQUIRED",
                        "priority": 0,
                        "authenticatorFlow": False,
                        "userSetupAllowed": False,
                    },
                ],
            },
        ]

        return_value_authentication_execution = [
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "DISABLED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
            ],
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
            ],
        ]

        # Truncated realm info
        return_value_realm_info = [
            {
                "clientAuthenticationFlow": ""
            },
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_authentication_flow_by_alias=return_value_authentication_flow,
                get_authentication_executions=return_value_authentication_execution,
                get_realm_info_by_id=return_value_realm_info,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 2)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 2)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 1)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 1)
        self.assertEqual(len(mock_update_realm.mock_calls), 1)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 1)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 1)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 0)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_authentication_flow_idempotency(self):
        """Add a new authentication flow, even though it already exists."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "bind_flow": "clientAuthenticationFlow",
            "execution": {
                "authenticationFlow": False,
                "displayName": "Reset Password",
                "providerId": "reset-password",
                "requirement": "REQUIRED",
            },
            "flow": {
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
            },
            "realm": "master",
            "state": "present",
        }

        return_value_authentication_flow = [
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [],
            },
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [
                    {
                        "authenticator": "reset-password",
                        "requirement": "REQUIRED",
                        "priority": 0,
                        "authenticatorFlow": False,
                        "userSetupAllowed": False,
                    },
                ],
            },
        ]

        return_value_authentication_execution = [
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
            ],
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
            ],
        ]

        # Truncated realm info
        return_value_realm_info = [
            {
                "clientAuthenticationFlow": "Test create authentication flow"
            },
        ]

        changed = False

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_authentication_flow_by_alias=return_value_authentication_flow,
                get_authentication_executions=return_value_authentication_execution,
                get_realm_info_by_id=return_value_realm_info,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 2)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 1)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 0)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_authentication_flow_add_execution_subflow(self):
        """Update an existing authentication flow by adding a new authentication execution sub-flow."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "execution": {
                "authenticationFlow": True,
                "displayName": "Browser - Conditional OTP",
                "providerId": "registration-page-form",
                "requirement": "REQUIRED",
            },
            "flow": {
                "alias": "Test create authentication flow",
            },
            "realm": "master",
            "state": "present",
        }

        return_value_authentication_flow = [
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [
                    {
                        "authenticator": "reset-password",
                        "requirement": "REQUIRED",
                        "priority": 0,
                        "authenticatorFlow": False,
                        "userSetupAllowed": False,
                    },
                ],
            },
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [
                    {
                        "authenticator": "reset-password",
                        "requirement": "REQUIRED",
                        "priority": 0,
                        "authenticatorFlow": False,
                        "userSetupAllowed": False,
                    },
                    {
                        "authenticatorFlow": True,
                        "requirement": "ALTERNATIVE",
                        "priority": 1,
                        "autheticatorFlow": True,
                        "flowAlias": "Browser - Conditional OTP",
                        "userSetupAllowed": False,
                    }
                ],
            },
        ]

        return_value_authentication_execution = [
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
            ],
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
                {
                    "id": "d0c3d9fa-92c7-4b90-a1c1-515ccea9a0ee",
                    "requirement": "DISABLED",
                    "displayName": "Browser - Conditional OTP",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                        "CONDITIONAL",
                    ],
                    "configurable": False,
                    "authenticationFlow": True,
                    "flowId": "9491b181-450a-4753-b563-5900eb9d957b",
                    "level": 1,
                    "index": 1,
                },
            ],
            [
                {
                    "id": "91113e19-2808-42c5-9749-d9c16e4b8c5e",
                    "requirement": "REQUIRED",
                    "displayName": "Reset Password",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                    ],
                    "configurable": False,
                    "providerId": "reset-password",
                    "level": 0,
                    "index": 0,
                },
                {
                    "id": "d0c3d9fa-92c7-4b90-a1c1-515ccea9a0ee",
                    "requirement": "REQUIRED",
                    "displayName": "Browser - Conditional OTP",
                    "requirementChoices": [
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                        "CONDITIONAL",
                    ],
                    "configurable": False,
                    "authenticationFlow": True,
                    "flowId": "9491b181-450a-4753-b563-5900eb9d957b",
                    "level": 0,
                    "index": 1,
                },
            ],
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_authentication_flow_by_alias=return_value_authentication_flow,
                get_authentication_executions=return_value_authentication_execution,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 3)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 1)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 1)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 0)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_authentication_flow(self):
        """Delete an existing authentication flow."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "flow": {
                "alias": "Test create authentication flow",
            },
            "realm": "master",
            "state": "absent",
        }

        return_value_authentication_flow = [
            {
                "id": "b0c64a16-acf6-4600-9dfc-db37a4801d9d",
                "alias": "Test create authentication flow",
                "description": "This is a test authentication flow.",
                "providerId": "basic-flow",
                "topLevel": True,
                "builtIn": False,
                "authenticationExecutions": [
                    {
                        "authenticator": "reset-password",
                        "requirement": "REQUIRED",
                        "priority": 0,
                        "authenticatorFlow": False,
                        "userSetupAllowed": False,
                    },
                ],
            },
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_authentication_flow_by_alias=return_value_authentication_flow,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 0)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 1)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_authentication_flow_idempotency(self):
        """Delete a non-existing authentication flow."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "flow": {
                "alias": "Test create authentication flow",
            },
            "realm": "master",
            "state": "absent",
        }

        return_value_authentication_flow = [
            {},
        ]

        changed = False

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_authentication_flow_by_alias=return_value_authentication_flow,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 1)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 0)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_register_required_action(self):
        """Register a new required action."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
            },
            "realm": "master",
            "state": "present",
        }

        return_value_required_action = [
            {},
            {
                "alias": "TEST_REQUIRED_ACTION",
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "defaultAction": False,
                "priority": 0,
                "config": {},
            },
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 2)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 1)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_register_required_action_idempotency(self):
        """Register a new required action, even though it already is registered."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
            },
            "realm": "master",
            "state": "present",
        }

        return_value_required_action = [
            {
                "alias": "TEST_REQUIRED_ACTION",
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "defaultAction": False,
                "priority": 0,
                "config": {},
            },
        ]

        changed = False

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_required_action(self):
        """Updated a registered required action."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
                "enabled": False,
            },
            "realm": "master",
            "state": "present",
        }

        return_value_required_action = [
            {
                "alias": "TEST_REQUIRED_ACTION",
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "defaultAction": False,
                "priority": 0,
                "config": {},
            },
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 1)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_required_action_idempotency(self):
        """Updated a registered required action, even though nothing is going to be updated."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
                "enabled": True,
            },
            "realm": "master",
            "state": "present",
        }

        return_value_required_action = [
            {
                "alias": "TEST_REQUIRED_ACTION",
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "defaultAction": False,
                "priority": 0,
                "config": {},
            },
        ]

        changed = False

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_required_action(self):
        """Delete a registered required action."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
            },
            "realm": "master",
            "state": "absent",
        }

        return_value_required_action = [
            {
                "alias": "TEST_REQUIRED_ACTION",
                "name": "Test required action",
                "providerId": "TEST_REQUIRED_ACTION",
                "enabled": True,
                "defaultAction": False,
                "priority": 0,
                "config": {},
            },
        ]

        changed = True

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_required_action_idempotency(self):
        """Delete a not registered required action."""

        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "required_action": {
                "alias": "TEST_REQUIRED_ACTION",
            },
            "realm": "master",
            "state": "absent",
        }

        return_value_required_action = [
            {},
        ]

        changed = False

        set_module_args(module_args)

        # Run the module
        with mock_good_connection():
            with patch_keycloak_api(
                get_required_action=return_value_required_action,
            ) as (
                mock_get_authentication_flow_by_alias,
                mock_get_authentication_executions,
                mock_update_authentication_flow,
                mock_copy_authentication_flow,
                mock_create_authentication_flow,
                mock_get_realm_info_by_id,
                mock_update_realm,
                mock_update_authentication_execution,
                mock_change_execution_priority,
                mock_create_authentication_execution_subflow,
                mock_create_authentication_execution_step,
                mock_get_authenticator_config,
                mock_update_authenticator_config,
                mock_create_authenticator_config,
                mock_get_required_action,
                mock_update_required_action,
                mock_register_required_action,
                mock_delete_authentication_flow_by_id,
                mock_delete_required_action,
            ):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_authentication_flow_by_alias.mock_calls), 0)
        self.assertEqual(len(mock_get_authentication_executions.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_copy_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_flow.mock_calls), 0)
        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 0)
        self.assertEqual(len(mock_update_realm.mock_calls), 0)
        self.assertEqual(len(mock_update_authentication_execution.mock_calls), 0)
        self.assertEqual(len(mock_change_execution_priority.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_subflow.mock_calls), 0)
        self.assertEqual(len(mock_create_authentication_execution_step.mock_calls), 0)
        self.assertEqual(len(mock_get_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_update_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_create_authenticator_config.mock_calls), 0)
        self.assertEqual(len(mock_get_required_action.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_authentication_flow_by_id.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

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

from ansible_collections.community.general.plugins.modules import keycloak_authentication_required_actions

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(
    get_required_actions=None,
    register_required_action=None,
    update_required_action=None,
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

    obj = keycloak_authentication_required_actions.KeycloakAPI
    with patch.object(
        obj,
        'get_required_actions',
        side_effect=get_required_actions
    ) as mock_get_required_actions:
        with patch.object(
            obj,
            'register_required_action',
            side_effect=register_required_action
        ) as mock_register_required_action:
            with patch.object(
                obj,
                'update_required_action',
                side_effect=update_required_action
            ) as mock_update_required_action:
                with patch.object(
                    obj,
                    'delete_required_action',
                    side_effect=delete_required_action
                ) as mock_delete_required_action:
                    yield (
                        mock_get_required_actions,
                        mock_register_required_action,
                        mock_update_required_action,
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
        self.module = keycloak_authentication_required_actions

    def test_register_required_action(self):
        """Register a new authentication required action."""

        module_args = {
            'auth_client_id': 'admin-cli',
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'realm': 'master',
            'required_actions': [
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID (DUPLICATE ALIAS)',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID (DIFFERENT PROVIDER ID)',
                    'providerId': 'test-provider-id-diff',
                },
            ],
            'state': 'present',
        }

        return_value_required_actions = [
            [
                {
                    'alias': 'CONFIGURE_TOTP',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Configure OTP',
                    'priority': 10,
                    'providerId': 'CONFIGURE_TOTP'
                },
                {
                    'alias': 'TERMS_AND_CONDITIONS',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Terms and conditions',
                    'priority': 20,
                    'providerId': 'TERMS_AND_CONDITIONS'
                },
                {
                    'alias': 'UPDATE_PASSWORD',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Password',
                    'priority': 30,
                    'providerId': 'UPDATE_PASSWORD'
                },
                {
                    'alias': 'UPDATE_PROFILE',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Profile',
                    'priority': 40,
                    'providerId': 'UPDATE_PROFILE'
                },
                {
                    'alias': 'VERIFY_EMAIL',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Verify Email',
                    'priority': 50,
                    'providerId': 'VERIFY_EMAIL'
                },
                {
                    'alias': 'delete_account',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Delete Account',
                    'priority': 60,
                    'providerId': 'delete_account'
                },
                {
                    'alias': 'webauthn-register',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register',
                    'priority': 70,
                    'providerId': 'webauthn-register'
                },
                {
                    'alias': 'webauthn-register-passwordless',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register Passwordless',
                    'priority': 80,
                    'providerId': 'webauthn-register-passwordless'
                },
                {
                    'alias': 'update_user_locale',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update User Locale',
                    'priority': 1000,
                    'providerId': 'update_user_locale'
                }
            ],
        ]

        changed = True

        # Run the module
        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_required_actions=return_value_required_actions,
                ) as (
                    mock_get_required_actions,
                    mock_register_required_action,
                    mock_update_required_action,
                    mock_delete_required_action,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_required_actions.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 1)
        self.assertEqual(len(mock_register_required_action.mock_calls), 1)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_register_required_action_idempotency(self):
        """Register an already existing new authentication required action again."""

        module_args = {
            'auth_client_id': 'admin-cli',
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'realm': 'master',
            'required_actions': [
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID (DUPLICATE ALIAS)',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID (DIFFERENT PROVIDER ID)',
                    'providerId': 'test-provider-id-diff',
                },
            ],
            'state': 'present',
        }

        return_value_required_actions = [
            [
                {
                    'alias': 'CONFIGURE_TOTP',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Configure OTP',
                    'priority': 10,
                    'providerId': 'CONFIGURE_TOTP'
                },
                {
                    'alias': 'TERMS_AND_CONDITIONS',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Terms and conditions',
                    'priority': 20,
                    'providerId': 'TERMS_AND_CONDITIONS'
                },
                {
                    'alias': 'UPDATE_PASSWORD',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Password',
                    'priority': 30,
                    'providerId': 'UPDATE_PASSWORD'
                },
                {
                    'alias': 'UPDATE_PROFILE',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Profile',
                    'priority': 40,
                    'providerId': 'UPDATE_PROFILE'
                },
                {
                    'alias': 'VERIFY_EMAIL',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Verify Email',
                    'priority': 50,
                    'providerId': 'VERIFY_EMAIL'
                },
                {
                    'alias': 'delete_account',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Delete Account',
                    'priority': 60,
                    'providerId': 'delete_account'
                },
                {
                    'alias': 'webauthn-register',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register',
                    'priority': 70,
                    'providerId': 'webauthn-register'
                },
                {
                    'alias': 'webauthn-register-passwordless',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register Passwordless',
                    'priority': 80,
                    'providerId': 'webauthn-register-passwordless'
                },
                {
                    'alias': 'test-provider-id',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Test provider ID',
                    'priority': 90,
                    'providerId': 'test-provider-id'
                },
                {
                    'alias': 'update_user_locale',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update User Locale',
                    'priority': 1000,
                    'providerId': 'update_user_locale'
                }
            ],
        ]

        changed = False

        # Run the module
        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_required_actions=return_value_required_actions,
                ) as (
                    mock_get_required_actions,
                    mock_register_required_action,
                    mock_update_required_action,
                    mock_delete_required_action,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_required_actions.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_required_actions(self):
        """Update an authentication required action."""

        module_args = {
            'auth_client_id': 'admin-cli',
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'realm': 'master',
            'required_actions': [
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID UPDATED',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID UPDATED (DUPLICATE ALIAS)',
                    'providerId': 'test-provider-id',
                },
                {
                    'alias': 'test-provider-id',
                    'name': 'Test provider ID UPDATED (DIFFERENT PROVIDER ID)',
                    'providerId': 'test-provider-id-diff',
                },
            ],
            'state': 'present',
        }

        return_value_required_actions = [
            [
                {
                    'alias': 'CONFIGURE_TOTP',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Configure OTP',
                    'priority': 10,
                    'providerId': 'CONFIGURE_TOTP'
                },
                {
                    'alias': 'TERMS_AND_CONDITIONS',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Terms and conditions',
                    'priority': 20,
                    'providerId': 'TERMS_AND_CONDITIONS'
                },
                {
                    'alias': 'UPDATE_PASSWORD',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Password',
                    'priority': 30,
                    'providerId': 'UPDATE_PASSWORD'
                },
                {
                    'alias': 'UPDATE_PROFILE',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Profile',
                    'priority': 40,
                    'providerId': 'UPDATE_PROFILE'
                },
                {
                    'alias': 'VERIFY_EMAIL',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Verify Email',
                    'priority': 50,
                    'providerId': 'VERIFY_EMAIL'
                },
                {
                    'alias': 'delete_account',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Delete Account',
                    'priority': 60,
                    'providerId': 'delete_account'
                },
                {
                    'alias': 'webauthn-register',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register',
                    'priority': 70,
                    'providerId': 'webauthn-register'
                },
                {
                    'alias': 'webauthn-register-passwordless',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register Passwordless',
                    'priority': 80,
                    'providerId': 'webauthn-register-passwordless'
                },
                {
                    'alias': 'test-provider-id',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Test provider ID',
                    'priority': 90,
                    'providerId': 'test-provider-id'
                },
                {
                    'alias': 'update_user_locale',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update User Locale',
                    'priority': 1000,
                    'providerId': 'update_user_locale'
                }
            ],
        ]

        changed = True

        # Run the module
        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_required_actions=return_value_required_actions,
                ) as (
                    mock_get_required_actions,
                    mock_register_required_action,
                    mock_update_required_action,
                    mock_delete_required_action,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_required_actions.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 1)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_required_action(self):
        """Delete a registered authentication required action."""

        module_args = {
            'auth_client_id': 'admin-cli',
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'realm': 'master',
            'required_actions': [
                {
                    'alias': 'test-provider-id',
                },
            ],
            'state': 'absent',
        }

        return_value_required_actions = [
            [
                {
                    'alias': 'CONFIGURE_TOTP',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Configure OTP',
                    'priority': 10,
                    'providerId': 'CONFIGURE_TOTP'
                },
                {
                    'alias': 'TERMS_AND_CONDITIONS',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Terms and conditions',
                    'priority': 20,
                    'providerId': 'TERMS_AND_CONDITIONS'
                },
                {
                    'alias': 'UPDATE_PASSWORD',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Password',
                    'priority': 30,
                    'providerId': 'UPDATE_PASSWORD'
                },
                {
                    'alias': 'UPDATE_PROFILE',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Profile',
                    'priority': 40,
                    'providerId': 'UPDATE_PROFILE'
                },
                {
                    'alias': 'VERIFY_EMAIL',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Verify Email',
                    'priority': 50,
                    'providerId': 'VERIFY_EMAIL'
                },
                {
                    'alias': 'delete_account',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Delete Account',
                    'priority': 60,
                    'providerId': 'delete_account'
                },
                {
                    'alias': 'webauthn-register',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register',
                    'priority': 70,
                    'providerId': 'webauthn-register'
                },
                {
                    'alias': 'webauthn-register-passwordless',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register Passwordless',
                    'priority': 80,
                    'providerId': 'webauthn-register-passwordless'
                },
                {
                    'alias': 'test-provider-id',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Test provider ID',
                    'priority': 90,
                    'providerId': 'test-provider-id'
                },
                {
                    'alias': 'update_user_locale',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update User Locale',
                    'priority': 1000,
                    'providerId': 'update_user_locale'
                }
            ],
        ]

        changed = True

        # Run the module
        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_required_actions=return_value_required_actions,
                ) as (
                    mock_get_required_actions,
                    mock_register_required_action,
                    mock_update_required_action,
                    mock_delete_required_action,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_required_actions.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_required_action_idempotency(self):
        """Delete an already deleted authentication required action."""

        module_args = {
            'auth_client_id': 'admin-cli',
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'realm': 'master',
            'required_actions': [
                {
                    'alias': 'test-provider-id',
                },
            ],
            'state': 'absent',
        }

        return_value_required_actions = [
            [
                {
                    'alias': 'CONFIGURE_TOTP',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Configure OTP',
                    'priority': 10,
                    'providerId': 'CONFIGURE_TOTP'
                },
                {
                    'alias': 'TERMS_AND_CONDITIONS',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Terms and conditions',
                    'priority': 20,
                    'providerId': 'TERMS_AND_CONDITIONS'
                },
                {
                    'alias': 'UPDATE_PASSWORD',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Password',
                    'priority': 30,
                    'providerId': 'UPDATE_PASSWORD'
                },
                {
                    'alias': 'UPDATE_PROFILE',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update Profile',
                    'priority': 40,
                    'providerId': 'UPDATE_PROFILE'
                },
                {
                    'alias': 'VERIFY_EMAIL',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Verify Email',
                    'priority': 50,
                    'providerId': 'VERIFY_EMAIL'
                },
                {
                    'alias': 'delete_account',
                    'config': {},
                    'defaultAction': False,
                    'enabled': False,
                    'name': 'Delete Account',
                    'priority': 60,
                    'providerId': 'delete_account'
                },
                {
                    'alias': 'webauthn-register',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register',
                    'priority': 70,
                    'providerId': 'webauthn-register'
                },
                {
                    'alias': 'webauthn-register-passwordless',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Webauthn Register Passwordless',
                    'priority': 80,
                    'providerId': 'webauthn-register-passwordless'
                },
                {
                    'alias': 'update_user_locale',
                    'config': {},
                    'defaultAction': False,
                    'enabled': True,
                    'name': 'Update User Locale',
                    'priority': 1000,
                    'providerId': 'update_user_locale'
                }
            ],
        ]

        changed = False

        # Run the module
        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_required_actions=return_value_required_actions,
                ) as (
                    mock_get_required_actions,
                    mock_register_required_action,
                    mock_update_required_action,
                    mock_delete_required_action,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Verify number of call on each mock
        self.assertEqual(len(mock_get_required_actions.mock_calls), 1)
        self.assertEqual(len(mock_update_required_action.mock_calls), 0)
        self.assertEqual(len(mock_register_required_action.mock_calls), 0)
        self.assertEqual(len(mock_delete_required_action.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

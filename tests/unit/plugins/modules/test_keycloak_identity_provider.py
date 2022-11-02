# -*- coding: utf-8 -*-

# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules import keycloak_identity_provider

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_identity_provider, create_identity_provider=None, update_identity_provider=None, delete_identity_provider=None,
                       get_identity_provider_mappers=None, create_identity_provider_mapper=None, update_identity_provider_mapper=None,
                       delete_identity_provider_mapper=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_identity_provider.KeycloakAPI
    with patch.object(obj, 'get_identity_provider', side_effect=get_identity_provider) \
            as mock_get_identity_provider:
        with patch.object(obj, 'create_identity_provider', side_effect=create_identity_provider) \
                as mock_create_identity_provider:
            with patch.object(obj, 'update_identity_provider', side_effect=update_identity_provider) \
                    as mock_update_identity_provider:
                with patch.object(obj, 'delete_identity_provider', side_effect=delete_identity_provider) \
                        as mock_delete_identity_provider:
                    with patch.object(obj, 'get_identity_provider_mappers', side_effect=get_identity_provider_mappers) \
                            as mock_get_identity_provider_mappers:
                        with patch.object(obj, 'create_identity_provider_mapper', side_effect=create_identity_provider_mapper) \
                                as mock_create_identity_provider_mapper:
                            with patch.object(obj, 'update_identity_provider_mapper', side_effect=update_identity_provider_mapper) \
                                    as mock_update_identity_provider_mapper:
                                with patch.object(obj, 'delete_identity_provider_mapper', side_effect=delete_identity_provider_mapper) \
                                        as mock_delete_identity_provider_mapper:
                                    yield mock_get_identity_provider, mock_create_identity_provider, mock_update_identity_provider, \
                                        mock_delete_identity_provider, mock_get_identity_provider_mappers, mock_create_identity_provider_mapper, \
                                        mock_update_identity_provider_mapper, mock_delete_identity_provider_mapper


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


class TestKeycloakIdentityProvider(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakIdentityProvider, self).setUp()
        self.module = keycloak_identity_provider

    def test_create_when_absent(self):
        """Add a new identity provider"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'alias': 'oidc-idp',
            'display_name': 'OpenID Connect IdP',
            'enabled': True,
            'provider_id': 'oidc',
            'config': {
                'issuer': 'https://idp.example.com',
                'authorizationUrl': 'https://idp.example.com/auth',
                'tokenUrl': 'https://idp.example.com/token',
                'userInfoUrl': 'https://idp.example.com/userinfo',
                'clientAuthMethod': 'client_secret_post',
                'clientId': 'my-client',
                'clientSecret': 'secret',
                'syncMode': "FORCE",
            },
            'mappers': [{
                'name': "first_name",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'config': {
                    'claim': "first_name",
                    'user.attribute': "first_name",
                    'syncMode': "INHERIT",
                }
            }, {
                'name': "last_name",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'config': {
                    'claim': "last_name",
                    'user.attribute': "last_name",
                    'syncMode': "INHERIT",
                }
            }]
        }
        return_value_idp_get = [
            None,
            {
                "addReadTokenRoleOnCreate": False,
                "alias": "oidc-idp",
                "authenticateByDefault": False,
                "config": {
                    "authorizationUrl": "https://idp.example.com/auth",
                    "clientAuthMethod": "client_secret_post",
                    "clientId": "my-client",
                    "clientSecret": "no_log",
                    "issuer": "https://idp.example.com",
                    "syncMode": "FORCE",
                    "tokenUrl": "https://idp.example.com/token",
                    "userInfoUrl": "https://idp.example.com/userinfo"
                },
                "displayName": "OpenID Connect IdP",
                "enabled": True,
                "firstBrokerLoginFlowAlias": "first broker login",
                "internalId": "7ab437d5-f2bb-4ecc-91a8-315349454da6",
                "linkOnly": False,
                "providerId": "oidc",
                "storeToken": False,
                "trustEmail": False,
            }
        ]
        return_value_mappers_get = [
            [{
                "config": {
                    "claim": "first_name",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }, {
                "config": {
                    "claim": "last_name",
                    "syncMode": "INHERIT",
                    "user.attribute": "last_name"
                },
                "id": "f00c61e0-34d9-4bed-82d1-7e45acfefc09",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "last_name"
            }]
        ]
        return_value_idp_created = [None]
        return_value_mapper_created = [None, None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_identity_provider=return_value_idp_get, get_identity_provider_mappers=return_value_mappers_get,
                                    create_identity_provider=return_value_idp_created, create_identity_provider_mapper=return_value_mapper_created) \
                    as (mock_get_identity_provider, mock_create_identity_provider, mock_update_identity_provider, mock_delete_identity_provider,
                        mock_get_identity_provider_mappers, mock_create_identity_provider_mapper, mock_update_identity_provider_mapper,
                        mock_delete_identity_provider_mapper):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_identity_provider.mock_calls), 2)
        self.assertEqual(len(mock_get_identity_provider_mappers.mock_calls), 1)
        self.assertEqual(len(mock_create_identity_provider.mock_calls), 1)
        self.assertEqual(len(mock_create_identity_provider_mapper.mock_calls), 2)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_when_present(self):
        """Update existing identity provider"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'alias': 'oidc-idp',
            'display_name': 'OpenID Connect IdP',
            'enabled': True,
            'provider_id': 'oidc',
            'config': {
                'issuer': 'https://idp.example.com',
                'authorizationUrl': 'https://idp.example.com/auth',
                'tokenUrl': 'https://idp.example.com/token',
                'userInfoUrl': 'https://idp.example.com/userinfo',
                'clientAuthMethod': 'client_secret_post',
                'clientId': 'my-client',
                'clientSecret': 'secret',
                'syncMode': "FORCE"
            },
            'mappers': [{
                'name': "username",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'config': {
                    'claim': "username",
                    'user.attribute': "username",
                    'syncMode': "INHERIT",
                }
            }, {
                'name': "first_name",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'config': {
                    'claim': "first_name",
                    'user.attribute': "first_name",
                    'syncMode': "INHERIT",
                }
            }, {
                'name': "last_name",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'config': {
                    'claim': "last_name",
                    'user.attribute': "last_name",
                    'syncMode': "INHERIT",
                }
            }]
        }
        return_value_idp_get = [
            {
                "addReadTokenRoleOnCreate": False,
                "alias": "oidc-idp",
                "authenticateByDefault": False,
                "config": {
                    "authorizationUrl": "https://idp.example.com/auth",
                    "clientAuthMethod": "client_secret_post",
                    "clientId": "my-client",
                    "clientSecret": "no_log",
                    "issuer": "https://idp.example.com",
                    "syncMode": "FORCE",
                    "tokenUrl": "https://idp.example.com/token",
                    "userInfoUrl": "https://idp.example.com/userinfo"
                },
                "displayName": "OpenID Connect IdP changeme",
                "enabled": True,
                "firstBrokerLoginFlowAlias": "first broker login",
                "internalId": "7ab437d5-f2bb-4ecc-91a8-315349454da6",
                "linkOnly": False,
                "providerId": "oidc",
                "storeToken": False,
                "trustEmail": False,
            },
            {
                "addReadTokenRoleOnCreate": False,
                "alias": "oidc-idp",
                "authenticateByDefault": False,
                "config": {
                    "authorizationUrl": "https://idp.example.com/auth",
                    "clientAuthMethod": "client_secret_post",
                    "clientId": "my-client",
                    "clientSecret": "no_log",
                    "issuer": "https://idp.example.com",
                    "syncMode": "FORCE",
                    "tokenUrl": "https://idp.example.com/token",
                    "userInfoUrl": "https://idp.example.com/userinfo"
                },
                "displayName": "OpenID Connect IdP",
                "enabled": True,
                "firstBrokerLoginFlowAlias": "first broker login",
                "internalId": "7ab437d5-f2bb-4ecc-91a8-315349454da6",
                "linkOnly": False,
                "providerId": "oidc",
                "storeToken": False,
                "trustEmail": False,
            }
        ]
        return_value_mappers_get = [
            [{
                'config': {
                    'claim': "username",
                    'syncMode': "INHERIT",
                    'user.attribute': "username"
                },
                "id": "616f11ba-b9ae-42ae-bd1b-bc618741c10b",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'name': "username"
            }, {
                "config": {
                    "claim": "first_name_changeme",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }],
            [{
                'config': {
                    'claim': "username",
                    'syncMode': "INHERIT",
                    'user.attribute': "username"
                },
                "id": "616f11ba-b9ae-42ae-bd1b-bc618741c10b",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'name': "username"
            }, {
                "config": {
                    "claim": "first_name_changeme",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }],
            [{
                'config': {
                    'claim': "username",
                    'syncMode': "INHERIT",
                    'user.attribute': "username"
                },
                "id": "616f11ba-b9ae-42ae-bd1b-bc618741c10b",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'name': "username"
            }, {
                "config": {
                    "claim": "first_name_changeme",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }],
            [{
                'config': {
                    'claim': "username",
                    'syncMode': "INHERIT",
                    'user.attribute': "username"
                },
                "id": "616f11ba-b9ae-42ae-bd1b-bc618741c10b",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'name': "username"
            }, {
                "config": {
                    "claim": "first_name_changeme",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }],
            [{
                'config': {
                    'claim': "username",
                    'syncMode': "INHERIT",
                    'user.attribute': "username"
                },
                "id": "616f11ba-b9ae-42ae-bd1b-bc618741c10b",
                'identityProviderAlias': "oidc-idp",
                'identityProviderMapper': "oidc-user-attribute-idp-mapper",
                'name': "username"
            }, {
                "config": {
                    "claim": "first_name",
                    "syncMode": "INHERIT",
                    "user.attribute": "first_name"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "first_name"
            }, {
                "config": {
                    "claim": "last_name",
                    "syncMode": "INHERIT",
                    "user.attribute": "last_name"
                },
                "id": "f00c61e0-34d9-4bed-82d1-7e45acfefc09",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "last_name"
            }]
        ]
        return_value_idp_updated = [None]
        return_value_mapper_updated = [None]
        return_value_mapper_created = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_identity_provider=return_value_idp_get, get_identity_provider_mappers=return_value_mappers_get,
                                    update_identity_provider=return_value_idp_updated, update_identity_provider_mapper=return_value_mapper_updated,
                                    create_identity_provider_mapper=return_value_mapper_created) \
                    as (mock_get_identity_provider, mock_create_identity_provider, mock_update_identity_provider, mock_delete_identity_provider,
                        mock_get_identity_provider_mappers, mock_create_identity_provider_mapper, mock_update_identity_provider_mapper,
                        mock_delete_identity_provider_mapper):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_identity_provider.mock_calls), 2)
        self.assertEqual(len(mock_get_identity_provider_mappers.mock_calls), 5)
        self.assertEqual(len(mock_update_identity_provider.mock_calls), 1)
        self.assertEqual(len(mock_update_identity_provider_mapper.mock_calls), 1)
        self.assertEqual(len(mock_create_identity_provider_mapper.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_absent(self):
        """Remove an absent identity provider"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'alias': 'oidc-idp',
            'state': 'absent',
        }
        return_value_idp_get = [None]
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_identity_provider=return_value_idp_get) \
                    as (mock_get_identity_provider, mock_create_identity_provider, mock_update_identity_provider, mock_delete_identity_provider,
                        mock_get_identity_provider_mappers, mock_create_identity_provider_mapper, mock_update_identity_provider_mapper,
                        mock_delete_identity_provider_mapper):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_identity_provider.mock_calls), 1)
        self.assertEqual(len(mock_delete_identity_provider.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_present(self):
        """Remove an existing identity provider"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'realm': 'realm-name',
            'alias': 'oidc-idp',
            'state': 'absent',
        }
        return_value_idp_get = [
            {
                "addReadTokenRoleOnCreate": False,
                "alias": "oidc-idp",
                "authenticateByDefault": False,
                "config": {
                    "authorizationUrl": "https://idp.example.com/auth",
                    "clientAuthMethod": "client_secret_post",
                    "clientId": "my-client",
                    "clientSecret": "no_log",
                    "issuer": "https://idp.example.com",
                    "syncMode": "FORCE",
                    "tokenUrl": "https://idp.example.com/token",
                    "userInfoUrl": "https://idp.example.com/userinfo"
                },
                "displayName": "OpenID Connect IdP",
                "enabled": True,
                "firstBrokerLoginFlowAlias": "first broker login",
                "internalId": "7ab437d5-f2bb-4ecc-91a8-315349454da6",
                "linkOnly": False,
                "providerId": "oidc",
                "storeToken": False,
                "trustEmail": False,
            },
            None
        ]
        return_value_mappers_get = [
            [{
                "config": {
                    "claim": "email",
                    "syncMode": "INHERIT",
                    "user.attribute": "email"
                },
                "id": "5fde49bb-93bd-4f5d-97d6-c5d0c1d07aef",
                "identityProviderAlias": "oidc-idp",
                "identityProviderMapper": "oidc-user-attribute-idp-mapper",
                "name": "email"
            }]
        ]
        return_value_idp_deleted = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_identity_provider=return_value_idp_get, get_identity_provider_mappers=return_value_mappers_get,
                                    delete_identity_provider=return_value_idp_deleted) \
                    as (mock_get_identity_provider, mock_create_identity_provider, mock_update_identity_provider, mock_delete_identity_provider,
                        mock_get_identity_provider_mappers, mock_create_identity_provider_mapper, mock_update_identity_provider_mapper,
                        mock_delete_identity_provider_mapper):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_identity_provider.mock_calls), 1)
        self.assertEqual(len(mock_get_identity_provider_mappers.mock_calls), 1)
        self.assertEqual(len(mock_delete_identity_provider.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

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

from ansible_collections.community.general.plugins.modules import keycloak_realm_key

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_components=None, get_component=None, create_component=None, update_component=None, delete_component=None):
    """Mock context manager for patching the methods in KeycloakAPI
    """

    obj = keycloak_realm_key.KeycloakAPI
    with patch.object(obj, 'get_components', side_effect=get_components) \
            as mock_get_components:
        with patch.object(obj, 'get_component', side_effect=get_component) \
                as mock_get_component:
            with patch.object(obj, 'create_component', side_effect=create_component) \
                    as mock_create_component:
                with patch.object(obj, 'update_component', side_effect=update_component) \
                        as mock_update_component:
                    with patch.object(obj, 'delete_component', side_effect=delete_component) \
                            as mock_delete_component:
                        yield mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component


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


class TestKeycloakRealmKeys(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealmKeys, self).setUp()
        self.module = keycloak_realm_key

    def test_create_when_absent(self):
        """Add a new realm key"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'parent_id': 'realm-name',
            'name': 'testkey',
            'state': 'present',
            'provider_id': 'rsa',
            'config': {
                'priority': 0,
                'enabled': True,
                'private_key': 'privatekey',
                'algorithm': 'RS256',
                'certificate': 'foo',
            },
        }
        return_value_component_create = [
            {
                "id": "ebb7d999-60cc-4dfe-ab79-48f7bbd9d4d9",
                "name": "testkey",
                "providerId": "rsa",
                "parentId": "90c8fef9-15f8-4d5b-8b22-44e2e1cdcd09",
                "config": {
                    "privateKey": [
                        "**********"
                    ],
                    "certificate": [
                        "foo"
                    ],
                    "active": [
                        "true"
                    ],
                    "priority": [
                        "122"
                    ],
                    "enabled": [
                        "true"
                    ],
                    "algorithm": [
                        "RS256"
                    ]
                }
            }
        ]
        # get before_comp, get default_mapper, get after_mapper
        return_value_components_get = [
            [], [], []
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_components=return_value_components_get, create_component=return_value_component_create) \
                        as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 1)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 1)
        self.assertEqual(len(mock_update_component.mock_calls), 0)
        self.assertEqual(len(mock_delete_component.mock_calls), 0)

        # must not contain parent_id
        mock_create_component.assert_called_once_with({
            'name': 'testkey',
            'providerId': 'rsa',
            'providerType': 'org.keycloak.keys.KeyProvider',
            'config': {
                'priority': ['0'],
                'enabled': ['true'],
                'privateKey': ['privatekey'],
                'algorithm': ['RS256'],
                'certificate': ['foo'],
                'active': ['true'],
            },
        }, 'realm-name')

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present(self):
        """Update existing realm key"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'parent_id': 'realm-name',
            'name': 'testkey',
            'state': 'present',
            'provider_id': 'rsa',
            'config': {
                'priority': 0,
                'enabled': True,
                'private_key': 'privatekey',
                'algorithm': 'RS256',
                'certificate': 'foo',
            },
        }
        return_value_components_get = [
            [

                {
                    "id": "c1a957aa-3df0-4f70-9418-44202bf4ae1f",
                    "name": "testkey",
                    "providerId": "rsa",
                    "providerType": "org.keycloak.keys.KeyProvider",
                    "parentId": "90c8fef9-15f8-4d5b-8b22-44e2e1cdcd09",
                    "config": {
                        "privateKey": [
                            "**********"
                        ],
                        "certificate": [
                            "foo"
                        ],
                        "active": [
                            "true"
                        ],
                        "priority": [
                            "122"
                        ],
                        "enabled": [
                            "true"
                        ],
                        "algorithm": [
                            "RS256"
                        ]
                    }
                },
            ],
            [],
            []
        ]
        return_value_component_update = [
            None
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_components=return_value_components_get,
                                        update_component=return_value_component_update) \
                        as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 1)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 0)
        self.assertEqual(len(mock_update_component.mock_calls), 1)
        self.assertEqual(len(mock_delete_component.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_absent(self):
        """Remove an absent realm key"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'parent_id': 'realm-name',
            'name': 'testkey',
            'state': 'absent',
            'provider_id': 'rsa',
            'config': {
                'priority': 0,
                'enabled': True,
                'private_key': 'privatekey',
                'algorithm': 'RS256',
                'certificate': 'foo',
            },
        }
        return_value_components_get = [
            []
        ]
        changed = False

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_components=return_value_components_get) \
                        as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 1)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 0)
        self.assertEqual(len(mock_update_component.mock_calls), 0)
        self.assertEqual(len(mock_delete_component.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_present(self):
        """Remove an existing realm key"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'parent_id': 'realm-name',
            'name': 'testkey',
            'state': 'absent',
            'provider_id': 'rsa',
            'config': {
                'priority': 0,
                'enabled': True,
                'private_key': 'privatekey',
                'algorithm': 'RS256',
                'certificate': 'foo',
            },
        }

        return_value_components_get = [
            [

                {
                    "id": "c1a957aa-3df0-4f70-9418-44202bf4ae1f",
                    "name": "testkey",
                    "providerId": "rsa",
                    "providerType": "org.keycloak.keys.KeyProvider",
                    "parentId": "90c8fef9-15f8-4d5b-8b22-44e2e1cdcd09",
                    "config": {
                        "privateKey": [
                            "**********"
                        ],
                        "certificate": [
                            "foo"
                        ],
                        "active": [
                            "true"
                        ],
                        "priority": [
                            "122"
                        ],
                        "enabled": [
                            "true"
                        ],
                        "algorithm": [
                            "RS256"
                        ]
                    }
                },
            ],
            [],
            []
        ]
        return_value_component_delete = [
            None
        ]
        changed = True

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_components=return_value_components_get, delete_component=return_value_component_delete) \
                        as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 1)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 0)
        self.assertEqual(len(mock_update_component.mock_calls), 0)
        self.assertEqual(len(mock_delete_component.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

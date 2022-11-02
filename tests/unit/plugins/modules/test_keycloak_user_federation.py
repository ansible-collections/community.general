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

from ansible_collections.community.general.plugins.modules import keycloak_user_federation

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_components=None, get_component=None, create_component=None, update_component=None, delete_component=None):
    """Mock context manager for patching the methods in KeycloakAPI
    """

    obj = keycloak_user_federation.KeycloakAPI
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


class TestKeycloakUserFederation(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakUserFederation, self).setUp()
        self.module = keycloak_user_federation

    def test_create_when_absent(self):
        """Add a new user federation"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'realm': 'realm-name',
            'name': 'kerberos',
            'state': 'present',
            'provider_id': 'kerberos',
            'provider_type': 'org.keycloak.storage.UserStorageProvider',
            'config': {
                'priority': 0,
                'enabled': True,
                'cachePolicy': 'DEFAULT',
                'kerberosRealm': 'REALM',
                'serverPrincipal': 'princ',
                'keyTab': 'keytab',
                'allowPasswordAuthentication': False,
                'updateProfileFirstLogin': False,
            },
        }
        return_value_component_create = [
            {
                "id": "ebb7d999-60cc-4dfe-ab79-48f7bbd9d4d9",
                "name": "kerberos",
                "providerId": "kerberos",
                "providerType": "org.keycloak.storage.UserStorageProvider",
                "parentId": "kerberos",
                "config": {
                    "serverPrincipal": [
                        "princ"
                    ],
                    "allowPasswordAuthentication": [
                        "false"
                    ],
                    "keyTab": [
                        "keytab"
                    ],
                    "cachePolicy": [
                        "DEFAULT"
                    ],
                    "updateProfileFirstLogin": [
                        "false"
                    ],
                    "kerberosRealm": [
                        "REALM"
                    ],
                    "priority": [
                        "0"
                    ],
                    "enabled": [
                        "true"
                    ]
                }
            }
        ]
        return_value_components_get = [
            [], []
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

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

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_when_present(self):
        """Update existing user federation"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'realm': 'realm-name',
            'name': 'kerberos',
            'state': 'present',
            'provider_id': 'kerberos',
            'provider_type': 'org.keycloak.storage.UserStorageProvider',
            'config': {
                'priority': 0,
                'enabled': True,
                'cachePolicy': 'DEFAULT',
                'kerberosRealm': 'REALM',
                'serverPrincipal': 'princ',
                'keyTab': 'keytab',
                'allowPasswordAuthentication': False,
                'updateProfileFirstLogin': False,
            },
        }
        return_value_components_get = [
            [
                {
                    "id": "ebb7d999-60cc-4dfe-ab79-48f7bbd9d4d9",
                    "name": "kerberos",
                    "providerId": "kerberos",
                    "providerType": "org.keycloak.storage.UserStorageProvider",
                    "parentId": "kerberos",
                    "config": {
                        "serverPrincipal": [
                            "princ"
                        ],
                        "allowPasswordAuthentication": [
                            "false"
                        ],
                        "keyTab": [
                            "keytab"
                        ],
                        "cachePolicy": [
                            "DEFAULT"
                        ],
                        "updateProfileFirstLogin": [
                            "false"
                        ],
                        "kerberosRealm": [
                            "REALM"
                        ],
                        "priority": [
                            "0"
                        ],
                        "enabled": [
                            "false"
                        ]
                    }
                }
            ],
            []
        ]
        return_value_component_get = [
            {
                "id": "ebb7d999-60cc-4dfe-ab79-48f7bbd9d4d9",
                "name": "kerberos",
                "providerId": "kerberos",
                "providerType": "org.keycloak.storage.UserStorageProvider",
                "parentId": "kerberos",
                "config": {
                    "serverPrincipal": [
                        "princ"
                    ],
                    "allowPasswordAuthentication": [
                        "false"
                    ],
                    "keyTab": [
                        "keytab"
                    ],
                    "cachePolicy": [
                        "DEFAULT"
                    ],
                    "updateProfileFirstLogin": [
                        "false"
                    ],
                    "kerberosRealm": [
                        "REALM"
                    ],
                    "priority": [
                        "0"
                    ],
                    "enabled": [
                        "true"
                    ]
                }
            }
        ]
        return_value_component_update = [
            None
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_components=return_value_components_get, get_component=return_value_component_get,
                                    update_component=return_value_component_update) \
                    as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 2)
        self.assertEqual(len(mock_get_component.mock_calls), 1)
        self.assertEqual(len(mock_create_component.mock_calls), 0)
        self.assertEqual(len(mock_update_component.mock_calls), 1)
        self.assertEqual(len(mock_delete_component.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_with_mappers(self):
        """Add a new user federation with mappers"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'realm': 'realm-name',
            'name': 'ldap',
            'state': 'present',
            'provider_id': 'ldap',
            'provider_type': 'org.keycloak.storage.UserStorageProvider',
            'config': {
                'priority': 0,
                'enabled': True,
                'cachePolicy': 'DEFAULT',
                'batchSizeForSync': 1000,
                'editMode': 'READ_ONLY',
                'importEnabled': True,
                'syncRegistrations': False,
                'vendor': 'other',
                'usernameLDAPAttribute': 'uid',
                'rdnLDAPAttribute': 'uid',
                'uuidLDAPAttribute': 'entryUUID',
                'userObjectClasses': 'inetOrgPerson, organizationalPerson',
                'connectionUrl': 'ldaps://ldap.example.com:636',
                'usersDn': 'ou=Users,dc=example,dc=com',
                'authType': 'none',
                'searchScope': 1,
                'validatePasswordPolicy': False,
                'trustEmail': False,
                'useTruststoreSpi': 'ldapsOnly',
                'connectionPooling': True,
                'pagination': True,
                'allowKerberosAuthentication': False,
                'debug': False,
                'useKerberosForPasswordAuthentication': False,
            },
            'mappers': [
                {
                    'name': 'full name',
                    'providerId': 'full-name-ldap-mapper',
                    'providerType': 'org.keycloak.storage.ldap.mappers.LDAPStorageMapper',
                    'config': {
                        'ldap.full.name.attribute': 'cn',
                        'read.only': True,
                        'write.only': False,
                    }
                }
            ]
        }
        return_value_components_get = [
            [], []
        ]
        return_value_component_create = [
            {
                "id": "eb691537-b73c-4cd8-b481-6031c26499d8",
                "name": "ldap",
                "providerId": "ldap",
                "providerType": "org.keycloak.storage.UserStorageProvider",
                "parentId": "ldap",
                "config": {
                    "pagination": [
                        "true"
                    ],
                    "connectionPooling": [
                        "true"
                    ],
                    "usersDn": [
                        "ou=Users,dc=example,dc=com"
                    ],
                    "cachePolicy": [
                        "DEFAULT"
                    ],
                    "useKerberosForPasswordAuthentication": [
                        "false"
                    ],
                    "importEnabled": [
                        "true"
                    ],
                    "enabled": [
                        "true"
                    ],
                    "usernameLDAPAttribute": [
                        "uid"
                    ],
                    "vendor": [
                        "other"
                    ],
                    "uuidLDAPAttribute": [
                        "entryUUID"
                    ],
                    "connectionUrl": [
                        "ldaps://ldap.example.com:636"
                    ],
                    "allowKerberosAuthentication": [
                        "false"
                    ],
                    "syncRegistrations": [
                        "false"
                    ],
                    "authType": [
                        "none"
                    ],
                    "debug": [
                        "false"
                    ],
                    "searchScope": [
                        "1"
                    ],
                    "useTruststoreSpi": [
                        "ldapsOnly"
                    ],
                    "trustEmail": [
                        "false"
                    ],
                    "priority": [
                        "0"
                    ],
                    "userObjectClasses": [
                        "inetOrgPerson, organizationalPerson"
                    ],
                    "rdnLDAPAttribute": [
                        "uid"
                    ],
                    "editMode": [
                        "READ_ONLY"
                    ],
                    "validatePasswordPolicy": [
                        "false"
                    ],
                    "batchSizeForSync": [
                        "1000"
                    ]
                }
            },
            {
                "id": "2dfadafd-8b34-495f-a98b-153e71a22311",
                "name": "full name",
                "providerId": "full-name-ldap-mapper",
                "providerType": "org.keycloak.storage.ldap.mappers.LDAPStorageMapper",
                "parentId": "eb691537-b73c-4cd8-b481-6031c26499d8",
                "config": {
                    "ldap.full.name.attribute": [
                        "cn"
                    ],
                    "read.only": [
                        "true"
                    ],
                    "write.only": [
                        "false"
                    ]
                }
            }
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_components=return_value_components_get, create_component=return_value_component_create) \
                    as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 2)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 2)
        self.assertEqual(len(mock_update_component.mock_calls), 0)
        self.assertEqual(len(mock_delete_component.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_when_absent(self):
        """Remove an absent user federation"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'realm': 'realm-name',
            'name': 'kerberos',
            'state': 'absent',
        }
        return_value_components_get = [
            []
        ]
        changed = False

        set_module_args(module_args)

        # Run the module

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
        """Remove an existing user federation"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'realm': 'realm-name',
            'name': 'kerberos',
            'state': 'absent',
        }
        return_value_components_get = [
            [
                {
                    "id": "ebb7d999-60cc-4dfe-ab79-48f7bbd9d4d9",
                    "name": "kerberos",
                    "providerId": "kerberos",
                    "providerType": "org.keycloak.storage.UserStorageProvider",
                    "parentId": "kerberos",
                    "config": {
                        "serverPrincipal": [
                            "princ"
                        ],
                        "allowPasswordAuthentication": [
                            "false"
                        ],
                        "keyTab": [
                            "keytab"
                        ],
                        "cachePolicy": [
                            "DEFAULT"
                        ],
                        "updateProfileFirstLogin": [
                            "false"
                        ],
                        "kerberosRealm": [
                            "REALM"
                        ],
                        "priority": [
                            "0"
                        ],
                        "enabled": [
                            "false"
                        ]
                    }
                }
            ],
            []
        ]
        return_value_component_delete = [
            None
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_components=return_value_components_get, delete_component=return_value_component_delete) \
                    as (mock_get_components, mock_get_component, mock_create_component, mock_update_component, mock_delete_component):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_components.mock_calls), 2)
        self.assertEqual(len(mock_get_component.mock_calls), 0)
        self.assertEqual(len(mock_create_component.mock_calls), 0)
        self.assertEqual(len(mock_update_component.mock_calls), 0)
        self.assertEqual(len(mock_delete_component.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

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

from ansible_collections.community.general.plugins.modules import keycloak_client_rolemapping

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_group_by_name=None, get_client_id=None, get_client_role_id_by_name=None,
                       get_client_group_rolemapping_by_id=None, get_client_group_available_rolemappings=None,
                       get_client_group_composite_rolemappings=None, add_group_rolemapping=None,
                       delete_group_rolemapping=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_client_rolemapping.KeycloakAPI
    with patch.object(obj, 'get_group_by_name',
                      side_effect=get_group_by_name) as mock_get_group_by_name:
        with patch.object(obj, 'get_client_id',
                          side_effect=get_client_id) as mock_get_client_id:
            with patch.object(obj, 'get_client_role_id_by_name',
                              side_effect=get_client_role_id_by_name) as mock_get_client_role_id_by_name:
                with patch.object(obj, 'get_client_group_rolemapping_by_id',
                                  side_effect=get_client_group_rolemapping_by_id) as mock_get_client_group_rolemapping_by_id:
                    with patch.object(obj, 'get_client_group_available_rolemappings',
                                      side_effect=get_client_group_available_rolemappings) as mock_get_client_group_available_rolemappings:
                        with patch.object(obj, 'get_client_group_composite_rolemappings',
                                          side_effect=get_client_group_composite_rolemappings) as mock_get_client_group_composite_rolemappings:
                            with patch.object(obj, 'add_group_rolemapping',
                                              side_effect=add_group_rolemapping) as mock_add_group_rolemapping:
                                with patch.object(obj, 'delete_group_rolemapping',
                                                  side_effect=delete_group_rolemapping) as mock_delete_group_rolemapping:
                                    yield mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping, \
                                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, \
                                        mock_get_client_group_composite_rolemappings, mock_delete_group_rolemapping


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
        self.module = keycloak_client_rolemapping

    def test_map_clientrole_to_group_with_name(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'client_id': 'test_client',
            'group_name': 'test_group',
            'roles': [
                {
                    'name': 'test_role1',
                },
                {
                    'name': 'test_role1',
                },
            ],
        }
        return_value_get_group_by_name = [{
            "access": {
                "manage": "true",
                "manageMembership": "true",
                "view": "true"
            },
            "attributes": "{}",
            "clientRoles": "{}",
            "id": "92f2400e-0ecb-4185-8950-12dcef616c2b",
            "name": "test_group",
            "path": "/test_group",
            "realmRoles": "[]",
            "subGroups": "[]"
        }]
        return_value_get_client_id = "c0f8490c-b224-4737-a567-20223e4c1727"
        return_value_get_client_role_id_by_name = "e91af074-cfd5-40ee-8ef5-ae0ae1ce69fe"
        return_value_get_client_group_available_rolemappings = [[
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                "name": "test_role2"
            },
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                "name": "test_role1"
            }
        ]]
        return_value_get_client_group_composite_rolemappings = [
            None,
            [
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                    "name": "test_role2"
                },
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                    "name": "test_role1"
                }
            ]
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_group_by_name=return_value_get_group_by_name, get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_group_available_rolemappings=return_value_get_client_group_available_rolemappings,
                                    get_client_group_composite_rolemappings=return_value_get_client_group_composite_rolemappings) \
                    as (mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping,
                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, mock_get_client_group_composite_rolemappings,
                        mock_delete_group_rolemapping):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_group_by_name.call_count, 1)
        self.assertEqual(mock_get_client_id.call_count, 1)
        self.assertEqual(mock_add_group_rolemapping.call_count, 1)
        self.assertEqual(mock_get_client_group_rolemapping_by_id.call_count, 0)
        self.assertEqual(mock_get_client_group_available_rolemappings.call_count, 1)
        self.assertEqual(mock_get_client_group_composite_rolemappings.call_count, 2)
        self.assertEqual(mock_delete_group_rolemapping.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_map_clientrole_to_group_with_name_idempotency(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'client_id': 'test_client',
            'group_name': 'test_group',
            'roles': [
                {
                    'name': 'test_role1',
                },
                {
                    'name': 'test_role1',
                },
            ],
        }
        return_value_get_group_by_name = [{
            "access": {
                "manage": "true",
                "manageMembership": "true",
                "view": "true"
            },
            "attributes": "{}",
            "clientRoles": "{}",
            "id": "92f2400e-0ecb-4185-8950-12dcef616c2b",
            "name": "test_group",
            "path": "/test_group",
            "realmRoles": "[]",
            "subGroups": "[]"
        }]
        return_value_get_client_id = "c0f8490c-b224-4737-a567-20223e4c1727"
        return_value_get_client_role_id_by_name = "e91af074-cfd5-40ee-8ef5-ae0ae1ce69fe"
        return_value_get_client_group_available_rolemappings = [[]]
        return_value_get_client_group_composite_rolemappings = [[
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                "name": "test_role2"
            },
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                "name": "test_role1"
            }
        ]]

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_group_by_name=return_value_get_group_by_name, get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_group_available_rolemappings=return_value_get_client_group_available_rolemappings,
                                    get_client_group_composite_rolemappings=return_value_get_client_group_composite_rolemappings) \
                    as (mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping,
                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, mock_get_client_group_composite_rolemappings,
                        mock_delete_group_rolemapping):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_group_by_name.call_count, 1)
        self.assertEqual(mock_get_client_id.call_count, 1)
        self.assertEqual(mock_add_group_rolemapping.call_count, 0)
        self.assertEqual(mock_get_client_group_rolemapping_by_id.call_count, 0)
        self.assertEqual(mock_get_client_group_available_rolemappings.call_count, 1)
        self.assertEqual(mock_get_client_group_composite_rolemappings.call_count, 1)
        self.assertEqual(mock_delete_group_rolemapping.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_map_clientrole_to_group_with_id(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'cid': 'c0f8490c-b224-4737-a567-20223e4c1727',
            'gid': '92f2400e-0ecb-4185-8950-12dcef616c2b',
            'roles': [
                {
                    'name': 'test_role1',
                },
                {
                    'name': 'test_role1',
                },
            ],
        }
        return_value_get_group_by_name = [{
            "access": {
                "manage": "true",
                "manageMembership": "true",
                "view": "true"
            },
            "attributes": "{}",
            "clientRoles": "{}",
            "id": "92f2400e-0ecb-4185-8950-12dcef616c2b",
            "name": "test_group",
            "path": "/test_group",
            "realmRoles": "[]",
            "subGroups": "[]"
        }]
        return_value_get_client_id = "c0f8490c-b224-4737-a567-20223e4c1727"
        return_value_get_client_role_id_by_name = "e91af074-cfd5-40ee-8ef5-ae0ae1ce69fe"
        return_value_get_client_group_available_rolemappings = [[
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                "name": "test_role2"
            },
            {
                "clientRole": "true",
                "composite": "false",
                "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                "name": "test_role1"
            }
        ]]
        return_value_get_client_group_composite_rolemappings = [
            None,
            [
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                    "name": "test_role2"
                },
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                    "name": "test_role1"
                }
            ]
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_group_by_name=return_value_get_group_by_name, get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_group_available_rolemappings=return_value_get_client_group_available_rolemappings,
                                    get_client_group_composite_rolemappings=return_value_get_client_group_composite_rolemappings) \
                    as (mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping,
                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, mock_get_client_group_composite_rolemappings,
                        mock_delete_group_rolemapping):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_group_by_name.call_count, 0)
        self.assertEqual(mock_get_client_id.call_count, 0)
        self.assertEqual(mock_add_group_rolemapping.call_count, 1)
        self.assertEqual(mock_get_client_group_rolemapping_by_id.call_count, 0)
        self.assertEqual(mock_get_client_group_available_rolemappings.call_count, 1)
        self.assertEqual(mock_get_client_group_composite_rolemappings.call_count, 2)
        self.assertEqual(mock_delete_group_rolemapping.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_remove_clientrole_from_group(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'absent',
            'client_id': 'test_client',
            'group_name': 'test_group',
            'roles': [
                {
                    'name': 'test_role1',
                },
                {
                    'name': 'test_role1',
                },
            ],
        }
        return_value_get_group_by_name = [{
            "access": {
                "manage": "true",
                "manageMembership": "true",
                "view": "true"
            },
            "attributes": "{}",
            "clientRoles": "{}",
            "id": "92f2400e-0ecb-4185-8950-12dcef616c2b",
            "name": "test_group",
            "path": "/test_group",
            "realmRoles": "[]",
            "subGroups": "[]"
        }]
        return_value_get_client_id = "c0f8490c-b224-4737-a567-20223e4c1727"
        return_value_get_client_role_id_by_name = "e91af074-cfd5-40ee-8ef5-ae0ae1ce69fe"
        return_value_get_client_group_available_rolemappings = [[]]
        return_value_get_client_group_composite_rolemappings = [
            [
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                    "name": "test_role2"
                },
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                    "name": "test_role1"
                }
            ],
            []
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_group_by_name=return_value_get_group_by_name, get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_group_available_rolemappings=return_value_get_client_group_available_rolemappings,
                                    get_client_group_composite_rolemappings=return_value_get_client_group_composite_rolemappings) \
                    as (mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping,
                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, mock_get_client_group_composite_rolemappings,
                        mock_delete_group_rolemapping):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_group_by_name.call_count, 1)
        self.assertEqual(mock_get_client_id.call_count, 1)
        self.assertEqual(mock_add_group_rolemapping.call_count, 0)
        self.assertEqual(mock_get_client_group_rolemapping_by_id.call_count, 0)
        self.assertEqual(mock_get_client_group_available_rolemappings.call_count, 1)
        self.assertEqual(mock_get_client_group_composite_rolemappings.call_count, 2)
        self.assertEqual(mock_delete_group_rolemapping.call_count, 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_remove_clientrole_from_group_idempotency(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'absent',
            'client_id': 'test_client',
            'group_name': 'test_group',
            'roles': [
                {
                    'name': 'test_role1',
                },
                {
                    'name': 'test_role1',
                },
            ],
        }
        return_value_get_group_by_name = [{
            "access": {
                "manage": "true",
                "manageMembership": "true",
                "view": "true"
            },
            "attributes": "{}",
            "clientRoles": "{}",
            "id": "92f2400e-0ecb-4185-8950-12dcef616c2b",
            "name": "test_group",
            "path": "/test_group",
            "realmRoles": "[]",
            "subGroups": "[]"
        }]
        return_value_get_client_id = "c0f8490c-b224-4737-a567-20223e4c1727"
        return_value_get_client_role_id_by_name = "e91af074-cfd5-40ee-8ef5-ae0ae1ce69fe"
        return_value_get_client_group_available_rolemappings = [
            [
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d",
                    "name": "test_role2"
                },
                {
                    "clientRole": "true",
                    "composite": "false",
                    "containerId": "c0f8490c-b224-4737-a567-20223e4c1727",
                    "id": "00a2d9a9-924e-49fa-8cde-c539c010ef6e",
                    "name": "test_role1"
                }
            ]
        ]
        return_value_get_client_group_composite_rolemappings = [[]]

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_group_by_name=return_value_get_group_by_name, get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_group_available_rolemappings=return_value_get_client_group_available_rolemappings,
                                    get_client_group_composite_rolemappings=return_value_get_client_group_composite_rolemappings) \
                    as (mock_get_group_by_name, mock_get_client_id, mock_get_client_role_id_by_name, mock_add_group_rolemapping,
                        mock_get_client_group_rolemapping_by_id, mock_get_client_group_available_rolemappings, mock_get_client_group_composite_rolemappings,
                        mock_delete_group_rolemapping):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_group_by_name.call_count, 1)
        self.assertEqual(mock_get_client_id.call_count, 1)
        self.assertEqual(mock_add_group_rolemapping.call_count, 0)
        self.assertEqual(mock_get_client_group_rolemapping_by_id.call_count, 0)
        self.assertEqual(mock_get_client_group_available_rolemappings.call_count, 1)
        self.assertEqual(mock_get_client_group_composite_rolemappings.call_count, 1)
        self.assertEqual(mock_delete_group_rolemapping.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

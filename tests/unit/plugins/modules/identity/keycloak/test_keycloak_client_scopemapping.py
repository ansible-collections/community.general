# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_client_scopemapping

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_client_id=None,
                       get_client_role_id_by_name=None,
                       get_client_role_name_by_id=None,
                       get_client_scopemappings_client_available=None,
                       get_client_scopemappings_client_composite=None,
                       add_client_scopemappings_client=None,
                       remove_client_scopemappings_client=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_client_scopemapping.KeycloakAPI
    with patch.object(obj, 'get_client_id',
                      side_effect=get_client_id) as mock_get_client_id:
        with patch.object(obj, 'get_client_role_id_by_name',
                          side_effect=get_client_role_id_by_name) as mock_get_client_role_id_by_name:
            with patch.object(obj, 'get_client_role_name_by_id',
                              side_effect=get_client_role_name_by_id) as mock_get_client_role_name_by_id:
                with patch.object(obj, 'get_client_scopemappings_client_available',
                                  side_effect=get_client_scopemappings_client_available) as mock_get_client_scopemappings_client_available:
                    with patch.object(obj, 'get_client_scopemappings_client_composite',
                                      side_effect=get_client_scopemappings_client_composite) as mock_get_client_scopemappings_client_composite:
                        with patch.object(obj, 'add_client_scopemappings_client',
                                          side_effect=add_client_scopemappings_client) as mock_add_client_scopemappings_client:
                            with patch.object(obj, 'remove_client_scopemappings_client',
                                              side_effect=remove_client_scopemappings_client) as mock_remove_client_scopemappings_client:
                                yield mock_get_client_id, \
                                    mock_get_client_role_id_by_name, \
                                    mock_get_client_role_name_by_id, \
                                    mock_get_client_scopemappings_client_available, \
                                    mock_get_client_scopemappings_client_composite, \
                                    mock_add_client_scopemappings_client, \
                                    mock_remove_client_scopemappings_client


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


class TestKeycloakClientScopeMapping(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakClientScopeMapping, self).setUp()
        self.module = keycloak_client_scopemapping

    def test_add_role_with_name(self):
        """Map role name to id and name, add one role"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'client_id': 'client_to_grant',  # c0f8490c-b224-4737-a567-20223e4c1727
            'client_role': {
                'client_id': 'client_with_roles',  # 27112a16-c847-4def-9140-2b97a1f4108a
                'roles': [{
                    'name': 'test_role2',  # c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d
                }],
            },
        }

        return_value_get_client_id = [
            'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
        ]
        return_value_get_client_role_id_by_name = [
            '00a2d9a9-924e-49fa-8cde-c539c010ef6e'  # test_role1
        ]
        return_value_get_client_role_name_by_id = [
            'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
        ]
        return_value_get_client_scopemappings_client_available = [
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }, {
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }]
        ]
        return_value_get_client_scopemappings_client_composite = [
            [],  # Before
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }]  # After
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_role_name_by_id=return_value_get_client_role_name_by_id,
                                    get_client_scopemappings_client_available=return_value_get_client_scopemappings_client_available,
                                    get_client_scopemappings_client_composite=return_value_get_client_scopemappings_client_composite)\
                    as (mock_get_client_id,
                        mock_get_client_role_id_by_name,
                        mock_get_client_role_name_by_id,
                        mock_get_client_scopemappings_client_available,
                        mock_get_client_scopemappings_client_composite,
                        mock_add_client_scopemappings_client,
                        mock_remove_client_scopemappings_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_id.call_count, 2)
        self.assertEqual(mock_get_client_role_id_by_name.call_count, 1)
        self.assertEqual(mock_get_client_role_name_by_id.call_count, 0)
        self.assertEqual(mock_get_client_scopemappings_client_available.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_composite.call_count, 2)
        self.assertEqual(mock_add_client_scopemappings_client.call_count, 1)
        self.assertEqual(mock_remove_client_scopemappings_client.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_add_role_with_name_idempotency(self):
        """Map role name to id and name, no change"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'client_id': 'client_to_grant',  # c0f8490c-b224-4737-a567-20223e4c1727
            'client_role': {
                'client_id': 'client_with_roles',  # 27112a16-c847-4def-9140-2b97a1f4108a
                'roles': [{
                    'name': 'test_role1',  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
                }, {
                    'name': 'test_role2',  # c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d
                }],
            },
        }

        return_value_get_client_id = [
            'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
        ]
        return_value_get_client_role_id_by_name = [
            '00a2d9a9-924e-49fa-8cde-c539c010ef6e',  # test_role1
            'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',  # test_role2
        ]
        return_value_get_client_role_name_by_id = [
            'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
        ]
        return_value_get_client_scopemappings_client_available = [
            [],  # Empty, all available roles are already granted
        ]
        return_value_get_client_scopemappings_client_composite = [
            [],  # Before
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }, {
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }]]  # After

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_role_name_by_id=return_value_get_client_role_name_by_id,
                                    get_client_scopemappings_client_available=return_value_get_client_scopemappings_client_available,
                                    get_client_scopemappings_client_composite=return_value_get_client_scopemappings_client_composite)\
                    as (mock_get_client_id,
                        mock_get_client_role_id_by_name,
                        mock_get_client_role_name_by_id,
                        mock_get_client_scopemappings_client_available,
                        mock_get_client_scopemappings_client_composite,
                        mock_add_client_scopemappings_client,
                        mock_remove_client_scopemappings_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_id.call_count, 2)
        self.assertEqual(mock_get_client_role_id_by_name.call_count, 2)
        self.assertEqual(mock_get_client_role_name_by_id.call_count, 0)
        self.assertEqual(mock_get_client_scopemappings_client_available.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_composite.call_count, 1)
        self.assertEqual(mock_add_client_scopemappings_client.call_count, 0)
        self.assertEqual(mock_remove_client_scopemappings_client.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_add_role_with_id(self):
        """Add one role with ID"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'present',
            'id': 'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            'client_role': {
                'id': '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
                'roles': [{
                    'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',  # test_role1
                }],
            },
        }
        return_value_get_client_id = [
            'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
        ]
        return_value_get_client_role_id_by_name = [
            '00a2d9a9-924e-49fa-8cde-c539c010ef6e'  # test_role1
        ]
        return_value_get_client_role_name_by_id = [
            'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
        ]
        return_value_get_client_scopemappings_client_available = [
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }, {
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }]
        ]
        return_value_get_client_scopemappings_client_composite = [
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }],  # Before
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }, {
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }]  # After
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_role_name_by_id=return_value_get_client_role_name_by_id,
                                    get_client_scopemappings_client_available=return_value_get_client_scopemappings_client_available,
                                    get_client_scopemappings_client_composite=return_value_get_client_scopemappings_client_composite)\
                    as (mock_get_client_id,
                        mock_get_client_role_id_by_name,
                        mock_get_client_role_name_by_id,
                        mock_get_client_scopemappings_client_available,
                        mock_get_client_scopemappings_client_composite,
                        mock_add_client_scopemappings_client,
                        mock_remove_client_scopemappings_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_id.call_count, 0)
        self.assertEqual(mock_get_client_role_id_by_name.call_count, 0)
        self.assertEqual(mock_get_client_role_name_by_id.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_available.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_composite.call_count, 2)
        self.assertEqual(mock_add_client_scopemappings_client.call_count, 1)
        self.assertEqual(mock_remove_client_scopemappings_client.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_remove_role(self):
        """Remove a role by client ID and role name"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'absent',
            'id': 'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            'client_role': {
                'id': '52c4d786-b790-4570-9fc2-037aee19a2c2',  # client_with_roles
                'roles': [{
                    'name': 'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
                }],
            },
        }
        return_value_get_client_id = [
            'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
        ]
        return_value_get_client_role_id_by_name = [
            '00a2d9a9-924e-49fa-8cde-c539c010ef6e'  # test_role1
        ]
        return_value_get_client_role_name_by_id = [
            'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
        ]
        return_value_get_client_scopemappings_client_available = [
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                'name': 'test_role2'
            }],
        ]
        return_value_get_client_scopemappings_client_composite = [
            [{
                'clientRole': 'true',
                'composite': 'false',
                'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                'name': 'test_role1'
            }],  # Before
            []   # After
        ]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_role_name_by_id=return_value_get_client_role_name_by_id,
                                    get_client_scopemappings_client_available=return_value_get_client_scopemappings_client_available,
                                    get_client_scopemappings_client_composite=return_value_get_client_scopemappings_client_composite)\
                    as (mock_get_client_id,
                        mock_get_client_role_id_by_name,
                        mock_get_client_role_name_by_id,
                        mock_get_client_scopemappings_client_available,
                        mock_get_client_scopemappings_client_composite,
                        mock_add_client_scopemappings_client,
                        mock_remove_client_scopemappings_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_id.call_count, 0)
        self.assertEqual(mock_get_client_role_id_by_name.call_count, 1)
        self.assertEqual(mock_get_client_role_name_by_id.call_count, 0)
        self.assertEqual(mock_get_client_scopemappings_client_available.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_composite.call_count, 2)
        self.assertEqual(mock_add_client_scopemappings_client.call_count, 0)
        self.assertEqual(mock_remove_client_scopemappings_client.call_count, 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_remove_role_idempotency(self):
        """Remove role, no change"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'realm': 'realm-name',
            'state': 'absent',
            'id': 'c0f8490c-b224-4737-a567-20223e4c1727',  # client_to_grant
            'client_role': {
                'client_id': 'client_with_roles',  # 52c4d786-b790-4570-9fc2-037aee19a2c2
                'roles': [{
                    'name': 'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
                }],
            },
        }
        return_value_get_client_id = [
            '27112a16-c847-4def-9140-2b97a1f4108a',  # client_with_roles
        ]
        return_value_get_client_role_id_by_name = [
            '00a2d9a9-924e-49fa-8cde-c539c010ef6e'  # test_role1
        ]
        return_value_get_client_role_name_by_id = [
            'test_role1'  # 00a2d9a9-924e-49fa-8cde-c539c010ef6e
        ]
        return_value_get_client_scopemappings_client_available = [
            [
                {
                    'clientRole': 'true',
                    'composite': 'false',
                    'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                    'id': 'c2bf2edb-da94-4f2f-b9f2-196dfee3fe4d',
                    'name': 'test_role2'
                },
                {
                    'clientRole': 'true',
                    'composite': 'false',
                    'containerId': 'c0f8490c-b224-4737-a567-20223e4c1727',
                    'id': '00a2d9a9-924e-49fa-8cde-c539c010ef6e',
                    'name': 'test_role1'
                }
            ],
        ]
        return_value_get_client_scopemappings_client_composite = [
            [],
        ]

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_id=return_value_get_client_id,
                                    get_client_role_id_by_name=return_value_get_client_role_id_by_name,
                                    get_client_role_name_by_id=return_value_get_client_role_name_by_id,
                                    get_client_scopemappings_client_available=return_value_get_client_scopemappings_client_available,
                                    get_client_scopemappings_client_composite=return_value_get_client_scopemappings_client_composite)\
                    as (mock_get_client_id,
                        mock_get_client_role_id_by_name,
                        mock_get_client_role_name_by_id,
                        mock_get_client_scopemappings_client_available,
                        mock_get_client_scopemappings_client_composite,
                        mock_add_client_scopemappings_client,
                        mock_remove_client_scopemappings_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_id.call_count, 1)
        self.assertEqual(mock_get_client_role_id_by_name.call_count, 1)
        self.assertEqual(mock_get_client_role_name_by_id.call_count, 0)
        self.assertEqual(mock_get_client_scopemappings_client_available.call_count, 1)
        self.assertEqual(mock_get_client_scopemappings_client_composite.call_count, 1)
        self.assertEqual(mock_add_client_scopemappings_client.call_count, 0)
        self.assertEqual(mock_remove_client_scopemappings_client.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

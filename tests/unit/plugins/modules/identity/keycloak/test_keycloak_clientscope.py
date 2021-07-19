# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, \
    ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_clientscope

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_clientscope_by_name=None, get_clientscope_by_clientscopeid=None, create_clientscope=None,
                       update_clientscope=None, get_clientscope_protocolmapper_by_name=None,
                       update_clientscope_protocolmappers=None, create_clientscope_protocolmapper=None,
                       delete_clientscope=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    """
    get_clientscope_by_clientscopeid
    delete_clientscope
    """

    obj = keycloak_clientscope.KeycloakAPI
    with patch.object(obj, 'get_clientscope_by_name', side_effect=get_clientscope_by_name) \
            as mock_get_clientscope_by_name:
        with patch.object(obj, 'get_clientscope_by_clientscopeid', side_effect=get_clientscope_by_clientscopeid) \
                as mock_get_clientscope_by_clientscopeid:
            with patch.object(obj, 'create_clientscope', side_effect=create_clientscope) \
                    as mock_create_clientscope:
                with patch.object(obj, 'update_clientscope', return_value=update_clientscope) \
                        as mock_update_clientscope:
                    with patch.object(obj, 'get_clientscope_protocolmapper_by_name',
                                      side_effect=get_clientscope_protocolmapper_by_name) \
                            as mock_get_clientscope_protocolmapper_by_name:
                        with patch.object(obj, 'update_clientscope_protocolmappers',
                                          side_effect=update_clientscope_protocolmappers) \
                                as mock_update_clientscope_protocolmappers:
                            with patch.object(obj, 'create_clientscope_protocolmapper',
                                              side_effect=create_clientscope_protocolmapper) \
                                    as mock_create_clientscope_protocolmapper:
                                with patch.object(obj, 'delete_clientscope', side_effect=delete_clientscope) \
                                        as mock_delete_clientscope:
                                    yield mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope, \
                                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name, mock_update_clientscope_protocolmappers, \
                                        mock_create_clientscope_protocolmapper, mock_delete_clientscope


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
        'http://keycloak.url/auth/realms/master/protocol/openid-connect/token': create_wrapper(
            '{"access_token": "alongtoken"}'), }
    return patch(
        'ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url',
        side_effect=build_mocked_request(count(), token_response),
        autospec=True
    )


class TestKeycloakAuthentication(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakAuthentication, self).setUp()
        self.module = keycloak_clientscope

    def test_create_clientscope(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'present',
            'name': 'my-new-kc-clientscope'
        }
        return_value_get_clientscope_by_name = [
            None,
            {
                "attributes": {},
                "id": "73fec1d2-f032-410c-8177-583104d01305",
                "name": "my-new-kc-clientscope"
            }]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 2)
        self.assertEqual(mock_create_clientscope.call_count, 1)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 0)
        self.assertEqual(mock_update_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 0)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 0)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_clientscope_idempotency(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'present',
            'name': 'my-new-kc-clientscope'
        }
        return_value_get_clientscope_by_name = [{
            "attributes": {},
            "id": "73fec1d2-f032-410c-8177-583104d01305",
            "name": "my-new-kc-clientscope"
        }]

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 1)
        self.assertEqual(mock_create_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 0)
        self.assertEqual(mock_update_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 0)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 0)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_clientscope(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'absent',
            'name': 'my-new-kc-clientscope'
        }
        return_value_get_clientscope_by_name = [{
            "attributes": {},
            "id": "73fec1d2-f032-410c-8177-583104d01305",
            "name": "my-new-kc-clientscope"
        }]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 1)
        self.assertEqual(mock_create_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 0)
        self.assertEqual(mock_update_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 0)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 0)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_clientscope_idempotency(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'absent',
            'name': 'my-new-kc-clientscope'
        }
        return_value_get_clientscope_by_name = [None]

        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 1)
        self.assertEqual(mock_create_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 0)
        self.assertEqual(mock_update_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 0)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 0)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_create_clientscope_with_protocolmappers(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'present',
            'name': 'my-new-kc-clientscope',
            'protocolMappers': [
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'true',
                        'id.token.claim': 'true',
                        'access.token.claim': 'true',
                        'userinfo.token.claim': 'true',
                        'claim.name': 'protocol1',
                    },
                    'name': 'protocol1',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'false',
                        'id.token.claim': 'false',
                        'access.token.claim': 'false',
                        'userinfo.token.claim': 'false',
                        'claim.name': 'protocol2',
                    },
                    'name': 'protocol2',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'true',
                        'id.token.claim': 'false',
                        'access.token.claim': 'true',
                        'userinfo.token.claim': 'false',
                        'claim.name': 'protocol3',
                    },
                    'name': 'protocol3',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
            ]
        }
        return_value_get_clientscope_by_name = [
            None,
            {
                "attributes": {},
                "id": "890ec72e-fe1d-4308-9f27-485ef7eaa182",
                "name": "my-new-kc-clientscope",
                "protocolMappers": [
                    {
                        "config": {
                            "access.token.claim": "false",
                            "claim.name": "protocol2",
                            "full.path": "false",
                            "id.token.claim": "false",
                            "userinfo.token.claim": "false"
                        },
                        "consentRequired": "false",
                        "id": "a7f19adb-cc58-41b1-94ce-782dc255139b",
                        "name": "protocol2",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-group-membership-mapper"
                    },
                    {
                        "config": {
                            "access.token.claim": "true",
                            "claim.name": "protocol3",
                            "full.path": "true",
                            "id.token.claim": "false",
                            "userinfo.token.claim": "false"
                        },
                        "consentRequired": "false",
                        "id": "2103a559-185a-40f4-84ae-9ab311d5b812",
                        "name": "protocol3",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-group-membership-mapper"
                    },
                    {
                        "config": {
                            "access.token.claim": "true",
                            "claim.name": "protocol1",
                            "full.path": "true",
                            "id.token.claim": "true",
                            "userinfo.token.claim": "true"
                        },
                        "consentRequired": "false",
                        "id": "bbf6390f-e95f-4c20-882b-9dad328363b9",
                        "name": "protocol1",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-group-membership-mapper"
                    }]
            }]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 2)
        self.assertEqual(mock_create_clientscope.call_count, 1)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 0)
        self.assertEqual(mock_update_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 0)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 0)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_clientscope_with_protocolmappers(self):
        """Add a new authentication flow from copy of an other flow"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_username': 'admin',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'realm': 'realm-name',
            'state': 'present',
            'name': 'my-new-kc-clientscope',
            'protocolMappers': [
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'false',
                        'id.token.claim': 'false',
                        'access.token.claim': 'false',
                        'userinfo.token.claim': 'false',
                        'claim.name': 'protocol1_updated',
                    },
                    'name': 'protocol1',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'true',
                        'id.token.claim': 'false',
                        'access.token.claim': 'false',
                        'userinfo.token.claim': 'false',
                        'claim.name': 'protocol2_updated',
                    },
                    'name': 'protocol2',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
                {
                    'protocol': 'openid-connect',
                    'config': {
                        'full.path': 'true',
                        'id.token.claim': 'true',
                        'access.token.claim': 'true',
                        'userinfo.token.claim': 'true',
                        'claim.name': 'protocol3_updated',
                    },
                    'name': 'protocol3',
                    'protocolMapper': 'oidc-group-membership-mapper',
                },
            ]
        }
        return_value_get_clientscope_by_name = [{
            "attributes": {},
            "id": "890ec72e-fe1d-4308-9f27-485ef7eaa182",
            "name": "my-new-kc-clientscope",
            "protocolMappers": [
                {
                    "config": {
                        "access.token.claim": "true",
                        "claim.name": "groups",
                        "full.path": "true",
                        "id.token.claim": "true",
                        "userinfo.token.claim": "true"
                    },
                    "consentRequired": "false",
                    "id": "e077007a-367a-444f-91ef-70277a1d868d",
                    "name": "groups",
                    "protocol": "saml",
                    "protocolMapper": "oidc-group-membership-mapper"
                },
                {
                    "config": {
                        "access.token.claim": "true",
                        "claim.name": "groups",
                        "full.path": "true",
                        "id.token.claim": "true",
                        "userinfo.token.claim": "true"
                    },
                    "consentRequired": "false",
                    "id": "06c518aa-c627-43cc-9a82-d8467b508d34",
                    "name": "groups",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-group-membership-mapper"
                },
                {
                    "config": {
                        "access.token.claim": "true",
                        "claim.name": "groups",
                        "full.path": "true",
                        "id.token.claim": "true",
                        "userinfo.token.claim": "true"
                    },
                    "consentRequired": "false",
                    "id": "1d03c557-d97e-40f4-ac35-6cecd74ea70d",
                    "name": "groups",
                    "protocol": "wsfed",
                    "protocolMapper": "oidc-group-membership-mapper"
                }
            ]
        }]
        return_value_get_clientscope_by_clientscopeid = [{
            "attributes": {},
            "id": "2286032f-451e-44d5-8be6-e45aac7983a1",
            "name": "my-new-kc-clientscope",
            "protocolMappers": [
                {
                    "config": {
                        "access.token.claim": "true",
                        "claim.name": "protocol1_updated",
                        "full.path": "true",
                        "id.token.claim": "false",
                        "userinfo.token.claim": "false"
                    },
                    "consentRequired": "false",
                    "id": "a7f19adb-cc58-41b1-94ce-782dc255139b",
                    "name": "protocol2",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-group-membership-mapper"
                },
                {
                    "config": {
                        "access.token.claim": "true",
                        "claim.name": "protocol1_updated",
                        "full.path": "true",
                        "id.token.claim": "false",
                        "userinfo.token.claim": "false"
                    },
                    "consentRequired": "false",
                    "id": "2103a559-185a-40f4-84ae-9ab311d5b812",
                    "name": "protocol3",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-group-membership-mapper"
                },
                {
                    "config": {
                        "access.token.claim": "false",
                        "claim.name": "protocol1_updated",
                        "full.path": "false",
                        "id.token.claim": "false",
                        "userinfo.token.claim": "false"
                    },
                    "consentRequired": "false",
                    "id": "bbf6390f-e95f-4c20-882b-9dad328363b9",
                    "name": "protocol1",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-group-membership-mapper"
                }
            ]
        }]

        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_clientscope_by_name=return_value_get_clientscope_by_name,
                                    get_clientscope_by_clientscopeid=return_value_get_clientscope_by_clientscopeid) \
                    as (mock_get_clientscope_by_name, mock_get_clientscope_by_clientscopeid, mock_create_clientscope,
                        mock_update_clientscope, mock_get_clientscope_protocolmapper_by_name,
                        mock_update_clientscope_protocolmappers,
                        mock_create_clientscope_protocolmapper, mock_delete_clientscope):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify number of call on each mock
        self.assertEqual(mock_get_clientscope_by_name.call_count, 1)
        self.assertEqual(mock_create_clientscope.call_count, 0)
        self.assertEqual(mock_get_clientscope_by_clientscopeid.call_count, 1)
        self.assertEqual(mock_update_clientscope.call_count, 1)
        self.assertEqual(mock_get_clientscope_protocolmapper_by_name.call_count, 3)
        self.assertEqual(mock_update_clientscope_protocolmappers.call_count, 3)
        self.assertEqual(mock_create_clientscope_protocolmapper.call_count, 0)
        self.assertEqual(mock_delete_clientscope.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

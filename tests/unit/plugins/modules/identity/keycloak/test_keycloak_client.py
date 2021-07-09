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

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_client

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_client_by_clientid=None, get_client_by_id=None, update_client=None, create_client=None,
                       delete_client=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_client.KeycloakAPI
    with patch.object(obj, 'get_client_by_clientid', side_effect=get_client_by_clientid) as mock_get_client_by_clientid:
        with patch.object(obj, 'get_client_by_id', side_effect=get_client_by_id) as mock_get_client_by_id:
            with patch.object(obj, 'create_client', side_effect=create_client) as mock_create_client:
                with patch.object(obj, 'update_client', side_effect=update_client) as mock_update_client:
                    with patch.object(obj, 'delete_client', side_effect=delete_client) as mock_delete_client:
                        yield mock_get_client_by_clientid, mock_get_client_by_id, mock_create_client, mock_update_client, mock_delete_client


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


class TestKeycloakRealm(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealm, self).setUp()
        self.module = keycloak_client

    def test_authentication_flow_binding_overrides_feature(self):
        """Add a new realm"""

        module_args = {
            'auth_keycloak_url': 'https: // auth.example.com / auth',
            'token': '{{ access_token }}',
            'state': 'present',
            'realm': 'master',
            'client_id': 'test',
            'authentication_flow_binding_overrides': {
                'browser': '4c90336b-bf1d-4b87-916d-3677ba4e5fbb'
            }
        }
        return_value_get_client_by_clientid = [
            None,
            {
                "authenticationFlowBindingOverrides": {
                    "browser": "f9502b6d-d76a-4efe-8331-2ddd853c9f9c"
                },
                "clientId": "onboardingid",
                "enabled": "true",
                "protocol": "openid-connect",
                "redirectUris": [
                    "*"
                ]
            }
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_client_by_clientid=return_value_get_client_by_clientid) \
                    as (mock_get_client_by_clientid, mock_get_client_by_id, mock_create_client, mock_update_client, mock_delete_client):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_client_by_clientid.call_count, 2)
        self.assertEqual(mock_get_client_by_id.call_count, 0)
        self.assertEqual(mock_create_client.call_count, 1)
        self.assertEqual(mock_update_client.call_count, 0)
        self.assertEqual(mock_delete_client.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_realm_info

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_realm_info_by_id):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_realm_info.KeycloakAPI
    with patch.object(obj, 'get_realm_info_by_id', side_effect=get_realm_info_by_id) as mock_get_realm_info_by_id:
        yield mock_get_realm_info_by_id


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


class TestKeycloakRealmRole(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealmRole, self).setUp()
        self.module = keycloak_realm_info

    def test_get_public_info(self):
        """Get realm public info"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'realm': 'my-realm',
        }
        return_value = [
            None,
            {
                "realm": "my-realm",
                "public_key": "MIIBIjANBgkqhkiG9w0BAQEF...",
                "token-service": "https://auth.mock.com/auth/realms/my-realm/protocol/openid-connect",
                "account-service": "https://auth.mock.com/auth/realms/my-realm/account",
                "tokens-not-before": 0,
            }
        ]

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_realm_info_by_id=return_value) \
                    as (mock_get_realm_info_by_id):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_get_realm_info_by_id.mock_calls), 1)


if __name__ == '__main__':
    unittest.main()

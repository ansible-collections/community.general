# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.identity.keycloak import keycloak_default_group

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(create_default_group, delete_default_group=None):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_default_group.KeycloakAPI
    with patch.object(obj, 'create_default_group', side_effect=create_default_group) as mock_create_default_group:
        with patch.object(obj, 'delete_default_group', side_effect=delete_default_group) as mock_delete_default_group:
            yield mock_create_default_group, mock_delete_default_group


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


class TestKeycloakDefaultGroup(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakDefaultGroup, self).setUp()
        self.module = keycloak_default_group

    def test_create_default_group(self):
        """Add a default group"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'state': 'present',
            'realm': 'my-realm',
            'id': 'my-default-group',
        }
        return_value = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(create_default_group=return_value, delete_default_group=return_value) \
                    as (mock_create_default_group, mock_delete_default_group):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_create_default_group.mock_calls), 1)
        self.assertEqual(len(mock_delete_default_group.mock_calls), 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_default_group(self):
        """Remove a default group"""

        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'auth_password': 'admin',
            'auth_realm': 'master',
            'auth_username': 'admin',
            'auth_client_id': 'admin-cli',
            'validate_certs': True,
            'state': 'absent',
            'realm': 'my-realm',
            'id': 'my-default-group',
        }
        return_value = [None]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(create_default_group=return_value, delete_default_group=return_value) \
                    as (mock_create_default_group, mock_delete_default_group):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(len(mock_create_default_group.mock_calls), 0)
        self.assertEqual(len(mock_delete_default_group.mock_calls), 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()

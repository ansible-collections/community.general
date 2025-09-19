# Python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import keycloak_realm_localization

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_localization_values=None, set_localization_value=None, delete_localization_value=None):
    """
    Patch KeycloakAPI methods used by the module under test.
    """
    obj = keycloak_realm_localization.KeycloakAPI
    with patch.object(obj, 'get_localization_values', side_effect=get_localization_values) as mock_get_values:
        with patch.object(obj, 'set_localization_value', side_effect=set_localization_value) as mock_set_value:
            with patch.object(obj, 'delete_localization_value', side_effect=delete_localization_value) as mock_del_value:
                yield mock_get_values, mock_set_value, mock_del_value


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
        'http://keycloak.url/auth/realms/master/protocol/openid-connect/token': create_wrapper('{"access_token": "alongtoken"}'),
    }
    return patch(
        'ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url',
        side_effect=build_mocked_request(count(), token_response),
        autospec=True
    )


class TestKeycloakRealmLocalization(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakRealmLocalization, self).setUp()
        self.module = keycloak_realm_localization

    def test_present_no_change_in_sync(self):
        """Desired overrides already match, no change."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'present',
            'overrides': [
                {'key': 'greeting', 'value': 'Hello'},
                {'key': 'farewell', 'value': 'Bye'},
            ],
        }
        # get_localization_values is called twice: before and after
        return_value_get_localization_values = [
            {'greeting': 'Hello', 'farewell': 'Bye'},
            {'greeting': 'Hello', 'farewell': 'Bye'},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) \
                        as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 2)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]['changed'], False)

    def test_present_creates_updates_and_deletes(self):
        """Create missing, update differing, and delete extra overrides."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'present',
            'overrides': [
                {'key': 'a', 'value': '1-new'},  # update
                {'key': 'c', 'value': '3'},      # create
            ],
        }
        # Before: a=1, b=2; After: a=1-new, c=3
        return_value_get_localization_values = [
            {'a': '1', 'b': '2'},
            {'a': '1-new', 'c': '3'},
        ]
        return_value_set = [None, None]
        return_value_delete = [None]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                        get_localization_values=return_value_get_localization_values,
                        set_localization_value=return_value_set,
                        delete_localization_value=return_value_delete,
                ) as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 2)
        # One delete for 'b'
        self.assertEqual(mock_del_value.call_count, 1)
        # Two set calls: update 'a', create 'c'
        self.assertEqual(mock_set_value.call_count, 2)
        self.assertIs(exec_info.exception.args[0]['changed'], True)

    def test_present_check_mode_only_reports(self):
        """Check mode: report changes, do not call API mutators."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'present',
            'overrides': [
                {'key': 'x', 'value': '1'},  # change
                {'key': 'y', 'value': '2'},  # create
            ],
            '_ansible_check_mode': True,  # signal for readers; set_module_args is what matters
        }
        return_value_get_localization_values = [
            {'x': '0'},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) \
                        as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Only read current values
        self.assertEqual(mock_get_values.call_count, 1)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]['changed'], True)
        self.assertIn('would be updated', exec_info.exception.args[0]['msg'])

    def test_absent_deletes_all(self):
        """Remove all overrides when present."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'absent',
        }
        return_value_get_localization_values = [
            {'k1': 'v1', 'k2': 'v2'},
        ]
        return_value_delete = [None, None]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                        get_localization_values=return_value_get_localization_values,
                        delete_localization_value=return_value_delete,
                ) as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 1)
        self.assertEqual(mock_del_value.call_count, 2)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]['changed'], True)

    def test_absent_idempotent_when_nothing_to_delete(self):
        """No change when locale has no overrides."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'absent',
        }
        return_value_get_localization_values = [
            {},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) \
                        as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 1)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]['changed'], False)

    def test_present_missing_value_validation(self):
        """Validation error when state=present and value is missing."""
        module_args = {
            'auth_keycloak_url': 'http://keycloak.url/auth',
            'token': '{{ access_token }}',
            'parent_id': 'my-realm',
            'locale': 'en',
            'state': 'present',
            'overrides': [
                {'key': 'greeting', 'value': None},
            ],
        }

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api() \
                        as (_mock_get_values, _mock_set_value, _mock_del_value):
                    with self.assertRaises(AnsibleFailJson) as exec_info:
                        self.module.main()

        self.assertIn("requires 'value' for keys", exec_info.exception.args[0]['msg'])


if __name__ == '__main__':
    unittest.main()
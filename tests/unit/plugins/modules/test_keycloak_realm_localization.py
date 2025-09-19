# Copyright Jakub Danek <danek.ja@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from io import StringIO
from itertools import count
from unittest.mock import patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import keycloak_realm_localization


@contextmanager
def patch_keycloak_api(get_localization_values=None, set_localization_value=None, delete_localization_value=None):
    """
    Patch KeycloakAPI methods used by the module under test.
    """
    obj = keycloak_realm_localization.KeycloakAPI
    with patch.object(obj, "get_localization_values", side_effect=get_localization_values) as mock_get_values:
        with patch.object(obj, "set_localization_value", side_effect=set_localization_value) as mock_set_value:
            with patch.object(
                obj, "delete_localization_value", side_effect=delete_localization_value
            ) as mock_del_value:
                yield mock_get_values, mock_set_value, mock_del_value


def get_response(object_with_future_response, method, get_id_call_count):
    if callable(object_with_future_response):
        return object_with_future_response()
    if isinstance(object_with_future_response, dict):
        return get_response(object_with_future_response[method], method, get_id_call_count)
    if isinstance(object_with_future_response, list):
        call_number = next(get_id_call_count)
        return get_response(object_with_future_response[call_number], method, get_id_call_count)
    return object_with_future_response


def build_mocked_request(get_id_user_count, response_dict):
    def _mocked_requests(*args, **kwargs):
        url = args[0]
        method = kwargs["method"]
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
        "http://keycloak.url/auth/realms/master/protocol/openid-connect/token": create_wrapper(
            '{"access_token": "alongtoken"}'
        ),
    }
    return patch(
        "ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url",
        side_effect=build_mocked_request(count(), token_response),
        autospec=True,
    )


class TestKeycloakRealmLocalization(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = keycloak_realm_localization

    def test_present_no_change_in_sync(self):
        """Desired overrides already match, no change."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "present",
            "overrides": [
                {"key": "greeting", "value": "Hello"},
                {"key": "farewell", "value": "Bye"},
            ],
        }
        # get_localization_values is called twice: before and after
        return_value_get_localization_values = [
            {"greeting": "Hello", "farewell": "Bye"},
            {"greeting": "Hello", "farewell": "Bye"},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) as (
                    mock_get_values,
                    mock_set_value,
                    mock_del_value,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 2)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]["changed"], False)

    def test_present_check_mode_only_reports(self):
        """Check mode: report changes, do not call API mutators."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "present",
            "overrides": [
                {"key": "x", "value": "1"},  # change
                {"key": "y", "value": "2"},  # create
            ],
            "_ansible_check_mode": True,  # signal for readers; set_module_args is what matters
        }
        return_value_get_localization_values = [
            {"x": "0"},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) as (
                    mock_get_values,
                    mock_set_value,
                    mock_del_value,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        # Only read current values
        self.assertEqual(mock_get_values.call_count, 1)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]["changed"], True)
        self.assertIn("would be updated", exec_info.exception.args[0]["msg"])

    def test_absent_idempotent_when_nothing_to_delete(self):
        """No change when locale has no overrides."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "absent",
        }
        return_value_get_localization_values = [
            {},
        ]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(get_localization_values=return_value_get_localization_values) as (
                    mock_get_values,
                    mock_set_value,
                    mock_del_value,
                ):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 1)
        self.assertEqual(mock_del_value.call_count, 0)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]["changed"], False)

    def test_present_value_defaults_to_empty_string(self):
        """When value is omitted, it defaults to empty string."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "present",
            "overrides": [
                {"key": "greeting"},  # value omitted, should default to ""
            ],
        }
        # Before: greeting="Hello"; After: greeting="" (empty string)
        return_value_get_localization_values = [
            {"greeting": "Hello"},
            {"greeting": ""},
        ]
        return_value_set = [None]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_localization_values=return_value_get_localization_values,
                    set_localization_value=return_value_set,
                ) as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 2)
        self.assertEqual(mock_del_value.call_count, 0)
        # One set call to update 'greeting' to empty string
        self.assertEqual(mock_set_value.call_count, 1)
        self.assertIs(exec_info.exception.args[0]["changed"], True)

    def test_present_append_true_preserves_unspecified_keys(self):
        """With append=True, only modify specified keys, preserve others."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "present",
            "force": False,
            "overrides": [
                {"key": "a", "value": "1-updated"},  # update existing
                {"key": "c", "value": "3"},  # create new
            ],
        }
        # Before: a=1, b=2; After: a=1-updated, b=2, c=3 (b is preserved)
        return_value_get_localization_values = [
            {"a": "1", "b": "2"},
            {"a": "1-updated", "b": "2", "c": "3"},
        ]
        return_value_set = [None, None]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_localization_values=return_value_get_localization_values,
                    set_localization_value=return_value_set,
                ) as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 2)
        # No deletes - key 'b' should be preserved
        self.assertEqual(mock_del_value.call_count, 0)
        # Two set calls: update 'a', create 'c'
        self.assertEqual(mock_set_value.call_count, 2)
        self.assertIs(exec_info.exception.args[0]["changed"], True)

    def test_present_append_false_removes_unspecified_keys(self):
        """With append=False, create new, update existing, and delete unspecified keys."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "present",
            "force": True,
            "overrides": [
                {"key": "a", "value": "1-updated"},  # update
                {"key": "c", "value": "3"},  # create
            ],
        }
        # Before: a=1, b=2; After: a=1-updated, c=3 (b is removed)
        return_value_get_localization_values = [
            {"a": "1", "b": "2"},
            {"a": "1-updated", "c": "3"},
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
        self.assertIs(exec_info.exception.args[0]["changed"], True)

    def test_absent_append_true_removes_only_specified_keys(self):
        """With state=absent and append=True, remove only specified keys."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "absent",
            "force": False,
            "overrides": [
                {"key": "a"},
            ],
        }
        # Before: a=1, b=2; Remove only 'a', keep 'b'
        return_value_get_localization_values = [
            {"a": "1", "b": "2"},
        ]
        return_value_delete = [None]

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(
                    get_localization_values=return_value_get_localization_values,
                    delete_localization_value=return_value_delete,
                ) as (mock_get_values, mock_set_value, mock_del_value):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        self.assertEqual(mock_get_values.call_count, 1)
        # One delete for 'a' only
        self.assertEqual(mock_del_value.call_count, 1)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]["changed"], True)

    def test_absent_append_false_removes_all_keys(self):
        """With state=absent and append=False, remove all keys."""
        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "parent_id": "my-realm",
            "locale": "en",
            "state": "absent",
            "force": True,
        }
        # Before: a=1, b=2; Remove all
        return_value_get_localization_values = [
            {"a": "1", "b": "2"},
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
        # Two deletes for 'a' and 'b'
        self.assertEqual(mock_del_value.call_count, 2)
        self.assertEqual(mock_set_value.call_count, 0)
        self.assertIs(exec_info.exception.args[0]["changed"], True)

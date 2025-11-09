# Copyright (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from contextlib import contextmanager
from unittest.mock import patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import (
    keycloak_user_execute_actions_email as module_under_test,
)

from io import StringIO
from itertools import count


def _create_wrapper(text_as_string):
    def _wrapper():
        return StringIO(text_as_string)

    return _wrapper


def _build_mocked_request(get_id_user_count, response_dict):
    def _mocked_requests(*args, **kwargs):
        url = args[0]
        future_response = response_dict.get(url, None)
        if callable(future_response):
            return future_response()
        return future_response

    return _mocked_requests


def _mock_good_connection():
    token_response = {
        "http://keycloak.url/auth/realms/master/protocol/openid-connect/token": _create_wrapper(
            '{"access_token": "alongtoken"}'
        )
    }
    return patch(
        "ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url",
        side_effect=_build_mocked_request(count(), token_response),
        autospec=True,
    )


@contextmanager
def patch_keycloak_api(get_user_by_username=None, send_execute_actions_email=None):
    obj = module_under_test.KeycloakAPI
    with patch.object(obj, "get_user_by_username", side_effect=get_user_by_username) as m_get_user:
        with patch.object(obj, "send_execute_actions_email", side_effect=send_execute_actions_email) as m_send:
            yield m_get_user, m_send


class TestKeycloakUserExecuteActionsEmail(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = module_under_test

    def test_default_action_with_username(self):
        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "realm": "master",
            "username": "jdoe",
        }

        with set_module_args(module_args):
            with _mock_good_connection():
                with patch_keycloak_api(
                    get_user_by_username=lambda **kwargs: {"id": "uid-123", "username": "jdoe"},
                    send_execute_actions_email=lambda **kwargs: None,
                ) as (m_get_user, m_send):
                    with self.assertRaises(AnsibleExitJson) as result:
                        self.module.main()

        data = result.exception.args[0]
        self.assertTrue(data["changed"])
        self.assertEqual(data["user_id"], "uid-123")
        self.assertEqual(data["actions"], ["UPDATE_PASSWORD"])
        self.assertEqual(len(m_get_user.mock_calls), 1)
        self.assertEqual(len(m_send.mock_calls), 1)

    def test_user_not_found(self):
        module_args = {
            "auth_client_id": "admin-cli",
            "auth_keycloak_url": "http://keycloak.url/auth",
            "auth_password": "admin",
            "auth_realm": "master",
            "auth_username": "admin",
            "realm": "master",
            "username": "missing",
        }

        with set_module_args(module_args):
            with _mock_good_connection():
                with patch_keycloak_api(
                    get_user_by_username=lambda **kwargs: None,
                    send_execute_actions_email=lambda **kwargs: None,
                ):
                    with self.assertRaises(AnsibleFailJson) as result:
                        self.module.main()
        data = result.exception.args[0]
        self.assertIn("User 'missing' not found", data["msg"])


if __name__ == "__main__":
    unittest.main()

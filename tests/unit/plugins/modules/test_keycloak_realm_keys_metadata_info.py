# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from contextlib import contextmanager
from io import StringIO
from itertools import count
from unittest.mock import patch

from ansible_collections.community.general.plugins.modules import keycloak_realm_keys_metadata_info
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)


@contextmanager
def patch_keycloak_api(side_effect):
    """Mock context manager for patching the methods in PwPolicyIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """

    obj = keycloak_realm_keys_metadata_info.KeycloakAPI
    with patch.object(obj, "get_realm_keys_metadata_by_id", side_effect=side_effect) as obj_mocked:
        yield obj_mocked


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


class TestKeycloakRealmRole(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = keycloak_realm_keys_metadata_info

    def test_get_public_info(self):
        """Get realm public info"""

        module_args = {
            "auth_keycloak_url": "http://keycloak.url/auth",
            "token": "{{ access_token }}",
            "realm": "my-realm",
        }
        return_value = [
            {
                "active": {
                    "AES": "aba3778d-d69d-4240-a578-a30720dbd3ca",
                    "HS512": "6e4fe29d-a7e4-472b-a348-298d8ae45dcc",
                    "RS256": "jaON84xLYg2fsKiV4p3wZag_S8MTjAp-dkpb1kRqzEs",
                    "RSA-OAEP": "3i_GikMqBBxtqhWXwpucxMvwl55jYlhiNIvxDTgNAEk",
                },
                "keys": [
                    {
                        "algorithm": "HS512",
                        "kid": "6e4fe29d-a7e4-472b-a348-298d8ae45dcc",
                        "providerId": "225dbe0b-3fc4-4e0d-8479-90a0cbc8adf7",
                        "providerPriority": 100,
                        "status": "ACTIVE",
                        "type": "OCT",
                        "use": "SIG",
                    },
                    {
                        "algorithm": "RS256",
                        "certificate": "MIIC…",
                        "kid": "jaON84xLYg2fsKiV4p3wZag_S8MTjAp-dkpb1kRqzEs",
                        "providerId": "98c1ebeb-c690-4c5c-8b32-81bebe264cda",
                        "providerPriority": 100,
                        "publicKey": "MIIB…",
                        "status": "ACTIVE",
                        "type": "RSA",
                        "use": "SIG",
                        "validTo": 2034748624000,
                    },
                    {
                        "algorithm": "AES",
                        "kid": "aba3778d-d69d-4240-a578-a30720dbd3ca",
                        "providerId": "99c70057-9b8d-4177-a83c-de2d081139e8",
                        "providerPriority": 100,
                        "status": "ACTIVE",
                        "type": "OCT",
                        "use": "ENC",
                    },
                    {
                        "algorithm": "RSA-OAEP",
                        "certificate": "MIIC…",
                        "kid": "3i_GikMqBBxtqhWXwpucxMvwl55jYlhiNIvxDTgNAEk",
                        "providerId": "ab3de3fb-a32d-4be8-8324-64aa48d14c36",
                        "providerPriority": 100,
                        "publicKey": "MIIB…",
                        "status": "ACTIVE",
                        "type": "RSA",
                        "use": "ENC",
                        "validTo": 2034748625000,
                    },
                ],
            }
        ]

        # Run the module

        with set_module_args(module_args):
            with mock_good_connection():
                with patch_keycloak_api(side_effect=return_value) as (mock_get_realm_keys_metadata_by_id):
                    with self.assertRaises(AnsibleExitJson) as exec_info:
                        self.module.main()

        result = exec_info.exception.args[0]
        self.assertIs(result["changed"], False)
        self.assertEqual(result["msg"], "Get realm keys metadata successful for ID my-realm")
        self.assertEqual(result["keys_metadata"], return_value[0])

        self.assertEqual(len(mock_get_realm_keys_metadata_by_id.mock_calls), 1)


if __name__ == "__main__":
    unittest.main()

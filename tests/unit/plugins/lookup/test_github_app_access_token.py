# Copyright (c) 2023, Poh Wei Sheng <weisheng-p@hotmail.sg>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import (
    patch,
    MagicMock,
    mock_open,
)

from ansible.plugins.loader import lookup_loader

ENCODE_RESULT = "Foobar"
PRIVATE_KEY = "private_key"


class MockJWT(MagicMock):
    def encode(self, payload, key, alg):
        return ENCODE_RESULT


class serialization(MagicMock):
    def load_pem_private_key(self, key_bytes, password):
        return PRIVATE_KEY


class MockResponse(MagicMock):
    response_token = "Bar"

    def read(self):
        return json.dumps(
            {
                "token": self.response_token,
            }
        ).encode("utf-8")


class TestLookupModule(unittest.TestCase):
    def test_get_token_with_file_with_pyjwt(self):
        pyjwt = types.ModuleType("jwt")
        pyjwt.encode = MagicMock(return_value=ENCODE_RESULT)
        with (
            patch.dict(sys.modules, {"jwt": pyjwt}),
            patch.multiple(
                "ansible_collections.community.general.plugins.lookup.github_app_access_token",
                open=mock_open(read_data="foo_bar"),
                open_url=MagicMock(return_value=MockResponse()),
                HAS_JWT=True,
                HAS_CRYPTOGRAPHY=True,
                serialization=serialization(),
            ),
        ):
            lookup = lookup_loader.get("community.general.github_app_access_token")
            self.assertListEqual(
                [MockResponse.response_token],
                lookup.run([], key_path="key", app_id="app_id", installation_id="installation_id", token_expiry=600),
            )

    def test_get_token_with_fact_with_pyjwt(self):
        pyjwt = types.ModuleType("jwt")
        pyjwt.encode = MagicMock(return_value=ENCODE_RESULT)
        with (
            patch.dict(sys.modules, {"jwt": pyjwt}),
            patch.multiple(
                "ansible_collections.community.general.plugins.lookup.github_app_access_token",
                open=mock_open(read_data="foo_bar"),
                open_url=MagicMock(return_value=MockResponse()),
                HAS_JWT=True,
                HAS_CRYPTOGRAPHY=True,
                serialization=serialization(),
            ),
        ):
            lookup = lookup_loader.get("community.general.github_app_access_token")
            self.assertListEqual(
                [MockResponse.response_token],
                lookup.run(
                    [], app_id="app_id", installation_id="installation_id", private_key="foo_bar", token_expiry=600
                ),
            )

    def test_get_token_with_python_jwt(self):
        python_jwt = types.ModuleType("jwt")
        python_jwt.JWT = MagicMock()
        python_jwt.jwk_from_pem = MagicMock(return_value="private_key")
        python_jwt.jwt_instance = MockJWT()
        with (
            patch.dict(sys.modules, {"jwt": python_jwt}),
            patch.multiple(
                "ansible_collections.community.general.plugins.lookup.github_app_access_token",
                open=mock_open(read_data="foo_bar"),
                open_url=MagicMock(return_value=MockResponse()),
                HAS_JWT=True,
            ),
        ):
            lookup = lookup_loader.get("community.general.github_app_access_token")
            self.assertListEqual(
                [MockResponse.response_token],
                lookup.run([], key_path="key", app_id="app_id", installation_id="installation_id", token_expiry=600),
            )

    def test_get_token_with_fact_with_python_jwt(self):
        python_jwt = types.ModuleType("jwt")
        python_jwt.JWT = MagicMock()
        python_jwt.jwk_from_pem = MagicMock(return_value="private_key")
        python_jwt.jwt_instance = MockJWT()
        with (
            patch.dict(sys.modules, {"jwt": python_jwt}),
            patch.multiple(
                "ansible_collections.community.general.plugins.lookup.github_app_access_token",
                open=mock_open(read_data="foo_bar"),
                open_url=MagicMock(return_value=MockResponse()),
                HAS_JWT=True,
            ),
        ):
            lookup = lookup_loader.get("community.general.github_app_access_token")
            self.assertListEqual(
                [MockResponse.response_token],
                lookup.run(
                    [], app_id="app_id", installation_id="installation_id", private_key="foo_bar", token_expiry=600
                ),
            )

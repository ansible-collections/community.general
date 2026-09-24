# Copyright (c) 2023, Poh Wei Sheng <weisheng-p@hotmail.sg>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import (
    MagicMock,
    mock_open,
    patch,
)

import pytest
from ansible.errors import AnsibleOptionsError
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


def test_get_token_with_client_id_does_not_warn_deprecated(mocker):
    pyjwt = types.ModuleType("jwt")
    pyjwt.encode = MagicMock(return_value=ENCODE_RESULT)
    module = "ansible_collections.community.general.plugins.lookup.github_app_access_token"
    mocker.patch.dict(sys.modules, {"jwt": pyjwt})
    mocker.patch.multiple(
        module,
        open=mock_open(read_data="foo_bar"),
        open_url=MagicMock(return_value=MockResponse()),
        HAS_JWT=True,
        HAS_CRYPTOGRAPHY=True,
        serialization=serialization(),
    )
    deprecated = mocker.patch(f"{module}.display.deprecated")

    lookup = lookup_loader.get("community.general.github_app_access_token")
    result = lookup.run([], key_path="key", client_id="client_id", installation_id="installation_id", token_expiry=600)

    assert result == [MockResponse.response_token]
    deprecated.assert_not_called()


def test_get_token_with_app_id_warns_deprecated(mocker):
    pyjwt = types.ModuleType("jwt")
    pyjwt.encode = MagicMock(return_value=ENCODE_RESULT)
    module = "ansible_collections.community.general.plugins.lookup.github_app_access_token"
    mocker.patch.dict(sys.modules, {"jwt": pyjwt})
    mocker.patch.multiple(
        module,
        open=mock_open(read_data="foo_bar"),
        open_url=MagicMock(return_value=MockResponse()),
        HAS_JWT=True,
        HAS_CRYPTOGRAPHY=True,
        serialization=serialization(),
    )
    deprecated = mocker.patch(f"{module}.display.deprecated")

    lookup = lookup_loader.get("community.general.github_app_access_token")
    result = lookup.run([], key_path="key", app_id="app_id", installation_id="installation_id", token_expiry=600)

    assert result == [MockResponse.response_token]
    deprecated.assert_called_once_with(
        mocker.ANY,
        version="15.0.0",
        collection_name="community.general",
    )


def test_run_requires_one_of_app_id_or_client_id():
    lookup = lookup_loader.get("community.general.github_app_access_token")
    with pytest.raises(AnsibleOptionsError, match="One of app_id or client_id is required"):
        lookup.run([], key_path="key", installation_id="installation_id")


def test_run_app_id_and_client_id_are_mutually_exclusive():
    lookup = lookup_loader.get("community.general.github_app_access_token")
    with pytest.raises(AnsibleOptionsError, match="app_id and client_id are mutually exclusive"):
        lookup.run(
            [],
            key_path="key",
            app_id="app_id",
            client_id="client_id",
            installation_id="installation_id",
        )

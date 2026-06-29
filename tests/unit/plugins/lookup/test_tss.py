# Copyright (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

from unittest import TestCase
from unittest.mock import (
    DEFAULT,
    MagicMock,
    patch,
)

from ansible.plugins.loader import lookup_loader

from ansible_collections.community.general.plugins.lookup import tss

TSS_IMPORT_PATH = "ansible_collections.community.general.plugins.lookup.tss"


def make_absolute(name):
    return f"{TSS_IMPORT_PATH}.{name}"


class SecretServerError(Exception):
    def __init__(self):
        self.message = ""


class SecretServerClientError(SecretServerError):
    pass


class MockSecretServer(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class MockFaultySecretServer(MagicMock):
    def get_secret_json(self, path):
        raise SecretServerError


@patch(make_absolute("SecretServer"), MockSecretServer())
class TestTSSClient(TestCase):
    def setUp(self):
        self.server_params = {
            "base_url": "",
            "username": "",
            "domain": "",
            "password": "",
            "api_path_uri": "",
            "token_path_uri": "",
        }

    def test_from_params(self):
        with patch(make_absolute("HAS_TSS_AUTHORIZER"), False):
            self.assert_client_version("v0")

            with patch.dict(self.server_params, {"domain": "foo"}):
                with self.assertRaises(tss.AnsibleError):
                    self._get_client()

        with patch.multiple(
            TSS_IMPORT_PATH,
            HAS_TSS_AUTHORIZER=True,
            PasswordGrantAuthorizer=DEFAULT,
            DomainPasswordGrantAuthorizer=DEFAULT,
        ):
            self.assert_client_version("v1")

            with patch.dict(self.server_params, {"domain": "foo"}):
                self.assert_client_version("v1")

    def assert_client_version(self, version):
        version_to_class = {"v0": tss.TSSClientV0, "v1": tss.TSSClientV1}

        client = self._get_client()
        self.assertIsInstance(client, version_to_class[version])

    def _get_client(self):
        return tss.TSSClient.from_params(**self.server_params)


class TestLookupModule(TestCase):
    VALID_TERMS = [1]
    INVALID_TERMS = ["foo"]

    def setUp(self):
        self.lookup = lookup_loader.get("community.general.tss")
        tss._client_cache.clear()
        self.addCleanup(tss._client_cache.clear)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=False, SecretServer=MockSecretServer)
    def test_missing_sdk(self):
        with self.assertRaises(tss.AnsibleError):
            self._run_lookup(self.VALID_TERMS)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_get_secret_json(self):
        with patch(make_absolute("SecretServer"), MockSecretServer):
            self.assertListEqual([MockSecretServer.RESPONSE], self._run_lookup(self.VALID_TERMS))

            with self.assertRaises(tss.AnsibleOptionsError):
                self._run_lookup(self.INVALID_TERMS)

        with patch(make_absolute("SecretServer"), MockFaultySecretServer):
            tss._client_cache.clear()
            with self.assertRaises(tss.AnsibleError):
                self._run_lookup(self.VALID_TERMS)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_client_cache_reuse(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(self.VALID_TERMS)
            self._run_lookup(self.VALID_TERMS)
            self.assertEqual(from_params.call_count, 1)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_cache_survives_plugin_reinstantiation(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        kwargs = {"base_url": "dummy", "username": "dummy", "password": "dummy"}
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self.lookup.run(self.VALID_TERMS, [], **kwargs)
            # A brand-new plugin instance (as ansible-core creates per invocation)
            # must reuse the module-level cache instead of building a new client.
            fresh = lookup_loader.get("community.general.tss")
            fresh.run(self.VALID_TERMS, [], **kwargs)
            self.assertEqual(from_params.call_count, 1)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_token_auth_is_not_cached(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(self.VALID_TERMS, base_url="dummy", token="token")
            self._run_lookup(self.VALID_TERMS, base_url="dummy", token="token")
            self.assertEqual(from_params.call_count, 2)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_cache_separates_clients_by_credential_identity(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(self.VALID_TERMS, base_url="dummy", username="alice", password="p")
            self._run_lookup(self.VALID_TERMS, base_url="dummy", username="bob", password="p")
            self.assertEqual(from_params.call_count, 2)
            self.assertEqual(len(tss._client_cache), 2)

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_token_path_source_auto_empties_token_path_uri(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(self.VALID_TERMS, base_url="dummy", username="u", password="p", token_path_source="auto")
            self.assertEqual(from_params.call_args.kwargs["token_path_uri"], "")

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_token_path_source_auto_overrides_explicit_token_path_uri(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(
                self.VALID_TERMS,
                base_url="dummy",
                username="u",
                password="p",
                token_path_source="auto",
                token_path_uri="/oauth2/token",
            )
            self.assertEqual(from_params.call_args.kwargs["token_path_uri"], "")

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_default_token_path_source_uses_configured_token_path_uri(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(
                self.VALID_TERMS,
                base_url="dummy",
                username="u",
                password="p",
                token_path_uri="/custom/token",
            )
            self.assertEqual(from_params.call_args.kwargs["token_path_uri"], "/custom/token")

    @patch.multiple(TSS_IMPORT_PATH, HAS_TSS_SDK=True, SecretServerError=SecretServerError)
    def test_token_path_source_partitions_cache(self):
        wrapper = MagicMock()
        wrapper.get_secret.return_value = "secret"
        with patch(make_absolute("TSSClient.from_params"), return_value=wrapper) as from_params:
            self._run_lookup(self.VALID_TERMS, base_url="dummy", username="u", password="p", token_path_source="auto")
            self._run_lookup(self.VALID_TERMS, base_url="dummy", username="u", password="p")
            self.assertEqual(from_params.call_count, 2)
            self.assertEqual(len(tss._client_cache), 2)

    @patch.multiple(
        TSS_IMPORT_PATH,
        HAS_TSS_SDK=True,
        HAS_SS_CLIENT_ERROR=True,
        SecretServerError=SecretServerError,
        SecretServerClientError=SecretServerClientError,
    )
    def test_retry_on_client_error_then_success(self):
        faulty = MagicMock()
        faulty.get_secret.side_effect = SecretServerClientError()
        good = MagicMock()
        good.get_secret.return_value = "ok"
        with patch(make_absolute("TSSClient.from_params"), side_effect=[faulty, good]) as from_params:
            self.assertListEqual(["ok"], self._run_lookup(self.VALID_TERMS))
            self.assertEqual(from_params.call_count, 2)

    @patch.multiple(
        TSS_IMPORT_PATH,
        HAS_TSS_SDK=True,
        HAS_SS_CLIENT_ERROR=True,
        SecretServerError=SecretServerError,
        SecretServerClientError=SecretServerClientError,
    )
    def test_retry_exhausted_raises(self):
        faulty1 = MagicMock()
        faulty1.get_secret.side_effect = SecretServerClientError()
        faulty2 = MagicMock()
        faulty2.get_secret.side_effect = SecretServerClientError()
        with patch(make_absolute("TSSClient.from_params"), side_effect=[faulty1, faulty2]) as from_params:
            with self.assertRaises(tss.AnsibleError):
                self._run_lookup(self.VALID_TERMS)
            self.assertEqual(from_params.call_count, 2)

    @patch.multiple(
        TSS_IMPORT_PATH,
        HAS_TSS_SDK=True,
        HAS_SS_CLIENT_ERROR=True,
        SecretServerError=SecretServerError,
        SecretServerClientError=SecretServerClientError,
    )
    def test_non_client_error_does_not_retry(self):
        faulty = MagicMock()
        faulty.get_secret.side_effect = SecretServerError()
        with patch(make_absolute("TSSClient.from_params"), side_effect=[faulty, MagicMock()]) as from_params:
            with self.assertRaises(tss.AnsibleError):
                self._run_lookup(self.VALID_TERMS)
            self.assertEqual(from_params.call_count, 1)

    @patch.multiple(
        TSS_IMPORT_PATH,
        HAS_TSS_SDK=True,
        HAS_SS_CLIENT_ERROR=False,
        SecretServerError=SecretServerError,
        SecretServerClientError=None,
    )
    def test_missing_client_error_symbol_does_not_retry(self):
        faulty = MagicMock()
        faulty.get_secret.side_effect = SecretServerClientError()
        with patch(make_absolute("TSSClient.from_params"), side_effect=[faulty, MagicMock()]) as from_params:
            with self.assertRaises(tss.AnsibleError):
                self._run_lookup(self.VALID_TERMS)
            self.assertEqual(from_params.call_count, 1)

    def _run_lookup(self, terms, variables=None, **kwargs):
        variables = variables or []
        kwargs = kwargs or {"base_url": "dummy", "username": "dummy", "password": "dummy"}

        return self.lookup.run(terms, variables, **kwargs)

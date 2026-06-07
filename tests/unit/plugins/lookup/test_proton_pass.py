# Copyright (c) 2026, Jean Khawand (@jeankhawand)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from ansible.errors import AnsibleLookupError, AnsibleOptionsError

from ansible_collections.community.general.plugins.lookup.proton_pass import (
    LookupModule,
    ProtonPassClient,
    ProtonPassCLIError,
    _parse_fields,
    _raise_item_error,
)

# ---------------------------------------------------------------------------
# Fixtures — representative pass-cli --output json payloads (v2.x schema)
# Each fixture mirrors the {"item": {...}} envelope returned by `pass-cli item view`.
# ---------------------------------------------------------------------------


def _make_item(type_key, type_data, extra_fields=None, extra_sections=None, note="", state="Active"):
    return {
        "item": {
            "content": {
                "title": "test_item",
                "note": note,
                "content": {type_key: type_data},
                "extra_fields": extra_fields or [],
                "extra_sections": extra_sections or [],
            },
            "state": state,
        }
    }


MOCK_LOGIN_ITEM = _make_item(
    "Login",
    {"email": "", "username": "", "password": "correct-horse-battery", "urls": [], "totp_uri": "", "passkeys": []},
    extra_fields=[
        {"name": "api_token", "content": {"Hidden": "token_value_abc"}},
        {"name": "backup_secret", "content": {"Hidden": "secure_value_1"}},
    ],
)

MOCK_SECTIONED_ITEM = _make_item(
    "Custom",
    {"sections": []},
    extra_sections=[
        {
            "section_name": "Credentials",
            "extra_fields": [
                {"name": "backup_secret", "content": {"Hidden": "secure_value_2"}},
                {"name": "storage_key", "content": {"Hidden": "secure_value_3"}},
            ],
        }
    ],
)

MOCK_NOTE_ITEM = _make_item("Custom", {"sections": []}, note="some free-text note")

MOCK_LOGIN_URLS_ITEM = _make_item(
    "Login",
    {
        "email": "user@example.com",
        "username": "user@example.com",
        "password": "secret",
        "totp_uri": "otpauth://totp/example?secret=JBSWY3DPEHPK3PXP",
        "urls": ["https://example.com", "https://app.example.com"],
        "passkeys": [],
    },
)

MOCK_CREDIT_CARD_ITEM = _make_item(
    "CreditCard",
    {
        "cardholder_name": "John Doe",
        "card_type": "Visa",
        "number": "4111111111111111",
        "verification_number": "123",
        "expiration_date": "2027-12",
        "pin": "1234",
    },
)

MOCK_WIFI_ITEM = _make_item(
    "Wifi",
    {"ssid": "HomeNetwork", "password": "wifipass123", "security": "WPA2", "sections": []},
)

MOCK_IDENTITY_ITEM = _make_item(
    "Identity",
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "+1234567890",
        "organization": "ACME",
        "city": "Springfield",
        "country_or_region": "US",
        "extra_personal_details": [
            {"name": "custom_personal", "content": {"Hidden": "personal_secret"}},
        ],
        "extra_address_details": [
            {"name": "custom_address", "content": {"Text": "123 Main St"}},
        ],
        "extra_contact_details": [],
        "extra_work_details": [],
        "extra_sections": [],
    },
)

MOCK_SSH_KEY_ITEM = _make_item(
    "SshKey",
    {
        "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nfake\n-----END OPENSSH PRIVATE KEY-----",
        "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFake deploy@host",
        "fingerprint": "SHA256:abc123fake",
        "key_type": "ed25519",
    },
)

MOCK_ALIAS_ITEM = _make_item(
    "Alias",
    None,
    extra_fields=[{"name": "aliased_email", "content": {"Text": "shopping.abc123@pm.me"}}],
)

MOCK_TRASHED_ITEM = _make_item(
    "Login",
    {"username": "x", "password": "y", "urls": [], "totp_uri": "", "passkeys": []},
    extra_fields=[{"name": "secret", "content": {"Hidden": "value"}}],
    state="Trashed",
)


# ---------------------------------------------------------------------------
# _parse_fields
# ---------------------------------------------------------------------------


class TestParseFields(unittest.TestCase):
    def test_login_item_with_extra_fields(self):
        fields = _parse_fields(MOCK_LOGIN_ITEM, "example_item")
        self.assertEqual(fields["api_token"], "token_value_abc")
        self.assertEqual(fields["backup_secret"], "secure_value_1")
        self.assertEqual(fields["password"], "correct-horse-battery")

    def test_sectioned_item(self):
        fields = _parse_fields(MOCK_SECTIONED_ITEM, "grouped_item")
        self.assertEqual(fields["backup_secret"], "secure_value_2")
        self.assertEqual(fields["storage_key"], "secure_value_3")

    def test_note_item(self):
        fields = _parse_fields(MOCK_NOTE_ITEM, "notes_item")
        self.assertEqual(fields["note"], "some free-text note")

    def test_empty_item_raises(self):
        empty = _make_item("Custom", {"sections": []})
        with self.assertRaises(AnsibleLookupError) as ctx:
            _parse_fields(empty, "empty_item")
        self.assertIn("empty_item", str(ctx.exception))

    def test_login_urls_returned_as_list(self):
        fields = _parse_fields(MOCK_LOGIN_URLS_ITEM, "web_login")
        self.assertEqual(fields["username"], "user@example.com")
        self.assertEqual(fields["password"], "secret")
        self.assertEqual(fields["totp_uri"], "otpauth://totp/example?secret=JBSWY3DPEHPK3PXP")
        self.assertEqual(fields["urls"], ["https://example.com", "https://app.example.com"])

    def test_credit_card_item(self):
        fields = _parse_fields(MOCK_CREDIT_CARD_ITEM, "my_visa")
        self.assertEqual(fields["cardholder_name"], "John Doe")
        self.assertEqual(fields["card_type"], "Visa")
        self.assertEqual(fields["number"], "4111111111111111")
        self.assertEqual(fields["verification_number"], "123")
        self.assertEqual(fields["expiration_date"], "2027-12")
        self.assertEqual(fields["pin"], "1234")

    def test_wifi_item(self):
        fields = _parse_fields(MOCK_WIFI_ITEM, "home_wifi")
        self.assertEqual(fields["ssid"], "HomeNetwork")
        self.assertEqual(fields["password"], "wifipass123")
        self.assertEqual(fields["security"], "WPA2")
        self.assertNotIn("username", fields)

    def test_identity_item(self):
        fields = _parse_fields(MOCK_IDENTITY_ITEM, "my_identity")
        self.assertEqual(fields["first_name"], "John")
        self.assertEqual(fields["last_name"], "Doe")
        self.assertEqual(fields["email"], "john@example.com")
        self.assertEqual(fields["organization"], "ACME")
        self.assertEqual(fields["city"], "Springfield")
        self.assertEqual(fields["country_or_region"], "US")

    def test_identity_sub_array_extra_fields(self):
        """Extra fields nested in Identity sub-arrays are merged into the result."""
        fields = _parse_fields(MOCK_IDENTITY_ITEM, "my_identity")
        self.assertEqual(fields["custom_personal"], "personal_secret")
        self.assertEqual(fields["custom_address"], "123 Main St")

    def test_ssh_key_item(self):
        fields = _parse_fields(MOCK_SSH_KEY_ITEM, "deploy_key")
        self.assertIn("-----BEGIN OPENSSH PRIVATE KEY-----", fields["private_key"])
        self.assertIn("ssh-ed25519", fields["public_key"])
        self.assertEqual(fields["fingerprint"], "SHA256:abc123fake")
        self.assertEqual(fields["key_type"], "ed25519")

    def test_alias_item(self):
        fields = _parse_fields(MOCK_ALIAS_ITEM, "shopping_alias")
        self.assertEqual(fields["aliased_email"], "shopping.abc123@pm.me")

    def test_alias_item_aliased_address_fallback(self):
        """aliased_address is accepted when aliased_email is absent."""
        item = _make_item("Alias", {"aliased_address": "alt.abc@pm.me"})
        fields = _parse_fields(item, "alias2")
        self.assertEqual(fields["aliased_email"], "alt.abc@pm.me")

    def test_timestamp_extra_field_converted_to_string(self):
        """Timestamp integer values in extra_fields must be stored as strings."""
        item = _make_item(
            "Login",
            {"username": "u", "password": "p", "urls": [], "totp_uri": "", "passkeys": []},
            extra_fields=[{"name": "expiry", "content": {"Timestamp": 1735689600}}],
        )
        fields = _parse_fields(item, "item")
        self.assertEqual(fields["expiry"], "1735689600")

    def test_trashed_item_raises(self):
        """Items in the Proton Pass trash must raise AnsibleLookupError."""
        with self.assertRaises(AnsibleLookupError) as ctx:
            _parse_fields(MOCK_TRASHED_ITEM, "old_item")
        self.assertIn("trash", str(ctx.exception).lower())
        self.assertIn("old_item", str(ctx.exception))


# ---------------------------------------------------------------------------
# _extract_extra_fields
# ---------------------------------------------------------------------------


class TestExtractExtraFields(unittest.TestCase):
    def test_hidden_field(self):
        from ansible_collections.community.general.plugins.lookup.proton_pass import _extract_extra_fields

        result = _extract_extra_fields([{"name": "my_key", "content": {"Hidden": "secret_val"}}])
        self.assertEqual(result, {"my_key": "secret_val"})

    def test_text_field(self):
        from ansible_collections.community.general.plugins.lookup.proton_pass import _extract_extra_fields

        result = _extract_extra_fields([{"name": "my_key", "content": {"Text": "text_val"}}])
        self.assertEqual(result, {"my_key": "text_val"})

    def test_totp_field(self):
        from ansible_collections.community.general.plugins.lookup.proton_pass import _extract_extra_fields

        uri = "otpauth://totp/Test?secret=ABC"
        result = _extract_extra_fields([{"name": "otp", "content": {"Totp": uri}}])
        self.assertEqual(result, {"otp": uri})

    def test_timestamp_field_converted_to_string(self):
        from ansible_collections.community.general.plugins.lookup.proton_pass import _extract_extra_fields

        result = _extract_extra_fields([{"name": "expiry", "content": {"Timestamp": 1735689600}}])
        self.assertEqual(result, {"expiry": "1735689600"})

    def test_skips_field_with_no_name(self):
        from ansible_collections.community.general.plugins.lookup.proton_pass import _extract_extra_fields

        result = _extract_extra_fields([{"content": {"Hidden": "val"}}])
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# _raise_item_error
# ---------------------------------------------------------------------------


class TestRaiseItemError(unittest.TestCase):
    def test_not_found_stderr(self):
        with self.assertRaises(AnsibleLookupError) as ctx:
            _raise_item_error("vm", "vault", None, "Error: item not found")
        self.assertIn("not found", str(ctx.exception).lower())
        self.assertIn("vm", str(ctx.exception))

    def test_unauthorized_stderr(self):
        with self.assertRaises(AnsibleLookupError) as ctx:
            _raise_item_error("vm", "vault", None, "Error: unauthorized access")
        self.assertIn("authentication", str(ctx.exception).lower())

    def test_generic_error(self):
        with self.assertRaises(AnsibleLookupError) as ctx:
            _raise_item_error("vm", "vault", "api_key", "unexpected failure")
        self.assertIn("unexpected failure", str(ctx.exception))
        self.assertIn("api_key", str(ctx.exception))


# ---------------------------------------------------------------------------
# ProtonPassClient
# ---------------------------------------------------------------------------


def _make_popen_mock(returncode: int, stdout: bytes, stderr: bytes):
    mock_proc = MagicMock()
    mock_proc.returncode = returncode
    mock_proc.communicate.return_value = (stdout, stderr)
    return mock_proc


class TestProtonPassClientRun(unittest.TestCase):
    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_successful_run(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(0, b"output\n", b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        rc, out, err = client._run(["test"])
        self.assertEqual(rc, 0)
        self.assertEqual(out, "output\n")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_missing_binary_raises(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError()
        client = ProtonPassClient(cli_path="/no/such/binary", timeout=30, agent_reason="")
        with self.assertRaises(ProtonPassCLIError) as ctx:
            client._run(["test"])
        self.assertIn("not found", str(ctx.exception))

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_agent_reason_injected_into_env(self, mock_popen):
        """PROTON_PASS_AGENT_REASON must be present in the subprocess env when set."""
        mock_popen.return_value = _make_popen_mock(0, b"ok\n", b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="nightly deployment")
        client._run(["test"])
        _call_args, kwargs = mock_popen.call_args
        self.assertEqual(kwargs["env"].get("PROTON_PASS_AGENT_REASON"), "nightly deployment")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_no_agent_reason_does_not_override_env(self, mock_popen):
        """When agent_reason is empty, PROTON_PASS_AGENT_REASON should not be forced."""
        mock_popen.return_value = _make_popen_mock(0, b"ok\n", b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        client._run(["test"])
        _call_args, kwargs = mock_popen.call_args
        # The key may be inherited from the real environment — we only assert it
        # was not forcibly added by the plugin logic (value will be None if absent).
        env = kwargs["env"]
        self.assertNotEqual(env.get("PROTON_PASS_AGENT_REASON"), "")  # not set to empty

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_timeout_raises(self, mock_popen):
        from subprocess import TimeoutExpired

        mock_proc = MagicMock()
        mock_proc.communicate.side_effect = TimeoutExpired(cmd="pass-cli", timeout=30)
        mock_popen.return_value = mock_proc
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        with self.assertRaises(ProtonPassCLIError) as ctx:
            client._run(["test"])
        self.assertIn("timed out", str(ctx.exception))


class TestProtonPassClientAuth(unittest.TestCase):
    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_test_session_returns_true_on_rc0(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(0, b"", b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        self.assertTrue(client.test_session())

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_test_session_returns_false_on_nonzero(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(1, b"", b"not logged in\n")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        self.assertFalse(client.test_session())

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_ensure_authenticated_already_ok(self, mock_popen):
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        client._session_ok = True
        # ensure_authenticated must not invoke pass-cli at all
        client.ensure_authenticated(pat="")
        mock_popen.assert_not_called()

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_ensure_authenticated_no_session_no_pat_raises(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(1, b"", b"unauthenticated\n")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        with self.assertRaises(AnsibleLookupError) as ctx:
            client.ensure_authenticated(pat="")
        self.assertIn("PAT", str(ctx.exception))

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_ensure_authenticated_logs_in_with_pat(self, mock_popen):
        # First call (test): unauthenticated; second call (login): success
        mock_popen.side_effect = [
            _make_popen_mock(1, b"", b"unauthenticated\n"),
            _make_popen_mock(0, b"", b""),
        ]
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        client.ensure_authenticated(pat="pst_token::key")
        self.assertEqual(mock_popen.call_count, 2)


class TestProtonPassClientFetch(unittest.TestCase):
    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_field_success(self, mock_popen):
        """fetch_field delegates to fetch_all_fields and returns the requested field."""
        payload = json.dumps(MOCK_LOGIN_ITEM).encode()
        mock_popen.return_value = _make_popen_mock(0, payload, b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        result = client.fetch_field(vault="vault", title="example_item", field="api_token")
        self.assertEqual(result, "token_value_abc")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_field_not_found_raises(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(1, b"", b"Error: item not found\n")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        with self.assertRaises(AnsibleLookupError):
            client.fetch_field(vault="vault", title="missing", field="password")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_field_missing_field_raises(self, mock_popen):
        """fetch_field raises with available fields listed when field is absent from item."""
        payload = json.dumps(MOCK_LOGIN_ITEM).encode()
        mock_popen.return_value = _make_popen_mock(0, payload, b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        with self.assertRaises(AnsibleLookupError) as ctx:
            client.fetch_field(vault="vault", title="example_item", field="nonexistent_key")
        err = str(ctx.exception)
        self.assertIn("nonexistent_key", err)
        self.assertIn("Available fields", err)

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_all_fields_success(self, mock_popen):
        payload = json.dumps(MOCK_LOGIN_ITEM).encode()
        mock_popen.return_value = _make_popen_mock(0, payload, b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        result = client.fetch_all_fields(vault="vault", title="example_item")
        self.assertEqual(result["api_token"], "token_value_abc")
        self.assertEqual(result["backup_secret"], "secure_value_1")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.display")
    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_all_fields_debug_warning(self, mock_popen, mock_display):
        """When debug=True, display.warning is called with raw JSON;
        the result is still parsed and returned correctly."""
        payload = json.dumps(MOCK_LOGIN_ITEM).encode()
        mock_popen.return_value = _make_popen_mock(0, payload, b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="", debug=True)
        result = client.fetch_all_fields(vault="vault", title="example_item")
        mock_display.warning.assert_called_once()
        self.assertIn("example_item", mock_display.warning.call_args[0][0])
        self.assertEqual(result["api_token"], "token_value_abc")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.display")
    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_all_fields_no_debug_warning(self, mock_popen, mock_display):
        """When debug=False, display.warning is not called."""
        payload = json.dumps(MOCK_LOGIN_ITEM).encode()
        mock_popen.return_value = _make_popen_mock(0, payload, b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="", debug=False)
        result = client.fetch_all_fields(vault="vault", title="example_item")
        mock_display.warning.assert_not_called()
        self.assertEqual(result["api_token"], "token_value_abc")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.Popen")
    def test_fetch_all_fields_invalid_json_raises(self, mock_popen):
        mock_popen.return_value = _make_popen_mock(0, b"not json {{", b"")
        client = ProtonPassClient(cli_path="pass-cli", timeout=30, agent_reason="")
        with self.assertRaises(AnsibleLookupError) as ctx:
            client.fetch_all_fields(vault="vault", title="bad_item")
        self.assertIn("invalid JSON", str(ctx.exception))


# ---------------------------------------------------------------------------
# LookupModule integration
# ---------------------------------------------------------------------------


class TestLookupModule(unittest.TestCase):
    """
    Integration tests for LookupModule.run().

    Ansible's config system requires a fully initialised plugin (via lookup_loader
    or ansible-test) to resolve options declared in DOCUMENTATION.  In a plain
    unittest environment lookup_loader returns None, so these tests patch
    set_options (no-op) and get_option (returns values from a local dict) to
    exercise the routing logic without depending on the Ansible config manager.
    Use ``ansible-test unit`` for a full integration test in CI.
    """

    def setUp(self):
        self.lookup = LookupModule()

    def _run(self, terms, vault="", field="", pat="", agent_reason="", cli_path="pass-cli", timeout=30, debug=False):
        """Run with Ansible option plumbing patched out."""
        options = {
            "vault": vault,
            "field": field,
            "pat": pat,
            "agent_reason": agent_reason,
            "cli_path": cli_path,
            "timeout": timeout,
            "debug": debug,
        }
        with patch.object(self.lookup, "set_options"):
            with patch.object(self.lookup, "get_option", side_effect=lambda k: options.get(k, "")):
                return self.lookup.run(terms)

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_all_fields_mode(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.fetch_all_fields.return_value = {"api_key": "secret123"}
        mock_client_cls.return_value = mock_client

        result = self._run(["vm"], vault="myvault")
        self.assertEqual(result, [{"api_key": "secret123"}])
        mock_client.fetch_all_fields.assert_called_once_with(vault="myvault", title="vm")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_single_field_via_second_term(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.fetch_field.return_value = "secret123"
        mock_client_cls.return_value = mock_client

        result = self._run(["vm", "api_key"], vault="myvault")
        self.assertEqual(result, ["secret123"])
        mock_client.fetch_field.assert_called_once_with(vault="myvault", title="vm", field="api_key")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_single_field_via_kwarg(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.fetch_field.return_value = "secret123"
        mock_client_cls.return_value = mock_client

        result = self._run(["vm"], vault="myvault", field="api_key")
        self.assertEqual(result, ["secret123"])

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_field_kwarg_overrides_second_term(self, mock_client_cls):
        """O(field) takes precedence over the second positional term."""
        mock_client = MagicMock()
        mock_client.fetch_field.return_value = "secret123"
        mock_client_cls.return_value = mock_client

        self._run(["vm", "ignored_term"], vault="myvault", field="real_field")
        mock_client.fetch_field.assert_called_once_with(vault="myvault", title="vm", field="real_field")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_multiple_items_with_field(self, mock_client_cls):
        # Three terms required: two terms trigger the (item, field) shorthand,
        # so three or more terms are needed to look up multiple items.
        mock_client = MagicMock()
        mock_client.fetch_field.side_effect = ["pass_a", "pass_b", "pass_c"]
        mock_client_cls.return_value = mock_client

        result = self._run(["host_a", "host_b", "host_c"], vault="", field="gpg_keyphrase")
        self.assertEqual(result, ["pass_a", "pass_b", "pass_c"])

    def test_multiple_items_no_field_raises(self):
        # Three terms without field= should raise AnsibleOptionsError.
        with self.assertRaises(AnsibleOptionsError):
            self._run(["host_a", "host_b", "host_c"], vault="")

    def test_no_terms_raises(self):
        with self.assertRaises(AnsibleLookupError):
            self._run([], vault="myvault")

    @patch("ansible_collections.community.general.plugins.lookup.proton_pass.ProtonPassClient")
    def test_debug_option_passed_to_client(self, mock_client_cls):
        """Verify that the debug option is passed to ProtonPassClient."""
        mock_client = MagicMock()
        mock_client.fetch_all_fields.return_value = {"api_key": "secret123"}
        mock_client_cls.return_value = mock_client

        self._run(["vm"], vault="myvault", debug=True)
        # Check that ProtonPassClient was instantiated with debug=True
        mock_client_cls.assert_called_once()
        call_kwargs = mock_client_cls.call_args[1]
        self.assertTrue(call_kwargs["debug"])

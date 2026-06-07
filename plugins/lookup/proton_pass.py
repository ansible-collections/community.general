# Copyright (c) 2026, Jean Khawand (@jeankhawand)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: proton_pass
author:
  - Jean Khawand (@jeankhawand)
version_added: "13.2.0"
short_description: Fetch secrets from Proton Pass via the C(pass-cli) command-line tool.
description:
  - Retrieves secrets stored in Proton Pass by calling the C(pass-cli) binary
    on the Ansible control machine.
  - When only one item title is given, returns a dictionary of all extra fields for
    that item so the caller can access individual secrets by key.
  - When a field name is also given, returns the field value as a string directly,
    without parsing JSON.
  - Every lookup invokes C(pass-cli) directly — no in-process caching — so each
    call always reflects the current vault state.
requirements:
  - C(pass-cli) installed on the Ansible control machine
    (see U(https://github.com/protonpass/pass-cli))
notes:
  - Two non-interactive authentication paths are available.
  - B(Agent tokens) (recommended for CI/CD) are scoped to specific vaults,
    carry an expiration date, and produce an encrypted audit log — create one
    with C(pass-cli agent create <NAME> --expiration 1m --vault <VAULT>), then
    supply the token via O(pat) / E(ANSIBLE_PROTON_PASS_PAT) and set
    O(agent_reason) / E(ANSIBLE_PROTON_PASS_AGENT_REASON) to a short description
    of why the automation is accessing the vault.
  - B(Personal Access Tokens) B(PAT) grant full account access and should be
    reserved for interactive or development use — generate one in the Proton
    Pass web app under B(Account > Security > Access and authentication >
    Personal Access Tokens). PAT format is C(pst_<token>::<key>).
  - Authenticate once interactively with C(pass-cli login) before running
    playbooks when neither an agent token nor a PAT is configured.
  - Set O(debug=true) on the lookup call to display the raw C(pass-cli) JSON via
    Ansible's warning output — useful for diagnosing field extraction failures
    across C(pass-cli) versions.
  - >-
    All Proton Pass item types are supported: B(Login), B(Note), B(Credit Card),
    B(Wi-Fi), B(Identity), B(SSH Key), B(Custom), and B(Alias). Standard fields
    for each type (for example C(username)/C(password) for Login, C(ssid)/C(password)
    for Wi-Fi, C(private_key)/C(public_key) for SSH Key) are included in the returned
    dictionary alongside any custom extra fields.
  - For B(Login) items the C(urls) field is returned as a list of strings.
  - In Proton Pass, create one item per host. Add every secret as an extra B(hidden)
    field whose name exactly matches the key your playbooks reference (for example
    C(api_token), C(gpg_keyphrase)).
  - Sections (C(extra_sections)) are supported — fields nested inside a section
    are merged into the same flat dict as top-level extra fields.
options:
  _terms:
    description:
      - One or more Proton Pass item titles to look up.
      - If exactly two terms are given and O(field) is not set, the second term
        is interpreted as a field name and a plain string is returned instead of
        a dictionary.
    required: true
    type: list
    elements: str
  field:
    description:
      - Field name to retrieve. When set, the lookup returns a plain string
        instead of a dictionary, equivalent to passing the field as the second
        positional term.
      - When both a second positional term and O(field) are supplied, O(field)
        takes precedence.
    type: str
    default: ""
  vault:
    description:
      - Name of the Proton Pass vault to query.
      - When omitted, C(pass-cli) searches across all vaults accessible to
        the authenticated account; this may raise an error when the item title
        is not unique across vaults.
    type: str
    default: ""
    ini:
      - section: proton_pass_lookup
        key: vault
    env:
      - name: ANSIBLE_PROTON_PASS_VAULT
    vars:
      - name: ansible_proton_pass_vault
  pat:
    description:
      - Personal Access Token used for non-interactive authentication.
      - Format is C(pst_<token>::<key>).
      - When provided, the plugin runs C(pass-cli login --pat <value>) before
        the first item lookup if no active session is detected.
    type: str
    default: ""
    ini:
      - section: proton_pass_lookup
        key: pat
    env:
      - name: ANSIBLE_PROTON_PASS_PAT
    vars:
      - name: ansible_proton_pass_pat
  agent_reason:
    description:
      - Human-readable reason string required by Proton Pass when authenticating
        with an B(agent token) (as opposed to a personal account PAT).
      - Maps to the C(PROTON_PASS_AGENT_REASON) environment variable consumed by
        C(pass-cli). Must be between 1 and 300 characters.
      - Agent tokens are the recommended authentication mechanism for CI/CD
        pipelines and automated processes — they are scoped to specific vaults,
        carry an expiration date, and produce an encrypted audit log.
        Create one with C(pass-cli agent create <NAME> --expiration 1m
        --vault <VAULT_NAME>).
    type: str
    default: ""
    ini:
      - section: proton_pass_lookup
        key: agent_reason
    env:
      - name: ANSIBLE_PROTON_PASS_AGENT_REASON
    vars:
      - name: ansible_proton_pass_agent_reason
  cli_path:
    description:
      - Path to the C(pass-cli) binary.
      - When not set, C(pass-cli) is resolved from E(PATH).
    type: str
    default: pass-cli
    ini:
      - section: proton_pass_lookup
        key: cli_path
    env:
      - name: ANSIBLE_PROTON_PASS_CLI_PATH
    vars:
      - name: ansible_proton_pass_cli_path
  timeout:
    description:
      - Timeout in seconds for each C(pass-cli) subprocess invocation.
    type: int
    default: 30
    ini:
      - section: proton_pass_lookup
        key: timeout
    env:
      - name: ANSIBLE_PROTON_PASS_TIMEOUT
    vars:
      - name: ansible_proton_pass_timeout
  debug:
    description:
      - When C(true), displays the raw C(pass-cli) JSON via Ansible's warning output.
      - Useful for diagnosing field extraction failures across C(pass-cli) versions.
      - >-
        B(Note) that this can show sensitive information. Use only when
        absolutely necessary and ensure the sensitive output is not logged.
    type: bool
    default: false
"""

EXAMPLES = r"""
# Prerequisites — authenticate once on the control machine:
#   pass-cli login --pat pst_<token>::<key>
# Or export for non-interactive / CI use:
#   export ANSIBLE_PROTON_PASS_PAT='pst_<token>::<key>'
# Or configure ansible.cfg (applies to all lookups in the project):
#   [proton_pass_lookup]
#   vault = myproject

# --- All-fields mode: returns a dict of all extra fields ---

- name: Load all secrets for the current host
  ansible.builtin.set_fact:
    host_secrets: "{{ lookup('community.general.proton_pass', inventory_hostname, vault='myproject') }}"

- name: Use a field from the loaded dict
  ansible.builtin.debug:
    msg: "Token: {{ host_secrets.api_token }}"

# --- Single-field mode: returns a plain string ---

- name: Fetch one field via second positional term
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.proton_pass', 'my_host', 'api_token', vault='myproject') }}"

- name: Fetch one field via keyword argument
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.proton_pass', 'my_host', field='api_token', vault='myproject') }}"

# --- Multiple items, same field ---

- name: Fetch gpg_keyphrase from two items
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.proton_pass', 'host_a', 'host_b', field='gpg_keyphrase', vault='myproject') }}"

# --- Drop-in replacement for ansible-vault secrets ---
# Place in group_vars/all/secrets.yaml (plain YAML, safe to commit):
#
#   secrets:
#     host_a: "{{ lookup('community.general.proton_pass', 'host_a', vault='myproject') }}"
#     host_b: "{{ lookup('community.general.proton_pass', 'host_b', vault='myproject') }}"
#
# Existing role tasks continue to work without modification:
#   "{{ secrets[inventory_hostname].some_secret }}"

# --- Vault configured globally in ansible.cfg — no vault= kwarg needed ---
- name: Lookup when ansible.cfg sets [proton_pass_lookup] vault
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.proton_pass', 'my_host', 'api_token') }}"

# --- Agent token authentication (recommended for CI/CD) ---
# Create the agent first (one-time setup):
#   pass-cli agent create ci-runner --expiration 1m --vault myproject
# Then configure ansible.cfg:
#   [proton_pass_lookup]
#   vault = myproject
#   agent_reason = ansible playbook run
# And set the token in the environment (or ansible.cfg):
#   export ANSIBLE_PROTON_PASS_PAT='<agent-token>'
- name: Lookup using an agent token
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.proton_pass', 'my_host', 'api_token',
             pat=lookup('env', 'ANSIBLE_PROTON_PASS_PAT'),
             agent_reason='nightly deployment pipeline') }}"
"""

RETURN = r"""
_raw:
  description:
    - A list with one element per input term.
    - In single-field mode (O(field) set or two-term shorthand), each element is
      the plain-text value of the requested field.
    - In all-fields mode, each element is a flat dictionary mapping standard
      item-type fields (C(username)/C(password) for login, C(ssid)/C(password) for
      wi-fi, C(private_key)/C(public_key) for ssh-key, etc.) and every custom extra
      field to its string value.
  type: list
  elements: raw
"""

import json
import os
from subprocess import DEVNULL, PIPE, Popen, TimeoutExpired

from ansible.errors import AnsibleLookupError, AnsibleOptionsError
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

from ansible_collections.community.general.plugins.plugin_utils._lookup import check_for_wrong_terms

display = Display()

# ---------------------------------------------------------------------------
# Item-type field registries — mirrors pass-cli item create <type> --get-template
# ---------------------------------------------------------------------------

_LOGIN_FIELDS = ("username", "email", "password", "totp_uri")
_CREDIT_CARD_FIELDS = ("cardholder_name", "card_type", "number", "verification_number", "expiration_date", "pin")
_WIFI_FIELDS = ("ssid", "password", "security")
_SSH_KEY_FIELDS = ("private_key", "public_key", "fingerprint", "key_type")
_IDENTITY_FIELDS = (
    "full_name",
    "email",
    "phone_number",
    "first_name",
    "middle_name",
    "last_name",
    "birthdate",
    "gender",
    "organization",
    "street_address",
    "zip_or_postal_code",
    "city",
    "state_or_province",
    "country_or_region",
    "floor",
    "county",
    "social_security_number",
    "passport_number",
    "license_number",
    "website",
    "x_handle",
    "second_phone_number",
    "linkedin",
    "reddit",
    "facebook",
    "yahoo",
    "instagram",
    "company",
    "job_title",
    "personal_website",
    "work_phone_number",
    "work_email",
)


class ProtonPassCLIError(AnsibleLookupError):
    """Raised when the pass-cli subprocess fails in an unexpected way."""


# ---------------------------------------------------------------------------
# CLI wrapper
# ---------------------------------------------------------------------------


class ProtonPassClient:
    """Thin wrapper around the pass-cli binary."""

    def __init__(
        self,
        cli_path: str,
        timeout: int,
        agent_reason: str,
        debug: bool = False,
    ) -> None:
        self.cli_path = cli_path
        self.timeout = timeout
        self.agent_reason = agent_reason
        self.debug = debug
        self._session_ok = False

    def _run(self, args: list[str]) -> tuple[int, str, str]:
        """Run pass-cli with *args* and return (returncode, stdout, stderr).

        When ``agent_reason`` is set, PROTON_PASS_AGENT_REASON is injected into
        the subprocess environment so that pass-cli records the reason in its
        encrypted audit log.

        Raises:
            ProtonPassCLIError: if the binary is not found or the call times out.
        """
        command = [self.cli_path] + args
        display.vvv(f"proton_pass: running {command}")

        env = os.environ.copy()
        if self.agent_reason:
            env["PROTON_PASS_AGENT_REASON"] = self.agent_reason

        try:
            proc = Popen(command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, env=env)
            out_bytes, err_bytes = proc.communicate(timeout=self.timeout)
            rc = proc.returncode
        except FileNotFoundError as e:
            raise ProtonPassCLIError(
                f"'{self.cli_path}' not found — install pass-cli or set "
                "ANSIBLE_PROTON_PASS_CLI_PATH / [proton_pass_lookup] cli_path "
                "in ansible.cfg"
            ) from e
        except TimeoutExpired as e:
            proc.kill()
            raise ProtonPassCLIError(f"pass-cli timed out after {self.timeout}s") from e

        return (
            rc,
            to_text(out_bytes, errors="surrogate_or_strict"),
            to_text(err_bytes, errors="surrogate_or_strict"),
        )

    # --- authentication ----------------------------------------------------------

    def test_session(self) -> bool:
        """Return True when an active pass-cli session exists."""
        rc, *_ignored = self._run(["test"])
        return rc == 0

    def login_with_pat(self, pat: str) -> None:
        """Authenticate using a Personal Access Token (``pst_<token>::<key>``)."""
        rc, _out, err = self._run(["login", "--pat", pat])
        if rc != 0:
            raise AnsibleLookupError(
                f"pass-cli login failed: {err.strip()} — verify the PAT format is pst_<token>::<key>"
            )

    def ensure_authenticated(self, pat: str) -> None:
        """Ensure there is an active session, logging in with PAT if necessary."""
        if self._session_ok:
            return
        if self.test_session():
            self._session_ok = True
            return
        if not pat:
            raise AnsibleLookupError(
                "No active pass-cli session and no PAT supplied. "
                "Run 'pass-cli login' on the control machine, or set "
                "ANSIBLE_PROTON_PASS_PAT."
            )
        self.login_with_pat(pat)
        self._session_ok = True

    # --- single-field retrieval --------------------------------------------------

    def fetch_all_fields(self, vault: str, title: str) -> dict[str, str | list[str]]:
        """Return all fields for *title* as a flat ``{field_name: value}`` dict.

        Always calls pass-cli — no caching, so callers always receive the
        current vault state.
        """
        args = ["item", "view", "--item-title", title, "--output", "json"]
        if vault:
            args += ["--vault-name", vault]

        rc, out, err = self._run(args)
        if rc != 0:
            _raise_item_error(title, vault, None, err)

        if self.debug:
            display.warning(f"proton_pass DEBUG — raw JSON for '{title}':\n{out}")

        try:
            raw = json.loads(out)
        except json.JSONDecodeError as e:
            raise AnsibleLookupError(
                f"pass-cli returned invalid JSON for item '{title}': {e}. "
                "Set the lookup option debug=true to inspect the raw output."
            ) from e

        return _parse_fields(raw, title)

    def fetch_field(self, vault: str, title: str, field: str) -> str:
        """Return a single field value for *title*.

        Delegates to ``fetch_all_fields`` so that trashed-item detection,
        JSON parsing, and error messages are consistent regardless of whether
        the caller requests one field or all fields.
        """
        all_fields = self.fetch_all_fields(vault=vault, title=title)
        if field not in all_fields:
            vault_hint = f" in vault '{vault}'" if vault else ""
            raise AnsibleLookupError(
                f"proton_pass: field '{field}' not found in item '{title}'{vault_hint}. "
                f"Available fields: {', '.join(sorted(all_fields)) or '(none)'}"
            )
        value = all_fields[field]
        return value if isinstance(value, str) else ", ".join(value)


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _raise_item_error(title: str, vault: str, field: str | None, stderr: str) -> None:
    """Translate pass-cli stderr into a descriptive AnsibleLookupError."""
    msg = stderr.strip()
    vault_hint = f" in vault '{vault}'" if vault else ""
    field_hint = f", field '{field}'" if field else ""

    lower = msg.lower()
    if "not found" in lower or "no items found" in lower:
        raise AnsibleLookupError(
            f"Item '{title}'{vault_hint} not found in Proton Pass{field_hint}. Verify the item title and vault name."
        )
    if "unauthorized" in lower or "unauthenticated" in lower:
        raise AnsibleLookupError(f"pass-cli authentication error: {msg}. Re-run 'pass-cli login' or refresh your PAT.")
    raise AnsibleLookupError(f"pass-cli failed for item '{title}'{vault_hint}{field_hint}: {msg}")


# ---------------------------------------------------------------------------
# JSON parser
# ---------------------------------------------------------------------------


def _extract_scalar_fields(source: dict, keys: tuple) -> dict[str, str]:
    """Return a dict of *keys* from *source*, skipping None and empty-string values."""
    return {key: str(val) for key in keys if (val := source.get(key)) is not None and val != ""}


def _extract_typed_fields(type_key: str, type_data: dict) -> dict[str, str | list[str]]:
    """Return type-specific standard fields extracted from *type_data*."""
    fields: dict[str, str | list[str]] = {}
    tk = type_key.lower()
    if tk == "login":
        fields.update(_extract_scalar_fields(type_data, _LOGIN_FIELDS))
        urls = type_data.get("urls")
        if urls:
            fields["urls"] = urls if isinstance(urls, list) else [urls]
    elif tk == "creditcard":
        fields.update(_extract_scalar_fields(type_data, _CREDIT_CARD_FIELDS))
    elif tk == "wifi":
        fields.update(_extract_scalar_fields(type_data, _WIFI_FIELDS))
    elif tk == "sshkey":
        fields.update(_extract_scalar_fields(type_data, _SSH_KEY_FIELDS))
        for section in type_data.get("sections", []):
            fields.update(_extract_extra_fields(section.get("extra_fields", [])))
    elif tk == "identity":
        fields.update(_extract_scalar_fields(type_data, _IDENTITY_FIELDS))
        for sub_key in (
            "extra_personal_details",
            "extra_address_details",
            "extra_contact_details",
            "extra_work_details",
        ):
            fields.update(_extract_extra_fields(type_data.get(sub_key, [])))
        for section in type_data.get("extra_sections", []):
            fields.update(_extract_extra_fields(section.get("extra_fields", [])))
    elif tk == "alias":
        for alias_key in ("aliased_email", "aliased_address"):
            val = type_data.get(alias_key)
            if val:
                fields["aliased_email"] = val
                break
    return fields


def _parse_fields(raw: dict, title: str) -> dict[str, str | list[str]]:
    """Extract a flat ``{field_name: value}`` dict from a pass-cli JSON response."""
    fields: dict[str, str | list[str]] = {}

    item_obj = raw.get("item", raw)
    state = item_obj.get("state", "")
    if state.lower() == "trashed":
        raise AnsibleLookupError(
            f"proton_pass: item '{title}' is in the Proton Pass trash and cannot be "
            "used. Restore it or permanently delete it."
        )

    content_wrapper = item_obj.get("content", {})
    note = content_wrapper.get("note")
    if note:
        fields["note"] = str(note)

    type_dict = content_wrapper.get("content")
    if isinstance(type_dict, dict):
        for type_key, type_data in type_dict.items():
            if isinstance(type_data, dict):
                fields.update(_extract_typed_fields(type_key, type_data))

    fields.update(_extract_extra_fields(content_wrapper.get("extra_fields", [])))
    for section in content_wrapper.get("extra_sections", []):
        fields.update(_extract_extra_fields(section.get("extra_fields", [])))

    if not fields:
        raise AnsibleLookupError(
            f"proton_pass: no fields extracted from item '{title}'. "
            "Ensure the item has a note, standard fields, or at least one extra "
            "hidden field. Set the lookup option debug=true to inspect the raw JSON."
        )

    return fields


def _extract_extra_fields(extra_fields: list[dict]) -> dict[str, str]:
    """Return a flat ``{field_name: value}`` dict from a pass-cli extra_fields list.

    Each entry has the shape::

        {"name": "key", "content": {"Hidden"|"Text"|"Totp"|"Timestamp": value}}

    The type wrapper key varies; the actual value is always the first dict value.
    Non-string values (for example ``Timestamp`` integers) are converted to strings.
    """
    result: dict[str, str] = {}
    for extra in extra_fields:
        name = extra.get("name", "")
        if not name:
            continue
        content = extra.get("content")
        if isinstance(content, dict):
            raw_value = next((v for v in content.values() if v is not None), "")
            result[name] = str(raw_value)
    return result


# ---------------------------------------------------------------------------
# Lookup module
# ---------------------------------------------------------------------------


class LookupModule(LookupBase):
    def run(self, terms: list[str], variables: dict | None = None, **kwargs) -> list:
        self.set_options(var_options=variables, direct=kwargs)
        check_for_wrong_terms(self, direct=kwargs)
        vault = self.get_option("vault") or ""
        pat = self.get_option("pat") or ""
        agent_reason = self.get_option("agent_reason") or ""
        cli_path = self.get_option("cli_path") or "pass-cli"
        timeout = int(self.get_option("timeout"))
        debug = boolean(self.get_option("debug"))
        field_opt = self.get_option("field") or ""

        if not terms:
            raise AnsibleLookupError(
                "community.general.proton_pass requires at least one positional argument (item title)"
            )

        # Two-term shorthand: lookup('proton_pass', 'item_title', 'field_name')
        if len(terms) == 2:
            item_titles = [terms[0]]
            field = field_opt or terms[1]
        else:
            item_titles = list(terms)
            field = field_opt

        if len(item_titles) > 1 and not field:
            raise AnsibleOptionsError(
                "community.general.proton_pass: fetching all fields for multiple "
                "items in one call is not supported. Specify 'field' or look up "
                "one item at a time."
            )

        client = ProtonPassClient(cli_path=cli_path, timeout=timeout, agent_reason=agent_reason, debug=debug)
        client.ensure_authenticated(pat)

        results: list[str | dict[str, str | list[str]]] = []
        for title in item_titles:
            if field:
                results.append(client.fetch_field(vault=vault, title=title, field=field))
            else:
                results.append(client.fetch_all_fields(vault=vault, title=title))

        return results

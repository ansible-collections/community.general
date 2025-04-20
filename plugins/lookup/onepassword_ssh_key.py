# -*- coding: utf-8 -*-
# Copyright (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: onepassword_ssh_key
author:
  - Mohammed Babelly (@mohammedbabelly20)
requirements:
  - C(op) 1Password command line utility version 2 or later.
short_description: Fetch SSH keys stored in 1Password
version_added: "10.3.0"
description:
  - P(community.general.onepassword_ssh_key#lookup) wraps C(op) command line utility to fetch SSH keys from 1Password.
notes:
  - By default, it returns the private key value in PKCS#8 format, unless O(ssh_format=true) is passed.
  - The pluging works only for C(SSHKEY) type items.
  - This plugin requires C(op) version 2 or later.
options:
  _terms:
    description: Identifier(s) (case-insensitive UUID or name) of item(s) to retrieve.
    required: true
    type: list
    elements: string
  ssh_format:
    description: Output key in SSH format if V(true). Otherwise, outputs in the default format (PKCS#8).
    default: false
    type: bool

extends_documentation_fragment:
  - community.general.onepassword
  - community.general.onepassword.lookup
"""

EXAMPLES = r"""
---
- name: Retrieve the private SSH key from 1Password
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.onepassword_ssh_key', 'SSH Key', ssh_format=true) }}"
"""

RETURN = r"""
_raw:
  description: Private key of SSH keypair.
  type: list
  elements: string
"""
import json

from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePass,
    OnePassCLIv2,
)
from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def get_ssh_key(self, out, item_id, ssh_format=False):
        data = json.loads(out)

        if data.get("category") != "SSH_KEY":
            raise AnsibleLookupError(f"Item {item_id} is not an SSH key")

        private_key_field = next(
            (
                field
                for field in data.get("fields", {})
                if field.get("id") == "private_key" and field.get("type") == "SSHKEY"
            ),
            None,
        )
        if not private_key_field:
            raise AnsibleLookupError(f"No private key found for item {item_id}.")

        if ssh_format:
            return (
                private_key_field.get("ssh_formats", {})
                .get("openssh", {})
                .get("value", "")
            )
        return private_key_field.get("value", "")

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        ssh_format = self.get_option("ssh_format")
        vault = self.get_option("vault")
        subdomain = self.get_option("subdomain")
        domain = self.get_option("domain", "1password.com")
        username = self.get_option("username")
        secret_key = self.get_option("secret_key")
        master_password = self.get_option("master_password")
        service_account_token = self.get_option("service_account_token")
        account_id = self.get_option("account_id")
        connect_host = self.get_option("connect_host")
        connect_token = self.get_option("connect_token")

        op = OnePass(
            subdomain=subdomain,
            domain=domain,
            username=username,
            secret_key=secret_key,
            master_password=master_password,
            service_account_token=service_account_token,
            account_id=account_id,
            connect_host=connect_host,
            connect_token=connect_token,
            cli_class=OnePassCLIv2,
        )
        op.assert_logged_in()

        return [
            self.get_ssh_key(op.get_raw(term, vault), term, ssh_format=ssh_format)
            for term in terms
        ]

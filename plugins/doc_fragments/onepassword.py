# -*- coding: utf-8 -*-

# Copyright (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
requirements:
  - See U(https://support.1password.com/command-line/)
options:
  master_password:
    description: The password used to unlock the specified vault.
    aliases: ['vault_password']
    type: str
  section:
    description: Item section containing the field to retrieve (case-insensitive). If absent, returns first match from any
      section.
  domain:
    description: Domain of 1Password.
    default: '1password.com'
    type: str
  subdomain:
    description: The 1Password subdomain to authenticate against.
    type: str
  account_id:
    description: The account ID to target.
    type: str
  username:
    description: The username used to sign in.
    type: str
  secret_key:
    description: The secret key used when performing an initial sign in.
    type: str
  service_account_token:
    description:
      - The access key for a service account.
      - Only works with 1Password CLI version 2 or later.
    type: str
  vault:
    description: Vault containing the item to retrieve (case-insensitive). If absent, searches all vaults.
    type: str
  connect_host:
    description: The host for 1Password Connect. Must be used in combination with O(connect_token).
    type: str
    env:
      - name: OP_CONNECT_HOST
    version_added: 8.1.0
  connect_token:
    description: The token for 1Password Connect. Must be used in combination with O(connect_host).
    type: str
    env:
      - name: OP_CONNECT_TOKEN
    version_added: 8.1.0
"""

    LOOKUP = r"""
options:
  service_account_token:
    env:
      - name: OP_SERVICE_ACCOUNT_TOKEN
        version_added: 8.2.0
notes:
  - This lookup uses an existing 1Password session if one exists. If not, and you have already performed an initial sign in
    (meaning C(~/.op/config), C(~/.config/op/config) or C(~/.config/.op/config) exists), then only the O(master_password)
    is required. You may optionally specify O(subdomain) in this scenario, otherwise the last used subdomain is used by C(op).
  - This lookup can perform an initial login by providing O(subdomain), O(username), O(secret_key), and O(master_password).
  - Can target a specific account by providing the O(account_id).
  - Due to the B(very) sensitive nature of these credentials, it is B(highly) recommended that you only pass in the minimal
    credentials needed at any given time. Also, store these credentials in an Ansible Vault using a key that is equal to or
    greater in strength to the 1Password master password.
  - This lookup stores potentially sensitive data from 1Password as Ansible facts. Facts are subject to caching if enabled,
    which means this data could be stored in clear text on disk or in a database.
  - Tested with C(op) version 2.7.2.
"""

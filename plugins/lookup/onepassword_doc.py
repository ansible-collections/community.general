# -*- coding: utf-8 -*-
# Copyright (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: onepassword_doc
    author:
      - Sam Doran (@samdoran)
    requirements:
      - C(op) 1Password command line utility. See U(https://support.1password.com/command-line/)
    short_description: Fetch one or more documents stored in a 1Password vault
    version_added: "9.0.0"
    description:
      - P(community.general.onepassword_raw#lookup) wraps C(op) command line utility to fetch document(s) from 1Password.
    options:
      _terms:
        description: identifier(s) (UUID or name, case-insensitive) of documents(s) to retrieve.
        required: true
      master_password:
        description: The password used to unlock the specified vault.
        aliases: ['vault_password']
      section:
        description: Item section containing the field to retrieve (case-insensitive). If absent will return first match from any section.
      subdomain:
        description: The 1Password subdomain to authenticate against.
      domain:
        description: Domain of 1Password.
        default: '1password.com'
        type: str
      account_id:
        description: The account ID to target.
        type: str
      username:
        description: The username used to sign in.
      secret_key:
        description: The secret key used when performing an initial sign in.
      service_account_token:
        description:
          - The access key for a service account.
          - Only works with 1Password CLI version 2 or later.
        type: string
      vault:
        description: Vault containing the document(s) to retrieve (case-insensitive). If absent will search all vaults.
    notes:
      - The document contents are a string excatly as stored in 1Password.
'''

EXAMPLES = """
- name: Retrieve all data about Wintermute
  ansible.builtin.debug:
    var: lookup('community.general.onepassword_doc', 'Private key')
"""

RETURN = """
  _raw:
    description: field data requested
    type: list
    elements: string
"""

from ansible_collections.community.general.plugins.lookup.onepassword import OnePass, OnePassCLIv2
from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_bytes
from ansible.plugins.lookup import LookupBase


class OnePassCLIv2Doc(OnePassCLIv2):
    def get_raw(self, item_id, vault=None, token=None):
        args = ["document", "get", item_id]
        if vault is not None:
            args = [*args, "--vault={0}".format(vault)]

        if self.service_account_token:
            if vault is None:
                raise AnsibleLookupError("'vault' is required with 'service_account_token'")

            environment_update = {"OP_SERVICE_ACCOUNT_TOKEN": self.service_account_token}
            return self._run(args, environment_update=environment_update)

        if token is not None:
            args = [*args, to_bytes("--session=") + token]

        return self._run(args)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        vault = self.get_option("vault")
        subdomain = self.get_option("subdomain")
        domain = self.get_option("domain", "1password.com")
        username = self.get_option("username")
        secret_key = self.get_option("secret_key")
        master_password = self.get_option("master_password")
        service_account_token = self.get_option("service_account_token")
        account_id = self.get_option("account_id")

        op = OnePass(subdomain, domain, username, secret_key, master_password, service_account_token, account_id, OnePassCLIv2Doc)
        op.assert_logged_in()

        values = []
        for term in terms:
            values.append(op.get_raw(term, vault))

        return values

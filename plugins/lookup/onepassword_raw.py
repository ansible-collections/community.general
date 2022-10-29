# -*- coding: utf-8 -*-
# Copyright (c) 2018, Scott Buchanan <sbuchanan@ri.pn>
# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: onepassword_raw
    author:
      - Scott Buchanan (@scottsb)
      - Andrew Zenk (@azenk)
      - Sam Doran (@samdoran)
    requirements:
      - C(op) 1Password command line utility. See U(https://support.1password.com/command-line/)
    short_description: fetch an entire item from 1Password
    description:
      - C(onepassword_raw) wraps C(op) command line utility to fetch an entire item from 1Password
    options:
      _terms:
        description: identifier(s) (UUID, name, or domain; case-insensitive) of item(s) to retrieve.
        required: true
      master_password:
        description: The password used to unlock the specified vault.
        aliases: ['vault_password']
      section:
        description: Item section containing the field to retrieve (case-insensitive). If absent will return first match from any section.
      subdomain:
        description: The 1Password subdomain to authenticate against.
      username:
        description: The username used to sign in.
      secret_key:
        description: The secret key used when performing an initial sign in.
      vault:
        description: Vault containing the item to retrieve (case-insensitive). If absent will search all vaults.
    notes:
      - This lookup will use an existing 1Password session if one exists. If not, and you have already
        performed an initial sign in (meaning C(~/.op/config exists)), then only the C(master_password) is required.
        You may optionally specify C(subdomain) in this scenario, otherwise the last used subdomain will be used by C(op).
      - This lookup can perform an initial login by providing C(subdomain), C(username), C(secret_key), and C(master_password).
      - Due to the B(very) sensitive nature of these credentials, it is B(highly) recommended that you only pass in the minimal credentials
        needed at any given time. Also, store these credentials in an Ansible Vault using a key that is equal to or greater in strength
        to the 1Password master password.
      - This lookup stores potentially sensitive data from 1Password as Ansible facts.
        Facts are subject to caching if enabled, which means this data could be stored in clear text
        on disk or in a database.
      - Tested with C(op) version 0.5.3
'''

EXAMPLES = """
- name: Retrieve all data about Wintermute
  ansible.builtin.debug:
    var: lookup('community.general.onepassword_raw', 'Wintermute')

- name: Retrieve all data about Wintermute when not signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword_raw', 'Wintermute', subdomain='Turing', vault_password='DmbslfLvasjdl')
"""

RETURN = """
  _raw:
    description: field data requested
    type: list
    elements: dict
"""

import json

from ansible_collections.community.general.plugins.lookup.onepassword import OnePass
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        op = OnePass()

        vault = kwargs.get('vault')
        op.subdomain = kwargs.get('subdomain')
        op.username = kwargs.get('username')
        op.secret_key = kwargs.get('secret_key')
        op.master_password = kwargs.get('master_password', kwargs.get('vault_password'))

        op.assert_logged_in()

        values = []
        for term in terms:
            data = json.loads(op.get_raw(term, vault))
            values.append(data)
        return values

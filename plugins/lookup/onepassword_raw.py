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
      - C(op) 1Password command line utility
    short_description: Fetch an entire item from 1Password
    description:
      - P(community.general.onepassword_raw#lookup) wraps C(op) command line utility to fetch an entire item from 1Password.
    extends_documentation_fragment:
      - community.general.onepassword
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
    description: Entire item requested
    type: list
    elements: dict
"""

import json

from ansible_collections.community.general.plugins.lookup.onepassword import OnePass
from ansible.errors import AnsibleOptionsError
from ansible.plugins.lookup import LookupBase


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
        connect_host = self.get_option("connect_host")
        connect_token = self.get_option("connect_token")

        if (connect_host or connect_token) and None in (connect_host, connect_token):
            raise AnsibleOptionsError("connect_host and connect_token are required together")

        op = OnePass(subdomain, domain, username, secret_key, master_password, service_account_token, account_id, connect_host, connect_token)
        op.assert_logged_in()

        values = []
        for term in terms:
            data = json.loads(op.get_raw(term, vault))
            values.append(data)

        return values

# -*- coding: utf-8 -*-
# Copyright (c) 2018, Scott Buchanan <sbuchanan@ri.pn>
# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: onepassword
    author:
      - Scott Buchanan (@scottsb)
      - Andrew Zenk (@azenk)
      - Sam Doran (@samdoran)
    requirements:
      - C(op) 1Password command line utility. See U(https://support.1password.com/command-line/)
    short_description: fetch field values from 1Password
    description:
      - C(onepassword) wraps the C(op) command line utility to fetch specific field values from 1Password.
    options:
      _terms:
        description: identifier(s) (UUID, name, or subdomain; case-insensitive) of item(s) to retrieve.
        required: true
      field:
        description: field to return from each matching item (case-insensitive).
        default: 'password'
      master_password:
        description: The password used to unlock the specified vault.
        aliases: ['vault_password']
      section:
        description: Item section containing the field to retrieve (case-insensitive). If absent will return first match from any section.
      domain:
        description: Domain of 1Password. Default is U(1password.com).
        version_added: 3.2.0
        default: '1password.com'
        type: str
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
        performed an initial sign in (meaning C(~/.op/config), C(~/.config/op/config) or C(~/.config/.op/config) exists), then only the
        C(master_password) is required. You may optionally specify C(subdomain) in this scenario, otherwise the last used subdomain will be used by C(op).
      - This lookup can perform an initial login by providing C(subdomain), C(username), C(secret_key), and C(master_password).
      - Due to the B(very) sensitive nature of these credentials, it is B(highly) recommended that you only pass in the minimal credentials
        needed at any given time. Also, store these credentials in an Ansible Vault using a key that is equal to or greater in strength
        to the 1Password master password.
      - This lookup stores potentially sensitive data from 1Password as Ansible facts.
        Facts are subject to caching if enabled, which means this data could be stored in clear text
        on disk or in a database.
      - Tested with C(op) version 2.7.0
'''

EXAMPLES = """
# These examples only work when already signed in to 1Password
- name: Retrieve password for KITT when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'KITT')

- name: Retrieve password for Wintermute when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'Tessier-Ashpool', section='Wintermute')

- name: Retrieve username for HAL when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'HAL 9000', field='username', vault='Discovery')

- name: Retrieve password for HAL when not signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword'
                'HAL 9000'
                subdomain='Discovery'
                master_password=vault_master_password)

- name: Retrieve password for HAL when never signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword'
                'HAL 9000'
                subdomain='Discovery'
                master_password=vault_master_password
                username='tweety@acme.com'
                secret_key=vault_secret_key)
"""

RETURN = """
  _raw:
    description: field data requested
    type: list
    elements: str
"""

import os

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError
from ansible.utils.display import Display

from ansible_collections.community.general.plugins.module_utils.onepassword import (
    OnePasswordConfig,
    OnePassCLIBase,
)

DISPLAY = Display()
PLUGIN_NAME = __name__.replace("ansible_collections.", "")


class OnePass(object):
    def __init__(self, subdomain=None, domain="1password.com", username=None, secret_key=None, master_password=None):
        self.subdomain = subdomain
        self.domain = domain
        self.username = username
        self.secret_key = secret_key
        self.master_password = master_password

        self.logged_in = False
        self.token = None

        self._config = OnePasswordConfig()
        self._cli = self._get_cli_class()

    def _get_cli_class(self):
        # TODO: When we get a new op version, warn but use the latest class
        version = OnePassCLIBase.get_current_version()
        for cls in OnePassCLIBase.__subclasses__():
            if cls.supports_version == version.split(".")[0]:
                try:
                    return cls(self.subdomain, self.domain, self.username, self.secret_key, self.master_password)
                except TypeError as e:
                    raise AnsibleLookupError(e)

        raise AnsibleLookupError("op version %s is unsupported" % version)

    def set_token(self):
        if self._config.config_file_path and os.path.isfile(self._config.config_file_path):
            # If the config file exists, assume an initial sign in has taken place and try basic sign in
            try:
                rc, out, err = self._cli.signin()
            except AnsibleLookupError as exc:
                test_strings = (
                    "missing required parameters",
                    "unauthorized",
                )
                if any(string in exc.message.lower() for string in test_strings):
                    # A required parameter is missing, or a bad master password was supplied
                    # so don't bother attempting a full signin
                    raise

                rc, out, err = self._cli.full_signin()

            self.token = out.strip()

        else:
            # Attempt a full signin since there appears to be no existing signin
            rc, out, err = self._cli.full_signin()
            self.token = out.strip()

    def assert_logged_in(self):
        logged_in = self._cli.assert_logged_in()
        if logged_in:
            self.logged_in = logged_in
            pass
        else:
            self.set_token()

    def get_raw(self, item_id, vault=None):
        rc, out, err = self._cli.get_raw(item_id, vault, self.token)
        return out

    def get_field(self, item_id, field, section=None, vault=None):
        output = self.get_raw(item_id, vault)
        if output:
            return self._cli._parse_field(output, field, section)

        return ""


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        field = self.get_option("field")
        section = self.get_option("section")
        vault = self.get_option("vault")
        new = 'faa'
        subdomain = self.get_option("subdomain")
        domain = self.get_option("domain")
        username = self.get_option("username")
        secret_key = self.get_option("secret_key")
        master_password = self.get_option("master_password")
        print(new)

        op = OnePass(subdomain, domain, username, secret_key, master_password)
        op.assert_logged_in()

        values = []
        for term in terms:
            values.append(op.get_field(term, field, section, vault))

        return values

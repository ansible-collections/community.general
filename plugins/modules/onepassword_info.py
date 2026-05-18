#!/usr/bin/python
#
# Copyright (c) 2018, Ryan Conway (@rylon)
# Copyright (c) 2018, Scott Buchanan <sbuchanan@ri.pn> (onepassword.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import annotations

DOCUMENTATION = r"""
module: onepassword_info
author:
  - Ryan Conway (@Rylon)
requirements:
  - C(op) 1Password command line utility version 2 or later. See U(https://support.1password.com/command-line/)
notes:
  - Based on the P(community.general.onepassword#lookup) lookup plugin by Scott Buchanan <sbuchanan@ri.pn>.
short_description: Gather items from 1Password
description:
  - M(community.general.onepassword_info) wraps the C(op) command line utility to fetch data about one or more 1Password items.
  - A fatal error occurs if any of the items being searched for can not be found.
  - Recommend using with the C(no_log) option to avoid logging the values of the secrets being retrieved.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  search_terms:
    type: list
    elements: dict
    description:
      - A list of one or more search terms.
      - Each search term can either be a simple string or it can be a dictionary for more control.
      - When passing a simple string, O(search_terms[].field) is assumed to be V(password).
      - When passing a dictionary, the following fields are available.
    suboptions:
      name:
        type: str
        description:
          - The name of the 1Password item to search for (required).
      field:
        type: str
        description:
          - The name of the field to search for within this item (optional, defaults to V(password)).
      section:
        type: str
        description:
          - The name of a section within this item containing the specified field (optional, it searches all sections if not
            specified).
      vault:
        type: str
        description:
          - The name of the particular 1Password vault to search, useful if your 1Password user has access to multiple vaults
            (optional).
    required: true
  auto_login:
    type: dict
    description:
      - A dictionary containing authentication details. If this is set, the module attempts to sign in to 1Password automatically.
      - Without this option, you must have already logged in using the 1Password CLI before running Ansible.
      - It is B(highly) recommended to store 1Password credentials in an Ansible Vault. Ensure that the key used to encrypt
        the Ansible Vault is equal to or greater in strength than the 1Password master password.
    suboptions:
      subdomain:
        type: str
        description:
          - 1Password subdomain name (V(subdomain).1password.com).
          - If this is not specified, the most recent subdomain is used.
      username:
        type: str
        description:
          - 1Password username.
          - Only required for initial sign in.
      master_password:
        type: str
        description:
          - The master password for your subdomain.
          - This is always required when specifying O(auto_login).
        required: true
      secret_key:
        type: str
        description:
          - The secret key for your subdomain.
          - Only required for initial sign in.
  cli_path:
    type: path
    description: Used to specify the exact path to the C(op) command line interface.
    default: 'op'
"""

EXAMPLES = r"""
# Gather secrets from 1Password, assuming there is a 'password' field:
- name: Get a password
  community.general.onepassword_info:
    search_terms: My 1Password item
  delegate_to: localhost
  register: my_1password_item
  no_log: true       # Don't want to log the secrets to the console!

# Gather secrets from 1Password, with more advanced search terms:
- name: Get a password
  community.general.onepassword_info:
    search_terms:
      - name: My 1Password item
        field: Custom field name       # optional, defaults to 'password'
        section: Custom section name   # optional, defaults to 'None'
        vault: Name of the vault       # optional, only necessary if there is more than 1 Vault available
  delegate_to: localhost
  register: my_1password_item
  no_log: true                         # Don't want to log the secrets to the console!

# Gather secrets combining simple and advanced search terms to retrieve two items, one of which we fetch two
# fields. In the first 'password' is fetched, as a field name is not specified (default behaviour) and in the
# second, 'Custom field name' is fetched, as that is specified explicitly.
- name: Get a password
  community.general.onepassword_info:
    search_terms:
      - My 1Password item              # 'name' is optional when passing a simple string...
      - name: My Other 1Password item  # ...but it can also be set for consistency
      - name: My 1Password item
        field: Custom field name       # optional, defaults to 'password'
        section: Custom section name   # optional, defaults to 'None'
        vault: Name of the vault       # optional, only necessary if there is more than 1 Vault available
  delegate_to: localhost
  register: my_1password_item
  no_log: true                         # Don't want to log the secrets to the console!

- name: Debug a password (for example)
  ansible.builtin.debug:
    msg: "{{ my_1password_item['onepassword']['My 1Password item'] }}"
"""

RETURN = r"""
# One or more dictionaries for each matching item from 1Password, along with the appropriate fields.
# This shows the response you would expect to receive from the third example documented above.
onepassword:
  description: Dictionary of each 1password item matching the given search terms, shows what would be returned from the third
    example above.
  returned: success
  type: dict
  sample:
    "My 1Password item":
      password: the value of this field
      Custom field name: the value of this field
    "My Other 1Password item":
      password: the value of this field
"""


import json
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils._onepassword import (
    OnePasswordConfig,
    onepassword_runner,
)


class OnePasswordInfo:
    def __init__(self, module):
        self.module = module
        self.cli_path = self.module.params.get("cli_path")
        self.auto_login = self.module.params.get("auto_login")
        self.logged_in = False
        self.token = None

        terms = self.module.params.get("search_terms")
        self.terms = self.parse_search_terms(terms)

        self._config = OnePasswordConfig()
        self._runner = onepassword_runner(self.module, self.cli_path)

    def _parse_field(self, data_json, item_id, field_name, section_title=None):
        data = json.loads(data_json)
        field_name_lower = field_name.lower()

        for field in data.get("fields", []):
            if section_title is None:
                if field.get(field_name_lower):
                    return {field_name: field.get(field_name_lower)}
                if field.get("label", "").lower() == field_name_lower:
                    return {field_name: field.get("value", "")}
                if field.get("id", "").lower() == field_name_lower:
                    return {field_name: field.get("value", "")}
            else:
                section = field.get("section", {})
                current_section = section.get("label", section.get("id", "")).lower()
                if section_title.lower() == current_section:
                    if field.get("label", "").lower() == field_name_lower:
                        return {field_name: field.get("value", "")}
                    if field.get("id", "").lower() == field_name_lower:
                        return {field_name: field.get("value", "")}

        optional_section_title = "" if section_title is None else f" in the section '{section_title}'"
        self.module.fail_json(
            msg=f"Unable to find an item in 1Password named '{item_id}' with the field '{field_name}'{optional_section_title}."
        )

    def parse_search_terms(self, terms):
        processed_terms = []

        for term in terms:
            if not isinstance(term, dict):
                term = {"name": term}

            if "name" not in term:
                self.module.fail_json(msg=f"Missing required 'name' field from search term, got: '{term}'")

            term["field"] = term.get("field", "password")
            term["section"] = term.get("section")
            term["vault"] = term.get("vault")

            processed_terms.append(term)

        return processed_terms

    def get_raw(self, item_id, vault=None):
        with self._runner("_item_get item_id vault session") as ctx:
            rc, out, err = ctx.run(item_id=item_id, vault=vault, session=self.token)
        if rc != 0:
            if "not found" in err.lower():
                self.module.fail_json(msg=f"Unable to find an item in 1Password named '{item_id}'.")
            self.module.fail_json(
                msg=f"Unexpected error attempting to find an item in 1Password named '{item_id}': {err}"
            )
        return out

    def get_field(self, item_id, field, section=None, vault=None):
        output = self.get_raw(item_id, vault)
        return self._parse_field(output, item_id, field, section) if output else ""

    def full_login(self):
        if self.auto_login is None:
            self.module.fail_json(
                msg=f"Unable to perform an initial sign in to 1Password. Please run '{self.cli_path} signin' "
                "or define credentials in 'auto_login'. See the module documentation for details."
            )

        if None in [
            self.auto_login.get("subdomain"),
            self.auto_login.get("username"),
            self.auto_login.get("secret_key"),
            self.auto_login.get("master_password"),
        ]:
            self.module.fail_json(
                msg="Unable to perform initial sign in to 1Password. "
                "subdomain, username, secret_key, and master_password are required to perform initial sign in."
            )

        subdomain = self.auto_login["subdomain"]
        with self._runner(
            "_account_add address email",
            data=to_bytes(self.auto_login["master_password"]),
            environ_update={"OP_SECRET_KEY": self.auto_login["secret_key"]},
        ) as ctx:
            rc, out, err = ctx.run(
                address=f"{subdomain}.1password.com",
                email=self.auto_login["username"],
            )
        if rc != 0:
            self.module.fail_json(msg=f"Failed to perform initial sign in to 1Password: {err}")
        self.token = out.strip()

    def get_token(self):
        config_path = self._config.config_file_path
        if config_path and os.path.isfile(config_path) and self.auto_login is not None:
            if not self.auto_login.get("master_password"):
                self.module.fail_json(msg="Unable to sign in to 1Password. 'auto_login.master_password' is required.")

            with self._runner("_signin account", data=to_bytes(self.auto_login["master_password"])) as ctx:
                rc, out, err = ctx.run(account=self.auto_login.get("subdomain"))
            if rc == 0:
                self.token = out.strip()
                return

        self.full_login()

    def assert_logged_in(self):
        subdomain = self.auto_login.get("subdomain") if self.auto_login else None
        account = f"{subdomain}.1password.com" if subdomain else None

        with self._runner("_account_list account") as ctx:
            rc, out, err = ctx.run(account=account)
        if rc == 0 and out.strip():
            with self._runner("_account_get account") as ctx:
                rc, out, err = ctx.run(account=account)
            if rc == 0:
                self.logged_in = True

        if not self.logged_in:
            self.get_token()

    def run(self):
        result = {}

        self.assert_logged_in()

        for term in self.terms:
            value = self.get_field(term["name"], term["field"], term["section"], term["vault"])

            if term["name"] in result:
                # Two search terms for the same item — merge the field dicts.
                result[term["name"]].update(value)
            else:
                result[term["name"]] = value

        return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cli_path=dict(type="path", default="op"),
            auto_login=dict(
                type="dict",
                options=dict(
                    subdomain=dict(type="str"),
                    username=dict(type="str"),
                    master_password=dict(required=True, type="str", no_log=True),
                    secret_key=dict(type="str", no_log=True),
                ),
            ),
            search_terms=dict(required=True, type="list", elements="dict"),
        ),
        supports_check_mode=True,
    )

    results = {"onepassword": OnePasswordInfo(module).run()}

    module.exit_json(changed=False, **results)


if __name__ == "__main__":
    main()

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
          - The name of the field to search for within this item (optional, defaults to V(password), or V(document) if the
            item has an attachment).
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
      - name: A 1Password item with document attachment
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
    "A 1Password item with document attachment":
      document: the contents of the document attached to this item
"""


import errno
import json
import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils._onepassword import OnePasswordConfig
from ansible_collections.community.general.plugins.module_utils._onepassword_cli import OnePassCLIv2, OnePasswordError


class OnePasswordInfo:
    def __init__(self, module):
        self.module = module
        self.cli_path = self.module.params["cli_path"]
        self.auto_login = self.module.params["auto_login"]
        self.logged_in = False
        self.token = None

        terms = self.module.params["search_terms"]
        self.terms = self.parse_search_terms(terms)

        self._config = OnePasswordConfig()

        auto_login = self.auto_login or dict.fromkeys(["subdomain", "username", "secret_key", "master_password"])
        self._cli = OnePassCLIv2(
            subdomain=auto_login["subdomain"],
            username=auto_login["username"],
            secret_key=auto_login["secret_key"],
            master_password=auto_login["master_password"],
            cli_path=self.cli_path,
            run_command=self.run_command,
        )

    def run_command(self, command, command_input=None, environment_update=None):
        rc, out, err = self.module.run_command(
            command,
            data=command_input,
            check_rc=False,
            binary_data=True,
            encoding=None,
            environ_update=environment_update,
        )
        return rc, out, to_native(err)

    def parse_field(self, data_json, item_id, field_name, section_title=None):
        data = json.loads(data_json)

        if data.get("category") == "DOCUMENT":
            # This is actually a document, let's fetch the document data instead!
            document = self._cli.get_document(data["title"], token=self.token)
            return {"document": document[1].strip()}

        else:
            # This is not a document, let's try to find the requested field
            value = self._cli._find_field(data_json, field_name, section_title)
            if value is not None:
                return {field_name: value}

        # We will get here if the field could not be found in any section and the item wasn't a document to be downloaded.
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
        try:
            rc, output, dummy = self._cli.get_raw(item_id, vault, self.token)
            return output

        except Exception as e:
            if re.search(".*isn't an item.*", f"{e}"):
                self.module.fail_json(msg=f"Unable to find an item in 1Password named '{item_id}'.")
            else:
                self.module.fail_json(
                    msg=f"Unexpected error attempting to find an item in 1Password named '{item_id}': {e}"
                )

    def get_field(self, item_id, field, section=None, vault=None):
        output = self.get_raw(item_id, vault)
        return self.parse_field(output, item_id, field, section) if output != "" else ""

    def full_login(self):
        if self.auto_login is not None:
            if None in [
                self.auto_login["subdomain"],
                self.auto_login["username"],
                self.auto_login["secret_key"],
                self.auto_login["master_password"],
            ]:
                self.module.fail_json(
                    msg="Unable to perform initial sign in to 1Password. "
                    "subdomain, username, secret_key, and master_password are required to perform initial sign in."
                )

            try:
                rc, out, err = self._cli.full_signin()
                self.token = out.strip()
            except OnePasswordError as e:
                self.module.fail_json(msg=f"Failed to perform initial sign in to 1Password: {e}")
        else:
            self.module.fail_json(
                msg=f"Unable to perform an initial sign in to 1Password. Please run '{self.cli_path} signin' "
                "or define credentials in 'auto_login'. See the module documentation for details."
            )

    def get_token(self):
        # If the config file exists, assume an initial signin has taken place and try basic sign in
        if os.path.isfile(self._config.config_file_path):
            if self.auto_login is not None:
                # Since we are not currently signed in, master_password is required at a minimum
                if not self.auto_login["master_password"]:
                    self.module.fail_json(
                        msg="Unable to sign in to 1Password. 'auto_login.master_password' is required."
                    )

                # Try signing in using the master_password and a subdomain if one is provided
                try:
                    rc, out, err = self._cli.signin()
                    self.token = out.strip()

                except OnePasswordError:
                    self.full_login()

            else:
                self.full_login()

        else:
            # Attempt a full sign in since there appears to be no existing sign in
            self.full_login()

    def assert_logged_in(self):
        try:
            if self._cli.assert_logged_in():
                self.logged_in = True
            if not self.logged_in:
                self.get_token()
        except OnePasswordError:
            self.get_token()
        except OSError as e:
            if e.errno == errno.ENOENT:
                self.module.fail_json(
                    msg=f"1Password CLI tool '{self.cli_path}' not installed in path on control machine"
                )
            raise e

    def run(self):
        result = {}

        self.assert_logged_in()

        for term in self.terms:
            value = self.get_field(term["name"], term["field"], term["section"], term["vault"])

            if term["name"] in result:
                # If we already have a result for this key, we have to append this result dictionary
                # to the existing one. This is only applicable when there is a single item
                # in 1Password which has two different fields, and we want to retrieve both of them.
                result[term["name"]].update(value)
            else:
                # If this is the first result for this key, simply set it.
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
    module.run_command_environ_update = {"LANGUAGE": "C", "LC_ALL": "C"}

    results = {"onepassword": OnePasswordInfo(module).run()}

    module.exit_json(changed=False, **results)


if __name__ == "__main__":
    main()

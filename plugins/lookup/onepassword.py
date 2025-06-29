# -*- coding: utf-8 -*-
# Copyright (c) 2018, Scott Buchanan <scott@buchanan.works>
# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
name: onepassword
author:
  - Scott Buchanan (@scottsb)
  - Andrew Zenk (@azenk)
  - Sam Doran (@samdoran)
short_description: Fetch field values from 1Password
description:
  - P(community.general.onepassword#lookup) wraps the C(op) command line utility to fetch specific field values from 1Password.
requirements:
  - C(op) 1Password command line utility
options:
  _terms:
    description: Identifier(s) (case-insensitive UUID or name) of item(s) to retrieve.
    required: true
    type: list
    elements: string
  account_id:
    version_added: 7.5.0
  domain:
    version_added: 3.2.0
  field:
    description: Field to return from each matching item (case-insensitive).
    default: 'password'
    type: str
  service_account_token:
    version_added: 7.1.0
extends_documentation_fragment:
  - community.general.onepassword
  - community.general.onepassword.lookup
"""

EXAMPLES = r"""
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
    var: lookup('community.general.onepassword', 'HAL 9000', subdomain='Discovery', master_password=vault_master_password)

- name: Retrieve password for HAL when never signed in to 1Password
  ansible.builtin.debug:
    var: >-
      lookup('community.general.onepassword', 'HAL 9000', subdomain='Discovery', master_password=vault_master_password,
             username='tweety@acme.com', secret_key=vault_secret_key)

- name: Retrieve password from specific account
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'HAL 9000', account_id='abc123')
"""

RETURN = r"""
_raw:
  description: Field data requested.
  type: list
  elements: str
"""

import abc
import os
import json
import subprocess

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError, AnsibleOptionsError
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.six import with_metaclass

from ansible_collections.community.general.plugins.module_utils.onepassword import OnePasswordConfig


def _lower_if_possible(value):
    """Return the lower case version value, otherwise return the value"""
    try:
        return value.lower()
    except AttributeError:
        return value


class OnePassCLIBase(with_metaclass(abc.ABCMeta, object)):
    bin = "op"

    def __init__(
        self,
        subdomain=None,
        domain="1password.com",
        username=None,
        secret_key=None,
        master_password=None,
        service_account_token=None,
        account_id=None,
        connect_host=None,
        connect_token=None,
    ):
        self.subdomain = subdomain
        self.domain = domain
        self.username = username
        self.master_password = master_password
        self.secret_key = secret_key
        self.service_account_token = service_account_token
        self.account_id = account_id
        self.connect_host = connect_host
        self.connect_token = connect_token

        self._path = None
        self._version = None

    def _check_required_params(self, required_params):
        non_empty_attrs = {param: getattr(self, param) for param in required_params if getattr(self, param, None)}
        missing = set(required_params).difference(non_empty_attrs)
        if missing:
            prefix = "Unable to sign in to 1Password. Missing required parameter"
            plural = ""
            suffix = f": {', '.join(missing)}."
            if len(missing) > 1:
                plural = "s"

            msg = f"{prefix}{plural}{suffix}"
            raise AnsibleLookupError(msg)

    @abc.abstractmethod
    def _parse_field(self, data_json, field_name, section_title):
        """Main method for parsing data returned from the op command line tool"""

    def _run(self, args, expected_rc=0, command_input=None, ignore_errors=False, environment_update=None):
        command = [self.path] + args
        call_kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.PIPE,
        }

        if environment_update:
            env = os.environ.copy()
            env.update(environment_update)
            call_kwargs["env"] = env

        p = subprocess.Popen(command, **call_kwargs)
        out, err = p.communicate(input=command_input)
        rc = p.wait()

        if not ignore_errors and rc != expected_rc:
            raise AnsibleLookupError(str(err))

        return rc, out, err

    @abc.abstractmethod
    def assert_logged_in(self):
        """Check whether a login session exists"""

    @abc.abstractmethod
    def full_signin(self):
        """Performa full login"""

    @abc.abstractmethod
    def get_raw(self, item_id, vault=None, token=None):
        """Gets the specified item from the vault"""

    @abc.abstractmethod
    def signin(self):
        """Sign in using the master password"""

    @property
    def path(self):
        if self._path is None:
            self._path = get_bin_path(self.bin)

        return self._path

    @property
    def version(self):
        if self._version is None:
            self._version = self.get_current_version()

        return self._version

    @classmethod
    def get_current_version(cls):
        """Standalone method to get the op CLI version. Useful when determining which class to load
        based on the current version."""
        try:
            bin_path = get_bin_path(cls.bin)
        except ValueError:
            raise AnsibleLookupError(f"Unable to locate '{cls.bin}' command line tool")

        try:
            b_out = subprocess.check_output([bin_path, "--version"], stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            raise AnsibleLookupError(f"Unable to get the op version: {cpe}")

        return to_text(b_out).strip()


class OnePassCLIv1(OnePassCLIBase):
    supports_version = "1"

    def _parse_field(self, data_json, field_name, section_title):
        """
        Retrieves the desired field from the `op` response payload

        When the item is a `password` type, the password is a key within the `details` key:

        $ op get item 'test item' | jq
        {
          [...]
          "templateUuid": "005",
          "details": {
            "notesPlain": "",
            "password": "foobar",
            "passwordHistory": [],
            "sections": [
              {
                "name": "linked items",
                "title": "Related Items"
              }
            ]
          },
          [...]
        }

        However, when the item is a `login` type, the password is within a fields array:

        $ op get item 'test item' | jq
        {
          [...]
          "details": {
            "fields": [
              {
                "designation": "username",
                "name": "username",
                "type": "T",
                "value": "foo"
              },
              {
                "designation": "password",
                "name": "password",
                "type": "P",
                "value": "bar"
              }
            ],
            [...]
          },
          [...]
        """
        data = json.loads(data_json)
        if section_title is None:
            # https://github.com/ansible-collections/community.general/pull/1610:
            # check the details dictionary for `field_name` and return it immediately if it exists
            # when the entry is a "password" instead of a "login" item, the password field is a key
            # in the `details` dictionary:
            if field_name in data["details"]:
                return data["details"][field_name]

            # when the field is not found above, iterate through the fields list in the object details
            for field_data in data["details"].get("fields", []):
                if field_data.get("name", "").lower() == field_name.lower():
                    return field_data.get("value", "")

        for section_data in data["details"].get("sections", []):
            if section_title is not None and section_title.lower() != section_data["title"].lower():
                continue

            for field_data in section_data.get("fields", []):
                if field_data.get("t", "").lower() == field_name.lower():
                    return field_data.get("v", "")

        return ""

    def assert_logged_in(self):
        args = ["get", "account"]
        if self.account_id:
            args.extend(["--account", self.account_id])
        elif self.subdomain:
            account = f"{self.subdomain}.{self.domain}"
            args.extend(["--account", account])

        rc, out, err = self._run(args, ignore_errors=True)

        return not bool(rc)

    def full_signin(self):
        if self.connect_host or self.connect_token:
            raise AnsibleLookupError(
                "1Password Connect is not available with 1Password CLI version 1. Please use version 2 or later.")

        if self.service_account_token:
            raise AnsibleLookupError(
                "1Password CLI version 1 does not support Service Accounts. Please use version 2 or later.")

        required_params = [
            "subdomain",
            "username",
            "secret_key",
            "master_password",
        ]
        self._check_required_params(required_params)

        args = [
            "signin",
            f"{self.subdomain}.{self.domain}",
            to_bytes(self.username),
            to_bytes(self.secret_key),
            "--raw",
        ]

        return self._run(args, command_input=to_bytes(self.master_password))

    def get_raw(self, item_id, vault=None, token=None):
        args = ["get", "item", item_id]

        if self.account_id:
            args.extend(["--account", self.account_id])

        if vault is not None:
            args += [f"--vault={vault}"]

        if token is not None:
            args += [to_bytes("--session=") + token]

        return self._run(args)

    def signin(self):
        self._check_required_params(['master_password'])

        args = ["signin", "--raw"]
        if self.subdomain:
            args.append(self.subdomain)

        return self._run(args, command_input=to_bytes(self.master_password))


class OnePassCLIv2(OnePassCLIBase):
    """
    CLIv2 Syntax Reference: https://developer.1password.com/docs/cli/upgrade#step-2-update-your-scripts
    """
    supports_version = "2"

    def _parse_field(self, data_json, field_name, section_title=None):
        """
        Schema reference: https://developer.1password.com/docs/cli/item-template-json

        Example Data:

            # Password item
            {
              "id": "ywvdbojsguzgrgnokmcxtydgdv",
              "title": "Authy Backup",
              "version": 1,
              "vault": {
                "id": "bcqxysvcnejjrwzoqrwzcqjqxc",
                "name": "Personal"
              },
              "category": "PASSWORD",
              "last_edited_by": "7FUPZ8ZNE02KSHMAIMKHIVUE17",
              "created_at": "2015-01-18T13:13:38Z",
              "updated_at": "2016-02-20T16:23:54Z",
              "additional_information": "Jan 18, 2015, 08:13:38",
              "fields": [
                {
                  "id": "password",
                  "type": "CONCEALED",
                  "purpose": "PASSWORD",
                  "label": "password",
                  "value": "OctoberPoppyNuttyDraperySabbath",
                  "reference": "op://Personal/Authy Backup/password",
                  "password_details": {
                    "strength": "FANTASTIC"
                  }
                },
                {
                  "id": "notesPlain",
                  "type": "STRING",
                  "purpose": "NOTES",
                  "label": "notesPlain",
                  "value": "Backup password to restore Authy",
                  "reference": "op://Personal/Authy Backup/notesPlain"
                }
              ]
            }

            # Login item
            {
              "id": "awk4s2u44fhnrgppszcsvc663i",
              "title": "Dummy Login",
              "version": 2,
              "vault": {
                "id": "stpebbaccrq72xulgouxsk4p7y",
                "name": "Personal"
              },
              "category": "LOGIN",
              "last_edited_by": "LSGPJERUYBH7BFPHMZ2KKGL6AU",
              "created_at": "2018-04-25T21:55:19Z",
              "updated_at": "2018-04-25T21:56:06Z",
              "additional_information": "agent.smith",
              "urls": [
                {
                  "primary": true,
                  "href": "https://acme.com"
                }
              ],
              "sections": [
                {
                  "id": "linked items",
                  "label": "Related Items"
                }
              ],
              "fields": [
                {
                  "id": "username",
                  "type": "STRING",
                  "purpose": "USERNAME",
                  "label": "username",
                  "value": "agent.smith",
                  "reference": "op://Personal/Dummy Login/username"
                },
                {
                  "id": "password",
                  "type": "CONCEALED",
                  "purpose": "PASSWORD",
                  "label": "password",
                  "value": "Q7vFwTJcqwxKmTU]Dzx7NW*wrNPXmj",
                  "entropy": 159.6083697084228,
                  "reference": "op://Personal/Dummy Login/password",
                  "password_details": {
                    "entropy": 159,
                    "generated": true,
                    "strength": "FANTASTIC"
                  }
                },
                {
                  "id": "notesPlain",
                  "type": "STRING",
                  "purpose": "NOTES",
                  "label": "notesPlain",
                  "reference": "op://Personal/Dummy Login/notesPlain"
                }
              ]
            }
        """
        data = json.loads(data_json)
        field_name = _lower_if_possible(field_name)
        for field in data.get("fields", []):
            if section_title is None:
                # If the field name exists in the section, return that value
                if field.get(field_name):
                    return field.get(field_name)

                # If the field name doesn't exist in the section, match on the value of "label"
                # then "id" and return "value"
                if field.get("label", "").lower() == field_name:
                    return field.get("value", "")

                if field.get("id", "").lower() == field_name:
                    return field.get("value", "")

            # Look at the section data and get an identifier. The value of 'id' is either a unique ID
            # or a human-readable string. If a 'label' field exists, prefer that since
            # it is the value visible in the 1Password UI when both 'id' and 'label' exist.
            section = field.get("section", {})
            section_title = _lower_if_possible(section_title)

            current_section_title = section.get("label", section.get("id", "")).lower()
            if section_title == current_section_title:
                # In the correct section. Check "label" then "id" for the desired field_name
                if field.get("label", "").lower() == field_name:
                    return field.get("value", "")

                if field.get("id", "").lower() == field_name:
                    return field.get("value", "")

        return ""

    def assert_logged_in(self):
        if self.connect_host and self.connect_token:
            return True

        if self.service_account_token:
            args = ["whoami"]
            environment_update = {"OP_SERVICE_ACCOUNT_TOKEN": self.service_account_token}
            rc, out, err = self._run(args, environment_update=environment_update)

            return not bool(rc)

        args = ["account", "list"]
        if self.subdomain:
            account = f"{self.subdomain}.{self.domain}"
            args.extend(["--account", account])

        rc, out, err = self._run(args)

        if out:
            # Running 'op account get' if there are no accounts configured on the system drops into
            # an interactive prompt. Only run 'op account get' after first listing accounts to see
            # if there are any previously configured accounts.
            args = ["account", "get"]
            if self.account_id:
                args.extend(["--account", self.account_id])
            elif self.subdomain:
                account = f"{self.subdomain}.{self.domain}"
                args.extend(["--account", account])

            rc, out, err = self._run(args, ignore_errors=True)

            return not bool(rc)

        return False

    def full_signin(self):
        required_params = [
            "subdomain",
            "username",
            "secret_key",
            "master_password",
        ]
        self._check_required_params(required_params)

        args = [
            "account", "add", "--raw",
            "--address", f"{self.subdomain}.{self.domain}",
            "--email", to_bytes(self.username),
            "--signin",
        ]

        environment_update = {"OP_SECRET_KEY": self.secret_key}
        return self._run(args, command_input=to_bytes(self.master_password), environment_update=environment_update)

    def _add_parameters_and_run(self, args, vault=None, token=None):
        if self.account_id:
            args.extend(["--account", self.account_id])

        if vault is not None:
            args += [f"--vault={vault}"]

        if self.connect_host and self.connect_token:
            if vault is None:
                raise AnsibleLookupError("'vault' is required with 1Password Connect")
            environment_update = {
                "OP_CONNECT_HOST": self.connect_host,
                "OP_CONNECT_TOKEN": self.connect_token,
            }
            return self._run(args, environment_update=environment_update)

        if self.service_account_token:
            if vault is None:
                raise AnsibleLookupError("'vault' is required with 'service_account_token'")
            environment_update = {"OP_SERVICE_ACCOUNT_TOKEN": self.service_account_token}
            return self._run(args, environment_update=environment_update)

        if token is not None:
            args += [to_bytes("--session=") + token]

        return self._run(args)

    def get_raw(self, item_id, vault=None, token=None):
        args = ["item", "get", item_id, "--format", "json"]
        return self._add_parameters_and_run(args, vault=vault, token=token)

    def signin(self):
        self._check_required_params(['master_password'])

        args = ["signin", "--raw"]
        if self.subdomain:
            args.extend(["--account", self.subdomain])

        return self._run(args, command_input=to_bytes(self.master_password))


class OnePass(object):
    def __init__(self, subdomain=None, domain="1password.com", username=None, secret_key=None, master_password=None,
                 service_account_token=None, account_id=None, connect_host=None, connect_token=None, cli_class=None):
        self.subdomain = subdomain
        self.domain = domain
        self.username = username
        self.secret_key = secret_key
        self.master_password = master_password
        self.service_account_token = service_account_token
        self.account_id = account_id
        self.connect_host = connect_host
        self.connect_token = connect_token

        self.logged_in = False
        self.token = None

        self._config = OnePasswordConfig()
        self._cli = self._get_cli_class(cli_class)

        if (self.connect_host or self.connect_token) and None in (self.connect_host, self.connect_token):
            raise AnsibleOptionsError("connect_host and connect_token are required together")

    def _get_cli_class(self, cli_class=None):
        if cli_class is not None:
            return cli_class(self.subdomain, self.domain, self.username, self.secret_key, self.master_password, self.service_account_token)

        version = OnePassCLIBase.get_current_version()
        for cls in OnePassCLIBase.__subclasses__():
            if cls.supports_version == version.split(".")[0]:
                try:
                    return cls(self.subdomain, self.domain, self.username, self.secret_key, self.master_password, self.service_account_token,
                               self.account_id, self.connect_host, self.connect_token)
                except TypeError as e:
                    raise AnsibleLookupError(e)

        raise AnsibleLookupError(f"op version {version} is unsupported")

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
        subdomain = self.get_option("subdomain")
        domain = self.get_option("domain")
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
        )
        op.assert_logged_in()

        values = []
        for term in terms:
            values.append(op.get_field(term, field, section, vault))

        return values

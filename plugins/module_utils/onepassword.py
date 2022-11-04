# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import abc
import json
import subprocess

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.six import with_metaclass


class OnePassCLIBase(with_metaclass(abc.ABCMeta, object)):
    bin = "op"

    def __init__(self, subdomain=None, domain="1password.com", username=None, secret_key=None, master_password=None):
        self.subdomain = subdomain
        self.domain = domain
        self.username = username
        self.master_password = master_password
        self.secret_key = secret_key

        self._path = None
        self._version = None

    def _check_required_params(self, required_params):
        non_empty_attrs = dict((param, getattr(self, param, None)) for param in required_params if getattr(self, param, None))
        missing = set(required_params).difference(non_empty_attrs)
        if missing:
            prefix = "Unable to sign in to 1Password. Missing required parameter"
            plural = ""
            suffix = ": {params}.".format(params=", ".join(missing))
            if len(missing) > 1:
                plural = "s"

            msg = "{prefix}{plural}{suffix}".format(prefix=prefix, plural=plural, suffix=suffix)
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
            raise AnsibleLookupError(to_text(err))

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
            raise AnsibleLookupError("Unable to locate '%s' command line tool" % cls.bin)

        try:
            b_out = subprocess.check_output([bin_path, "--version"], stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as cpe:
            raise AnsibleLookupError("Unable to get the op version: %s" % cpe)

        return to_text(b_out).strip()


class OnePassCLIv1(OnePassCLIBase):
    # TODO: Should supports_version be a tuple?
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
        if self.subdomain:
            account = "{subdomain}.{domain}".format(subdomain=self.subdomain, domain=self.domain)
            args.extend(["--account", account])

        rc, out, err = self._run(args, ignore_errors=True)

        return not bool(rc)

    def full_signin(self):
        required_params = [
            "subdomain",
            "username",
            "secret_key",
            "master_password",
        ]
        self._check_required_params(required_params)

        args = [
            "signin",
            "{0}.{1}".format(self.subdomain, self.domain),
            to_bytes(self.username),
            to_bytes(self.secret_key),
            "--raw",
        ]

        return self._run(args, command_input=to_bytes(self.master_password))

    def get_raw(self, item_id, vault=None, token=None):
        args = ["get", "item", item_id]
        if vault is not None:
            args += ["--vault={0}".format(vault)]

        if token is not None:
            args += [to_bytes("--session=") + token]  # FIXME: Why is only this bytes?

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
        for field in data.get("fields", []):
            if section_title is None:
                # If the field name exists in the section, return that value
                if field.get(field_name):
                    return field.get(field_name)

                # If the field name doesn't exist in the section, match on the value of "label"
                # then "id" and return "value"
                if field.get("label") == field_name:
                    return field["value"]

                if field.get("id") == field_name:
                    return field["value"]

            # Match on the section name.
            # TODO: This returns t
            if field.get("section", {}).get("label") == field_name:
                return field["value"]

            if field.get("section", {}).get("id") == field_name:
                return field["value"]

        return ""

    def assert_logged_in(self):
        args = ["account", "list"]
        if self.subdomain:
            account = "{subdomain}.{domain}".format(subdomain=self.subdomain, domain=self.domain)
            args.extend(["--account", account])

        rc, out, err = self._run(args)

        if out:
            # Running 'op account get' if there are no accounts configured on the system drops into
            # an interactive prompt. Only run 'op account get' after first listing accounts to see
            # if there are any previously configured accounts.
            args = ["account", "get"]
            if self.subdomain:
                account = "{subdomain}.{domain}".format(subdomain=self.subdomain, domain=self.domain)
                args.extend(["--account", account])

            rc, out, err = self._run(args)

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
            "--address", "{0}.{1}".format(self.subdomain, self.domain),
            "--email", to_bytes(self.username),
            "--signin",
        ]

        environment_update = {"OP_SECRET_KEY": self.secret_key}
        return self._run(args, command_input=to_bytes(self.master_password), environment_update=environment_update)

    def get_raw(self, item_id, vault=None, token=None):
        args = ["item", "get", item_id, "--format", "json"]
        if vault is not None:
            args += ["--vault={0}".format(vault)]
        if token is not None:
            args += [to_bytes("--session=") + token]  # FIXME: Why is only this bytes?

        return self._run(args)

    def signin(self):
        self._check_required_params(['master_password'])

        args = ["signin", "--raw"]
        if self.subdomain:
            args.extend(["--account", self.subdomain])

        return self._run(args, command_input=to_bytes(self.master_password))


class OnePasswordConfig(object):
    _config_file_paths = (
        "~/.op/config",
        "~/.config/op/config",
        "~/.config/.op/config",
    )

    def __init__(self):
        self._config_file_path = ""

    @property
    def config_file_path(self):
        if self._config_file_path:
            return self._config_file_path

        for path in self._config_file_paths:
            realpath = os.path.expanduser(path)
            if os.path.exists(realpath):
                self._config_file_path = realpath
                return self._config_file_path

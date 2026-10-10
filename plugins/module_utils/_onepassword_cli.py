# Copyright (c) 2018, Scott Buchanan <scott@buchanan.works>
# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import abc
import json
import os

from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text

from ansible_collections.community.general.plugins.module_utils._onepassword import OnePasswordConfig


class OnePasswordError(Exception):
    pass


class OnePasswordOptionsError(OnePasswordError):
    pass


def _lower_if_possible(value):
    """Return the lower case version value, otherwise return the value"""
    try:
        return value.lower()
    except AttributeError:
        return value


class OnePassCLIBase(metaclass=abc.ABCMeta):
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
        cli_path=None,
        run_command=None,
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
        self.run_command = run_command

        self._path = cli_path
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
            raise OnePasswordError(msg)

    @abc.abstractmethod
    def _parse_field(self, data_json, field_name, section_title):
        """Main method for parsing data returned from the op command line tool"""

    def _run(self, args, expected_rc=0, command_input=None, ignore_errors=False, environment_update=None):
        command = [self.path] + args
        rc, out, err = self.run_command(command, command_input=command_input, environment_update=environment_update)

        if not ignore_errors and rc != expected_rc:
            raise OnePasswordError(str(err))

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
            self._version = self.get_current_version(run_command=self.run_command)

        return self._version

    @classmethod
    def get_current_version(cls, run_command=None):
        """Standalone method to get the op CLI version. Useful when determining which class to load
        based on the current version."""
        try:
            bin_path = get_bin_path(cls.bin)
        except ValueError as e:
            raise OnePasswordError(f"Unable to locate '{cls.bin}' command line tool") from e

        command = [bin_path, "--version"]
        rc, out, err = run_command(command)
        if rc != 0:
            raise OnePasswordError(
                f"Unable to get the op version: Command '{command}' returned non-zero exit status {rc}."
            )

        return to_text(out).strip()


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
        value = self._find_field(data_json, field_name, section_title)
        return "" if value is None else value

    def _find_field(self, data_json, field_name, section_title=None):
        """Same as _parse_field(), but returns None when the field is not found"""
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

        return None

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
            "account",
            "add",
            "--raw",
            "--address",
            f"{self.subdomain}.{self.domain}",
            "--email",
            to_bytes(self.username),
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
                raise OnePasswordError("'vault' is required with 1Password Connect")
            environment_update = {
                "OP_CONNECT_HOST": self.connect_host,
                "OP_CONNECT_TOKEN": self.connect_token,
            }
            return self._run(args, environment_update=environment_update)

        if self.service_account_token:
            if vault is None:
                raise OnePasswordError("'vault' is required with 'service_account_token'")
            environment_update = {"OP_SERVICE_ACCOUNT_TOKEN": self.service_account_token}
            return self._run(args, environment_update=environment_update)

        if token is not None:
            args += [to_bytes("--session=") + token]

        return self._run(args)

    def get_raw(self, item_id, vault=None, token=None):
        args = ["item", "get", item_id, "--format", "json"]
        return self._add_parameters_and_run(args, vault=vault, token=token)

    def get_document(self, item_id, vault=None, token=None):
        args = ["document", "get", item_id]
        return self._add_parameters_and_run(args, vault=vault, token=token)

    def get_secret_reference(self, reference, token=None):
        args = ["read", reference]
        return self._add_parameters_and_run(args, token=token)

    def signin(self):
        self._check_required_params(["master_password"])

        args = ["signin", "--raw"]
        if self.subdomain:
            args.extend(["--account", self.subdomain])

        return self._run(args, command_input=to_bytes(self.master_password))


class OnePass:
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
        cli_class=None,
        run_command=None,
    ):
        self.subdomain = subdomain
        self.domain = domain
        self.username = username
        self.secret_key = secret_key
        self.master_password = master_password
        self.service_account_token = service_account_token
        self.account_id = account_id
        self.connect_host = connect_host
        self.connect_token = connect_token
        self.run_command = run_command

        self.logged_in = False
        self.token = None

        self._config = OnePasswordConfig()
        self._cli = self._get_cli_class(cli_class)

        if (self.connect_host or self.connect_token) and None in (self.connect_host, self.connect_token):
            raise OnePasswordOptionsError("connect_host and connect_token are required together")

    def _get_cli_class(self, cli_class=None):
        if cli_class is not None:
            return cli_class(
                self.subdomain,
                self.domain,
                self.username,
                self.secret_key,
                self.master_password,
                self.service_account_token,
                self.account_id,
                self.connect_host,
                self.connect_token,
                run_command=self.run_command,
            )

        version = OnePassCLIBase.get_current_version(run_command=self.run_command)
        for cls in OnePassCLIBase.__subclasses__():
            if cls.supports_version == version.split(".")[0]:
                try:
                    return cls(
                        self.subdomain,
                        self.domain,
                        self.username,
                        self.secret_key,
                        self.master_password,
                        self.service_account_token,
                        self.account_id,
                        self.connect_host,
                        self.connect_token,
                        run_command=self.run_command,
                    )
                except TypeError as e:
                    raise OnePasswordError(e) from e

        raise OnePasswordError(f"op version {version} is unsupported")

    def set_token(self):
        if self._config.config_file_path and os.path.isfile(self._config.config_file_path):
            # If the config file exists, assume an initial sign in has taken place and try basic sign in
            try:
                rc, out, err = self._cli.signin()
            except OnePasswordError as exc:
                test_strings = (
                    "missing required parameters",
                    "unauthorized",
                )
                if any(string in str(exc).lower() for string in test_strings):
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

    def get_secret_reference(self, reference):
        path = reference[5:]
        if not path:
            raise OnePasswordError("Secret references must have a path")
        # Split into parts, to check length in a second
        path_parts = [part for part in path.split("/") if part]

        # Must be 3 parts (vault,item,field) or 4 (vault,item,section,field)
        if len(path_parts) not in (3, 4):
            raise OnePasswordError("Not a valid secret reference")

        rc, out, err = self._cli.get_secret_reference(reference, self.token)
        return to_text(out).strip()

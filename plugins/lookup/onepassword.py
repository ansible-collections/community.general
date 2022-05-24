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
      - Tested with C(op) version 0.5.3
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

import abc
import errno
import json
import os
import subprocess

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.six import with_metaclass

from ansible_collections.community.general.plugins.module_utils.onepassword import OnePasswordConfig


class OnePassCLIBase(with_metaclass(abc.ABCMeta, object)):
    bin = "op"

    def __init__(self, subdomain, domain, master_password, secret_key, vault):
        self.subdomain = subdomain
        self.domain = domain
        self.master_password = master_password
        self.secret_key = secret_key
        self.vault = vault

        self._path = None
        self._version = None

    @abc.abstractmethod
    def get_account(self):
        pass

    @abc.abstractmethod
    def get_item(self, item_id):
        pass

    @abc.abstractmethod
    def signin(self):
        pass

    @abc.abstractmethod
    def _parse_field(self, data_json, field_name, section_title):
        pass

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
        """Standalone method to get the op CLI version. Useful when determing which class to load
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

    def _run(self, args, expected_rc=0, command_input=None, ignore_errors=False):
        command = [self.path] + args
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = p.communicate(input=command_input)
        rc = p.wait()
        if not ignore_errors and rc != expected_rc:
            raise AnsibleLookupError(to_text(err))

        return rc, out, err


class OnePassCLIv1(OnePassCLIBase):
    supports_version = "1"

    def get_account(self):
        pass

    def get_item(self, item_id):
        pass

    def signin(self):
        pass

    def _parse_field(self, data_json, field_name, section_title):
        pass


class OnePassCLIv2(OnePassCLIBase):
    supports_version = "2"

    def get_account(self):
        pass

    def get_item(self, item_id):
        pass

    def signin(self):
        pass

    def _parse_field(self, data_json, field_name, section_title):
        pass


class OnePass(object):
    def __init__(self, subdomain, domain, username, secret_key, master_password):
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
        version = OnePassCLIBase.get_current_version()
        for cls in OnePassCLIBase.__subclasses__():
            if cls.supports_version == version.split(".")[0]:
                try:
                    return cls(self.subdomain, self.domain, self.username, self.secret_key, self.master_password)
                except TypeError as e:
                    raise AnsibleLookupError(e)

        raise AnsibleLookupError("op version %s is unsupported" % version)

    def get_token(self):
        # If the config file exists, assume an initial signin has taken place and try basic sign in
        if os.path.isfile(self._config.config_file_path):

            if not self.master_password:
                raise AnsibleLookupError('Unable to sign in to 1Password. master_password is required.')

            try:
                args = ['signin', '--output=raw']

                if self.subdomain:
                    args = ['signin', self.subdomain, '--output=raw']

                rc, out, err = self._run(args, command_input=to_bytes(self.master_password))
                self.token = out.strip()

            except AnsibleLookupError:
                self.full_login()

        else:
            # Attempt a full sign in since there appears to be no existing sign in
            self.full_login()

    def assert_logged_in(self):
        try:
            rc, out, err = self._run(['get', 'account'], ignore_errors=True)
            if rc == 0:
                self.logged_in = True
            if not self.logged_in:
                self.get_token()
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise AnsibleLookupError("1Password CLI tool '%s' not installed in path on control machine" % self.cli_path)
            raise e

    def get_raw(self, item_id, vault=None):
        args = ["get", "item", item_id]
        if vault is not None:
            args += ['--vault={0}'.format(vault)]
        if not self.logged_in:
            args += [to_bytes('--session=') + self.token]
        rc, output, dummy = self._run(args)
        return output

    def get_field(self, item_id, field, section=None, vault=None):
        output = self.get_raw(item_id, vault)
        return self._parse_field(output, field, section) if output != '' else ''

    def full_login(self):
        if None in [self.subdomain, self.username, self.secret_key, self.master_password]:
            raise AnsibleLookupError('Unable to perform initial sign in to 1Password. '
                                     'subdomain, username, secret_key, and master_password are required to perform initial sign in.')

        args = [
            'signin',
            '{0}.{1}'.format(self.subdomain, self.domain),
            to_bytes(self.username),
            to_bytes(self.secret_key),
            '--output=raw',
        ]

        rc, out, err = self._run(args, command_input=to_bytes(self.master_password))
        self.token = out.strip()

    def _parse_field(self, data_json, field_name, section_title=None):
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
            if field_name in data['details']:
                return data['details'][field_name]

            # when the field is not found above, iterate through the fields list in the object details
            for field_data in data['details'].get('fields', []):
                if field_data.get('name', '').lower() == field_name.lower():
                    return field_data.get('value', '')
        for section_data in data['details'].get('sections', []):
            if section_title is not None and section_title.lower() != section_data['title'].lower():
                continue
            for field_data in section_data.get('fields', []):
                if field_data.get('t', '').lower() == field_name.lower():
                    return field_data.get('v', '')
        return ''


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        field = kwargs.get("field", "password")
        section = kwargs.get("section", "")
        vault = kwargs.get("vault", "")
        subdomain = kwargs.get("subdomain")
        domain = kwargs.get("domain", "1password.com")
        username = kwargs.get("username", "")
        secret_key = kwargs.get("secret_key", "")
        master_password = kwargs.get("master_password", kwargs.get("vault_password", ""))

        op = OnePass(subdomain, domain, username, secret_key, master_password)
        # op.assert_logged_in()

        values = []
        for term in terms:
            values.append(op.get_field(term, field, section, vault))

        return values

# -*- coding: utf-8 -*-
# Copyright (c) 2022, Jonathan Lung <lungj@heresjono.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: bitwarden
    author:
      - Jonathan Lung (@lungj) <lungj@heresjono.com>
    requirements:
      - bw (command line utility)
      - be logged into bitwarden
      - bitwarden vault unlocked
      - C(BW_SESSION) environment variable set
    short_description: Retrieve secrets from Bitwarden
    version_added: 5.4.0
    description:
      - Retrieve secrets from Bitwarden.
    options:
      _terms:
        description: Key(s) to fetch values for from login info.
        required: true
        type: list
        elements: str
      search:
        description: Field to retrieve, for example C(name) or C(id).
        type: str
        default: name
        version_added: 5.7.0
      field:
        description: Field to fetch. Leave unset to fetch whole response.
        type: str
      collection_id:
        description: Collection ID to filter results by collection. Leave unset to skip filtering.
        type: str
        version_added: 6.3.0
"""

EXAMPLES = """
- name: "Get 'password' from Bitwarden record named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='password') }}

- name: "Get 'password' from Bitwarden record with id 'bafba515-af11-47e6-abe3-af1200cd18b2'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'bafba515-af11-47e6-abe3-af1200cd18b2', search='id', field='password') }}

- name: "Get 'password' from Bitwarden record named 'a_test' from collection"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='password', collection_id='bafba515-af11-47e6-abe3-af1200cd18b2') }}

- name: "Get full Bitwarden record named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test') }}

- name: "Get custom field 'api_key' from Bitwarden record named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='api_key') }}
"""

RETURN = """
  _raw:
    description: List of requested field or JSON object of list of matches.
    type: list
    elements: raw
"""

from subprocess import Popen, PIPE

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.parsing.ajson import AnsibleJSONDecoder
from ansible.plugins.lookup import LookupBase


class BitwardenException(AnsibleError):
    pass


class Bitwarden(object):

    def __init__(self, path='bw'):
        self._cli_path = path

    @property
    def cli_path(self):
        return self._cli_path

    @property
    def unlocked(self):
        out, err = self._run(['status'], stdin="")
        decoded = AnsibleJSONDecoder().raw_decode(out)[0]
        return decoded['status'] == 'unlocked'

    def _run(self, args, stdin=None, expected_rc=0):
        p = Popen([self.cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(to_bytes(stdin))
        rc = p.wait()
        if rc != expected_rc:
            raise BitwardenException(err)
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict')

    def _get_matches(self, search_value, search_field, collection_id):
        """Return matching records whose search_field is equal to key.
        """

        # Prepare set of params for Bitwarden CLI
        params = ['list', 'items', '--search', search_value]

        if collection_id:
            params.extend(['--collectionid', collection_id])

        out, err = self._run(params)

        # This includes things that matched in different fields.
        initial_matches = AnsibleJSONDecoder().raw_decode(out)[0]

        # Filter to only include results from the right field.
        return [item for item in initial_matches if item[search_field] == search_value]

    def get_field(self, field, search_value, search_field="name", collection_id=None):
        """Return a list of the specified field for records whose search_field match search_value
        and filtered by collection if collection has been provided.

        If field is None, return the whole record for each match.
        """
        matches = self._get_matches(search_value, search_field, collection_id)

        if field in ['autofillOnPageLoad', 'password', 'passwordRevisionDate', 'totp', 'uris', 'username']:
            return [match['login'][field] for match in matches]
        elif not field:
            return matches
        else:
            custom_field_matches = []
            for match in matches:
                for custom_field in match['fields']:
                    if custom_field['name'] == field:
                        custom_field_matches.append(custom_field['value'])
            if matches and not custom_field_matches:
                raise AnsibleError("Custom field {field} does not exist in {search_value}".format(field=field, search_value=search_value))
            return custom_field_matches


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        field = self.get_option('field')
        search_field = self.get_option('search')
        collection_id = self.get_option('collection_id')
        if not _bitwarden.unlocked:
            raise AnsibleError("Bitwarden Vault locked. Run 'bw unlock'.")

        return [_bitwarden.get_field(field, term, search_field, collection_id) for term in terms]


_bitwarden = Bitwarden()

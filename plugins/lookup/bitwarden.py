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
      - E(BW_SESSION) environment variable set
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
        description:
          - Field to retrieve, for example V(name) or V(id).
          - If set to V(id), only zero or one element can be returned.
            Use the Jinja C(first) filter to get the only list element.
          - If set to V(None) or V(''), or if O(_terms) is empty, records are not filtered by fields.
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
      organization_id:
        description: Organization ID to filter results by organization. Leave unset to skip filtering.
        type: str
        version_added: 8.5.0
      bw_session:
        description: Pass session key instead of reading from env.
        type: str
        version_added: 8.4.0
"""

EXAMPLES = """
- name: "Get 'password' from all Bitwarden records named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='password') }}

- name: "Get 'password' from Bitwarden record with ID 'bafba515-af11-47e6-abe3-af1200cd18b2'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'bafba515-af11-47e6-abe3-af1200cd18b2', search='id', field='password') | first }}

- name: "Get 'password' from all Bitwarden records named 'a_test' from collection"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='password', collection_id='bafba515-af11-47e6-abe3-af1200cd18b2') }}

- name: "Get list of all full Bitwarden records named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test') }}

- name: "Get custom field 'api_key' from all Bitwarden records named 'a_test'"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='api_key') }}

- name: "Get 'password' from all Bitwarden records named 'a_test', using given session key"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', 'a_test', field='password', bw_session='bXZ9B5TXi6...') }}

- name: "Get all Bitwarden records from collection"
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.general.bitwarden', None, collection_id='bafba515-af11-47e6-abe3-af1200cd18b2') }}
"""

RETURN = """
  _raw:
    description:
      - A one-element list that contains a list of requested fields or JSON objects of matches.
      - If you use C(query), you get a list of lists. If you use C(lookup) without C(wantlist=true),
        this always gets reduced to a list of field values or JSON objects.
    type: list
    elements: list
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
        self._session = None

    @property
    def cli_path(self):
        return self._cli_path

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def unlocked(self):
        out, err = self._run(['status'], stdin="")
        decoded = AnsibleJSONDecoder().raw_decode(out)[0]
        return decoded['status'] == 'unlocked'

    def _run(self, args, stdin=None, expected_rc=0):
        if self.session:
            args += ['--session', self.session]

        p = Popen([self.cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(to_bytes(stdin))
        rc = p.wait()
        if rc != expected_rc:
            if len(args) > 2 and args[0] == 'get' and args[1] == 'item' and b'Not found.' in err:
                return 'null', ''
            raise BitwardenException(err)
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict')

    def _get_matches(self, search_value, search_field, collection_id=None, organization_id=None):
        """Return matching records whose search_field is equal to key.
        """

        # Prepare set of params for Bitwarden CLI
        if search_field == 'id':
            params = ['get', 'item', search_value]
        else:
            params = ['list', 'items']
            if search_value:
                params.extend(['--search', search_value])

        if collection_id:
            params.extend(['--collectionid', collection_id])
        if organization_id:
            params.extend(['--organizationid', organization_id])

        out, err = self._run(params)

        # This includes things that matched in different fields.
        initial_matches = AnsibleJSONDecoder().raw_decode(out)[0]

        if search_field == 'id':
            if initial_matches is None:
                initial_matches = []
            else:
                initial_matches = [initial_matches]

        # Filter to only include results from the right field, if a search is requested by value or field
        return [item for item in initial_matches
                if not search_value or not search_field or item.get(search_field) == search_value]

    def get_field(self, field, search_value, search_field="name", collection_id=None, organization_id=None):
        """Return a list of the specified field for records whose search_field match search_value
        and filtered by collection if collection has been provided.

        If field is None, return the whole record for each match.
        """
        matches = self._get_matches(search_value, search_field, collection_id, organization_id)
        if not field:
            return matches
        field_matches = []
        for match in matches:
            # if there are no custom fields, then `match` has no key 'fields'
            if 'fields' in match:
                custom_field_found = False
                for custom_field in match['fields']:
                    if field == custom_field['name']:
                        field_matches.append(custom_field['value'])
                        custom_field_found = True
                        break
                if custom_field_found:
                    continue
            if 'login' in match and field in match['login']:
                field_matches.append(match['login'][field])
                continue
            if field in match:
                field_matches.append(match[field])
                continue

        if matches and not field_matches:
            raise AnsibleError("field {field} does not exist in {search_value}".format(field=field, search_value=search_value))

        return field_matches


class LookupModule(LookupBase):

    def run(self, terms=None, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        field = self.get_option('field')
        search_field = self.get_option('search')
        collection_id = self.get_option('collection_id')
        organization_id = self.get_option('organization_id')
        _bitwarden.session = self.get_option('bw_session')

        if not _bitwarden.unlocked:
            raise AnsibleError("Bitwarden Vault locked. Run 'bw unlock'.")

        if not terms:
            terms = [None]

        return [_bitwarden.get_field(field, term, search_field, collection_id, organization_id) for term in terms]


_bitwarden = Bitwarden()

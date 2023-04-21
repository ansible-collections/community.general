# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
    name: bitwarden_secrets_manager
    author:
      - @jantari
    requirements:
      - bws (command line utility)
    short_description: Retrieve secrets from Bitwarden Secrets Manager
    version_added: ?.?.?
    description:
      - Retrieve secrets from Bitwarden Secrets Manager.
    options:
      _terms:
        description: Secret ID(s) to fetch values for.
        required: true
        type: list
        elements: str
      bws_access_token:
        description: A BWS access token to use for this lookup.
        type: str
"""

EXAMPLES = """
- name: "Get a secret relying on the BWS_ACCESS_TOKEN environment variable for authentication"
  ansible.builtin.debug:
    msg: >-
      {{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972") }}

- name: "Get a secret passing an explicit access token for authentication"
  ansible.builtin.debug:
    msg: >-
      {{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972", bws_access_token="9.4f570d14-4b54-42f5-bc07-60f4450b1db5.YmluYXJ5LXNvbWV0aGluZy0xMjMK:d2h5IGhlbGxvIHRoZXJlCg==") }}

- name: "Get two different secrets each using a different access token for authentication"
  ansible.builtin.debug:
    msg:
      - '{{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972", bws_access_token="9.4f570d14-4b54-42f5-bc07-60f4450b1db5.YmluYXJ5LXNvbWV0aGluZy0xMjMK:d2h5IGhlbGxvIHRoZXJlCg==") }}'
      - '{{ lookup("community.general.bitwarden_secrets_manager", "9d89af4c-eb5d-41f5-bb0f-4ae81215c768", bws_access_token="1.69b72797-6ea9-4687-a11e-848e41a30ae6.YW5zaWJsZSBpcyBncmVhdD8K:YW5zaWJsZSBpcyBncmVhdAo=") }}'

- name: "Get just the value of a secret"
  ansible.builtin.debug:
    msg: >-
      {{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972")[0].value }}
"""

RETURN = """
  _raw:
    description: List containing the secret JSON object. Guaranteed to be of length 1.
    type: list
    elements: raw
"""

import os
from subprocess import Popen, PIPE

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.parsing.ajson import AnsibleJSONDecoder
from ansible.plugins.lookup import LookupBase


class BitwardenException(AnsibleError):
    pass


class Bitwarden(object):

    def __init__(self, path='bws'):
        self._cli_path = path

    @property
    def cli_path(self):
        return self._cli_path

    def _run(self, args, stdin=None, expected_rc=0):
        p = Popen([self.cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(to_bytes(stdin))
        rc = p.wait()
        if rc != expected_rc:
            raise BitwardenException(err)
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict')

    def get_secret(self, secret_id, bws_access_token):
        """Get and return the secret with the given secret_id.
        """

        # Prepare set of params for Bitwarden Secrets Manager CLI
        # Color output was not always disabled correctly with the default 'auto' setting so explicitly disable it.
        params = [
            '--color', 'no',
            '--access-token', bws_access_token,
            'get', 'secret', secret_id
        ]

        out, err = self._run(params)

        # This includes things that matched in different fields.
        initial_matches = AnsibleJSONDecoder().raw_decode(out)[0]

        return [initial_matches]


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        bws_access_token = self.get_option('bws_access_token')

        if not bws_access_token:
            bws_access_token = os.getenv('BWS_ACCESS_TOKEN')

        if not bws_access_token:
            raise AnsibleError("No access token for Bitwarden Secrets Manager. Pass the bws_access_token parameter or set the BWS_ACCESS_TOKEN environment variable.")

        return [_bitwarden.get_secret(term, bws_access_token) for term in terms]


_bitwarden = Bitwarden()

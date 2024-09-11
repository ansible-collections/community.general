# -*- coding: utf-8 -*-
# Copyright (c) 2023, jantari (https://github.com/jantari)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
    name: bitwarden_secrets_manager
    author:
      - jantari (@jantari)
    requirements:
      - bws (command line utility)
    short_description: Retrieve secrets from Bitwarden Secrets Manager
    version_added: 7.2.0
    description:
      - Retrieve secrets from Bitwarden Secrets Manager.
    options:
      _terms:
        description: Secret ID(s) to fetch values for.
        required: true
        type: list
        elements: str
      bws_access_token:
        description: The BWS access token to use for this lookup.
        env:
          - name: BWS_ACCESS_TOKEN
        required: true
        type: str
"""

EXAMPLES = """
- name: Get a secret relying on the BWS_ACCESS_TOKEN environment variable for authentication
  ansible.builtin.debug:
    msg: >-
      {{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972") }}

- name: Get a secret passing an explicit access token for authentication
  ansible.builtin.debug:
    msg: >-
      {{
        lookup(
          "community.general.bitwarden_secrets_manager",
          "2bc23e48-4932-40de-a047-5524b7ddc972",
          bws_access_token="9.4f570d14-4b54-42f5-bc07-60f4450b1db5.YmluYXJ5LXNvbWV0aGluZy0xMjMK:d2h5IGhlbGxvIHRoZXJlCg=="
        )
      }}

- name: Get two different secrets each using a different access token for authentication
  ansible.builtin.debug:
    msg:
      - '{{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972", bws_access_token=token1) }}'
      - '{{ lookup("community.general.bitwarden_secrets_manager", "9d89af4c-eb5d-41f5-bb0f-4ae81215c768", bws_access_token=token2) }}'
  vars:
    token1: "9.4f570d14-4b54-42f5-bc07-60f4450b1db5.YmluYXJ5LXNvbWV0aGluZy0xMjMK:d2h5IGhlbGxvIHRoZXJlCg=="
    token2: "1.69b72797-6ea9-4687-a11e-848e41a30ae6.YW5zaWJsZSBpcyBncmVhdD8K:YW5zaWJsZSBpcyBncmVhdAo="

- name: Get just the value of a secret
  ansible.builtin.debug:
    msg: >-
      {{ lookup("community.general.bitwarden_secrets_manager", "2bc23e48-4932-40de-a047-5524b7ddc972").value }}
"""

RETURN = """
  _raw:
    description: List containing one or more secrets.
    type: list
    elements: dict
"""

from subprocess import Popen, PIPE
from time import sleep

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_text
from ansible.parsing.ajson import AnsibleJSONDecoder
from ansible.plugins.lookup import LookupBase


class BitwardenSecretsManagerException(AnsibleLookupError):
    pass


class BitwardenSecretsManager(object):
    def __init__(self, path='bws'):
        self._cli_path = path
        self._max_retries = 3
        self._retry_delay = 1

    @property
    def cli_path(self):
        return self._cli_path

    def _run_with_retry(self, args, stdin=None, retries=0):
        out, err, rc = self._run(args, stdin)

        if rc != 0:
            if retries >= self._max_retries:
                raise BitwardenSecretsManagerException("Max retries exceeded. Unable to retrieve secret.")

            if "Too many requests" in err:
                delay = self._retry_delay * (2 ** retries)
                sleep(delay)
                return self._run_with_retry(args, stdin, retries + 1)
            else:
                raise BitwardenSecretsManagerException(f"Command failed with return code {rc}: {err}")

        return out, err, rc

    def _run(self, args, stdin=None):
        p = Popen([self.cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(stdin)
        rc = p.wait()
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict'), rc

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

        out, err, rc = self._run_with_retry(params)
        if rc != 0:
            raise BitwardenSecretsManagerException(to_text(err))

        return AnsibleJSONDecoder().raw_decode(out)[0]


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        bws_access_token = self.get_option('bws_access_token')

        return [_bitwarden_secrets_manager.get_secret(term, bws_access_token) for term in terms]


_bitwarden_secrets_manager = BitwardenSecretsManager()

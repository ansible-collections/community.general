# -*- coding: utf-8 -*-
# Copyright: (c) 2021, RevBits <info@revbits.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: revbitspss
author: RevBits (@info) <info@revbits.com>
short_description: Get secrets from RevBits PAM server
version_added: 3.8.0
description:
    - Uses the revbits-ansible Python SDK to get Secrets from RevBits PAM
      Server using API key authentication with the REST API.
requirements:
    - revbits-ansible - U(https://pypi.org/project/revbits-ansible/)
options:
    _terms:
        description:
            - This will be an array. First index will conatin another array of keys for secrets which you want to fetch from RevBits PAM
            - At second index you need to pass the base URL of the server, e.g. C(https://pam.revbits.net).
            - At third index you need to place API key for auth. You can get from RevBits PAM secret manger module
        ini:
            - section: revbitspss_lookup
              key: _terms
        required: true
"""

RETURN = r"""
_list:
    description:
        - The JSON responses which you can access with defined keys.
        - If you are fetching secrets named as UUID, PASSWORD it will gives you the dict of all secrets
    type: list
    elements: dict
"""

EXAMPLES = r"""
- hosts: localhost
  vars:
      secret: >-
        {{
            lookup(
                'community.general.revbitspss',
                 ['UUIDPAM','DB_PASS','DB_USER'],
                 'https://pam.revbits.net',
                 'API_KEY_GOES_HERE'
            )
        }}

  tasks:
      - ansible.builtin.debug:
          msg: >
            UUIDPAM is {{ (secret['UUIDPAM']) }} and DB_PASS is {{ (secret['DB_PASS']) }} and DB_USER is {{ (secret['DB_USER']) }}
"""

from ansible.errors import AnsibleError, AnsibleOptionsError

sdk_is_missing = False
try:
    from pam.revbits_ansible.server import (
      SecretServer,
      SecretServerError,
    )
except ImportError:
    sdk_is_missing = True
from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase


display = Display()


class LookupModule(LookupBase):
    @staticmethod
    def Client(server_parameters):
        return SecretServer(**server_parameters)

    def run(self, terms, variables, **kwargs):
        if sdk_is_missing:
            raise AnsibleError("revbits-ansible must be installed to use this plugin")
        self.set_options(var_options=variables, direct=kwargs)
        secret_server = LookupModule.Client(
            {
                "base_url": terms[1],
                "api_key": terms[2],
            }
        )
        result = []
        for term in terms[0]:
             display.debug("revbitspss_lookup term: %s" % term)
             try:
                 display.vvv(u"Secret Server lookup of Secret with ID %s" % term)
                 result.append({term:secret_server.get_pam_secret(term)})
             except SecretServerError as error:
                 raise AnsibleError("Secret Server lookup failure: %s" % error.message)
        return result

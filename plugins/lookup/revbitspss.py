# -*- coding: utf-8 -*-
# Copyright: (c) 2021, RevBits <info@revbits.com>
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: revbitspss
author: RevBits (@RevBits) <info@revbits.com>
short_description: Get secrets from RevBits PAM server
version_added: 3.8.0
description:
    - Uses the revbits_ansible Python SDK to get Secrets from RevBits PAM
      Server using API key authentication with the REST API.
requirements:
    - revbits_ansible - U(https://pypi.org/project/revbits_ansible/)
options:
    secret_ids:
        description:
            - This will be an array of keys for secrets which you want to fetch from RevBits PAM.
        required: true
    base_url:
        description:
            - This will be the base URL of the server, for example C(https://pam.revbits.net).
        required: true
    api_key:
        description:
            - This will be the API key for authentication. You can get from RevBits PAM secret manager module.
        required: true
"""

RETURN = r"""
_list:
    description:
        - The JSON responses which you can access with defined keys.
        - If you are fetching secrets named as UUID, PASSWORD it will gives you the dict of all secrets.
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
                 secret_ids=['UUIDPAM', 'DB_PASS', ...],
                 base_url='https://pam.revbits.net',
                 api_key='API_KEY_GOES_HERE'
            )
        }}
  tasks:
      - ansible.builtin.debug:
          msg: >
            UUIDPAM is {{ (secret['UUIDPAM']) }} and DB_PASS is {{ (secret['DB_PASS']) }}
"""

from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from ansible.errors import AnsibleError, AnsibleOptionsError
from ansible.module_utils.six import raise_from

try:
    from pam.revbits_ansible.server import SecretServer, SecretServerError
except ImportError as imp_exc:
    ANOTHER_LIBRARY_IMPORT_ERROR = imp_exc
else:
    ANOTHER_LIBRARY_IMPORT_ERROR = None


display = Display()


class LookupModule(LookupBase):

    @staticmethod
    def Client(server_parameters):
        return SecretServer(**server_parameters)

    def run(self, terms, variables, **kwargs):
        if ANOTHER_LIBRARY_IMPORT_ERROR:
            raise_from(
                AnsibleError('revbits_ansible must be installed to use this plugin'),
                ANOTHER_LIBRARY_IMPORT_ERROR
            )
        self.set_options(var_options=variables, direct=kwargs)
        secret_server = LookupModule.Client(
            {
                "base_url": self.get_option('base_url'),
                "api_key": self.get_option('api_key'),
            }
        )
        result = []
        for term in self.get_option('secret_ids'):
            display.debug("revbitspss_lookup term: %s" % term)
            try:
                display.vvv(u"Secret Server lookup of Secret with ID %s" % term)
                result.append({term: secret_server.get_pam_secret(term)})
            except SecretServerError as error:
                raise AnsibleError("Secret Server lookup failure: %s" % error.message)
        return result

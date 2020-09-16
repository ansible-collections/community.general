# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
lookup: tss
author: Adam Migus (@amigus) <adam@migus.org>
short_description: Get secrets from Thycotic Secret Server
version_added: 1.0.0
description:
    - Uses the Thycotic Secret Server Python SDK to get Secrets from Secret
      Server using token authentication with I(username) and I(password) on
      the REST API at I(base_url).
requirements:
    - python-tss-sdk - https://pypi.org/project/python-tss-sdk/
options:
    _terms:
        description: The integer ID of the secret.
        required: true
        type: int
    base_url:
        description: The base URL of the server, e.g. C(https://localhost/SecretServer).
        env:
            - name: TSS_BASE_URL
        ini:
            - section: tss_lookup
              key: base_url
        required: true
    username:
        description: The username with which to request the OAuth2 Access Grant.
        env:
            - name: TSS_USERNAME
        ini:
            - section: tss_lookup
              key: username
        required: true
    password:
        description: The password associated with the supplied username.
        env:
            - name: TSS_PASSWORD
        ini:
            - section: tss_lookup
              key: password
        required: true
    api_path_uri:
        default: /api/v1
        description: The path to append to the base URL to form a valid REST
            API request.
        env:
            - name: TSS_API_PATH_URI
        required: false
    token_path_uri:
        default: /oauth2/token
        description: The path to append to the base URL to form a valid OAuth2
            Access Grant request.
        env:
            - name: TSS_TOKEN_PATH_URI
        required: false
"""

RETURN = r"""
_list:
    description:
        - The JSON responses to C(GET /secrets/{id}).
        - See U(https://updates.thycotic.net/secretserver/restapiguide/TokenAuth/#operation--secrets--id--get).
    type: list
    elements: dict
"""

EXAMPLES = r"""
- hosts: localhost
  vars:
      secret: "{{ lookup('community.general.tss', 1) }}"
  tasks:
      - ansible.builtin.debug: msg="the password is {{ (secret['items'] | items2dict(key_name='slug', value_name='itemValue'))['password'] }}"
"""

from ansible.errors import AnsibleError, AnsibleOptionsError

sdk_is_missing = False

try:
    from thycotic.secrets.server import (
        SecretServer,
        SecretServerAccessError,
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
            raise AnsibleError("python-tss-sdk must be installed to use this plugin")

        self.set_options(var_options=variables, direct=kwargs)

        secret_server = LookupModule.Client(
            {
                "base_url": self.get_option("base_url"),
                "username": self.get_option("username"),
                "password": self.get_option("password"),
                "api_path_uri": self.get_option("api_path_uri"),
                "token_path_uri": self.get_option("token_path_uri"),
            }
        )
        result = []

        for term in terms:
            display.debug("tss_lookup term: %s" % term)
            try:
                id = int(term)
                display.vvv(u"Secret Server lookup of Secret with ID %d" % id)
                result.append(secret_server.get_secret_json(id))
            except ValueError:
                raise AnsibleOptionsError("Secret ID must be an integer")
            except SecretServerError as error:
                raise AnsibleError("Secret Server lookup failure: %s" % error.message)
        return result

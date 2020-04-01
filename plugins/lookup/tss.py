# python 3 headers, required if submitting to Ansible
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
lookup: tss
author: Adam Migus (adam@migus.org)
short_description: Get secrets from Thycotic Secret Server
description:
    - Uses the Thycotic Secret Server Python SDK to get Secrets from Secret
      Server using token authentication with `username` and `password` on
      the REST API at `base_url`.
requirements:
    - python-tss-sdk - https://pypi.org/project/python-tss-sdk/
options:
    _terms:
        description: the integer ID of the secret
        required: True
        type: integer
    base_url:
        description: the base URL of the server e.g. https://localhost/SecretServer
        env:
            - name: TSS_BASE_URL
        ini:
            - section: tss_lookup
              key: base_url
        required: True
    username:
        description: the username with which to request the OAuth2 Access Grant
        env:
            - name: TSS_USERNAME
        ini:
            - section: tss_lookup
              key: username
        required: True
    password:
        description: the password associated with the supplied username
        env:
            - name: TSS_PASSWORD
        ini:
            - section: tss_lookup
              key: password
        required: True
    api_path_uri:
        default: /api/v1
        description: the path to append to the base URL to form a valid REST
            API request
        env:
            - name: TSS_API_PATH_URI
        required: False
    token_path_uri:
        default: /oauth2/token
        description: the path to append to the base URL to form a valid OAuth2
            Access Grant request
        env:
            - name: TSS_TOKEN_PATH_URI
        required: False"""

RETURN = r"""
_list:
    description:
        - The JSON responses to `GET /secrets/{id}`
        - See https://updates.thycotic.net/secretserver/restapiguide/TokenAuth/#operation--secrets--id--get>"""

EXAMPLES = r"""
- hosts: localhost
  vars:
      secret: "{{ lookup('tss', 1) }}"
  tasks:
      - debug: msg="the password is {{ (secret['items'] | items2dict(key_name='slug', value_name='itemValue'))['password'] }}"
"""

from ansible.errors import AnsibleError, AnsibleOptionsError

try:
    from thycotic.secrets.server import (
        SecretServer,
        SecretServerAccessError,
        SecretServerError,
    )
except ImportError:
    raise AnsibleError("python-tss-sdk must be installed to use this plugin")

from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase


display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        server_parameters = {
            "base_url": self.get_option("base_url"),
            "username": self.get_option("username"),
            "password": self.get_option("password"),
            "api_path_uri": self.get_option("api_path_uri"),
            "token_path_uri": self.get_option("token_path_uri"),
        }
        secret_server = SecretServer(**server_parameters)
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
        display.debug(u"tss_lookup result: %s" % result)
        return result

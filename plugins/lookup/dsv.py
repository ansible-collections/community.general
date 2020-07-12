from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
lookup: dsv
author: Adam Migus (adam@migus.org)
short_description: Get secrets from Thycotic DevOps Secrets Vault
description:
    - Uses the Thycotic DevOps Secrets Vault Python SDK to get Secrets from a
       DSV `tenant` using a `client_id` and `client_secret`.
requirements:
    - python-dsv-sdk - https://pypi.org/project/python-dsv-sdk/
options:
    _terms:
        description: The path to the secret, e.g. C(/staging/servers/web1).
        required: True
    tenant:
        description: The first format parameter in the default I(url_template).
        env:
            - name: DSV_TENANT
        ini:
            - section: dsv_lookup
              key: tenant
        required: True
    tld:
        default: com
        description: The top-level domain of the tenant; the second format
            parameter in the default I(url_template).
        env:
            - name: DSV_TLD
        ini:
            - section: dsv_lookup
              key: tld
        required: False
    client_id:
        description: The client_id with which to request the Access Grant.
        env:
            - name: DSV_CLIENT_ID
        ini:
            - section: dsv_lookup
              key: client_id
        required: True
    client_secret:
        description: The client secret associated with the specific I(client_id).
        env:
            - name: DSV_CLIENT_SECRET
        ini:
            - section: dsv_lookup
              key: client_secret
        required: True
    url_template:
        default: https://{}.secretsvaultcloud.{}/v1
        description: The path to prepend to the base URL to form a valid REST
            API request.
        env:
            - name: DSV_URL_TEMPLATE
        ini:
            - section: dsv_lookup
              key: url_template
        required: False
"""

RETURN = r"""
_list:
    description:
        - One or more JSON responses to C(GET /secrets/{path}).
        - See U(https://dsv.thycotic.com/api/index.html#operation/getSecret).
"""

EXAMPLES = r"""
- hosts: localhost
  vars:
      secret: "{{ lookup('community.general.dsv', '/test/secret') }}"
  tasks:
      - debug:
          msg: 'the password is {{ secret["data"]["password"] }}'
"""

from ansible.errors import AnsibleError, AnsibleOptionsError

sdk_is_missing = False

try:
    from thycotic.secrets.vault import (
        SecretsVault,
        SecretsVaultError,
    )
except ImportError:
    sdk_is_missing = True

from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase


display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        if sdk_is_missing:
            raise AnsibleError("python-dsv-sdk must be installed to use this plugin")

        self.set_options(var_options=variables, direct=kwargs)

        vault_parameters = {
            "tenant": self.get_option("tenant"),
            "client_id": self.get_option("client_id"),
            "client_secret": self.get_option("client_secret"),
            "url_template": self.get_option("url_template"),
        }
        vault = SecretsVault(**vault_parameters)
        result = []

        for term in terms:
            display.debug("dsv_lookup term: %s" % term)
            try:
                path = term.lstrip("[/:]")

                if path == "":
                    raise AnsibleOptionsError("Invalid secret path: %s" % term)

                display.vvv(u"DevOps Secrets Vault GET /secrets/%s" % path)
                result.append(vault.get_secret_json(path))
            except SecretsVaultError as error:
                raise AnsibleError(
                    "DevOps Secrets Vault lookup failure: %s" % error.message
                )
        return result

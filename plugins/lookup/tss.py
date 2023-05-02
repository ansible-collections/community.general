# -*- coding: utf-8 -*-
# Copyright (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: tss
author: Adam Migus (@amigus) <adam@migus.org>
short_description: Get secrets from Thycotic Secret Server
version_added: 1.0.0
description:
    - Uses the Thycotic Secret Server Python SDK to get Secrets from Secret
      Server using token authentication with I(username) and I(password) on
      the REST API at I(base_url).
    - When using self-signed certificates the environment variable
      C(REQUESTS_CA_BUNDLE) can be set to a file containing the trusted certificates
      (in C(.pem) format).
    - For example, C(export REQUESTS_CA_BUNDLE='/etc/ssl/certs/ca-bundle.trust.crt').
requirements:
    - python-tss-sdk - https://pypi.org/project/python-tss-sdk/
options:
    _terms:
        description: The integer ID of the secret.
        required: true
        type: int
    fetch_attachments:
        description:
            - Boolean flag which indicates whether attached files will get downloaded or not.
            - The download will only happen if I(file_download_path) has been provided.
        required: false
        type: bool
        version_added: 7.0.0
    file_download_path:
        description: Indicate the file attachment download location.
        required: false
        type: path
        version_added: 7.0.0
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
    password:
        description:
            - The password associated with the supplied username.
            - Required when I(token) is not provided.
        env:
            - name: TSS_PASSWORD
        ini:
            - section: tss_lookup
              key: password
    domain:
        default: ""
        description:
          - The domain with which to request the OAuth2 Access Grant.
          - Optional when I(token) is not provided.
          - Requires C(python-tss-sdk) version 1.0.0 or greater.
        env:
            - name: TSS_DOMAIN
        ini:
            - section: tss_lookup
              key: domain
        required: false
        version_added: 3.6.0
    token:
        description:
          - Existing token for Thycotic authorizer.
          - If provided, I(username) and I(password) are not needed.
          - Requires C(python-tss-sdk) version 1.0.0 or greater.
        env:
            - name: TSS_TOKEN
        ini:
            - section: tss_lookup
              key: token
        version_added: 3.7.0
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
      secret: >-
        {{
            lookup(
                'community.general.tss',
                102,
                base_url='https://secretserver.domain.com/SecretServer/',
                username='user.name',
                password='password'
            )
        }}
  tasks:
      - ansible.builtin.debug:
          msg: >
            the password is {{
              (secret['items']
                | items2dict(key_name='slug',
                             value_name='itemValue'))['password']
            }}

- hosts: localhost
  vars:
      secret: >-
        {{
            lookup(
                'community.general.tss',
                102,
                base_url='https://secretserver.domain.com/SecretServer/',
                username='user.name',
                password='password',
                domain='domain'
            )
        }}
  tasks:
      - ansible.builtin.debug:
          msg: >
            the password is {{
              (secret['items']
                | items2dict(key_name='slug',
                             value_name='itemValue'))['password']
            }}

- hosts: localhost
  vars:
      secret_password: >-
        {{
            ((lookup(
                'community.general.tss',
                102,
                base_url='https://secretserver.domain.com/SecretServer/',
                token='thycotic_access_token',
            )  | from_json).get('items') | items2dict(key_name='slug', value_name='itemValue'))['password']
        }}
  tasks:
      - ansible.builtin.debug:
          msg: the password is {{ secret_password }}

# Private key stores into certificate file which is attached with secret.
# If fetch_attachments=True then private key file will be download on specified path
# And file content will display in debug message.
- hosts: localhost
  vars:
      secret: >-
        {{
            lookup(
                'community.general.tss',
                102,
                fetch_attachments=True,
                file_download_path='/home/certs',
                base_url='https://secretserver.domain.com/SecretServer/',
                token='thycotic_access_token'
            )
        }}
  tasks:
    - ansible.builtin.debug:
        msg: >
          the private key is {{
            (secret['items']
              | items2dict(key_name='slug',
                           value_name='itemValue'))['private-key']
          }}
"""

import abc
import os
from ansible.errors import AnsibleError, AnsibleOptionsError
from ansible.module_utils import six
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

try:
    from thycotic.secrets.server import SecretServer, SecretServerError

    HAS_TSS_SDK = True
except ImportError:
    try:
        from delinea.secrets.server import SecretServer, SecretServerError

        HAS_TSS_SDK = True
    except ImportError:
        SecretServer = None
        SecretServerError = None
        HAS_TSS_SDK = False

try:
    from thycotic.secrets.server import PasswordGrantAuthorizer, DomainPasswordGrantAuthorizer, AccessTokenAuthorizer

    HAS_TSS_AUTHORIZER = True
except ImportError:
    try:
        from delinea.secrets.server import PasswordGrantAuthorizer, DomainPasswordGrantAuthorizer, AccessTokenAuthorizer

        HAS_TSS_AUTHORIZER = True
    except ImportError:
        PasswordGrantAuthorizer = None
        DomainPasswordGrantAuthorizer = None
        AccessTokenAuthorizer = None
        HAS_TSS_AUTHORIZER = False


display = Display()


@six.add_metaclass(abc.ABCMeta)
class TSSClient(object):
    def __init__(self):
        self._client = None

    @staticmethod
    def from_params(**server_parameters):
        if HAS_TSS_AUTHORIZER:
            return TSSClientV1(**server_parameters)
        else:
            return TSSClientV0(**server_parameters)

    def get_secret(self, term, fetch_file_attachments, file_download_path):
        display.debug("tss_lookup term: %s" % term)
        secret_id = self._term_to_secret_id(term)
        display.vvv(u"Secret Server lookup of Secret with ID %d" % secret_id)

        if fetch_file_attachments:
            obj = self._client.get_secret(secret_id, fetch_file_attachments)
            for i in obj['items']:
                if file_download_path and os.path.isdir(file_download_path):
                    if i['isFile']:
                        try:
                            with open(os.path.join(file_download_path, str(obj['id']) + "_" + i['slug']), "w") as f:
                                f.write(i['itemValue'].text)
                            i['itemValue'] = "*** Not Valid For Display ***"
                        except ValueError:
                            raise AnsibleOptionsError("Failed to download {0}".format(str(i['slug'])))
                else:
                    raise AnsibleOptionsError("File download path does not exist")
            return obj
        else:
            return self._client.get_secret_json(secret_id)

    @staticmethod
    def _term_to_secret_id(term):
        try:
            return int(term)
        except ValueError:
            raise AnsibleOptionsError("Secret ID must be an integer")


class TSSClientV0(TSSClient):
    def __init__(self, **server_parameters):
        super(TSSClientV0, self).__init__()

        if server_parameters.get("domain"):
            raise AnsibleError("The 'domain' option requires 'python-tss-sdk' version 1.0.0 or greater")

        self._client = SecretServer(
            server_parameters["base_url"],
            server_parameters["username"],
            server_parameters["password"],
            server_parameters["api_path_uri"],
            server_parameters["token_path_uri"],
        )


class TSSClientV1(TSSClient):
    def __init__(self, **server_parameters):
        super(TSSClientV1, self).__init__()

        authorizer = self._get_authorizer(**server_parameters)
        self._client = SecretServer(
            server_parameters["base_url"], authorizer, server_parameters["api_path_uri"]
        )

    @staticmethod
    def _get_authorizer(**server_parameters):
        if server_parameters.get("token"):
            return AccessTokenAuthorizer(
                server_parameters["token"],
            )

        if server_parameters.get("domain"):
            return DomainPasswordGrantAuthorizer(
                server_parameters["base_url"],
                server_parameters["username"],
                server_parameters["domain"],
                server_parameters["password"],
                server_parameters["token_path_uri"],
            )

        return PasswordGrantAuthorizer(
            server_parameters["base_url"],
            server_parameters["username"],
            server_parameters["password"],
            server_parameters["token_path_uri"],
        )


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        if not HAS_TSS_SDK:
            raise AnsibleError("python-tss-sdk must be installed to use this plugin")

        self.set_options(var_options=variables, direct=kwargs)

        tss = TSSClient.from_params(
            base_url=self.get_option("base_url"),
            username=self.get_option("username"),
            password=self.get_option("password"),
            domain=self.get_option("domain"),
            token=self.get_option("token"),
            api_path_uri=self.get_option("api_path_uri"),
            token_path_uri=self.get_option("token_path_uri"),
        )

        try:
            return [tss.get_secret(term, self.get_option("fetch_attachments"), self.get_option("file_download_path")) for term in terms]
        except SecretServerError as error:
            raise AnsibleError("Secret Server lookup failure: %s" % error.message)

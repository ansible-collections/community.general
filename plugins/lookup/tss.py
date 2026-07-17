# Copyright (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: tss
author: Adam Migus (@amigus) <adam@migus.org>
short_description: Get secrets from Delinea Secret Server
version_added: 1.0.0
description:
  - Uses the Thycotic Secret Server Python SDK to get Secrets from Secret Server using token authentication with O(username)
    and O(password) on the REST API at O(base_url).
  - When using self-signed certificates the environment variable E(REQUESTS_CA_BUNDLE) can be set to a file containing the
    trusted certificates (in C(.pem) format).
  - For example, C(export REQUESTS_CA_BUNDLE='/etc/ssl/certs/ca-bundle.trust.crt').
requirements:
  - python-tss-sdk - https://pypi.org/project/python-tss-sdk/
options:
  _terms:
    description: The integer ID of the secret.
    required: true
    type: list
    elements: int
  secret_path:
    description: Indicate a full path of secret including folder and secret name when the secret ID is set to 0.
    required: false
    type: str
    version_added: 7.2.0
  fetch_secret_ids_from_folder:
    description:
      - Boolean flag which indicates whether secret IDs are in a folder is fetched by folder ID or not.
      - V(true) then the terms are considered as a folder IDs. Otherwise (default), they are considered as secret IDs.
    required: false
    type: bool
    version_added: 7.1.0
  fetch_attachments:
    description:
      - Boolean flag which indicates whether attached files are downloaded or not.
      - The download only happens if O(file_download_path) has been provided.
    required: false
    type: bool
    version_added: 7.0.0
  file_download_path:
    description: Indicate the file attachment download location.
    required: false
    type: path
    version_added: 7.0.0
  base_url:
    description: The base URL of the server, for example V(https://localhost/SecretServer).
    type: string
    env:
      - name: TSS_BASE_URL
    ini:
      - section: tss_lookup
        key: base_url
    required: true
  username:
    description: The username with which to request the OAuth2 Access Grant.
    type: string
    env:
      - name: TSS_USERNAME
    ini:
      - section: tss_lookup
        key: username
  password:
    description:
      - The password associated with the supplied username.
      - Required when O(token) is not provided.
    type: string
    env:
      - name: TSS_PASSWORD
    ini:
      - section: tss_lookup
        key: password
  domain:
    default: ""
    description:
      - The domain with which to request the OAuth2 Access Grant.
      - Optional when O(token) is not provided.
      - Requires C(python-tss-sdk) version 1.0.0 or greater.
    type: string
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
      - If provided, O(username) and O(password) are not needed.
      - Requires C(python-tss-sdk) version 1.0.0 or greater.
    type: string
    env:
      - name: TSS_TOKEN
    ini:
      - section: tss_lookup
        key: token
    version_added: 3.7.0
  api_path_uri:
    default: /api/v1
    description: The path to append to the base URL to form a valid REST API request.
    type: string
    env:
      - name: TSS_API_PATH_URI
    required: false
  token_path_uri:
    default: /oauth2/token
    description:
      - The path to append to the base URL to form a valid OAuth2 Access Grant request.
      - Used when O(token_path_source=token_path_uri) (the default). To let C(python-tss-sdk) auto-detect the token endpoint
        instead (for example for Delinea Platform authentication), set O(token_path_source=auto).
    type: string
    env:
      - name: TSS_TOKEN_PATH_URI
    ini:
      - section: tss_lookup
        key: token_path_uri
        version_added: 13.2.0
    required: false
  token_path_source:
    description:
      - How to determine the OAuth2 token endpoint path.
      - V(token_path_uri) uses the O(token_path_uri) option as given.
      - V(auto) ignores O(token_path_uri) and lets C(python-tss-sdk) auto-detect the token endpoint from O(base_url), selecting
        the correct path for Secret Server or the Delinea Platform.
    type: string
    choices:
      - token_path_uri
      - auto
    default: token_path_uri
    env:
      - name: TSS_TOKEN_PATH_SOURCE
    ini:
      - section: tss_lookup
        key: token_path_source
    required: false
    version_added: 13.2.0
"""

RETURN = r"""
_list:
  description:
    - The JSON responses to C(GET /secrets/{id}) and C(GET /secrets/{path}).
    - See U(https://updates.thycotic.net/secretserver/restapiguide/TokenAuth/#operation--secrets--id--get).
  type: list
  elements: dict
"""

EXAMPLES = r"""
# Using Secret Server Authentication
- name: Lookup secret using Secret Server user credentials
  hosts: localhost
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

- name: Lookup secret with domain user
  hosts: localhost
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

- name: Lookup secret using Secret Server token
  hosts: localhost
  vars:
    secret_password: >-
      {{
        ((lookup(
          'community.general.tss',
          102,
          base_url='https://secretserver.domain.com/SecretServer/',
          token='thycotic_access_token',
        ) | from_json).get('items') | items2dict(key_name='slug', value_name='itemValue'))['password']
      }}
  tasks:
    - ansible.builtin.debug:
        msg: the password is {{ secret_password }}

# Private key stores into certificate file which is attached with secret.
# If fetch_attachments=True then private key file will be download on specified path
# and file content will display in debug message.
- name: Lookup secret and fetch attachments using Secret Server token
  hosts: localhost
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

# If fetch_secret_ids_from_folder=true then secret IDs are in a folder is fetched based on folder ID
- name: Lookup secret IDs by folder ID using Secret Server token
  hosts: localhost
  vars:
    secret: >-
      {{
        lookup(
          'community.general.tss',
          102,
          fetch_secret_ids_from_folder=true,
          base_url='https://secretserver.domain.com/SecretServer/',
          token='thycotic_access_token'
        )
      }}
  tasks:
    - ansible.builtin.debug:
        msg: >
          the secret id's are {{
              secret
          }}

# If secret ID is 0 and secret_path has value then secret is fetched by secret path
- name: Lookup secret by secret path using Secret Server user credentials
  hosts: localhost
  vars:
    secret: >-
      {{
        lookup(
          'community.general.tss',
          0,
          secret_path='\folderName\secretName'
          base_url='https://secretserver.domain.com/SecretServer/',
          username='user.name',
          password='password'
        )
      }}
  tasks:
    - ansible.builtin.debug:
        msg: >-
          the password is {{
            (secret['items']
              | items2dict(key_name='slug',
                           value_name='itemValue'))['password']
          }}

# Using Platform Authentication
- name: Lookup secret using Platform service user credentials
  hosts: localhost
  vars:
    secret: >-
      {{
        lookup(
          'community.general.tss',
          102,
          base_url='https://platform.delinea.app/',
          username='platform_service_username',
          password='platform_service_user_password',
          token_path_source='auto'
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

- name: Lookup secret using platform token
  hosts: localhost
  vars:
    secret_password: >-
      {{
        ((lookup(
          'community.general.tss',
          102,
          base_url='https://platform.delinea.app/',
          token='delinea_platform_access_token',
        ) | from_json).get('items') | items2dict(key_name='slug', value_name='itemValue'))['password']
      }}
  tasks:
    - ansible.builtin.debug:
        msg: the password is {{ secret_password }}
"""

import abc
import os
import typing as t

from ansible.errors import AnsibleError, AnsibleOptionsError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

from ansible_collections.community.general.plugins.plugin_utils._lookup import check_for_wrong_terms

try:
    from delinea.secrets.server import (
        AccessTokenAuthorizer,
        DomainPasswordGrantAuthorizer,
        PasswordGrantAuthorizer,
        SecretServer,
        SecretServerError,
    )

    HAS_TSS_SDK = True
    HAS_DELINEA_SS_SDK = True
    HAS_TSS_AUTHORIZER = True
except ImportError:
    try:
        from thycotic.secrets.server import (
            AccessTokenAuthorizer,
            DomainPasswordGrantAuthorizer,
            PasswordGrantAuthorizer,
            SecretServer,
            SecretServerError,
        )

        HAS_TSS_SDK = True
        HAS_DELINEA_SS_SDK = False
        HAS_TSS_AUTHORIZER = True
    except ImportError:
        SecretServer = None
        SecretServerError = None
        HAS_TSS_SDK = False
        HAS_DELINEA_SS_SDK = False
        PasswordGrantAuthorizer = None
        DomainPasswordGrantAuthorizer = None
        AccessTokenAuthorizer = None
        HAS_TSS_AUTHORIZER = False


# SecretServerClientError (4xx) is exported by newer python-tss-sdk builds. When
# present it lets us distinguish auth/permission failures from 5xx service errors
# so a stale cached client can be invalidated and the lookup retried once. On
# older SDKs the import is absent and the retry is simply skipped.
try:
    from delinea.secrets.server import SecretServerClientError

    HAS_SS_CLIENT_ERROR = True
except ImportError:
    try:
        from thycotic.secrets.server import SecretServerClientError

        HAS_SS_CLIENT_ERROR = True
    except ImportError:
        SecretServerClientError = None
        HAS_SS_CLIENT_ERROR = False


if t.TYPE_CHECKING:
    CacheKey = tuple[str | None, str | None, str | None, str | None, str | None]


display = Display()


class TSSClient(metaclass=abc.ABCMeta):  # noqa: B024
    def __init__(self):
        self._client = None

    @staticmethod
    def from_params(**server_parameters):
        if HAS_TSS_AUTHORIZER:
            return TSSClientV1(**server_parameters)
        else:
            return TSSClientV0(**server_parameters)

    def get_secret(self, term, secret_path, fetch_file_attachments, file_download_path):
        display.debug(f"tss_lookup term: {term}")
        secret_id = self._term_to_secret_id(term)
        if secret_id == 0 and secret_path:
            fetch_secret_by_path = True
            display.vvv(f"Secret Server lookup of Secret with path {secret_path}")
        else:
            fetch_secret_by_path = False
            display.vvv(f"Secret Server lookup of Secret with ID {secret_id}")

        if fetch_file_attachments:
            if fetch_secret_by_path:
                obj = self._client.get_secret_by_path(secret_path, fetch_file_attachments)
            else:
                obj = self._client.get_secret(secret_id, fetch_file_attachments)
            for i in obj["items"]:
                if file_download_path and os.path.isdir(file_download_path):
                    if i["isFile"]:
                        try:
                            file_content = i["itemValue"].content
                            with open(os.path.join(file_download_path, f"{obj['id']}_{i['slug']}"), "wb") as f:
                                f.write(file_content)
                        except ValueError as e:
                            raise AnsibleOptionsError(f"Failed to download {i['slug']}") from e
                        except AttributeError:
                            display.warning(f"Could not read file content for {i['slug']}")
                        finally:
                            i["itemValue"] = "*** Not Valid For Display ***"
                else:
                    raise AnsibleOptionsError("File download path does not exist")
            return obj
        else:
            if fetch_secret_by_path:
                return self._client.get_secret_by_path(secret_path, False)
            else:
                return self._client.get_secret_json(secret_id)

    def get_secret_ids_by_folderid(self, term):
        display.debug(f"tss_lookup term: {term}")
        folder_id = self._term_to_folder_id(term)
        display.vvv(f"Secret Server lookup of Secret id's with Folder ID {folder_id}")

        return self._client.get_secret_ids_by_folderid(folder_id)

    @staticmethod
    def _term_to_secret_id(term):
        try:
            return int(term)
        except ValueError as e:
            raise AnsibleOptionsError("Secret ID must be an integer") from e

    @staticmethod
    def _term_to_folder_id(term):
        try:
            return int(term)
        except ValueError as e:
            raise AnsibleOptionsError("Folder ID must be an integer") from e


class TSSClientV0(TSSClient):
    def __init__(self, **server_parameters):
        super().__init__()

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
        super().__init__()

        authorizer = self._get_authorizer(**server_parameters)
        self._client = SecretServer(server_parameters["base_url"], authorizer, server_parameters["api_path_uri"])

    @staticmethod
    def _get_authorizer(**server_parameters):
        if server_parameters.get("token"):
            return AccessTokenAuthorizer(server_parameters["token"], server_parameters["base_url"])

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


# Module-scope cache of TSSClient instances, keyed on credential identity. Each
# TSSClient holds an authorizer whose internal token cache is only useful if the
# client is reused; without this, every lookup() call mints a fresh OAuth2 token
# grant, which can overload the token endpoint on lookup-heavy playbooks.
_client_cache: dict[CacheKey, TSSClient] = {}


def _credential_key(server_parameters: dict[str, str | None]) -> CacheKey | None:
    # Token-based auth makes no token-endpoint call, so caching adds nothing.
    if server_parameters.get("token"):
        return None
    # password is intentionally excluded from the key: the cached client holds
    # the password on its authorizer, so a second lookup with the same username
    # but a different password would not be "fixed" by keying separately - it
    # would just split the cache while the first authorizer's password is what
    # actually gets used.
    return (
        server_parameters.get("base_url"),
        server_parameters.get("username"),
        server_parameters.get("domain"),
        server_parameters.get("api_path_uri"),
        server_parameters.get("token_path_uri"),
    )


def _get_or_build_client(server_parameters: dict[str, str | None]) -> TSSClient:
    key = _credential_key(server_parameters)
    if key is None:
        return TSSClient.from_params(**server_parameters)
    # On a cache miss, build the client (from_params makes the token-endpoint
    # network call) and setdefault to insert it. setdefault resolves the case
    # where two builds for the same key happen concurrently: the first insert
    # wins and the later client is discarded.
    tss = _client_cache.get(key)
    if tss is not None:
        return tss
    new_tss = TSSClient.from_params(**server_parameters)
    return _client_cache.setdefault(key, new_tss)


def _drop_cached_client(server_parameters: dict[str, str | None]) -> None:
    key = _credential_key(server_parameters)
    if key is None:
        return
    _client_cache.pop(key, None)


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        if not HAS_TSS_SDK:
            raise AnsibleError("python-tss-sdk must be installed to use this plugin")

        self.set_options(var_options=variables, direct=kwargs)
        check_for_wrong_terms(self, direct=kwargs)

        # token_path_source selects how the OAuth2 token endpoint is resolved:
        # "auto" passes an empty path so python-tss-sdk auto-detects the endpoint
        # from base_url; the default uses token_path_uri as given.
        token_path_uri = self.get_option("token_path_uri")
        if self.get_option("token_path_source") == "auto":
            token_path_uri = ""

        params = {
            "base_url": self.get_option("base_url"),
            "username": self.get_option("username"),
            "password": self.get_option("password"),
            "domain": self.get_option("domain"),
            "token": self.get_option("token"),
            "api_path_uri": self.get_option("api_path_uri"),
            "token_path_uri": token_path_uri,
        }

        try:
            return self._lookup(terms, _get_or_build_client(params))
        except SecretServerError as error:
            # A 4xx is often a stale cached token: drop the cached client so the
            # rebuild mints a fresh grant, then retry once. 5xx and anything else
            # propagate unchanged. The retry re-runs the lookup for all terms,
            # not just the one that raised; reads are idempotent so that is safe,
            # though it can produce duplicate reads in the Secret Server audit log.
            if HAS_SS_CLIENT_ERROR and isinstance(error, SecretServerClientError):
                _drop_cached_client(params)
                try:
                    return self._lookup(terms, _get_or_build_client(params))
                except SecretServerError as retry_error:
                    raise AnsibleError(f"Secret Server lookup failure: {retry_error.message}") from retry_error
            raise AnsibleError(f"Secret Server lookup failure: {error.message}") from error

    def _lookup(self, terms, tss):
        if self.get_option("fetch_secret_ids_from_folder"):
            if HAS_DELINEA_SS_SDK:
                return [tss.get_secret_ids_by_folderid(term) for term in terms]
            raise AnsibleError("latest python-tss-sdk must be installed to use this plugin")
        return [
            tss.get_secret(
                term,
                self.get_option("secret_path"),
                self.get_option("fetch_attachments"),
                self.get_option("file_download_path"),
            )
            for term in terms
        ]

# (c) 2015, Jonathan Davila <jonathan(at)davila.io>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  lookup: hashi_vault
  author: Jonathan Davila <jdavila(at)ansible.com>
  short_description: retrieve secrets from HashiCorp's Vault
  requirements:
    - hvac (python library)
  description:
    - retrieve secrets from HashiCorp's Vault
  notes:
    - Due to a current limitation in the HVAC library there won't necessarily be an error if a bad endpoint is specified.
    - As of Ansible 2.10, only the latest secret is returned when specifying a KV v2 path.
  options:
    secret:
      description: Vault path to the secret being requested in the format C(path[:field]).
      required: True
    token:
      description: Vault token.
      env:
        - name: VAULT_TOKEN
    url:
      description: URL to the Vault service.
      env:
        - name: VAULT_ADDR
      default: 'http://127.0.0.1:8200'
    username:
      description: Authentication user name.
    password:
      description: Authentication password.
    role_id:
      description: Role ID to be used for Vault authentication.
      env:
        - name: VAULT_ROLE_ID
    secret_id:
      description: Secret ID to be used for Vault AppRole authentication.
      env:
        - name: VAULT_SECRET_ID
    auth_method:
      description:
      - Authentication method to be used.
      - C(userpass) is added in version 2.8.
      env:
        - name: VAULT_AUTH_METHOD
      choices:
        - userpass
        - ldap
        - approle
        - jwt
    mount_point:
      description: Vault mount point, only required if you have a custom mount point. Does not apply to token authentication.
      default: auth_method
    jwt:
      description: The JSON Web Token (JWT) to use for authentication to Vault.
      env:
        - name: VAULT_JWT
    ca_cert:
      description: Path to certificate to use for authentication.
      aliases: [ cacert ]
    validate_certs:
      description:
        - If set to C(no), the TLS certificate of the Vault service will not be validated.
        - Use extreme caution when disabling certificate validation. This should not be used in production.
      type: boolean
      default: True
    namespace:
      description:
        - Vault namespace where secrets reside. This option requires HVAC 0.7.0+ and Vault 0.11+.
        - Optionally, this may be achieved by prefixing the authentication mount point and/or secret path with the namespace (e.g C(mynamespace/secret/mysecret)).
'''

EXAMPLES = """
- debug:
    msg: "{{ lookup('hashi_vault', 'secret=secret/hello:value token=c975b780-d1be-8016-866b-01d0f9b688a5 url=http://myvault:8200')}}"

- name: Return all secrets from a path
  debug:
    msg: "{{ lookup('hashi_vault', 'secret=secret/hello token=c975b780-d1be-8016-866b-01d0f9b688a5 url=http://myvault:8200')}}"

- name: Vault that requires authentication via LDAP
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hello:value auth_method=ldap mount_point=ldap username=myuser password=mypas url=http://myvault:8200')}}"

- name: Vault that requires authentication via username and password
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hello:value auth_method=userpass username=myuser password=mypas url=http://myvault:8200')}}"

- name: Connect to Vault using TLS
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hola:value token=c975b780-d1be-8016-866b-01d0f9b688a5 url=https://myvault:8200 validate_certs=False')}}"

- name: using certificate auth
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hi:value token=xxxx-xxx-xxx url=https://myvault:8200 validate_certs=True cacert=/cacert/path/ca.pem')}}"

- name: Authenticate with a Vault app role
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hello:value auth_method=approle role_id=myroleid secret_id=mysecretid url=http://myvault:8200')}}"

- name: Authenticate with a JWT
  debug:
      msg: "{{ lookup('hashi_vault', 'secret=secret/hello:value auth_method=jwt role_id=myroleid jwt=myjwt url=https://myvault:8200')}}"

- name: Return all secrets from a path in a namespace
  debug:
    msg: "{{ lookup('hashi_vault', 'secret=secret/hello token=c975b780-d1be-8016-866b-01d0f9b688a5 url=http://myvault:8200 namespace=teama/admins')}}"

# When using KV v2 the PATH should include "data" between the secret engine mount and path (e.g. "secret/data/:path")
# see: https://www.vaultproject.io/api/secret/kv/kv-v2.html#read-secret-version
- name: Return latest KV v2 secret from path
  debug:
    msg: "{{ lookup('hashi_vault', 'secret=secret/data/hello token=my_vault_token url=http://myvault_url:8200') }}"


"""

RETURN = """
_raw:
  description:
    - secrets(s) requested
"""

import os

from ansible.errors import AnsibleError
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.lookup import LookupBase

HAS_HVAC = False
try:
    import hvac
    HAS_HVAC = True
except ImportError:
    HAS_HVAC = False


ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']


class HashiVault:
    def __init__(self, **kwargs):

        self.url = kwargs.get('url', ANSIBLE_HASHI_VAULT_ADDR)
        self.namespace = kwargs.get('namespace', None)
        self.avail_auth_method = ['approle', 'userpass', 'ldap', 'jwt']

        # split secret arg, which has format 'secret/hello:value' into secret='secret/hello' and secret_field='value'
        s = kwargs.get('secret')
        if s is None:
            raise AnsibleError("No secret specified for hashi_vault lookup")

        s_f = s.rsplit(':', 1)
        self.secret = s_f[0]
        if len(s_f) >= 2:
            self.secret_field = s_f[1]
        else:
            self.secret_field = ''

        self.verify = self.boolean_or_cacert(kwargs.get('validate_certs', True), kwargs.get('cacert', ''))

        # If a particular backend is asked for (and its method exists) we call it, otherwise drop through to using
        # token auth. This means if a particular auth backend is requested and a token is also given, then we
        # ignore the token and attempt authentication against the specified backend.
        #
        # to enable a new auth backend, simply add a new 'def auth_<type>' method below.
        #
        self.auth_method = kwargs.get('auth_method', os.environ.get('VAULT_AUTH_METHOD'))
        self.verify = self.boolean_or_cacert(kwargs.get('validate_certs', True), kwargs.get('cacert', ''))
        if self.auth_method and self.auth_method != 'token':
            try:
                if self.namespace is not None:
                    self.client = hvac.Client(url=self.url, verify=self.verify, namespace=self.namespace)
                else:
                    self.client = hvac.Client(url=self.url, verify=self.verify)
                # prefixing with auth_ to limit which methods can be accessed
                getattr(self, 'auth_' + self.auth_method)(**kwargs)
            except AttributeError:
                raise AnsibleError("Authentication method '%s' not supported."
                                   " Available options are %r" % (self.auth_method, self.avail_auth_method))
        else:
            self.token = kwargs.get('token', os.environ.get('VAULT_TOKEN', None))
            if self.token is None and os.environ.get('HOME'):
                token_filename = os.path.join(
                    os.environ.get('HOME'),
                    '.vault-token'
                )
                if os.path.exists(token_filename):
                    with open(token_filename) as token_file:
                        self.token = token_file.read().strip()

            if self.token is None:
                raise AnsibleError("No Vault Token specified")

            if self.namespace is not None:
                self.client = hvac.Client(url=self.url, token=self.token, verify=self.verify, namespace=self.namespace)
            else:
                self.client = hvac.Client(url=self.url, token=self.token, verify=self.verify)

        if not self.client.is_authenticated():
            raise AnsibleError("Invalid Hashicorp Vault Token Specified for hashi_vault lookup")

    def get(self):
        data = self.client.read(self.secret)

        # Check response for KV v2 fields and flatten nested secret data.
        #
        # https://vaultproject.io/api/secret/kv/kv-v2.html#sample-response-1
        try:
            # sentinel field checks
            check_dd = data['data']['data']
            check_md = data['data']['metadata']
            # unwrap nested data
            data = data['data']
        except KeyError:
            pass

        if data is None:
            raise AnsibleError("The secret %s doesn't seem to exist for hashi_vault lookup" % self.secret)

        if self.secret_field == '':
            return data['data']

        if self.secret_field not in data['data']:
            raise AnsibleError("The secret %s does not contain the field '%s'. for hashi_vault lookup" % (self.secret, self.secret_field))

        return data['data'][self.secret_field]

    def check_params(self, **kwargs):
        username = kwargs.get('username')
        if username is None:
            raise AnsibleError("Authentication method %s requires a username" % self.auth_method)

        password = kwargs.get('password')
        if password is None:
            raise AnsibleError("Authentication method %s requires a password" % self.auth_method)

        mount_point = kwargs.get('mount_point')

        return username, password, mount_point

    def auth_userpass(self, **kwargs):
        username, password, mount_point = self.check_params(**kwargs)
        if mount_point is None:
            mount_point = 'userpass'

        self.client.auth_userpass(username, password, mount_point=mount_point)

    def auth_ldap(self, **kwargs):
        username, password, mount_point = self.check_params(**kwargs)
        if mount_point is None:
            mount_point = 'ldap'

        self.client.auth.ldap.login(username, password, mount_point=mount_point)

    def auth_jwt(self, **kwargs):
        role_id = kwargs.get('role_id', os.environ.get('VAULT_ROLE_ID', None))
        if role_id is None:
            raise AnsibleError("Authentication method jwt requires a role_id")

        jwt = kwargs.get('jwt', os.environ.get('VAULT_JWT', None))
        if jwt is None:
            raise AnsibleError("Authentication method jwt requires parameter jwt to be set")

        mount_point = kwargs.get('mount_point')
        if mount_point is None:
            mount_point = 'jwt'

        # The GCP (and Azure, Kubernetes) auth methods just implement JWT
        self.client.auth.gcp.login(role=role_id, jwt=jwt, mount_point=mount_point)

    def boolean_or_cacert(self, validate_certs, cacert):
        validate_certs = boolean(validate_certs, strict=False)
        '''' return a bool or cacert '''
        if validate_certs is True:
            if cacert != '':
                return cacert
            else:
                return True
        else:
            return False

    def auth_approle(self, **kwargs):
        role_id = kwargs.get('role_id', os.environ.get('VAULT_ROLE_ID', None))
        if role_id is None:
            raise AnsibleError("Authentication method app role requires a role_id")

        secret_id = kwargs.get('secret_id', os.environ.get('VAULT_SECRET_ID', None))
        if secret_id is None:
            raise AnsibleError("Authentication method app role requires a secret_id")

        self.client.auth_approle(role_id, secret_id)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if not HAS_HVAC:
            raise AnsibleError("Please pip install hvac to use the hashi_vault lookup module.")

        vault_args = terms[0].split()
        vault_dict = {}
        ret = []

        for param in vault_args:
            try:
                key, value = param.split('=')
            except ValueError:
                raise AnsibleError("hashi_vault lookup plugin needs key=value pairs, but received %s" % terms)
            vault_dict[key] = value

        if 'ca_cert' in vault_dict.keys():
            vault_dict['cacert'] = vault_dict['ca_cert']
            vault_dict.pop('ca_cert', None)

        vault_conn = HashiVault(**vault_dict)

        for term in terms:
            key = term.split()[0]
            value = vault_conn.get()
            ret.append(value)

        return ret

# -*- coding: utf-8 -*-
#
# (c) 2020, SCC France, Eric Belhomme <ebelhomme@fr.scc.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
    author:
    - Eric Belhomme (@eric-belhomme) <ebelhomme@fr.scc.com>
    version_added: '0.2.0'
    lookup: etcd3
    short_description: Get key values from etcd3 server
    description:
    - Retrieves key values and/or key prefixes from etcd3 server using its native gRPC API.
    - Try to reuse M(community.general.etcd3) options for connection parameters, but add support for some C(ETCDCTL_*) environment variables.
    - See U(https://github.com/etcd-io/etcd/tree/master/Documentation/op-guide) for etcd overview.

    options:
        _terms:
            description:
            - The list of keys (or key prefixes) to look up on the etcd3 server.
            type: list
            elements: str
            required: True
        prefix:
            description:
            - Look for key or prefix key.
            type: bool
            default: False
        endpoints:
            description:
            - Counterpart of C(ETCDCTL_ENDPOINTS) environment variable.
              Specify the etcd3 connection with and URL form eg. C(https://hostname:2379)  or C(<host>:<port>) form.
            - The C(host) part is overwritten by I(host) option, if defined.
            - The C(port) part is overwritten by I(port) option, if defined.
            env:
            - name: ETCDCTL_ENDPOINTS
            default: '127.0.0.1:2379'
            type: str
        host:
            description:
            - etcd3 listening client host.
            - Takes precedence over I(endpoints).
            type: str
        port:
            description:
            - etcd3 listening client port.
            - Takes precedence over I(endpoints).
            type: int
        ca_cert:
            description:
            - etcd3 CA authority.
            env:
            - name: ETCDCTL_CACERT
            type: str
        cert_cert:
            description:
            - etcd3 client certificate.
            env:
            - name: ETCDCTL_CERT
            type: str
        cert_key:
            description:
            - etcd3 client private key.
            env:
            - name: ETCDCTL_KEY
            type: str
        timeout:
            description:
            - Client timeout.
            default: 60
            env:
            - name: ETCDCTL_DIAL_TIMEOUT
            type: int
        user:
            description:
            - Authenticated user name.
            env:
            - name: ETCDCTL_USER
            type: str
        password:
            description:
            - Authenticated user password.
            env:
            - name: ETCDCTL_PASSWORD
            type: str

    notes:
    - I(host) and I(port) options take precedence over (endpoints) option.
    - The recommended way to connect to etcd3 server is using C(ETCDCTL_ENDPOINT)
      environment variable and keep I(endpoints), I(host), and I(port) unused.
    seealso:
    - module: community.general.etcd3
    - ref: etcd_lookup
      description: The etcd v2 lookup.

    requirements:
    - "etcd3 >= 0.10"
'''

EXAMPLES = '''
- name: "a value from a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo/bar') }}"

- name: "values from multiple folders on a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo', 'bar', 'baz') }}"

- name: "look for a key prefix"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', '/foo/bar', prefix=True) }}"

- name: "connect to etcd3 with a client certificate"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd3', 'foo/bar', cert_cert='/etc/ssl/etcd/client.pem', cert_key='/etc/ssl/etcd/client.key') }}"
'''

RETURN = '''
    _raw:
        description:
        - List of keys and associated values.
        type: list
        elements: dict
        contains:
            key:
                description: The element's key.
                type: str
            value:
                description: The element's value.
                type: str
'''

import re

from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils._text import to_native
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError, AnsibleLookupError

try:
    import etcd3
    HAS_ETCD = True
except ImportError:
    HAS_ETCD = False

display = Display()

etcd3_cnx_opts = (
    'host',
    'port',
    'ca_cert',
    'cert_key',
    'cert_cert',
    'timeout',
    'user',
    'password',
    # 'grpc_options' Etcd3Client() option currently not supported by lookup module (maybe in future ?)
)


def etcd3_client(client_params):
    try:
        etcd = etcd3.client(**client_params)
        etcd.status()
    except Exception as exp:
        raise AnsibleLookupError('Cannot connect to etcd cluster: %s' % (to_native(exp)))
    return etcd


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        if not HAS_ETCD:
            display.error(missing_required_lib('etcd3'))
            return None

        # create the etcd3 connection parameters dict to pass to etcd3 class
        client_params = {}

        # etcd3 class expects host and port as connection parameters, so endpoints
        # must be mangled a bit to fit in this scheme.
        # so here we use a regex to extract server and port
        match = re.compile(
            r'^(https?://)?(?P<host>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([-_\d\w\.]+))(:(?P<port>\d{1,5}))?/?$'
        ).match(self.get_option('endpoints'))
        if match:
            if match.group('host'):
                client_params['host'] = match.group('host')
            if match.group('port'):
                client_params['port'] = match.group('port')

        for opt in etcd3_cnx_opts:
            if self.get_option(opt):
                client_params[opt] = self.get_option(opt)

        cnx_log = dict(client_params)
        if 'password' in cnx_log:
            cnx_log['password'] = '<redacted>'
        display.verbose("etcd3 connection parameters: %s" % cnx_log)

        # connect to etcd3 server
        etcd = etcd3_client(client_params)

        ret = []
        # we can pass many keys to lookup
        for term in terms:
            if self.get_option('prefix'):
                try:
                    for val, meta in etcd.get_prefix(term):
                        if val and meta:
                            ret.append({'key': to_native(meta.key), 'value': to_native(val)})
                except Exception as exp:
                    display.warning('Caught except during etcd3.get_prefix: %s' % (to_native(exp)))
            else:
                try:
                    val, meta = etcd.get(term)
                    if val and meta:
                        ret.append({'key': to_native(meta.key), 'value': to_native(val)})
                except Exception as exp:
                    display.warning('Caught except during etcd3.get: %s' % (to_native(exp)))
        return ret

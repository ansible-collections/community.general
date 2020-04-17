# -*- coding: utf-8 -*-
#
# (c) 2020, SCC France, Eric Belhomme <ebelhomme@fr.scc.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
    author:
    - Eric Belhomme <ebelhomme@fr.scc.com>
    lookup: etcd3
    short_description: get info from an etcd3 server
    description:
    - Retrieves data from an etcd3 server.

    options:
        _terms:
            description:
            - The list of keys to look up on the etcd3 server.
            type: list
            elements: str
            required: True
        prefix:
            description:
            - look for key or prefix key
            type: bool
        host:
            description:
            - etcd3 listening client host
            env:
            - name: ETCDCTL_ENDPOINTS
            default: '127.0.0.1'
            type: str
        port:
            description:
            - etcd3 listening client port
            default: 2379
            type: int
        ca_cert:
            description:
            - etcd3 CA authority
            default: None
            env:
            - name: ETCDCTL_CACERT
            type: str
        cert_cert:
            description:
            - etcd3 client certificate
            default: None
            env:
            - name: ETCDCTL_CERT
            type: str
        cert_key:
            description:
            - etcd3 client private key
            default: None
            env:
            - name: ETCDCTL_KEY
            type: str
        timeout:
            description:
            - client timeout
            default: 60
            env:
            - name: ETCDCTL_DIAL_TIMEOUT
            type: int
        user:
            description:
            - auth user name
            default: None
            env:
            - name: ETCDCTL_USER
            type: str
        password:
            description:
            - auth user password
            default: None
            env:
            - name: ETCDCTL_PASSWORD
            type: str

    requirements:
    - "etcd3 >= 0.10"
'''

EXAMPLES = '''
    - name: "a value from a locally running etcd"
      debug:
        msg: "{{ lookup('community.general.etcd3', 'foo/bar') }}"

    - name: "values from multiple folders on a locally running etcd"
      debug:
        msg: "{{ lookup('community.general.etcd3', 'foo', 'bar', 'baz') }}"

    - name: "look for a key prefix"
      debug:
        msg: "{{ lookup('community.general.etcd3', '/foo/bar', prefix=True) }}"

    - name: "connect to etcd3 with a client certificate"
      debug:
        msg: "{{ lookup('community.general.etcd3', 'foo/bar', cert_cert='/etc/ssl/etcd/client.pem', cert_key='/etc/ssl/etcd/client.key') }}"
'''

RETURN = '''
    _raw:
        description:
        - List of keys and associated values.
        type: list
        elements: complex
'''

import os
import re
import traceback

from ansible.errors import AnsibleLookupError
from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils._text import to_native

try:
    import etcd3
    HAS_ETCD = True
except ImportError:
    HAS_ETCD = False

display = Display()


def etcd3_client(client_params):
    etcd = None
    try:
        etcd = etcd3.client(**client_params)
        etcd.status()
    except Exception as exp:
        raise AnsibleLookupError('Cannot connect to etcd cluster: %s' % (to_native(exp)))
    return etcd


class LookupModule(LookupBase):

    def log_env_override(self, params, key):
        display.verbose(
            "Overriding etcd3 '{0}' param with ENV variable '{1}'".format(
                to_native(key),
                to_native(params[key])
            )
        )

    def run(self, terms, variables, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        if not HAS_ETCD:
            display.error(missing_required_lib('etcd3'))
            return None

        # get etcd3 optional args
        client_params = {
            'host': '127.0.0.1',
            'port': 2379,
            'ca_cert': None,
            'cert_cert': None,
            'cert_key': None,
            'timeout': 60,
            'user': None,
            'password': None
        }

        # use ETCD environment variables if they are set
        etcd3_envs = {
            'ca_cert': 'ETCDCTL_CACERT',
            'cert_cert': 'ETCDCTL_CERT',
            'cert_key': 'ETCDCTL_KEY',
            'user': 'ETCDCTL_USER',
            'password': 'ETCDCTL_PASSWORD',
            'timeout': 'ETCDCTL_DIAL_TIMEOUT',
        }

        for key in etcd3_envs.keys():
            if etcd3_envs[key] in os.environ:
                client_params[key] = os.environ[etcd3_envs[key]]
                self.log_env_override(client_params, key)

        # ETCDCTL_ENDPOINTS expects something in the form <http(s)://server:port> of <server:port>
        # so here we use a regex to extract server and port
        if 'ETCDCTL_ENDPOINTS' in os.environ:
            match = re.compile(
                r'^(https?://)?(?P<host>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([-_\d\w\.]+))(:(?P<port>\d{1,5}))?/?$'
            ).match(os.environ['ETCDCTL_ENDPOINTS'])
            if match:
                if match.group('host'):
                    client_params['host'] = match.group('host')
                    self.log_env_override(client_params, 'host')
                if match.group('port'):
                    client_params['port'] = match.group('port')
                    self.log_env_override(client_params, 'port')

        # override env with optional lookup parameters
        for key in client_params.keys():
            value = kwargs.get(key)
            if value:
                client_params[key] = value

        # look for a key or for a key prefix ?
        prefix = kwargs.get('prefix')

        # connect to etcd3 server
        etcd = etcd3_client(client_params)

        ret = []
        # can pass many keys to lookup
        for term in terms:
            if prefix:
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

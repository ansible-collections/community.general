#!/usr/bin/python
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
    - Retrieves data from an etcd3 server

    options:
        _terms:
            description:
            - the list of keys to lookup on the etcd3 server
            type: list
            elements: string
            required: True
        prefix:
            description:
            - look for a key or for a prefix key
            type: boolean
        host:
            description:
            - etcd3 listening client host
            default: '127.0.0.1'
            type: string
        port:
            description:
            - etcd3 listening client port
            default: 2379
            type: integer
        ca_cert:
            description:
            - etcd3 CA authority
            default: None
            env:
            - name: ETCDCTL_CACERT
            type: string
        cert_cert:
            description:
            - etcd3 client certificate
            default: None
            env:
            - name: ETCDCTL_CERT
            type: string
        cert_key:
            description:
            - etcd3 client private key
            default: None
            env:
            - name: ETCDCTL_KEY
            type: string
        timeout:
            description:
            - client timeout
            default: 60
            type: integer
        user:
            description:
            - auth user name
            default: None
            type: string
        password:
            description:
            - auth user password
            default: None
            type: string

    requirements:
    - "etcd3 >= 0.12"
'''

EXAMPLES = '''
    - name: "a value from a locally running etcd"
      debug: msg={{ lookup('etcd3', 'foo/bar') }}

    - name: "values from multiple folders on a locally running etcd"
      debug: msg={{ lookup('etcd3', 'foo', 'bar', 'baz') }}

    - name: "look for a key prefix"
      debug: msg="{{ lookup('etcd3', '/foo/bar', prefix=True) }}"

    - name: "connect to etcd3 with a client certificate"
      debug msg: "{{ lookup('etcd3', 'foo/bar', cert_cert='/etc/ssl/etcd/client.pem', cert_key='/etc/ssl/etcd/client.key') }}"
'''

RETURN = '''
    _raw:
        description:
        - list of keys and associated values
        type: list
        elements: complex
'''

import os
import traceback

from ansible.plugins.lookup import LookupBase
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils._text import to_native

try:
    import etcd3
    HAS_ETCD = True
except ImportError:
    ETCD_IMP_ERR = traceback.format_exc()
    HAS_ETCD = False


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        if not HAS_ETCD:
            self._display.error(missing_required_lib('etcd3'))
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
        }
        for key in etcd3_envs.keys():
            value = os.getenv(etcd3_envs[key])
            if value:
                client_params[key] = value

        # override env with optional lookup parameters
        for key in client_params.keys():
            value = kwargs.get(key)
            if value:
                client_params[key] = value

        # look for a key or for a key prefix ?
        prefix = kwargs.get('prefix')

        try:
            etcd = etcd3.client(**client_params)
        except Exception as exp:
            self._display.warning('Cannot connect to etcd cluster: %s' % (to_native(exp)))
            return None

        ret = []
        for term in terms:
            key = term.split()[0]
            if prefix:
                try:
                    for val, meta in etcd.get_prefix(key):
                        ret.append({'key': to_native(meta.key), 'value': to_native(val)})
                except Exception as exp:
                    pass
            else:
                try:
                    val, meta = etcd.get(key)
                    ret.append({'key': to_native(meta.key), 'value': to_native(val)})
                except Exception as exp:
                    pass
        return ret

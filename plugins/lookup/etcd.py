# -*- coding: utf-8 -*-
# Copyright (c) 2013, Jan-Piet Mens <jpmens(at)gmail.com>
# (m) 2016, Mihai Moldovanu <mihaim@tfm.ro>
# (m) 2017, Juan Manuel Parrilla <jparrill@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
author:
  - Jan-Piet Mens (@jpmens)
name: etcd
short_description: Get info from an etcd server
description:
  - Retrieves data from an etcd server.
options:
  _terms:
    description:
      - The list of keys to lookup on the etcd server.
    type: list
    elements: string
    required: true
  url:
    description:
      - Environment variable with the URL for the etcd server.
    type: string
    default: 'http://127.0.0.1:4001'
    env:
      - name: ANSIBLE_ETCD_URL
  version:
    description:
      - Environment variable with the etcd protocol version.
    type: string
    default: 'v1'
    env:
      - name: ANSIBLE_ETCD_VERSION
  validate_certs:
    description:
      - Toggle checking that the ssl certificates are valid, you normally only want to turn this off with self-signed certs.
    default: true
    type: boolean
seealso:
  - module: community.general.etcd3
  - plugin: community.general.etcd3
    plugin_type: lookup
"""

EXAMPLES = r"""
- name: "a value from a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd', 'foo/bar') }}"

- name: "values from multiple folders on a locally running etcd"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd', 'foo', 'bar', 'baz') }}"

- name: "you can set server options inline"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.etcd', 'foo', version='v2', url='http://192.168.0.27:4001') }}"
"""

RETURN = r"""
_raw:
  description:
    - List of values associated with input keys.
  type: list
  elements: string
"""

import json

from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url

# this can be made configurable, not should not use ansible.cfg
#
# Made module configurable from playbooks:
# If etcd  v2 running on host 192.168.1.21 on port 2379
# we can use the following in a playbook to retrieve /tfm/network/config key
#
# - ansible.builtin.debug: msg={{lookup('etcd','/tfm/network/config', url='http://192.168.1.21:2379' , version='v2')}}
#
# Example Output:
#
# TASK [debug] *******************************************************************
# ok: [localhost] => {
#     "msg": {
#         "Backend": {
#             "Type": "vxlan"
#         },
#         "Network": "172.30.0.0/16",
#         "SubnetLen": 24
#     }
# }
#
#
#
#


class Etcd:
    def __init__(self, url, version, validate_certs):
        self.url = url
        self.version = version
        self.baseurl = f'{self.url}/{self.version}/keys'
        self.validate_certs = validate_certs

    def _parse_node(self, node):
        # This function will receive all etcd tree,
        # if the level requested has any node, the recursion starts
        # create a list in the dir variable and it is passed to the
        # recursive function, and so on, if we get a variable,
        # the function will create a key-value at this level and
        # undoing the loop.
        path = {}
        if node.get('dir', False):
            for n in node.get('nodes', []):
                path[n['key'].split('/')[-1]] = self._parse_node(n)

        else:
            path = node['value']

        return path

    def get(self, key):
        url = f"{self.baseurl}/{key}?recursive=true"
        data = None
        value = {}
        try:
            r = open_url(url, validate_certs=self.validate_certs)
            data = r.read()
        except Exception:
            return None

        try:
            # I will not support Version 1 of etcd for folder parsing
            item = json.loads(data)
            if self.version == 'v1':
                # When ETCD are working with just v1
                if 'value' in item:
                    value = item['value']
            else:
                if 'node' in item:
                    # When a usual result from ETCD
                    value = self._parse_node(item['node'])

            if 'errorCode' in item:
                # Here return an error when an unknown entry responds
                value = "ENOENT"
        except Exception:
            raise

        return value


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        validate_certs = self.get_option('validate_certs')
        url = self.get_option('url')
        version = self.get_option('version')

        etcd = Etcd(url=url, version=version, validate_certs=validate_certs)

        ret = []
        for term in terms:
            key = term.split()[0]
            value = etcd.get(key)
            ret.append(value)
        return ret

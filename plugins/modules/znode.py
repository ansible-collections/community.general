#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 WP Engine, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: znode
short_description: Create, delete, retrieve, and update znodes using ZooKeeper
description:
    - Create, delete, retrieve, and update znodes using ZooKeeper.
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
extends_documentation_fragment:
    - community.general.attributes
options:
    hosts:
        description:
            - A list of ZooKeeper servers (format '[server]:[port]').
        required: true
        type: str
    name:
        description:
            - The path of the znode.
        required: true
        type: str
    value:
        description:
            - The value assigned to the znode.
        type: str
    op:
        description:
            - An operation to perform. Mutually exclusive with state.
        choices: [ get, wait, list ]
        type: str
    state:
        description:
            - The state to enforce. Mutually exclusive with op.
        choices: [ present, absent ]
        type: str
    timeout:
        description:
            - The amount of time to wait for a node to appear.
        default: 300
        type: int
    recursive:
        description:
            - Recursively delete node and all its children.
        type: bool
        default: false
    auth_scheme:
        description:
            - 'Authentication scheme.'
        choices: [ digest, sasl ]
        type: str
        default: "digest"
        required: false
        version_added: 5.8.0
    auth_credential:
        description:
            - The authentication credential value. Depends on I(auth_scheme).
            - The format for I(auth_scheme=digest) is C(user:password),
              and the format for I(auth_scheme=sasl) is C(user:password).
        type: str
        required: false
        version_added: 5.8.0
    use_tls:
        description:
            - Using TLS/SSL or not.
        type: bool
        default: false
        required: false
        version_added: '6.5.0'
requirements:
    - kazoo >= 2.1
    - python >= 2.6
author: "Trey Perry (@treyperry)"
'''

EXAMPLES = """
- name: Creating or updating a znode with a given value
  community.general.znode:
    hosts: 'localhost:2181'
    name: /mypath
    value: myvalue
    state: present

- name: Getting the value and stat structure for a znode
  community.general.znode:
    hosts: 'localhost:2181'
    name: /mypath
    op: get

- name: Getting the value and stat structure for a znode using digest authentication
  community.general.znode:
    hosts: 'localhost:2181'
    auth_credential: 'user1:s3cr3t'
    name: /secretmypath
    op: get

- name: Listing a particular znode's children
  community.general.znode:
    hosts: 'localhost:2181'
    name: /zookeeper
    op: list

- name: Waiting 20 seconds for a znode to appear at path /mypath
  community.general.znode:
    hosts: 'localhost:2181'
    name: /mypath
    op: wait
    timeout: 20

- name: Deleting a znode at path /mypath
  community.general.znode:
    hosts: 'localhost:2181'
    name: /mypath
    state: absent

- name: Creating or updating a znode with a given value on a remote Zookeeper
  community.general.znode:
    hosts: 'my-zookeeper-node:2181'
    name: /mypath
    value: myvalue
    state: present
  delegate_to: 127.0.0.1
"""

import time
import traceback

KAZOO_IMP_ERR = None
try:
    from kazoo.client import KazooClient
    from kazoo.handlers.threading import KazooTimeoutError
    KAZOO_INSTALLED = True
except ImportError:
    KAZOO_IMP_ERR = traceback.format_exc()
    KAZOO_INSTALLED = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hosts=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            value=dict(type='str'),
            op=dict(choices=['get', 'wait', 'list']),
            state=dict(choices=['present', 'absent']),
            timeout=dict(default=300, type='int'),
            recursive=dict(default=False, type='bool'),
            auth_scheme=dict(default='digest', choices=['digest', 'sasl']),
            auth_credential=dict(type='str', no_log=True),
            use_tls=dict(default=False, type='bool'),
        ),
        supports_check_mode=False
    )

    if not KAZOO_INSTALLED:
        module.fail_json(msg=missing_required_lib('kazoo >= 2.1'), exception=KAZOO_IMP_ERR)

    check = check_params(module.params)
    if not check['success']:
        module.fail_json(msg=check['msg'])

    zoo = KazooCommandProxy(module)
    try:
        zoo.start()
    except KazooTimeoutError:
        module.fail_json(msg='The connection to the ZooKeeper ensemble timed out.')

    command_dict = {
        'op': {
            'get': zoo.get,
            'list': zoo.list,
            'wait': zoo.wait
        },
        'state': {
            'present': zoo.present,
            'absent': zoo.absent
        }
    }

    command_type = 'op' if 'op' in module.params and module.params['op'] is not None else 'state'
    method = module.params[command_type]
    result, result_dict = command_dict[command_type][method]()
    zoo.shutdown()

    if result:
        module.exit_json(**result_dict)
    else:
        module.fail_json(**result_dict)


def check_params(params):
    if not params['state'] and not params['op']:
        return {'success': False, 'msg': 'Please define an operation (op) or a state.'}

    if params['state'] and params['op']:
        return {'success': False, 'msg': 'Please choose an operation (op) or a state, but not both.'}

    return {'success': True}


class KazooCommandProxy():
    def __init__(self, module):
        self.module = module
        self.zk = KazooClient(module.params['hosts'], use_ssl=module.params['use_tls'])

    def absent(self):
        return self._absent(self.module.params['name'])

    def exists(self, znode):
        return self.zk.exists(znode)

    def list(self):
        children = self.zk.get_children(self.module.params['name'])
        return True, {'count': len(children), 'items': children, 'msg': 'Retrieved znodes in path.',
                      'znode': self.module.params['name']}

    def present(self):
        return self._present(self.module.params['name'], self.module.params['value'])

    def get(self):
        return self._get(self.module.params['name'])

    def shutdown(self):
        self.zk.stop()
        self.zk.close()

    def start(self):
        self.zk.start()
        if self.module.params['auth_credential']:
            self.zk.add_auth(self.module.params['auth_scheme'], self.module.params['auth_credential'])

    def wait(self):
        return self._wait(self.module.params['name'], self.module.params['timeout'])

    def _absent(self, znode):
        if self.exists(znode):
            self.zk.delete(znode, recursive=self.module.params['recursive'])
            return True, {'changed': True, 'msg': 'The znode was deleted.'}
        else:
            return True, {'changed': False, 'msg': 'The znode does not exist.'}

    def _get(self, path):
        if self.exists(path):
            value, zstat = self.zk.get(path)
            stat_dict = {}
            for i in dir(zstat):
                if not i.startswith('_'):
                    attr = getattr(zstat, i)
                    if isinstance(attr, (int, str)):
                        stat_dict[i] = attr
            result = True, {'msg': 'The node was retrieved.', 'znode': path, 'value': value,
                            'stat': stat_dict}
        else:
            result = False, {'msg': 'The requested node does not exist.'}

        return result

    def _present(self, path, value):
        if self.exists(path):
            (current_value, zstat) = self.zk.get(path)
            if value != current_value:
                self.zk.set(path, to_bytes(value))
                return True, {'changed': True, 'msg': 'Updated the znode value.', 'znode': path,
                              'value': value}
            else:
                return True, {'changed': False, 'msg': 'No changes were necessary.', 'znode': path, 'value': value}
        else:
            self.zk.create(path, to_bytes(value), makepath=True)
            return True, {'changed': True, 'msg': 'Created a new znode.', 'znode': path, 'value': value}

    def _wait(self, path, timeout, interval=5):
        lim = time.time() + timeout

        while time.time() < lim:
            if self.exists(path):
                return True, {'msg': 'The node appeared before the configured timeout.',
                              'znode': path, 'timeout': timeout}
            else:
                time.sleep(interval)

        return False, {'msg': 'The node did not appear before the operation timed out.', 'timeout': timeout,
                       'znode': path}


if __name__ == '__main__':
    main()

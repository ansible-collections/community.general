# -*- coding: utf-8 -*-
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: xen_orchestra
    short_description: Xen Orchestra inventory source
    version_added: 4.1.0
    author:
        - Dom Del Nano (@ddelnano) <ddelnano@gmail.com>
        - Samori Gorse (@shinuza) <samorigorse@gmail.com>
    requirements:
        - websocket-client >= 1.0.0
    description:
        - Get inventory hosts from a Xen Orchestra deployment.
        - 'Uses a configuration file as an inventory source, it must end in C(.xen_orchestra.yml) or C(.xen_orchestra.yaml).'
    extends_documentation_fragment:
        - constructed
        - inventory_cache
    options:
        plugin:
            description: The name of this plugin, it should always be set to V(community.general.xen_orchestra) for this plugin to recognize it as its own.
            required: true
            choices: ['community.general.xen_orchestra']
            type: str
        api_host:
            description:
                - API host to XOA API.
                - If the value is not specified in the inventory configuration, the value of environment variable E(ANSIBLE_XO_HOST) will be used instead.
            type: str
            env:
                - name: ANSIBLE_XO_HOST
        user:
            description:
                - Xen Orchestra user.
                - If the value is not specified in the inventory configuration, the value of environment variable E(ANSIBLE_XO_USER) will be used instead.
            required: true
            type: str
            env:
                - name: ANSIBLE_XO_USER
        password:
            description:
                - Xen Orchestra password.
                - If the value is not specified in the inventory configuration, the value of environment variable E(ANSIBLE_XO_PASSWORD) will be used instead.
            required: true
            type: str
            env:
                - name: ANSIBLE_XO_PASSWORD
        validate_certs:
            description: Verify TLS certificate if using HTTPS.
            type: boolean
            default: true
        use_ssl:
            description: Use wss when connecting to the Xen Orchestra API
            type: boolean
            default: true
'''


EXAMPLES = '''
# file must be named xen_orchestra.yaml or xen_orchestra.yml
plugin: community.general.xen_orchestra
api_host: 192.168.1.255
user: xo
password: xo_pwd
validate_certs: true
use_ssl: true
groups:
    kube_nodes: "'kube_node' in tags"
compose:
    ansible_port: 2222

'''

import json
import ssl
from time import sleep

from ansible.errors import AnsibleError

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible.module_utils.basic import AnsibleModule

# 3rd party imports
try:
    HAS_WEBSOCKET = True
    import websocket
    from websocket import create_connection

    if LooseVersion(websocket.__version__) <= LooseVersion('1.0.0'):
        raise ImportError
except ImportError as e:
    HAS_WEBSOCKET = False


HALTED = 'Halted'
PAUSED = 'Paused'
RUNNING = 'Running'
SUSPENDED = 'Suspended'
POWER_STATES = [RUNNING, HALTED, SUSPENDED, PAUSED]
HOST_GROUP = 'xo_hosts'
POOL_GROUP = 'xo_pools'


def clean_group_name(label):
    return label.lower().replace(' ', '-').replace('-', '_')


class XenOrchestra(object):
    ''' Host inventory parser for ansible using XenOrchestra as source. '''

    NAME = 'community.general.xen_orchestra'
    CALL_TIMEOUT = 100
    """Number of 1/10ths of a second to wait before method call times out."""


    def __init__(self, module):
        # from config
        self.counter = -1
        self.con = None
        self.module = module

        self.create_connection(module['api_host'])
        self.login(module['user'], module['password'])

    @property
    def pointer(self):
        self.counter += 1
        return self.counter

    def create_connection(self, xoa_api_host):
        validate_certs = self.module['validate_certs']
        use_ssl = self.module['use_ssl']
        proto = 'wss' if use_ssl else 'ws'

        sslopt = None if validate_certs else {'cert_reqs': ssl.CERT_NONE}
        self.conn = create_connection(
            '{0}://{1}/api/'.format(proto, xoa_api_host), sslopt=sslopt)

    def call(self, method, params):
        """Calls a method on the XO server with the provided parameters."""
        id = self.pointer
        self.conn.send(json.dumps({
            'id': id,
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }))

        waited = 0
        while waited < self.CALL_TIMEOUT:
            response = json.loads(self.conn.recv())
            if 'id' in response and response['id'] == id:
                return response
            else:
                sleep(0.1)
                waited += 1

        raise AnsibleError(
            'Method call {method} timed out after {timeout} seconds.'.format(method=method, timeout=self.CALL_TIMEOUT / 10))

    def login(self, user, password):
        answer = self.call('session.signIn', {
            'username': user, 'password': password
        })

        if 'error' in answer:
            raise AnsibleError(
                'Could not connect: {0}'.format(answer['error']))
        
    def stop_vm(self, vm_uid):
        answer = self.call('vm.stop', {'id': vm_uid})

        if 'error' in answer:
            raise AnsibleError(
                'Could not request: {0}'.format(answer['error']))
        
        return answer['result']
    
    def start_vm(self, vm_uid):
        answer = self.call('vm.start', {'id': vm_uid})

        if 'error' in answer:
            raise AnsibleError(
                'Could not request: {0}'.format(answer['error']))
        
        return answer['result']

    def get_object(self, name):
        answer = self.call('xo.getAllObjects', {'filter': {'type': name}})

        if 'error' in answer:
            raise AnsibleError(
                'Could not request: {0}'.format(answer['error']))

        return answer['result']


def main():
    module_args = dict(
        api_host=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool', default=True),
        use_ssl=dict(type='bool', default=True),
        vm_uid=dict(type='str'),
        state=dict(default='present', choices=['absent', 'stopped', 'started', 'restarted']),
    )

    xen_orchestra = XenOrchestra()
    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
    )

    state = module.params['state']
    vm_uid = module.params['vm_uid']

    if state == 'stopped':
        xen_orchestra.stop_vm(vm_uid)
        module.exit_json(changed=True)

    if state == 'started':
        xen_orchestra.start_vm(vm_uid)
        module.exit_json(changed=True)

if __name__ == '__main__':
    main()

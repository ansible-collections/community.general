# -*- coding: utf-8 -*-
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: xen_orchestra
    short_description: Management of instances on Xen Orchestra
    version_added: 9.0.1
    author:
      - Samori Gorse (@shinuza) <samorigorse@gmail.com>
    requirements:
      - websocket-client >= 1.0.0
    description:
      - Allows you to create/delete/restart/stop instances on Xen Orchestra
    options:
      api_host:
        description: API host to XOA API.
        type: str
      user:
        description: Xen Orchestra user.
        required: true
        type: str
      password:
        description: Xen Orchestra password.
        required: true
        type: str
      validate_certs:
        description: Verify TLS certificate if using HTTPS.
        type: boolean
        default: true
      use_ssl:
        description: Use wss when connecting to the Xen Orchestra API
        type: boolean
        default: true
      state:
        description: State in which the Virtual Machine should be
        choices: ['present', 'started', 'absent', 'stopped', 'restarted']
        default: present
      label:
        description: Label of the Virtual Machine to create, can be used when O(state=present)
        type: boolean
        default: false
      description:
        description: Description of the Virtual Machine to create, can be used when O(state=present)
        type: boolean
        default: false
      boot_after_create:
        description: Boot Virtual Machine after creation, can be used when O(state=present)
        type: boolean
        default: false
'''


EXAMPLES = r'''
- name: Create a new virtual machine
  community.general.xen_orchestra:
    api_host: xen-orchestra.lab
    user: user
    password: passw0rd
    validate_certs: no
    state: present
    template: 355ee47d-ff4c-4924-3db2-fd86ae629676-a3d70e4d-c5ac-4dfb-999b-30a0a7efe546
    label: This is a test from ansible
    description: This is a test from ansible
    boot_after_create: no

- name: Start an existing virtual machine
  community.general.xen_orchestra:
    api_host: xen-orchestra.lab
    user: user
    password: passw0rd
    validate_certs: no
    state: started

- name: Stop an existing virtual machine
  community.general.xen_orchestra:
    api_host: xen-orchestra.lab
    user: user
    password: passw0rd
    validate_certs: no
    state: stop

- name: Restart an existing virtual machine
  community.general.xen_orchestra:
    api_host: xen-orchestra.lab
    user: user
    password: passw0rd
    validate_certs: no
    state: stopped

- name: Delete a virtual machine
  community.general.xen_orchestra:
    api_host: xen-orchestra.lab
    user: user
    password: passw0rd
    validate_certs: no
    state: absent
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

    if LooseVersion(websocket.__version__) < LooseVersion('1.0.0'):
        raise ImportError
except ImportError as e:
    HAS_WEBSOCKET = False

OBJECT_NOT_FOUND = 1
VM_STATE_ERROR = 13


class XenOrchestra(object):
    ''' Host inventory parser for ansible using XenOrchestra as source. '''

    NAME = 'community.general.xen_orchestra'
    CALL_TIMEOUT = 100
    '''Number of 1/10ths of a second to wait before method call times out.'''

    def __init__(self, module):
        # from config
        self.counter = -1
        self.con = None
        self.module = module

        self.create_connection(module.params['api_host'])
        self.login(module.params['user'], module.params['password'])

    @property
    def pointer(self):
        self.counter += 1
        return self.counter

    def create_connection(self, xoa_api_host):
        validate_certs = self.module.params['validate_certs']
        use_ssl = self.module.params['use_ssl']
        proto = 'wss' if use_ssl else 'ws'

        sslopt = None if validate_certs else {'cert_reqs': ssl.CERT_NONE}
        self.conn = create_connection(
            '{0}://{1}/api/'.format(proto, xoa_api_host), sslopt=sslopt)

    def call(self, method, params):
        '''Calls a method on the XO server with the provided parameters.'''
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
            raise self.module.fail_json(
                'Could not connect: {0}'.format(answer['error']))

        return answer['result']

    def create_vm(self):
        params = {
            'template': self.module.params['template'],
            'name_label': self.module.params['label'],
            'bootAfterCreate': self.module.params.get('boot_after_create', False)
        }

        description = self.module.params.get('description')
        if description:
            params['name_description'] = description

        answer = self.call('vm.create', params)

        if 'error' in answer:
            raise self.module.fail_json(
                'Could not create vm: {0}'.format(answer['error']))

        return answer['result']

    def restart_vm(self, vm_uid):
        answer = self.call('vm.restart', {'id': vm_uid, 'force': True})

        if 'error' in answer:
            raise self.module.fail_json(
                'Could not restart vm: {0}'.format(answer['error']))

        return answer['result']

    def stop_vm(self, vm_uid):
        answer = self.call('vm.stop', {'id': vm_uid, 'force': True})

        if 'error' in answer:
            # VM is not paused, suspended or running
            if answer['error']['code'] == VM_STATE_ERROR:
                return False
            raise self.module.fail_json(
                'Could not stop vm: {0}'.format(answer['error']))

        return answer['result']

    def start_vm(self, vm_uid):
        answer = self.call('vm.start', {'id': vm_uid})

        if 'error' in answer:
            # VM is already started, nothing to do
            if answer['error']['code'] == VM_STATE_ERROR:
                return False
            raise self.module.fail_json(
                'Could not start vm: {0}'.format(answer['error']))

        return answer['result']

    def delete_vm(self, vm_uid):
        answer = self.call('vm.delete', {'id': vm_uid})

        if 'error' in answer:
            if answer['error']['code'] == OBJECT_NOT_FOUND:
                return False
            raise self.module.fail_json(
                'Could not delete vm: {0}'.format(answer['error']))

        return answer['result']


def main():
    if not HAS_WEBSOCKET:
        raise AnsibleError('This module requires websocket-client 1.0.0 or higher: '
                           'https://github.com/websocket-client/websocket-client.')

    module_args = dict(
        api_host=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool', default=True),
        use_ssl=dict(type='bool', default=True),
        vm_uid=dict(type='str'),
        template=dict(type='str'),
        label=dict(type='str'),
        description=dict(type='str'),
        boot_after_create=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent', 'stopped', 'started', 'restarted']),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ('state', 'present', ['template', 'label']),
            ('state', 'absent', ('vm_uid')),
            ('state', 'started', ('vm_uid')),
            ('state', 'restarted', ('vm_uid')),
            ('state', 'stopped', ('vm_uid')),
        ],
    )
    xen_orchestra = XenOrchestra(module)

    state = module.params['state']
    vm_uid = module.params['vm_uid']

    if state == 'stopped':
        result = xen_orchestra.stop_vm(vm_uid)
        module.exit_json(changed=result)

    if state == 'started':
        result = xen_orchestra.start_vm(vm_uid)
        module.exit_json(changed=result)

    if state == 'restarted':
        result = xen_orchestra.restart_vm(vm_uid)
        module.exit_json(changed=result)

    if state == 'absent':
        result = xen_orchestra.delete_vm(vm_uid)
        module.exit_json(changed=result)

    if state == 'present':
        result = xen_orchestra.create_vm()
        module.exit_json(changed=True, vm_uid=result)


if __name__ == '__main__':
    main()

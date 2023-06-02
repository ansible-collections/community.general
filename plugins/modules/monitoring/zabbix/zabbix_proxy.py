#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Alen Komic
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
module: zabbix_proxy
short_description: Create/delete/get/update Zabbix proxies
description:
   - This module allows you to create, modify, get and delete Zabbix proxy entries.
author:
    - "Alen Komic (@akomic)"
requirements:
    - "python >= 2.6"
    - "zabbix-api >= 0.5.4"
options:
    proxy_name:
        description:
            - Name of the proxy in Zabbix.
        required: true
        type: str
    proxy_address:
        description:
            - Comma-delimited list of IP/CIDR addresses or DNS names to accept active proxy requests from.
            - Requires I(status=active).
            - Works only with >= Zabbix 4.0. ( remove option for <= 4.0 )
        required: false
        type: str
    description:
        description:
            - Description of the proxy.
        required: false
        type: str
    status:
        description:
            - Type of proxy. (4 - active, 5 - passive)
        required: false
        choices: ['active', 'passive']
        default: "active"
        type: str
    tls_connect:
        description:
            - Connections to proxy.
        required: false
        choices: ['no_encryption','PSK','certificate']
        default: 'no_encryption'
        type: str
    tls_accept:
        description:
            - Connections from proxy.
        required: false
        choices: ['no_encryption','PSK','certificate']
        default: 'no_encryption'
        type: str
    ca_cert:
        description:
            - Certificate issuer.
        required: false
        aliases: [ tls_issuer ]
        type: str
    tls_subject:
        description:
            - Certificate subject.
        required: false
        type: str
    tls_psk_identity:
        description:
            - PSK identity. Required if either I(tls_connect) or I(tls_accept) has PSK enabled.
        required: false
        type: str
    tls_psk:
        description:
            - The preshared key, at least 32 hex digits. Required if either I(tls_connect) or I(tls_accept) has PSK enabled.
        required: false
        type: str
    state:
        description:
            - State of the proxy.
            - On C(present), it will create if proxy does not exist or update the proxy if the associated data is different.
            - On C(absent) will remove a proxy if it exists.
        required: false
        choices: ['present', 'absent']
        default: "present"
        type: str
    interface:
        description:
            - Dictionary with params for the interface when proxy is in passive mode.
            - For more information, review proxy interface documentation at
            - U(https://www.zabbix.com/documentation/4.0/manual/api/reference/proxy/object#proxy_interface).
        required: false
        suboptions:
            useip:
                type: int
                description:
                    - Connect to proxy interface with IP address instead of DNS name.
                    - 0 (don't use ip), 1 (use ip).
                default: 0
                choices: [0, 1]
            ip:
                type: str
                description:
                    - IP address used by proxy interface.
                    - Required if I(useip=1).
                default: ''
            dns:
                type: str
                description:
                    - DNS name of the proxy interface.
                    - Required if I(useip=0).
                default: ''
            port:
                type: str
                description:
                    - Port used by proxy interface.
                default: '10051'
            type:
                type: int
                description:
                    - Interface type to add.
                    - This suboption is currently ignored for Zabbix proxy.
                    - This suboption is deprecated since Ansible 2.10 and will eventually be removed in 2.14.
                required: false
                default: 0
            main:
                type: int
                description:
                    - Whether the interface is used as default.
                    - This suboption is currently ignored for Zabbix proxy.
                    - This suboption is deprecated since Ansible 2.10 and will eventually be removed in 2.14.
                required: false
                default: 0
        default: {}
        type: dict

extends_documentation_fragment:
- community.general.zabbix

'''

EXAMPLES = r'''
- name: Create or update a proxy with proxy type active
  local_action:
    module: zabbix_proxy
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    proxy_name: ExampleProxy
    description: ExampleProxy
    status: active
    state: present
    proxy_address: ExampleProxy.local

- name: Create a new passive proxy using only it's IP
  local_action:
    module: zabbix_proxy
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    proxy_name: ExampleProxy
    description: ExampleProxy
    status: passive
    state: present
    interface:
      useip: 1
      ip: 10.1.1.2
      port: 10051

- name: Create a new passive proxy using only it's DNS
  local_action:
    module: zabbix_proxy
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    proxy_name: ExampleProxy
    description: ExampleProxy
    status: passive
    state: present
    interface:
      dns: proxy.example.com
      port: 10051
'''

RETURN = r''' # '''


import traceback
import atexit

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
try:
    from zabbix_api import ZabbixAPI

    HAS_ZABBIX_API = True
except ImportError:
    ZBX_IMP_ERR = traceback.format_exc()
    HAS_ZABBIX_API = False


class Proxy(object):
    def __init__(self, module, zbx):
        self._module = module
        self._zapi = zbx
        self.existing_data = None

    def proxy_exists(self, proxy_name):
        result = self._zapi.proxy.get({
            'output': 'extend', 'selectInterface': 'extend',
            'filter': {'host': proxy_name}})

        if len(result) > 0 and 'proxyid' in result[0]:
            self.existing_data = result[0]
            return result[0]['proxyid']
        else:
            return result

    def add_proxy(self, data):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)

            parameters = {}
            for item in data:
                if data[item]:
                    parameters[item] = data[item]

            if 'proxy_address' in data and data['status'] != '5':
                parameters.pop('proxy_address', False)

            if 'interface' in data and data['status'] != '6':
                parameters.pop('interface', False)

            proxy_ids_list = self._zapi.proxy.create(parameters)
            self._module.exit_json(changed=True,
                                   result="Successfully added proxy %s (%s)" %
                                          (data['host'], data['status']))
            if len(proxy_ids_list) >= 1:
                return proxy_ids_list['proxyids'][0]
        except Exception as e:
            self._module.fail_json(msg="Failed to create proxy %s: %s" %
                                   (data['host'], e))

    def delete_proxy(self, proxy_id, proxy_name):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.proxy.delete([proxy_id])
            self._module.exit_json(changed=True,
                                   result="Successfully deleted"
                                          + " proxy %s" % proxy_name)
        except Exception as e:
            self._module.fail_json(msg="Failed to delete proxy %s: %s" %
                                       (proxy_name, str(e)))

    def compile_interface_params(self, new_interface):
        old_interface = {}
        if 'interface' in self.existing_data and \
           len(self.existing_data['interface']) > 0:
            old_interface = self.existing_data['interface']

        for item in ['type', 'main']:
            new_interface.pop(item, False)

        final_interface = old_interface.copy()
        final_interface.update(new_interface)
        final_interface = dict((k, str(v)) for k, v in final_interface.items())

        if final_interface != old_interface:
            return final_interface
        else:
            return {}

    def update_proxy(self, proxy_id, data):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            parameters = {'proxyid': proxy_id}

            for item in data:
                if data[item] and item in self.existing_data and \
                   self.existing_data[item] != data[item]:
                    parameters[item] = data[item]

            if 'interface' in parameters:
                parameters.pop('interface')

            if 'proxy_address' in data and data['status'] != '5':
                parameters.pop('proxy_address', False)

            if 'interface' in data and data['status'] != '6':
                parameters.pop('interface', False)

            if 'interface' in data and data['status'] == '6':
                new_interface = self.compile_interface_params(data['interface'])
                if len(new_interface) > 0:
                    parameters['interface'] = new_interface

            if len(parameters) > 1:
                self._zapi.proxy.update(parameters)
                self._module.exit_json(
                    changed=True,
                    result="Successfully updated proxy %s (%s)" %
                           (data['host'], proxy_id)
                )
            else:
                self._module.exit_json(changed=False)
        except Exception as e:
            self._module.fail_json(msg="Failed to update proxy %s: %s" %
                                       (data['host'], e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(type='str', required=True, aliases=['url']),
            login_user=dict(type='str', required=True),
            login_password=dict(type='str', required=True, no_log=True),
            proxy_name=dict(type='str', required=True),
            proxy_address=dict(type='str', required=False),
            http_login_user=dict(type='str', required=False, default=None),
            http_login_password=dict(type='str', required=False,
                                     default=None, no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            status=dict(type='str', default="active", choices=['active', 'passive']),
            state=dict(type='str', default="present", choices=['present', 'absent']),
            description=dict(type='str', required=False),
            tls_connect=dict(type='str', default='no_encryption',
                             choices=['no_encryption', 'PSK', 'certificate']),
            tls_accept=dict(type='str', default='no_encryption',
                            choices=['no_encryption', 'PSK', 'certificate']),
            ca_cert=dict(type='str', required=False, default=None, aliases=['tls_issuer']),
            tls_subject=dict(type='str', required=False, default=None),
            tls_psk_identity=dict(type='str', required=False, default=None),
            tls_psk=dict(type='str', required=False, default=None),
            timeout=dict(type='int', default=10),
            interface=dict(
                type='dict',
                required=False,
                default={},
                options=dict(
                    useip=dict(type='int', choices=[0, 1], default=0),
                    ip=dict(type='str', default=''),
                    dns=dict(type='str', default=''),
                    port=dict(type='str', default='10051'),
                    type=dict(type='int', default=0, removed_in_version='2.14'),
                    main=dict(type='int', default=0, removed_in_version='2.14')
                ),
            )
        ),
        supports_check_mode=True
    )

    if not HAS_ZABBIX_API:
        module.fail_json(msg=missing_required_lib('zabbix-api', url='https://pypi.org/project/zabbix-api/'), exception=ZBX_IMP_ERR)

    server_url = module.params['server_url']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    http_login_user = module.params['http_login_user']
    http_login_password = module.params['http_login_password']
    validate_certs = module.params['validate_certs']
    proxy_name = module.params['proxy_name']
    proxy_address = module.params['proxy_address']
    description = module.params['description']
    status = module.params['status']
    tls_connect = module.params['tls_connect']
    tls_accept = module.params['tls_accept']
    tls_issuer = module.params['ca_cert']
    tls_subject = module.params['tls_subject']
    tls_psk_identity = module.params['tls_psk_identity']
    tls_psk = module.params['tls_psk']
    state = module.params['state']
    timeout = module.params['timeout']
    interface = module.params['interface']

    # convert enabled to 0; disabled to 1
    status = 6 if status == "passive" else 5

    if tls_connect == 'certificate':
        tls_connect = 4
    elif tls_connect == 'PSK':
        tls_connect = 2
    else:
        tls_connect = 1

    if tls_accept == 'certificate':
        tls_accept = 4
    elif tls_accept == 'PSK':
        tls_accept = 2
    else:
        tls_accept = 1

    zbx = None
    # login to zabbix
    try:
        zbx = ZabbixAPI(server_url, timeout=timeout,
                        user=http_login_user,
                        passwd=http_login_password,
                        validate_certs=validate_certs)
        zbx.login(login_user, login_password)
        atexit.register(zbx.logout)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

    proxy = Proxy(module, zbx)

    # check if proxy already exists
    proxy_id = proxy.proxy_exists(proxy_name)

    if proxy_id:
        if state == "absent":
            # remove proxy
            proxy.delete_proxy(proxy_id, proxy_name)
        else:
            proxy.update_proxy(proxy_id, {
                'host': proxy_name,
                'description': description,
                'status': str(status),
                'tls_connect': str(tls_connect),
                'tls_accept': str(tls_accept),
                'tls_issuer': tls_issuer,
                'tls_subject': tls_subject,
                'tls_psk_identity': tls_psk_identity,
                'tls_psk': tls_psk,
                'interface': interface,
                'proxy_address': proxy_address
            })
    else:
        if state == "absent":
            # the proxy is already deleted.
            module.exit_json(changed=False)

        proxy_id = proxy.add_proxy(data={
            'host': proxy_name,
            'description': description,
            'status': str(status),
            'tls_connect': str(tls_connect),
            'tls_accept': str(tls_accept),
            'tls_issuer': tls_issuer,
            'tls_subject': tls_subject,
            'tls_psk_identity': tls_psk_identity,
            'tls_psk': tls_psk,
            'interface': interface,
            'proxy_address': proxy_address
        })


if __name__ == '__main__':
    main()

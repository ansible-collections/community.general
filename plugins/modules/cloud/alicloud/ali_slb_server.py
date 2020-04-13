#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
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
# along with Ansible. If not, see http://www.gnu.org/licenses/.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ali_slb_server
short_description: Add or remove a list of backend servers to/from a specified SLB
description:
  - Returns information about the backend servers. Will be marked changed when called only if state is changed.
options:
  state:
    description:
      - Add or remove backend server to/from a specified slb
    default: 'present'
    choices: ['present', 'absent']
    type: str
  load_balancer_id:
    description:
      - The unique ID of a Server Load Balancer instance
    required: true
    aliases: ['lb_id']
    type: str
  backend_servers:
    description:
      - List of hash/dictionary of backend servers to add or set in when C(state=present)
      - List IDs of backend servers which in the load balancer when C(state=absent)
    required: true
    aliases: ['servers']
    type: list
    elements: dict
    suboptions:
      server_id:
        description:
          - The ID of ecs instance which is added into load balancer.
          - One of I(server_id) and I(server_ids) required.
      server_ids:
        description:
          - If you have multiple servers to add and they have the same weight, type, you can use the server_ids parameter, which is a list of ids.
          - One of I(server_id) and I(server_ids) required.
      weight:
        description:
          - The weight of backend server in the load balancer.
        choices: [0~100]
        default: 100
      type:
        description:
          - The type of backend server in the load balancer.
        choices: ['ecs', 'eni']
        default: 'ecs'
requirements:
    - "python >= 3.6"
    - "footmark >= 1.19.0"
extends_documentation_fragment:
    - community.general.alicloud
author:
  - "He Guimin (@xiaozhu36)"
"""

EXAMPLES = '''
# Provisioning new add or remove Backend Server from SLB
# Basic example to add backend server to load balancer instance
- name: add backend server
  hosts: localhost
  connection: local
  vars:
    load_balancer_id: lb-abcd1234
  tasks:
    - name: add backend server
      ali_slb_server:
        load_balancer_id: '{{ load_balancer_id }}'
        backend_servers:
          - server_id: i-abcd1234
            weight: 70
          - server_id: i-abce1245

#Basic example to set backend server of load balancer instance
- name: set backend server
  hosts: localhost
  connection: local
  vars:
    alicloud_access_key: <your-alicloud-access-key-id>
    alicloud_secret_key: <your-alicloud-access-secret-key>
  tasks:
    - name: set backend server
      ali_slb_server:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        load_balancer_id: lb-abcd1234
        backend_servers:
          - server_id: i-abcd1234
            weight: 50
          - server_id: i-abcd1234
            weight: 80

#Basic example to remove backend servers from load balancer instance
- name: remove backend servers
  hosts: localhost
  connection: local
  tasks:
    - name: remove backend servers
      ali_slb_server:
        load_balancer_id: lb-abcd1234
        state: absent
        backend_servers:
          - i-abcd1234
          - i-abcd1234

'''
RETURN = '''
load_balancer_id:
    description: ID of the load balancer.
    returned: when success
    type: str
    sample: "lb-2zeyfm5a14c9ffxvxmvco"
"backend_servers":
    description: Details about the backened-servers that were added.
    returned: when success
    type: list
    sample: [
        {
            "health_status": "abnormal",
            "id": "i-2zeau2evvbnwufq0fa7q"
        },
        {
            "health_status": "abnormal",
            "id": "i-2zehasnejqr6g6agys5a"
        }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, slb_connect

try:
    from footmark.exception import SLBResponseError

    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def parse_server_ids(servers):
    parse_server = []
    if servers:
        for s in servers:
            if "server_ids" in s:
                ids = s.pop("server_ids")
                for id in ids:
                    server = {"server_id": id}
                    server.update(s)
                    parse_server.append(server)
            else:
                parse_server.append(s)
    return parse_server


def get_backen_server_weight(server):
    """
    Retrieves instance information from an instance
    ID and returns it as a dictionary
    """
    return {'id': server.id, 'weight': server.weight}


def get_backen_server_status(server):
    """
    Retrieves instance information from an instance
    ID and returns it as a dictionary
    """
    return {'id': server.id, 'health_status': server.status}


def add_set_backend_servers(module, slb, load_balancer_id, backend_servers):
    """
    Add and/or Set backend servers to an slb

    :param module: Ansible module object
    :param slb: authenticated slb connection object
    :param load_balancer_id: load balancer id to add/set backend servers to
    :param backend_servers: backend severs information to add/set
    :return: returns changed state, current added backend servers and custom message.
    """

    changed = False
    server_id_param = 'server_id'
    backend_servers_to_set = []
    backend_servers_to_add = []
    result = []
    current_backend_servers = []
    changed_after_add = False
    changed_after_set = False

    try:

        load_balancer_info = slb.describe_load_balancer_attribute(load_balancer_id=load_balancer_id)

        # Verifying if server load balancer Object is present
        if load_balancer_info:
            existing_backend_servers = str(load_balancer_info.backend_servers['backend_server'])

            # Segregating existing backend servers from new backend servers from the provided backend servers
            for backend_server in backend_servers:

                backend_server_string = backend_server[server_id_param] + '\''
                if backend_server_string in existing_backend_servers:
                    backend_servers_to_set.append(backend_server)
                else:
                    backend_servers_to_add.append(backend_server)

                    # Adding new backend servers if provided
            if len(backend_servers_to_add) > 0:
                current_backend_servers.extend(slb.add_backend_servers(load_balancer_id=load_balancer_id, backend_servers=backend_servers_to_add))
                changed = True
                # Setting exisiting backend servers if provided
            if len(backend_servers_to_set) > 0:
                backen_servers = slb.set_backend_servers(load_balancer_id=load_balancer_id, backend_servers=backend_servers_to_set)
                changed = True
                # If backend server result after set action is available then clearing actual list
                # and adding new result to it.
                if len(backen_servers) > 0:
                    # Below operation clears list using slice operation
                    current_backend_servers[:] = []
                    current_backend_servers.extend(backen_servers)

            if changed_after_add or changed_after_set:
                changed = True

        else:
            module.fail_json(msg="Could not find provided load balancer instance")

    except SLBResponseError as ex:
        module.fail_json(msg='Unable to add backend servers, error: {0}'.format(ex))

    return changed, current_backend_servers


def remove_backend_servers(module, slb, load_balancer_id, backend_servers):
    """
    Remove backend servers from an slb

    :param module: Ansible module object
    :param slb: authenticated slb connection object
    :param load_balancer_id: load balancer id to remove backend servers from
    :param backend_servers: list of backend server ids to remove from slb
    :return: returns changed state, current added backend servers and custom message.
    """

    changed = False

    try:
        backend_servers = slb.remove_backend_servers(load_balancer_id=load_balancer_id, backend_server_ids=backend_servers)
        changed = True

    except SLBResponseError as ex:
        module.fail_json(msg='Unable to remove backend servers, error: {0}'.format(ex))

    return changed, backend_servers


def describe_backend_servers_health_status(module, slb, load_balancer_id=None, listener_ports=None):
    """
    Describe health status of added backend servers of an slb

    :param module: Ansible module object
    :param slb: authenticated slb connection object
    :param load_balancer_id: load balancer id to remove backend servers from
    :param listener_ports: list of ports to for which backend server health status is required
    :return: returns backend servers health status and custom message
    """

    backend_servers_health_status = []
    try:
        if listener_ports:
            for port in listener_ports:

                backend_server = slb.describe_backend_servers_health_status(load_balancer_id=load_balancer_id, port=port)
                backend_servers_health_status.extend(backend_server)
        else:
            backend_servers_health_status = slb.describe_backend_servers_health_status(load_balancer_id=load_balancer_id)

    except SLBResponseError as ex:
        module.fail_json(msg='Unable to describe backend servers health status, error: {0}'.format(ex))

    return backend_servers_health_status


def validate_backend_server_info(module, backend_servers, default_weight):
    """
    Validate backend server information provided by user for add, set and remove action

    :param module: Ansible module object
    :param backend_servers: backend severs information to validate (list of dictionaries or string)
    :param default_weight: assigns default weight, if provided, for a backend server to set/add
    """
    VALID_PARAMS = ['server_id', 'server_ids', 'weight', 'type']

    for backend_server in backend_servers:

        if not isinstance(backend_server, dict):
            module.fail_json(msg='Invalid backend_servers parameter type [%s] for state=present.' % type(backend_server))

        for k in backend_server:
            if k not in VALID_PARAMS:
                module.fail_json(msg='Invalid backend_server parameter {}'.format(k))

        if "server_id" not in backend_server and "server_ids" not in backend_server:
            module.fail_json(msg="'server_id' or 'server_ids': required field is set")

        # verifying weight parameter for non numeral string and limit validation
        if "weight" in backend_server:
            try:
                w = int(backend_server['weight'])
                if w < 0 or w > 100:
                    module.fail_json(msg="'weight': field value is invalid. Expect to [0-100].")
            except Exception as e:
                module.fail_json(msg="'weight': field value is invalid. Expect to positive integer [0-100].")


def get_verify_listener_ports(module, listener_ports=None):
    """
    Validate and get listener ports

    :param module: Ansible module object
    :param listener_ports: list of ports to for which backend server health status is required
    :return: formatted listener ports
    """

    if listener_ports:
        if len(listener_ports) > 0:
            for port in listener_ports:

                try:
                    port = int(port)
                except Exception as ex:
                    module.fail_json(msg='Invalid port value')
        else:
            listener_ports = None

    return listener_ports


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        state=dict(choices=['present', 'absent'], default='present', type='str'),
        backend_servers=dict(required=True, type='list', elements='dict', aliases=['servers']),
        load_balancer_id=dict(required=True, aliases=['lb_id'], type='str'),
    ))

    # handling region parameter which is not required by this module
    del argument_spec['alicloud_region']

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="'footmark' is required for the module ali_slb_server. "
                             "Please install 'footmark' by using 'sudo pip install footmark'.")

    # handling region parameter which is required by common utils file to login but not required by this module
    module.params['alicloud_region'] = 'cn-hangzhou'
    slb = slb_connect(module)

    state = module.params['state']
    backend_servers = parse_server_ids(module.params['backend_servers'])
    load_balancer_id = module.params['load_balancer_id']

    if state == 'present':

        if len(backend_servers) > 0:

            validate_backend_server_info(module, backend_servers, 100)
            changed, current_backend_servers = add_set_backend_servers(module, slb, load_balancer_id, backend_servers)

            result_servers = []
            for server in current_backend_servers:
                result_servers.append(get_backen_server_weight(server))
            module.exit_json(changed=changed, backend_servers=result_servers, load_balancer_id=load_balancer_id)
        else:
            module.fail_json(msg='backend servers information is mandatory to state=present')

    if len(backend_servers) > 0:

        if not isinstance(backend_servers, list):
            module.fail_json(msg='Invalid backend_server parameter type [%s] for state=absent.' % type(backend_servers))

        changed, backend_servers = remove_backend_servers(module, slb, load_balancer_id, backend_servers)
        result_servers = []
        for server in backend_servers:
            result_servers.append(get_backen_server_weight(server))
        module.exit_json(changed=changed, backend_servers=result_servers, load_balancer_id=load_balancer_id)
    else:
        module.fail_json(msg='backend server ID(s) information is mandatory to state=absent')

    # elif state == 'list':
    #
    #     if load_balancer_id:
    #
    #         listener_ports = get_verify_listener_ports(module, listener_ports)
    #
    #         backend_servers = describe_backend_servers_health_status(module, slb, load_balancer_id=load_balancer_id,
    #                                                                  listener_ports=listener_ports)
    #
    #         result_servers = []
    #         for server in backend_servers:
    #             result_servers.append(get_backen_server_status(server))
    #         module.exit_json(changed=changed, backend_servers=result_servers, load_balancer_id=load_balancer_id)
    #     else:
    #         module.fail_json(msg='load balancer id is mandatory to perform action')


if __name__ == '__main__':
    main()

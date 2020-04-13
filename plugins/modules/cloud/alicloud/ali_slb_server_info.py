#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#  This file is part of Ansible
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
module: ali_slb_server_info
short_description: Gather facts on backend server of Alibaba Cloud SLB.
description:
     - This module fetches data from the Open API in Alicloud.
       The module must be called from within the SLB backend server itself.
options:
    load_balancer_id:
      description:
        - ID of server load balancer.
      required: true
      aliases: ["lb_id" ]
      type: str
    listener_ports:
      description:
        - A list of backend server listening ports.
      aliases: ["ports"]
      type: list
      elements: int
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - community.general.alicloud
"""

EXAMPLES = '''
# Fetch backend server health status details according to setting different filters
- name: Find all backend server health status in specified region
  ali_slb_server_info:
    load_balancer_id: '{{ load_balancer_id }}'


- name: Find all backend server health status based on specified port no.
  ali_slb_server_info:
    load_balancer_id: '{{ load_balancer_id }}'
    listener_ports: '{{ ports }}'
'''

RETURN = '''
load_balancer_id:
    description: ID of the load balancer.
    returned: when success
    type: str
    sample: "lb-dj1jywbux1zslfna6pvnv"
"backend_servers":
    description: Details about the backened-servers that were added.
    returned: when success
    type: list
    sample: [
        {
            "id": "i-2ze35dldjc05dcvezgwk",
            "listener_port": 80,
            "port": 80,
            "server_health_status": "unavailable"
        },
        {
            "id": "i-2ze35dldjc05dcvezgwk",
            "listener_port": 8080,
            "port": 8080,
            "server_health_status": "unavailable"
        },
        {
            "id": "i-2ze35dldjc05dcvezgwk",
            "listener_port": 8085,
            "port": 8085,
            "server_health_status": "unavailable"
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


def get_info(backend_server):
    """
    get info from backend server object
    :param backend_server: backend server object
    :return: info of backend server
    """
    return {
        'id': backend_server.server_id,
        'port': backend_server.port,
        'listener_port': backend_server.listener_port,
        'server_health_status': backend_server.server_health_status,
    }


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        load_balancer_id=dict(required=True, aliases=['lb_id']),
        listener_ports=dict(type='list', elements='int', aliases=['ports']),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")

    load_balancer_id = module.params['load_balancer_id']
    ports = module.params['listener_ports']
    result = []

    if ports and (not isinstance(ports, list) or len(ports)) < 1:
        module.fail_json(msg='backend_server_ports should be a list of backend server ports, aborting')

    try:
        slb = slb_connect(module)

        # check whether server load balancer exist or not
        laod_balancer = slb.describe_load_balancers(load_balancer_id=load_balancer_id)
        if laod_balancer and len(laod_balancer) == 1:
            if ports:
                # list slb servers by port no.
                for port in ports:
                    for backend_server in slb.describe_backend_servers_health_status(
                            load_balancer_id=load_balancer_id, port=port):
                        result.append(get_info(backend_server))

            else:
                # list all slb servers
                for backend_server in slb.describe_backend_servers_health_status(load_balancer_id=load_balancer_id):
                    result.append(get_info(backend_server))

            module.exit_json(changed=False, load_balancer_id=load_balancer_id, backend_servers=result)

        else:
            module.fail_json(msg="Unable to list slb backend server health status, invalid load balancer id")
    except Exception as e:
        module.fail_json(msg="Unable to list slb backend server health status, and got an error: {0}.".format(e))


if __name__ == '__main__':
    main()

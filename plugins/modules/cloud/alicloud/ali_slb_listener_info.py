#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Ansible Project
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
module: ali_slb_listener_info
short_description: Gather facts on listener of Alibaba Cloud SLB.
description:
     - This module fetches data from the Open API in Alicloud.
       The module must be called from within the SLB listeners itself.

options:
    load_balancer_id:
      description:
        - ID of server load balancer.
      required: true
      aliases: ["lb_id"]
      type: str
    listener_type:
      description:
        - User expects the type of operation listener.
      required: true
      choices: ['http', 'https', 'tcp', 'udp']
      type: str
    listener_port:
      description:
        - Port used by the Server Load Balancer instance frontend. Value(1~65535)
      required: true
      type: int
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - community.general.alicloud
"""

EXAMPLES = """
# Fetch SLB listener details according to setting different filters
- name: Fetch SLB listener details example
  ali_slb_listener_info:
    load_balancer_id: '{{ load_balancer_id }}'
    listener_type: '{{ listener_type }}'
    listener_port: '{{ listener_port }}'
"""

RETURN = '''
listener:
    description: Details about SLB listener that were created.
    returned: when success
    type: dict
    sample: {
        "backend_server_port": 8085,
        "bandwidth": 1,
        "listener_port": 8085,
        "listener_type": null,
        "persistence_timeout": null,
        "schedule": null,
        "server_certificate_id": null,
        "status": "stopped",
        "sticky_session": "off"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, slb_connect

HAS_ECS = False
HAS_FOOTMARK = False

try:
    from footmark.exception import SLBResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def get_info(obj):
    """
    get info from lb object
    :param obj: lb obj
    :return: info of lb
    """
    result = dict(listener_port=obj.listener_port,
                  backend_server_port=obj.backend_server_port,
                  bandwidth=obj.bandwidth,
                  status=obj.status,
                  schedule=obj.schedule,
                  listener_type=obj.listener_type)

    if hasattr(obj, 'server_certificate_id'):
        result['server_certificate_id'] = obj.server_certificate_id
    if hasattr(obj, 'sticky_session'):
        result['sticky_session'] = obj.sticky_session
    if hasattr(obj, 'persistence_timeout'):
        result['persistence_timeout'] = obj.persistence_timeout
    return result


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        listener_port=dict(type='int', required=True),
        load_balancer_id=dict(type='str', required=True, aliases=['lb_id']),
        listener_type=dict(type='str', required=True, choices=['http', 'https', 'tcp', 'udp'])
    ))
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")

    load_balancer_id = module.params['load_balancer_id']
    listener_port = module.params['listener_port']
    listener_type = module.params['listener_type']

    try:
        slb = slb_connect(module)

        # check whether server load balancer exist or not
        laod_balancer = slb.describe_load_balancers(load_balancer_id=load_balancer_id)
        if laod_balancer and len(laod_balancer) == 1:

            # list load balancers listeners
            listener = slb.describe_load_balancer_listener_attribute(load_balancer_id,
                                                                     listener_port,
                                                                     listener_type)
            if listener is None:
                module.fail_json(msg="Unable to describe slb listeners, no listeners found")
            else:
                module.exit_json(changed=False, listener=get_info(listener))
        else:
            module.fail_json(msg="Unable to describe slb listeners, invalid load balancer id")
    except Exception as e:
        module.fail_json(msg="Unable to describe slb listeners, and got an error: {0}.".format(e))


if __name__ == "__main__":
    main()

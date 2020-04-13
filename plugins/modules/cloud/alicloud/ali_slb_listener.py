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
module: ali_slb_listener
short_description: Create, Delete, Start or Stop Server Load Balancer Listener in ECS
description:
  - Create, Delete, Start or Stop Server Load Balancer Listener in ECS
options:
  state:
    description:
      - The state of the load balancer listener after operating.
    required: true
    choices: [ 'present', 'absent', 'running', 'stopped']
    type: str
  load_balancer_id:
    description:
      - The unique ID of an Server Load Balancer instance
    required: true
    aliases: ['id']
    type: str
  protocol:
    description:
      - The protocol which listener used. It is requried when C(state=present).
    required: false
    choices: [ 'http', 'https', 'tcp', 'udp']
    type: str
  listener_port:
    description:
      - Port used by the Server Load Balancer instance frontend, Value(1-65535).
    required: true
    type: int
    aliases: ['frontend_port']
  bandwidth:
    description:
      - Bandwidth peak of Listener. It is required when C(present), Value(-1|1-5120)。
      - If C(bandwidth=-1), For public network load balancing instances that are charged by traffic,
        you can set the peak bandwidth to -1, which means that the peak bandwidth is not limited.
    type: int
  backend_server_port:
    description:
      - Port used by the Server Load Balancer instance backend port, Value(1-65535).
    aliases: ['backend_port']
    type: int
  scheduler:
    description:
      - Scheduling algorithm.
    default: 'wrr'
    choices: ['wlc', 'wrr']
    type: str
  sticky_session:
    description:
      - Whether to enable session persistence.
    choices: ['on', 'off']
    default: 'off'
    type: str
  sticky_session_type:
    description:
      - Mode for handling the cookie. Required when C(sticky_session='on').
    choices: ['server', 'insert']
    type: str
  cookie_timeout:
    description:
      - Cookie timeout, Required when C(sticky_session='on', sticky_session_type='insert'), Value(1~86400)
    type: str
  cookie:
    description:
      - The cookie configured on the server. Required when C(sticky_session='on', sticky_session_type='server')
    type: str
  persistence_timeout:
    description:
      - Timeout of connection persistence. Value(0-3600)
    default: 0
    type: int
  health_check:
    description:
      - Whether to enable health check. TCP and UDP listener's HealthCheck is always on, so it will be ignore when launching TCP or UDP listener.
    choices: ['on', 'off']
    default: 'on'
    type: str
  health_check_type:
    description:
      - Type of health check. TCP supports TCP and HTTP health check mode, you can select the particular mode depending on your application.
    default: 'tcp'
    choices: ['tcp', 'http']
    type: str
  health_check_domain:
    description:
      - Domain name used for health check.
        When it is not set or empty, Server Load Balancer uses the private network IP address of each backend server as Domain used for health check.
    type: str
  health_check_uri:
    description:
      - URI used for health check. Required when C(health_check='on').
    default: "/"
    type: str
  health_check_connect_port:
    description:
      - Port used for health check. Required when C(health_check='on'). Default to C(backend_server_port). Value(1~65535)
    type: int
  healthy_threshold:
    description:
      - Threshold determining the result of the health check is success.
        Namely, after how many successive successful health checks,
        the health check result of the backend server is changed from fail to success. Required when C(health_check='on').
        Value(1-10)
    default: 3
    type: int
  unhealthy_threshold:
    description:
      - Threshold determining the result of the health check is fail.
        Namely, after how many successive failed health checks,
        the health check result of the backend server is changed from success to fail. Required when C(health_check='on').
        Value(1-10)
    default: 3
    type: int
  health_check_timeout:
    description:
      - Maximum timeout of each health check response. Required when C(health_check='on'). Value(1-300)
    default: 5
    type: int
  health_check_interval:
    description:
      - Time interval of health checks. Required when C(health_check='on'). Value(1-50)
    default: 2
    type: int
  health_check_http_code:
    description:
      - Regular health check HTTP status code. Multiple codes are segmented by ",". Required when C(health_check='on').
    default: http_2xx
    choices: ['http_2xx','http_3xx', 'http_4xx', 'http_5xx']
    type: str
  vserver_group_id:
    description:
      - Virtual server group ID, when the VserverGroup is on, the incoming VServerGroupId value takes effect.
    type: str
  server_certificate_id:
    description:
      - Server certificate ID
    type: str
requirements:
    - "python >= 3.6"
    - "footmark >= 1.15.0"
extends_documentation_fragment:
    - community.general.alicloud
author:
  - "He Guimin (@xiaozhu36)"
"""

EXAMPLES = """
# Basic provisioning example to create Load Balancer Listener
- name: create server load balancer listener
  ali_slb_listener:
    load_balancer_id: '{{ load_balancer_id }}'
    listener_port: '{{ listener_port }}'
    backend_server_port: '{{ backend_server_port }}'
    bandwidth: 1
    sticky_session: off
    health_check: off
    protocol: http

# Basic provisioning example to stop Load Balancer Listener
- name: stop server load balancer listener
  ali_slb_listener:
    load_balancer_id: '{{ load_balancer_id }}'
    protocol: http
    listener_port: '{{ listener_port }}'
    state: absent

# Basic provisioning example to start Load Balancer Listener
- name: start server load balancer listener
  ali_slb_listener:
    load_balancer_id: '{{ load_balancer_id }}'
    protocol: http
    listener_port: '{{ listener_port }}'


# Basic provisioning example to set listener attribute
- name: set listener attribute
  ali_slb_listener:
    protocol: http
    load_balancer_id: '{{ load_balancer_id }}'
    listener_port: '{{ listener_port }}'
    bandwidth: 4
    scheduler: wlc
    sticky_session: off
    health_check: off

# Basic provisioning example to delete listener
- name: delete listener
  ali_slb_listener:
    load_balancer_id: '{{ load_balancer_id }}'
    listener_port: '{{ listener_port }}'
    state: absent
"""
RETURN = '''
listener:
    description:
        - The info of load balancer listener
    returned: when success
    type: dict
    sample: {
        "backend_server_port": 80,
        "bandwidth": 4,
        "listener_port": 80,
        "schedule": null,
        "server_certificate_id": null,
        "status": "running",
        "sticky_session": "off",
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
    :param lb_ls_obj: lb obj
    :return: info of lb
    """
    result = dict(listener_port=obj.listener_port,
                  backend_server_port=obj.backend_server_port,
                  bandwidth=obj.bandwidth,
                  status=obj.status,
                  schedule=obj.schedule)

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
        listener_port=dict(type='int', required=True, aliases=['frontend_port']),
        state=dict(type='str', required=True, choices=['present', 'absent', 'stopped', 'running']),
        load_balancer_id=dict(type='str', required=True, aliases=['id']),
        backend_server_port=dict(type='int', aliases=['backend_port']),
        bandwidth=dict(type='int'),
        sticky_session=dict(type='str', choices=['on', 'off'], default='off'),
        protocol=dict(type='str', choices=['http', 'https', 'tcp', 'udp']),
        health_check=dict(type='str', default='on', choices=['on', 'off']),
        scheduler=dict(type='str', default='wrr', choices=['wrr', 'wlc']),
        sticky_session_type=dict(type='str', choices=['insert', 'server']),
        cookie_timeout=dict(type='str'),
        cookie=dict(type='str'),
        health_check_domain=dict(type='str'),
        health_check_uri=dict(type='str', default='/'),
        health_check_connect_port=dict(type='int'),
        healthy_threshold=dict(type='int', default=3),
        unhealthy_threshold=dict(type='int', default=3),
        health_check_timeout=dict(type='int', default=5),
        health_check_interval=dict(type='int', default=2),
        health_check_http_code=dict(type='str', default='http_2xx', choices=['http_2xx', 'http_3xx', 'http_4xx', 'http_5xx']),
        vserver_group_id=dict(type='str'),
        persistence_timeout=dict(type='int', default=0),
        server_certificate_id=dict(type='str'),
        health_check_type=dict(type='str', default='tcp', choices=['tcp', 'http']),
    ))

    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for the module ali_slb_listener.')

    slb = slb_connect(module)
    state = module.params['state']
    load_balancer_id = module.params['load_balancer_id']
    listener_port = module.params['listener_port']
    backend_server_port = module.params['backend_server_port']
    bandwidth = module.params['bandwidth']
    sticky_session = module.params['sticky_session']
    protocol = module.params['protocol']
    health_check = module.params['health_check']
    scheduler = module.params['scheduler']
    sticky_session_type = module.params['sticky_session_type']
    cookie_timeout = module.params['cookie_timeout']
    cookie = module.params['cookie']
    health_check_domain = module.params['health_check_domain']
    health_check_uri = module.params['health_check_uri']
    health_check_connect_port = module.params['health_check_connect_port']
    healthy_threshold = module.params['healthy_threshold']
    unhealthy_threshold = module.params['unhealthy_threshold']
    health_check_timeout = module.params['health_check_timeout']
    health_check_interval = module.params['health_check_interval']
    health_check_http_code = module.params['health_check_http_code']
    vserver_group_id = module.params['vserver_group_id']
    server_certificate_id = module.params['server_certificate_id']
    persistence_timeout = module.params['persistence_timeout']
    health_check_type = module.params['health_check_type']

    current_listener = slb.describe_load_balancer_listener_attribute(load_balancer_id, listener_port, protocol)
    changed = False
    if state == "present":
        if current_listener:
            changed = current_listener.set_attribute(load_balancer_id=load_balancer_id,
                                                     bandwidth=bandwidth,
                                                     sticky_session=sticky_session,
                                                     protocol=protocol,
                                                     health_check=health_check,
                                                     scheduler=scheduler,
                                                     sticky_session_type=sticky_session_type,
                                                     cookie_timeout=cookie_timeout,
                                                     cookie=cookie,
                                                     health_check_domain=health_check_domain,
                                                     health_check_uri=health_check_uri,
                                                     health_check_connect_port=health_check_connect_port,
                                                     healthy_threshold=healthy_threshold,
                                                     unhealthy_threshold=unhealthy_threshold,
                                                     health_check_timeout=health_check_timeout,
                                                     health_check_interval=health_check_interval,
                                                     health_check_http_code=health_check_http_code,
                                                     vserver_group_id=vserver_group_id,
                                                     server_certificate_id=server_certificate_id,
                                                     persistence_timeout=persistence_timeout,
                                                     health_check_type=health_check_type)
            module.exit_json(changed=changed, listener=get_info(current_listener.describe_attribute(load_balancer_id, protocol)))
        else:
            changed = slb.create_load_balancer_listener(load_balancer_id=load_balancer_id,
                                                        listener_port=listener_port,
                                                        backend_server_port=backend_server_port,
                                                        bandwidth=bandwidth,
                                                        sticky_session=sticky_session,
                                                        protocol=protocol,
                                                        health_check=health_check,
                                                        scheduler=scheduler,
                                                        sticky_session_type=sticky_session_type,
                                                        cookie_timeout=cookie_timeout,
                                                        cookie=cookie,
                                                        health_check_domain=health_check_domain,
                                                        health_check_uri=health_check_uri,
                                                        health_check_connect_port=health_check_connect_port,
                                                        healthy_threshold=healthy_threshold,
                                                        unhealthy_threshold=unhealthy_threshold,
                                                        health_check_timeout=health_check_timeout,
                                                        health_check_interval=health_check_interval,
                                                        health_check_http_code=health_check_http_code,
                                                        vserver_group_id=vserver_group_id,
                                                        server_certificate_id=server_certificate_id,
                                                        persistence_timeout=persistence_timeout)
            new_current_listener = slb.describe_load_balancer_listener_attribute(load_balancer_id, listener_port, protocol)
            module.exit_json(changed=changed, listener=get_info(new_current_listener))
    if not current_listener:
        module.fail_json(msg="The specified load balancer listener is not exist. Please check your load_balancer_id or listener_port and try again.")
    if state == "absent":
        changed = current_listener.delete(load_balancer_id)
        module.exit_json(changed=changed, listener=get_info(current_listener))
    if state == "running":
        if current_listener.status == "stopped":
            # start
            changed = current_listener.start(load_balancer_id)
        module.exit_json(changed=changed, listener=get_info(current_listener.describe_attribute(load_balancer_id, protocol)))
    if state == "stopped":
        if current_listener.status == "running":
            # stop
            changed = current_listener.stop(load_balancer_id)
        module.exit_json(changed=changed, listener=get_info(current_listener.describe_attribute(load_balancer_id, protocol)))


if __name__ == "__main__":
    main()

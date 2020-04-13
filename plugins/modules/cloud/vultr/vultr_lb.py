#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2020, Julien BORDELLIER <git@julienbordellier.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: vultr_lb
short_description: Manages Load Balanders on Vultr.
description:
  - Create and remove Load Balancers.
author: "Julien BORDELLIER (@jstoja)"
options:
  dcid:
    description:
      - DCID integer Location in which to create the load balancer.
    required: true
  name:
    description:
      - Text label that will be associated with the subscription.
    aliases: [ label ]
    required: true
  config_ssl_redirect:
    description:
      - Forces redirect from HTTP to HTTPS.
  sticky_sessions:
    description:
      - Enables stick sessions for your load balancer.
  cookie_name:
    description:
      - Name for your stick session.
  balancing_algorithm:
    description:
      - Balancing algorithm for your load balancer.
    choices: [ roundrobin, leastconn ]
  health_check:
    description:
      - Defines health checks for your attached backend nodes.
  forwarding_rules:
    description:
      - Defines forwarding rules that your load balancer will follow.
  ssl_private_key:
    description:
      - The SSL certificates private key.
  ssl_certificate:
    description:
      - The SSL Certificate.
  ssl_chain
    description:
      - The SSL certificate chain.
  state:
    description:
      - State of the Load Balancer.
    default: present
    choices: [ present, absent ]
extends_documentation_fragment:
- community.general.vultr

'''

EXAMPLES = r'''
- name: Ensure a Load Balancer exists
  local_action:
    module: vultr_lb
    dcid: 1
    algorithm: Leastconn
    label: web
    state: present
    forwarding_rules:
      - frontend_protocol: https
        frontend_port: 81
        backend_protocol: https
        backend_port: 81
'''

RETURN = r'''
---
vultr_api:
  description: Response from Vultr API with a few additions/modification
  returned: success
  type: complex
  contains:
    api_account:
      description: Account used in the ini file to select the key
      returned: success
      type: str
      sample: default
    api_timeout:
      description: Timeout used for the API requests
      returned: success
      type: int
      sample: 60
    api_retries:
      description: Amount of max retries for the API requests
      returned: success
      type: int
      sample: 5
    api_retry_max_delay:
      description: Exponential backoff delay in seconds between retries up to this max delay value.
      returned: success
      type: int
      sample: 12
    api_endpoint:
      description: Endpoint used for the API requests
      returned: success
      type: str
      sample: "https://api.vultr.com"
vultr_dns_domain:
  description: Response from Vultr API
  returned: success
  type: complex
  contains:
    SUBID:
      description: Unique identifier of a load balancer subscription.
      returned: success
      type: int
      sample: 1314217
    date_created:
      description: Date the Load Balancer was created.
      returned: success
      type: str
      sample: "2017-08-26 12:47:48"
    DCID:
      description: Location in which the Load Balancer was created.
      returned: success
      type: int
      sample: 1
    location:
      description: The physical localtion where the Load Balancer was created.
      returned: success
      type: str
      sample: "New Jersey"
    label:
      description: The name of the Load Balancer.
      returned: success
      type: str
      sample: "lb01"
    status:
      description: Status of the subscription and will be one of: pending | active | suspended | closed.
      returned: success
      type: str
      sample: "active"
    ipv4:
      description: IPv4 of the Load Balancer.
      returned: success
      type: str
      sample: "203.0.113.20"
    ipv4:
      description: IPv6 of the Load Balancer.
      returned: success
      type: str
      sample: "fd06:30bd:6374:dc29:ffff:ffff:ffff:ffff"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.vultr import (
    Vultr,
    vultr_argument_spec,
)


class AnsibleVultrLoadBalancer(Vultr):

    def __init__(self, module):
        super(AnsibleVultrLoadBalancer, self).__init__(module, "vultr_lb")

        self.returns = {
        }

    def get_lb(self):
        lb_list = self.api_query(path="/v1/loadbalancer/list")
        lb_name = self.module.params.get('name').lower()
        found_lbs = []

        if lb_list:
            found_lbs = [lb for lb in lb_list if lb['name'] is lb_name]

        if len(found_lbs) in (0, 1):
            self.module.warn("Found more than 1 or no Vultr Load Balancer matching {}".format(lb_name))
            return {}

        return found_lbs[0]

    def present_lb(self):
        lb = self.get_lb()
        if not lb:
            lb = self._create_lb(lb)
        return lb

    def _create_lb(self, lb):
        self.result['changed'] = True
        data = {
            'DCID': self.module.params.get('dcid'),
            'label': self.module.params.get('name'),
        }

        def add_param_if_exists(d, param):
            value = self.module.params.get(param)
            if value:
                d[param] = value

        optional_params = [
            'config_ssl_redirect',
            'sticky_sessions',
            'cookie_name',
            'balancing_algorithm',
            'health_check',
            'forwarding_rules',
            'ssl_private_key',
            'ssl_certificate',
            'ssl_chain'
        ]

        for param in optional_params:
            add_param_if_exists(data, param)

        # StickSessions should be either 'on' or 'off'
        if 'sticky_sessions' in data:
            ss_values = { True: 'on', False: 'off'}
            data['sticky_sessions'] = ss_values[data['sticky_sessions']]

        self.result['diff']['before'] = {}
        self.result['diff']['after'] = data

        if not self.module.check_mode:
            self.api_query(
                path="/v1/loadbalancer/create",
                method="POST",
                data=data
            )
            lb = self.get_lb()
        return lb

    def absent_lb(self):
        lb = self.get_lb()
        if lb:
            self.result['changed'] = True

        data = {
            'label': lb['name'],
        }

        self.result['diff']['before'] = lb
        self.result['diff']['after'] = {}

        if not self.module.check_mode:
            self.api_query(
                path="/v1/loadbalancer/create",
                method="POST",
                data=data
            )
        return lb


def main():
    argument_spec = vultr_argument_spec()
    argument_spec.update({
        'name': {
            'required': True,
            'aliases': ['domain'],
        },
        'dcid': {
            'required': True,
        },
        'config_ssl_redirect': {},
        'sticky_sessions': {},
        'cookie_name': {},
        'balancing_algorithm': {},
        'health_check': {},
        'forwarding_rules': {},
        'ssl_private_key': {},
        'ssl_certificate': {},
        'ssl_chain': {},
        'state': {
            'choices': ['present', 'absent'],
            'default': 'present',
        },
    })

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name', 'dcid']),
        ],
        supports_check_mode=True,
    )

    vultr_lb = AnsibleVultrLoadBalancer(module)
    if module.params.get('state') == "absent":
        lb = vultr_lb.absent_lb()
    else:
        lb = vultr_lb.present_lb()

    result = vultr_lb.get_result(lb)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

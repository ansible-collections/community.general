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
  label:
    description:
      - Text label that will be associated with the subscription.
  config_ssl_redirect:
    description:
      - Forces redirect from HTTP to HTTPS.
  sticky_sessions:
    description:
      - Enables stick sessions for your load balancer.
    choices: [ on, off ]
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
        return {}

    def present_lb(self):
        return None

    def _create_lb(self, lb):
        return None

    def absent_lb(self):
        return None


def main():
    argument_spec = vultr_argument_spec()
    argument_spec.update()

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[],
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

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: cs_network_acl_rule
short_description: Manages network access control list (ACL) rules on Apache CloudStack based clouds.
description:
    - Add, update and remove network ACL rules.
author: René Moser (@resmo)
options:
  network_acl:
    description:
      - Name of the network ACL.
    type: str
    required: true
    aliases: [ acl ]
  cidrs:
    description:
      - CIDRs of the rule.
    type: list
    default: [ 0.0.0.0/0 ]
    aliases: [ cidr ]
  rule_position:
    description:
      - The position of the network ACL rule.
    type: int
    required: true
    aliases: [ number ]
  protocol:
    description:
      - Protocol of the rule
    choices: [ tcp, udp, icmp, all, by_number ]
    type: str
    default: tcp
  protocol_number:
    description:
      - Protocol number from 1 to 256 required if I(protocol=by_number).
    type: int
  start_port:
    description:
      - Start port for this rule.
      - Considered if I(protocol=tcp) or I(protocol=udp).
    type: int
    aliases: [ port ]
  end_port:
    description:
      - End port for this rule.
      - Considered if I(protocol=tcp) or I(protocol=udp).
      - If not specified, equal I(start_port).
    type: int
  icmp_type:
    description:
      - Type of the icmp message being sent.
      - Considered if I(protocol=icmp).
    type: int
  icmp_code:
    description:
      - Error code for this icmp message.
      - Considered if I(protocol=icmp).
    type: int
  vpc:
    description:
      - VPC the network ACL is related to.
    type: str
    required: true
  traffic_type:
    description:
      - Traffic type of the rule.
    type: str
    choices: [ ingress, egress ]
    default: ingress
    aliases: [ type ]
  action_policy:
    description:
      - Action policy of the rule.
    type: str
    choices: [ allow, deny ]
    default: allow
    aliases: [ action ]
  tags:
    description:
      - List of tags. Tags are a list of dictionaries having keys I(key) and I(value).
      - "If you want to delete all tags, set a empty list e.g. I(tags: [])."
    type: list
    aliases: [ tag ]
  domain:
    description:
      - Domain the VPC is related to.
    type: str
  account:
    description:
      - Account the VPC is related to.
    type: str
  project:
    description:
      - Name of the project the VPC is related to.
    type: str
  zone:
    description:
      - Name of the zone the VPC related to.
      - If not set, default zone is used.
    type: str
  state:
    description:
      - State of the network ACL rule.
    type: str
    default: present
    choices: [ present, absent ]
  poll_async:
    description:
      - Poll async jobs until job has finished.
    type: bool
    default: yes
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: create a network ACL rule, allow port 80 ingress
  cs_network_acl_rule:
    network_acl: web
    rule_position: 1
    vpc: my vpc
    traffic_type: ingress
    action_policy: allow
    port: 80
    cidr: 0.0.0.0/0
  delegate_to: localhost

- name: create a network ACL rule, deny port range 8000-9000 ingress for 10.20.0.0/16 and 10.22.0.0/16
  cs_network_acl_rule:
    network_acl: web
    rule_position: 1
    vpc: my vpc
    traffic_type: ingress
    action_policy: deny
    start_port: 8000
    end_port: 9000
    cidrs:
    - 10.20.0.0/16
    - 10.22.0.0/16
  delegate_to: localhost

- name: remove a network ACL rule
  cs_network_acl_rule:
    network_acl: web
    rule_position: 1
    vpc: my vpc
    state: absent
  delegate_to: localhost
'''

RETURN = '''
---
network_acl:
  description: Name of the network ACL.
  returned: success
  type: str
  sample: customer acl
cidr:
  description: CIDR of the network ACL rule.
  returned: success
  type: str
  sample: 0.0.0.0/0
cidrs:
  description: CIDRs of the network ACL rule.
  returned: success
  type: list
  sample: [ 0.0.0.0/0 ]
  version_added: '2.9'
rule_position:
  description: Position of the network ACL rule.
  returned: success
  type: int
  sample: 1
action_policy:
  description: Action policy of the network ACL rule.
  returned: success
  type: str
  sample: deny
traffic_type:
  description: Traffic type of the network ACL rule.
  returned: success
  type: str
  sample: ingress
protocol:
  description: Protocol of the network ACL rule.
  returned: success
  type: str
  sample: tcp
protocol_number:
  description: Protocol number in case protocol is by number.
  returned: success
  type: int
  sample: 8
start_port:
  description: Start port of the network ACL rule.
  returned: success
  type: int
  sample: 80
end_port:
  description: End port of the network ACL rule.
  returned: success
  type: int
  sample: 80
icmp_code:
  description: ICMP code of the network ACL rule.
  returned: success
  type: int
  sample: 8
icmp_type:
  description: ICMP type of the network ACL rule.
  returned: success
  type: int
  sample: 0
state:
  description: State of the network ACL rule.
  returned: success
  type: str
  sample: Active
vpc:
  description: VPC of the network ACL.
  returned: success
  type: str
  sample: customer vpc
tags:
  description: List of resource tags associated with the network ACL rule.
  returned: success
  type: list
  sample: '[ { "key": "foo", "value": "bar" } ]'
domain:
  description: Domain the network ACL rule is related to.
  returned: success
  type: str
  sample: example domain
account:
  description: Account the network ACL rule is related to.
  returned: success
  type: str
  sample: example account
project:
  description: Name of project the network ACL rule is related to.
  returned: success
  type: str
  sample: Production
zone:
  description: Zone the VPC is related to.
  returned: success
  type: str
  sample: ch-gva-2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
    cs_required_together
)


class AnsibleCloudStackNetworkAclRule(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackNetworkAclRule, self).__init__(module)
        self.returns = {
            'cidrlist': 'cidr',
            'action': 'action_policy',
            'protocol': 'protocol',
            'icmpcode': 'icmp_code',
            'icmptype': 'icmp_type',
            'number': 'rule_position',
            'traffictype': 'traffic_type',
        }
        # these values will be casted to int
        self.returns_to_int = {
            'startport': 'start_port',
            'endport': 'end_port',
        }

    def get_network_acl_rule(self):
        args = {
            'aclid': self.get_network_acl(key='id'),
            'account': self.get_account(key='name'),
            'domainid': self.get_domain(key='id'),
            'projectid': self.get_project(key='id'),
        }
        network_acl_rules = self.query_api('listNetworkACLs', **args)
        for acl_rule in network_acl_rules.get('networkacl', []):
            if acl_rule['number'] == self.module.params.get('rule_position'):
                return acl_rule
        return None

    def present_network_acl_rule(self):
        network_acl_rule = self.get_network_acl_rule()

        protocol = self.module.params.get('protocol')
        start_port = self.module.params.get('start_port')
        end_port = self.get_or_fallback('end_port', 'start_port')
        icmp_type = self.module.params.get('icmp_type')
        icmp_code = self.module.params.get('icmp_code')

        if protocol in ['tcp', 'udp'] and (start_port is None or end_port is None):
            self.module.fail_json(msg="protocol is %s but the following are missing: start_port, end_port" % protocol)

        elif protocol == 'icmp' and (icmp_type is None or icmp_code is None):
            self.module.fail_json(msg="protocol is icmp but the following are missing: icmp_type, icmp_code")

        elif protocol == 'by_number' and self.module.params.get('protocol_number') is None:
            self.module.fail_json(msg="protocol is by_number but the following are missing: protocol_number")

        if not network_acl_rule:
            network_acl_rule = self._create_network_acl_rule(network_acl_rule)
        else:
            network_acl_rule = self._update_network_acl_rule(network_acl_rule)

        if network_acl_rule:
            network_acl_rule = self.ensure_tags(resource=network_acl_rule, resource_type='NetworkACL')
        return network_acl_rule

    def absent_network_acl_rule(self):
        network_acl_rule = self.get_network_acl_rule()
        if network_acl_rule:
            self.result['changed'] = True
            args = {
                'id': network_acl_rule['id'],
            }
            if not self.module.check_mode:
                res = self.query_api('deleteNetworkACL', **args)

                poll_async = self.module.params.get('poll_async')
                if poll_async:
                    self.poll_job(res, 'networkacl')

        return network_acl_rule

    def _create_network_acl_rule(self, network_acl_rule):
        self.result['changed'] = True
        protocol = self.module.params.get('protocol')
        args = {
            'aclid': self.get_network_acl(key='id'),
            'action': self.module.params.get('action_policy'),
            'protocol': protocol if protocol != 'by_number' else self.module.params.get('protocol_number'),
            'startport': self.module.params.get('start_port'),
            'endport': self.get_or_fallback('end_port', 'start_port'),
            'number': self.module.params.get('rule_position'),
            'icmpcode': self.module.params.get('icmp_code'),
            'icmptype': self.module.params.get('icmp_type'),
            'traffictype': self.module.params.get('traffic_type'),
            'cidrlist': self.module.params.get('cidrs'),
        }
        if not self.module.check_mode:
            res = self.query_api('createNetworkACL', **args)

            poll_async = self.module.params.get('poll_async')
            if poll_async:
                network_acl_rule = self.poll_job(res, 'networkacl')

        return network_acl_rule

    def _update_network_acl_rule(self, network_acl_rule):
        protocol = self.module.params.get('protocol')
        args = {
            'id': network_acl_rule['id'],
            'action': self.module.params.get('action_policy'),
            'protocol': protocol if protocol != 'by_number' else str(self.module.params.get('protocol_number')),
            'startport': self.module.params.get('start_port'),
            'endport': self.get_or_fallback('end_port', 'start_port'),
            'icmpcode': self.module.params.get('icmp_code'),
            'icmptype': self.module.params.get('icmp_type'),
            'traffictype': self.module.params.get('traffic_type'),
            'cidrlist': ",".join(self.module.params.get('cidrs')),
        }
        if self.has_changed(args, network_acl_rule):
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('updateNetworkACLItem', **args)

                poll_async = self.module.params.get('poll_async')
                if poll_async:
                    network_acl_rule = self.poll_job(res, 'networkacl')

        return network_acl_rule

    def get_result(self, network_acl_rule):
        super(AnsibleCloudStackNetworkAclRule, self).get_result(network_acl_rule)
        if network_acl_rule:
            if 'cidrlist' in network_acl_rule:
                self.result['cidrs'] = network_acl_rule['cidrlist'].split(',') or [network_acl_rule['cidrlist']]
            if network_acl_rule['protocol'] not in ['tcp', 'udp', 'icmp', 'all']:
                self.result['protocol_number'] = int(network_acl_rule['protocol'])
                self.result['protocol'] = 'by_number'
            self.result['action_policy'] = self.result['action_policy'].lower()
            self.result['traffic_type'] = self.result['traffic_type'].lower()
        return self.result


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        network_acl=dict(required=True, aliases=['acl']),
        rule_position=dict(required=True, type='int', aliases=['number']),
        vpc=dict(required=True),
        cidrs=dict(type='list', default=['0.0.0.0/0'], aliases=['cidr']),
        protocol=dict(choices=['tcp', 'udp', 'icmp', 'all', 'by_number'], default='tcp'),
        protocol_number=dict(type='int'),
        traffic_type=dict(choices=['ingress', 'egress'], aliases=['type'], default='ingress'),
        action_policy=dict(choices=['allow', 'deny'], aliases=['action'], default='allow'),
        icmp_type=dict(type='int'),
        icmp_code=dict(type='int'),
        start_port=dict(type='int', aliases=['port']),
        end_port=dict(type='int'),
        state=dict(choices=['present', 'absent'], default='present'),
        zone=dict(),
        domain=dict(),
        account=dict(),
        project=dict(),
        tags=dict(type='list', aliases=['tag']),
        poll_async=dict(type='bool', default=True),
    ))

    required_together = cs_required_together()
    required_together.extend([
        ['icmp_type', 'icmp_code'],
    ])

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=cs_required_together(),
        mutually_exclusive=(
            ['icmp_type', 'start_port'],
            ['icmp_type', 'end_port'],
        ),
        supports_check_mode=True
    )

    acs_network_acl_rule = AnsibleCloudStackNetworkAclRule(module)

    state = module.params.get('state')
    if state == 'absent':
        network_acl_rule = acs_network_acl_rule.absent_network_acl_rule()
    else:
        network_acl_rule = acs_network_acl_rule.present_network_acl_rule()

    result = acs_network_acl_rule.get_result(network_acl_rule)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

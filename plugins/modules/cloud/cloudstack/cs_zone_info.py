#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_zone_info
short_description: Gathering information about zones from Apache CloudStack based clouds.
description:
  - Gathering information from the API of a zone.
author: René Moser (@resmo)
options:
  zone:
    description:
      - Name of the zone.
      - If not specified, all zones are returned
    type: str
    aliases: [ name ]
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: Gather information from a zone
  cs_zone_info:
    zone: ch-gva-1
  register: zone
  delegate_to: localhost

- name: Show the returned results of the registered variable
  debug:
    msg: "{{ zone }}"

- name: Gather information from all zones
  cs_zone_info:
  register: zones
  delegate_to: localhost

- name: Show information on all zones
  debug:
    msg: "{{ zones }}"
'''

RETURN = '''
---
zones:
  description: A list of matching zones.
  type: list
  returned: success
  contains:
    id:
      description: UUID of the zone.
      returned: success
      type: str
      sample: 04589590-ac63-4ffc-93f5-b698b8ac38b6
    name:
      description: Name of the zone.
      returned: success
      type: str
      sample: zone01
    dns1:
      description: First DNS for the zone.
      returned: success
      type: str
      sample: 8.8.8.8
    dns2:
      description: Second DNS for the zone.
      returned: success
      type: str
      sample: 8.8.4.4
    internal_dns1:
      description: First internal DNS for the zone.
      returned: success
      type: str
      sample: 8.8.8.8
    internal_dns2:
      description: Second internal DNS for the zone.
      returned: success
      type: str
      sample: 8.8.4.4
    dns1_ipv6:
      description: First IPv6 DNS for the zone.
      returned: success
      type: str
      sample: "2001:4860:4860::8888"
    dns2_ipv6:
      description: Second IPv6 DNS for the zone.
      returned: success
      type: str
      sample: "2001:4860:4860::8844"
    allocation_state:
      description: State of the zone.
      returned: success
      type: str
      sample: Enabled
    domain:
      description: Domain the zone is related to.
      returned: success
      type: str
      sample: ROOT
    network_domain:
      description: Network domain for the zone.
      returned: success
      type: str
      sample: example.com
    network_type:
      description: Network type for the zone.
      returned: success
      type: str
      sample: basic
    local_storage_enabled:
      description: Local storage offering enabled.
      returned: success
      type: bool
      sample: false
    securitygroups_enabled:
      description: Security groups support is enabled.
      returned: success
      type: bool
      sample: false
    guest_cidr_address:
      description: Guest CIDR address for the zone
      returned: success
      type: str
      sample: 10.1.1.0/24
    dhcp_provider:
      description: DHCP provider for the zone
      returned: success
      type: str
      sample: VirtualRouter
    zone_token:
      description: Zone token
      returned: success
      type: str
      sample: ccb0a60c-79c8-3230-ab8b-8bdbe8c45bb7
    tags:
      description: List of resource tags associated with the zone.
      returned: success
      type: dict
      sample: [ { "key": "foo", "value": "bar" } ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
)


class AnsibleCloudStackZoneInfo(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackZoneInfo, self).__init__(module)
        self.returns = {
            'dns1': 'dns1',
            'dns2': 'dns2',
            'internaldns1': 'internal_dns1',
            'internaldns2': 'internal_dns2',
            'ipv6dns1': 'dns1_ipv6',
            'ipv6dns2': 'dns2_ipv6',
            'domain': 'network_domain',
            'networktype': 'network_type',
            'securitygroupsenabled': 'securitygroups_enabled',
            'localstorageenabled': 'local_storage_enabled',
            'guestcidraddress': 'guest_cidr_address',
            'dhcpprovider': 'dhcp_provider',
            'allocationstate': 'allocation_state',
            'zonetoken': 'zone_token',
        }

    def get_zone(self):
        if self.module.params['zone']:
            zones = [super(AnsibleCloudStackZoneInfo, self).get_zone()]
        else:
            zones = self.query_api('listZones')
            if zones:
                zones = zones['zone']
            else:
                zones = []
        return {
            'zones': [self.update_result(resource) for resource in zones]
        }


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        zone=dict(type='str', aliases=['name']),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    acs_zone_info = AnsibleCloudStackZoneInfo(module=module)
    result = acs_zone_info.get_zone()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

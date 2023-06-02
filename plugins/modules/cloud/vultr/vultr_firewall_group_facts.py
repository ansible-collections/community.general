#!/usr/bin/python
#
# (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['deprecated'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: vultr_firewall_group_facts
deprecated:
  removed_in: '2.13'
  why: Deprecated in favour of C(_info) module.
  alternative: Use M(vultr_firewall_group_info) instead.
short_description: Gather facts about the Vultr firewall groups available.
description:
  - Gather facts about firewall groups available in Vultr.
author: "Yanis Guenane (@Spredzy)"
extends_documentation_fragment:
- community.general.vultr

'''

EXAMPLES = r'''
- name: Gather Vultr firewall groups facts
  local_action:
    module: vultr_firewall_group_facts

- name: Print the gathered facts
  debug:
    var: ansible_facts.vultr_firewall_group_facts
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
      version_added: '2.9'
    api_endpoint:
      description: Endpoint used for the API requests
      returned: success
      type: str
      sample: "https://api.vultr.com"
vultr_firewall_group_facts:
  description: Response from Vultr API
  returned: success
  type: complex
  sample:
    "vultr_firewall_group_facts": [
      {
        "date_created": "2018-07-12 10:27:14",
        "date_modified": "2018-07-12 10:27:14",
        "description": "test",
        "id": "5e128ff0",
        "instance_count": 0,
        "max_rule_count": 50,
        "rule_count": 0
      }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.vultr import (
    Vultr,
    vultr_argument_spec,
)


class AnsibleVultrFirewallGroupFacts(Vultr):

    def __init__(self, module):
        super(AnsibleVultrFirewallGroupFacts, self).__init__(module, "vultr_firewall_group_facts")

        self.returns = {
            "FIREWALLGROUPID": dict(key='id'),
            "date_created": dict(),
            "date_modified": dict(),
            "description": dict(),
            "instance_count": dict(convert_to='int'),
            "max_rule_count": dict(convert_to='int'),
            "rule_count": dict(convert_to='int')
        }

    def get_firewall_group(self):
        return self.api_query(path="/v1/firewall/group_list")


def parse_fw_group_list(fwgroups_list):
    if not fwgroups_list:
        return []

    return [group for id, group in fwgroups_list.items()]


def main():
    argument_spec = vultr_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    fw_group_facts = AnsibleVultrFirewallGroupFacts(module)
    result = fw_group_facts.get_result(parse_fw_group_list(fw_group_facts.get_firewall_group()))
    ansible_facts = {
        'vultr_firewall_group_facts': result['vultr_firewall_group_facts']
    }
    module.exit_json(ansible_facts=ansible_facts, **result)


if __name__ == '__main__':
    main()

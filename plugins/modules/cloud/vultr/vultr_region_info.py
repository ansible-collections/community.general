#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: vultr_region_info
short_description: Gather information about the Vultr regions available.
description:
  - Gather information about regions available to boot servers.
author: "Yanis Guenane (@Spredzy)"
extends_documentation_fragment:
- community.general.vultr

'''

EXAMPLES = r'''
- name: Gather Vultr regions information
  local_action:
    module: vultr_region_info
  register: result

- name: Print the gathered information
  debug:
    var: result.vultr_region_info
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
vultr_region_info:
  description: Response from Vultr API
  returned: success
  type: complex
  sample:
    "vultr_region_info": [
      {
        "block_storage": false,
        "continent": "Europe",
        "country": "GB",
        "ddos_protection": true,
        "id": 8,
        "name": "London",
        "regioncode": "LHR",
        "state": ""
      }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.vultr import (
    Vultr,
    vultr_argument_spec,
)


class AnsibleVultrRegionInfo(Vultr):

    def __init__(self, module):
        super(AnsibleVultrRegionInfo, self).__init__(module, "vultr_region_info")

        self.returns = {
            "DCID": dict(key='id', convert_to='int'),
            "block_storage": dict(convert_to='bool'),
            "continent": dict(),
            "country": dict(),
            "ddos_protection": dict(convert_to='bool'),
            "name": dict(),
            "regioncode": dict(),
            "state": dict()
        }

    def get_regions(self):
        return self.api_query(path="/v1/regions/list")


def parse_regions_list(regions_list):
    return [region for id, region in regions_list.items()]


def main():
    argument_spec = vultr_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    region_info = AnsibleVultrRegionInfo(module)
    result = region_info.get_result(parse_regions_list(region_info.get_regions()))
    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: scaleway_ip_facts
deprecated:
  removed_in: 3.0.0  # was Ansible 2.13
  why: Deprecated in favour of C(_info) module.
  alternative: Use M(community.general.scaleway_ip_info) instead.
short_description: Gather facts about the Scaleway ips available.
description:
  - Gather facts about the Scaleway ips available.
author:
  - "Yanis Guenane (@Spredzy)"
  - "Remy Leone (@sieben)"
extends_documentation_fragment:
- community.general.scaleway

options:
  region:
    type: str
    description:
     - Scaleway region to use (for example par1).
    required: true
    choices:
      - ams1
      - EMEA-NL-EVS
      - par1
      - EMEA-FR-PAR1
      - par2
      - EMEA-FR-PAR2
      - waw1
      - EMEA-PL-WAW1
'''

EXAMPLES = r'''
- name: Gather Scaleway ips facts
  community.general.scaleway_ip_facts:
    region: par1
'''

RETURN = r'''
---
scaleway_ip_facts:
  description: Response from Scaleway API
  returned: success
  type: complex
  sample:
    "scaleway_ip_facts": [
        {
            "address": "163.172.170.243",
            "id": "ea081794-a581-8899-8451-386ddaf0a451",
            "organization": "3f709602-5e6c-4619-b80c-e324324324af",
            "reverse": null,
            "server": {
                "id": "12f19bc7-109c-4517-954c-e6b3d0311363",
                "name": "scw-e0d158"
            }
        }
    ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.scaleway import (
    Scaleway,
    ScalewayException,
    scaleway_argument_spec,
    SCALEWAY_LOCATION,
)


class ScalewayIpFacts(Scaleway):

    def __init__(self, module):
        super(ScalewayIpFacts, self).__init__(module)
        self.name = 'ips'

        region = module.params["region"]
        self.module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint"]


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        module.exit_json(
            ansible_facts={'scaleway_ip_facts': ScalewayIpFacts(module).get_resources()}
        )
    except ScalewayException as exc:
        module.fail_json(msg=exc.message)


if __name__ == '__main__':
    main()

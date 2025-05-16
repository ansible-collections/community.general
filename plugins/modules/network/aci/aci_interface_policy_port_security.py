#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = r'''
---
module: aci_interface_policy_port_security
short_description: Manage port security (l2:PortSecurityPol)
description:
- Manage port security on Cisco ACI fabrics.
options:
  port_security:
    description:
    - The name of the port security.
    type: str
    required: yes
    aliases: [ name ]
  description:
    description:
    - The description for the contract.
    type: str
    aliases: [ descr ]
  max_end_points:
    description:
    - Maximum number of end points.
    - Accepted values range between C(0) and C(12000).
    - The APIC defaults to C(0) when unset during creation.
    type: int
  port_security_timeout:
    description:
    - The delay time in seconds before MAC learning is re-enabled
    - Accepted values range between C(60) and C(3600)
    - The APIC defaults to C(60) when unset during creation
    type: int
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
  name_alias:
    description:
    - The alias for the current object. This relates to the nameAlias field in ACI.
    type: str
extends_documentation_fragment:
- cisco.aci.aci

seealso:
- name: APIC Management Information Model reference
  description: More information about the internal APIC class B(l2:PortSecurityPol).
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Dag Wieers (@dagwieers)
'''

# FIXME: Add more, better examples
EXAMPLES = r'''
- aci_interface_policy_port_security:
    host: '{{ inventory_hostname }}'
    username: '{{ username }}'
    password: '{{ password }}'
    port_security: '{{ port_security }}'
    description: '{{ descr }}'
    max_end_points: '{{ max_end_points }}'
    port_security_timeout: '{{ port_security_timeout }}'
  delegate_to: localhost
'''

RETURN = r'''
current:
  description: The existing configuration from the APIC after the module has finished
  returned: success
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production environment",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
error:
  description: The error information as returned from the APIC
  returned: failure
  type: dict
  sample:
    {
        "code": "122",
        "text": "unknown managed object class foo"
    }
raw:
  description: The raw output returned by the APIC REST API (xml or json)
  returned: parse error
  type: str
  sample: '<?xml version="1.0" encoding="UTF-8"?><imdata totalCount="1"><error code="122" text="unknown managed object class foo"/></imdata>'
sent:
  description: The actual/minimal configuration pushed to the APIC
  returned: info
  type: list
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment"
            }
        }
    }
previous:
  description: The original configuration from the APIC before the module has started
  returned: info
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
proposed:
  description: The assembled configuration from the user-provided parameters
  returned: info
  type: dict
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment",
                "name": "production"
            }
        }
    }
filter_string:
  description: The filter string used for the request
  returned: failure or debug
  type: str
  sample: ?rsp-prop-include=config-only
method:
  description: The HTTP method used for the request to the APIC
  returned: failure or debug
  type: str
  sample: POST
response:
  description: The HTTP response from the APIC
  returned: failure or debug
  type: str
  sample: OK (30 bytes)
status:
  description: The HTTP status from the APIC
  returned: failure or debug
  type: int
  sample: 200
url:
  description: The HTTP url used for the request to the APIC
  returned: failure or debug
  type: str
  sample: https://10.11.12.13/api/mo/uni/tn-production.json
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.aci.plugins.module_utils.network.aci.aci import ACIModule, aci_argument_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        port_security=dict(type='str', aliases=['name']),  # Not required for querying all objects
        description=dict(type='str', aliases=['descr']),
        max_end_points=dict(type='int'),
        port_security_timeout=dict(type='int'),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
        name_alias=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['port_security']],
            ['state', 'present', ['port_security']],
        ],
    )

    port_security = module.params.get('port_security')
    description = module.params.get('description')
    max_end_points = module.params.get('max_end_points')
    port_security_timeout = module.params.get('port_security_timeout')
    name_alias = module.params.get('name_alias')
    if max_end_points is not None and max_end_points not in range(12001):
        module.fail_json(msg='The "max_end_points" must be between 0 and 12000')
    if port_security_timeout is not None and port_security_timeout not in range(60, 3601):
        module.fail_json(msg='The "port_security_timeout" must be between 60 and 3600')
    state = module.params.get('state')

    aci = ACIModule(module)
    aci.construct_url(
        root_class=dict(
            aci_class='l2PortSecurityPol',
            aci_rn='infra/portsecurityP-{0}'.format(port_security),
            module_object=port_security,
            target_filter={'name': port_security},
        ),
    )

    aci.get_existing()

    if state == 'present':
        aci.payload(
            aci_class='l2PortSecurityPol',
            class_config=dict(
                name=port_security,
                descr=description,
                maximum=max_end_points,
                nameAlias=name_alias,
            ),
        )

        aci.get_diff(aci_class='l2PortSecurityPol')

        aci.post_config()

    elif state == 'absent':
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()

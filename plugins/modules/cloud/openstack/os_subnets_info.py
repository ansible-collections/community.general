#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_subnets_info
short_description: Retrieve information about one or more OpenStack subnets.
author: "Davide Agnello (@dagnello)"
description:
    - Retrieve information about one or more subnets from OpenStack.
    - This module was called C(os_subnets_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(os_subnets_info) module no longer returns C(ansible_facts)!
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
   name:
     description:
        - Name or ID of the subnet.
        - Alias 'subnet' added in version 2.8.
     required: false
     aliases: ['subnet']
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
     required: false
   availability_zone:
     description:
       - Ignored. Present for backwards compatibility
     required: false
extends_documentation_fragment:
- openstack.cloud.openstack

'''

EXAMPLES = '''
- name: Gather information about previously created subnets
  os_subnets_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
  register: result

- name: Show openstack subnets
  debug:
    msg: "{{ result.openstack_subnets }}"

- name: Gather information about a previously created subnet by name
  os_subnets_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    name: subnet1
  register: result

- name: Show openstack subnets
  debug:
    msg: "{{ result.openstack_subnets }}"

- name: Gather information about a previously created subnet with filter
  # Note: name and filters parameters are not mutually exclusive
  os_subnets_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    filters:
      tenant_id: 55e2ce24b2a245b09f181bf025724cbe
  register: result

- name: Show openstack subnets
  debug:
    msg: "{{ result.openstack_subnets }}"
'''

RETURN = '''
openstack_subnets:
    description: has all the openstack information about the subnets
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the subnet.
            returned: success
            type: str
        network_id:
            description: Network ID this subnet belongs in.
            returned: success
            type: str
        cidr:
            description: Subnet's CIDR.
            returned: success
            type: str
        gateway_ip:
            description: Subnet's gateway ip.
            returned: success
            type: str
        enable_dhcp:
            description: DHCP enable flag for this subnet.
            returned: success
            type: bool
        ip_version:
            description: IP version for this subnet.
            returned: success
            type: int
        tenant_id:
            description: Tenant id associated with this subnet.
            returned: success
            type: str
        dns_nameservers:
            description: DNS name servers for this subnet.
            returned: success
            type: list
            elements: str
        allocation_pools:
            description: Allocation pools associated with this subnet.
            returned: success
            type: list
            elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        name=dict(required=False, default=None, aliases=['subnet']),
        filters=dict(required=False, type='dict', default=None)
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name == 'os_subnets_facts'
    if is_old_facts:
        module.deprecate("The 'os_subnets_facts' module has been renamed to 'os_subnets_info', "
                         "and the renamed one no longer returns ansible_facts", version='2.13')

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        subnets = cloud.search_subnets(module.params['name'],
                                       module.params['filters'])
        if is_old_facts:
            module.exit_json(changed=False, ansible_facts=dict(
                openstack_subnets=subnets))
        else:
            module.exit_json(changed=False, openstack_subnets=subnets)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()

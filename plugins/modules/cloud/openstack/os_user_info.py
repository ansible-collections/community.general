#!/usr/bin/python
# Copyright (c) 2016 Hewlett-Packard Enterprise Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_user_info
short_description: Retrieve information about one or more OpenStack users
extends_documentation_fragment:
- openstack.cloud.openstack

author: "Ricardo Carrillo Cruz (@rcarrillocruz)"
description:
    - Retrieve information about a one or more OpenStack users
    - This module was called C(os_user_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(os_user_info) module no longer returns C(ansible_facts)!
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
   name:
     description:
        - Name or ID of the user
     required: true
   domain:
     description:
        - Name or ID of the domain containing the user if the cloud supports domains
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
   availability_zone:
     description:
       - Ignored. Present for backwards compatibility
'''

EXAMPLES = '''
# Gather information about previously created users
- os_user_info:
    cloud: awesomecloud
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user by name
- os_user_info:
    cloud: awesomecloud
    name: demouser
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user in a specific domain
- os_user_info:
    cloud: awesomecloud
    name: demouser
    domain: admindomain
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user in a specific domain with filter
- os_user_info:
    cloud: awesomecloud
    name: demouser
    domain: admindomain
    filters:
      enabled: False
  register: result
- debug:
    msg: "{{ result.openstack_users }}"
'''


RETURN = '''
openstack_users:
    description: has all the OpenStack information about users
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the user.
            returned: success
            type: str
        enabled:
            description: Flag to indicate if the user is enabled
            returned: success
            type: bool
        domain_id:
            description: Domain ID containing the user
            returned: success
            type: str
        default_project_id:
            description: Default project ID of the user
            returned: success
            type: str
        email:
            description: Email of the user
            returned: success
            type: str
        username:
            description: Username of the user
            returned: success
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        name=dict(required=False, default=None),
        domain=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None),
    )

    module = AnsibleModule(argument_spec)
    is_old_facts = module._name == 'os_user_facts'
    if is_old_facts:
        module.deprecate("The 'os_user_facts' module has been renamed to 'os_user_info', "
                         "and the renamed one no longer returns ansible_facts", version='2.13')

    sdk, opcloud = openstack_cloud_from_module(module)
    try:
        name = module.params['name']
        domain = module.params['domain']
        filters = module.params['filters']

        if domain:
            try:
                # We assume admin is passing domain id
                dom = opcloud.get_domain(domain)['id']
                domain = dom
            except Exception:
                # If we fail, maybe admin is passing a domain name.
                # Note that domains have unique names, just like id.
                dom = opcloud.search_domains(filters={'name': domain})
                if dom:
                    domain = dom[0]['id']
                else:
                    module.fail_json(msg='Domain name or ID does not exist')

            if not filters:
                filters = {}

            filters['domain_id'] = domain

        users = opcloud.search_users(name, filters)
        if is_old_facts:
            module.exit_json(changed=False, ansible_facts=dict(
                openstack_users=users))
        else:
            module.exit_json(changed=False, openstack_users=users)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()

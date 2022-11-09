#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
# Copyright (c) 2017, Yaacov Zamir <yzamir@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: manageiq_policies

short_description: Management of resource policy_profiles in ManageIQ
extends_documentation_fragment:
- community.general.manageiq

author: Daniel Korn (@dkorn)
description:
  - The manageiq_policies module supports adding and deleting policy_profiles in ManageIQ.

options:
  state:
    type: str
    description:
      - C(absent) - policy_profiles should not exist,
      - C(present) - policy_profiles should exist,
      - C(list) - list current policy_profiles and policies.
    choices: ['absent', 'present', 'list']
    default: 'present'
  policy_profiles:
    type: list
    elements: dict
    description:
      - List of dictionaries, each includes the policy_profile C(name) key.
      - Required if I(state) is C(present) or C(absent).
  resource_type:
    type: str
    description:
      - The type of the resource to which the profile should be [un]assigned.
    required: true
    choices: ['provider', 'host', 'vm', 'blueprint', 'category', 'cluster',
        'data store', 'group', 'resource pool', 'service', 'service template',
        'template', 'tenant', 'user']
  resource_name:
    type: str
    description:
      - The name of the resource to which the profile should be [un]assigned.
      - Must be specified if I(resource_id) is not set. Both options are mutually exclusive.
  resource_id:
    type: int
    description:
      - The ID of the resource to which the profile should be [un]assigned.
      - Must be specified if I(resource_name) is not set. Both options are mutually exclusive.
    version_added: 2.2.0
'''

EXAMPLES = '''
- name: Assign new policy_profile for a provider in ManageIQ
  community.general.manageiq_policies:
    resource_name: 'EngLab'
    resource_type: 'provider'
    policy_profiles:
      - name: openscap profile
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false

- name: Unassign a policy_profile for a provider in ManageIQ
  community.general.manageiq_policies:
    state: absent
    resource_name: 'EngLab'
    resource_type: 'provider'
    policy_profiles:
      - name: openscap profile
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false

- name: List current policy_profile and policies for a provider in ManageIQ
  community.general.manageiq_policies:
    state: list
    resource_name: 'EngLab'
    resource_type: 'provider'
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false
'''

RETURN = '''
manageiq_policies:
    description:
      - List current policy_profile and policies for a provider in ManageIQ
    returned: always
    type: dict
    sample: '{
        "changed": false,
        "profiles": [
            {
                "policies": [
                    {
                        "active": true,
                        "description": "OpenSCAP",
                        "name": "openscap policy"
                    },
                    {
                        "active": true,
                        "description": "Analyse incoming container images",
                        "name": "analyse incoming container images"
                    },
                    {
                        "active": true,
                        "description": "Schedule compliance after smart state analysis",
                        "name": "schedule compliance after smart state analysis"
                    }
                ],
                "profile_description": "OpenSCAP profile",
                "profile_name": "openscap profile"
            }
        ]
    }'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.manageiq import ManageIQ, manageiq_argument_spec, manageiq_entities


def main():
    actions = {'present': 'assign', 'absent': 'unassign', 'list': 'list'}
    argument_spec = dict(
        policy_profiles=dict(type='list', elements='dict'),
        resource_id=dict(type='int'),
        resource_name=dict(type='str'),
        resource_type=dict(required=True, type='str',
                           choices=list(manageiq_entities().keys())),
        state=dict(required=False, type='str',
                   choices=['present', 'absent', 'list'], default='present'),
    )
    # add the manageiq connection arguments to the arguments
    argument_spec.update(manageiq_argument_spec())

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["resource_id", "resource_name"]],
        required_one_of=[["resource_id", "resource_name"]],
        required_if=[
            ('state', 'present', ['policy_profiles']),
            ('state', 'absent', ['policy_profiles'])
        ],
    )

    policy_profiles = module.params['policy_profiles']
    resource_id = module.params['resource_id']
    resource_type_key = module.params['resource_type']
    resource_name = module.params['resource_name']
    state = module.params['state']

    # get the action and resource type
    action = actions[state]
    resource_type = manageiq_entities()[resource_type_key]

    manageiq = ManageIQ(module)
    manageiq_policies = manageiq.policies(resource_id, resource_type, resource_name)

    if action == 'list':
        # return a list of current profiles for this object
        current_profiles = manageiq_policies.query_resource_profiles()
        res_args = dict(changed=False, profiles=current_profiles)
    else:
        # assign or unassign the profiles
        res_args = manageiq_policies.assign_or_unassign_profiles(policy_profiles, action)

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
# Copyright (c) 2017, Yaacov Zamir <yzamir@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: manageiq_policies_info
version_added: 5.8.0

short_description: Listing of resource policy_profiles in ManageIQ
extends_documentation_fragment:
  - community.general.manageiq
  - community.general.attributes
  - community.general.attributes.info_module

author: Alexei Znamensky (@russoz)
description:
  - The manageiq_policies module supports listing policy_profiles in ManageIQ.
options:
  resource_type:
    type: str
    description:
      - The type of the resource to obtain the profile for.
    required: true
    choices:
      - provider
      - host
      - vm
      - blueprint
      - category
      - cluster
      - data store
      - group
      - resource pool
      - service
      - service template
      - template
      - tenant
      - user
  resource_name:
    type: str
    description:
      - The name of the resource to obtain the profile for.
      - Must be specified if O(resource_id) is not set. Both options are mutually exclusive.
  resource_id:
    type: int
    description:
      - The ID of the resource to obtain the profile for.
      - Must be specified if O(resource_name) is not set. Both options are mutually exclusive.
"""

EXAMPLES = r"""
- name: List current policy_profile and policies for a provider in ManageIQ
  community.general.manageiq_policies_info:
    resource_name: 'EngLab'
    resource_type: 'provider'
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
  register: result
"""

RETURN = r"""
profiles:
  description:
    - List current policy_profile and policies for a provider in ManageIQ.
  returned: always
  type: list
  elements: dict
  sample:
    - policies:
        - active: true
          description: OpenSCAP
          name: openscap policy
        - active: true,
          description: Analyse incoming container images
          name: analyse incoming container images
        - active: true
          description: Schedule compliance after smart state analysis
          name: schedule compliance after smart state analysis
      profile_description: OpenSCAP profile
      profile_name: openscap profile
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.manageiq import ManageIQ, manageiq_argument_spec, manageiq_entities


def main():
    argument_spec = dict(
        resource_id=dict(type='int'),
        resource_name=dict(type='str'),
        resource_type=dict(required=True, type='str',
                           choices=list(manageiq_entities().keys())),
    )
    # add the manageiq connection arguments to the arguments
    argument_spec.update(manageiq_argument_spec())

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["resource_id", "resource_name"]],
        required_one_of=[["resource_id", "resource_name"]],
        supports_check_mode=True,
    )

    resource_id = module.params['resource_id']
    resource_type_key = module.params['resource_type']
    resource_name = module.params['resource_name']

    # get the resource type
    resource_type = manageiq_entities()[resource_type_key]

    manageiq_policies = ManageIQ(module).policies(resource_id, resource_type, resource_name)

    # return a list of current profiles for this object
    current_profiles = manageiq_policies.query_resource_profiles()
    res_args = dict(changed=False, profiles=current_profiles)

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()

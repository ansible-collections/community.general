#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
# Copyright (c) 2017, Yaacov Zamir <yzamir@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: manageiq_tags

short_description: Management of resource tags in ManageIQ
extends_documentation_fragment:
- community.general.manageiq

author: Daniel Korn (@dkorn)
description:
  - The manageiq_tags module supports adding, updating and deleting tags in ManageIQ.

options:
  state:
    type: str
    description:
      - C(absent) - tags should not exist.
      - C(present) - tags should exist.
      - C(list) - list current tags.
    choices: ['absent', 'present', 'list']
    default: 'present'
  tags:
    type: list
    elements: dict
    description:
      - C(tags) - list of dictionaries, each includes C(name) and c(category) keys.
      - Required if I(state) is C(present) or C(absent).
  resource_type:
    type: str
    description:
      - The relevant resource type in manageiq.
    required: true
    choices: ['provider', 'host', 'vm', 'blueprint', 'category', 'cluster',
        'data store', 'group', 'resource pool', 'service', 'service template',
        'template', 'tenant', 'user']
  resource_name:
    type: str
    description:
      - The name of the resource at which tags will be controlled.
      - Must be specified if I(resource_id) is not set. Both options are mutually exclusive.
  resource_id:
    description:
      - The ID of the resource at which tags will be controlled.
      - Must be specified if I(resource_name) is not set. Both options are mutually exclusive.
    type: int
    version_added: 2.2.0
'''

EXAMPLES = '''
- name: Create new tags for a provider in ManageIQ.
  community.general.manageiq_tags:
    resource_name: 'EngLab'
    resource_type: 'provider'
    tags:
    - category: environment
      name: prod
    - category: owner
      name: prod_ops
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false

- name: Create new tags for a provider in ManageIQ.
  community.general.manageiq_tags:
    resource_id: 23000000790497
    resource_type: 'provider'
    tags:
    - category: environment
      name: prod
    - category: owner
      name: prod_ops
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false

- name: Remove tags for a provider in ManageIQ.
  community.general.manageiq_tags:
    state: absent
    resource_name: 'EngLab'
    resource_type: 'provider'
    tags:
    - category: environment
      name: prod
    - category: owner
      name: prod_ops
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
      validate_certs: false

- name: List current tags for a provider in ManageIQ.
  community.general.manageiq_tags:
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.manageiq import (
    ManageIQ, ManageIQTags, manageiq_argument_spec, manageiq_entities
)


def main():
    actions = {'present': 'assign', 'absent': 'unassign', 'list': 'list'}
    argument_spec = dict(
        tags=dict(type='list', elements='dict'),
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
            ('state', 'present', ['tags']),
            ('state', 'absent', ['tags'])
        ],
    )

    tags = module.params['tags']
    resource_id = module.params['resource_id']
    resource_type_key = module.params['resource_type']
    resource_name = module.params['resource_name']
    state = module.params['state']

    # get the action and resource type
    action = actions[state]
    resource_type = manageiq_entities()[resource_type_key]

    manageiq = ManageIQ(module)

    # query resource id, fail if resource does not exist
    if resource_id is None:
        resource_id = manageiq.query_resource_id(resource_type, resource_name)

    manageiq_tags = ManageIQTags(manageiq, resource_type, resource_id)

    if action == 'list':
        # return a list of current tags for this object
        current_tags = manageiq_tags.query_resource_tags()
        res_args = dict(changed=False, tags=current_tags)
    else:
        # assign or unassign the tags
        res_args = manageiq_tags.assign_or_unassign_tags(tags, action)

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()

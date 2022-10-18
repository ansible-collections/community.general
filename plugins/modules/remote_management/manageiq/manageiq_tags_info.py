#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
# Copyright (c) 2017, Yaacov Zamir <yzamir@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: manageiq_tags_info
version_added: 5.8.0
short_description: Retrieve resource tags in ManageIQ
extends_documentation_fragment:
- community.general.manageiq

author: Alexei Znamensky (@russoz)
description:
  - This module supports retrieving resource tags from ManageIQ.

options:
  resource_type:
    type: str
    description:
      - The relevant resource type in ManageIQ.
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
'''

EXAMPLES = '''
- name: List current tags for a provider in ManageIQ.
  community.general.manageiq_tags_info:
    resource_name: 'EngLab'
    resource_type: 'provider'
    manageiq_connection:
      url: 'http://127.0.0.1:3000'
      username: 'admin'
      password: 'smartvm'
  register: result
'''

RETURN = '''
tags:
  description: List of tags associated with the resource.
  returned: on success
  type: list
  elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.manageiq import (
    ManageIQ, ManageIQTags, manageiq_argument_spec, manageiq_entities
)


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

    # get the action and resource type
    resource_type = manageiq_entities()[resource_type_key]

    manageiq = ManageIQ(module)

    # query resource id, fail if resource does not exist
    if resource_id is None:
        resource_id = manageiq.query_resource_id(resource_type, resource_name)

    manageiq_tags = ManageIQTags(manageiq, resource_type, resource_id)

    # return a list of current tags for this object
    current_tags = manageiq_tags.query_resource_tags()
    res_args = dict(changed=False, tags=current_tags)

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()

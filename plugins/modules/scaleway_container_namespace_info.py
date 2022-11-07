#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless container namespace info module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_container_namespace_info
short_description: Retrieve information on Scaleway Container namespace
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module return information about a container namespace on Scaleway account.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
  - community.general.attributes.info_module

options:
  project_id:
    type: str
    description:
      - Project identifier.
    required: true

  region:
    type: str
    description:
      - Scaleway region to use (for example C(fr-par)).
    required: true
    choices:
      - fr-par
      - nl-ams
      - pl-waw

  name:
    type: str
    description:
      - Name of the container namespace.
    required: true
'''

EXAMPLES = '''
- name: Get a container namespace info
  community.general.scaleway_container_namespace_info:
    project_id: '{{ scw_project }}'
    region: fr-par
    name: my-awesome-container-namespace
  register: container_namespace_info_task
'''

RETURN = '''
container_namespace:
  description: The container namespace information.
  returned: always
  type: dict
  sample:
    description: ""
    environment_variables:
      MY_VAR: my_value
    error_message: null
    id: 531a1fd7-98d2-4a74-ad77-d398324304b8
    name: my-awesome-container-namespace
    organization_id: e04e3bdc-015c-4514-afde-9389e9be24b0
    project_id: d44cea58-dcb7-4c95-bff1-1105acb60a98
    region: fr-par
    registry_endpoint: ""
    registry_namespace_id: ""
    secret_environment_variables:
      - key: MY_SECRET_VAR
        value: $argon2id$v=19$m=65536,t=1,p=2$tb6UwSPWx/rH5Vyxt9Ujfw$5ZlvaIjWwNDPxD9Rdght3NarJz4IETKjpvAU3mMSmFg
    status: pending
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_ENDPOINT, SCALEWAY_REGIONS, scaleway_argument_spec, Scaleway
)
from ansible.module_utils.basic import AnsibleModule


def info_strategy(api, wished_cn):
    cn_list = api.fetch_all_resources("namespaces")
    cn_lookup = dict((fn["name"], fn)
                     for fn in cn_list)

    if wished_cn["name"] not in cn_lookup:
        msg = "Error during container namespace lookup: Unable to find container namespace named '%s' in project '%s'" % (wished_cn["name"],
                                                                                                                          wished_cn["project_id"])

        api.module.fail_json(msg=msg)

    target_cn = cn_lookup[wished_cn["name"]]

    response = api.get(path=api.api_path + "/%s" % target_cn["id"])
    if not response.ok:
        msg = "Error during container namespace lookup: %s: '%s' (%s)" % (response.info['msg'],
                                                                          response.json['message'],
                                                                          response.json)
        api.module.fail_json(msg=msg)

    return response.json


def core(module):
    region = module.params["region"]
    wished_container_namespace = {
        "project_id": module.params["project_id"],
        "name": module.params["name"]
    }

    api = Scaleway(module=module)
    api.api_path = "containers/v1beta1/regions/%s/namespaces" % region

    summary = info_strategy(api=api, wished_cn=wished_container_namespace)

    module.exit_json(changed=False, container_namespace=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        project_id=dict(type='str', required=True),
        region=dict(type='str', required=True, choices=SCALEWAY_REGIONS),
        name=dict(type='str', required=True)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()

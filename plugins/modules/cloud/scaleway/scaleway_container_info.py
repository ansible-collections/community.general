#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless container info module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_container_info
short_description: Scaleway Container info module
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module return info on container on Scaleway account
    U(https://developer.scaleway.com)
extends_documentation_fragment:
  - community.general.scaleway


options:
  namespace_id:
    type: str
    description:
      - Container namespace identifier.
    required: true

  region:
    type: str
    description:
      - Scaleway region to use (for example fr-par).
    required: true
    choices:
      - fr-par
      - nl-ams
      - pl-waw

  name:
    type: str
    description:
      - Name of the container.
    required: true
'''

EXAMPLES = '''
- name: Get a container info
  community.general.scaleway_container_info:
    namespace_id: '{{ scw_container_namespace }}'
    region: fr-par
    name: my-awesome-container
  register: container_info_task
'''

RETURN = '''
data:
    description: This is always present
    returned: always
    type: dict
    sample: {
      "container": {
        "cpu_limit": 140,
        "description": "Container used for testing scaleway_container ansible module",
        "domain_name": "cnansibletestgfogtjod-cn-ansible-test.functions.fnc.fr-par.scw.cloud",
        "environment_variables": {
            "MY_VAR": "my_value"
        },
        "error_message": null,
        "http_option": "",
        "id": "c9070eb0-d7a4-48dd-9af3-4fb139890721",
        "max_concurrency": 50,
        "max_scale": 5,
        "memory_limit": 256,
        "min_scale": 0,
        "name": "cn-ansible-test",
        "namespace_id": "75e299f1-d1e5-4e6b-bc6e-4fb51cfe1e69",
        "port": 80,
        "privacy": "public",
        "protocol": "http1",
        "region": "fr-par",
        "registry_image": "rg.fr-par.scw.cloud/namespace-ansible-ci/nginx:latest",
        "secret_environment_variables": "SENSITIVE_VALUE",
        "status": "created",
        "timeout": "300s"
      }
    }
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_ENDPOINT, SCALEWAY_REGIONS, scaleway_argument_spec, Scaleway,
    filter_sensitive_attributes
)
from ansible.module_utils.basic import AnsibleModule

SENSITIVE_ATTRIBUTES = (
    "secret_environment_variables"
)


def info_strategy(api, wished_cn):
    response = api.get(path=api.api_path)
    if not response.ok:
        api.module.fail_json(msg='Error getting container [{0}: {1}]'.format(
            response.status_code, response.json['message']))

    cn_list = response.json["containers"]
    cn_lookup = dict((fn["name"], fn)
                     for fn in cn_list)

    if wished_cn["name"] not in cn_lookup.keys():
        msg = "Error during container lookup: Unable to find container named '%s' in namespace '%s'" % (wished_cn["name"],
                                                                                                        wished_cn["namespace_id"])

        api.module.fail_json(msg=msg)

    target_cn = cn_lookup[wished_cn["name"]]

    response = api.get(path=api.api_path + "/%s" % target_cn["id"])
    if not response.ok:
        msg = "Error during container lookup: %s: '%s' (%s)" % (response.info['msg'],
                                                                response.json['message'],
                                                                response.json)
        api.module.fail_json(msg=msg)

    return response.json


def core(module):
    region = module.params["region"]
    wished_container = {
        "namespace_id": module.params["namespace_id"],
        "name": module.params["name"]
    }

    api = Scaleway(module=module)
    api.api_path = "containers/v1beta1/regions/%s/containers" % region

    summary = info_strategy(api=api, wished_cn=wished_container)

    module.exit_json(changed=False, container=filter_sensitive_attributes(summary, SENSITIVE_ATTRIBUTES))


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        namespace_id=dict(type='str', required=True),
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

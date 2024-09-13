#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless function info module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_function_info
short_description: Retrieve information on Scaleway Function
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module return information about a function on Scaleway account.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
  - community.general.attributes.info_module

options:
  namespace_id:
    type: str
    description:
      - Container namespace identifier.
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
      - Name of the function.
    required: true
'''

EXAMPLES = '''
- name: Get a function info
  community.general.scaleway_function_info:
    namespace_id: '{{ scw_function_namespace }}'
    region: fr-par
    name: my-awesome-function
  register: function_info_task
'''

RETURN = '''
function:
  description: The function information.
  returned: always
  type: dict
  sample:
    cpu_limit: 140
    description: Function used for testing scaleway_function ansible module
    domain_name: fnansibletestfxamabuc-fn-ansible-test.functions.fnc.fr-par.scw.cloud
    environment_variables:
      MY_VAR: my_value
    error_message: null
    handler: handler.handle
    http_option: ""
    id: ceb64dc4-4464-4196-8e20-ecef705475d3
    max_scale: 5
    memory_limit: 256
    min_scale: 0
    name: fn-ansible-test
    namespace_id: 82737d8d-0ebb-4d89-b0ad-625876eca50d
    privacy: public
    region: fr-par
    runtime: python310
    runtime_message: ""
    secret_environment_variables:
      - key: MY_SECRET_VAR
        value: $argon2id$v=19$m=65536,t=1,p=2$tb6UwSPWx/rH5Vyxt9Ujfw$5ZlvaIjWwNDPxD9Rdght3NarJz4IETKjpvAU3mMSmFg
    status: created
    timeout: 300s
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_REGIONS, scaleway_argument_spec, Scaleway
)
from ansible.module_utils.basic import AnsibleModule


def info_strategy(api, wished_fn):
    fn_list = api.fetch_all_resources("functions")
    fn_lookup = {fn["name"]: fn for fn in fn_list}

    if wished_fn["name"] not in fn_lookup:
        msg = "Error during function lookup: Unable to find function named '%s' in namespace '%s'" % (wished_fn["name"],
                                                                                                      wished_fn["namespace_id"])

        api.module.fail_json(msg=msg)

    target_fn = fn_lookup[wished_fn["name"]]

    response = api.get(path=api.api_path + "/%s" % target_fn["id"])
    if not response.ok:
        msg = "Error during function lookup: %s: '%s' (%s)" % (response.info['msg'],
                                                               response.json['message'],
                                                               response.json)
        api.module.fail_json(msg=msg)

    return response.json


def core(module):
    region = module.params["region"]
    wished_function = {
        "namespace_id": module.params["namespace_id"],
        "name": module.params["name"]
    }

    api = Scaleway(module=module)
    api.api_path = "functions/v1beta1/regions/%s/functions" % region

    summary = info_strategy(api=api, wished_fn=wished_function)

    module.exit_json(changed=False, function=summary)


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

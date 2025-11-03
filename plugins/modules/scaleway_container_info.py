#!/usr/bin/python
#
# Scaleway Serverless container info module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: scaleway_container_info
short_description: Retrieve information on Scaleway Container
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module return information about a container on Scaleway account.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
  - community.general.scaleway.actiongroup_scaleway
  - community.general.attributes.info_module

attributes:
  action_group:
    version_added: 11.3.0

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
      - Name of the container.
    required: true
"""

EXAMPLES = r"""
- name: Get a container info
  community.general.scaleway_container_info:
    namespace_id: '{{ scw_container_namespace }}'
    region: fr-par
    name: my-awesome-container
  register: container_info_task
"""

RETURN = r"""
container:
  description: The container information.
  returned: always
  type: dict
  sample:
    cpu_limit: 140
    description: Container used for testing scaleway_container ansible module
    domain_name: cnansibletestgfogtjod-cn-ansible-test.functions.fnc.fr-par.scw.cloud
    environment_variables:
      MY_VAR: my_value
    error_message: null
    http_option: ""
    id: c9070eb0-d7a4-48dd-9af3-4fb139890721
    max_concurrency: 50
    max_scale: 5
    memory_limit: 256
    min_scale: 0
    name: cn-ansible-test
    namespace_id: 75e299f1-d1e5-4e6b-bc6e-4fb51cfe1e69
    port: 80
    privacy: public
    protocol: http1
    region: fr-par
    registry_image: rg.fr-par.scw.cloud/namespace-ansible-ci/nginx:latest
    secret_environment_variables:
      - key: MY_SECRET_VAR
        value: $argon2id$v=19$m=65536,t=1,p=2$tb6UwSPWx/rH5Vyxt9Ujfw$5ZlvaIjWwNDPxD9Rdght3NarJz4IETKjpvAU3mMSmFg
    status: created
    timeout: 300s
"""

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_REGIONS,
    scaleway_argument_spec,
    Scaleway,
)
from ansible.module_utils.basic import AnsibleModule


def info_strategy(api, wished_cn):
    cn_list = api.fetch_all_resources("containers")
    cn_lookup = {cn["name"]: cn for cn in cn_list}

    if wished_cn["name"] not in cn_lookup:
        msg = f"Error during container lookup: Unable to find container named '{wished_cn['name']}' in namespace '{wished_cn['namespace_id']}'"

        api.module.fail_json(msg=msg)

    target_cn = cn_lookup[wished_cn["name"]]

    response = api.get(path=f"{api.api_path}/{target_cn['id']}")
    if not response.ok:
        msg = f"Error during container lookup: {response.info['msg']}: '{response.json['message']}' ({response.json})"
        api.module.fail_json(msg=msg)

    return response.json


def core(module):
    region = module.params["region"]
    wished_container = {"namespace_id": module.params["namespace_id"], "name": module.params["name"]}

    api = Scaleway(module=module)
    api.api_path = f"containers/v1beta1/regions/{region}/containers"

    summary = info_strategy(api=api, wished_cn=wished_container)

    module.exit_json(changed=False, container=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(
        dict(
            namespace_id=dict(type="str", required=True),
            region=dict(type="str", required=True, choices=SCALEWAY_REGIONS),
            name=dict(type="str", required=True),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == "__main__":
    main()

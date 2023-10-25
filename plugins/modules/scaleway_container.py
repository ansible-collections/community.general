#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless container management module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_container
short_description: Scaleway Container management
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module manages container on Scaleway account.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.scaleway_waitable_resource
  - community.general.attributes
requirements:
  - passlib[argon2] >= 1.7.4

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  state:
    type: str
    description:
      - Indicate desired state of the container.
    default: present
    choices:
      - present
      - absent

  namespace_id:
    type: str
    description:
      - Container namespace identifier.
    required: true

  region:
    type: str
    description:
      - Scaleway region to use (for example V(fr-par)).
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

  description:
    description:
      - Description of the container namespace.
    type: str
    default: ''

  min_scale:
    description:
      - Minimum number of replicas for the container.
    type: int

  max_scale:
    description:
      - Maximum number of replicas for the container.
    type: int

  environment_variables:
    description:
      - Environment variables of the container namespace.
      - Injected in container at runtime.
    type: dict
    default: {}

  secret_environment_variables:
    description:
      - Secret environment variables of the container namespace.
      - Updating those values will not output a C(changed) state in Ansible.
      - Injected in container at runtime.
    type: dict
    default: {}

  memory_limit:
    description:
      - Resources define performance characteristics of your container.
      - They are allocated to your container at runtime.
    type: int

  container_timeout:
    description:
      - The length of time your handler can spend processing a request before being stopped.
    type: str

  privacy:
    description:
      - Privacy policies define whether a container can be executed anonymously.
      - Choose V(public) to enable anonymous execution, or V(private) to protect your container with an authentication mechanism provided by the Scaleway API.
    type: str
    default: public
    choices:
      - public
      - private

  registry_image:
    description:
      - The name of image used for the container.
    type: str
    required: true

  max_concurrency:
    description:
      - Maximum number of connections per container.
      - This parameter will be used to trigger autoscaling.
    type: int

  protocol:
    description:
      - Communication protocol of the container.
    type: str
    default: http1
    choices:
      - http1
      - h2c

  port:
    description:
      - Listen port used to expose the container.
    type: int

  redeploy:
    description:
      - Redeploy the container if update is required.
    type: bool
    default: false
'''

EXAMPLES = '''
- name: Create a container
  community.general.scaleway_container:
    namespace_id: '{{ scw_container_namespace }}'
    state: present
    region: fr-par
    name: my-awesome-container
    registry_image: rg.fr-par.scw.cloud/funcscwtestrgy2f9zw/nginx:latest
    environment_variables:
      MY_VAR: my_value
    secret_environment_variables:
      MY_SECRET_VAR: my_secret_value
  register: container_creation_task

- name: Make sure container is deleted
  community.general.scaleway_container:
    namespace_id: '{{ scw_container_namespace }}'
    state: absent
    region: fr-par
    name: my-awesome-container
'''

RETURN = '''
container:
  description: The container information.
  returned: when O(state=present)
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
'''

from copy import deepcopy

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_REGIONS, scaleway_argument_spec, Scaleway,
    scaleway_waitable_resource_argument_spec, resource_attributes_should_be_changed,
    SecretVariables
)
from ansible.module_utils.basic import AnsibleModule

STABLE_STATES = (
    "ready",
    "created",
    "absent"
)

MUTABLE_ATTRIBUTES = (
    "description",
    "min_scale",
    "max_scale",
    "environment_variables",
    "memory_limit",
    "timeout",
    "privacy",
    "registry_image",
    "max_concurrency",
    "protocol",
    "port",
    "secret_environment_variables"
)


def payload_from_wished_cn(wished_cn):
    payload = {
        "namespace_id": wished_cn["namespace_id"],
        "name": wished_cn["name"],
        "description": wished_cn["description"],
        "min_scale": wished_cn["min_scale"],
        "max_scale": wished_cn["max_scale"],
        "environment_variables": wished_cn["environment_variables"],
        "secret_environment_variables": SecretVariables.dict_to_list(wished_cn["secret_environment_variables"]),
        "memory_limit": wished_cn["memory_limit"],
        "timeout": wished_cn["timeout"],
        "privacy": wished_cn["privacy"],
        "registry_image": wished_cn["registry_image"],
        "max_concurrency": wished_cn["max_concurrency"],
        "protocol": wished_cn["protocol"],
        "port": wished_cn["port"],
        "redeploy": wished_cn["redeploy"]
    }

    return payload


def absent_strategy(api, wished_cn):
    changed = False

    cn_list = api.fetch_all_resources("containers")
    cn_lookup = dict((cn["name"], cn)
                     for cn in cn_list)

    if wished_cn["name"] not in cn_lookup:
        return changed, {}

    target_cn = cn_lookup[wished_cn["name"]]
    changed = True
    if api.module.check_mode:
        return changed, {"status": "Container would be destroyed"}

    api.wait_to_complete_state_transition(resource=target_cn, stable_states=STABLE_STATES, force_wait=True)
    response = api.delete(path=api.api_path + "/%s" % target_cn["id"])
    if not response.ok:
        api.module.fail_json(msg='Error deleting container [{0}: {1}]'.format(
            response.status_code, response.json))

    api.wait_to_complete_state_transition(resource=target_cn, stable_states=STABLE_STATES)
    return changed, response.json


def present_strategy(api, wished_cn):
    changed = False

    cn_list = api.fetch_all_resources("containers")
    cn_lookup = dict((cn["name"], cn)
                     for cn in cn_list)

    payload_cn = payload_from_wished_cn(wished_cn)

    if wished_cn["name"] not in cn_lookup:
        changed = True
        if api.module.check_mode:
            return changed, {"status": "A container would be created."}

        # Creation doesn't support `redeploy` parameter
        del payload_cn["redeploy"]

        # Create container
        api.warn(payload_cn)
        creation_response = api.post(path=api.api_path,
                                     data=payload_cn)

        if not creation_response.ok:
            msg = "Error during container creation: %s: '%s' (%s)" % (creation_response.info['msg'],
                                                                      creation_response.json['message'],
                                                                      creation_response.json)
            api.module.fail_json(msg=msg)

        api.wait_to_complete_state_transition(resource=creation_response.json, stable_states=STABLE_STATES)
        response = api.get(path=api.api_path + "/%s" % creation_response.json["id"])
        return changed, response.json

    target_cn = cn_lookup[wished_cn["name"]]
    decoded_target_cn = deepcopy(target_cn)
    decoded_target_cn["secret_environment_variables"] = SecretVariables.decode(decoded_target_cn["secret_environment_variables"],
                                                                               payload_cn["secret_environment_variables"])
    patch_payload = resource_attributes_should_be_changed(target=decoded_target_cn,
                                                          wished=payload_cn,
                                                          verifiable_mutable_attributes=MUTABLE_ATTRIBUTES,
                                                          mutable_attributes=MUTABLE_ATTRIBUTES)

    if not patch_payload:
        return changed, target_cn

    changed = True
    if api.module.check_mode:
        return changed, {"status": "Container attributes would be changed."}

    cn_patch_response = api.patch(path=api.api_path + "/%s" % target_cn["id"],
                                  data=patch_payload)

    if not cn_patch_response.ok:
        api.module.fail_json(msg='Error during container attributes update: [{0}: {1}]'.format(
            cn_patch_response.status_code, cn_patch_response.json['message']))

    api.wait_to_complete_state_transition(resource=target_cn, stable_states=STABLE_STATES)
    response = api.get(path=api.api_path + "/%s" % target_cn["id"])
    return changed, response.json


state_strategy = {
    "present": present_strategy,
    "absent": absent_strategy
}


def core(module):
    SecretVariables.ensure_scaleway_secret_package(module)

    region = module.params["region"]
    wished_container = {
        "state": module.params["state"],
        "namespace_id": module.params["namespace_id"],
        "name": module.params["name"],
        "description": module.params['description'],
        "min_scale": module.params["min_scale"],
        "max_scale": module.params["max_scale"],
        "environment_variables": module.params['environment_variables'],
        "secret_environment_variables": module.params['secret_environment_variables'],
        "memory_limit": module.params["memory_limit"],
        "timeout": module.params["container_timeout"],
        "privacy": module.params["privacy"],
        "registry_image": module.params["registry_image"],
        "max_concurrency": module.params["max_concurrency"],
        "protocol": module.params["protocol"],
        "port": module.params["port"],
        "redeploy": module.params["redeploy"]
    }

    api = Scaleway(module=module)
    api.api_path = "containers/v1beta1/regions/%s/containers" % region

    changed, summary = state_strategy[wished_container["state"]](api=api, wished_cn=wished_container)

    module.exit_json(changed=changed, container=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(scaleway_waitable_resource_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default='present', choices=['absent', 'present']),
        namespace_id=dict(type='str', required=True),
        region=dict(type='str', required=True, choices=SCALEWAY_REGIONS),
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        min_scale=dict(type='int'),
        max_scale=dict(type='int'),
        memory_limit=dict(type='int'),
        container_timeout=dict(type='str'),
        privacy=dict(type='str', default='public', choices=['public', 'private']),
        registry_image=dict(type='str', required=True),
        max_concurrency=dict(type='int'),
        protocol=dict(type='str', default='http1', choices=['http1', 'h2c']),
        port=dict(type='int'),
        redeploy=dict(type='bool', default=False),
        environment_variables=dict(type='dict', default={}),
        secret_environment_variables=dict(type='dict', default={}, no_log=True)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless function management module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: scaleway_function
short_description: Scaleway Function management
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module manages function on Scaleway account.
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
      - Indicate desired state of the function.
    default: present
    choices:
      - present
      - absent

  namespace_id:
    type: str
    description:
      - Function namespace identifier.
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
      - Name of the function.
    required: true

  description:
    description:
      - Description of the function.
    type: str
    default: ''

  min_scale:
    description:
      - Minimum number of replicas for the function.
    type: int

  max_scale:
    description:
      - Maximum number of replicas for the function.
    type: int

  environment_variables:
    description:
      - Environment variables of the function.
      - Injected in function at runtime.
    type: dict
    default: {}

  secret_environment_variables:
    description:
      - Secret environment variables of the function.
      - Updating those values does not output a C(changed) state in Ansible.
      - Injected in function at runtime.
    type: dict
    default: {}

  runtime:
    description:
      - Runtime of the function.
      - See U(https://www.scaleway.com/en/docs/compute/functions/reference-content/functions-lifecycle/) for all available
        runtimes.
    type: str
    required: true

  memory_limit:
    description:
      - Resources define performance characteristics of your function.
      - They are allocated to your function at runtime.
    type: int

  function_timeout:
    description:
      - The length of time your handler can spend processing a request before being stopped.
    type: str

  handler:
    description:
      - The C(module-name.export) value in your function.
    type: str

  privacy:
    description:
      - Privacy policies define whether a function can be executed anonymously.
      - Choose V(public) to enable anonymous execution, or V(private) to protect your function with an authentication mechanism
        provided by the Scaleway API.
    type: str
    default: public
    choices:
      - public
      - private

  redeploy:
    description:
      - Redeploy the function if update is required.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Create a function
  community.general.scaleway_function:
    namespace_id: '{{ scw_function_namespace }}'
    region: fr-par
    state: present
    name: my-awesome-function
    runtime: python3
    environment_variables:
      MY_VAR: my_value
    secret_environment_variables:
      MY_SECRET_VAR: my_secret_value
  register: function_creation_task

- name: Make sure function is deleted
  community.general.scaleway_function:
    namespace_id: '{{ scw_function_namespace }}'
    region: fr-par
    state: absent
    name: my-awesome-function
"""

RETURN = r"""
function:
  description: The function information.
  returned: when O(state=present)
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
"""

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

VERIFIABLE_MUTABLE_ATTRIBUTES = (
    "description",
    "min_scale",
    "max_scale",
    "environment_variables",
    "runtime",
    "memory_limit",
    "timeout",
    "handler",
    "privacy",
    "secret_environment_variables"
)

MUTABLE_ATTRIBUTES = VERIFIABLE_MUTABLE_ATTRIBUTES + (
    "redeploy",
)


def payload_from_wished_fn(wished_fn):
    payload = {
        "namespace_id": wished_fn["namespace_id"],
        "name": wished_fn["name"],
        "description": wished_fn["description"],
        "min_scale": wished_fn["min_scale"],
        "max_scale": wished_fn["max_scale"],
        "runtime": wished_fn["runtime"],
        "memory_limit": wished_fn["memory_limit"],
        "timeout": wished_fn["timeout"],
        "handler": wished_fn["handler"],
        "privacy": wished_fn["privacy"],
        "redeploy": wished_fn["redeploy"],
        "environment_variables": wished_fn["environment_variables"],
        "secret_environment_variables": SecretVariables.dict_to_list(wished_fn["secret_environment_variables"])
    }

    return payload


def absent_strategy(api, wished_fn):
    changed = False

    fn_list = api.fetch_all_resources("functions")
    fn_lookup = {fn["name"]: fn for fn in fn_list}

    if wished_fn["name"] not in fn_lookup:
        return changed, {}

    target_fn = fn_lookup[wished_fn["name"]]
    changed = True
    if api.module.check_mode:
        return changed, {"status": "Function would be destroyed"}

    api.wait_to_complete_state_transition(resource=target_fn, stable_states=STABLE_STATES, force_wait=True)
    response = api.delete(path=api.api_path + "/%s" % target_fn["id"])
    if not response.ok:
        api.module.fail_json(msg='Error deleting function [{0}: {1}]'.format(
            response.status_code, response.json))

    api.wait_to_complete_state_transition(resource=target_fn, stable_states=STABLE_STATES)
    return changed, response.json


def present_strategy(api, wished_fn):
    changed = False

    fn_list = api.fetch_all_resources("functions")
    fn_lookup = {fn["name"]: fn for fn in fn_list}

    payload_fn = payload_from_wished_fn(wished_fn)

    if wished_fn["name"] not in fn_lookup:
        changed = True
        if api.module.check_mode:
            return changed, {"status": "A function would be created."}

        # Creation doesn't support `redeploy` parameter
        del payload_fn["redeploy"]

        # Create function
        api.warn(payload_fn)
        creation_response = api.post(path=api.api_path,
                                     data=payload_fn)

        if not creation_response.ok:
            msg = "Error during function creation: %s: '%s' (%s)" % (creation_response.info['msg'],
                                                                     creation_response.json['message'],
                                                                     creation_response.json)
            api.module.fail_json(msg=msg)

        api.wait_to_complete_state_transition(resource=creation_response.json, stable_states=STABLE_STATES)
        response = api.get(path=api.api_path + "/%s" % creation_response.json["id"])
        return changed, response.json

    target_fn = fn_lookup[wished_fn["name"]]
    decoded_target_fn = deepcopy(target_fn)
    decoded_target_fn["secret_environment_variables"] = SecretVariables.decode(decoded_target_fn["secret_environment_variables"],
                                                                               payload_fn["secret_environment_variables"])

    patch_payload = resource_attributes_should_be_changed(target=decoded_target_fn,
                                                          wished=payload_fn,
                                                          verifiable_mutable_attributes=VERIFIABLE_MUTABLE_ATTRIBUTES,
                                                          mutable_attributes=MUTABLE_ATTRIBUTES)

    if not patch_payload:
        return changed, target_fn

    changed = True
    if api.module.check_mode:
        return changed, {"status": "Function attributes would be changed."}

    fn_patch_response = api.patch(path=api.api_path + "/%s" % target_fn["id"],
                                  data=patch_payload)

    if not fn_patch_response.ok:
        api.module.fail_json(msg='Error during function attributes update: [{0}: {1}]'.format(
            fn_patch_response.status_code, fn_patch_response.json['message']))

    api.wait_to_complete_state_transition(resource=target_fn, stable_states=STABLE_STATES)
    response = api.get(path=api.api_path + "/%s" % target_fn["id"])
    return changed, response.json


state_strategy = {
    "present": present_strategy,
    "absent": absent_strategy
}


def core(module):
    SecretVariables.ensure_scaleway_secret_package(module)

    region = module.params["region"]
    wished_function = {
        "state": module.params["state"],
        "namespace_id": module.params["namespace_id"],
        "name": module.params["name"],
        "description": module.params['description'],
        "min_scale": module.params['min_scale'],
        "max_scale": module.params['max_scale'],
        "runtime": module.params["runtime"],
        "memory_limit": module.params["memory_limit"],
        "timeout": module.params["function_timeout"],
        "handler": module.params["handler"],
        "privacy": module.params["privacy"],
        "redeploy": module.params["redeploy"],
        "environment_variables": module.params['environment_variables'],
        "secret_environment_variables": module.params['secret_environment_variables']
    }

    api = Scaleway(module=module)
    api.api_path = "functions/v1beta1/regions/%s/functions" % region

    changed, summary = state_strategy[wished_function["state"]](api=api, wished_fn=wished_function)

    module.exit_json(changed=changed, function=summary)


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
        runtime=dict(type='str', required=True),
        memory_limit=dict(type='int'),
        function_timeout=dict(type='str'),
        handler=dict(type='str'),
        privacy=dict(type='str', default='public', choices=['public', 'private']),
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

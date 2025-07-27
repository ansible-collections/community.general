#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Serverless function namespace management module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: scaleway_function_namespace
short_description: Scaleway Function namespace management
version_added: 6.0.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module manages function namespaces on Scaleway account.
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
      - Indicate desired state of the function namespace.
    default: present
    choices:
      - present
      - absent

  project_id:
    type: str
    description:
      - Project identifier.
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
      - Name of the function namespace.
    required: true

  description:
    description:
      - Description of the function namespace.
    type: str
    default: ''

  environment_variables:
    description:
      - Environment variables of the function namespace.
      - Injected in functions at runtime.
    type: dict
    default: {}

  secret_environment_variables:
    description:
      - Secret environment variables of the function namespace.
      - Updating those values does not output a C(changed) state in Ansible.
      - Injected in functions at runtime.
    type: dict
    default: {}
"""

EXAMPLES = r"""
- name: Create a function namespace
  community.general.scaleway_function_namespace:
    project_id: '{{ scw_project }}'
    state: present
    region: fr-par
    name: my-awesome-function-namespace
    environment_variables:
      MY_VAR: my_value
    secret_environment_variables:
      MY_SECRET_VAR: my_secret_value
  register: function_namespace_creation_task

- name: Make sure function namespace is deleted
  community.general.scaleway_function_namespace:
    project_id: '{{ scw_project }}'
    state: absent
    region: fr-par
    name: my-awesome-function-namespace
"""

RETURN = r"""
function_namespace:
  description: The function namespace information.
  returned: when O(state=present)
  type: dict
  sample:
    description: ""
    environment_variables:
      MY_VAR: my_value
    error_message:
    id: 531a1fd7-98d2-4a74-ad77-d398324304b8
    name: my-awesome-function-namespace
    organization_id: e04e3bdc-015c-4514-afde-9389e9be24b0
    project_id: d44cea58-dcb7-4c95-bff1-1105acb60a98
    region: fr-par
    registry_endpoint: ""
    registry_namespace_id: ""
    secret_environment_variables:
      - key: MY_SECRET_VAR
        value: $argon2id$v=19$m=65536,t=1,p=2$tb6UwSPWx/rH5Vyxt9Ujfw$5ZlvaIjWwNDPxD9Rdght3NarJz4IETKjpvAU3mMSmFg
    status: pending
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
    "absent"
)

MUTABLE_ATTRIBUTES = (
    "description",
    "environment_variables",
    "secret_environment_variables",
)


def payload_from_wished_fn(wished_fn):
    payload = {
        "project_id": wished_fn["project_id"],
        "name": wished_fn["name"],
        "description": wished_fn["description"],
        "environment_variables": wished_fn["environment_variables"],
        "secret_environment_variables": SecretVariables.dict_to_list(wished_fn["secret_environment_variables"])
    }

    return payload


def absent_strategy(api, wished_fn):
    changed = False

    fn_list = api.fetch_all_resources("namespaces")
    fn_lookup = {fn["name"]: fn for fn in fn_list}

    if wished_fn["name"] not in fn_lookup:
        return changed, {}

    target_fn = fn_lookup[wished_fn["name"]]
    changed = True
    if api.module.check_mode:
        return changed, {"status": "Function namespace would be destroyed"}

    api.wait_to_complete_state_transition(resource=target_fn, stable_states=STABLE_STATES, force_wait=True)
    response = api.delete(path=api.api_path + "/%s" % target_fn["id"])
    if not response.ok:
        api.module.fail_json(msg='Error deleting function namespace [{0}: {1}]'.format(
            response.status_code, response.json))

    api.wait_to_complete_state_transition(resource=target_fn, stable_states=STABLE_STATES)
    return changed, response.json


def present_strategy(api, wished_fn):
    changed = False

    fn_list = api.fetch_all_resources("namespaces")
    fn_lookup = {fn["name"]: fn for fn in fn_list}

    payload_fn = payload_from_wished_fn(wished_fn)

    if wished_fn["name"] not in fn_lookup:
        changed = True
        if api.module.check_mode:
            return changed, {"status": "A function namespace would be created."}

        # Create function namespace
        api.warn(payload_fn)
        creation_response = api.post(path=api.api_path,
                                     data=payload_fn)

        if not creation_response.ok:
            msg = "Error during function namespace creation: %s: '%s' (%s)" % (creation_response.info['msg'],
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
                                                          verifiable_mutable_attributes=MUTABLE_ATTRIBUTES,
                                                          mutable_attributes=MUTABLE_ATTRIBUTES)

    if not patch_payload:
        return changed, target_fn

    changed = True
    if api.module.check_mode:
        return changed, {"status": "Function namespace attributes would be changed."}

    fn_patch_response = api.patch(path=api.api_path + "/%s" % target_fn["id"],
                                  data=patch_payload)

    if not fn_patch_response.ok:
        api.module.fail_json(msg='Error during function namespace attributes update: [{0}: {1}]'.format(
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
    wished_function_namespace = {
        "state": module.params["state"],
        "project_id": module.params["project_id"],
        "name": module.params["name"],
        "description": module.params['description'],
        "environment_variables": module.params['environment_variables'],
        "secret_environment_variables": module.params['secret_environment_variables']
    }

    api = Scaleway(module=module)
    api.api_path = "functions/v1beta1/regions/%s/namespaces" % region

    changed, summary = state_strategy[wished_function_namespace["state"]](api=api, wished_fn=wished_function_namespace)

    module.exit_json(changed=changed, function_namespace=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(scaleway_waitable_resource_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default='present', choices=['absent', 'present']),
        project_id=dict(type='str', required=True),
        region=dict(type='str', required=True, choices=SCALEWAY_REGIONS),
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
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

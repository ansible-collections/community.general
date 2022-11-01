#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway Container registry management module
#
# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_container_registry
short_description: Scaleway Container registry management module
version_added: 5.8.0
author: Guillaume MARTINEZ (@Lunik)
description:
  - This module manages container registries on Scaleway account.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.scaleway_waitable_resource


options:
  state:
    type: str
    description:
      - Indicate desired state of the container regitry.
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
      - Scaleway region to use (for example C(fr-par)).
    required: true
    choices:
      - fr-par
      - nl-ams
      - pl-waw

  name:
    type: str
    description:
      - Name of the container registry.
    required: true

  description:
    description:
      - Description of the container registry.
    type: str
    default: ''

  privacy_policy:
    type: str
    description:
      - Default visibility policy.
      - Everyone will be able to pull images from a C(public) registry.
    choices:
      - public
      - private
    default: private
'''

EXAMPLES = '''
- name: Create a container registry
  community.general.scaleway_container_registry:
    project_id: '{{ scw_project }}'
    state: present
    region: fr-par
    name: my-awesome-container-registry
  register: container_registry_creation_task

- name: Make sure container registry is deleted
  community.general.scaleway_container_registry:
    project_id: '{{ scw_project }}'
    state: absent
    region: fr-par
    name: my-awesome-container-registry
'''

RETURN = '''
container_registry:
  description: The container registry information.
  returned: when I(state=present)
  type: dict
  sample:
    created_at: "2022-10-14T09:51:07.949716Z"
    description: Managed by Ansible
    endpoint: rg.fr-par.scw.cloud/my-awesome-registry
    id: 0d7d5270-7864-49c2-920b-9fd6731f3589
    image_count: 0
    is_public: false
    name: my-awesome-registry
    organization_id: 10697b59-5c34-4d24-8d15-9ff2d3b89f58
    project_id: 3da4f0b2-06be-4773-8ec4-5dfa435381be
    region: fr-par
    size: 0
    status: ready
    status_message: ""
    updated_at: "2022-10-14T09:51:07.949716Z"
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_ENDPOINT, SCALEWAY_REGIONS, scaleway_argument_spec, Scaleway,
    scaleway_waitable_resource_argument_spec, resource_attributes_should_be_changed
)
from ansible.module_utils.basic import AnsibleModule

STABLE_STATES = (
    "ready",
    "absent"
)

MUTABLE_ATTRIBUTES = (
    "description",
    "is_public"
)


def payload_from_wished_cr(wished_cr):
    payload = {
        "project_id": wished_cr["project_id"],
        "name": wished_cr["name"],
        "description": wished_cr["description"],
        "is_public": wished_cr["privacy_policy"] == "public"
    }

    return payload


def absent_strategy(api, wished_cr):
    changed = False

    cr_list = api.fetch_all_resources("namespaces")
    cr_lookup = dict((cr["name"], cr)
                     for cr in cr_list)

    if wished_cr["name"] not in cr_lookup:
        return changed, {}

    target_cr = cr_lookup[wished_cr["name"]]
    changed = True
    if api.module.check_mode:
        return changed, {"status": "Container registry would be destroyed"}

    api.wait_to_complete_state_transition(resource=target_cr, stable_states=STABLE_STATES, force_wait=True)
    response = api.delete(path=api.api_path + "/%s" % target_cr["id"])
    if not response.ok:
        api.module.fail_json(msg='Error deleting container registry [{0}: {1}]'.format(
            response.status_code, response.json))

    api.wait_to_complete_state_transition(resource=target_cr, stable_states=STABLE_STATES)
    return changed, response.json


def present_strategy(api, wished_cr):
    changed = False

    cr_list = api.fetch_all_resources("namespaces")
    cr_lookup = dict((cr["name"], cr)
                     for cr in cr_list)

    payload_cr = payload_from_wished_cr(wished_cr)

    if wished_cr["name"] not in cr_lookup:
        changed = True
        if api.module.check_mode:
            return changed, {"status": "A container registry would be created."}

        # Create container registry
        api.warn(payload_cr)
        creation_response = api.post(path=api.api_path,
                                     data=payload_cr)

        if not creation_response.ok:
            msg = "Error during container registry creation: %s: '%s' (%s)" % (creation_response.info['msg'],
                                                                               creation_response.json['message'],
                                                                               creation_response.json)
            api.module.fail_json(msg=msg)

        api.wait_to_complete_state_transition(resource=creation_response.json, stable_states=STABLE_STATES)
        response = api.get(path=api.api_path + "/%s" % creation_response.json["id"])
        return changed, response.json

    target_cr = cr_lookup[wished_cr["name"]]
    patch_payload = resource_attributes_should_be_changed(target=target_cr,
                                                          wished=payload_cr,
                                                          verifiable_mutable_attributes=MUTABLE_ATTRIBUTES,
                                                          mutable_attributes=MUTABLE_ATTRIBUTES)

    if not patch_payload:
        return changed, target_cr

    changed = True
    if api.module.check_mode:
        return changed, {"status": "Container registry attributes would be changed."}

    cr_patch_response = api.patch(path=api.api_path + "/%s" % target_cr["id"],
                                  data=patch_payload)

    if not cr_patch_response.ok:
        api.module.fail_json(msg='Error during container registry attributes update: [{0}: {1}]'.format(
            cr_patch_response.status_code, cr_patch_response.json['message']))

    api.wait_to_complete_state_transition(resource=target_cr, stable_states=STABLE_STATES)
    response = api.get(path=api.api_path + "/%s" % target_cr["id"])
    return changed, response.json


state_strategy = {
    "present": present_strategy,
    "absent": absent_strategy
}


def core(module):
    region = module.params["region"]
    wished_container_registry = {
        "state": module.params["state"],
        "project_id": module.params["project_id"],
        "name": module.params["name"],
        "description": module.params['description'],
        "privacy_policy": module.params['privacy_policy']
    }

    api = Scaleway(module=module)
    api.api_path = "registry/v1/regions/%s/namespaces" % region

    changed, summary = state_strategy[wished_container_registry["state"]](api=api, wished_cr=wished_container_registry)

    module.exit_json(changed=changed, container_registry=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(scaleway_waitable_resource_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default='present', choices=['absent', 'present']),
        project_id=dict(type='str', required=True),
        region=dict(type='str', required=True, choices=SCALEWAY_REGIONS),
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        privacy_policy=dict(type='str', default='private', choices=['public', 'private'])
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Florian Apolloner (@apollo13)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: consul_token
short_description: Manipulate Consul tokens
version_added: 8.3.0
description:
 - Allows the addition, modification and deletion of tokens in a consul
   cluster via the agent. For more details on using and configuring ACLs,
   see U(https://www.consul.io/docs/guides/acl.html).
author:
  - Florian Apolloner (@apollo13)
extends_documentation_fragment:
  - community.general.consul
  - community.general.consul.token
  - community.general.consul.actiongroup_consul
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
    details:
      - In check mode the diff will miss operational attributes.
  action_group:
    version_added: 8.3.0
options:
  state:
    description:
      - Whether the token should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  accessor_id:
    description:
      - Specifies a UUID to use as the token's Accessor ID.
        If not specified a UUID will be generated for this field.
    type: str
  secret_id:
    description:
      - Specifies a UUID to use as the token's Secret ID.
        If not specified a UUID will be generated for this field.
    type: str
  description:
    description:
      - Free form human readable description of the token.
    type: str
  policies:
    type: list
    elements: dict
    description:
      - List of policies to attach to the token. Each policy is a dict.
      - If the parameter is left blank, any policies currently assigned will not be changed.
      - Any empty array (V([])) will clear any policies previously set.
    suboptions:
      name:
        description:
          - The name of the policy to attach to this token; see M(community.general.consul_policy) for more info.
          - Either this or O(policies[].id) must be specified.
        type: str
      id:
        description:
          - The ID of the policy to attach to this token; see M(community.general.consul_policy) for more info.
          - Either this or O(policies[].name) must be specified.
        type: str
  roles:
    type: list
    elements: dict
    description:
      - List of roles to attach to the token. Each role is a dict.
      - If the parameter is left blank, any roles currently assigned will not be changed.
      - Any empty array (V([])) will clear any roles previously set.
    suboptions:
      name:
        description:
          - The name of the role to attach to this token; see M(community.general.consul_role) for more info.
          - Either this or O(roles[].id) must be specified.
        type: str
      id:
        description:
          - The ID of the role to attach to this token; see M(community.general.consul_role) for more info.
          - Either this or O(roles[].name) must be specified.
        type: str
  templated_policies:
    description:
      - The list of templated policies that should be applied to the role.
    type: list
    elements: dict
    suboptions:
      template_name:
        description:
          - The templated policy name.
        type: str
        required: true
      template_variables:
        description:
          - The templated policy variables.
          - Not all templated policies require variables.
        type: dict
  service_identities:
    type: list
    elements: dict
    description:
      - List of service identities to attach to the token.
      - If not specified, any service identities currently assigned will not be changed.
      - If the parameter is an empty array (V([])), any node identities assigned will be unassigned.
    suboptions:
      service_name:
        description:
          - The name of the service.
          - Must not be longer than 256 characters, must start and end with a lowercase alphanumeric character.
          - May only contain lowercase alphanumeric characters as well as V(-) and V(_).
        type: str
        required: true
      datacenters:
        description:
          - The datacenters the token will be effective.
          - If an empty array (V([])) is specified, the token will valid in all datacenters.
          - including those which do not yet exist but may in the future.
        type: list
        elements: str
  node_identities:
    type: list
    elements: dict
    description:
      - List of node identities to attach to the token.
      - If not specified, any node identities currently assigned will not be changed.
      - If the parameter is an empty array (V([])), any node identities assigned will be unassigned.
    suboptions:
      node_name:
        description:
          - The name of the node.
          - Must not be longer than 256 characters, must start and end with a lowercase alphanumeric character.
          - May only contain lowercase alphanumeric characters as well as V(-) and V(_).
        type: str
        required: true
      datacenter:
        description:
          - The nodes datacenter.
          - This will result in effective token only being valid in this datacenter.
        type: str
        required: true
  local:
    description:
      - If true, indicates that the token should not be replicated globally
        and instead be local to the current datacenter.
    type: bool
  expiration_ttl:
    description:
      - This is a convenience field and if set will initialize the C(expiration_time).
        Can be specified in the form of V(60s) or V(5m) (that is, 60 seconds or 5 minutes,
        respectively). Ingored when the token is updated!
    type: str
"""

EXAMPLES = """
- name: Create / Update a token by accessor_id
  community.general.consul_token:
    state: present
    accessor_id: 07a7de84-c9c7-448a-99cc-beaf682efd21
    token: 8adddd91-0bd6-d41d-ae1a-3b49cfa9a0e8
    roles:
      - name: role1
      - name: role2
    service_identities:
      - service_name: service1
        datacenters: [dc1, dc2]
    node_identities:
      - node_name: node1
        datacenter: dc1
    expiration_ttl: 50m

- name: Delete a token
  community.general.consul_token:
    state: absent
    accessor_id: 07a7de84-c9c7-448a-99cc-beaf682efd21
    token: 8adddd91-0bd6-d41d-ae1a-3b49cfa9a0e8
"""

RETURN = """
token:
    description: The token as returned by the consul HTTP API.
    returned: always
    type: dict
    sample:
        AccessorID: 07a7de84-c9c7-448a-99cc-beaf682efd21
        CreateIndex: 632
        CreateTime: "2024-01-14T21:53:01.402749174+01:00"
        Description: Testing
        Hash: rj5PeDHddHslkpW7Ij4OD6N4bbSXiecXFmiw2SYXg2A=
        Local: false
        ModifyIndex: 633
        SecretID: bd380fba-da17-7cee-8576-8d6427c6c930
        ServiceIdentities: [{"ServiceName": "test"}]
operation:
    description: The operation performed.
    returned: changed
    type: str
    sample: update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    _ConsulModule,
)


def normalize_link_obj(api_obj, module_obj, key):
    api_objs = api_obj.get(key)
    module_objs = module_obj.get(key)
    if api_objs is None or module_objs is None:
        return
    name_to_id = {i["Name"]: i["ID"] for i in api_objs}
    id_to_name = {i["ID"]: i["Name"] for i in api_objs}

    for obj in module_objs:
        identifier = obj.get("ID")
        name = obj.get("Name)")
        if identifier and not name and identifier in id_to_name:
            obj["Name"] = id_to_name[identifier]
        if not identifier and name and name in name_to_id:
            obj["ID"] = name_to_id[name]


class ConsulTokenModule(_ConsulModule):
    api_endpoint = "acl/token"
    result_key = "token"
    unique_identifiers = ["accessor_id"]

    create_only_fields = {"expiration_ttl"}

    def read_object(self):
        # if `accessor_id` is not supplied we can only create objects and are not idempotent
        if not self.id_from_obj(self.params):
            return None
        return super(ConsulTokenModule, self).read_object()

    def needs_update(self, api_obj, module_obj):
        # SecretID is usually not supplied
        if "SecretID" not in module_obj and "SecretID" in api_obj:
            del api_obj["SecretID"]
        normalize_link_obj(api_obj, module_obj, "Roles")
        normalize_link_obj(api_obj, module_obj, "Policies")
        # ExpirationTTL is only supported on create, not for update
        # it writes to ExpirationTime, so we need to remove that as well
        if "ExpirationTTL" in module_obj:
            del module_obj["ExpirationTTL"]
        return super(ConsulTokenModule, self).needs_update(api_obj, module_obj)


NAME_ID_SPEC = dict(
    name=dict(type="str"),
    id=dict(type="str"),
)

NODE_ID_SPEC = dict(
    node_name=dict(type="str", required=True),
    datacenter=dict(type="str", required=True),
)

SERVICE_ID_SPEC = dict(
    service_name=dict(type="str", required=True),
    datacenters=dict(type="list", elements="str"),
)

TEMPLATE_POLICY_SPEC = dict(
    template_name=dict(type="str", required=True),
    template_variables=dict(type="dict"),
)


_ARGUMENT_SPEC = {
    "description": dict(),
    "accessor_id": dict(),
    "secret_id": dict(no_log=True),
    "roles": dict(
        type="list",
        elements="dict",
        options=NAME_ID_SPEC,
        mutually_exclusive=[("name", "id")],
        required_one_of=[("name", "id")],
    ),
    "policies": dict(
        type="list",
        elements="dict",
        options=NAME_ID_SPEC,
        mutually_exclusive=[("name", "id")],
        required_one_of=[("name", "id")],
    ),
    "templated_policies": dict(
        type="list",
        elements="dict",
        options=TEMPLATE_POLICY_SPEC,
    ),
    "node_identities": dict(
        type="list",
        elements="dict",
        options=NODE_ID_SPEC,
    ),
    "service_identities": dict(
        type="list",
        elements="dict",
        options=SERVICE_ID_SPEC,
    ),
    "local": dict(type="bool"),
    "expiration_ttl": dict(type="str"),
    "state": dict(default="present", choices=["present", "absent"]),
}
_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        required_if=[("state", "absent", ["accessor_id"])],
        supports_check_mode=True,
    )
    consul_module = ConsulTokenModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()

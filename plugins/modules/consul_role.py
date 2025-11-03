#!/usr/bin/python

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: consul_role
short_description: Manipulate Consul roles
version_added: 7.5.0
description:
  - Allows the addition, modification and deletion of roles in a Consul cluster using the agent. For more details on using
    and configuring ACLs, see U(https://www.consul.io/docs/guides/acl.html).
author:
  - Håkon Lerring (@Hakon)
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
      - In check mode the diff misses operational attributes.
    version_added: 8.3.0
  action_group:
    version_added: 8.3.0
options:
  name:
    description:
      - A name used to identify the role.
    required: true
    type: str
  state:
    description:
      - Whether the role should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  description:
    description:
      - Description of the role.
      - If not specified, the assigned description is not changed.
    type: str
  policies:
    type: list
    elements: dict
    description:
      - List of policies to attach to the role. Each policy is a dict.
      - If the parameter is left blank, any policies currently assigned are not changed.
      - Any empty array (V([])) clears any policies previously set.
    suboptions:
      name:
        description:
          - The name of the policy to attach to this role; see M(community.general.consul_policy) for more info.
          - Either this or O(policies[].id) must be specified.
        type: str
      id:
        description:
          - The ID of the policy to attach to this role; see M(community.general.consul_policy) for more info.
          - Either this or O(policies[].name) must be specified.
        type: str
  templated_policies:
    description:
      - The list of templated policies that should be applied to the role.
    type: list
    elements: dict
    version_added: 8.3.0
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
      - List of service identities to attach to the role.
      - If not specified, any service identities currently assigned are not changed.
      - If the parameter is an empty array (V([])), any node identities assigned are unassigned.
    suboptions:
      service_name:
        description:
          - The name of the node.
          - Must not be longer than 256 characters, must start and end with a lowercase alphanumeric character.
          - May only contain lowercase alphanumeric characters as well as V(-) and V(_).
          - This suboption has been renamed from O(service_identities[].name) to O(service_identities[].service_name) in community.general
            8.3.0. The old name can still be used.
        type: str
        required: true
        aliases:
          - name
      datacenters:
        description:
          - The datacenters where the policies are effective.
          - This results in effective policy only being valid in this datacenter.
          - If an empty array (V([])) is specified, the policies are valid in all datacenters.
          - Including those which do not yet exist but may in the future.
        type: list
        elements: str
  node_identities:
    type: list
    elements: dict
    description:
      - List of node identities to attach to the role.
      - If not specified, any node identities currently assigned are not changed.
      - If the parameter is an empty array (V([])), any node identities assigned are unassigned.
    suboptions:
      node_name:
        description:
          - The name of the node.
          - Must not be longer than 256 characters, must start and end with a lowercase alphanumeric character.
          - May only contain lowercase alphanumeric characters as well as V(-) and V(_).
          - This suboption has been renamed from O(node_identities[].name) to O(node_identities[].node_name) in community.general
            8.3.0. The old name can still be used.
        type: str
        required: true
        aliases:
          - name
      datacenter:
        description:
          - The nodes datacenter.
          - This results in effective policy only being valid in this datacenter.
        type: str
        required: true
"""

EXAMPLES = r"""
- name: Create a role with 2 policies
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role
    policies:
      - id: 783beef3-783f-f41f-7422-7087dc272765
      - name: "policy-1"

- name: Create a role with service identity
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-2
    service_identities:
      - name: web
        datacenters:
          - dc1

- name: Create a role with node identity
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-3
    node_identities:
      - name: node-1
        datacenter: dc2

- name: Remove a role
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-3
    state: absent
"""

RETURN = r"""
role:
  description: The role object.
  returned: success
  type: dict
  sample:
    {
      "CreateIndex": 39,
      "Description": "",
      "Hash": "Trt0QJtxVEfvTTIcdTUbIJRr6Dsi6E4EcwSFxx9tCYM=",
      "ID": "9a300b8d-48db-b720-8544-a37c0f5dafb5",
      "ModifyIndex": 39,
      "Name": "foo-role",
      "Policies": [
        {
          "ID": "b1a00172-d7a1-0e66-a12e-7a4045c4b774",
          "Name": "foo-access"
        }
      ]
    }
operation:
  description: The operation performed on the role.
  returned: changed
  type: str
  sample: update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    OPERATION_READ,
    _ConsulModule,
)


class ConsulRoleModule(_ConsulModule):
    api_endpoint = "acl/role"
    result_key = "role"
    unique_identifiers = ["id"]

    def endpoint_url(self, operation, identifier=None):
        if operation == OPERATION_READ:
            return [self.api_endpoint, "name", self.params["name"]]
        return super().endpoint_url(operation, identifier)


NAME_ID_SPEC = dict(
    name=dict(type="str"),
    id=dict(type="str"),
)

NODE_ID_SPEC = dict(
    node_name=dict(type="str", required=True, aliases=["name"]),
    datacenter=dict(type="str", required=True),
)

SERVICE_ID_SPEC = dict(
    service_name=dict(type="str", required=True, aliases=["name"]),
    datacenters=dict(type="list", elements="str"),
)

TEMPLATE_POLICY_SPEC = dict(
    template_name=dict(type="str", required=True),
    template_variables=dict(type="dict"),
)

_ARGUMENT_SPEC = {
    "name": dict(type="str", required=True),
    "description": dict(type="str"),
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
    "state": dict(default="present", choices=["present", "absent"]),
}
_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        supports_check_mode=True,
    )
    consul_module = ConsulRoleModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()

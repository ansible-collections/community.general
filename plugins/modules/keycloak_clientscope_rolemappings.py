#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_clientscope_rolemappings

short_description: Allows administration of Keycloak clientscope scope mappings to restrict the usage of certain roles to
  specific clientscopes

version_added: TODO

description:
  - This module allows you to add or remove Keycloak roles from clientscopes using the Keycloak REST API. It requires access
    to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with
    the scope tailored to your needs and a user having the expected roles.
  - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and are returned that way
    by this module. You may pass single values for attributes when calling the module, and this is translated into a list
    suitable for the API.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  state:
    description:
      - State of the role mapping.
      - On V(present), all roles in O(role_names) are mapped if not exist yet.
      - On V(absent), all roles mapping in O(role_names) are removed if it exists.
    default: 'present'
    type: str
    choices:
      - present
      - absent

  realm:
    type: str
    description:
      - The Keycloak realm under which clients resides.
    default: 'master'

  clientscope_id:
    required: true
    type: str
    description:
      - Roles provided in O(role_names) will be added to this clientscope.

  client_id:
    type: str
    description:
      - If the O(role_names) are client role, the client ID under which it resides.
      - If this parameter is absent, the roles are considered a realm role.

  role_names:
    required: true
    type: list
    elements: str
    description:
      - Names of roles to add.
      - If O(client_id) is present, all roles must be under this client.
      - If O(client_id) is absent, all roles must be under the realm.

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Felix Grzelka
  # TODO
  # adapted from keycloak_client_rolescope
  # - Andre Desrosiers (@desand01)
"""

EXAMPLES = r"""
- name: Add roles to clientscope
  community.general.keycloak_clientscope_rolemappings:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    client_id: frontend-client-public
    clientscope_id: frontend-clientscope
    role_names:
      - backend-role-admin
      - backend-role-user

- name: Remove roles from clientscope
  community.general.keycloak_clientscope_rolemappings:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    client_id: frontend-client-public
    clientscope_id: frontend-clientscope
    role_names:
      - backend-role-admin
    state: absent

- name: Add realm roles to clientscope
  community.general.keycloak_clientscope_rolemappings:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    clientscope_id: frontend-clientscope
    role_names:
      - realm-role-admin
      - realm-role-user
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: "clientscope scope mappings for frontend-client-public have been updated"

end_state:
  description: Representation of clientscope scope mappings after module execution.
  returned: on success
  type: list
  elements: dict
  sample:
    [
      {
            "clientRole": false,
            "composite": false,
            "containerId": "77f9bd4e-13a6-451e-9c72-ee6997299c1f",
            "description": "User role",
            "id": "9e155ef7-86f5-4def-b507-581ce7b87013",
            "name": "realm-role-user"
      },
      {
            "clientRole": false,
            "composite": false,
            "containerId": "77f9bd4e-13a6-451e-9c72-ee6997299c1f",
            "description": "Admin role",
            "id": "9e155ef7-86f5-4def-b507-581ce7b87013",
            "name": "realm-role-admin"
      }
    ]
"""

import copy

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    KeycloakError,
    get_token,
    keycloak_argument_spec,
)


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        client_id=dict(type="str"),
        clientscope_id=dict(type="str", required=True),
        realm=dict(type="str", default="master"),
        role_names=dict(type="list", elements="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = dict(changed=False, msg="", diff={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    client_id = module.params.get("client_id")
    clientscope_id = module.params.get("clientscope_id")
    role_names = module.params.get("role_names")
    state = module.params.get("state")

    realm_object = kc.get_realm_by_id(realm)
    if not realm_object:
        module.fail_json(msg=f"Failed to retrive realm '{realm}'")

    clientscope_object = kc.get_clientscope_by_name(clientscope_id, realm)
    if not clientscope_object:
        module.fail_json(msg=f"Failed to retrive client-scope '{clientscope_id}'")

    if client_id:
        # add client role
        client_object = kc.get_client_by_clientid(client_id, realm)
        if not client_object:
            module.fail_json(msg=f"Failed to retrive client '{realm}.{client_id}'")
        if client_object["fullScopeAllowed"] and state == "present":
            module.fail_json(msg=f"FullScopeAllowed is active for Client '{realm}.{client_id}'")

        before_roles = kc.get_clientscope_scope_mappings_client(clientscope_object["id"], client_object["id"], realm)
        available_roles_by_name = kc.get_client_roles_by_id(client_object["id"], realm)
    else:
        # add realm role
        before_roles = kc.get_clientscope_scope_mappings_realm(clientscope_object["id"], realm)
        available_roles_by_name = kc.get_realm_roles(realm)

    # convert to indexed Dict by name
    available_roles_by_name = {role["name"]: role for role in available_roles_by_name}
    before_roles_by_name = {role["name"]: role for role in before_roles}
    desired_roles = copy.deepcopy(before_roles)
    changed_roles = []

    if state == "present":
        # update desired
        for role_name in role_names:
            if role_name not in available_roles_by_name:
                if clientscope_id:
                    module.fail_json(msg=f"Failed to retrive role '{realm}.{clientscope_id}.{role_name}'")
                else:
                    module.fail_json(msg=f"Failed to retrive role '{realm}.{role_name}'")
            if role_name not in before_roles_by_name:
                changed_roles.append(available_roles_by_name[role_name])
                desired_roles.append(available_roles_by_name[role_name])
    else:
        # remove role if present
        for role_name in role_names:
            if role_name in before_roles_by_name:
                changed_roles.append(before_roles_by_name[role_name])
                desired_roles.remove(available_roles_by_name[role_name])

    before_roles = sorted(before_roles, key=lambda d: d["name"])
    desired_role_mapping = sorted(desired_roles, key=lambda d: d["name"])

    result["changed"] = len(changed_roles) > 0

    if module._diff:
        result["diff"] = dict(before={"roles": before_roles}, after={"roles": desired_role_mapping})

    if not result["changed"]:
        # no changes
        result["end_state"] = before_roles
        result["msg"] = f"No changes required for clientscope {clientscope_id}."
    elif state == "present":
        # doing update
        if module.check_mode:
            result["end_state"] = desired_role_mapping
        elif client_id:
            result["end_state"] = kc.update_clientscope_scope_mappings_client(
                changed_roles, clientscope_object["id"], client_object["id"], realm
            )
        else:
            result["end_state"] = kc.update_clientscope_scope_mappings_realm(
                changed_roles, clientscope_object["id"], realm
            )
        result["msg"] = f"Clientscope scope mappings for {clientscope_id} have been updated"
    else:
        # doing delete
        if module.check_mode:
            result["end_state"] = desired_role_mapping
        elif client_id:
            result["end_state"] = kc.delete_clientscope_scope_mappings_client(
                changed_roles, clientscope_object["id"], client_object["id"], realm
            )
        else:
            result["end_state"] = kc.delete_clientscope_scope_mappings_realm(
                changed_roles, clientscope_object["id"], realm
            )
        result["msg"] = f"Clientscope scope mappings for {clientscope_id} have been deleted"
    module.exit_json(**result)


if __name__ == "__main__":
    main()

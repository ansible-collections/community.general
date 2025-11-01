#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_client_rolescope

short_description: Allows administration of Keycloak client roles scope to restrict the usage of certain roles to a other
  specific client applications

version_added: 8.6.0

description:
  - This module allows you to add or remove Keycloak roles from clients scope using the Keycloak REST API. It requires access
    to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with
    the scope tailored to your needs and a user having the expected roles.
  - Client O(client_id) must have O(community.general.keycloak_client#module:full_scope_allowed) set to V(false).
  - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and are returned that way
    by this module. You may pass single values for attributes when calling the module, and this is translated into a list
    suitable for the API.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 10.2.0

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

  client_id:
    type: str
    required: true
    description:
      - Roles provided in O(role_names) while be added to this client scope.
  client_scope_id:
    type: str
    description:
      - If the O(role_names) are client role, the client ID under which it resides.
      - If this parameter is absent, the roles are considered a realm role.
  role_names:
    required: true
    type: list
    elements: str
    description:
      - Names of roles to manipulate.
      - If O(client_scope_id) is present, all roles must be under this client.
      - If O(client_scope_id) is absent, all roles must be under the realm.
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Andre Desrosiers (@desand01)
"""

EXAMPLES = r"""
- name: Add roles to public client scope
  community.general.keycloak_client_rolescope:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    client_id: frontend-client-public
    client_scope_id: backend-client-private
    role_names:
      - backend-role-admin
      - backend-role-user

- name: Remove roles from public client scope
  community.general.keycloak_client_rolescope:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    client_id: frontend-client-public
    client_scope_id: backend-client-private
    role_names:
      - backend-role-admin
    state: absent

- name: Add realm roles to public client scope
  community.general.keycloak_client_rolescope:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
    client_id: frontend-client-public
    role_names:
      - realm-role-admin
      - realm-role-user
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: "Client role scope for frontend-client-public has been updated"

end_state:
  description: Representation of role role scope after module execution.
  returned: on success
  type: list
  elements: dict
  sample:
    [
      {
        "clientRole": false,
        "composite": false,
        "containerId": "MyCustomRealm",
        "id": "47293104-59a6-46f0-b460-2e9e3c9c424c",
        "name": "backend-role-admin"
      },
      {
        "clientRole": false,
        "composite": false,
        "containerId": "MyCustomRealm",
        "id": "39c62a6d-542c-4715-92d2-41021eb33967",
        "name": "backend-role-user"
      }
    ]
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    keycloak_argument_spec,
    get_token,
    KeycloakError,
)
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        client_id=dict(type="str", required=True),
        client_scope_id=dict(type="str"),
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
    clientid = module.params.get("client_id")
    client_scope_id = module.params.get("client_scope_id")
    role_names = module.params.get("role_names")
    state = module.params.get("state")

    objRealm = kc.get_realm_by_id(realm)
    if not objRealm:
        module.fail_json(msg=f"Failed to retrive realm '{realm}'")

    objClient = kc.get_client_by_clientid(clientid, realm)
    if not objClient:
        module.fail_json(msg=f"Failed to retrive client '{realm}.{clientid}'")
    if objClient["fullScopeAllowed"] and state == "present":
        module.fail_json(msg=f"FullScopeAllowed is active for Client '{realm}.{clientid}'")

    if client_scope_id:
        objClientScope = kc.get_client_by_clientid(client_scope_id, realm)
        if not objClientScope:
            module.fail_json(msg=f"Failed to retrive client '{realm}.{client_scope_id}'")
        before_role_mapping = kc.get_client_role_scope_from_client(objClient["id"], objClientScope["id"], realm)
    else:
        before_role_mapping = kc.get_client_role_scope_from_realm(objClient["id"], realm)

    if client_scope_id:
        # retrive all role from client_scope
        client_scope_roles_by_name = kc.get_client_roles_by_id(objClientScope["id"], realm)
    else:
        # retrive all role from realm
        client_scope_roles_by_name = kc.get_realm_roles(realm)

    # convert to indexed Dict by name
    client_scope_roles_by_name = {role["name"]: role for role in client_scope_roles_by_name}
    role_mapping_by_name = {role["name"]: role for role in before_role_mapping}
    role_mapping_to_manipulate = []

    if state == "present":
        # update desired
        for role_name in role_names:
            if role_name not in client_scope_roles_by_name:
                if client_scope_id:
                    module.fail_json(msg=f"Failed to retrive role '{realm}.{client_scope_id}.{role_name}'")
                else:
                    module.fail_json(msg=f"Failed to retrive role '{realm}.{role_name}'")
            if role_name not in role_mapping_by_name:
                role_mapping_to_manipulate.append(client_scope_roles_by_name[role_name])
                role_mapping_by_name[role_name] = client_scope_roles_by_name[role_name]
    else:
        # remove role if present
        for role_name in role_names:
            if role_name in role_mapping_by_name:
                role_mapping_to_manipulate.append(role_mapping_by_name[role_name])
                del role_mapping_by_name[role_name]

    before_role_mapping = sorted(before_role_mapping, key=lambda d: d["name"])
    desired_role_mapping = sorted(role_mapping_by_name.values(), key=lambda d: d["name"])

    result["changed"] = len(role_mapping_to_manipulate) > 0

    if result["changed"]:
        result["diff"] = dict(before=before_role_mapping, after=desired_role_mapping)

    if not result["changed"]:
        # no changes
        result["end_state"] = before_role_mapping
        result["msg"] = f"No changes required for client role scope {clientid}."
    elif state == "present":
        # doing update
        if module.check_mode:
            result["end_state"] = desired_role_mapping
        elif client_scope_id:
            result["end_state"] = kc.update_client_role_scope_from_client(
                role_mapping_to_manipulate, objClient["id"], objClientScope["id"], realm
            )
        else:
            result["end_state"] = kc.update_client_role_scope_from_realm(
                role_mapping_to_manipulate, objClient["id"], realm
            )
        result["msg"] = f"Client role scope for {clientid} has been updated"
    else:
        # doing delete
        if module.check_mode:
            result["end_state"] = desired_role_mapping
        elif client_scope_id:
            result["end_state"] = kc.delete_client_role_scope_from_client(
                role_mapping_to_manipulate, objClient["id"], objClientScope["id"], realm
            )
        else:
            result["end_state"] = kc.delete_client_role_scope_from_realm(
                role_mapping_to_manipulate, objClient["id"], realm
            )
        result["msg"] = f"Client role scope for {clientid} has been deleted"
    module.exit_json(**result)


if __name__ == "__main__":
    main()

#!/usr/bin/python

# Copyright (c) 2022, Dušan Marković (@bratwurzt)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_user_rolemapping

short_description: Allows administration of Keycloak user_rolemapping with the Keycloak API

version_added: 5.7.0

description:
  - This module allows you to add, remove or modify Keycloak user_rolemapping with the Keycloak REST API. It requires access
    to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with
    the scope tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).
  - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and are returned that way
    by this module. You may pass single values for attributes when calling the module, and this is translated into a list
    suitable for the API.
  - When updating a user_rolemapping, where possible provide the role ID to the module. This removes a lookup to the API to
    translate the name into the role ID.
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
      - State of the user_rolemapping.
      - On V(present), the user_rolemapping is created if it does not yet exist, or updated with the parameters you provide.
      - On V(absent), the user_rolemapping is removed if it exists.
    default: 'present'
    type: str
    choices:
      - present
      - absent

  realm:
    type: str
    description:
      - They Keycloak realm under which this role_representation resides.
    default: 'master'

  target_username:
    type: str
    description:
      - Username of the user roles are mapped to.
      - This parameter is not required (can be replaced by uid for less API call).
  uid:
    type: str
    description:
      - ID of the user to be mapped.
      - This parameter is not required for updating or deleting the rolemapping but providing it reduces the number of API
        calls required.
  service_account_user_client_id:
    type: str
    description:
      - Client ID of the service-account-user to be mapped.
      - This parameter is not required for updating or deleting the rolemapping but providing it reduces the number of API
        calls required.
  client_id:
    type: str
    description:
      - Name of the client (different than O(cid)) whose role is to be mapped.
      - This parameter is required if O(cid) is not provided (can be replaced by O(cid) to reduce the number of API calls
        that must be made).
      - If neither O(cid) nor O(client_id) is specified, a B(realm) role is mapped instead.
  cid:
    type: str
    description:
      - ID of the client whose role is to be mapped.
      - This parameter is not required for updating or deleting the rolemapping but providing it reduces the number of API
        calls required.
      - If neither O(cid) nor O(client_id) is specified, a B(realm) role is mapped instead.
  roles:
    description:
      - Roles to be mapped to the user.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        description:
          - Name of the role representation.
          - This parameter is required only when creating or updating the role_representation.
      id:
        type: str
        description:
          - The unique identifier for this role_representation.
          - This parameter is not required for updating or deleting a role_representation but providing it reduces the number
            of API calls required.
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Dušan Marković (@bratwurzt)
"""

EXAMPLES = r"""
- name: Map a realm role to a user, authentication with credentials
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    user_id: user1Id
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Map a client role to a user, authentication with credentials
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    client_id: client1
    user_id: user1Id
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Map a client role to a service account user for a client, authentication with credentials
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    client_id: client1
    service_account_user_client_id: clientIdOfServiceAccount
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Map a client role to a user, authentication with token
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    state: present
    client_id: client1
    target_username: user1
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Unmap client role from a user
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: absent
    client_id: client1
    uid: 70e3ae72-96b6-11e6-9056-9737fd4d0764
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: "Role role1 assigned to user user1."

proposed:
  description: Representation of proposed client role mapping.
  returned: always
  type: dict
  sample: {"clientId": "test"}

existing:
  description:
    - Representation of existing client role mapping.
    - The sample is truncated.
  returned: always
  type: dict
  sample:
    {
      "adminUrl": "http://www.example.com/admin_url",
      "attributes": {
        "request.object.signature.alg": "RS256"
      }
    }

end_state:
  description:
    - Representation of client role mapping after module execution.
    - The sample is truncated.
  returned: on success
  type: dict
  sample:
    {
      "adminUrl": "http://www.example.com/admin_url",
      "attributes": {
        "request.object.signature.alg": "RS256"
      }
    }
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

    roles_spec = dict(
        name=dict(type="str"),
        id=dict(type="str"),
    )

    meta_args = dict(
        state=dict(default="present", choices=["present", "absent"]),
        realm=dict(default="master"),
        uid=dict(type="str"),
        target_username=dict(type="str"),
        service_account_user_client_id=dict(type="str"),
        cid=dict(type="str"),
        client_id=dict(type="str"),
        roles=dict(type="list", elements="dict", options=roles_spec),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [
                ["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"],
                ["uid", "target_username", "service_account_user_client_id"],
            ]
        ),
        required_together=([["auth_username", "auth_password"]]),
        required_by={"refresh_token": "auth_realm"},
    )

    result = dict(changed=False, msg="", diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    state = module.params.get("state")
    cid = module.params.get("cid")
    client_id = module.params.get("client_id")
    uid = module.params.get("uid")
    target_username = module.params.get("target_username")
    service_account_user_client_id = module.params.get("service_account_user_client_id")
    roles = module.params.get("roles")

    # Check the parameters
    if uid is None and target_username is None and service_account_user_client_id is None:
        module.fail_json(
            msg="Either the `target_username`, `uid` or `service_account_user_client_id` has to be specified."
        )

    # Get the potential missing parameters
    if uid is None and service_account_user_client_id is None:
        user_rep = kc.get_user_by_username(username=target_username, realm=realm)
        if user_rep is not None:
            uid = user_rep.get("id")
        else:
            module.fail_json(msg=f"Could not fetch user for username {target_username}:")
    else:
        if uid is None and target_username is None:
            user_rep = kc.get_service_account_user_by_client_id(client_id=service_account_user_client_id, realm=realm)
            if user_rep is not None:
                uid = user_rep["id"]
            else:
                module.fail_json(msg=f"Could not fetch service-account-user for client_id {target_username}:")

    if cid is None and client_id is not None:
        cid = kc.get_client_id(client_id=client_id, realm=realm)
        if cid is None:
            module.fail_json(msg=f"Could not fetch client {client_id}:")
    if roles is None:
        module.exit_json(msg="Nothing to do (no roles specified).")
    else:
        for role_index, role in enumerate(roles, start=0):
            if role.get("name") is None and role.get("id") is None:
                module.fail_json(msg="Either the `name` or `id` has to be specified on each role.")
            # Fetch missing role_id
            if role.get("id") is None:
                if cid is None:
                    role_id = kc.get_realm_role(name=role.get("name"), realm=realm)["id"]
                else:
                    role_id = kc.get_client_role_id_by_name(cid=cid, name=role.get("name"), realm=realm)
                if role_id is not None:
                    role["id"] = role_id
                else:
                    module.fail_json(
                        msg=f"Could not fetch role {role.get('name')} for client_id {client_id} or realm {realm}"
                    )
            # Fetch missing role_name
            else:
                if cid is None:
                    role["name"] = kc.get_realm_user_rolemapping_by_id(uid=uid, rid=role.get("id"), realm=realm)["name"]
                else:
                    role["name"] = kc.get_client_user_rolemapping_by_id(
                        uid=uid, cid=cid, rid=role.get("id"), realm=realm
                    )["name"]
                if role.get("name") is None:
                    module.fail_json(
                        msg=f"Could not fetch role {role.get('id')} for client_id {client_id} or realm {realm}"
                    )

    # Get effective role mappings
    if cid is None:
        available_roles_before = kc.get_realm_user_available_rolemappings(uid=uid, realm=realm)
        assigned_roles_before = kc.get_realm_user_composite_rolemappings(uid=uid, realm=realm)
    else:
        available_roles_before = kc.get_client_user_available_rolemappings(uid=uid, cid=cid, realm=realm)
        assigned_roles_before = kc.get_client_user_composite_rolemappings(uid=uid, cid=cid, realm=realm)

    result["existing"] = assigned_roles_before
    result["proposed"] = roles

    update_roles = []
    for role_index, role in enumerate(roles, start=0):
        # Fetch roles to assign if state present
        if state == "present":
            for available_role in available_roles_before:
                if role.get("name") == available_role.get("name"):
                    update_roles.append(
                        {
                            "id": role.get("id"),
                            "name": role.get("name"),
                        }
                    )
        # Fetch roles to remove if state absent
        else:
            for assigned_role in assigned_roles_before:
                if role.get("name") == assigned_role.get("name"):
                    update_roles.append(
                        {
                            "id": role.get("id"),
                            "name": role.get("name"),
                        }
                    )

    if len(update_roles):
        if state == "present":
            # Assign roles
            result["changed"] = True
            if module._diff:
                result["diff"] = dict(before={"roles": assigned_roles_before}, after={"roles": update_roles})
            if module.check_mode:
                module.exit_json(**result)
            kc.add_user_rolemapping(uid=uid, cid=cid, role_rep=update_roles, realm=realm)
            result["msg"] = f"Roles {update_roles} assigned to userId {uid}."
            if cid is None:
                assigned_roles_after = kc.get_realm_user_composite_rolemappings(uid=uid, realm=realm)
            else:
                assigned_roles_after = kc.get_client_user_composite_rolemappings(uid=uid, cid=cid, realm=realm)
            result["end_state"] = assigned_roles_after
            module.exit_json(**result)
        else:
            # Remove mapping of role
            result["changed"] = True
            if module._diff:
                result["diff"] = dict(before={"roles": assigned_roles_before}, after={"roles": update_roles})
            if module.check_mode:
                module.exit_json(**result)
            kc.delete_user_rolemapping(uid=uid, cid=cid, role_rep=update_roles, realm=realm)
            result["msg"] = f"Roles {update_roles} removed from userId {uid}."
            if cid is None:
                assigned_roles_after = kc.get_realm_user_composite_rolemappings(uid=uid, realm=realm)
            else:
                assigned_roles_after = kc.get_client_user_composite_rolemappings(uid=uid, cid=cid, realm=realm)
            result["end_state"] = assigned_roles_after
            module.exit_json(**result)
    # Do nothing
    else:
        result["changed"] = False
        result["msg"] = f"Nothing to do, roles {roles} are correctly mapped to user for username {target_username}."
        module.exit_json(**result)


if __name__ == "__main__":
    main()

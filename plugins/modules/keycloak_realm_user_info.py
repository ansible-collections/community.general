#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_realm_rolemapping

short_description: Allows administration of Keycloak realm role mappings into groups with the Keycloak API

version_added: 8.2.0

description:
  - This module allows you to add, remove or modify Keycloak realm role mappings into groups with the Keycloak REST API. It
    requires access to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite
    access rights. In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client
    definition with the scope tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/18.0/rest-api/index.html).
  - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and are returned that way
    by this module. You may pass single values for attributes when calling the module, and this is translated into a list
    suitable for the API.
  - When updating a group_rolemapping, where possible provide the role ID to the module. This removes a lookup to the API
    to translate the name into the role ID.
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
      - State of the realm_rolemapping.
      - On C(present), the realm_rolemapping is created if it does not yet exist, or updated with the parameters you provide.
      - On C(absent), the realm_rolemapping is removed if it exists.
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

  group_name:
    type: str
    description:
      - Name of the group to be mapped.
      - This parameter is required (can be replaced by gid for less API call).
  parents:
    type: list
    description:
      - List of parent groups for the group to handle sorted top to bottom.
      - Set this if your group is a subgroup and you do not provide the GID in O(gid).
    elements: dict
    suboptions:
      id:
        type: str
        description:
          - Identify parent by ID.
          - Needs less API calls than using O(parents[].name).
          - A deep parent chain can be started at any point when first given parent is given as ID.
          - Note that in principle both ID and name can be specified at the same time but current implementation only always
            use just one of them, with ID being preferred.
      name:
        type: str
        description:
          - Identify parent by name.
          - Needs more internal API calls than using O(parents[].id) to map names to ID's under the hood.
          - When giving a parent chain with only names it must be complete up to the top.
          - Note that in principle both ID and name can be specified at the same time but current implementation only always
            use just one of them, with ID being preferred.
  gid:
    type: str
    description:
      - ID of the group to be mapped.
      - This parameter is not required for updating or deleting the rolemapping but providing it reduces the number of API
        calls required.
  roles:
    description:
      - Roles to be mapped to the group.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        description:
          - Name of the role_representation.
          - This parameter is required only when creating or updating the role_representation.
      id:
        type: str
        description:
          - The unique identifier for this role_representation.
          - This parameter is not required for updating or deleting a role_representation but providing it reduces the number
            of API calls required.
extends_documentation_fragment:
  - community.general._keycloak
  - community.general._keycloak.actiongroup_keycloak
  - community.general._attributes

author:
  - Gaëtan Daubresse (@Gaetan2907)
  - Marius Huysamen (@mhuysamen)
  - Alexander Groß (@agross)
"""

EXAMPLES = r"""
- name: Map a client role to a group, authentication with credentials
  community.general.keycloak_realm_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    group_name: group1
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Map a client role to a group, authentication with token
  community.general.keycloak_realm_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    state: present
    group_name: group1
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Map a client role to a subgroup, authentication with token
  community.general.keycloak_realm_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    state: present
    group_name: subgroup1
    parents:
      - name: parent-group
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

- name: Unmap realm role from a group
  community.general.keycloak_realm_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: absent
    group_name: group1
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
  sample: "Role role1 assigned to group group1."

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

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._keycloak import (
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
        realm=dict(default="master"),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"]]
        ),
        required_together=([["auth_username", "auth_password"]]),
        required_by={"refresh_token": "auth_realm"},
    )

    result = dict(changed=False, msg="", users="")

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")

    users = kc.get_realm_users(realm=realm)

    result["users"] = users
    result["msg"] = f"Got users in realm {realm}"
    module.exit_json(**result)


if __name__ == "__main__":
    main()

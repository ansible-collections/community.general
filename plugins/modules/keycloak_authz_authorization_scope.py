#!/usr/bin/python

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_authz_authorization_scope

short_description: Allows administration of Keycloak client authorization scopes using Keycloak API

version_added: 6.6.0

description:
  - This module allows the administration of Keycloak client Authorization Scopes using the Keycloak REST API. Authorization
    Scopes are only available if a client has Authorization enabled.
  - This module requires access to the REST API using OpenID Connect; the user connecting and the realm being used must have
    the requisite access rights. In a default Keycloak installation, admin-cli and an admin user would work, as would a separate
    realm definition with the scope tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase options used by Keycloak. The Authorization Services
    paths and payloads have not officially been documented by the Keycloak project.
    U(https://www.puppeteers.net/blog/keycloak-authorization-services-rest-api-paths-and-payload/).
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
      - State of the authorization scope.
      - On V(present), the authorization scope is created (or updated if it exists already).
      - On V(absent), the authorization scope is removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  name:
    description:
      - Name of the authorization scope to create.
    type: str
    required: true
  display_name:
    description:
      - The display name of the authorization scope.
    type: str
  icon_uri:
    description:
      - The icon URI for the authorization scope.
    type: str
  client_id:
    description:
      - The C(clientId) of the Keycloak client that should have the authorization scope.
      - This is usually a human-readable name of the Keycloak client.
    type: str
    required: true
  realm:
    description:
      - The name of the Keycloak realm the Keycloak client is in.
    type: str
    required: true

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Samuli Seppänen (@mattock)
"""

EXAMPLES = r"""
- name: Manage Keycloak file:delete authorization scope
  keycloak_authz_authorization_scope:
    name: file:delete
    state: present
    display_name: File delete
    client_id: myclient
    realm: myrealm
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str

end_state:
  description: Representation of the authorization scope after module execution.
  returned: on success
  type: complex
  contains:
    id:
      description: ID of the authorization scope.
      type: str
      returned: when O(state=present)
      sample: a6ab1cf2-1001-40ec-9f39-48f23b6a0a41
    name:
      description: Name of the authorization scope.
      type: str
      returned: when O(state=present)
      sample: file:delete
    display_name:
      description: Display name of the authorization scope.
      type: str
      returned: when O(state=present)
      sample: File delete
    icon_uri:
      description: Icon URI for the authorization scope.
      type: str
      returned: when O(state=present)
      sample: http://localhost/icon.png
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        name=dict(type="str", required=True),
        display_name=dict(type="str"),
        icon_uri=dict(type="str"),
        client_id=dict(type="str", required=True),
        realm=dict(type="str", required=True),
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

    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Convenience variables
    state = module.params.get("state")
    name = module.params.get("name")
    display_name = module.params.get("display_name")
    icon_uri = module.params.get("icon_uri")
    client_id = module.params.get("client_id")
    realm = module.params.get("realm")

    # Get the "id" of the client based on the usually more human-readable
    # "clientId"
    cid = kc.get_client_id(client_id, realm=realm)
    if not cid:
        module.fail_json(msg=f"Invalid client {client_id} for realm {realm}")

    # Get current state of the Authorization Scope using its name as the search
    # filter. This returns False if it is not found.
    before_authz_scope = kc.get_authz_authorization_scope_by_name(name=name, client_id=cid, realm=realm)

    # Generate a JSON payload for Keycloak Admin API. This is needed for
    # "create" and "update" operations.
    desired_authz_scope = {}
    desired_authz_scope["name"] = name
    desired_authz_scope["displayName"] = display_name
    desired_authz_scope["iconUri"] = icon_uri

    # Add "id" to payload for modify operations
    if before_authz_scope:
        desired_authz_scope["id"] = before_authz_scope["id"]

    # Ensure that undefined (null) optional parameters are presented as empty
    # strings in the desired state. This makes comparisons with current state
    # much easier.
    for k, v in desired_authz_scope.items():
        if not v:
            desired_authz_scope[k] = ""

    # Do the above for the current state
    if before_authz_scope:
        for k in ["displayName", "iconUri"]:
            if k not in before_authz_scope:
                before_authz_scope[k] = ""

    if before_authz_scope and state == "present":
        changes = False
        for k, v in desired_authz_scope.items():
            if before_authz_scope[k] != v:
                changes = True
                # At this point we know we have to update the object anyways,
                # so there's no need to do more work.
                break

        if changes:
            if module._diff:
                result["diff"] = dict(before=before_authz_scope, after=desired_authz_scope)

            if module.check_mode:
                result["changed"] = True
                result["msg"] = "Authorization scope would be updated"
                module.exit_json(**result)
            else:
                kc.update_authz_authorization_scope(
                    payload=desired_authz_scope, id=before_authz_scope["id"], client_id=cid, realm=realm
                )
                result["changed"] = True
                result["msg"] = "Authorization scope updated"
        else:
            result["changed"] = False
            result["msg"] = "Authorization scope not updated"

        result["end_state"] = desired_authz_scope
    elif not before_authz_scope and state == "present":
        if module._diff:
            result["diff"] = dict(before={}, after=desired_authz_scope)

        if module.check_mode:
            result["changed"] = True
            result["msg"] = "Authorization scope would be created"
            module.exit_json(**result)
        else:
            kc.create_authz_authorization_scope(payload=desired_authz_scope, client_id=cid, realm=realm)
            result["changed"] = True
            result["msg"] = "Authorization scope created"
            result["end_state"] = desired_authz_scope
    elif before_authz_scope and state == "absent":
        if module._diff:
            result["diff"] = dict(before=before_authz_scope, after={})

        if module.check_mode:
            result["changed"] = True
            result["msg"] = "Authorization scope would be removed"
            module.exit_json(**result)
        else:
            kc.remove_authz_authorization_scope(id=before_authz_scope["id"], client_id=cid, realm=realm)
            result["changed"] = True
            result["msg"] = "Authorization scope removed"
    elif not before_authz_scope and state == "absent":
        result["changed"] = False
    else:
        module.fail_json(
            msg=f"Unable to determine what to do with authorization scope {name} of client {client_id} in realm {realm}"
        )

    module.exit_json(**result)


if __name__ == "__main__":
    main()

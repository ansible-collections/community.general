#!/usr/bin/python

# Copyright (c) 2025, mariusbertram <marius@brtrm.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_user_execute_actions_email

short_description: Send a Keycloak execute-actions email to a user

version_added: 12.0.0

description:
  - Triggers the Keycloak endpoint C(execute-actions-email) for a user.
    This sends an email with one or more required actions the user must complete (for example resetting the password).
  - If no O(actions) list is provided, the default action C(UPDATE_PASSWORD) is used.
  - You must supply either the user's O(id) or O(username). Supplying only C(username) causes an extra lookup call.
  - This module always reports C(changed=true) because sending an email is a side effect and cannot be made idempotent.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  auth_username:
    aliases: []
  realm:
    description:
      - The Keycloak realm where the user resides.
    type: str
    default: master
  id:
    description:
      - The unique ID (UUID) of the user.
      - Mutually exclusive with O(username).
    type: str
  username:
    description:
      - Username of the user.
      - Mutually exclusive with O(id).
    type: str
  actions:
    description:
      - List of required actions to include in the email.
    type: list
    elements: str
    default:
      - UPDATE_PASSWORD
  client_id:
    description:
      - Optional client ID used for the redirect link.
    aliases: [clientId]
    type: str
  redirect_uri:
    description:
      - Optional redirect URI. Must be valid for the given client if O(client_id) is set.
    aliases: [redirectUri]
    type: str
  lifespan:
    description:
      - Optional lifespan (in seconds) for the action token (supported on newer Keycloak versions). Forwarded as query parameter if provided.
    type: int
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes
author:
  - Marius Bertram (@mariusbertram)
"""

EXAMPLES = r"""
- name: Password reset email (default action) with 1h lifespan
  community.general.keycloak_user_execute_actions_email:
    username: johndoe
    realm: MyRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: ADMIN
    auth_password: SECRET
    lifespan: 3600
  delegate_to: localhost

- name: Multiple required actions using token auth
  community.general.keycloak_user_execute_actions_email:
    username: johndoe
    actions:
      - UPDATE_PASSWORD
      - VERIFY_EMAIL
    realm: MyRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Email by user id with redirect
  community.general.keycloak_user_execute_actions_email:
    id: 9d59aa76-2755-48c6-b1af-beb70a82c3cd
    client_id: my-frontend
    redirect_uri: https://app.example.com/post-actions
    actions:
      - UPDATE_PASSWORD
    realm: MyRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: ADMIN
    auth_password: SECRET
  delegate_to: localhost
"""

RETURN = r"""
user_id:
  description: The user ID the email was (or would be, in check mode) sent to.
  returned: success
  type: str
actions:
  description: List of actions included in the email.
  returned: success
  type: list
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    keycloak_argument_spec,
    get_token,
    KeycloakError,
    KeycloakAPI,
)


def main():
    argument_spec = keycloak_argument_spec()
    # Avoid alias collision as in keycloak_user: clear auth_username aliases locally
    argument_spec["auth_username"]["aliases"] = []

    meta_args = dict(
        realm=dict(type="str", default="master"),
        id=dict(type="str"),
        username=dict(type="str"),
        actions=dict(type="list", elements="str", default=["UPDATE_PASSWORD"]),
        client_id=dict(type="str", aliases=["clientId"]),
        redirect_uri=dict(type="str", aliases=["redirectUri"]),
        lifespan=dict(type="int"),
    )
    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["id", "username"]],
        mutually_exclusive=[["id", "username"]],
    )

    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    user_id = module.params.get("id")
    username = module.params.get("username")
    actions = module.params.get("actions")
    client_id = module.params.get("client_id")
    redirect_uri = module.params.get("redirect_uri")
    lifespan = module.params.get("lifespan")

    # Resolve user ID if only username is provided
    if user_id is None:
        user_obj = kc.get_user_by_username(username=username, realm=realm)
        if user_obj is None:
            module.fail_json(msg=f"User '{username}' not found in realm {realm}")
        user_id = user_obj["id"]

    if module.check_mode:
        module.exit_json(
            changed=True, msg=f"Would send execute-actions email to user {user_id}", user_id=user_id, actions=actions
        )

    try:
        kc.send_execute_actions_email(
            user_id=user_id,
            realm=realm,
            client_id=client_id,
            data=actions,
            redirect_uri=redirect_uri,
            lifespan=lifespan,
        )
    except Exception as e:
        module.fail_json(msg=str(e))

    module.exit_json(
        changed=True, msg=f"Execute-actions email sent to user {user_id}", user_id=user_id, actions=actions
    )


if __name__ == "__main__":
    main()

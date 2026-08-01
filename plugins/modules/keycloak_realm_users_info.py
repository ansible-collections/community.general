#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_realm_users_info

short_description: Retrieve users from a Keycloak realm using the Keycloak API

version_added: 13.1.0

description:
  - This module retrieves all users from a specified Keycloak realm using the Keycloak REST API.
  - Access to the REST API is performed via OpenID Connect. The user and client used must have the necessary permissions.
  - Authentication can be performed either with username/password or with a token.
  - The names of module options are snake_case versions of the camelCase ones found in the Keycloak API
    and its documentation at U(https://www.keycloak.org/docs-api/18.0/rest-api/index.html).

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  realm:
    type: str
    description:
      - The Keycloak realm from which users should be retrieved.
    default: 'master'

extends_documentation_fragment:
  - community.general._keycloak
  - community.general._keycloak.actiongroup_keycloak
  - community.general._attributes
  - community.general._attributes.info_module

author:
  - Felix Grzelka (@felix-grzelka)
"""

EXAMPLES = r"""
- name: List all users in the "MyCustomRealm" realm using username/password authentication
  community.general.keycloak_realm_users_info:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: List all users in the "MyCustomRealm" realm using a token
  community.general.keycloak_realm_users_info:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost
"""

RETURN = r"""
users:
  description: List of users in the specified realm.
  returned: always
  type: list
  elements: dict
  sample:
    - id: "1234-5678-90"
      username: "user1"
      email: "user1@example.com"
    - id: "2345-6789-01"
      username: "user2"
      email: "user2@example.com"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._keycloak import (
    KeycloakAPI,
    KeycloakError,
    get_token,
    keycloak_argument_spec,
)


def main():
    argument_spec = keycloak_argument_spec()

    argument_spec["realm"] = dict(default="master")

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

    result["users"] = kc.get_realm_users(realm=realm)
    module.exit_json(**result)


if __name__ == "__main__":
    main()

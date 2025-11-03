#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: keycloak_realm_keys_metadata_info

short_description: Allows obtaining Keycloak realm keys metadata using Keycloak API

version_added: 9.3.0

description:
  - This module allows you to get Keycloak realm keys metadata using the Keycloak REST API.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/latest/rest-api/index.html).
attributes:
  action_group:
    version_added: 10.2.0

options:
  realm:
    type: str
    description:
      - They Keycloak realm to fetch keys metadata.
    default: 'master'

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes
  - community.general.attributes.info_module

author:
  - Thomas Bach (@thomasbach-dev)
"""

EXAMPLES = r"""
- name: Fetch Keys metadata
  community.general.keycloak_realm_keys_metadata_info:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: MyCustomRealm
  delegate_to: localhost
  register: keycloak_keys_metadata

- name: Write the Keycloak keys certificate into a file
  ansible.builtin.copy:
    dest: /tmp/keycloak.cert
    content: |
      {{ keys_metadata['keycloak_keys_metadata']['keys']
      | selectattr('algorithm', 'equalto', 'RS256')
      | map(attribute='certificate')
      | first
      }}
  delegate_to: localhost
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str

keys_metadata:
  description:

    - Representation of the realm keys metadata (see U(https://www.keycloak.org/docs-api/latest/rest-api/index.html#KeysMetadataRepresentation)).
  returned: always
  type: dict
  contains:
    active:
      description: A mapping (that is, a dict) from key algorithms to UUIDs.
      type: dict
      returned: always
    keys:
      description: A list of dicts providing detailed information on the keys.
      type: list
      elements: dict
      returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    KeycloakError,
    get_token,
    keycloak_argument_spec,
)


def main():
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

    result = dict(changed=False, msg="", keys_metadata="")

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")

    keys_metadata = kc.get_realm_keys_metadata_by_id(realm=realm)

    result["keys_metadata"] = keys_metadata
    result["msg"] = f"Get realm keys metadata successful for ID {realm}"
    module.exit_json(**result)


if __name__ == "__main__":
    main()

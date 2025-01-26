#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_authz_permission_info

version_added: 7.2.0

short_description: Query Keycloak client authorization permissions information

description:
  - This module allows querying information about Keycloak client authorization permissions from the resources endpoint using
    the Keycloak REST API. Authorization permissions are only available if a client has Authorization enabled.
  - This module requires access to the REST API using OpenID Connect; the user connecting and the realm being used must have
    the requisite access rights. In a default Keycloak installation, admin-cli and an admin user would work, as would a separate
    realm definition with the scope tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase options used by Keycloak. The Authorization Services
    paths and payloads have not officially been documented by the Keycloak project.
    U(https://www.puppeteers.net/blog/keycloak-authorization-services-rest-api-paths-and-payload/).
attributes:
  action_group:
    version_added: 10.2.0

options:
  name:
    description:
      - Name of the authorization permission to create.
    type: str
    required: true
  client_id:
    description:
      - The clientId of the keycloak client that should have the authorization scope.
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
  - community.general.attributes.info_module

author:
  - Samuli Seppänen (@mattock)
"""

EXAMPLES = r"""
- name: Query Keycloak authorization permission
  community.general.keycloak_authz_permission_info:
    name: ScopePermission
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

queried_state:
  description: State of the resource (a policy) as seen by Keycloak.
  returned: on success
  type: complex
  contains:
    id:
      description: ID of the authorization permission.
      type: str
      sample: 9da05cd2-b273-4354-bbd8-0c133918a454
    name:
      description: Name of the authorization permission.
      type: str
      sample: ResourcePermission
    description:
      description: Description of the authorization permission.
      type: str
      sample: Resource Permission
    type:
      description: Type of the authorization permission.
      type: str
      sample: resource
    decisionStrategy:
      description: The decision strategy.
      type: str
      sample: UNANIMOUS
    logic:
      description: The logic used for the permission (part of the payload, but has a fixed value).
      type: str
      sample: POSITIVE
    config:
      description: Configuration of the permission (empty in all observed cases).
      type: dict
      sample: {}
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        name=dict(type='str', required=True),
        client_id=dict(type='str', required=True),
        realm=dict(type='str', required=True)
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=(
                               [['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]),
                           required_by={'refresh_token': 'auth_realm'},
                           )

    # Convenience variables
    name = module.params.get('name')
    client_id = module.params.get('client_id')
    realm = module.params.get('realm')

    result = dict(changed=False, msg='', queried_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Get id of the client based on client_id
    cid = kc.get_client_id(client_id, realm=realm)
    if not cid:
        module.fail_json(msg='Invalid client %s for realm %s' %
                         (client_id, realm))

    # Get current state of the permission using its name as the search
    # filter. This returns False if it is not found.
    permission = kc.get_authz_permission_by_name(
        name=name, client_id=cid, realm=realm)

    result['queried_state'] = permission

    module.exit_json(**result)


if __name__ == '__main__':
    main()

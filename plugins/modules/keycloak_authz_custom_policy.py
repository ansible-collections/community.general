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
module: keycloak_authz_custom_policy

short_description: Allows administration of Keycloak client custom Javascript policies using Keycloak API

version_added: 7.5.0

description:
  - This module allows the administration of Keycloak client custom Javascript using the Keycloak REST API. Custom Javascript
    policies are only available if a client has Authorization enabled and if they have been deployed to the Keycloak server
    as JAR files.
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
    support: none
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the custom policy.
      - On V(present), the custom policy is created (or updated if it exists already).
      - On V(absent), the custom policy is removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  name:
    description:
      - Name of the custom policy to create.
    type: str
    required: true
  policy_type:
    description:
      - The type of the policy. This must match the name of the custom policy deployed to the server.
      - Multiple policies pointing to the same policy type can be created, but their names have to differ.
    type: str
    required: true
  client_id:
    description:
      - The V(clientId) of the Keycloak client that should have the custom policy attached to it.
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
- name: Manage Keycloak custom authorization policy
  community.general.keycloak_authz_custom_policy:
    name: OnlyOwner
    state: present
    policy_type: script-policy.js
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
  description: Representation of the custom policy after module execution.
  returned: on success
  type: dict
  contains:
    name:
      description: Name of the custom policy.
      type: str
      returned: when I(state=present)
      sample: file:delete
    policy_type:
      description: Type of custom policy.
      type: str
      returned: when I(state=present)
      sample: File delete
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
        state=dict(type='str', default='present',
                   choices=['present', 'absent']),
        name=dict(type='str', required=True),
        policy_type=dict(type='str', required=True),
        client_id=dict(type='str', required=True),
        realm=dict(type='str', required=True)
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=(
                               [['token', 'auth_realm', 'auth_username', 'auth_password', 'auth_client_id', 'auth_client_secret']]),
                           required_together=([['auth_username', 'auth_password']]),
                           required_by={'refresh_token': 'auth_realm'},
                           )

    result = dict(changed=False, msg='', end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Convenience variables
    state = module.params.get('state')
    name = module.params.get('name')
    policy_type = module.params.get('policy_type')
    client_id = module.params.get('client_id')
    realm = module.params.get('realm')

    cid = kc.get_client_id(client_id, realm=realm)
    if not cid:
        module.fail_json(msg='Invalid client %s for realm %s' %
                         (client_id, realm))

    before_authz_custom_policy = kc.get_authz_policy_by_name(
        name=name, client_id=cid, realm=realm)

    desired_authz_custom_policy = {}
    desired_authz_custom_policy['name'] = name
    desired_authz_custom_policy['type'] = policy_type

    # Modifying existing custom policies is not possible
    if before_authz_custom_policy and state == 'present':
        result['msg'] = "Custom policy %s already exists" % (name)
        result['changed'] = False
        result['end_state'] = desired_authz_custom_policy
    elif not before_authz_custom_policy and state == 'present':
        if module.check_mode:
            result['msg'] = "Would create custom policy %s" % (name)
        else:
            kc.create_authz_custom_policy(
                payload=desired_authz_custom_policy, policy_type=policy_type, client_id=cid, realm=realm)
            result['msg'] = "Custom policy %s created" % (name)

        result['changed'] = True
        result['end_state'] = desired_authz_custom_policy
    elif before_authz_custom_policy and state == 'absent':
        if module.check_mode:
            result['msg'] = "Would remove custom policy %s" % (name)
        else:
            kc.remove_authz_custom_policy(
                policy_id=before_authz_custom_policy['id'], client_id=cid, realm=realm)
            result['msg'] = "Custom policy %s removed" % (name)

        result['changed'] = True
        result['end_state'] = {}
    elif not before_authz_custom_policy and state == 'absent':
        result['msg'] = "Custom policy %s does not exist" % (name)
        result['changed'] = False
        result['end_state'] = {}

    module.exit_json(**result)


if __name__ == '__main__':
    main()

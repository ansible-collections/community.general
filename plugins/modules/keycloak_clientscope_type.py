#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_clientscope_type

short_description: Set the type of aclientscope in realm or client using Keycloak API

version_added: 6.6.0

description:
  - This module allows you to set the type (optional, default) of clientscopes using the Keycloak REST API. It requires access
    to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with
    the scope tailored to your needs and a user having the expected roles.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 10.2.0

options:
  realm:
    type: str
    description:
      - The Keycloak realm.
    default: 'master'

  client_id:
    description:
      - The O(client_id) of the client. If not set the clientscope types are set as a default for the realm.
    aliases:
      - clientId
    type: str

  default_clientscopes:
    description:
      - Client scopes that should be of type default.
    type: list
    elements: str

  optional_clientscopes:
    description:
      - Client scopes that should be of type optional.
    type: list
    elements: str

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Simon Pahl (@simonpahl)
"""

EXAMPLES = r"""
- name: Set default client scopes on realm level
  community.general.keycloak_clientscope_type:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: "MyCustomRealm"
    default_clientscopes: ['profile', 'roles']
  delegate_to: localhost


- name: Set default and optional client scopes on client level with token auth
  community.general.keycloak_clientscope_type:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    realm: "MyCustomRealm"
    client_id: "MyCustomClient"
    default_clientscopes: ['profile', 'roles']
    optional_clientscopes: ['phone']
  delegate_to: localhost
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: ""
proposed:
  description: Representation of proposed client-scope types mapping.
  returned: always
  type: dict
  sample:
    {
      "default_clientscopes": [
        "profile",
        "role"
      ],
      "optional_clientscopes": []
    }
existing:
  description:
    - Representation of client scopes before module execution.
  returned: always
  type: dict
  sample:
    {
      "default_clientscopes": [
        "profile",
        "role"
      ],
      "optional_clientscopes": [
        "phone"
      ]
    }
end_state:
  description:
    - Representation of client scopes after module execution.
    - The sample is truncated.
  returned: on success
  type: dict
  sample:
    {
      "default_clientscopes": [
        "profile",
        "role"
      ],
      "optional_clientscopes": []
    }
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI, KeycloakError, get_token)

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import \
    keycloak_argument_spec


def keycloak_clientscope_type_module():
    """
    Returns an AnsibleModule definition.

    :return: argument_spec dict
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        realm=dict(default='master'),
        client_id=dict(type='str', aliases=['clientId']),
        default_clientscopes=dict(type='list', elements='str'),
        optional_clientscopes=dict(type='list', elements='str'),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=([
            ['token', 'auth_realm', 'auth_username', 'auth_password', 'auth_client_id', 'auth_client_secret'],
            ['default_clientscopes', 'optional_clientscopes']
        ]),
        required_together=([['auth_username', 'auth_password']]),
        required_by={'refresh_token': 'auth_realm'},
        mutually_exclusive=[
            ['token', 'auth_realm'],
            ['token', 'auth_username'],
            ['token', 'auth_password']
        ],
    )

    return module


def clientscopes_to_add(existing, proposed):
    to_add = []
    existing_clientscope_ids = extract_field(existing, 'id')
    for clientscope in proposed:
        if not clientscope['id'] in existing_clientscope_ids:
            to_add.append(clientscope)
    return to_add


def clientscopes_to_delete(existing, proposed):
    to_delete = []
    proposed_clientscope_ids = extract_field(proposed, 'id')
    for clientscope in existing:
        if not clientscope['id'] in proposed_clientscope_ids:
            to_delete.append(clientscope)
    return to_delete


def extract_field(dictionary, field='name'):
    return [cs[field] for cs in dictionary]


def normalize_scopes(scopes):
    scopes_copy = scopes.copy()
    if isinstance(scopes_copy.get('default_clientscopes'), list):
        scopes_copy['default_clientscopes'] = sorted(scopes_copy['default_clientscopes'])
    if isinstance(scopes_copy.get('optional_clientscopes'), list):
        scopes_copy['optional_clientscopes'] = sorted(scopes_copy['optional_clientscopes'])
    return scopes_copy


def main():
    """
    Module keycloak_clientscope_type

    :return:
    """

    module = keycloak_clientscope_type_module()

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    client_id = module.params.get('client_id')
    default_clientscopes = module.params.get('default_clientscopes')
    optional_clientscopes = module.params.get('optional_clientscopes')

    result = dict(changed=False, msg='', proposed={}, existing={}, end_state={})

    all_clientscopes = kc.get_clientscopes(realm)
    default_clientscopes_real = []
    optional_clientscopes_real = []

    for client_scope in all_clientscopes:
        if default_clientscopes is not None and client_scope["name"] in default_clientscopes:
            default_clientscopes_real.append(client_scope)
        if optional_clientscopes is not None and client_scope["name"] in optional_clientscopes:
            optional_clientscopes_real.append(client_scope)

    if default_clientscopes is not None and len(default_clientscopes_real) != len(default_clientscopes):
        module.fail_json(msg='At least one of the default_clientscopes does not exist!')

    if optional_clientscopes is not None and len(optional_clientscopes_real) != len(optional_clientscopes):
        module.fail_json(msg='At least one of the optional_clientscopes does not exist!')

    result['proposed'].update({
        'default_clientscopes': 'no-change' if default_clientscopes is None else default_clientscopes,
        'optional_clientscopes': 'no-change' if optional_clientscopes is None else optional_clientscopes
    })

    default_clientscopes_existing = kc.get_default_clientscopes(realm, client_id)
    optional_clientscopes_existing = kc.get_optional_clientscopes(realm, client_id)

    result['existing'].update({
        'default_clientscopes': extract_field(default_clientscopes_existing),
        'optional_clientscopes': extract_field(optional_clientscopes_existing)
    })

    if module._diff:
        result['diff'] = dict(before=normalize_scopes(result['existing']), after=normalize_scopes(result['proposed']))

    default_clientscopes_add = clientscopes_to_add(default_clientscopes_existing, default_clientscopes_real)
    optional_clientscopes_add = clientscopes_to_add(optional_clientscopes_existing, optional_clientscopes_real)

    default_clientscopes_delete = clientscopes_to_delete(default_clientscopes_existing, default_clientscopes_real)
    optional_clientscopes_delete = clientscopes_to_delete(optional_clientscopes_existing, optional_clientscopes_real)

    result["changed"] = any(len(x) > 0 for x in [
        default_clientscopes_add, optional_clientscopes_add, default_clientscopes_delete, optional_clientscopes_delete
    ])

    if module.check_mode:
        module.exit_json(**result)

    # first delete so clientscopes can change type
    for clientscope in default_clientscopes_delete:
        kc.delete_default_clientscope(clientscope['id'], realm, client_id)
    for clientscope in optional_clientscopes_delete:
        kc.delete_optional_clientscope(clientscope['id'], realm, client_id)

    for clientscope in default_clientscopes_add:
        kc.add_default_clientscope(clientscope['id'], realm, client_id)
    for clientscope in optional_clientscopes_add:
        kc.add_optional_clientscope(clientscope['id'], realm, client_id)

    result['end_state'].update({
        'default_clientscopes': extract_field(kc.get_default_clientscopes(realm, client_id)),
        'optional_clientscopes': extract_field(kc.get_optional_clientscopes(realm, client_id))
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()

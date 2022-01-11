#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_client_scopemapping

short_description: Allows administration of Keycloak client-level roles of the client's scope via the Keycloak API

version_added: 3.5.0

description:
    - This module allows you to add, remove Keycloak client-level roles scope mapping with the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - When updating a scope mapping, where possible provide the role ID to the module. This removes a lookup
      to the API to translate the name into the role ID.

options:
    state:
        description:
            - State of the client-level role scope mapping.
            - On C(present), the client-level role scope mapping will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the client-level role scope mapping will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent
    realm:
        type: str
        description:
            - They Keycloak realm under which this role representation resides.
        default: 'master'
    client_id:
        type: str
        description:
            - Name of the client to be mapped (different than I(cid)).
            - This parameter is required (can be replaced by cid for less API call).
    id:
        type: str
        description:
            - ID of the client to be mapped.
            - This parameter is not required for updating or deleting the rolemapping but
              providing it will reduce the number of API calls required.
    client_role:
        description: Scope mapping of the client-level role.
        type: dict
        suboptions:
            id:
                description: ID of the client
                type: str
            client_id:
                description: Name of the client
                type: str
            roles:
                description: Client roles
                type: list
                elements: dict
                suboptions:
                    name:
                        description: Name of the role
                        type: str
                    id:
                        description: ID of the role
                        type: str

extends_documentation_fragment:
- community.general.keycloak


author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Map a client role to a client, authentication with credentials
  community.general.keycloak_client_scope_mapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    client_id: client1
    client_role:
        client_id: client2
        roles:
          - name: role_name1
            id: role_id1
          - name: role_name2
            id: role_id2
  delegate_to: localhost

- name: Map a client role to a client, authentication with token
  community.general.keycloak_client_scope_mapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    state: present
    id: 6e1d65de-f01a-4d3a-b7c6-3d581165966f
    client_role:
        id: 6e1d65de-f01a-4d3a-b7c6-3d581165966f
        roles:
          - name: role_name1
            id: role_id1
          - name: role_name2
            id: role_id2
  delegate_to: localhost

- name: Unmap client role from a client
  community.general.keycloak_client_scope_mapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: absent
    id: 6e1d65de-f01a-4d3a-b7c6-3d581165966f
    client_role:
        id: 52c4d786-b790-4570-9fc2-037aee19a2c2
        roles:
          - name: role_name3
            id: role_id3
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str
    sample: "Role role1 assigned to client client1."

proposed:
    description: Representation of proposed client role mapping.
    returned: always
    type: dict
    sample: {
      clientId: "test"
    }

existing:
    description:
      - Representation of existing client role mapping.
      - The sample is truncated.
    returned: always
    type: dict
    sample: {
        "adminUrl": "http://www.example.com/admin_url",
        "attributes": {
            "request.object.signature.alg": "RS256",
        }
    }

end_state:
    description:
      - Representation of client role mapping after module execution.
      - The sample is truncated.
    returned: on success
    type: dict
    sample: {
        "adminUrl": "http://www.example.com/admin_url",
        "attributes": {
            "request.object.signature.alg": "RS256",
        }
    }
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError, is_struct_included
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        client_id=dict(type='str'),
        id=dict(type='str'),
        client_role=dict(
            type='dict',
            options=dict(
                client_id=dict(type='str'),
                id=dict(type='str'),
                roles=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        id=dict(type='str'),
                        name=dict(type='str')
                    ),
                    required_one_of=([['id', 'name']])),
            ),
            required_one_of=([['client_id', 'id']])),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([
                               ['token', 'auth_realm', 'auth_username', 'auth_password'],
                               ['client_id', 'id'],
                           ]),
                           required_together=([
                               ['auth_realm', 'auth_username', 'auth_password']
                           ]))

    result = dict(changed=False, msg='', diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    client_id = module.params.get('client_id')
    cid = module.params.get('id')
    client_role = module.params.get('client_role')

    # Get the potential missing parameters
    if cid is None:
        cid = kc.get_client_id(client_id, realm=realm)
        if cid is None:
            module.fail_json(msg='Could not fetch client %s:' % client_id)

    if not client_role:
        module.exit_json(msg="Nothing to do (no roles specified).")
    if client_role['id'] is None:
        client_role['id'] = kc.get_client_id(client_role['client_id'], realm=realm)
        if client_role['id'] is None:
            module.fail_json(msg='Could not fetch client %s:' % client_role['client_id'])
    if not client_role['roles']:
        module.exit_json(msg="Nothing to do (no roles specified).")
    for role in client_role['roles']:
        if role['id'] is None:
            role['id'] = kc.get_client_role_id_by_name(cid, role['name'], realm=realm)
            if role['id'] is None:
                module.fail_json(msg='Could not fetch role %s:' % (role['name']))
        if role['name'] is None:
            role['name'] = kc.get_client_role_name_by_id(client_role['id'], role['id'], realm=realm)
            if role['name'] is None:
                module.fail_json(msg='Could not fetch role %s:' % (role['id']))

    # Get effective client-level role mappings
    available_roles_before = kc.get_client_scopemappings_client_available(cid, client_role['id'], realm=realm)
    assigned_roles_before = kc.get_client_scopemappings_client_composite(cid, client_role['id'], realm=realm)

    result['existing'] = assigned_roles_before
    result['proposed'] = client_role['roles']

    update_roles = []

    for role in client_role['roles']:
        # Fetch roles to assign if state present
        if state == 'present':
            for available_role in available_roles_before:
                if role['name'] == available_role['name']:
                    update_roles.append({
                        'id': role['id'],
                        'name': role['name'],
                    })
        # Fetch roles to remove if state absent
        else:
            for assigned_role in assigned_roles_before:
                if role['name'] == assigned_role['name']:
                    update_roles.append({
                        'id': role['id'],
                        'name': role['name'],
                    })

    if len(update_roles):
        if state == 'present':
            # Assign roles
            result['changed'] = True
            if module._diff:
                result['diff'] = dict(before=assigned_roles_before, after=update_roles)
            if module.check_mode:
                module.exit_json(**result)
            kc.add_client_scopemappings_client(cid, client_role['id'], update_roles, realm=realm)
            result['msg'] = 'Roles %s from %s assigned to client %s.' % (update_roles, client_role['id'], cid)
            assigned_roles_after = kc.get_client_scopemappings_client_composite(cid, client_role['id'], realm=realm)
            result['end_state'] = assigned_roles_after
            module.exit_json(**result)
        else:
            # Remove mapping of role
            result['changed'] = True
            if module._diff:
                result['diff'] = dict(before=assigned_roles_before, after=update_roles)
            if module.check_mode:
                module.exit_json(**result)
            kc.remove_client_scopemappings_client(cid, client_role['id'], update_roles, realm=realm)
            result['msg'] = 'Roles %s from %s removed from client %s.' % (update_roles, client_role['id'], cid)
            assigned_roles_after = kc.get_client_scopemappings_client_composite(cid, client_role['id'], realm=realm)
            result['end_state'] = assigned_roles_after
            module.exit_json(**result)
    # Do nothing
    else:
        result['changed'] = False
        result['msg'] = 'Nothing to do, roles %s are correctly mapped with client %s.' % (client_role['roles'], client_role['id'])
        module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

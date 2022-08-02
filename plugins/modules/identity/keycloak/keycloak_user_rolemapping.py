#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_user_rolemapping

short_description: Allows administration of Keycloak user_rolemapping with the Keycloak API

version_added: 5.1.2

description:
    - This module allows you to add, remove or modify Keycloak user_rolemapping with the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When updating a user_rolemapping, where possible provide the role ID to the module. This removes a lookup
      to the API to translate the name into the role ID.


options:
    state:
        description:
            - State of the user_rolemapping.
            - On C(present), the user_rolemapping will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the user_rolemapping will be removed if it exists.
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

    username:
        type: str
        description:
            - Username of the user to be mapped.
            - This parameter is required (can be replaced by uid for less API call).

    uid:
        type: str
        description:
            - Id of the user to be mapped.
            - This parameter is not required for updating or deleting the rolemapping but
              providing it will reduce the number of API calls required.

    service_account_user_client_id:
        type: str
        description:
            - client_id of the service-account-user to be mapped.
            - This parameter is not required for updating or deleting the rolemapping but
              providing it will reduce the number of API calls required.    

    client_id:
        type: str
        description:
            - Name of the client to be mapped (different than I(cid)).
            - This parameter is required (can be replaced by cid for less API call).

    cid:
        type: str
        description:
            - Id of the client to be mapped.
            - This parameter is not required for updating or deleting the rolemapping but
              providing it will reduce the number of API calls required.

    roles:
        description:
            - Roles to be mapped to the user.
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
                    - This parameter is not required for updating or deleting a role_representation but
                      providing it will reduce the number of API calls required.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Dušan Marković
'''

EXAMPLES = '''
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

- name: Map a client role to a user, authentication with token
  community.general.keycloak_user_rolemapping:
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
    state: present
    client_id: client1
    username: user1
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
    username: user1
    roles:
      - name: role_name1
        id: role_id1
      - name: role_name2
        id: role_id2
  delegate_to: localhost

'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str
    sample: "Role role1 assigned to user user1."

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

    roles_spec = dict(
        name=dict(type='str'),
        id=dict(type='str'),
    )

    meta_args = dict(
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        uid=dict(type='str'),
        username=dict(type='str'),
        service_account_user_client_id=dict(type='str'),
        cid=dict(type='str'),
        client_id=dict(type='str'),
        roles=dict(type='list', elements='dict', options=roles_spec),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    cid = module.params.get('cid')
    client_id = module.params.get('client_id')
    uid = module.params.get('uid')
    username = module.params.get('username')
    service_account_user_client_id = module.params.get('service_account_user_client_id')
    roles = module.params.get('roles')

    # Check the parameters
    if cid is None and client_id is None:
        module.fail_json(msg='Either the `client_id` or `cid` has to be specified.')
    if uid is None and username is None and service_account_user_client_id is None:
        module.fail_json(msg='Either the `username`, `uid` or `service_account_user_client_id` has to be specified.')

    # Get the potential missing parameters
    if uid is None and service_account_user_client_id is None:
        user_rep = kc.get_user_by_username(username, realm=realm)
        if user_rep is not None:
            uid = user_rep['id']
        else:
            module.fail_json(msg='Could not fetch user for username %s:' % username)
    else:
        if uid is None and username is None:
            user_rep = kc.get_service_account_user_by_client_id(service_account_user_client_id, realm=realm)
            if user_rep is not None:
                uid = user_rep['id']
            else:
                module.fail_json(msg='Could not fetch service-account-user for client_id %s:' % username)
    if cid is None:
        cid = kc.get_client_id(client_id, realm=realm)
        if cid is None:
            module.fail_json(msg='Could not fetch client %s:' % client_id)
    if roles is None:
        module.exit_json(msg="Nothing to do (no roles specified).")
    else:
        for role_index, role in enumerate(roles, start=0):
            if role['name'] is None and role['id'] is None:
                module.fail_json(msg='Either the `name` or `id` has to be specified on each role.')
            # Fetch missing role_id
            if role['id'] is None:
                role_id = kc.get_client_role_by_name(uid, cid, role['name'], realm=realm)
                if role_id is not None:
                    role['id'] = role_id
                else:
                    module.fail_json(msg='Could not fetch role %s for client_id %s' % (role['name'], client_id))
            # Fetch missing role_name
            else:
                role['name'] = kc.get_client_user_rolemapping_by_id(uid, cid, role['id'], realm=realm)['name']
                if role['name'] is None:
                    module.fail_json(msg='Could not fetch role %s for client_id %s' % (role['id'], client_id))

    # Get effective client-level role mappings
    available_roles_before = kc.get_client_user_available_rolemappings(uid, cid, realm=realm)
    assigned_roles_before = kc.get_client_user_composite_rolemappings(uid, cid, realm=realm)

    result['existing'] = assigned_roles_before
    result['proposed'] = roles

    update_roles = []
    for role_index, role in enumerate(roles, start=0):
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
            kc.add_user_rolemapping(uid, cid, update_roles, realm=realm)
            result['msg'] = 'Roles %s assigned to user for username %s.' % (update_roles, username)
            assigned_roles_after = kc.get_client_user_composite_rolemappings(uid, cid, realm=realm)
            result['end_state'] = assigned_roles_after
            module.exit_json(**result)
        else:
            # Remove mapping of role
            result['changed'] = True
            if module._diff:
                result['diff'] = dict(before=assigned_roles_before, after=update_roles)
            if module.check_mode:
                module.exit_json(**result)
            kc.delete_user_rolemapping(uid, cid, update_roles, realm=realm)
            result['msg'] = 'Roles %s removed from user for username %s.' % (update_roles, username)
            assigned_roles_after = kc.get_client_user_composite_rolemappings(uid, cid, realm=realm)
            result['end_state'] = assigned_roles_after
            module.exit_json(**result)
    # Do nothing
    else:
        result['changed'] = False
        result['msg'] = 'Nothing to do, roles %s are correctly mapped to user for username %s.' % (roles, username)
        module.exit_json(**result)


if __name__ == '__main__':
    main()

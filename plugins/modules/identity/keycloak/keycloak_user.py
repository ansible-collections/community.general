#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_user

short_description: Allows administration of Keycloak users via Keycloak API

description:
    - This module allows you to add, remove or modify Keycloak users via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When updating a user, where possible provide the user ID to the module. This removes a lookup
      to the API to translate the username into the user ID.


options:
    state:
        description:
            - State of the user.
            - On C(present), the user will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the user will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    username:
        type: str
        description:
            - Username of the user.
            - This parameter is required only when creating or updating the user.

    realm:
        type: str
        description:
            - They Keycloak realm under which this user resides.
        default: 'master'

    access:
        type: dict
        description:
            - The access.
    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the user.
            - Values may be single values (e.g. a string) or a list of strings.
    client_consents:
        description:
            - The client consents
        aliases:
            - clientConsents
        type: list
        elements: dict
        suboptions:
            client_id:
                description:
                    - The client ID
                aliases:
                    - clientId
                type: str
            granted_client_scopes:
                description:
                    - The granted client scopes
                aliases:
                    - grantedClientScopes
                type: list
                elements: str
    credentials:
        description:
            - The credentials
        type: list
        elements: dict
        suboptions:
            priority:
                description:
                    - The priority
                type: int
            type:
                description:
                    - The type
                type: str
            temporary:
                description:
                    - The temporary
                type: bool
            value:
                description:
                    - The value
                type: str
    disableable_credential_types:
        description:
            - The disableable credential types
        aliases:
            - disableableCredentialTypes
        type: list
        elements: str
    email:
        description:
            - The email
        type: str
    email_verified:
        description:
            - The email verified
        aliases:
            - emailVerified
        type: bool
    enabled:
        description:
            - The enabled
        type: bool
    first_name:
        description:
            - The first name
        aliases:
            - firstName
        type: str
    groups:
        description:
            - The group pathes
        type: list
        elements: str
    id:
        description:
            - The unique identifier for this user.
            - This parameter is not required for updating or deleting a user but
              providing it will reduce the number of API calls required.
        type: str
    last_name:
        description:
            - The last name
        aliases:
            - lastName
        type: str
    not_before:
        description:
            - The not before
        aliases:
            - notBefore
        type: int
    origin:
        description:
            - The origin
        type: str
    realm_roles:
        description:
            - The realm roles
        aliases:
            - realmRoles
        type: list
        elements: str
    required_actions:
        description:
            - The required actions
        aliases:
            - requiredActions
        type: list
        elements: str
    self:
        description:
            - The self
        type: str
    service_account_client_id:
        description:
            - The service account client ID
        aliases:
          - requiredActions
        type: str


extends_documentation_fragment:
- community.general.keycloak

author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Create a Keycloak user, authentication with credentials
  community.general.keycloak_user:
    username: my-new-kc-user
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak user, authentication with token
  community.general.keycloak_user:
    username: my-new-kc-user
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Delete a keycloak user
  community.general.keycloak_user:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    state: absent
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak user based on username
  community.general.keycloak_user:
    username: my-user-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Update the first name of a Keycloak user
  community.general.keycloak_user:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    first_name: an-updated-kc-user-first-name
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a keycloak user with credentials
  community.general.keycloak_user:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    username: my-new_user
    credentials:
      - priority: 0
        type: password
        temporary: false
        value: 'PASSWORD'
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Representation of the user after module execution (sample is truncated).
    returned: on success
    type: complex
    contains:
        id:
            description: GUID that identifies the user.
            type: str
            returned: always
            sample: 23f38145-3195-462c-97e7-97041ccea73e
        username:
            description: Username of the user.
            type: str
            returned: always
            sample: user-test-123
        attributes:
            description: Attributes applied to this user.
            type: dict
            returned: always
            sample:
                attr1: ["val1", "val2", "val3"]

user:
  description:
    - Representation of the user after module execution.
    - Deprecated return value, it will be removed in community.general 6.0.0. Please use the return value I(end_state) instead.
  returned: always
  type: complex
  contains:
    id:
        description: GUID that identifies the user.
        type: str
        returned: always
        sample: 23f38145-3195-462c-97e7-97041ccea73e
    username:
        description: Username of the user.
        type: str
        returned: always
        sample: user-test-123
    attributes:
        description: Attributes applied to this user.
        type: dict
        returned: always
        sample:
            attr1: ["val1", "val2", "val3"]

'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        # Remove alias `username` on `auth_username`
        auth_username=dict(type='str'),

        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),

        username=dict(type='str'),

        access=dict(type='dict'),
        attributes=dict(type='dict'),
        client_consents=dict(type='list', elements='dict',
                             options=dict(
                                 # UserConsentRepresentation
                                 client_id=dict(
                                     type='str', aliases=['clientId']),
                                 granted_client_scopes=dict(
                                     type='list', elements='str', aliases=['grantedClientScopes']),
                             ),
                             aliases=['clientConsents']),
        credentials=dict(type='list', elements='dict',
                         options=dict(
                             # CredentialRepresentation
                             priority=dict(type='int'),
                             type=dict(type='str'),
                             temporary=dict(type='bool'),
                             value=dict(type='str'),
                         )),
        disableable_credential_types=dict(type='list', elements='str', aliases=[
                                          'disableableCredentialTypes']),
        email=dict(type='str'),
        email_verified=dict(type='bool', aliases=['emailVerified']),
        enabled=dict(type='bool'),
        first_name=dict(type='str', aliases=['firstName']),
        groups=dict(type='list', elements='str'),
        id=dict(type='str'),
        last_name=dict(type='str', aliases=['lastName']),
        not_before=dict(type='int', aliases=['notBefore']),
        origin=dict(type='str'),
        realm_roles=dict(type='list', elements='str', aliases=['realmRoles']),
        required_actions=dict(type='list', elements='str',
                              aliases=['requiredActions']),
        self=dict(type='str'),
        service_account_client_id=dict(
            type='str', aliases=['serviceAccountClientId']),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'username'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, user='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    username = module.params.get('username')
    attributes = module.params.get('attributes')

    # attributes in Keycloak have their values returned as lists
    # via the API. attributes is a dict, so we'll transparently convert
    # the values to lists.
    if attributes is not None:
        for key, val in module.params['attributes'].items():
            module.params['attributes'][key] = [
                val] if not isinstance(val, list) else val

    # Filter and map the parameters names that apply to the user
    user_params = [x for x in module.params
                   if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm'] and
                   module.params.get(x) is not None]

    found_users = kc.get_users_by_username(username, realm=realm)

    if found_users is None or found_users == []:
        before_user = {}
    else:
        before_user = found_users[0]

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for param in user_params:
        new_param_value = module.params.get(param)
        old_value = before_user[param] if param in before_user else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_user = before_user.copy()
    desired_user.update(changeset)

    # Cater for when it doesn't exist (an empty dict)
    if not before_user:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['user'] = result['end_state']
            result['msg'] = 'User does not exist; doing nothing.'
            module.exit_json(**result)

        # Process a creation
        result['changed'] = True

        if module._diff:
            result['diff'] = dict(before='', after=desired_user)

        if module.check_mode:
            module.exit_json(**result)

        # create it
        kc.create_user(desired_user, realm=realm)

        after_user = kc.get_users_by_username(username, realm=realm)[0]

        result['end_state'] = after_user
        result['user'] = result['end_state']

        result['msg'] = 'User {username} has been created with ID {id}'.format(username=after_user['username'],
                                                                               id=after_user['id'])
        module.exit_json(**result)

    else:
        if state == 'present':
            # Process an update

            # no changes
            if desired_user == before_user:
                result['changed'] = False
                result['end_state'] = desired_user
                result['user'] = result['end_state']
                result['msg'] = "No changes required to user {username}.".format(
                    username=before_user['username'])
                module.exit_json(**result)

            # doing an update
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_user, after=desired_user)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            kc.update_user(desired_user, realm=realm)

            after_user = kc.get_users_by_username(username, realm=realm)[0]

            result['end_state'] = after_user
            result['user'] = result['end_state']

            result['msg'] = "User {id} has been updated".format(
                id=after_user['id'])
            module.exit_json(**result)

        else:
            # Process a deletion (because state was not 'present')
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_user, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            id = before_user['id']
            kc.delete_user(id=id, realm=realm)

            result['end_state'] = {}
            result['user'] = result['end_state']

            result['msg'] = "User {username} has been deleted".format(
                username=before_user['username'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()

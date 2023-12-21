#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, INSPQ (@elfelip)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: keycloak_user
short_description: Create and configure a user in Keycloak
description:
    - This module creates, removes, or updates Keycloak users.
version_added: 7.1.0
options:
    auth_username:
        aliases: []
    realm:
        description:
            - The name of the realm in which is the client.
        default: master
        type: str
    username:
        description:
            - Username for the user.
        required: true
        type: str
    id:
        description:
            - ID of the user on the Keycloak server if known.
        type: str
    enabled:
        description:
            - Enabled user.
        type: bool
    email_verified:
        description:
            - Check the validity of user email.
        default: false
        type: bool
        aliases:
            - emailVerified
    first_name:
        description:
            - The user's first name.
        required: false
        type: str
        aliases:
            - firstName
    last_name:
        description:
            - The user's last name.
        required: false
        type: str
        aliases:
            - lastName
    email:
        description:
            - User email.
        required: false
        type: str
    federation_link:
        description:
            - Federation Link.
        required: false
        type: str
        aliases:
            - federationLink
    service_account_client_id:
        description:
            - Description of the client Application.
        required: false
        type: str
        aliases:
            - serviceAccountClientId
    client_consents:
        description:
            - Client Authenticator Type.
        type: list
        elements: dict
        default: []
        aliases:
            - clientConsents
        suboptions:
            client_id:
                description:
                    - Client ID of the client role. Not the technical ID of the client.
                type: str
                required: true
                aliases:
                    - clientId
            roles:
                description:
                    - List of client roles to assign to the user.
                type: list
                required: true
                elements: str
    groups:
        description:
            - List of groups for the user.
        type: list
        elements: dict
        default: []
        suboptions:
            name:
                description:
                    - Name of the group.
                type: str
            state:
                description:
                    - Control whether the user must be member of this group or not.
                choices: [ "present", "absent" ]
                default: present
                type: str
    credentials:
        description:
            - User credentials.
        default: []
        type: list
        elements: dict
        suboptions:
            type:
                description:
                    - Credential type.
                type: str
                required: true
            value:
                description:
                    - Value of the credential.
                type: str
                required: true
            temporary:
                description:
                    - If V(true), the users are required to reset their credentials at next login.
                type: bool
                default: false
    required_actions:
        description:
            - RequiredActions user Auth.
        default: []
        type: list
        elements: str
        aliases:
            - requiredActions
    federated_identities:
        description:
            - List of IDPs of user.
        default: []
        type: list
        elements: str
        aliases:
            - federatedIdentities
    attributes:
        description:
            - List of user attributes.
        required: false
        type: list
        elements: dict
        suboptions:
            name:
                description:
                    - Name of the attribute.
                type: str
            values:
                description:
                    - Values for the attribute as list.
                type: list
                elements: str
            state:
                description:
                    - Control whether the attribute must exists or not.
                choices: [ "present", "absent" ]
                default: present
                type: str
    access:
        description:
            - list user access.
        required: false
        type: dict
    disableable_credential_types:
        description:
            - list user Credential Type.
        default: []
        type: list
        elements: str
        aliases:
            - disableableCredentialTypes
    origin:
        description:
            - user origin.
        required: false
        type: str
    self:
        description:
            - user self administration.
        required: false
        type: str
    state:
        description:
            - Control whether the user should exists or not.
        choices: [ "present", "absent" ]
        default: present
        type: str
    force:
        description:
            - If V(true), allows to remove user and recreate it.
        type: bool
        default: false
extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: full
notes:
    - The module does not modify the user ID of an existing user.
author:
    - Philippe Gauthier (@elfelip)
'''

EXAMPLES = '''
- name: Create a user user1
  community.general.keycloak_user:
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: admin
    auth_password: password
    realm: master
    username: user1
    firstName: user1
    lastName: user1
    email: user1
    enabled: true
    emailVerified: false
    credentials:
        - type: password
          value: password
          temporary: false
    attributes:
        - name: attr1
          values:
            - value1
          state: present
        - name: attr2
          values:
            - value2
          state: absent
    groups:
        - name: group1
          state: present
    state: present

- name: Re-create a User
  community.general.keycloak_user:
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: admin
    auth_password: password
    realm: master
    username: user1
    firstName: user1
    lastName: user1
    email: user1
    enabled: true
    emailVerified: false
    credentials:
        - type: password
          value: password
          temporary: false
    attributes:
        - name: attr1
          values:
            - value1
          state: present
        - name: attr2
          values:
            - value2
          state: absent
    groups:
        - name: group1
          state: present
    state: present

- name: Re-create a User
  community.general.keycloak_user:
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: admin
    auth_password: password
    realm: master
    username: user1
    firstName: user1
    lastName: user1
    email: user1
    enabled: true
    emailVerified: false
    credentials:
        - type: password
          value: password
          temporary: false
    attributes:
        - name: attr1
          values:
            - value1
          state: present
        - name: attr2
          values:
            - value2
          state: absent
    groups:
        - name: group1
          state: present
    state: present
    force: true

- name: Remove User
  community.general.keycloak_user:
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: admin
    auth_password: password
    realm: master
    username: user1
    state: absent
'''

RETURN = '''
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: User f18c709c-03d6-11ee-970b-c74bf2721112 created
proposed:
  description: Representation of the proposed user.
  returned: on success
  type: dict
existing:
  description: Representation of the existing user.
  returned: on success
  type: dict
end_state:
  description: Representation of the user after module execution
  returned: on success
  type: dict
changed:
  description: Return V(true) if the operation changed the user on the keycloak server, V(false) otherwise.
  returned: always
  type: bool
'''
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError, is_struct_included
from ansible.module_utils.basic import AnsibleModule
import copy


def main():
    argument_spec = keycloak_argument_spec()
    argument_spec['auth_username']['aliases'] = []
    credential_spec = dict(
        type=dict(type='str', required=True),
        value=dict(type='str', required=True),
        temporary=dict(type='bool', default=False)
    )
    client_consents_spec = dict(
        client_id=dict(type='str', required=True, aliases=['clientId']),
        roles=dict(type='list', elements='str', required=True)
    )
    attributes_spec = dict(
        name=dict(type='str'),
        values=dict(type='list', elements='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present')
    )
    groups_spec = dict(
        name=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present')
    )
    meta_args = dict(
        realm=dict(type='str', default='master'),
        self=dict(type='str'),
        id=dict(type='str'),
        username=dict(type='str', required=True),
        first_name=dict(type='str', aliases=['firstName']),
        last_name=dict(type='str', aliases=['lastName']),
        email=dict(type='str'),
        enabled=dict(type='bool'),
        email_verified=dict(type='bool', default=False, aliases=['emailVerified']),
        federation_link=dict(type='str', aliases=['federationLink']),
        service_account_client_id=dict(type='str', aliases=['serviceAccountClientId']),
        attributes=dict(type='list', elements='dict', options=attributes_spec),
        access=dict(type='dict'),
        groups=dict(type='list', default=[], elements='dict', options=groups_spec),
        disableable_credential_types=dict(type='list', default=[], aliases=['disableableCredentialTypes'], elements='str'),
        required_actions=dict(type='list', default=[], aliases=['requiredActions'], elements='str'),
        credentials=dict(type='list', default=[], elements='dict', options=credential_spec),
        federated_identities=dict(type='list', default=[], aliases=['federatedIdentities'], elements='str'),
        client_consents=dict(type='list', default=[], aliases=['clientConsents'], elements='dict', options=client_consents_spec),
        origin=dict(type='str'),
        state=dict(choices=["absent", "present"], default='present'),
        force=dict(type='bool', default=False),
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
    force = module.params.get('force')
    username = module.params.get('username')
    groups = module.params.get('groups')

    # Filter and map the parameters names that apply to the user
    user_params = [x for x in module.params
                   if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'force', 'groups'] and
                   module.params.get(x) is not None]

    before_user = kc.get_user_by_username(username=username, realm=realm)

    if before_user is None:
        before_user = {}

    changeset = {}

    for param in user_params:
        new_param_value = module.params.get(param)
        if param == 'attributes' and param in before_user:
            old_value = kc.convert_keycloak_user_attributes_dict_to_module_list(attributes=before_user['attributes'])
        else:
            old_value = before_user[param] if param in before_user else None
        if new_param_value != old_value:
            if old_value is not None and param == 'attributes':
                for old_attribute in old_value:
                    old_attribute_found = False
                    for new_attribute in new_param_value:
                        if new_attribute['name'] == old_attribute['name']:
                            old_attribute_found = True
                    if not old_attribute_found:
                        new_param_value.append(copy.deepcopy(old_attribute))
            if isinstance(new_param_value, dict):
                changeset[camel(param)] = copy.deepcopy(new_param_value)
            else:
                changeset[camel(param)] = new_param_value
    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_user = copy.deepcopy(before_user)
    desired_user.update(changeset)

    result['proposed'] = changeset
    result['existing'] = before_user

    changed = False

    # Cater for when it doesn't exist (an empty dict)
    if state == 'absent':
        if not before_user:
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = 'Role does not exist, doing nothing.'
            module.exit_json(**result)
        else:
            # Delete user
            kc.delete_user(user_id=before_user['id'], realm=realm)
            result["msg"] = 'User %s deleted' % (before_user['username'])
            changed = True

    else:
        after_user = {}
        if force and before_user:  # If the force option is set to true
            # Delete the existing user
            kc.delete_user(user_id=before_user["id"], realm=realm)

        if not before_user or force:
            # Process a creation
            changed = True

            if username is None:
                module.fail_json(msg='username must be specified when creating a new user')

            if module._diff:
                result['diff'] = dict(before='', after=desired_user)

            if module.check_mode:
                module.exit_json(**result)
            # Create the user
            after_user = kc.create_user(userrep=desired_user, realm=realm)
            result["msg"] = 'User %s created' % (desired_user['username'])
            # Add user ID to new representation
            desired_user['id'] = after_user["id"]
        else:
            excludes = [
                "access",
                "notBefore",
                "createdTimestamp",
                "totp",
                "credentials",
                "disableableCredentialTypes",
                "groups",
                "clientConsents",
                "federatedIdentities",
                "requiredActions"]
            # Add user ID to new representation
            desired_user['id'] = before_user["id"]

            # Compare users
            if not (is_struct_included(desired_user, before_user, excludes)):  # If the new user does not introduce a change to the existing user
                # Update the user
                after_user = kc.update_user(userrep=desired_user, realm=realm)
                changed = True

        # set user groups
        if kc.update_user_groups_membership(userrep=desired_user, groups=groups, realm=realm):
            changed = True
        # Get the user groups
        after_user["groups"] = kc.get_user_groups(user_id=desired_user["id"], realm=realm)
        result["end_state"] = after_user
        if changed:
            result["msg"] = 'User %s updated' % (desired_user['username'])
        else:
            result["msg"] = 'No changes made for user %s' % (desired_user['username'])

    result['changed'] = changed
    module.exit_json(**result)


if __name__ == '__main__':
    main()

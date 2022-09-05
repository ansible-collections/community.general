#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Adam Goossens <adam.goossens@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_user_info

short_description: Allows obtaining Keycloak user information via Keycloak API

version_added: 5.4.0

description:
    - This module allows you to get Keycloak user information via the Keycloak REST API.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

options:
    auth_keycloak_url:
        description:
            - URL to the Keycloak instance.
        type: str
        required: true
        aliases:
          - url
    validate_certs:
        description:
            - Verify TLS certificates (do not disable this in production).
        type: bool
        default: yes

    realm:
        type: str
        description:
            - They Keycloak realm ID.
        default: 'master'
    id:
        type: str
        description:
            - They Keycloak User ID.
    name:
        type: str
        description:
            - They Keycloak User Name.

author:
    - Dishant Pandya (@drpdishant)
    - Mahek Katariya (@MahekKatariya)

extends_documentation_fragment:
- community.general.keycloak
'''

EXAMPLES = '''
- name: Get all users in a realm
  community.general.keycloak_user_info:
    realm: MyCustomRealm
    auth_keycloak_url: https://auth.example.com/auth
  delegate_to: localhost

- name: Get a Keycloak User Info by User Id
  community.general.keycloak_user_info:
    realm: MyCustomRealm
    userid: "677a27df-02e8-48e9-8f90-fa95caf64bd7" #UUID of the User
    auth_keycloak_url: https://auth.example.com/auth
  delegate_to: localhost

- name: Get a Keycloak User Info by User Name
  community.general.keycloak_user_info:
    realm: MyCustomRealm
    username: "user@example.com"
    auth_keycloak_url: https://auth.example.com/auth
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
    type: dict
    contains:
        username:
            description: Username.
            type: str
            returned: always
            sample: johnwick@boogeyman.com
        createdTimestamp:
            description: Timestamp when this user was created.
            type: str
            returned: always
            sample: 1657990547016
        email:
            description: Email address.
            type: str
            returned: always
            sample: johnwick@boogeyman.com
        emailVerified:
            description: Whether or not the email is verified.
            type: bool
            returned: always
            sample: true
        enabled:
            description: Whether or not this user is enabled.
            type: bool
            returned: always
            sample: true
        firstName:
            description: First name.
            type: str
            returned: always
            sample: "John"
        id:
            description: ID of the user.
            type: str
            returned: always
            sample: 2d4b5ea1-9aa2-44da-a8a6
        lastName:
            description: Last name.
            type: str
            returned: always
            sample: "Wick"
        notBefore:
            description: Not before date.
            type: str
            returned: always
            sample: "2020-01-01"
        requiredActions:
            description: Required actions.
            returned: always
            type: str
            sample: []
        totp:
            description: Time based OTP enabled or not.
            type: bool
            returned: always
            sample: false
        access:
            description: A dict describing the accesses you have to this user based on the credentials used.
            type: dict
            returned: always
            sample:
                manage: true
                manageMembership: true
                view: true
users:
  description:
    - Representation of the user after module execution.
    - Deprecated return value, it will be removed in community.general 6.0.0. Please use the return value I(end_state) instead.
  returned: always
  type: dict
  contains:
        username:
            description: Username.
            type: str
            returned: always
            sample: johnwick@boogeyman.com
        createdTimestamp:
            description: Timestamp when this user was created.
            type: str
            returned: always
            sample: 1657990547016
        email:
            description: Email address.
            type: str
            returned: always
            sample: johnwick@boogeyman.com
        emailVerified:
            description: Whether or not the email is verified.
            type: bool
            returned: always
            sample: true
        enabled:
            description: Whether or not this user is enabled.
            type: bool
            returned: always
            sample: true
        firstName:
            description: First name.
            type: str
            returned: always
            sample: "John"
        id:
            description: ID of the user.
            type: str
            returned: always
            sample: 2d4b5ea1-9aa2-44da-a8a6
        lastName:
            description: Last name.
            type: str
            returned: always
            sample: "Wick"
        notBefore:
            description: Not before date.
            type: str
            returned: always
            sample: "2020-01-01"
        requiredActions:
            description: Required actions.
            returned: always
            type: str
            sample: []
        totp:
            description: Time based OTP enabled or not.
            type: bool
            returned: always
            sample: false
        access:
            description: A dict describing the accesses you have to this user based on the credentials used.
            type: dict
            returned: always
            sample:
                manage: true
                manageMembership: true
                view: true
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
        realm=dict(default='master'),
        id=dict(type='str'),
        name=dict(type='str')
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, users='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    uid = module.params.get('id')
    name = module.params.get('name')

    if uid is None and name is None:
        user_info = kc.get_users(realm=realm)
    if uid is None:
        user_info = kc.get_user_by_name(name, realm=realm)
    else:
        user_info = kc.get_user_by_userid(uid, realm=realm)

    result['users'] = user_info
    result['msg'] = 'Get User info successful for Realm: {realm}'.format(realm=realm)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

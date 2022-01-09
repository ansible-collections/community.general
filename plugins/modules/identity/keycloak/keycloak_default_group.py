#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_default_group

short_description: Allows administration of Keycloak default groups via Keycloak API

description:
    - This module allows you to add or remove Keycloak default groups via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.


options:
    state:
        description:
            - State of the group.
            - On C(present), the default group will be added if it does not yet exist.
            - On C(absent), the default group will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent
    realm:
        type: str
        description:
            - They Keycloak realm under which this group resides.
        default: 'master'
    id:
        type: str
        required: true
        description:
            - The unique identifier for this group.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Add a Keycloak default group, authentication with credentials
  community.general.keycloak_group:
    realm: MyCustomRealm
    id: 27112a16-c847-4def-9140-2b97a1f4108a
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Remove a Keycloak default group, authentication with token
  community.general.keycloak_group:
    realm: MyCustomRealm
    id: 27112a16-c847-4def-9140-2b97a1f4108a
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Empty.
    returned: on success
    type: complex

default_group:
    description: Empty
    returned: always
    type: complex
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
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        id=dict(type='str', required=True),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, default_group={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    gid = module.params.get('id')

    if state == 'present':
        # Add to default groups
        kc.create_default_group(groupid=gid, realm=realm)
        result['changed'] = True
        result['end_state'] = {}
        result['default_group'] = result['end_state']
        result['msg'] = 'Group {id} has been added to default groups'.format(id=gid)
        module.exit_json(**result)
    else:
        # Remove from default groups
        kc.delete_default_group(groupid=gid, realm=realm)
        result['changed'] = True
        result['end_state'] = {}
        result['default_group'] = result['end_state']
        result['msg'] = 'Group {id} has been removed from default groups'.format(id=gid)
        module.exit_json(**result)


if __name__ == '__main__':
    main()

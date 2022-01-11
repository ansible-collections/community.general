#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_realm_info

short_description: Allows obtaining Keycloak realm public information via Keycloak API

version_added: 4.3.0

description:
    - This module allows you to get Keycloak realm public information via the Keycloak REST API.

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

author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Get a Keycloak public key
  community.general.keycloak_realm_info:
    realm: MyCustomRealm
    auth_keycloak_url: https://auth.example.com/auth
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

realm_info:
    description:
        - Representation of the realm public infomation.
    returned: always
    type: dict
    contains:
        realm:
            description: Realm ID.
            type: str
            returned: always
            sample: MyRealm
        public_key:
            description: Public key of the realm.
            type: str
            returned: always
            sample: MIIBIjANBgkqhkiG9w0BAQEFAAO...
        token-service:
            description: Token endpoint URL.
            type: str
            returned: always
            sample: https://auth.example.com/auth/realms/MyRealm/protocol/openid-connect
        account-service:
            description: Account console URL.
            type: str
            returned: always
            sample: https://auth.example.com/auth/realms/MyRealm/account
        tokens-not-before:
            description: The token not before.
            type: int
            returned: always
            sample: 0
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = dict(
        auth_keycloak_url=dict(type='str', aliases=['url'], required=True, no_log=False),
        validate_certs=dict(type='bool', default=True),

        realm=dict(default='master'),
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = dict(changed=False, msg='', realm_info='')

    kc = KeycloakAPI(module, {})

    realm = module.params.get('realm')

    realm_info = kc.get_realm_info_by_id(realm=realm)

    result['realm_info'] = realm_info
    result['msg'] = 'Get realm public info successful for ID {realm}'.format(realm=realm)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

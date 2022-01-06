#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_clientsecret

short_description: Allows administration of Keycloak client secret via Keycloak API

description:
    - This module allows you to get or generate new Keycloak client secret via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When generate a new client secret, where possible provide the client ID (not client_id) to the module.
      This removes a lookup to the API to translate the client_id into the client ID.


options:
    state:
        description:
            - State of the client secret.
            - On C(present), get the current client secret.
            - On C(absent), the new client secret will be generated.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    realm:
        type: str
        description:
            - They Keycloak realm under which this client resides.
        default: 'master'

    id:
        description:
            - The unique identifier for this client.
            - This parameter is not required for getting or generating a client secret but
              providing it will reduce the number of API calls required.
        type: str
    client_id:
        description:
            - The client_id of the client to lookup account client ID
        aliases:
          - clientId
        type: str


extends_documentation_fragment:
- community.general.keycloak

author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Get a Keycloak client secret, authentication with credentials
  community.general.keycloak_clientsecret:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Generate a new Keycloak client secret, authentication with token
  community.general.keycloak_user:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    realm: MyCustomRealm
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
    description: Representation of the client credential after module execution (sample is truncated).
    returned: on success
    type: complex
    contains:
        type:
            description: Credential type.
            type: str
            returned: always
            sample: secret
        value:
            description: Secret of the client.
            type: str
            returned: always
            sample: cUGnX1EIeTtPPAkcyGMv0ncyqDPu68P1

clientsecret:
  description:
      - Representation of the client credential after module execution.
      - Deprecated return value, it will be removed in community.general 6.0.0. Please use the return value I(end_state) instead.
  returned: always
  type: complex
  contains:
      type:
          description: Credential type.
          type: str
          returned: always
          sample: secret
      value:
          description: Secret of the client.
          type: str
          returned: always
          sample: cUGnX1EIeTtPPAkcyGMv0ncyqDPu68P1

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

        id=dict(type='str'),
        client_id=dict(type='str', aliases=['clientId']),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'client_id'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, clientsecret='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    id = module.params.get('id')
    client_id = module.params.get('client_id')

    # only lookup the client_id if id isn't provided.
    # in the case that both are provided, prefer the ID, since it's one
    # less lookup.
    if id is None and client_id is not None:
        client = kc.get_client_by_clientid(client_id, realm=realm)

        if client is None:
            raise Exception('Client does not exist {client_id}'.format(client_id=client_id))

        id = client['id']

    if state == 'present':
        # Get secret
        result['changed'] = False

        if module.check_mode:
            module.exit_json(**result)

        # Create new secret
        clientsecret = kc.get_clientsecret(id=id, realm=realm)

        result['clientsecret'] = clientsecret
        result['end_state'] = clientsecret
        result['msg'] = 'Get client secret successful for ID {id}'.format(id=id)

        module.exit_json(**result)
    else:
        if state == 'absent':
            # Process a creation
            result['changed'] = True

            if module.check_mode:
                module.exit_json(**result)

            # Create new secret
            clientsecret = kc.create_clientsecret(id=id, realm=realm)

            result['end_state'] = clientsecret
            result['msg'] = 'New client secret has been generated for ID {id}'.format(id=id)

            module.exit_json(**result)

        # Do nothing and exit
        result['changed'] = False
        result['end_state'] = {}
        result['msg'] = 'State not specified; doing nothing.'
        module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

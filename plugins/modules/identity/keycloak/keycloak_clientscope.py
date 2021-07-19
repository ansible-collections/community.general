#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_clientscope

short_description: Allows administration of Keycloak client_scopes via Keycloak API

version_added: 3.4.0

description:
    - This module allows you to add, remove or modify Keycloak client_scopes via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When updating a client_scope, where possible provide the client_scope ID to the module. This removes a lookup
      to the API to translate the name into the client_scope ID.


options:
    state:
        description:
            - State of the client_scope.
            - On C(present), the client_scope will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the client_scope will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    name:
        type: str
        description:
            - Name of the client_scope.
            - This parameter is required only when creating or updating the client_scope.

    realm:
        type: str
        description:
            - They Keycloak realm under which this client_scope resides.
        default: 'master'

    id:
        type: str
        description:
            - The unique identifier for this client_scope.
            - This parameter is not required for updating or deleting a client_scope but
              providing it will reduce the number of API calls required.

    description:
        type: str
        description:
            - Description for this client_scope.
            - This parameter is not required for updating or deleting a client_scope.

    protocol:
        description:
            - Type of client.
        choices: ['openid-connect', 'saml', 'wsfed']
        type: str

    protocol_mappers:
        description:
            - A list of dicts defining protocol mappers for this client.
            - This is 'protocolMappers' in the Keycloak REST API.
        aliases:
            - protocolMappers
        type: list
        elements: dict
        suboptions:
            protocol:
                description:
                    - This specifies for which protocol this protocol mapper
                    - is active.
                choices: ['openid-connect', 'saml', 'wsfed']
                type: str

            protocolMapper:
                description:
                    - "The Keycloak-internal name of the type of this protocol-mapper. While an exhaustive list is
                      impossible to provide since this may be extended through SPIs by the user of Keycloak,
                      by default Keycloak as of 3.4 ships with at least:"
                    - C(docker-v2-allow-all-mapper)
                    - C(oidc-address-mapper)
                    - C(oidc-full-name-mapper)
                    - C(oidc-group-membership-mapper)
                    - C(oidc-hardcoded-claim-mapper)
                    - C(oidc-hardcoded-role-mapper)
                    - C(oidc-role-name-mapper)
                    - C(oidc-script-based-protocol-mapper)
                    - C(oidc-sha256-pairwise-sub-mapper)
                    - C(oidc-usermodel-attribute-mapper)
                    - C(oidc-usermodel-client-role-mapper)
                    - C(oidc-usermodel-property-mapper)
                    - C(oidc-usermodel-realm-role-mapper)
                    - C(oidc-usersessionmodel-note-mapper)
                    - C(saml-group-membership-mapper)
                    - C(saml-hardcode-attribute-mapper)
                    - C(saml-hardcode-role-mapper)
                    - C(saml-role-list-mapper)
                    - C(saml-role-name-mapper)
                    - C(saml-user-attribute-mapper)
                    - C(saml-user-property-mapper)
                    - C(saml-user-session-note-mapper)
                    - An exhaustive list of available mappers on your installation can be obtained on
                      the admin console by going to Server Info -> Providers and looking under
                      'protocol-mapper'.
                type: str

            name:
                description:
                    - The name of this protocol mapper.
                type: str

            id:
                description:
                    - Usually a UUID specifying the internal ID of this protocol mapper instance.
                type: str

            config:
                description:
                    - Dict specifying the configuration options for the protocol mapper; the
                      contents differ depending on the value of I(protocolMapper) and are not documented
                      other than by the source of the mappers and its parent class(es). An example is given
                      below. It is easiest to obtain valid config values by dumping an already-existing
                      protocol mapper configuration through check-mode in the C(existing) return value.
                type: dict

    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the client_scope.
            - Values may be single values (for example a string) or a list of strings.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Gaëtan Daubresse (@Gaetan2907)
'''

EXAMPLES = '''
- name: Create a Keycloak client_scopes, authentication with credentials
  community.general.keycloak_clientscope:
    name: my-new-kc-clientscope
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak client_scopes, authentication with token
  community.general.keycloak_clientscope:
    name: my-new-kc-clientscope
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Delete a keycloak client_scopes
  community.general.keycloak_clientscope:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    state: absent
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak client_scope based on name
  community.general.keycloak_clientscope:
    name: my-clientscope-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Update the name of a Keycloak client_scope
  community.general.keycloak_clientscope:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    name: an-updated-kc-clientscope-name
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak client_scope with some custom attributes
  community.general.keycloak_clientscope:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    name: my-new_clientscope
    description: description-of-clientscope
    protocol: openid-connect
    protocol_mappers:
      - config:
          access.token.claim: True
          claim.name: "family_name"
          id.token.claim: True
          jsonType.label: String
          user.attribute: lastName
          userinfo.token.claim: True
        name: family name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          attribute.name: Role
          attribute.nameformat: Basic
          single: false
        name: role list
        protocol: saml
        protocolMapper: saml-role-list-mapper
    attributes:
        attrib1: value1
        attrib2: value2
        attrib3:
            - with
            - numerous
            - individual
            - list
            - items
  delegate_to: localhost
'''

RETURN = '''
msg:
  description: Message as to what action was taken
  returned: always
  type: str
  sample: "Client_scope testclientscope has been updated"

proposed:
    description: client_scope representation of proposed changes to client_scope
    returned: always
    type: dict
    sample: {
      clientId: "test"
    }
existing:
    description: client_scope representation of existing client_scope (sample is truncated)
    returned: always
    type: dict
    sample: {
        "adminUrl": "http://www.example.com/admin_url",
        "attributes": {
            "request.object.signature.alg": "RS256",
        }
    }
end_state:
    description: client_scope representation of client_scope after module execution (sample is truncated)
    returned: always
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


def sanitize_cr(clientscoperep):
    """ Removes probably sensitive details from a clientscoperep representation

    :param clientscoperep: the clientscoperep dict to be sanitized
    :return: sanitized clientrep dict
    """
    result = clientscoperep.copy()
    if 'secret' in result:
        result['secret'] = 'no_log'
    if 'attributes' in result:
        if 'saml.signing.private.key' in result['attributes']:
            result['attributes']['saml.signing.private.key'] = 'no_log'
    return result


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    protmapper_spec = dict(
        id=dict(type='str'),
        name=dict(type='str'),
        protocol=dict(type='str', choices=['openid-connect', 'saml', 'wsfed']),
        protocolMapper=dict(type='str'),
        config=dict(type='dict'),
    )

    meta_args = dict(
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        protocol=dict(type='str', choices=['openid-connect', 'saml', 'wsfed']),
        attributes=dict(type='dict'),
        protocol_mappers=dict(type='list', elements='dict', options=protmapper_spec, aliases=['protocolMappers']),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
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
    cid = module.params.get('id')
    name = module.params.get('name')
    protocol_mappers = module.params.get('protocol_mappers')

    before_clientscope = None         # current state of the clientscope, for merging.

    # does the clientscope already exist?
    if cid is None:
        before_clientscope = kc.get_clientscope_by_name(name, realm=realm)
    else:
        before_clientscope = kc.get_clientscope_by_clientscopeid(cid, realm=realm)

    before_clientscope = {} if before_clientscope is None else before_clientscope

    clientscope_params = [x for x in module.params
                          if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm'] and
                          module.params.get(x) is not None]

    # Build a proposed changeset from parameters given to this module
    changeset = dict()

    for clientscope_param in clientscope_params:
        new_param_value = module.params.get(clientscope_param)

        # some lists in the Keycloak API are sorted, some are not.
        if isinstance(new_param_value, list):
            if clientscope_param in ['attributes']:
                try:
                    new_param_value = sorted(new_param_value)
                except TypeError:
                    pass
        # Unfortunately, the ansible argument spec checker introduces variables with null values when
        # they are not specified
        if clientscope_param == 'protocol_mappers':
            new_param_value = [dict((k, v) for k, v in x.items() if x[k] is not None) for x in new_param_value]
        changeset[camel(clientscope_param)] = new_param_value

    # prepare the new clientscope
    updated_clientscope = before_clientscope.copy()
    updated_clientscope.update(changeset)

    # if before_clientscope is none, the clientscope doesn't exist.
    if before_clientscope == {}:
        if state == 'absent':
            # nothing to do.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['msg'] = 'Clientscope does not exist; doing nothing.'
            result['end_state'] = dict()
            module.exit_json(**result)

        # for 'present', create a new clientscope.
        result['changed'] = True
        if name is None:
            module.fail_json(msg='name must be specified when creating a new clientscope')

        if module._diff:
            result['diff'] = dict(before='', after=sanitize_cr(updated_clientscope))

        if module.check_mode:
            module.exit_json(**result)

        # do it for real!
        kc.create_clientscope(updated_clientscope, realm=realm)
        after_clientscope = kc.get_clientscope_by_name(name, realm)

        result['end_state'] = sanitize_cr(after_clientscope)
        result['msg'] = 'Clientscope {name} has been created with ID {id}'.format(name=after_clientscope['name'],
                                                                                  id=after_clientscope['id'])

    else:
        if state == 'present':
            # no changes
            if updated_clientscope == before_clientscope:
                result['changed'] = False
                result['end_state'] = sanitize_cr(updated_clientscope)
                result['msg'] = "No changes required to clientscope {name}.".format(name=before_clientscope['name'])
                module.exit_json(**result)

            # update the existing clientscope
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=sanitize_cr(before_clientscope), after=sanitize_cr(updated_clientscope))

            if module.check_mode:
                module.exit_json(**result)

            # do the clientscope update
            kc.update_clientscope(updated_clientscope, realm=realm)

            # do the protocolmappers update
            if protocol_mappers is not None:
                for protocol_mapper in protocol_mappers:
                    # update if protocolmapper exist
                    current_protocolmapper = kc.get_clientscope_protocolmapper_by_name(updated_clientscope['id'], protocol_mapper['name'], realm=realm)
                    if current_protocolmapper is not None:
                        protocol_mapper['id'] = current_protocolmapper['id']
                        kc.update_clientscope_protocolmappers(updated_clientscope['id'], protocol_mapper, realm=realm)
                    # create otherwise
                    else:
                        kc.create_clientscope_protocolmapper(updated_clientscope['id'], protocol_mapper, realm=realm)

            after_clientscope = kc.get_clientscope_by_clientscopeid(updated_clientscope['id'], realm=realm)

            result['end_state'] = after_clientscope
            result['msg'] = "Clientscope {id} has been updated".format(id=after_clientscope['id'])

            module.exit_json(**result)

        elif state == 'absent':
            result['end_state'] = dict()

            if module._diff:
                result['diff'] = dict(before=sanitize_cr(before_clientscope), after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete for real
            cid = before_clientscope['id']
            kc.delete_clientscope(cid=cid, realm=realm)

            result['changed'] = True
            result['msg'] = "Clientscope {name} has been deleted".format(name=before_clientscope['name'])

            module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

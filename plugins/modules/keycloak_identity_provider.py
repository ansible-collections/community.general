#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_identity_provider

short_description: Allows administration of Keycloak identity providers via Keycloak API

version_added: 3.6.0

description:
    - This module allows you to add, remove or modify Keycloak identity providers via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/15.0/rest-api/index.html).

attributes:
    check_mode:
        support: full
    diff_mode:
        support: full

options:
    state:
        description:
            - State of the identity provider.
            - On V(present), the identity provider will be created if it does not yet exist, or updated with the parameters you provide.
            - On V(absent), the identity provider will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    realm:
        description:
            - The Keycloak realm under which this identity provider resides.
        default: 'master'
        type: str

    alias:
        description:
            - The alias uniquely identifies an identity provider and it is also used to build the redirect URI.
        required: true
        type: str

    display_name:
        description:
            - Friendly name for identity provider.
        aliases:
            - displayName
        type: str

    enabled:
        description:
            - Enable/disable this identity provider.
        type: bool

    store_token:
        description:
            - Enable/disable whether tokens must be stored after authenticating users.
        aliases:
            - storeToken
        type: bool

    add_read_token_role_on_create:
        description:
            - Enable/disable whether new users can read any stored tokens. This assigns the C(broker.read-token) role.
        aliases:
            - addReadTokenRoleOnCreate
        type: bool

    trust_email:
        description:
            - If enabled, email provided by this provider is not verified even if verification is enabled for the realm.
        aliases:
            - trustEmail
        type: bool

    link_only:
        description:
            - If true, users cannot log in through this provider. They can only link to this provider.
              This is useful if you don't want to allow login from the provider, but want to integrate with a provider.
        aliases:
            - linkOnly
        type: bool

    first_broker_login_flow_alias:
        description:
            - Alias of authentication flow, which is triggered after first login with this identity provider.
        aliases:
            - firstBrokerLoginFlowAlias
        type: str

    post_broker_login_flow_alias:
        description:
            - Alias of authentication flow, which is triggered after each login with this identity provider.
        aliases:
            - postBrokerLoginFlowAlias
        type: str

    authenticate_by_default:
        description:
            - Specifies if this identity provider should be used by default for authentication even before displaying login screen.
        aliases:
            - authenticateByDefault
        type: bool

    provider_id:
        description:
            - Protocol used by this provider (supported values are V(oidc) or V(saml)).
        aliases:
            - providerId
        type: str

    config:
        description:
            - Dict specifying the configuration options for the provider; the contents differ depending on the value of O(provider_id).
              Examples are given below for V(oidc) and V(saml). It is easiest to obtain valid config values by dumping an already-existing
              identity provider configuration through check-mode in the RV(existing) field.
        type: dict
        suboptions:
            hide_on_login_page:
                description:
                    - If hidden, login with this provider is possible only if requested explicitly, for example using the C(kc_idp_hint) parameter.
                aliases:
                    - hideOnLoginPage
                type: bool

            gui_order:
                description:
                    - Number defining order of the provider in GUI (for example, on Login page).
                aliases:
                    - guiOrder
                type: int

            sync_mode:
                description:
                    - Default sync mode for all mappers. The sync mode determines when user data will be synced using the mappers.
                aliases:
                    - syncMode
                type: str

            issuer:
                description:
                    - The issuer identifier for the issuer of the response. If not provided, no validation will be performed.
                type: str

            authorizationUrl:
                description:
                    - The Authorization URL.
                type: str

            tokenUrl:
                description:
                    - The Token URL.
                type: str

            logoutUrl:
                description:
                    - End session endpoint to use to logout user from external IDP.
                type: str

            userInfoUrl:
                description:
                    - The User Info URL.
                type: str

            clientAuthMethod:
                description:
                    - The client authentication method.
                type: str

            clientId:
                description:
                    - The client or client identifier registered within the identity provider.
                type: str

            clientSecret:
                description:
                    - The client or client secret registered within the identity provider.
                type: str

            defaultScope:
                description:
                    - The scopes to be sent when asking for authorization.
                type: str

            validateSignature:
                description:
                    - Enable/disable signature validation of external IDP signatures.
                type: bool

            useJwksUrl:
                description:
                    - If the switch is on, identity provider public keys will be downloaded from given JWKS URL.
                type: bool

            jwksUrl:
                description:
                    - URL where identity provider keys in JWK format are stored. See JWK specification for more details.
                type: str

            entityId:
                description:
                    - The Entity ID that will be used to uniquely identify this SAML Service Provider.
                type: str

            singleSignOnServiceUrl:
                description:
                    - The URL that must be used to send authentication requests (SAML AuthnRequest).
                type: str

            singleLogoutServiceUrl:
                description:
                    - The URL that must be used to send logout requests.
                type: str

            backchannelSupported:
                description:
                    - Does the external IDP support backchannel logout?
                type: str

            nameIDPolicyFormat:
                description:
                    - Specifies the URI reference corresponding to a name identifier format.
                type: str

            principalType:
                description:
                    - Way to identify and track external users from the assertion.
                type: str

    mappers:
        description:
            - A list of dicts defining mappers associated with this Identity Provider.
        type: list
        elements: dict
        suboptions:
            id:
                description:
                    - Unique ID of this mapper.
                type: str

            name:
                description:
                    - Name of the mapper.
                type: str

            identityProviderAlias:
                description:
                    - Alias of the identity provider for this mapper.
                type: str

            identityProviderMapper:
                description:
                    - Type of mapper.
                type: str

            config:
                description:
                    - Dict specifying the configuration options for the mapper; the contents differ depending on the value of
                      O(mappers[].identityProviderMapper).
                type: dict

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
    - Laurent Paumier (@laurpaum)
'''

EXAMPLES = '''
- name: Create OIDC identity provider, authentication with credentials
  community.general.keycloak_identity_provider:
    state: present
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: admin
    realm: myrealm
    alias: oidc-idp
    display_name: OpenID Connect IdP
    enabled: true
    provider_id: oidc
    config:
      issuer: https://idp.example.com
      authorizationUrl: https://idp.example.com/auth
      tokenUrl: https://idp.example.com/token
      userInfoUrl: https://idp.example.com/userinfo
      clientAuthMethod: client_secret_post
      clientId: my-client
      clientSecret: secret
      syncMode: FORCE
    mappers:
      - name: first_name
        identityProviderMapper: oidc-user-attribute-idp-mapper
        config:
          claim: first_name
          user.attribute: first_name
          syncMode: INHERIT
      - name: last_name
        identityProviderMapper: oidc-user-attribute-idp-mapper
        config:
          claim: last_name
          user.attribute: last_name
          syncMode: INHERIT

- name: Create SAML identity provider, authentication with credentials
  community.general.keycloak_identity_provider:
    state: present
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: admin
    realm: myrealm
    alias: saml-idp
    display_name: SAML IdP
    enabled: true
    provider_id: saml
    config:
      entityId: https://auth.example.com/auth/realms/myrealm
      singleSignOnServiceUrl: https://idp.example.com/login
      wantAuthnRequestsSigned: true
      wantAssertionsSigned: true
    mappers:
      - name: roles
        identityProviderMapper: saml-user-attribute-idp-mapper
        config:
          user.attribute: roles
          attribute.friendly.name: User Roles
          attribute.name: roles
          syncMode: INHERIT
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str
    sample: "Identity provider my-idp has been created"

proposed:
    description: Representation of proposed identity provider.
    returned: always
    type: dict
    sample: {
        "config": {
            "authorizationUrl": "https://idp.example.com/auth",
            "clientAuthMethod": "client_secret_post",
            "clientId": "my-client",
            "clientSecret": "secret",
            "issuer": "https://idp.example.com",
            "tokenUrl": "https://idp.example.com/token",
            "userInfoUrl": "https://idp.example.com/userinfo"
        },
        "displayName": "OpenID Connect IdP",
        "providerId": "oidc"
    }

existing:
    description: Representation of existing identity provider.
    returned: always
    type: dict
    sample: {
        "addReadTokenRoleOnCreate": false,
        "alias": "my-idp",
        "authenticateByDefault": false,
        "config": {
            "authorizationUrl": "https://old.example.com/auth",
            "clientAuthMethod": "client_secret_post",
            "clientId": "my-client",
            "clientSecret": "**********",
            "issuer": "https://old.example.com",
            "syncMode": "FORCE",
            "tokenUrl": "https://old.example.com/token",
            "userInfoUrl": "https://old.example.com/userinfo"
        },
        "displayName": "OpenID Connect IdP",
        "enabled": true,
        "firstBrokerLoginFlowAlias": "first broker login",
        "internalId": "4d28d7e3-1b80-45bb-8a30-5822bf55aa1c",
        "linkOnly": false,
        "providerId": "oidc",
        "storeToken": false,
        "trustEmail": false,
    }

end_state:
    description: Representation of identity provider after module execution.
    returned: on success
    type: dict
    sample: {
        "addReadTokenRoleOnCreate": false,
        "alias": "my-idp",
        "authenticateByDefault": false,
        "config": {
            "authorizationUrl": "https://idp.example.com/auth",
            "clientAuthMethod": "client_secret_post",
            "clientId": "my-client",
            "clientSecret": "**********",
            "issuer": "https://idp.example.com",
            "tokenUrl": "https://idp.example.com/token",
            "userInfoUrl": "https://idp.example.com/userinfo"
        },
        "displayName": "OpenID Connect IdP",
        "enabled": true,
        "firstBrokerLoginFlowAlias": "first broker login",
        "internalId": "4d28d7e3-1b80-45bb-8a30-5822bf55aa1c",
        "linkOnly": false,
        "providerId": "oidc",
        "storeToken": false,
        "trustEmail": false,
    }
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy


def sanitize(idp):
    idpcopy = deepcopy(idp)
    if 'config' in idpcopy:
        if 'clientSecret' in idpcopy['config']:
            idpcopy['clientSecret'] = '**********'
    return idpcopy


def get_identity_provider_with_mappers(kc, alias, realm):
    idp = kc.get_identity_provider(alias, realm)
    if idp is not None:
        idp['mappers'] = sorted(kc.get_identity_provider_mappers(alias, realm), key=lambda x: x.get('name'))
    if idp is None:
        idp = {}
    return idp


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    mapper_spec = dict(
        id=dict(type='str'),
        name=dict(type='str'),
        identityProviderAlias=dict(type='str'),
        identityProviderMapper=dict(type='str'),
        config=dict(type='dict'),
    )

    meta_args = dict(
        state=dict(type='str', default='present', choices=['present', 'absent']),
        realm=dict(type='str', default='master'),
        alias=dict(type='str', required=True),
        add_read_token_role_on_create=dict(type='bool', aliases=['addReadTokenRoleOnCreate']),
        authenticate_by_default=dict(type='bool', aliases=['authenticateByDefault']),
        config=dict(type='dict'),
        display_name=dict(type='str', aliases=['displayName']),
        enabled=dict(type='bool'),
        first_broker_login_flow_alias=dict(type='str', aliases=['firstBrokerLoginFlowAlias']),
        link_only=dict(type='bool', aliases=['linkOnly']),
        post_broker_login_flow_alias=dict(type='str', aliases=['postBrokerLoginFlowAlias']),
        provider_id=dict(type='str', aliases=['providerId']),
        store_token=dict(type='bool', aliases=['storeToken']),
        trust_email=dict(type='bool', aliases=['trustEmail']),
        mappers=dict(type='list', elements='dict', options=mapper_spec),
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
    alias = module.params.get('alias')
    state = module.params.get('state')

    # Filter and map the parameters names that apply to the identity provider.
    idp_params = [x for x in module.params
                  if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'mappers'] and
                  module.params.get(x) is not None]

    # See if it already exists in Keycloak
    before_idp = get_identity_provider_with_mappers(kc, alias, realm)

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for param in idp_params:
        new_param_value = module.params.get(param)
        old_value = before_idp[camel(param)] if camel(param) in before_idp else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # special handling of mappers list to allow change detection
    if module.params.get('mappers') is not None:
        for change in module.params['mappers']:
            change = dict((k, v) for k, v in change.items() if change[k] is not None)
            if change.get('id') is None and change.get('name') is None:
                module.fail_json(msg='Either `name` or `id` has to be specified on each mapper.')
            if before_idp == dict():
                old_mapper = dict()
            elif change.get('id') is not None:
                old_mapper = kc.get_identity_provider_mapper(change['id'], alias, realm)
                if old_mapper is None:
                    old_mapper = dict()
            else:
                found = [x for x in kc.get_identity_provider_mappers(alias, realm) if x['name'] == change['name']]
                if len(found) == 1:
                    old_mapper = found[0]
                else:
                    old_mapper = dict()
            new_mapper = old_mapper.copy()
            new_mapper.update(change)

            if changeset.get('mappers') is None:
                changeset['mappers'] = list()
            # eventually this holds all desired mappers, unchanged, modified and newly added
            changeset['mappers'].append(new_mapper)

        # ensure idempotency in case module.params.mappers is not sorted by name
        changeset['mappers'] = sorted(changeset['mappers'], key=lambda x: x.get('id') if x.get('name') is None else x['name'])

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_idp = before_idp.copy()
    desired_idp.update(changeset)

    result['proposed'] = sanitize(changeset)
    result['existing'] = sanitize(before_idp)

    # Cater for when it doesn't exist (an empty dict)
    if not before_idp:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = 'Identity provider does not exist; doing nothing.'
            module.exit_json(**result)

        # Process a creation
        result['changed'] = True

        if module._diff:
            result['diff'] = dict(before='', after=sanitize(desired_idp))

        if module.check_mode:
            module.exit_json(**result)

        # create it
        desired_idp = desired_idp.copy()
        mappers = desired_idp.pop('mappers', [])
        kc.create_identity_provider(desired_idp, realm)
        for mapper in mappers:
            if mapper.get('identityProviderAlias') is None:
                mapper['identityProviderAlias'] = alias
            kc.create_identity_provider_mapper(mapper, alias, realm)
        after_idp = get_identity_provider_with_mappers(kc, alias, realm)

        result['end_state'] = sanitize(after_idp)

        result['msg'] = 'Identity provider {alias} has been created'.format(alias=alias)
        module.exit_json(**result)

    else:
        if state == 'present':
            # Process an update

            # no changes
            if desired_idp == before_idp:
                result['changed'] = False
                result['end_state'] = sanitize(desired_idp)
                result['msg'] = "No changes required to identity provider {alias}.".format(alias=alias)
                module.exit_json(**result)

            # doing an update
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=sanitize(before_idp), after=sanitize(desired_idp))

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            desired_idp = desired_idp.copy()
            updated_mappers = desired_idp.pop('mappers', [])
            original_mappers = list(before_idp.get('mappers', []))

            kc.update_identity_provider(desired_idp, realm)
            for mapper in updated_mappers:
                if mapper.get('id') is not None:
                    # only update existing if there is a change
                    for i, orig in enumerate(original_mappers):
                        if mapper['id'] == orig['id']:
                            del original_mappers[i]
                            if mapper != orig:
                                kc.update_identity_provider_mapper(mapper, alias, realm)
                else:
                    if mapper.get('identityProviderAlias') is None:
                        mapper['identityProviderAlias'] = alias
                    kc.create_identity_provider_mapper(mapper, alias, realm)
            for mapper in [x for x in before_idp['mappers']
                           if [y for y in updated_mappers if y["name"] == x['name']] == []]:
                kc.delete_identity_provider_mapper(mapper['id'], alias, realm)

            after_idp = get_identity_provider_with_mappers(kc, alias, realm)

            result['end_state'] = sanitize(after_idp)

            result['msg'] = "Identity provider {alias} has been updated".format(alias=alias)
            module.exit_json(**result)

        elif state == 'absent':
            # Process a deletion
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=sanitize(before_idp), after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            kc.delete_identity_provider(alias, realm)

            result['end_state'] = {}

            result['msg'] = "Identity provider {alias} has been deleted".format(alias=alias)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

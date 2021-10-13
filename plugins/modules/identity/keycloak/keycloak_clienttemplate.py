#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_clienttemplate

short_description: Allows administration of Keycloak client templates via Keycloak API


description:
    - This module allows the administration of Keycloak client templates via the Keycloak REST API. It
      requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html)

    - The Keycloak API does not always enforce for only sensible settings to be used -- you can set
      SAML-specific settings on an OpenID Connect client for instance and vice versa. Be careful.
      If you do not specify a setting, usually a sensible default is chosen.

options:
    state:
        description:
            - State of the client template.
            - On C(present), the client template will be created (or updated if it exists already).
            - On C(absent), the client template will be removed if it exists
        choices: ['present', 'absent']
        default: 'present'
        type: str

    id:
        description:
            - Id of client template to be worked on. This is usually a UUID.
        type: str

    realm:
        description:
            - Realm this client template is found in.
        type: str
        default: master

    name:
        description:
            - Name of the client template.
        type: str

    description:
        description:
            - Description of the client template in Keycloak.
        type: str

    protocol:
        description:
            - Type of client template (either C(openid-connect) or C(saml).
        choices: ['openid-connect', 'saml']
        type: str

    full_scope_allowed:
        description:
            - Is the "Full Scope Allowed" feature set for this client template or not.
              This is 'fullScopeAllowed' in the Keycloak REST API.
        type: bool

    protocol_mappers:
        description:
            - a list of dicts defining protocol mappers for this client template.
              This is 'protocolMappers' in the Keycloak REST API.
        type: list
        elements: dict
        suboptions:
            consentRequired:
                description:
                    - Specifies whether a user needs to provide consent to a client for this mapper to be active.
                type: bool

            consentText:
                description:
                    - The human-readable name of the consent the user is presented to accept.
                type: str

            id:
                description:
                    - Usually a UUID specifying the internal ID of this protocol mapper instance.
                type: str

            name:
                description:
                    - The name of this protocol mapper.
                type: str

            protocol:
                description:
                    - This is either C(openid-connect) or C(saml), this specifies for which protocol this protocol mapper.
                      is active.
                choices: ['openid-connect', 'saml']
                type: str

            protocolMapper:
                description:
                    - The Keycloak-internal name of the type of this protocol-mapper. While an exhaustive list is
                      impossible to provide since this may be extended through SPIs by the user of Keycloak,
                      by default Keycloak as of 3.4 ships with at least
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

            config:
                description:
                    - Dict specifying the configuration options for the protocol mapper; the
                      contents differ depending on the value of I(protocolMapper) and are not documented
                      other than by the source of the mappers and its parent class(es). An example is given
                      below. It is easiest to obtain valid config values by dumping an already-existing
                      protocol mapper configuration through check-mode in the I(existing) field.
                type: dict

    attributes:
        description:
            - A dict of further attributes for this client template. This can contain various
              configuration settings, though in the default installation of Keycloak as of 3.4, none
              are documented or known, so this is usually empty.
        type: dict

notes:
- The Keycloak REST API defines further fields (namely I(bearerOnly), I(consentRequired), I(standardFlowEnabled),
  I(implicitFlowEnabled), I(directAccessGrantsEnabled), I(serviceAccountsEnabled), I(publicClient), and
  I(frontchannelLogout)) which, while available with keycloak_client, do not have any effect on
  Keycloak client-templates and are discarded if supplied with an API request changing client-templates. As such,
  they are not available through this module.

extends_documentation_fragment:
- community.general.keycloak

author:
    - Eike Frost (@eikef)
'''

EXAMPLES = '''
- name: Create or update Keycloak client template (minimal), authentication with credentials
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: master
    name: this_is_a_test
  delegate_to: localhost

- name: Create or update Keycloak client template (minimal), authentication with token
  community.general.keycloak_clienttemplate:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    token: TOKEN
    realm: master
    name: this_is_a_test
  delegate_to: localhost

- name: Delete Keycloak client template
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: master
    state: absent
    name: test01
  delegate_to: localhost

- name: Create or update Keycloak client template (with a protocol mapper)
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: master
    name: this_is_a_test
    protocol_mappers:
      - config:
          access.token.claim: True
          claim.name: "family_name"
          id.token.claim: True
          jsonType.label: String
          user.attribute: lastName
          userinfo.token.claim: True
        consentRequired: True
        consentText: "${familyName}"
        name: family name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
    full_scope_allowed: false
    id: bce6f5e9-d7d3-4955-817e-c5b7f8d65b3f
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str
    sample: "Client template testclient has been updated"

proposed:
    description: Representation of proposed client template.
    returned: always
    type: dict
    sample: {
      name: "test01"
    }

existing:
    description: Representation of existing client template (sample is truncated).
    returned: always
    type: dict
    sample: {
        "description": "test01",
        "fullScopeAllowed": false,
        "id": "9c3712ab-decd-481e-954f-76da7b006e5f",
        "name": "test01",
        "protocol": "saml"
    }

end_state:
    description: Representation of client template after module execution (sample is truncated).
    returned: on success
    type: dict
    sample: {
        "description": "test01",
        "fullScopeAllowed": false,
        "id": "9c3712ab-decd-481e-954f-76da7b006e5f",
        "name": "test01",
        "protocol": "saml"
    }
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

    protmapper_spec = dict(
        consentRequired=dict(type='bool'),
        consentText=dict(type='str'),
        id=dict(type='str'),
        name=dict(type='str'),
        protocol=dict(type='str', choices=['openid-connect', 'saml']),
        protocolMapper=dict(type='str'),
        config=dict(type='dict'),
    )

    meta_args = dict(
        realm=dict(type='str', default='master'),
        state=dict(default='present', choices=['present', 'absent']),

        id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        protocol=dict(type='str', choices=['openid-connect', 'saml']),
        attributes=dict(type='dict'),
        full_scope_allowed=dict(type='bool'),
        protocol_mappers=dict(type='list', elements='dict', options=protmapper_spec),
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

    # Filter and map the parameters names that apply to the client template
    clientt_params = [x for x in module.params
                      if x not in ['state', 'auth_keycloak_url', 'auth_client_id', 'auth_realm',
                                   'auth_client_secret', 'auth_username', 'auth_password',
                                   'validate_certs', 'realm'] and module.params.get(x) is not None]

    # See if it already exists in Keycloak
    if cid is None:
        before_clientt = kc.get_client_template_by_name(module.params.get('name'), realm=realm)
        if before_clientt is not None:
            cid = before_clientt['id']
    else:
        before_clientt = kc.get_client_template_by_id(cid, realm=realm)

    if before_clientt is None:
        before_clientt = {}

    result['existing'] = before_clientt

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for clientt_param in clientt_params:
        # lists in the Keycloak API are sorted
        new_param_value = module.params.get(clientt_param)
        if isinstance(new_param_value, list):
            try:
                new_param_value = sorted(new_param_value)
            except TypeError:
                pass
        changeset[camel(clientt_param)] = new_param_value

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_clientt = before_clientt.copy()
    desired_clientt.update(changeset)

    result['proposed'] = changeset

    # Cater for when it doesn't exist (an empty dict)
    if not before_clientt:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = 'Client template does not exist, doing nothing.'
            module.exit_json(**result)

        # Process a creation
        result['changed'] = True

        if 'name' not in desired_clientt:
            module.fail_json(msg='name needs to be specified when creating a new client')

        if module._diff:
            result['diff'] = dict(before='', after=desired_clientt)

        if module.check_mode:
            module.exit_json(**result)

        # create it
        kc.create_client_template(desired_clientt, realm=realm)
        after_clientt = kc.get_client_template_by_name(desired_clientt['name'], realm=realm)

        result['end_state'] = after_clientt

        result['msg'] = 'Client template %s has been created.' % desired_clientt['name']
        module.exit_json(**result)

    else:
        if state == 'present':
            # Process an update

            result['changed'] = True
            if module.check_mode:
                # We can only compare the current client template with the proposed updates we have
                if module._diff:
                    result['diff'] = dict(before=before_clientt,
                                          after=desired_clientt)

                module.exit_json(**result)

            # do the update
            kc.update_client_template(cid, desired_clientt, realm=realm)

            after_clientt = kc.get_client_template_by_id(cid, realm=realm)
            if before_clientt == after_clientt:
                result['changed'] = False

            result['end_state'] = after_clientt

            if module._diff:
                result['diff'] = dict(before=before_clientt, after=after_clientt)

            result['msg'] = 'Client template %s has been updated.' % desired_clientt['name']
            module.exit_json(**result)

        else:
            # Process a deletion (because state was not 'present')
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_clientt, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            kc.delete_client_template(cid, realm=realm)
            result['proposed'] = {}

            result['end_state'] = {}

            result['msg'] = 'Client template %s has been deleted.' % before_clientt['name']

    module.exit_json(**result)


if __name__ == '__main__':
    main()

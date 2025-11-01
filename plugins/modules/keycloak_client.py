#!/usr/bin/python

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_client

short_description: Allows administration of Keycloak clients using Keycloak API


description:
  - This module allows the administration of Keycloak clients using the Keycloak REST API. It requires access to the REST
    API using OpenID Connect; the user connecting and the client being used must have the requisite access rights. In a default
    Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with the scope tailored
    to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html). Aliases are provided so camelCased versions can be used
    as well.
  - The Keycloak API does not always sanity check inputs, for example you can set SAML-specific settings on an OpenID Connect
    client for instance and the other way around. Be careful. If you do not specify a setting, usually a sensible default
    is chosen.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the client.
      - On V(present), the client are created (or updated if it exists already).
      - On V(absent), the client are removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  realm:
    description:
      - The realm to create the client in.
    type: str
    default: master

  client_id:
    description:
      - Client ID of client to be worked on. This is usually an alphanumeric name chosen by you. Either this or O(id) is required.
        If you specify both, O(id) takes precedence. This is C(clientId) in the Keycloak REST API.
    aliases:
      - clientId
    type: str

  id:
    description:
      - ID of client to be worked on. This is usually an UUID. Either this or O(client_id) is required. If you specify both,
        this takes precedence.
    type: str

  name:
    description:
      - Name of the client (this is not the same as O(client_id)).
    type: str

  description:
    description:
      - Description of the client in Keycloak.
    type: str

  root_url:
    description:
      - Root URL appended to relative URLs for this client. This is C(rootUrl) in the Keycloak REST API.
    aliases:
      - rootUrl
    type: str

  admin_url:
    description:
      - URL to the admin interface of the client. This is C(adminUrl) in the Keycloak REST API.
    aliases:
      - adminUrl
    type: str

  base_url:
    description:
      - Default URL to use when the auth server needs to redirect or link back to the client This is C(baseUrl) in the Keycloak
        REST API.
    aliases:
      - baseUrl
    type: str

  enabled:
    description:
      - Is this client enabled or not?
    type: bool

  client_authenticator_type:
    description:
      - How do clients authenticate with the auth server? Either V(client-secret), V(client-jwt), or V(client-x509) can be
        chosen. When using V(client-secret), the module parameter O(secret) can set it, for V(client-jwt), you can use the
        keys C(use.jwks.url), C(jwks.url), and C(jwt.credential.certificate) in the O(attributes) module parameter to configure
        its behavior. For V(client-x509) you can use the keys C(x509.allow.regex.pattern.comparison) and C(x509.subjectdn)
        in the O(attributes) module parameter to configure which certificate(s) to accept.
      - This is C(clientAuthenticatorType) in the Keycloak REST API.
    choices: ['client-secret', 'client-jwt', 'client-x509']
    aliases:
      - clientAuthenticatorType
    type: str

  secret:
    description:
      - When using O(client_authenticator_type=client-secret) (the default), you can specify a secret here (otherwise one
        is generated if it does not exit). If changing this secret, the module does not register a change currently (but the
        changed secret is saved).
    type: str

  registration_access_token:
    description:
      - The registration access token provides access for clients to the client registration service. This is C(registrationAccessToken)
        in the Keycloak REST API.
    aliases:
      - registrationAccessToken
    type: str

  default_roles:
    description:
      - List of default roles for this client. If the client roles referenced do not exist yet, they are created. This is
        C(defaultRoles) in the Keycloak REST API.
    aliases:
      - defaultRoles
    type: list
    elements: str

  redirect_uris:
    description:
      - Acceptable redirect URIs for this client. This is C(redirectUris) in the Keycloak REST API.
    aliases:
      - redirectUris
    type: list
    elements: str

  web_origins:
    description:
      - List of allowed CORS origins. This is C(webOrigins) in the Keycloak REST API.
    aliases:
      - webOrigins
    type: list
    elements: str

  not_before:
    description:
      - Revoke any tokens issued before this date for this client (this is a UNIX timestamp). This is C(notBefore) in the
        Keycloak REST API.
    type: int
    aliases:
      - notBefore

  bearer_only:
    description:
      - The access type of this client is bearer-only. This is C(bearerOnly) in the Keycloak REST API.
    aliases:
      - bearerOnly
    type: bool

  consent_required:
    description:
      - If enabled, users have to consent to client access. This is C(consentRequired) in the Keycloak REST API.
    aliases:
      - consentRequired
    type: bool

  standard_flow_enabled:
    description:
      - Enable standard flow for this client or not (OpenID connect). This is C(standardFlowEnabled) in the Keycloak REST
        API.
    aliases:
      - standardFlowEnabled
    type: bool

  implicit_flow_enabled:
    description:
      - Enable implicit flow for this client or not (OpenID connect). This is C(implicitFlowEnabled) in the Keycloak REST
        API.
    aliases:
      - implicitFlowEnabled
    type: bool

  direct_access_grants_enabled:
    description:
      - Are direct access grants enabled for this client or not (OpenID connect). This is C(directAccessGrantsEnabled) in
        the Keycloak REST API.
    aliases:
      - directAccessGrantsEnabled
    type: bool

  service_accounts_enabled:
    description:
      - Are service accounts enabled for this client or not (OpenID connect). This is C(serviceAccountsEnabled) in the Keycloak
        REST API.
    aliases:
      - serviceAccountsEnabled
    type: bool

  authorization_services_enabled:
    description:
      - Are authorization services enabled for this client or not (OpenID connect). This is C(authorizationServicesEnabled)
        in the Keycloak REST API.
    aliases:
      - authorizationServicesEnabled
    type: bool

  public_client:
    description:
      - Is the access type for this client public or not. This is C(publicClient) in the Keycloak REST API.
    aliases:
      - publicClient
    type: bool

  frontchannel_logout:
    description:
      - Is frontchannel logout enabled for this client or not. This is C(frontchannelLogout) in the Keycloak REST API.
    aliases:
      - frontchannelLogout
    type: bool

  protocol:
    description:
      - Type of client.
      - At creation only, default value is V(openid-connect) if O(protocol) is omitted.
      - The V(docker-v2) value was added in community.general 8.6.0.
    type: str
    choices: ['openid-connect', 'saml', 'docker-v2']

  full_scope_allowed:
    description:
      - Is the "Full Scope Allowed" feature set for this client or not. This is C(fullScopeAllowed) in the Keycloak REST API.
    aliases:
      - fullScopeAllowed
    type: bool

  node_re_registration_timeout:
    description:
      - Cluster node re-registration timeout for this client. This is C(nodeReRegistrationTimeout) in the Keycloak REST API.
    type: int
    aliases:
      - nodeReRegistrationTimeout

  registered_nodes:
    description:
      - Dict of registered cluster nodes (with C(nodename) as the key and last registration time as the value). This is C(registeredNodes)
        in the Keycloak REST API.
    type: dict
    aliases:
      - registeredNodes

  client_template:
    description:
      - Client template to use for this client. If it does not exist this field is silently dropped. This is C(clientTemplate)
        in the Keycloak REST API.
    type: str
    aliases:
      - clientTemplate

  use_template_config:
    description:
      - Whether or not to use configuration from the O(client_template). This is C(useTemplateConfig) in the Keycloak REST
        API.
    aliases:
      - useTemplateConfig
    type: bool

  use_template_scope:
    description:
      - Whether or not to use scope configuration from the O(client_template). This is C(useTemplateScope) in the Keycloak
        REST API.
    aliases:
      - useTemplateScope
    type: bool

  use_template_mappers:
    description:
      - Whether or not to use mapper configuration from the O(client_template). This is C(useTemplateMappers) in the Keycloak
        REST API.
    aliases:
      - useTemplateMappers
    type: bool

  always_display_in_console:
    description:
      - Whether or not to display this client in account console, even if the user does not have an active session.
    aliases:
      - alwaysDisplayInConsole
    type: bool
    version_added: 4.7.0

  surrogate_auth_required:
    description:
      - Whether or not surrogate auth is required. This is C(surrogateAuthRequired) in the Keycloak REST API.
    aliases:
      - surrogateAuthRequired
    type: bool

  authorization_settings:
    description:
      - A data structure defining the authorization settings for this client. For reference, please see the Keycloak API docs
        at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html#_resourceserverrepresentation). This is C(authorizationSettings)
        in the Keycloak REST API.
    type: dict
    aliases:
      - authorizationSettings

  authentication_flow_binding_overrides:
    description:
      - Override realm authentication flow bindings.
    type: dict
    suboptions:
      browser:
        description:
          - Flow ID of the browser authentication flow.
          - O(authentication_flow_binding_overrides.browser) and O(authentication_flow_binding_overrides.browser_name) are
            mutually exclusive.
        type: str

      browser_name:
        description:
          - Flow name of the browser authentication flow.
          - O(authentication_flow_binding_overrides.browser) and O(authentication_flow_binding_overrides.browser_name) are
            mutually exclusive.
        aliases:
          - browserName
        type: str
        version_added: 9.1.0

      direct_grant:
        description:
          - Flow ID of the direct grant authentication flow.
          - O(authentication_flow_binding_overrides.direct_grant) and O(authentication_flow_binding_overrides.direct_grant_name)
            are mutually exclusive.
        aliases:
          - directGrant
        type: str

      direct_grant_name:
        description:
          - Flow name of the direct grant authentication flow.
          - O(authentication_flow_binding_overrides.direct_grant) and O(authentication_flow_binding_overrides.direct_grant_name)
            are mutually exclusive.
        aliases:
          - directGrantName
        type: str
        version_added: 9.1.0
    aliases:
      - authenticationFlowBindingOverrides
    version_added: 3.4.0

  client_scopes_behavior:
    description:
      - Determine how O(default_client_scopes) and O(optional_client_scopes) behave when updating an existing client.
      - 'V(ignore): Do not change the client scopes of an existing client. This is the default for backward compatibility.'
      - 'V(patch): Add missing scopes, do not remove any missing scopes.'
      - 'V(idempotent): Make the client scopes exactly as specified, adding and removing scopes as needed.'
    aliases:
      - clientScopesBehavior
    type: str
    choices: ['ignore', 'patch', 'idempotent']
    default: 'ignore'
    version_added: 11.4.0

  default_client_scopes:
    description:
      - List of default client scopes.
      - See O(client_scopes_behavior) for how this behaves when updating an existing client.
    aliases:
      - defaultClientScopes
    type: list
    elements: str
    version_added: 4.7.0

  optional_client_scopes:
    description:
      - List of optional client scopes.
      - See O(client_scopes_behavior) for how this behaves when updating an existing client.
    aliases:
      - optionalClientScopes
    type: list
    elements: str
    version_added: 4.7.0

  protocol_mappers:
    description:
      - A list of dicts defining protocol mappers for this client. This is C(protocolMappers) in the Keycloak REST API.
    aliases:
      - protocolMappers
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
          - This specifies for which protocol this protocol mapper is active.
        choices: ['openid-connect', 'saml', 'docker-v2']
        type: str

      protocolMapper:
        description:
          - 'The Keycloak-internal name of the type of this protocol-mapper. While an exhaustive list is impossible to provide
            since this may be extended through SPIs by the user of Keycloak, by default Keycloak as of 3.4 ships with at least:'
          - V(docker-v2-allow-all-mapper).
          - V(oidc-address-mapper).
          - V(oidc-full-name-mapper).
          - V(oidc-group-membership-mapper).
          - V(oidc-hardcoded-claim-mapper).
          - V(oidc-hardcoded-role-mapper).
          - V(oidc-role-name-mapper).
          - V(oidc-script-based-protocol-mapper).
          - V(oidc-sha256-pairwise-sub-mapper).
          - V(oidc-usermodel-attribute-mapper).
          - V(oidc-usermodel-client-role-mapper).
          - V(oidc-usermodel-property-mapper).
          - V(oidc-usermodel-realm-role-mapper).
          - V(oidc-usersessionmodel-note-mapper).
          - V(saml-group-membership-mapper).
          - V(saml-hardcode-attribute-mapper).
          - V(saml-hardcode-role-mapper).
          - V(saml-role-list-mapper).
          - V(saml-role-name-mapper).
          - V(saml-user-attribute-mapper).
          - V(saml-user-property-mapper).
          - V(saml-user-session-note-mapper).
          - An exhaustive list of available mappers on your installation can be obtained on the admin console by going to
            Server Info -> Providers and looking under 'protocol-mapper'.
        type: str

      config:
        description:
          - Dict specifying the configuration options for the protocol mapper; the contents differ depending on the value
            of O(protocol_mappers[].protocolMapper) and are not documented other than by the source of the mappers and its
            parent class(es). An example is given below. It is easiest to obtain valid config values by dumping an already-existing
            protocol mapper configuration through check-mode in the RV(existing) field.
        type: dict

  attributes:
    description:
      - A dict of further attributes for this client. This can contain various configuration settings; an example is given
        in the examples section. While an exhaustive list of permissible options is not available; possible options as of
        Keycloak 3.4 are listed below. The Keycloak API does not validate whether a given option is appropriate for the protocol
        used; if specified anyway, Keycloak does not use it.
    type: dict
    suboptions:
      saml.authnstatement:
        description:
          - For SAML clients, boolean specifying whether or not a statement containing method and timestamp should be included
            in the login response.
      saml.client.signature:
        description:
          - For SAML clients, boolean specifying whether a client signature is required and validated.
      saml.encrypt:
        description:
          - Boolean specifying whether SAML assertions should be encrypted with the client's public key.
      saml.force.post.binding:
        description:
          - For SAML clients, boolean specifying whether always to use POST binding for responses.
      saml.onetimeuse.condition:
        description:
          - For SAML clients, boolean specifying whether a OneTimeUse condition should be included in login responses.
      saml.server.signature:
        description:
          - Boolean specifying whether SAML documents should be signed by the realm.
      saml.server.signature.keyinfo.ext:
        description:
          - For SAML clients, boolean specifying whether REDIRECT signing key lookup should be optimized through inclusion
            of the signing key ID in the SAML Extensions element.
      saml.signature.algorithm:
        description:
          - Signature algorithm used to sign SAML documents. One of V(RSA_SHA256), V(RSA_SHA1), V(RSA_SHA512), or V(DSA_SHA1).
      saml.signing.certificate:
        description:
          - SAML signing key certificate, base64-encoded.
      saml.signing.private.key:
        description:
          - SAML signing key private key, base64-encoded.
      saml_assertion_consumer_url_post:
        description:
          - SAML POST Binding URL for the client's assertion consumer service (login responses).
      saml_assertion_consumer_url_redirect:
        description:
          - SAML Redirect Binding URL for the client's assertion consumer service (login responses).
      saml_force_name_id_format:
        description:
          - For SAML clients, Boolean specifying whether to ignore requested NameID subject format and using the configured
            one instead.
      saml_name_id_format:
        description:
          - For SAML clients, the NameID format to use (one of V(username), V(email), V(transient), or V(persistent)).
      saml_signature_canonicalization_method:
        description:
          - SAML signature canonicalization method. This is one of four values, namely V(http://www.w3.org/2001/10/xml-exc-c14n#)
            for EXCLUSIVE, V(http://www.w3.org/2001/10/xml-exc-c14n#WithComments) for EXCLUSIVE_WITH_COMMENTS,
            V(http://www.w3.org/TR/2001/REC-xml-c14n-20010315)
            for INCLUSIVE, and V(http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments) for INCLUSIVE_WITH_COMMENTS.
      saml_single_logout_service_url_post:
        description:
          - SAML POST binding URL for the client's single logout service.
      saml_single_logout_service_url_redirect:
        description:
          - SAML redirect binding URL for the client's single logout service.
      user.info.response.signature.alg:
        description:
          - For OpenID-Connect clients, JWA algorithm for signed UserInfo-endpoint responses. One of V(RS256) or V(unsigned).
      request.object.signature.alg:
        description:
          - For OpenID-Connect clients, JWA algorithm which the client needs to use when sending OIDC request object. One
            of V(any), V(none), V(RS256).
      use.jwks.url:
        description:
          - For OpenID-Connect clients, boolean specifying whether to use a JWKS URL to obtain client public keys.
      jwks.url:
        description:
          - For OpenID-Connect clients, URL where client keys in JWK are stored.
      jwt.credential.certificate:
        description:
          - For OpenID-Connect clients, client certificate for validating JWT issued by client and signed by its key, base64-encoded.
      x509.subjectdn:
        description:
          - For OpenID-Connect clients, subject which is used to authenticate the client.
        type: str
        version_added: 9.5.0

      x509.allow.regex.pattern.comparison:
        description:
          - For OpenID-Connect clients, boolean specifying whether to allow C(x509.subjectdn) as regular expression.
        type: bool
        version_added: 9.5.0

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Eike Frost (@eikef)
"""

EXAMPLES = r"""
- name: Create or update Keycloak client (minimal example), authentication with credentials
  community.general.keycloak_client:
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    client_id: test
    state: present
  delegate_to: localhost


- name: Create or update Keycloak client (minimal example), authentication with token
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    token: TOKEN
    client_id: test
    state: present
  delegate_to: localhost


- name: Delete a Keycloak client
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    client_id: test
    state: absent
  delegate_to: localhost


- name: Create or update a Keycloak client (minimal example), with x509 authentication
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    realm: master
    state: present
    client_id: test
    client_authenticator_type: client-x509
    attributes:
      x509.subjectdn: "CN=client"
      x509.allow.regex.pattern.comparison: false


- name: Create or update a Keycloak client (with all the bells and whistles)
  community.general.keycloak_client:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    state: present
    realm: master
    client_id: test
    id: d8b127a3-31f6-44c8-a7e4-4ab9a3e78d95
    name: this_is_a_test
    description: Description of this wonderful client
    root_url: https://www.example.com/
    admin_url: https://www.example.com/admin_url
    base_url: basepath
    enabled: true
    client_authenticator_type: client-secret
    secret: REALLYWELLKEPTSECRET
    redirect_uris:
      - https://www.example.com/*
      - http://localhost:8888/
    web_origins:
      - https://www.example.com/*
    not_before: 1507825725
    bearer_only: false
    consent_required: false
    standard_flow_enabled: true
    implicit_flow_enabled: false
    direct_access_grants_enabled: false
    service_accounts_enabled: false
    authorization_services_enabled: false
    public_client: false
    frontchannel_logout: false
    protocol: openid-connect
    full_scope_allowed: false
    node_re_registration_timeout: -1
    client_template: test
    use_template_config: false
    use_template_scope: false
    use_template_mappers: false
    always_display_in_console: true
    registered_nodes:
      node01.example.com: 1507828202
    registration_access_token: eyJWT_TOKEN
    surrogate_auth_required: false
    default_roles:
      - test01
      - test02
    authentication_flow_binding_overrides:
      browser: 4c90336b-bf1d-4b87-916d-3677ba4e5fbb
    protocol_mappers:
      - config:
          access.token.claim: true
          claim.name: "family_name"
          id.token.claim: true
          jsonType.label: String
          user.attribute: lastName
          userinfo.token.claim: true
        consentRequired: true
        consentText: "${familyName}"
        name: family name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          attribute.name: Role
          attribute.nameformat: Basic
          single: false
        consentRequired: false
        name: role list
        protocol: saml
        protocolMapper: saml-role-list-mapper
    attributes:
      saml.authnstatement: true
      saml.client.signature: true
      saml.force.post.binding: true
      saml.server.signature: true
      saml.signature.algorithm: RSA_SHA256
      saml.signing.certificate: CERTIFICATEHERE
      saml.signing.private.key: PRIVATEKEYHERE
      saml_force_name_id_format: false
      saml_name_id_format: username
      saml_signature_canonicalization_method: "http://www.w3.org/2001/10/xml-exc-c14n#"
      user.info.response.signature.alg: RS256
      request.object.signature.alg: RS256
      use.jwks.url: true
      jwks.url: JWKS_URL_FOR_CLIENT_AUTH_JWT
      jwt.credential.certificate: JWT_CREDENTIAL_CERTIFICATE_FOR_CLIENT_AUTH
  delegate_to: localhost
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: "Client testclient has been updated"

proposed:
  description: Representation of proposed client.
  returned: always
  type: dict
  sample: {"clientId": "test"}

existing:
  description: Representation of existing client (sample is truncated).
  returned: always
  type: dict
  sample:
    {
      "adminUrl": "http://www.example.com/admin_url",
      "attributes": {
        "request.object.signature.alg": "RS256"
      }
    }

end_state:
  description: Representation of client after module execution (sample is truncated).
  returned: on success
  type: dict
  sample:
    {
      "adminUrl": "http://www.example.com/admin_url",
      "attributes": {
        "request.object.signature.alg": "RS256"
      }
    }
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    camel,
    keycloak_argument_spec,
    get_token,
    KeycloakError,
)
from ansible.module_utils.basic import AnsibleModule
import copy


PROTOCOL_OPENID_CONNECT = "openid-connect"
PROTOCOL_SAML = "saml"
PROTOCOL_DOCKER_V2 = "docker-v2"
CLIENT_META_DATA = ["authorizationServicesEnabled"]


def normalise_scopes_for_behavior(desired_client, before_client, clientScopesBehavior):
    """
    Normalize the desired and existing client scopes according to the specified behavior.

    This function adjusts the lists of default and optional client scopes in the desired client
    configuration based on the selected behavior:
      - 'ignore': The desired scopes are set to match the existing scopes.
      - 'patch': Any scopes present in the existing configuration but missing from the desired configuration
        are appended to the desired scopes.
      - 'idempotent': No modification is made; the desired scopes are used as-is.

    :param desired_client:
        type: dict
        description: The desired client configuration, including default and optional client scopes.

    :param before_client:
        type: dict
        description: The current client configuration, including default and optional client scopes.

    :param clientScopesBehavior:
        type: str
        description: The behavior mode for handling client scopes. Must be one of 'ignore', 'patch', or 'idempotent'.

    :return:
        type: tuple
        description: Returns a tuple of (desired_client, before_client) after normalization.
    """
    desired_client = copy.deepcopy(desired_client)
    before_client = copy.deepcopy(before_client)
    if clientScopesBehavior == "ignore":
        desired_client["defaultClientScopes"] = copy.deepcopy(before_client["defaultClientScopes"])
        desired_client["optionalClientScopes"] = copy.deepcopy(before_client["optionalClientScopes"])
    elif clientScopesBehavior == "patch":
        for scope in before_client["defaultClientScopes"]:
            if scope not in desired_client["defaultClientScopes"]:
                desired_client["defaultClientScopes"].append(scope)
        for scope in before_client["optionalClientScopes"]:
            if scope not in desired_client["optionalClientScopes"]:
                desired_client["optionalClientScopes"].append(scope)

    return desired_client, before_client


def check_optional_scopes_not_default(desired_client, clientScopesBehavior, module):
    """
    Ensure that no client scope is assigned as both default and optional.

    This function checks the desired client configuration to verify that no scope is present
    in both the default and optional client scopes. If such a conflict is found, the module
    execution fails with an appropriate error message.

    :param desired_client:
        type: dict
        description: The desired client configuration, including default and optional client scopes.

    :param clientScopesBehavior:
        type: str
        description: The behavior mode for handling client scopes. Must be one of 'ignore', 'patch', or 'idempotent'.

    :param module:
        type: AnsibleModule
        description: The Ansible module instance, used to fail execution if a conflict is detected.

    :return:
        type: None
        description: Returns None. Fails the module if a scope is both default and optional.
    """
    if clientScopesBehavior == "ignore":
        return
    for scope in desired_client["optionalClientScopes"]:
        if scope in desired_client["defaultClientScopes"]:
            module.fail_json(msg=f"Client scope {scope} cannot be both default and optional")


def normalise_cr(clientrep, remove_ids=False):
    """Re-sorts any properties where the order so that diff's is minimised, and adds default values where appropriate so that the
    the change detection is more effective.

    :param clientrep: the clientrep dict to be sanitized
    :param remove_ids: If set to true, then the unique ID's of objects is removed to make the diff and checks for changed
                       not alert when the ID's of objects are not usually known, (e.g. for protocol_mappers)
    :return: normalised clientrep dict
    """
    # Avoid the dict passed in to be modified
    clientrep = copy.deepcopy(clientrep)

    if remove_ids:
        clientrep.pop("id", None)

    if "defaultClientScopes" in clientrep:
        clientrep["defaultClientScopes"] = list(sorted(clientrep["defaultClientScopes"]))
    else:
        clientrep["defaultClientScopes"] = []

    if "optionalClientScopes" in clientrep:
        clientrep["optionalClientScopes"] = list(sorted(clientrep["optionalClientScopes"]))
    else:
        clientrep["optionalClientScopes"] = []

    if "redirectUris" in clientrep:
        clientrep["redirectUris"] = list(sorted(clientrep["redirectUris"]))
    else:
        clientrep["redirectUris"] = []

    if "protocolMappers" in clientrep:
        clientrep["protocolMappers"] = sorted(
            clientrep["protocolMappers"], key=lambda x: (x.get("name"), x.get("protocol"), x.get("protocolMapper"))
        )
        for mapper in clientrep["protocolMappers"]:
            if remove_ids:
                mapper.pop("id", None)

            # Convert bool to string
            if "config" in mapper:
                for key, value in mapper["config"].items():
                    if isinstance(value, bool):
                        mapper["config"][key] = str(value).lower()

            # Set to a default value.
            mapper["consentRequired"] = mapper.get("consentRequired", False)
    else:
        clientrep["protocolMappers"] = []

    if "attributes" in clientrep:
        for key, value in clientrep["attributes"].items():
            if isinstance(value, bool):
                clientrep["attributes"][key] = str(value).lower()
        clientrep["attributes"].pop("client.secret.creation.time", None)
    else:
        clientrep["attributes"] = []

    if "webOrigins" in clientrep:
        clientrep["webOrigins"] = sorted(clientrep["webOrigins"])
    else:
        clientrep["webOrigins"] = []

    if "redirectUris" in clientrep:
        clientrep["redirectUris"] = sorted(clientrep["redirectUris"])
    else:
        clientrep["redirectUris"] = []

    return clientrep


def normalize_kc_resp(clientrep):
    # kc drops the variable 'authorizationServicesEnabled' if set to false
    # to minimize diff/changes we set it to false if not set by kc
    if clientrep and "authorizationServicesEnabled" not in clientrep:
        clientrep["authorizationServicesEnabled"] = False


def sanitize_cr(clientrep):
    """Removes probably sensitive details from a client representation.

    :param clientrep: the clientrep dict to be sanitized
    :return: sanitized clientrep dict
    """
    result = copy.deepcopy(clientrep)
    if "secret" in result:
        result["secret"] = "no_log"
    if "attributes" in result:
        attributes = result["attributes"]
        if isinstance(attributes, dict):
            if "saml.signing.private.key" in attributes:
                attributes["saml.signing.private.key"] = "no_log"
            if "saml.encryption.private.key" in attributes:
                attributes["saml.encryption.private.key"] = "no_log"
    return normalise_cr(result)


def get_authentication_flow_id(flow_name, realm, kc):
    """Get the authentication flow ID based on the flow name, realm, and Keycloak client.

    Args:
        flow_name (str): The name of the authentication flow.
        realm (str): The name of the realm.
        kc (KeycloakClient): The Keycloak client instance.

    Returns:
        str: The ID of the authentication flow.

    Raises:
        KeycloakAPIException: If the authentication flow with the given name is not found in the realm.
    """
    flow = kc.get_authentication_flow_by_alias(flow_name, realm)
    if flow:
        return flow["id"]
    kc.module.fail_json(msg=f"Authentification flow {flow_name} not found in realm {realm}")


def flow_binding_from_dict_to_model(newClientFlowBinding, realm, kc):
    """Convert a dictionary representing client flow bindings to a model representation.

    Args:
        newClientFlowBinding (dict): A dictionary containing client flow bindings.
        realm (str): The name of the realm.
        kc (KeycloakClient): An instance of the KeycloakClient class.

    Returns:
        dict: A dictionary representing the model flow bindings. The dictionary has two keys:
            - "browser" (str or None): The ID of the browser authentication flow binding, or None if not provided.
            - "direct_grant" (str or None): The ID of the direct grant authentication flow binding, or None if not provided.

    Raises:
        KeycloakAPIException: If the authentication flow with the given name is not found in the realm.

    """

    modelFlow = {"browser": None, "direct_grant": None}

    for k, v in newClientFlowBinding.items():
        if not v:
            continue
        if k == "browser":
            modelFlow["browser"] = v
        elif k == "browser_name":
            modelFlow["browser"] = get_authentication_flow_id(v, realm, kc)
        elif k == "direct_grant":
            modelFlow["direct_grant"] = v
        elif k == "direct_grant_name":
            modelFlow["direct_grant"] = get_authentication_flow_id(v, realm, kc)

    return modelFlow


def find_match(iterable, attribute, name):
    """
    Search for an element in a list of dictionaries based on a given attribute and value.

    This function iterates over the elements of an iterable (typically a list of dictionaries)
    and returns the first element whose value for the specified attribute matches `name`.

    :param iterable:
        type: iterable (commonly list[dict])
        description: The collection of elements to search within (usually a list of dictionaries).

    :param attribute:
        type: str
        description: The dictionary key/attribute used for comparison.

    :param name:
        type: Any
        description: The value to search for within the given attribute.

    :return:
        type: dict | None
        description: Returns the first dictionary where the attribute matches the given value case insensitive.
                     Returns `None` if no match is found.
    """
    name_lower = str(name).lower()
    return next(
        (value for value in iterable if attribute in value and str(value[attribute]).lower() == name_lower),
        None,
    )


def add_default_client_scopes(desired_client, before_client, realm, kc):
    """
    Adds missing default client scopes to a Keycloak client.

    This function compares the desired default client scopes specified in `desired_client`
    with the current default client scopes in `before_client`. For each scope that is present
    in `desired_client["defaultClientScopes"]` but missing from `before_client['defaultClientScopes']`,
    it retrieves the scope information from Keycloak and adds it to the client.

    :param desired_client:
        type: dict
        description: The desired client configuration, including the list of default client scopes.

    :param before_client:
        type: dict
        description: The current client configuration, including the list of default client scopes.

    :param realm
        type: str
        description: The name of the Keycloak realm.

    :param kc
        type: KeycloakAPI
        description: An instance of the Keycloak API client.

    Returns:
        None
    """
    desired_default_scope = desired_client["defaultClientScopes"]
    missing_scopes = [item for item in desired_default_scope if item not in before_client["defaultClientScopes"]]
    if not missing_scopes:
        return
    client_scopes = kc.get_clientscopes(realm)
    for name in missing_scopes:
        scope = find_match(client_scopes, "name", name)
        if scope:
            kc.add_default_clientscope(scope["id"], realm, desired_client["clientId"])


def add_optional_client_scopes(desired_client, before_client, realm, kc):
    """
    Adds missing optional client scopes to a Keycloak client.

    This function compares the desired optional client scopes specified in `desired_client`
    with the current optional client scopes in `before_client`. For each scope that is present
    in `desired_client["optionalClientScopes"]` but missing from `before_client['optionalClientScopes']`,
    it retrieves the scope information from Keycloak and adds it to the client.

    :param desired_client:
        type: dict
        description: The desired client configuration, including the list of optional client scopes.

    :param before_client:
        type: dict
        description: The current client configuration, including the list of optional client scopes.

    :param realm:
        type: str
        description: The name of the Keycloak realm.

    :param kc:
        type: KeycloakAPI
        description: An instance of the Keycloak API client.

    Returns:
        None
    """
    desired_optional_scope = desired_client["optionalClientScopes"]
    missing_scopes = [item for item in desired_optional_scope if item not in before_client["optionalClientScopes"]]
    if not missing_scopes:
        return
    client_scopes = kc.get_clientscopes(realm)
    for name in missing_scopes:
        scope = find_match(client_scopes, "name", name)
        if scope:
            kc.add_optional_clientscope(scope["id"], realm, desired_client["clientId"])


def remove_default_client_scopes(desired_client, before_client, realm, kc):
    """
    Removes default client scopes from a Keycloak client that are no longer desired.

    This function compares the current default client scopes in `before_client`
    with the desired default client scopes in `desired_client`. For each scope that is present
    in `before_client["defaultClientScopes"]` but missing from `desired_client['defaultClientScopes']`,
    it retrieves the scope information from Keycloak and removes it from the client.

    :param desired_client:
        type: dict
        description: The desired client configuration, including the list of default client scopes.

    :param before_client:
        type: dict
        description: The current client configuration, including the list of default client scopes.

    :param realm:
        type: str
        description: The name of the Keycloak realm.

    :param kc:
        type: KeycloakAPI
        description: An instance of the Keycloak API client.

    Returns:
        None
    """
    before_default_scope = before_client["defaultClientScopes"]
    missing_scopes = [item for item in before_default_scope if item not in desired_client["defaultClientScopes"]]
    if not missing_scopes:
        return
    client_scopes = kc.get_default_clientscopes(realm, desired_client["clientId"])
    for name in missing_scopes:
        scope = find_match(client_scopes, "name", name)
        if scope:
            kc.delete_default_clientscope(scope["id"], realm, desired_client["clientId"])


def remove_optional_client_scopes(desired_client, before_client, realm, kc):
    """
    Removes optional client scopes from a Keycloak client that are no longer desired.

    This function compares the current optional client scopes in `before_client`
    with the desired optional client scopes in `desired_client`. For each scope that is present
    in `before_client["optionalClientScopes"]` but missing from `desired_client['optionalClientScopes']`,
    it retrieves the scope information from Keycloak and removes it from the client.

    :param desired_client:
        type: dict
        description: The desired client configuration, including the list of optional client scopes.

    :param before_client:
        type: dict
        description: The current client configuration, including the list of optional client scopes.

    :param realm:
        type: str
        description: The name of the Keycloak realm.

    :param kc:
        type: KeycloakAPI
        description: An instance of the Keycloak API client.

    Returns:
        None
    """
    before_optional_scope = before_client["optionalClientScopes"]
    missing_scopes = [item for item in before_optional_scope if item not in desired_client["optionalClientScopes"]]
    if not missing_scopes:
        return
    client_scopes = kc.get_optional_clientscopes(realm, desired_client["clientId"])
    for name in missing_scopes:
        scope = find_match(client_scopes, "name", name)
        if scope:
            kc.delete_optional_clientscope(scope["id"], realm, desired_client["clientId"])


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    protmapper_spec = dict(
        consentRequired=dict(type="bool"),
        consentText=dict(type="str"),
        id=dict(type="str"),
        name=dict(type="str"),
        protocol=dict(type="str", choices=[PROTOCOL_OPENID_CONNECT, PROTOCOL_SAML, PROTOCOL_DOCKER_V2]),
        protocolMapper=dict(type="str"),
        config=dict(type="dict"),
    )

    authentication_flow_spec = dict(
        browser=dict(type="str"),
        browser_name=dict(type="str", aliases=["browserName"]),
        direct_grant=dict(type="str", aliases=["directGrant"]),
        direct_grant_name=dict(type="str", aliases=["directGrantName"]),
    )

    meta_args = dict(
        state=dict(default="present", choices=["present", "absent"]),
        realm=dict(type="str", default="master"),
        id=dict(type="str"),
        client_id=dict(type="str", aliases=["clientId"]),
        name=dict(type="str"),
        description=dict(type="str"),
        root_url=dict(type="str", aliases=["rootUrl"]),
        admin_url=dict(type="str", aliases=["adminUrl"]),
        base_url=dict(type="str", aliases=["baseUrl"]),
        surrogate_auth_required=dict(type="bool", aliases=["surrogateAuthRequired"]),
        enabled=dict(type="bool"),
        client_authenticator_type=dict(
            type="str", choices=["client-secret", "client-jwt", "client-x509"], aliases=["clientAuthenticatorType"]
        ),
        secret=dict(type="str", no_log=True),
        registration_access_token=dict(type="str", aliases=["registrationAccessToken"], no_log=True),
        default_roles=dict(type="list", elements="str", aliases=["defaultRoles"]),
        redirect_uris=dict(type="list", elements="str", aliases=["redirectUris"]),
        web_origins=dict(type="list", elements="str", aliases=["webOrigins"]),
        not_before=dict(type="int", aliases=["notBefore"]),
        bearer_only=dict(type="bool", aliases=["bearerOnly"]),
        consent_required=dict(type="bool", aliases=["consentRequired"]),
        standard_flow_enabled=dict(type="bool", aliases=["standardFlowEnabled"]),
        implicit_flow_enabled=dict(type="bool", aliases=["implicitFlowEnabled"]),
        direct_access_grants_enabled=dict(type="bool", aliases=["directAccessGrantsEnabled"]),
        service_accounts_enabled=dict(type="bool", aliases=["serviceAccountsEnabled"]),
        authorization_services_enabled=dict(type="bool", aliases=["authorizationServicesEnabled"]),
        public_client=dict(type="bool", aliases=["publicClient"]),
        frontchannel_logout=dict(type="bool", aliases=["frontchannelLogout"]),
        protocol=dict(type="str", choices=[PROTOCOL_OPENID_CONNECT, PROTOCOL_SAML, PROTOCOL_DOCKER_V2]),
        attributes=dict(type="dict"),
        full_scope_allowed=dict(type="bool", aliases=["fullScopeAllowed"]),
        node_re_registration_timeout=dict(type="int", aliases=["nodeReRegistrationTimeout"]),
        registered_nodes=dict(type="dict", aliases=["registeredNodes"]),
        client_template=dict(type="str", aliases=["clientTemplate"]),
        use_template_config=dict(type="bool", aliases=["useTemplateConfig"]),
        use_template_scope=dict(type="bool", aliases=["useTemplateScope"]),
        use_template_mappers=dict(type="bool", aliases=["useTemplateMappers"]),
        always_display_in_console=dict(type="bool", aliases=["alwaysDisplayInConsole"]),
        authentication_flow_binding_overrides=dict(
            type="dict",
            aliases=["authenticationFlowBindingOverrides"],
            options=authentication_flow_spec,
            required_one_of=[["browser", "direct_grant", "browser_name", "direct_grant_name"]],
            mutually_exclusive=[["browser", "browser_name"], ["direct_grant", "direct_grant_name"]],
        ),
        protocol_mappers=dict(type="list", elements="dict", options=protmapper_spec, aliases=["protocolMappers"]),
        authorization_settings=dict(type="dict", aliases=["authorizationSettings"]),
        client_scopes_behavior=dict(
            type="str", aliases=["clientScopesBehavior"], choices=["ignore", "patch", "idempotent"], default="ignore"
        ),
        default_client_scopes=dict(type="list", elements="str", aliases=["defaultClientScopes"]),
        optional_client_scopes=dict(type="list", elements="str", aliases=["optionalClientScopes"]),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [
                ["client_id", "id"],
                ["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"],
            ]
        ),
        required_together=([["auth_username", "auth_password"]]),
        required_by={"refresh_token": "auth_realm"},
    )

    result = dict(changed=False, msg="", diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    cid = module.params.get("id")
    clientScopesBehavior = module.params.get("client_scopes_behavior")
    state = module.params.get("state")

    # Filter and map the parameters names that apply to the client
    client_params = [
        x
        for x in module.params
        if x not in list(keycloak_argument_spec().keys()) + ["state", "realm"] and module.params.get(x) is not None
    ]

    # See if it already exists in Keycloak
    if cid is None:
        before_client = kc.get_client_by_clientid(module.params.get("client_id"), realm=realm)
        if before_client is not None:
            cid = before_client["id"]
    else:
        before_client = kc.get_client_by_id(cid, realm=realm)

    normalize_kc_resp(before_client)

    if before_client is None:
        before_client = {}

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for client_param in client_params:
        new_param_value = module.params.get(client_param)

        # Unfortunately, the ansible argument spec checker introduces variables with null values when
        # they are not specified
        if client_param == "protocol_mappers":
            new_param_value = [{k: v for k, v in x.items() if v is not None} for x in new_param_value]
        elif client_param == "authentication_flow_binding_overrides":
            new_param_value = flow_binding_from_dict_to_model(new_param_value, realm, kc)
        elif client_param == "attributes" and "attributes" in before_client:
            attributes_copy = copy.deepcopy(before_client["attributes"])
            attributes_copy.update(new_param_value)
            new_param_value = attributes_copy
        elif client_param in ["clientScopesBehavior", "client_scopes_behavior"]:
            continue

        changeset[camel(client_param)] = new_param_value

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_client = copy.deepcopy(before_client)
    desired_client.update(changeset)

    result["proposed"] = sanitize_cr(changeset)
    result["existing"] = sanitize_cr(before_client)

    # Cater for when it doesn't exist (an empty dict)
    if not before_client:
        if state == "absent":
            # Do nothing and exit
            if module._diff:
                result["diff"] = dict(before="", after="")
            result["changed"] = False
            result["end_state"] = {}
            result["msg"] = "Client does not exist; doing nothing."
            module.exit_json(**result)

        # Process a creation
        result["changed"] = True

        if "clientId" not in desired_client:
            module.fail_json(msg="client_id needs to be specified when creating a new client")
        if "protocol" not in desired_client:
            desired_client["protocol"] = PROTOCOL_OPENID_CONNECT

        if module._diff:
            result["diff"] = dict(before="", after=sanitize_cr(desired_client))

        if module.check_mode:
            module.exit_json(**result)

        # create it
        kc.create_client(desired_client, realm=realm)
        after_client = kc.get_client_by_clientid(desired_client["clientId"], realm=realm)

        result["end_state"] = sanitize_cr(after_client)

        result["msg"] = f"Client {desired_client['clientId']} has been created."
        module.exit_json(**result)

    else:
        if state == "present":
            # We can only compare the current client with the proposed updates we have
            desired_client_with_scopes, before_client_with_scopes = normalise_scopes_for_behavior(
                desired_client, before_client, clientScopesBehavior
            )
            check_optional_scopes_not_default(desired_client, clientScopesBehavior, module)
            before_norm = normalise_cr(before_client_with_scopes, remove_ids=True)
            desired_norm = normalise_cr(desired_client_with_scopes, remove_ids=True)
            # no changes
            if before_norm == desired_norm:
                result["changed"] = False
                result["end_state"] = sanitize_cr(before_client)
                result["msg"] = f"No changes required for Client {desired_client['clientId']}."
                module.exit_json(**result)

            # Process an update
            result["changed"] = True

            if module.check_mode:
                result["end_state"] = sanitize_cr(desired_client_with_scopes)
                if module._diff:
                    result["diff"] = dict(before=sanitize_cr(before_client), after=sanitize_cr(desired_client))
                module.exit_json(**result)

            # do the update
            kc.update_client(cid, desired_client, realm=realm)

            remove_default_client_scopes(desired_client_with_scopes, before_client_with_scopes, realm, kc)
            remove_optional_client_scopes(desired_client_with_scopes, before_client_with_scopes, realm, kc)
            add_default_client_scopes(desired_client_with_scopes, before_client_with_scopes, realm, kc)
            add_optional_client_scopes(desired_client_with_scopes, before_client_with_scopes, realm, kc)

            after_client = kc.get_client_by_id(cid, realm=realm)
            normalize_kc_resp(after_client)

            if module._diff:
                result["diff"] = dict(before=sanitize_cr(before_client), after=sanitize_cr(after_client))

            result["end_state"] = sanitize_cr(after_client)

            result["msg"] = f"Client {desired_client['clientId']} has been updated."
            module.exit_json(**result)

        else:
            # Process a deletion (because state was not 'present')
            result["changed"] = True

            if module._diff:
                result["diff"] = dict(before=sanitize_cr(before_client), after="")

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            kc.delete_client(cid, realm=realm)
            result["proposed"] = {}

            result["end_state"] = {}

            result["msg"] = f"Client {before_client['clientId']} has been deleted."

    module.exit_json(**result)


if __name__ == "__main__":
    main()

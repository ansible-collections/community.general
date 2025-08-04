# -*- coding: utf-8 -*-
# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# BSD 2-Clause license (see LICENSES/BSD-2-Clause.txt)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import traceback
import copy

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.common.text.converters import to_native, to_text

URL_REALM_INFO = "{url}/realms/{realm}"
URL_REALMS = "{url}/admin/realms"
URL_REALM = "{url}/admin/realms/{realm}"
URL_REALM_KEYS_METADATA = "{url}/admin/realms/{realm}/keys"

URL_TOKEN = "{url}/realms/{realm}/protocol/openid-connect/token"
URL_CLIENT = "{url}/admin/realms/{realm}/clients/{id}"
URL_CLIENTS = "{url}/admin/realms/{realm}/clients"

URL_CLIENT_ROLES = "{url}/admin/realms/{realm}/clients/{id}/roles"
URL_CLIENT_ROLE = "{url}/admin/realms/{realm}/clients/{id}/roles/{name}"
URL_CLIENT_ROLE_COMPOSITES = "{url}/admin/realms/{realm}/clients/{id}/roles/{name}/composites"

URL_CLIENT_ROLE_SCOPE_CLIENTS = "{url}/admin/realms/{realm}/clients/{id}/scope-mappings/clients/{scopeid}"
URL_CLIENT_ROLE_SCOPE_REALM = "{url}/admin/realms/{realm}/clients/{id}/scope-mappings/realm"

URL_REALM_ROLES = "{url}/admin/realms/{realm}/roles"
URL_REALM_ROLE = "{url}/admin/realms/{realm}/roles/{name}"
URL_REALM_ROLEMAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/realm"
URL_REALM_ROLEMAPPINGS_AVAILABLE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/realm/available"
URL_REALM_ROLEMAPPINGS_COMPOSITE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/realm/composite"
URL_REALM_ROLE_COMPOSITES = "{url}/admin/realms/{realm}/roles/{name}/composites"

URL_ROLES_BY_ID = "{url}/admin/realms/{realm}/roles-by-id/{id}"
URL_ROLES_BY_ID_COMPOSITES_CLIENTS = "{url}/admin/realms/{realm}/roles-by-id/{id}/composites/clients/{cid}"
URL_ROLES_BY_ID_COMPOSITES = "{url}/admin/realms/{realm}/roles-by-id/{id}/composites"

URL_CLIENTTEMPLATE = "{url}/admin/realms/{realm}/client-templates/{id}"
URL_CLIENTTEMPLATES = "{url}/admin/realms/{realm}/client-templates"
URL_GROUPS = "{url}/admin/realms/{realm}/groups"
URL_GROUP = "{url}/admin/realms/{realm}/groups/{groupid}"
URL_GROUP_CHILDREN = "{url}/admin/realms/{realm}/groups/{groupid}/children"

URL_CLIENTSCOPES = "{url}/admin/realms/{realm}/client-scopes"
URL_CLIENTSCOPE = "{url}/admin/realms/{realm}/client-scopes/{id}"
URL_CLIENTSCOPE_PROTOCOLMAPPERS = "{url}/admin/realms/{realm}/client-scopes/{id}/protocol-mappers/models"
URL_CLIENTSCOPE_PROTOCOLMAPPER = "{url}/admin/realms/{realm}/client-scopes/{id}/protocol-mappers/models/{mapper_id}"

URL_DEFAULT_CLIENTSCOPES = "{url}/admin/realms/{realm}/default-default-client-scopes"
URL_DEFAULT_CLIENTSCOPE = "{url}/admin/realms/{realm}/default-default-client-scopes/{id}"
URL_OPTIONAL_CLIENTSCOPES = "{url}/admin/realms/{realm}/default-optional-client-scopes"
URL_OPTIONAL_CLIENTSCOPE = "{url}/admin/realms/{realm}/default-optional-client-scopes/{id}"

URL_CLIENT_DEFAULT_CLIENTSCOPES = "{url}/admin/realms/{realm}/clients/{cid}/default-client-scopes"
URL_CLIENT_DEFAULT_CLIENTSCOPE = "{url}/admin/realms/{realm}/clients/{cid}/default-client-scopes/{id}"
URL_CLIENT_OPTIONAL_CLIENTSCOPES = "{url}/admin/realms/{realm}/clients/{cid}/optional-client-scopes"
URL_CLIENT_OPTIONAL_CLIENTSCOPE = "{url}/admin/realms/{realm}/clients/{cid}/optional-client-scopes/{id}"

URL_CLIENT_GROUP_ROLEMAPPINGS = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}"
URL_CLIENT_GROUP_ROLEMAPPINGS_AVAILABLE = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}/available"
URL_CLIENT_GROUP_ROLEMAPPINGS_COMPOSITE = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}/composite"

URL_USERS = "{url}/admin/realms/{realm}/users"
URL_USER = "{url}/admin/realms/{realm}/users/{id}"
URL_USER_ROLE_MAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings"
URL_USER_REALM_ROLE_MAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/realm"
URL_USER_CLIENTS_ROLE_MAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients"
URL_USER_CLIENT_ROLE_MAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client_id}"
URL_USER_GROUPS = "{url}/admin/realms/{realm}/users/{id}/groups"
URL_USER_GROUP = "{url}/admin/realms/{realm}/users/{id}/groups/{group_id}"

URL_CLIENT_SERVICE_ACCOUNT_USER = "{url}/admin/realms/{realm}/clients/{id}/service-account-user"
URL_CLIENT_USER_ROLEMAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}"
URL_CLIENT_USER_ROLEMAPPINGS_AVAILABLE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/available"
URL_CLIENT_USER_ROLEMAPPINGS_COMPOSITE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/composite"

URL_REALM_GROUP_ROLEMAPPINGS = "{url}/admin/realms/{realm}/groups/{group}/role-mappings/realm"

URL_CLIENTSECRET = "{url}/admin/realms/{realm}/clients/{id}/client-secret"

URL_AUTHENTICATION_FLOWS = "{url}/admin/realms/{realm}/authentication/flows"
URL_AUTHENTICATION_FLOW = "{url}/admin/realms/{realm}/authentication/flows/{id}"
URL_AUTHENTICATION_FLOW_COPY = "{url}/admin/realms/{realm}/authentication/flows/{copyfrom}/copy"
URL_AUTHENTICATION_FLOW_EXECUTIONS = "{url}/admin/realms/{realm}/authentication/flows/{flowalias}/executions"
URL_AUTHENTICATION_FLOW_EXECUTIONS_EXECUTION = "{url}/admin/realms/{realm}/authentication/flows/{flowalias}/executions/execution"
URL_AUTHENTICATION_FLOW_EXECUTIONS_FLOW = "{url}/admin/realms/{realm}/authentication/flows/{flowalias}/executions/flow"
URL_AUTHENTICATION_EXECUTION_CONFIG = "{url}/admin/realms/{realm}/authentication/executions/{id}/config"
URL_AUTHENTICATION_EXECUTION_RAISE_PRIORITY = "{url}/admin/realms/{realm}/authentication/executions/{id}/raise-priority"
URL_AUTHENTICATION_EXECUTION_LOWER_PRIORITY = "{url}/admin/realms/{realm}/authentication/executions/{id}/lower-priority"
URL_AUTHENTICATION_CONFIG = "{url}/admin/realms/{realm}/authentication/config/{id}"
URL_AUTHENTICATION_REGISTER_REQUIRED_ACTION = "{url}/admin/realms/{realm}/authentication/register-required-action"
URL_AUTHENTICATION_REQUIRED_ACTIONS = "{url}/admin/realms/{realm}/authentication/required-actions"
URL_AUTHENTICATION_REQUIRED_ACTIONS_ALIAS = "{url}/admin/realms/{realm}/authentication/required-actions/{alias}"

URL_IDENTITY_PROVIDERS = "{url}/admin/realms/{realm}/identity-provider/instances"
URL_IDENTITY_PROVIDER = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}"
URL_IDENTITY_PROVIDER_MAPPERS = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}/mappers"
URL_IDENTITY_PROVIDER_MAPPER = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}/mappers/{id}"
URL_IDENTITY_PROVIDER_IMPORT = "{url}/admin/realms/{realm}/identity-provider/import-config"

URL_COMPONENTS = "{url}/admin/realms/{realm}/components"
URL_COMPONENT = "{url}/admin/realms/{realm}/components/{id}"

URL_AUTHZ_AUTHORIZATION_SCOPE = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/scope/{id}"
URL_AUTHZ_AUTHORIZATION_SCOPES = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/scope"

# This URL is used for:
# - Querying client authorization permissions
# - Removing client authorization permissions
URL_AUTHZ_POLICIES = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/policy"
URL_AUTHZ_POLICY = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/policy/{id}"

URL_AUTHZ_PERMISSION = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/permission/{permission_type}/{id}"
URL_AUTHZ_PERMISSIONS = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/permission/{permission_type}"

URL_AUTHZ_RESOURCES = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/resource"

URL_AUTHZ_CUSTOM_POLICY = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/policy/{policy_type}"
URL_AUTHZ_CUSTOM_POLICIES = "{url}/admin/realms/{realm}/clients/{client_id}/authz/resource-server/policy"


def keycloak_argument_spec():
    """
    Returns argument_spec of options common to keycloak_*-modules

    :return: argument_spec dict
    """
    return dict(
        auth_keycloak_url=dict(type='str', aliases=['url'], required=True, no_log=False),
        auth_client_id=dict(type='str', default='admin-cli'),
        auth_realm=dict(type='str'),
        auth_client_secret=dict(type='str', default=None, no_log=True),
        auth_username=dict(type='str', aliases=['username']),
        auth_password=dict(type='str', aliases=['password'], no_log=True),
        validate_certs=dict(type='bool', default=True),
        connection_timeout=dict(type='int', default=10),
        token=dict(type='str', no_log=True),
        refresh_token=dict(type='str', no_log=True),
        http_agent=dict(type='str', default='Ansible'),
    )


def camel(words):
    return words.split('_')[0] + ''.join(x.capitalize() or '_' for x in words.split('_')[1:])


class KeycloakError(Exception):
    def __init__(self, msg, authError=None):
        self.msg = msg
        self.authError = authError

    def __str__(self):
        return str(self.msg)


def _token_request(module_params, payload):
    """ Obtains connection header with token for the authentication,
    using the provided auth_username/auth_password
    :param module_params: parameters of the module
    :param payload:
       type:
           dict
       description:
           Authentication request payload. Must contain at least
           'grant_type' and 'client_id', optionally 'client_secret',
           along with parameters based on 'grant_type'; e.g.,
           'username'/'password' for type 'password',
           'refresh_token' for type 'refresh_token'.
    :return: access token
    """
    base_url = module_params.get('auth_keycloak_url')
    if not base_url.lower().startswith(('http', 'https')):
        raise KeycloakError("auth_url '%s' should either start with 'http' or 'https'." % base_url)
    auth_realm = module_params.get('auth_realm')
    auth_url = URL_TOKEN.format(url=base_url, realm=auth_realm)
    http_agent = module_params.get('http_agent')
    validate_certs = module_params.get('validate_certs')
    connection_timeout = module_params.get('connection_timeout')

    try:
        r = json.loads(to_native(open_url(auth_url, method='POST',
                                          validate_certs=validate_certs, http_agent=http_agent, timeout=connection_timeout,
                                          data=urlencode(payload)).read()))

        return r['access_token']
    except ValueError as e:
        raise KeycloakError(
            'API returned invalid JSON when trying to obtain access token from %s: %s'
            % (auth_url, str(e)))
    except KeyError:
        raise KeycloakError(
            'API did not include access_token field in response from %s' % auth_url)
    except Exception as e:
        raise KeycloakError('Could not obtain access token from %s: %s'
                            % (auth_url, str(e)), authError=e)


def _request_token_using_credentials(module_params):
    """ Obtains connection header with token for the authentication,
    using the provided auth_username/auth_password
    :param module_params: parameters of the module. Must include 'auth_username' and 'auth_password'.
    :return: connection header
    """
    client_id = module_params.get('auth_client_id')
    auth_username = module_params.get('auth_username')
    auth_password = module_params.get('auth_password')
    client_secret = module_params.get('auth_client_secret')

    temp_payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': auth_username,
        'password': auth_password,
    }
    # Remove empty items, for instance missing client_secret
    payload = {k: v for k, v in temp_payload.items() if v is not None}

    return _token_request(module_params, payload)


def _request_token_using_refresh_token(module_params):
    """ Obtains connection header with token for the authentication,
    using the provided refresh_token
    :param module_params: parameters of the module. Must include 'refresh_token'.
    :return: connection header
    """
    client_id = module_params.get('auth_client_id')
    refresh_token = module_params.get('refresh_token')
    client_secret = module_params.get('auth_client_secret')

    temp_payload = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
    }
    # Remove empty items, for instance missing client_secret
    payload = {k: v for k, v in temp_payload.items() if v is not None}

    return _token_request(module_params, payload)


def _request_token_using_client_credentials(module_params):
    """ Obtains connection header with token for the authentication,
    using the provided auth_client_id and auth_client_secret by grant_type
    client_credentials. Ensure that the used client uses client authorization
    with service account roles enabled and required service roles assigned.
    :param module_params: parameters of the module. Must include 'auth_client_id'
    and 'auth_client_secret'..
    :return: connection header
    """
    client_id = module_params.get('auth_client_id')
    client_secret = module_params.get('auth_client_secret')

    temp_payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    # Remove empty items, for instance missing client_secret
    payload = {k: v for k, v in temp_payload.items() if v is not None}

    return _token_request(module_params, payload)


def get_token(module_params):
    """ Obtains connection header with token for the authentication,
    token already given or obtained from credentials
    :param module_params: parameters of the module
    :return: connection header
    """
    token = module_params.get('token')

    if token is None:
        auth_client_id = module_params.get('auth_client_id')
        auth_client_secret = module_params.get('auth_client_secret')
        auth_username = module_params.get('auth_username')
        if auth_client_id is not None and auth_client_secret is not None and auth_username is None:
            token = _request_token_using_client_credentials(module_params)
        else:
            token = _request_token_using_credentials(module_params)

    return {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }


def is_struct_included(struct1, struct2, exclude=None):
    """
    This function compare if the first parameter structure is included in the second.
    The function use every elements of struct1 and validates they are present in the struct2 structure.
    The two structure does not need to be equals for that function to return true.
    Each elements are compared recursively.
    :param struct1:
        type:
            dict for the initial call, can be dict, list, bool, int or str for recursive calls
        description:
            reference structure
    :param struct2:
        type:
            dict for the initial call, can be dict, list, bool, int or str for recursive calls
        description:
            structure to compare with first parameter.
    :param exclude:
        type:
            list
        description:
            Key to exclude from the comparison.
        default: None
    :return:
        type:
            bool
        description:
            Return True if all element of dict 1 are present in dict 2, return false otherwise.
    """
    if isinstance(struct1, list) and isinstance(struct2, list):
        if not struct1 and not struct2:
            return True
        for item1 in struct1:
            if isinstance(item1, (list, dict)):
                for item2 in struct2:
                    if is_struct_included(item1, item2, exclude):
                        break
                else:
                    return False
            else:
                if item1 not in struct2:
                    return False
        return True
    elif isinstance(struct1, dict) and isinstance(struct2, dict):
        if not struct1 and not struct2:
            return True
        try:
            for key in struct1:
                if not (exclude and key in exclude):
                    if not is_struct_included(struct1[key], struct2[key], exclude):
                        return False
        except KeyError:
            return False
        return True
    elif isinstance(struct1, bool) and isinstance(struct2, bool):
        return struct1 == struct2
    else:
        return to_text(struct1, 'utf-8') == to_text(struct2, 'utf-8')


class KeycloakAPI(object):
    """ Keycloak API access; Keycloak uses OAuth 2.0 to protect its API, an access token for which
        is obtained through OpenID connect
    """

    def __init__(self, module, connection_header):
        self.module = module
        self.baseurl = self.module.params.get('auth_keycloak_url')
        self.validate_certs = self.module.params.get('validate_certs')
        self.connection_timeout = self.module.params.get('connection_timeout')
        self.restheaders = connection_header
        self.http_agent = self.module.params.get('http_agent')

    def _request(self, url, method, data=None):
        """ Makes a request to Keycloak and returns the raw response.
        If a 401 is returned, attempts to re-authenticate
        using first the module's refresh_token (if provided)
        and then the module's username/password (if provided).
        On successful re-authentication, the new token is stored
        in the restheaders for future requests.

        :param url: request path
        :param method: request method (e.g., 'GET', 'POST', etc.)
        :param data: (optional) data for request
        :return: raw API response
        """
        def make_request_catching_401():
            try:
                return open_url(url, method=method, data=data,
                                http_agent=self.http_agent, headers=self.restheaders,
                                timeout=self.connection_timeout,
                                validate_certs=self.validate_certs)
            except HTTPError as e:
                if e.code != 401:
                    raise e
                return e

        r = make_request_catching_401()

        if isinstance(r, Exception):
            # Try to refresh token and retry, if available
            refresh_token = self.module.params.get('refresh_token')
            if refresh_token is not None:
                try:
                    token = _request_token_using_refresh_token(self.module.params)
                    self.restheaders['Authorization'] = 'Bearer ' + token

                    r = make_request_catching_401()
                except KeycloakError as e:
                    # Token refresh returns 400 if token is expired/invalid, so continue on if we get a 400
                    if e.authError is not None and e.authError.code != 400:
                        raise e

        if isinstance(r, Exception):
            # Try to re-auth with username/password, if available
            auth_username = self.module.params.get('auth_username')
            auth_password = self.module.params.get('auth_password')
            if auth_username is not None and auth_password is not None:
                token = _request_token_using_credentials(self.module.params)
                self.restheaders['Authorization'] = 'Bearer ' + token

                r = make_request_catching_401()

        if isinstance(r, Exception):
            # Try to re-auth with client_id and client_secret, if available
            auth_client_id = self.module.params.get('auth_client_id')
            auth_client_secret = self.module.params.get('auth_client_secret')
            if auth_client_id is not None and auth_client_secret is not None:
                try:
                    token = _request_token_using_client_credentials(self.module.params)
                    self.restheaders['Authorization'] = 'Bearer ' + token

                    r = make_request_catching_401()
                except KeycloakError as e:
                    # Token refresh returns 400 if token is expired/invalid, so continue on if we get a 400
                    if e.authError is not None and e.authError.code != 400:
                        raise e

        if isinstance(r, Exception):
            # Either no re-auth options were available, or they all failed
            raise r

        return r

    def _request_and_deserialize(self, url, method, data=None):
        """ Wraps the _request method with JSON deserialization of the response.

        :param url: request path
        :param method: request method (e.g., 'GET', 'POST', etc.)
        :param data: (optional) data for request
        :return: raw API response
        """
        return json.loads(to_native(self._request(url, method, data).read()))

    def get_realm_info_by_id(self, realm='master'):
        """ Obtain realm public info by id

        :param realm: realm id
        :return: dict of real, representation or None if none matching exist
        """
        realm_info_url = URL_REALM_INFO.format(url=self.baseurl, realm=realm)

        try:
            return self._request_and_deserialize(realm_info_url, method='GET')

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except Exception as e:
            self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())

    def get_realm_keys_metadata_by_id(self, realm='master'):
        """Obtain realm public info by id

        :param realm: realm id

        :return: None, or a 'KeysMetadataRepresentation'
                 (https://www.keycloak.org/docs-api/latest/rest-api/index.html#KeysMetadataRepresentation)
                 -- a dict containing the keys 'active' and 'keys', the former containing a mapping
                 from algorithms to key-ids, the latter containing a list of dicts with key
                 information.
        """
        realm_keys_metadata_url = URL_REALM_KEYS_METADATA.format(url=self.baseurl, realm=realm)

        try:
            return self._request_and_deserialize(realm_keys_metadata_url, method="GET")

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except Exception as e:
            self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())

    # The Keycloak API expects the realm name (like `master`) not the ID when fetching the realm data.
    # See the Keycloak API docs: https://www.keycloak.org/docs-api/latest/rest-api/#_realms_admin
    def get_realm_by_id(self, realm='master'):
        """ Obtain realm representation by id

        :param realm: realm id
        :return: dict of real, representation or None if none matching exist
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return self._request_and_deserialize(realm_url, method='GET')

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except Exception as e:
            self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())

    def update_realm(self, realmrep, realm="master"):
        """ Update an existing realm
        :param realmrep: corresponding (partial/full) realm representation with updates
        :param realm: realm to be updated in Keycloak
        :return: HTTPResponse object on success
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return self._request(realm_url, method='PUT', data=json.dumps(realmrep))
        except Exception as e:
            self.fail_request(e, msg='Could not update realm %s: %s' % (realm, str(e)),
                              exception=traceback.format_exc())

    def create_realm(self, realmrep):
        """ Create a realm in keycloak
        :param realmrep: Realm representation of realm to be created.
        :return: HTTPResponse object on success
        """
        realm_url = URL_REALMS.format(url=self.baseurl)

        try:
            return self._request(realm_url, method='POST', data=json.dumps(realmrep))
        except Exception as e:
            self.fail_request(e, msg='Could not create realm %s: %s' % (realmrep['id'], str(e)),
                              exception=traceback.format_exc())

    def delete_realm(self, realm="master"):
        """ Delete a realm from Keycloak

        :param realm: realm to be deleted
        :return: HTTPResponse object on success
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return self._request(realm_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete realm %s: %s' % (realm, str(e)),
                              exception=traceback.format_exc())

    def get_clients(self, realm='master', filter=None):
        """ Obtains client representations for clients in a realm

        :param realm: realm to be queried
        :param filter: if defined, only the client with clientId specified in the filter is returned
        :return: list of dicts of client representations
        """
        clientlist_url = URL_CLIENTS.format(url=self.baseurl, realm=realm)
        if filter is not None:
            clientlist_url += '?clientId=%s' % filter

        try:
            return self._request_and_deserialize(clientlist_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of clients for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of clients for realm %s: %s'
                                     % (realm, str(e)))

    def get_client_by_clientid(self, client_id, realm='master'):
        """ Get client representation by clientId
        :param client_id: The clientId to be queried
        :param realm: realm from which to obtain the client representation
        :return: dict with a client representation or None if none matching exist
        """
        r = self.get_clients(realm=realm, filter=client_id)
        if len(r) > 0:
            return r[0]
        else:
            return None

    def get_client_by_id(self, id, realm='master'):
        """ Obtain client representation by id

        :param id: id (not clientId) of client to be queried
        :param realm: client from this realm
        :return: dict of client representation or None if none matching exist
        """
        client_url = URL_CLIENT.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request_and_deserialize(client_url, method='GET')

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain client %s for realm %s: %s'
                                         % (id, realm, str(e)))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain client %s for realm %s: %s'
                                      % (id, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain client %s for realm %s: %s'
                                      % (id, realm, str(e)))

    def get_client_id(self, client_id, realm='master'):
        """ Obtain id of client by client_id

        :param client_id: client_id of client to be queried
        :param realm: client template from this realm
        :return: id of client (usually a UUID)
        """
        result = self.get_client_by_clientid(client_id, realm)
        if isinstance(result, dict) and 'id' in result:
            return result['id']
        else:
            return None

    def update_client(self, id, clientrep, realm="master"):
        """ Update an existing client
        :param id: id (not clientId) of client to be updated in Keycloak
        :param clientrep: corresponding (partial/full) client representation with updates
        :param realm: realm the client is in
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENT.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request(client_url, method='PUT', data=json.dumps(clientrep))
        except Exception as e:
            self.fail_request(e, msg='Could not update client %s in realm %s: %s'
                                     % (id, realm, str(e)))

    def create_client(self, clientrep, realm="master"):
        """ Create a client in keycloak
        :param clientrep: Client representation of client to be created. Must at least contain field clientId.
        :param realm: realm for client to be created.
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENTS.format(url=self.baseurl, realm=realm)

        try:
            return self._request(client_url, method='POST', data=json.dumps(clientrep))
        except Exception as e:
            self.fail_request(e, msg='Could not create client %s in realm %s: %s'
                                     % (clientrep['clientId'], realm, str(e)))

    def delete_client(self, id, realm="master"):
        """ Delete a client from Keycloak

        :param id: id (not clientId) of client to be deleted
        :param realm: realm of client to be deleted
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENT.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request(client_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete client %s in realm %s: %s'
                                     % (id, realm, str(e)))

    def get_client_roles_by_id(self, cid, realm="master"):
        """ Fetch the roles of the a client on the Keycloak server.

        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        client_roles_url = URL_CLIENT_ROLES.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request_and_deserialize(client_roles_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch rolemappings for client %s in realm %s: %s"
                                     % (cid, realm, str(e)))

    def get_client_role_id_by_name(self, cid, name, realm="master"):
        """ Get the role ID of a client.

        :param cid: ID of the client from which to obtain the rolemappings.
        :param name: Name of the role.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The ID of the role, None if not found.
        """
        rolemappings = self.get_client_roles_by_id(cid, realm=realm)
        for role in rolemappings:
            if name == role['name']:
                return role['id']
        return None

    def get_client_group_rolemapping_by_id(self, gid, cid, rid, realm='master'):
        """ Obtain client representation by id

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param rid: ID of the role.
        :param realm: client from this realm
        :return: dict of rolemapping representation or None if none matching exist
        """
        rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            rolemappings = self._request_and_deserialize(rolemappings_url, method="GET")
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.fail_request(e, msg="Could not fetch rolemappings for client %s in group %s, realm %s: %s"
                                     % (cid, gid, realm, str(e)))
        return None

    def get_client_group_available_rolemappings(self, gid, cid, realm="master"):
        """ Fetch the available role of a client in a specified group on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        available_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS_AVAILABLE.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            return self._request_and_deserialize(available_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
                                     % (cid, gid, realm, str(e)))

    def get_client_group_composite_rolemappings(self, gid, cid, realm="master"):
        """ Fetch the composite role of a client in a specified group on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        composite_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS_COMPOSITE.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            return self._request_and_deserialize(composite_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
                                     % (cid, gid, realm, str(e)))

    def get_role_by_id(self, rid, realm="master"):
        """ Fetch a role by its id on the Keycloak server.

        :param rid: ID of the role.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The role.
        """
        client_roles_url = URL_ROLES_BY_ID.format(url=self.baseurl, realm=realm, id=rid)
        try:
            return self._request_and_deserialize(client_roles_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch role for id %s in realm %s: %s"
                                     % (rid, realm, str(e)))

    def get_client_roles_by_id_composite_rolemappings(self, rid, cid, realm="master"):
        """ Fetch a role by its id on the Keycloak server.

        :param rid: ID of the composite role.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The role.
        """
        client_roles_url = URL_ROLES_BY_ID_COMPOSITES_CLIENTS.format(url=self.baseurl, realm=realm, id=rid, cid=cid)
        try:
            return self._request_and_deserialize(client_roles_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch role for id %s and cid %s in realm %s: %s"
                                     % (rid, cid, realm, str(e)))

    def add_client_roles_by_id_composite_rolemapping(self, rid, roles_rep, realm="master"):
        """ Assign roles to composite role

        :param rid: ID of the composite role.
        :param roles_rep: Representation of the roles to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        available_rolemappings_url = URL_ROLES_BY_ID_COMPOSITES.format(url=self.baseurl, realm=realm, id=rid)
        try:
            self._request(available_rolemappings_url, method="POST", data=json.dumps(roles_rep))
        except Exception as e:
            self.fail_request(e, msg="Could not assign roles to composite role %s and realm %s: %s"
                                     % (rid, realm, str(e)))

    def add_group_realm_rolemapping(self, gid, role_rep, realm="master"):
        """ Add the specified realm role to specified group on the Keycloak server.

        :param gid: ID of the group to add the role mapping.
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        url = URL_REALM_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, group=gid)
        try:
            self._request(url, method="POST", data=json.dumps(role_rep))
        except Exception as e:
            self.fail_request(e, msg="Could add realm role mappings for group %s, realm %s: %s"
                                     % (gid, realm, str(e)))

    def delete_group_realm_rolemapping(self, gid, role_rep, realm="master"):
        """ Delete the specified realm role from the specified group on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        url = URL_REALM_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, group=gid)
        try:
            self._request(url, method="DELETE", data=json.dumps(role_rep))
        except Exception as e:
            self.fail_request(e, msg="Could not delete realm role mappings for group %s, realm %s: %s"
                                     % (gid, realm, str(e)))

    def add_group_rolemapping(self, gid, cid, role_rep, realm="master"):
        """ Fetch the composite role of a client in a specified group on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        available_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            self._request(available_rolemappings_url, method="POST", data=json.dumps(role_rep))
        except Exception as e:
            self.fail_request(e, msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
                                     % (cid, gid, realm, str(e)))

    def delete_group_rolemapping(self, gid, cid, role_rep, realm="master"):
        """ Delete the rolemapping of a client in a specified group on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        available_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            self._request(available_rolemappings_url, method="DELETE", data=json.dumps(role_rep))
        except Exception as e:
            self.fail_request(e, msg="Could not delete available rolemappings for client %s in group %s, realm %s: %s"
                                     % (cid, gid, realm, str(e)))

    def get_client_user_rolemapping_by_id(self, uid, cid, rid, realm='master'):
        """ Obtain client representation by id

        :param uid: ID of the user from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param rid: ID of the role.
        :param realm: client from this realm
        :return: dict of rolemapping representation or None if none matching exist
        """
        rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid, client=cid)
        try:
            rolemappings = self._request_and_deserialize(rolemappings_url, method="GET")
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.fail_request(e, msg="Could not fetch rolemappings for client %s and user %s, realm %s: %s"
                                     % (cid, uid, realm, str(e)))
        return None

    def get_client_user_available_rolemappings(self, uid, cid, realm="master"):
        """ Fetch the available role of a client for a specified user on the Keycloak server.

        :param uid: ID of the user from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The effective rollemappings of specified client and user of the realm (default "master").
        """
        available_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS_AVAILABLE.format(url=self.baseurl, realm=realm, id=uid, client=cid)
        try:
            return self._request_and_deserialize(available_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch effective rolemappings for client %s and user %s, realm %s: %s"
                                     % (cid, uid, realm, str(e)))

    def get_client_user_composite_rolemappings(self, uid, cid, realm="master"):
        """ Fetch the composite role of a client for a specified user on the Keycloak server.

        :param uid: ID of the user from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        composite_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS_COMPOSITE.format(url=self.baseurl, realm=realm, id=uid, client=cid)
        try:
            return self._request_and_deserialize(composite_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch available rolemappings for user %s of realm %s: %s"
                                     % (uid, realm, str(e)))

    def get_realm_user_rolemapping_by_id(self, uid, rid, realm='master'):
        """ Obtain role representation by id

        :param uid: ID of the user from which to obtain the rolemappings.
        :param rid: ID of the role.
        :param realm: client from this realm
        :return: dict of rolemapping representation or None if none matching exist
        """
        rolemappings_url = URL_REALM_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid)
        try:
            rolemappings = self._request_and_deserialize(rolemappings_url, method="GET")
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.fail_request(e, msg="Could not fetch rolemappings for user %s, realm %s: %s"
                                     % (uid, realm, str(e)))
        return None

    def get_realm_user_available_rolemappings(self, uid, realm="master"):
        """ Fetch the available role of a realm for a specified user on the Keycloak server.

        :param uid: ID of the user from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        available_rolemappings_url = URL_REALM_ROLEMAPPINGS_AVAILABLE.format(url=self.baseurl, realm=realm, id=uid)
        try:
            return self._request_and_deserialize(available_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch available rolemappings for user %s of realm %s: %s"
                                     % (uid, realm, str(e)))

    def get_realm_user_composite_rolemappings(self, uid, realm="master"):
        """ Fetch the composite role of a realm for a specified user on the Keycloak server.

        :param uid: ID of the user from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The effective rollemappings of specified client and user of the realm (default "master").
        """
        composite_rolemappings_url = URL_REALM_ROLEMAPPINGS_COMPOSITE.format(url=self.baseurl, realm=realm, id=uid)
        try:
            return self._request_and_deserialize(composite_rolemappings_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch effective rolemappings for user %s, realm %s: %s"
                                     % (uid, realm, str(e)))

    def get_user_by_username(self, username, realm="master"):
        """ Fetch a keycloak user within a realm based on its username.

        If the user does not exist, None is returned.
        :param username: Username of the user to fetch.
        :param realm: Realm in which the user resides; default 'master'
        """
        users_url = URL_USERS.format(url=self.baseurl, realm=realm)
        users_url += '?username=%s&exact=true' % username
        try:
            userrep = None
            users = self._request_and_deserialize(users_url, method='GET')
            for user in users:
                if user['username'] == username:
                    userrep = user
                    break
            return userrep

        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain the user for realm %s and username %s: %s'
                                      % (realm, username, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain the user for realm %s and username %s: %s'
                                     % (realm, username, str(e)))

    def get_service_account_user_by_client_id(self, client_id, realm="master"):
        """ Fetch a keycloak service account user within a realm based on its client_id.

        If the user does not exist, None is returned.
        :param client_id: clientId of the service account user to fetch.
        :param realm: Realm in which the user resides; default 'master'
        """
        cid = self.get_client_id(client_id, realm=realm)

        service_account_user_url = URL_CLIENT_SERVICE_ACCOUNT_USER.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request_and_deserialize(service_account_user_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain the service-account-user for realm %s and client_id %s: %s'
                                      % (realm, client_id, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain the service-account-user for realm %s and client_id %s: %s'
                                     % (realm, client_id, str(e)))

    def add_user_rolemapping(self, uid, cid, role_rep, realm="master"):
        """ Assign a realm or client role to a specified user on the Keycloak server.

        :param uid: ID of the user roles are assigned to.
        :param cid: ID of the client from which to obtain the rolemappings. If empty, roles are from the realm
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        if cid is None:
            user_realm_rolemappings_url = URL_REALM_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid)
            try:
                self._request(user_realm_rolemappings_url, method="POST", data=json.dumps(role_rep))
            except Exception as e:
                self.fail_request(e, msg="Could not map roles to userId %s for realm %s and roles %s: %s"
                                         % (uid, realm, json.dumps(role_rep), str(e)))
        else:
            user_client_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid, client=cid)
            try:
                self._request(user_client_rolemappings_url, method="POST", data=json.dumps(role_rep))
            except Exception as e:
                self.fail_request(e, msg="Could not map roles to userId %s for client %s, realm %s and roles %s: %s"
                                         % (cid, uid, realm, json.dumps(role_rep), str(e)))

    def delete_user_rolemapping(self, uid, cid, role_rep, realm="master"):
        """ Delete the rolemapping of a client in a specified user on the Keycloak server.

        :param uid: ID of the user from which to remove the rolemappings.
        :param cid: ID of the client from which to remove the rolemappings.
        :param role_rep: Representation of the role to remove from rolemappings.
        :param realm: Realm from which to remove the rolemappings.
        :return: None.
        """
        if cid is None:
            user_realm_rolemappings_url = URL_REALM_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid)
            try:
                self._request(user_realm_rolemappings_url, method="DELETE", data=json.dumps(role_rep))
            except Exception as e:
                self.fail_request(e, msg="Could not remove roles %s from userId %s, realm %s: %s"
                                         % (json.dumps(role_rep), uid, realm, str(e)))
        else:
            user_client_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid, client=cid)
            try:
                self._request(user_client_rolemappings_url, method="DELETE", data=json.dumps(role_rep))
            except Exception as e:
                self.fail_request(e, msg="Could not remove roles %s for client %s from userId %s, realm %s: %s"
                                         % (json.dumps(role_rep), cid, uid, realm, str(e)))

    def get_client_templates(self, realm='master'):
        """ Obtains client template representations for client templates in a realm

        :param realm: realm to be queried
        :return: list of dicts of client representations
        """
        url = URL_CLIENTTEMPLATES.format(url=self.baseurl, realm=realm)

        try:
            return self._request_and_deserialize(url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of client templates for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of client templates for realm %s: %s'
                                     % (realm, str(e)))

    def get_client_template_by_id(self, id, realm='master'):
        """ Obtain client template representation by id

        :param id: id (not name) of client template to be queried
        :param realm: client template from this realm
        :return: dict of client template representation or None if none matching exist
        """
        url = URL_CLIENTTEMPLATE.format(url=self.baseurl, id=id, realm=realm)

        try:
            return self._request_and_deserialize(url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain client templates %s for realm %s: %s'
                                      % (id, realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain client template %s for realm %s: %s'
                                     % (id, realm, str(e)))

    def get_client_template_by_name(self, name, realm='master'):
        """ Obtain client template representation by name

        :param name: name of client template to be queried
        :param realm: client template from this realm
        :return: dict of client template representation or None if none matching exist
        """
        result = self.get_client_templates(realm)
        if isinstance(result, list):
            result = [x for x in result if x['name'] == name]
            if len(result) > 0:
                return result[0]
        return None

    def get_client_template_id(self, name, realm='master'):
        """ Obtain client template id by name

        :param name: name of client template to be queried
        :param realm: client template from this realm
        :return: client template id (usually a UUID)
        """
        result = self.get_client_template_by_name(name, realm)
        if isinstance(result, dict) and 'id' in result:
            return result['id']
        else:
            return None

    def update_client_template(self, id, clienttrep, realm="master"):
        """ Update an existing client template
        :param id: id (not name) of client template to be updated in Keycloak
        :param clienttrep: corresponding (partial/full) client template representation with updates
        :param realm: realm the client template is in
        :return: HTTPResponse object on success
        """
        url = URL_CLIENTTEMPLATE.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request(url, method='PUT', data=json.dumps(clienttrep))
        except Exception as e:
            self.fail_request(e, msg='Could not update client template %s in realm %s: %s'
                                     % (id, realm, str(e)))

    def create_client_template(self, clienttrep, realm="master"):
        """ Create a client in keycloak
        :param clienttrep: Client template representation of client template to be created. Must at least contain field name
        :param realm: realm for client template to be created in
        :return: HTTPResponse object on success
        """
        url = URL_CLIENTTEMPLATES.format(url=self.baseurl, realm=realm)

        try:
            return self._request(url, method='POST', data=json.dumps(clienttrep))
        except Exception as e:
            self.fail_request(e, msg='Could not create client template %s in realm %s: %s'
                                     % (clienttrep['clientId'], realm, str(e)))

    def delete_client_template(self, id, realm="master"):
        """ Delete a client template from Keycloak

        :param id: id (not name) of client to be deleted
        :param realm: realm of client template to be deleted
        :return: HTTPResponse object on success
        """
        url = URL_CLIENTTEMPLATE.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request(url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete client template %s in realm %s: %s'
                                     % (id, realm, str(e)))

    def get_clientscopes(self, realm="master"):
        """ Fetch the name and ID of all clientscopes on the Keycloak server.

        To fetch the full data of the group, make a subsequent call to
        get_clientscope_by_clientscopeid, passing in the ID of the group you wish to return.

        :param realm: Realm in which the clientscope resides; default 'master'.
        :return The clientscopes of this realm (default "master")
        """
        clientscopes_url = URL_CLIENTSCOPES.format(url=self.baseurl, realm=realm)
        try:
            return self._request_and_deserialize(clientscopes_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch list of clientscopes in realm %s: %s"
                                     % (realm, str(e)))

    def get_clientscope_by_clientscopeid(self, cid, realm="master"):
        """ Fetch a keycloak clientscope from the provided realm using the clientscope's unique ID.

        If the clientscope does not exist, None is returned.

        gid is a UUID provided by the Keycloak API
        :param cid: UUID of the clientscope to be returned
        :param realm: Realm in which the clientscope resides; default 'master'.
        """
        clientscope_url = URL_CLIENTSCOPE.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request_and_deserialize(clientscope_url, method="GET")

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg="Could not fetch clientscope %s in realm %s: %s"
                                         % (cid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg="Could not clientscope group %s in realm %s: %s"
                                      % (cid, realm, str(e)))

    def get_clientscope_by_name(self, name, realm="master"):
        """ Fetch a keycloak clientscope within a realm based on its name.

        The Keycloak API does not allow filtering of the clientscopes resource by name.
        As a result, this method first retrieves the entire list of clientscopes - name and ID -
        then performs a second query to fetch the group.

        If the clientscope does not exist, None is returned.
        :param name: Name of the clientscope to fetch.
        :param realm: Realm in which the clientscope resides; default 'master'
        """
        try:
            all_clientscopes = self.get_clientscopes(realm=realm)

            for clientscope in all_clientscopes:
                if clientscope['name'] == name:
                    return self.get_clientscope_by_clientscopeid(clientscope['id'], realm=realm)

            return None

        except Exception as e:
            self.module.fail_json(msg="Could not fetch clientscope %s in realm %s: %s"
                                      % (name, realm, str(e)))

    def create_clientscope(self, clientscoperep, realm="master"):
        """ Create a Keycloak clientscope.

        :param clientscoperep: a ClientScopeRepresentation of the clientscope to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        clientscopes_url = URL_CLIENTSCOPES.format(url=self.baseurl, realm=realm)
        try:
            return self._request(clientscopes_url, method='POST', data=json.dumps(clientscoperep))
        except Exception as e:
            self.fail_request(e, msg="Could not create clientscope %s in realm %s: %s"
                                     % (clientscoperep['name'], realm, str(e)))

    def update_clientscope(self, clientscoperep, realm="master"):
        """ Update an existing clientscope.

        :param grouprep: A GroupRepresentation of the updated group.
        :return HTTPResponse object on success
        """
        clientscope_url = URL_CLIENTSCOPE.format(url=self.baseurl, realm=realm, id=clientscoperep['id'])

        try:
            return self._request(clientscope_url, method='PUT', data=json.dumps(clientscoperep))

        except Exception as e:
            self.fail_request(e, msg='Could not update clientscope %s in realm %s: %s'
                                     % (clientscoperep['name'], realm, str(e)))

    def delete_clientscope(self, name=None, cid=None, realm="master"):
        """ Delete a clientscope. One of name or cid must be provided.

        Providing the clientscope ID is preferred as it avoids a second lookup to
        convert a clientscope name to an ID.

        :param name: The name of the clientscope. A lookup will be performed to retrieve the clientscope ID.
        :param cid: The ID of the clientscope (preferred to name).
        :param realm: The realm in which this group resides, default "master".
        """

        if cid is None and name is None:
            # prefer an exception since this is almost certainly a programming error in the module itself.
            raise Exception("Unable to delete group - one of group ID or name must be provided.")

        # only lookup the name if cid is not provided.
        # in the case that both are provided, prefer the ID, since it is one
        # less lookup.
        if cid is None and name is not None:
            for clientscope in self.get_clientscopes(realm=realm):
                if clientscope['name'] == name:
                    cid = clientscope['id']
                    break

        # if the group doesn't exist - no problem, nothing to delete.
        if cid is None:
            return None

        # should have a good cid by here.
        clientscope_url = URL_CLIENTSCOPE.format(realm=realm, id=cid, url=self.baseurl)
        try:
            return self._request(clientscope_url, method='DELETE')

        except Exception as e:
            self.fail_request(e, msg="Unable to delete clientscope %s: %s" % (cid, str(e)))

    def get_clientscope_protocolmappers(self, cid, realm="master"):
        """ Fetch the name and ID of all clientscopes on the Keycloak server.

        To fetch the full data of the group, make a subsequent call to
        get_clientscope_by_clientscopeid, passing in the ID of the group you wish to return.

        :param cid: id of clientscope (not name).
        :param realm: Realm in which the clientscope resides; default 'master'.
        :return The protocolmappers of this realm (default "master")
        """
        protocolmappers_url = URL_CLIENTSCOPE_PROTOCOLMAPPERS.format(id=cid, url=self.baseurl, realm=realm)
        try:
            return self._request_and_deserialize(protocolmappers_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch list of protocolmappers in realm %s: %s"
                                     % (realm, str(e)))

    def get_clientscope_protocolmapper_by_protocolmapperid(self, pid, cid, realm="master"):
        """ Fetch a keycloak clientscope from the provided realm using the clientscope's unique ID.

        If the clientscope does not exist, None is returned.

        gid is a UUID provided by the Keycloak API

        :param cid: UUID of the protocolmapper to be returned
        :param cid: UUID of the clientscope to be returned
        :param realm: Realm in which the clientscope resides; default 'master'.
        """
        protocolmapper_url = URL_CLIENTSCOPE_PROTOCOLMAPPER.format(url=self.baseurl, realm=realm, id=cid, mapper_id=pid)
        try:
            return self._request_and_deserialize(protocolmapper_url, method="GET")

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg="Could not fetch protocolmapper %s in realm %s: %s"
                                         % (pid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch protocolmapper %s in realm %s: %s"
                                      % (cid, realm, str(e)))

    def get_clientscope_protocolmapper_by_name(self, cid, name, realm="master"):
        """ Fetch a keycloak clientscope within a realm based on its name.

        The Keycloak API does not allow filtering of the clientscopes resource by name.
        As a result, this method first retrieves the entire list of clientscopes - name and ID -
        then performs a second query to fetch the group.

        If the clientscope does not exist, None is returned.
        :param cid: Id of the clientscope (not name).
        :param name: Name of the protocolmapper to fetch.
        :param realm: Realm in which the clientscope resides; default 'master'
        """
        try:
            all_protocolmappers = self.get_clientscope_protocolmappers(cid, realm=realm)

            for protocolmapper in all_protocolmappers:
                if protocolmapper['name'] == name:
                    return self.get_clientscope_protocolmapper_by_protocolmapperid(protocolmapper['id'], cid, realm=realm)

            return None

        except Exception as e:
            self.module.fail_json(msg="Could not fetch protocolmapper %s in realm %s: %s"
                                      % (name, realm, str(e)))

    def create_clientscope_protocolmapper(self, cid, mapper_rep, realm="master"):
        """ Create a Keycloak clientscope protocolmapper.

        :param cid: Id of the clientscope.
        :param mapper_rep: a ProtocolMapperRepresentation of the protocolmapper to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        protocolmappers_url = URL_CLIENTSCOPE_PROTOCOLMAPPERS.format(url=self.baseurl, id=cid, realm=realm)
        try:
            return self._request(protocolmappers_url, method='POST', data=json.dumps(mapper_rep))
        except Exception as e:
            self.fail_request(e, msg="Could not create protocolmapper %s in realm %s: %s"
                                     % (mapper_rep['name'], realm, str(e)))

    def update_clientscope_protocolmappers(self, cid, mapper_rep, realm="master"):
        """ Update an existing clientscope.

        :param cid: Id of the clientscope.
        :param mapper_rep: A ProtocolMapperRepresentation of the updated protocolmapper.
        :return HTTPResponse object on success
        """
        protocolmapper_url = URL_CLIENTSCOPE_PROTOCOLMAPPER.format(url=self.baseurl, realm=realm, id=cid, mapper_id=mapper_rep['id'])

        try:
            return self._request(protocolmapper_url, method='PUT', data=json.dumps(mapper_rep))

        except Exception as e:
            self.fail_request(e, msg='Could not update protocolmappers for clientscope %s in realm %s: %s'
                                     % (mapper_rep, realm, str(e)))

    def get_default_clientscopes(self, realm, client_id=None):
        """Fetch the name and ID of all clientscopes on the Keycloak server.

        To fetch the full data of the client scope, make a subsequent call to
        get_clientscope_by_clientscopeid, passing in the ID of the client scope you wish to return.

        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        :return The default clientscopes of this realm or client
        """
        url = URL_DEFAULT_CLIENTSCOPES if client_id is None else URL_CLIENT_DEFAULT_CLIENTSCOPES
        return self._get_clientscopes_of_type(realm, url, 'default', client_id)

    def get_optional_clientscopes(self, realm, client_id=None):
        """Fetch the name and ID of all clientscopes on the Keycloak server.

        To fetch the full data of the client scope, make a subsequent call to
        get_clientscope_by_clientscopeid, passing in the ID of the client scope you wish to return.

        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        :return The optional clientscopes of this realm or client
        """
        url = URL_OPTIONAL_CLIENTSCOPES if client_id is None else URL_CLIENT_OPTIONAL_CLIENTSCOPES
        return self._get_clientscopes_of_type(realm, url, 'optional', client_id)

    def _get_clientscopes_of_type(self, realm, url_template, scope_type, client_id=None):
        """Fetch the name and ID of all clientscopes on the Keycloak server.

        To fetch the full data of the client scope, make a subsequent call to
        get_clientscope_by_clientscopeid, passing in the ID of the client scope you wish to return.

        :param realm: Realm in which the clientscope resides.
        :param url_template the template for the right type
        :param scope_type this can be either optional or default
        :param client_id: The client in which the clientscope resides.
        :return The clientscopes of the specified type of this realm
        """
        if client_id is None:
            clientscopes_url = url_template.format(url=self.baseurl, realm=realm)
            try:
                return self._request_and_deserialize(clientscopes_url, method="GET")
            except Exception as e:
                self.fail_request(e, msg="Could not fetch list of %s clientscopes in realm %s: %s" % (scope_type, realm, str(e)))
        else:
            cid = self.get_client_id(client_id=client_id, realm=realm)
            clientscopes_url = url_template.format(url=self.baseurl, realm=realm, cid=cid)
            try:
                return self._request_and_deserialize(clientscopes_url, method="GET")
            except Exception as e:
                self.fail_request(e, msg="Could not fetch list of %s clientscopes in client %s: %s" % (scope_type, client_id, clientscopes_url))

    def _decide_url_type_clientscope(self, client_id=None, scope_type="default"):
        """Decides which url to use.
        :param scope_type this can be either optional or default
        :param client_id: The client in which the clientscope resides.
        """
        if client_id is None:
            if scope_type == "default":
                return URL_DEFAULT_CLIENTSCOPE
            if scope_type == "optional":
                return URL_OPTIONAL_CLIENTSCOPE
        else:
            if scope_type == "default":
                return URL_CLIENT_DEFAULT_CLIENTSCOPE
            if scope_type == "optional":
                return URL_CLIENT_OPTIONAL_CLIENTSCOPE

    def add_default_clientscope(self, id, realm="master", client_id=None):
        """Add a client scope as default either on realm or client level.

        :param id: Client scope Id.
        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        """
        self._action_type_clientscope(id, client_id, "default", realm, 'add')

    def add_optional_clientscope(self, id, realm="master", client_id=None):
        """Add a client scope as optional either on realm or client level.

        :param id: Client scope Id.
        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        """
        self._action_type_clientscope(id, client_id, "optional", realm, 'add')

    def delete_default_clientscope(self, id, realm="master", client_id=None):
        """Remove a client scope as default either on realm or client level.

        :param id: Client scope Id.
        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        """
        self._action_type_clientscope(id, client_id, "default", realm, 'delete')

    def delete_optional_clientscope(self, id, realm="master", client_id=None):
        """Remove a client scope as optional either on realm or client level.

        :param id: Client scope Id.
        :param realm: Realm in which the clientscope resides.
        :param client_id: The client in which the clientscope resides.
        """
        self._action_type_clientscope(id, client_id, "optional", realm, 'delete')

    def _action_type_clientscope(self, id=None, client_id=None, scope_type="default", realm="master", action='add'):
        """ Delete or add a clientscope of type.
        :param name: The name of the clientscope. A lookup will be performed to retrieve the clientscope ID.
        :param client_id: The ID of the clientscope (preferred to name).
        :param scope_type 'default' or 'optional'
        :param realm: The realm in which this group resides, default "master".
        """
        cid = None if client_id is None else self.get_client_id(client_id=client_id, realm=realm)
        # should have a good cid by here.
        clientscope_type_url = self._decide_url_type_clientscope(client_id, scope_type).format(realm=realm, id=id, cid=cid, url=self.baseurl)
        try:
            method = 'PUT' if action == "add" else 'DELETE'
            return self._request(clientscope_type_url, method=method)

        except Exception as e:
            place = 'realm' if client_id is None else 'client ' + client_id
            self.fail_request(e, msg="Unable to %s %s clientscope %s @ %s : %s" % (action, scope_type, id, place, str(e)))

    def create_clientsecret(self, id, realm="master"):
        """ Generate a new client secret by id

        :param id: id (not clientId) of client to be queried
        :param realm: client from this realm
        :return: dict of credential representation
        """
        clientsecret_url = URL_CLIENTSECRET.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request_and_deserialize(clientsecret_url, method='POST')

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain clientsecret of client %s for realm %s: %s'
                                         % (id, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain clientsecret of client %s for realm %s: %s'
                                      % (id, realm, str(e)))

    def get_clientsecret(self, id, realm="master"):
        """ Obtain client secret by id

        :param id: id (not clientId) of client to be queried
        :param realm: client from this realm
        :return: dict of credential representation
        """
        clientsecret_url = URL_CLIENTSECRET.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request_and_deserialize(clientsecret_url, method='GET')

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not obtain clientsecret of client %s for realm %s: %s'
                                         % (id, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain clientsecret of client %s for realm %s: %s'
                                      % (id, realm, str(e)))

    def get_groups(self, realm="master"):
        """ Fetch the name and ID of all groups on the Keycloak server.

        To fetch the full data of the group, make a subsequent call to
        get_group_by_groupid, passing in the ID of the group you wish to return.

        :param realm: Return the groups of this realm (default "master").
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            return self._request_and_deserialize(groups_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg="Could not fetch list of groups in realm %s: %s"
                                     % (realm, str(e)))

    def get_group_by_groupid(self, gid, realm="master"):
        """ Fetch a keycloak group from the provided realm using the group's unique ID.

        If the group does not exist, None is returned.

        gid is a UUID provided by the Keycloak API
        :param gid: UUID of the group to be returned
        :param realm: Realm in which the group resides; default 'master'.
        """
        groups_url = URL_GROUP.format(url=self.baseurl, realm=realm, groupid=gid)
        try:
            return self._request_and_deserialize(groups_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg="Could not fetch group %s in realm %s: %s"
                                         % (gid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch group %s in realm %s: %s"
                                      % (gid, realm, str(e)))

    def get_subgroups(self, parent, realm="master"):
        if 'subGroupCount' in parent:
            # Since version 23, when GETting a group Keycloak does not
            # return subGroups but only a subGroupCount.
            # Children must be fetched in a second request.
            if parent['subGroupCount'] == 0:
                group_children = []
            else:
                group_children_url = URL_GROUP_CHILDREN.format(url=self.baseurl, realm=realm, groupid=parent['id']) + "?max=" + str(parent['subGroupCount'])
                group_children = self._request_and_deserialize(group_children_url, method="GET")
            subgroups = group_children
        else:
            subgroups = parent['subGroups']
        return subgroups

    def get_group_by_name(self, name, realm="master", parents=None):
        """ Fetch a keycloak group within a realm based on its name.

        The Keycloak API does not allow filtering of the Groups resource by name.
        As a result, this method first retrieves the entire list of groups - name and ID -
        then performs a second query to fetch the group.

        If the group does not exist, None is returned.
        :param name: Name of the group to fetch.
        :param realm: Realm in which the group resides; default 'master'
        :param parents: Optional list of parents when group to look for is a subgroup
        """
        try:
            if parents:
                parent = self.get_subgroup_direct_parent(parents, realm)

                if not parent:
                    return None

                all_groups = self.get_subgroups(parent, realm)
            else:
                all_groups = self.get_groups(realm=realm)

            for group in all_groups:
                if group['name'] == name:
                    return self.get_group_by_groupid(group['id'], realm=realm)

            return None

        except Exception as e:
            self.module.fail_json(msg="Could not fetch group %s in realm %s: %s"
                                      % (name, realm, str(e)))

    def _get_normed_group_parent(self, parent):
        """ Converts parent dict information into a more easy to use form.

        :param parent: parent describing dict
        """
        if parent['id']:
            return (parent['id'], True)

        return (parent['name'], False)

    def get_subgroup_by_chain(self, name_chain, realm="master"):
        """ Access a subgroup API object by walking down a given name/id chain.

        Groups can be given either as by name or by ID, the first element
        must either be a toplvl group or given as ID, all parents must exist.

        If the group cannot be found, None is returned.
        :param name_chain: Topdown ordered list of subgroup parent (ids or names) + its own name at the end
        :param realm: Realm in which the group resides; default 'master'
        """
        cp = name_chain[0]

        # for 1st parent in chain we must query the server
        cp, is_id = self._get_normed_group_parent(cp)

        if is_id:
            tmp = self.get_group_by_groupid(cp, realm=realm)
        else:
            # given as name, assume toplvl group
            tmp = self.get_group_by_name(cp, realm=realm)

        if not tmp:
            return None

        for p in name_chain[1:]:
            for sg in self.get_subgroups(tmp):
                pv, is_id = self._get_normed_group_parent(p)

                if is_id:
                    cmpkey = "id"
                else:
                    cmpkey = "name"

                if pv == sg[cmpkey]:
                    tmp = sg
                    break

            if not tmp:
                return None

        return tmp

    def get_subgroup_direct_parent(self, parents, realm="master", children_to_resolve=None):
        """ Get keycloak direct parent group API object for a given chain of parents.

        To successfully work the API for subgroups we actually don't need
        to "walk the whole tree" for nested groups but only need to know
        the ID for the direct predecessor of current subgroup. This
        method will guarantee us this information getting there with
        as minimal work as possible.

        Note that given parent list can and might be incomplete at the
        upper levels as long as it starts with an ID instead of a name

        If the group does not exist, None is returned.
        :param parents: Topdown ordered list of subgroup parents
        :param realm: Realm in which the group resides; default 'master'
        """
        if children_to_resolve is None:
            # start recursion by reversing parents (in optimal cases
            # we dont need to walk the whole tree upwarts)
            parents = list(reversed(parents))
            children_to_resolve = []

        if not parents:
            # walk complete parents list to the top, all names, no id's,
            # try to resolve it assuming list is complete and 1st
            # element is a toplvl group
            return self.get_subgroup_by_chain(list(reversed(children_to_resolve)), realm=realm)

        cp = parents[0]
        unused, is_id = self._get_normed_group_parent(cp)

        if is_id:
            # current parent is given as ID, we can stop walking
            # upwards searching for an entry point
            return self.get_subgroup_by_chain([cp] + list(reversed(children_to_resolve)), realm=realm)
        else:
            # current parent is given as name, it must be resolved
            # later, try next parent (recurse)
            children_to_resolve.append(cp)
            return self.get_subgroup_direct_parent(
                parents[1:],
                realm=realm, children_to_resolve=children_to_resolve
            )

    def create_group(self, grouprep, realm="master"):
        """ Create a Keycloak group.

        :param grouprep: a GroupRepresentation of the group to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            return self._request(groups_url, method='POST', data=json.dumps(grouprep))
        except Exception as e:
            self.fail_request(e, msg="Could not create group %s in realm %s: %s"
                                     % (grouprep['name'], realm, str(e)))

    def create_subgroup(self, parents, grouprep, realm="master"):
        """ Create a Keycloak subgroup.

        :param parents: list of one or more parent groups
        :param grouprep: a GroupRepresentation of the group to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        parent_id = "---UNDETERMINED---"
        try:
            parent_id = self.get_subgroup_direct_parent(parents, realm)

            if not parent_id:
                raise Exception(
                    "Could not determine subgroup parent ID for given"
                    " parent chain {0}. Assure that all parents exist"
                    " already and the list is complete and properly"
                    " ordered, starts with an ID or starts at the"
                    " top level".format(parents)
                )

            parent_id = parent_id["id"]
            url = URL_GROUP_CHILDREN.format(url=self.baseurl, realm=realm, groupid=parent_id)
            return self._request(url, method='POST', data=json.dumps(grouprep))
        except Exception as e:
            self.fail_request(e, msg="Could not create subgroup %s for parent group %s in realm %s: %s"
                                     % (grouprep['name'], parent_id, realm, str(e)))

    def update_group(self, grouprep, realm="master"):
        """ Update an existing group.

        :param grouprep: A GroupRepresentation of the updated group.
        :return HTTPResponse object on success
        """
        group_url = URL_GROUP.format(url=self.baseurl, realm=realm, groupid=grouprep['id'])

        try:
            return self._request(group_url, method='PUT', data=json.dumps(grouprep))
        except Exception as e:
            self.fail_request(e, msg='Could not update group %s in realm %s: %s'
                                     % (grouprep['name'], realm, str(e)))

    def delete_group(self, name=None, groupid=None, realm="master"):
        """ Delete a group. One of name or groupid must be provided.

        Providing the group ID is preferred as it avoids a second lookup to
        convert a group name to an ID.

        :param name: The name of the group. A lookup will be performed to retrieve the group ID.
        :param groupid: The ID of the group (preferred to name).
        :param realm: The realm in which this group resides, default "master".
        """

        if groupid is None and name is None:
            # prefer an exception since this is almost certainly a programming error in the module itself.
            raise Exception("Unable to delete group - one of group ID or name must be provided.")

        # only lookup the name if groupid isn't provided.
        # in the case that both are provided, prefer the ID, since it is one
        # less lookup.
        if groupid is None and name is not None:
            for group in self.get_groups(realm=realm):
                if group['name'] == name:
                    groupid = group['id']
                    break

        # if the group doesn't exist - no problem, nothing to delete.
        if groupid is None:
            return None

        # should have a good groupid by here.
        group_url = URL_GROUP.format(realm=realm, groupid=groupid, url=self.baseurl)
        try:
            return self._request(group_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg="Unable to delete group %s: %s" % (groupid, str(e)))

    def get_realm_roles(self, realm='master'):
        """ Obtains role representations for roles in a realm

        :param realm: realm to be queried
        :return: list of dicts of role representations
        """
        rolelist_url = URL_REALM_ROLES.format(url=self.baseurl, realm=realm)
        try:
            return self._request_and_deserialize(rolelist_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of roles for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of roles for realm %s: %s'
                                     % (realm, str(e)))

    def get_realm_role(self, name, realm='master'):
        """ Fetch a keycloak role from the provided realm using the role's name.

        If the role does not exist, None is returned.
        :param name: Name of the role to fetch.
        :param realm: Realm in which the role resides; default 'master'.
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(name, safe=''))
        try:
            return self._request_and_deserialize(role_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not fetch role %s in realm %s: %s'
                                         % (name, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not fetch role %s in realm %s: %s'
                                      % (name, realm, str(e)))

    def create_realm_role(self, rolerep, realm='master'):
        """ Create a Keycloak realm role.

        :param rolerep: a RoleRepresentation of the role to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        roles_url = URL_REALM_ROLES.format(url=self.baseurl, realm=realm)
        try:
            if "composites" in rolerep:
                keycloak_compatible_composites = self.convert_role_composites(rolerep["composites"])
                rolerep["composites"] = keycloak_compatible_composites
            return self._request(roles_url, method='POST', data=json.dumps(rolerep))
        except Exception as e:
            self.fail_request(e, msg='Could not create role %s in realm %s: %s'
                                     % (rolerep['name'], realm, str(e)))

    def update_realm_role(self, rolerep, realm='master'):
        """ Update an existing realm role.

        :param rolerep: A RoleRepresentation of the updated role.
        :return HTTPResponse object on success
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(rolerep['name']), safe='')
        try:
            composites = None
            if "composites" in rolerep:
                composites = copy.deepcopy(rolerep["composites"])
                del rolerep["composites"]
            role_response = self._request(role_url, method='PUT', data=json.dumps(rolerep))
            if composites is not None:
                self.update_role_composites(rolerep=rolerep, composites=composites, realm=realm)
            return role_response
        except Exception as e:
            self.fail_request(e, msg='Could not update role %s in realm %s: %s'
                                     % (rolerep['name'], realm, str(e)))

    def get_role_composites(self, rolerep, clientid=None, realm='master'):
        composite_url = ''
        try:
            if clientid is not None:
                client = self.get_client_by_clientid(client_id=clientid, realm=realm)
                cid = client['id']
                composite_url = URL_CLIENT_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, id=cid, name=quote(rolerep["name"], safe=''))
            else:
                composite_url = URL_REALM_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, name=quote(rolerep["name"], safe=''))
            # Get existing composites
            return self._request_and_deserialize(composite_url, method='GET')
        except Exception as e:
            self.fail_request(e, msg='Could not get role %s composites in realm %s: %s'
                                     % (rolerep['name'], realm, str(e)))

    def create_role_composites(self, rolerep, composites, clientid=None, realm='master'):
        composite_url = ''
        try:
            if clientid is not None:
                client = self.get_client_by_clientid(client_id=clientid, realm=realm)
                cid = client['id']
                composite_url = URL_CLIENT_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, id=cid, name=quote(rolerep["name"], safe=''))
            else:
                composite_url = URL_REALM_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, name=quote(rolerep["name"], safe=''))
            # Get existing composites
            # create new composites
            return self._request(composite_url, method='POST', data=json.dumps(composites))
        except Exception as e:
            self.fail_request(e, msg='Could not create role %s composites in realm %s: %s'
                                     % (rolerep['name'], realm, str(e)))

    def delete_role_composites(self, rolerep, composites, clientid=None, realm='master'):
        composite_url = ''
        try:
            if clientid is not None:
                client = self.get_client_by_clientid(client_id=clientid, realm=realm)
                cid = client['id']
                composite_url = URL_CLIENT_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, id=cid, name=quote(rolerep["name"], safe=''))
            else:
                composite_url = URL_REALM_ROLE_COMPOSITES.format(url=self.baseurl, realm=realm, name=quote(rolerep["name"], safe=''))
            # Get existing composites
            # create new composites
            return self._request(composite_url, method='DELETE', data=json.dumps(composites))
        except Exception as e:
            self.fail_request(e, msg='Could not create role %s composites in realm %s: %s'
                                     % (rolerep['name'], realm, str(e)))

    def update_role_composites(self, rolerep, composites, clientid=None, realm='master'):
        # Get existing composites
        existing_composites = self.get_role_composites(rolerep=rolerep, clientid=clientid, realm=realm)
        composites_to_be_created = []
        composites_to_be_deleted = []
        for composite in composites:
            composite_found = False
            existing_composite_client = None
            for existing_composite in existing_composites:
                if existing_composite["clientRole"]:
                    existing_composite_client = self.get_client_by_id(existing_composite["containerId"], realm=realm)
                    if ("client_id" in composite
                            and composite['client_id'] is not None
                            and existing_composite_client["clientId"] == composite["client_id"]
                            and composite["name"] == existing_composite["name"]):
                        composite_found = True
                        break
                else:
                    if (("client_id" not in composite or composite['client_id'] is None)
                            and composite["name"] == existing_composite["name"]):
                        composite_found = True
                        break
            if not composite_found and ('state' not in composite or composite['state'] == 'present'):
                if "client_id" in composite and composite['client_id'] is not None:
                    client_roles = self.get_client_roles(clientid=composite['client_id'], realm=realm)
                    for client_role in client_roles:
                        if client_role['name'] == composite['name']:
                            composites_to_be_created.append(client_role)
                            break
                else:
                    realm_role = self.get_realm_role(name=composite["name"], realm=realm)
                    composites_to_be_created.append(realm_role)
            elif composite_found and 'state' in composite and composite['state'] == 'absent':
                if "client_id" in composite and composite['client_id'] is not None:
                    client_roles = self.get_client_roles(clientid=composite['client_id'], realm=realm)
                    for client_role in client_roles:
                        if client_role['name'] == composite['name']:
                            composites_to_be_deleted.append(client_role)
                            break
                else:
                    realm_role = self.get_realm_role(name=composite["name"], realm=realm)
                    composites_to_be_deleted.append(realm_role)

        if len(composites_to_be_created) > 0:
            # create new composites
            self.create_role_composites(rolerep=rolerep, composites=composites_to_be_created, clientid=clientid, realm=realm)
        if len(composites_to_be_deleted) > 0:
            # delete new composites
            self.delete_role_composites(rolerep=rolerep, composites=composites_to_be_deleted, clientid=clientid, realm=realm)

    def delete_realm_role(self, name, realm='master'):
        """ Delete a realm role.

        :param name: The name of the role.
        :param realm: The realm in which this role resides, default "master".
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(name, safe=''))
        try:
            return self._request(role_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Unable to delete role %s in realm %s: %s'
                                     % (name, realm, str(e)))

    def get_client_roles(self, clientid, realm='master'):
        """ Obtains role representations for client roles in a specific client

        :param clientid: Client id to be queried
        :param realm: Realm to be queried
        :return: List of dicts of role representations
        """
        cid = self.get_client_id(clientid, realm=realm)
        if cid is None:
            self.module.fail_json(msg='Could not find client %s in realm %s'
                                      % (clientid, realm))
        rolelist_url = URL_CLIENT_ROLES.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request_and_deserialize(rolelist_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of roles for client %s in realm %s: %s'
                                      % (clientid, realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of roles for client %s in realm %s: %s'
                                     % (clientid, realm, str(e)))

    def get_client_role(self, name, clientid, realm='master'):
        """ Fetch a keycloak client role from the provided realm using the role's name.

        :param name: Name of the role to fetch.
        :param clientid: Client id for the client role
        :param realm: Realm in which the role resides
        :return: Dict of role representation
        If the role does not exist, None is returned.
        """
        cid = self.get_client_id(clientid, realm=realm)
        if cid is None:
            self.module.fail_json(msg='Could not find client %s in realm %s'
                                      % (clientid, realm))
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(name, safe=''))
        try:
            return self._request_and_deserialize(role_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not fetch role %s in client %s of realm %s: %s'
                                         % (name, clientid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not fetch role %s for client %s in realm %s: %s'
                                      % (name, clientid, realm, str(e)))

    def create_client_role(self, rolerep, clientid, realm='master'):
        """ Create a Keycloak client role.

        :param rolerep: a RoleRepresentation of the role to be created. Must contain at minimum the field name.
        :param clientid: Client id for the client role
        :param realm: Realm in which the role resides
        :return: HTTPResponse object on success
        """
        cid = self.get_client_id(clientid, realm=realm)
        if cid is None:
            self.module.fail_json(msg='Could not find client %s in realm %s'
                                      % (clientid, realm))
        roles_url = URL_CLIENT_ROLES.format(url=self.baseurl, realm=realm, id=cid)
        try:
            if "composites" in rolerep:
                keycloak_compatible_composites = self.convert_role_composites(rolerep["composites"])
                rolerep["composites"] = keycloak_compatible_composites
            return self._request(roles_url, method='POST', data=json.dumps(rolerep))
        except Exception as e:
            self.fail_request(e, msg='Could not create role %s for client %s in realm %s: %s'
                                     % (rolerep['name'], clientid, realm, str(e)))

    def convert_role_composites(self, composites):
        keycloak_compatible_composites = {
            'client': {},
            'realm': []
        }
        for composite in composites:
            if 'state' not in composite or composite['state'] == 'present':
                if "client_id" in composite and composite["client_id"] is not None:
                    if composite["client_id"] not in keycloak_compatible_composites["client"]:
                        keycloak_compatible_composites["client"][composite["client_id"]] = []
                    keycloak_compatible_composites["client"][composite["client_id"]].append(composite["name"])
                else:
                    keycloak_compatible_composites["realm"].append(composite["name"])
        return keycloak_compatible_composites

    def update_client_role(self, rolerep, clientid, realm="master"):
        """ Update an existing client role.

        :param rolerep: A RoleRepresentation of the updated role.
        :param clientid: Client id for the client role
        :param realm: Realm in which the role resides
        :return HTTPResponse object on success
        """
        cid = self.get_client_id(clientid, realm=realm)
        if cid is None:
            self.module.fail_json(msg='Could not find client %s in realm %s'
                                      % (clientid, realm))
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(rolerep['name'], safe=''))
        try:
            composites = None
            if "composites" in rolerep:
                composites = copy.deepcopy(rolerep["composites"])
                del rolerep['composites']
            update_role_response = self._request(role_url, method='PUT', data=json.dumps(rolerep))
            if composites is not None:
                self.update_role_composites(rolerep=rolerep, clientid=clientid, composites=composites, realm=realm)
            return update_role_response
        except Exception as e:
            self.fail_request(e, msg='Could not update role %s for client %s in realm %s: %s'
                                     % (rolerep['name'], clientid, realm, str(e)))

    def delete_client_role(self, name, clientid, realm="master"):
        """ Delete a role. One of name or roleid must be provided.

        :param name: The name of the role.
        :param clientid: Client id for the client role
        :param realm: Realm in which the role resides
        """
        cid = self.get_client_id(clientid, realm=realm)
        if cid is None:
            self.module.fail_json(msg='Could not find client %s in realm %s'
                                      % (clientid, realm))
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(name, safe=''))
        try:
            return self._request(role_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Unable to delete role %s for client %s in realm %s: %s'
                                     % (name, clientid, realm, str(e)))

    def get_authentication_flow_by_alias(self, alias, realm='master'):
        """
        Get an authentication flow by its alias
        :param alias: Alias of the authentication flow to get.
        :param realm: Realm.
        :return: Authentication flow representation.
        """
        try:
            authentication_flow = {}
            # Check if the authentication flow exists on the Keycloak serveraders
            authentications = json.load(self._request(URL_AUTHENTICATION_FLOWS.format(url=self.baseurl, realm=realm), method='GET'))
            for authentication in authentications:
                if authentication["alias"] == alias:
                    authentication_flow = authentication
                    break
            return authentication_flow
        except Exception as e:
            self.fail_request(e, msg="Unable get authentication flow %s: %s" % (alias, str(e)))

    def delete_authentication_flow_by_id(self, id, realm='master'):
        """
        Delete an authentication flow from Keycloak
        :param id: id of authentication flow to be deleted
        :param realm: realm of client to be deleted
        :return: HTTPResponse object on success
        """
        flow_url = URL_AUTHENTICATION_FLOW.format(url=self.baseurl, realm=realm, id=id)

        try:
            return self._request(flow_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete authentication flow %s in realm %s: %s'
                                     % (id, realm, str(e)))

    def copy_auth_flow(self, config, realm='master'):
        """
        Create a new authentication flow from a copy of another.
        :param config: Representation of the authentication flow to create.
        :param realm: Realm.
        :return: Representation of the new authentication flow.
        """
        try:
            new_name = dict(
                newName=config["alias"]
            )
            self._request(
                URL_AUTHENTICATION_FLOW_COPY.format(
                    url=self.baseurl,
                    realm=realm,
                    copyfrom=quote(config["copyFrom"], safe='')),
                method='POST',
                data=json.dumps(new_name))
            flow_list = json.load(
                self._request(
                    URL_AUTHENTICATION_FLOWS.format(url=self.baseurl,
                                                    realm=realm),
                    method='GET'))
            for flow in flow_list:
                if flow["alias"] == config["alias"]:
                    return flow
            return None
        except Exception as e:
            self.fail_request(e, msg='Could not copy authentication flow %s in realm %s: %s'
                                     % (config["alias"], realm, str(e)))

    def create_empty_auth_flow(self, config, realm='master'):
        """
        Create a new empty authentication flow.
        :param config: Representation of the authentication flow to create.
        :param realm: Realm.
        :return: Representation of the new authentication flow.
        """
        try:
            new_flow = dict(
                alias=config["alias"],
                providerId=config["providerId"],
                description=config["description"],
                topLevel=True
            )
            self._request(
                URL_AUTHENTICATION_FLOWS.format(
                    url=self.baseurl,
                    realm=realm),
                method='POST',
                data=json.dumps(new_flow))
            flow_list = json.load(
                self._request(
                    URL_AUTHENTICATION_FLOWS.format(
                        url=self.baseurl,
                        realm=realm),
                    method='GET'))
            for flow in flow_list:
                if flow["alias"] == config["alias"]:
                    return flow
            return None
        except Exception as e:
            self.fail_request(e, msg='Could not create empty authentication flow %s in realm %s: %s'
                                     % (config["alias"], realm, str(e)))

    def update_authentication_executions(self, flowAlias, updatedExec, realm='master'):
        """ Update authentication executions

        :param flowAlias: name of the parent flow
        :param updatedExec: JSON containing updated execution
        :return: HTTPResponse object on success
        """
        try:
            self._request(
                URL_AUTHENTICATION_FLOW_EXECUTIONS.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias, safe='')),
                method='PUT',
                data=json.dumps(updatedExec))
        except HTTPError as e:
            self.fail_request(e, msg="Unable to update execution '%s': %s: %s %s"
                                     % (flowAlias, repr(e), ";".join([e.url, e.msg, str(e.code), str(e.hdrs)]), str(updatedExec)))
        except Exception as e:
            self.module.fail_json(msg="Unable to update executions %s: %s" % (updatedExec, str(e)))

    def add_authenticationConfig_to_execution(self, executionId, authenticationConfig, realm='master'):
        """ Add autenticatorConfig to the execution

        :param executionId: id of execution
        :param authenticationConfig: config to add to the execution
        :return: HTTPResponse object on success
        """
        try:
            self._request(
                URL_AUTHENTICATION_EXECUTION_CONFIG.format(
                    url=self.baseurl,
                    realm=realm,
                    id=executionId),
                method='POST',
                data=json.dumps(authenticationConfig))
        except Exception as e:
            self.fail_request(e, msg="Unable to add authenticationConfig %s: %s" % (executionId, str(e)))

    def delete_authentication_config(self, configId, realm='master'):
        """ Delete authenticator config

        :param configId: id of authentication config
        :param realm: realm of authentication config to be deleted
        """
        try:
            # Send a DELETE request to remove the specified authentication config from the Keycloak server.
            self._request(
                URL_AUTHENTICATION_CONFIG.format(
                    url=self.baseurl,
                    realm=realm,
                    id=configId),
                method='DELETE')
        except Exception as e:
            self.fail_request(e, msg="Unable to delete authentication config %s: %s" % (configId, str(e)))

    def create_subflow(self, subflowName, flowAlias, realm='master', flowType='basic-flow'):
        """ Create new sublow on the flow

        :param subflowName: name of the subflow to create
        :param flowAlias: name of the parent flow
        :return: HTTPResponse object on success
        """
        try:
            newSubFlow = {}
            newSubFlow["alias"] = subflowName
            newSubFlow["provider"] = "registration-page-form"
            newSubFlow["type"] = flowType
            self._request(
                URL_AUTHENTICATION_FLOW_EXECUTIONS_FLOW.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias, safe='')),
                method='POST',
                data=json.dumps(newSubFlow))
        except Exception as e:
            self.fail_request(e, msg="Unable to create new subflow %s: %s" % (subflowName, str(e)))

    def create_execution(self, execution, flowAlias, realm='master'):
        """ Create new execution on the flow

        :param execution: name of execution to create
        :param flowAlias: name of the parent flow
        :return: HTTPResponse object on success
        """
        try:
            newExec = {}
            newExec["provider"] = execution["providerId"]
            newExec["requirement"] = execution["requirement"]
            self._request(
                URL_AUTHENTICATION_FLOW_EXECUTIONS_EXECUTION.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias, safe='')),
                method='POST',
                data=json.dumps(newExec))
        except HTTPError as e:
            self.fail_request(e, msg="Unable to create new execution '%s' %s: %s: %s %s"
                                     % (flowAlias, execution["providerId"], repr(e), ";".join([e.url, e.msg, str(e.code), str(e.hdrs)]), str(newExec)))
        except Exception as e:
            self.module.fail_json(msg="Unable to create new execution '%s' %s: %s" % (flowAlias, execution["providerId"], repr(e)))

    def change_execution_priority(self, executionId, diff, realm='master'):
        """ Raise or lower execution priority of diff time

        :param executionId: id of execution to lower priority
        :param realm: realm the client is in
        :param diff: Integer number, raise of diff time if positive lower of diff time if negative
        :return: HTTPResponse object on success
        """
        try:
            if diff > 0:
                for i in range(diff):
                    self._request(
                        URL_AUTHENTICATION_EXECUTION_RAISE_PRIORITY.format(
                            url=self.baseurl,
                            realm=realm,
                            id=executionId),
                        method='POST')
            elif diff < 0:
                for i in range(-diff):
                    self._request(
                        URL_AUTHENTICATION_EXECUTION_LOWER_PRIORITY.format(
                            url=self.baseurl,
                            realm=realm,
                            id=executionId),
                        method='POST')
        except Exception as e:
            self.fail_request(e, msg="Unable to change execution priority %s: %s" % (executionId, str(e)))

    def get_executions_representation(self, config, realm='master'):
        """
        Get a representation of the executions for an authentication flow.
        :param config: Representation of the authentication flow
        :param realm: Realm
        :return: Representation of the executions
        """
        try:
            # Get executions created
            executions = json.load(
                self._request(
                    URL_AUTHENTICATION_FLOW_EXECUTIONS.format(
                        url=self.baseurl,
                        realm=realm,
                        flowalias=quote(config["alias"], safe='')),
                    method='GET'))
            for execution in executions:
                if "authenticationConfig" in execution:
                    execConfigId = execution["authenticationConfig"]
                    execConfig = json.load(
                        self._request(
                            URL_AUTHENTICATION_CONFIG.format(
                                url=self.baseurl,
                                realm=realm,
                                id=execConfigId),
                            method='GET'))
                    execution["authenticationConfig"] = execConfig
            return executions
        except Exception as e:
            self.fail_request(e, msg='Could not get executions for authentication flow %s in realm %s: %s'
                                     % (config["alias"], realm, str(e)))

    def get_required_actions(self, realm='master'):
        """
        Get required actions.
        :param realm: Realm name (not id).
        :return:      List of representations of the required actions.
        """

        try:
            required_actions = json.load(
                self._request(
                    URL_AUTHENTICATION_REQUIRED_ACTIONS.format(
                        url=self.baseurl,
                        realm=realm
                    ),
                    method='GET'
                )
            )

            return required_actions
        except Exception:
            return None

    def register_required_action(self, rep, realm='master'):
        """
        Register required action.
        :param rep:   JSON containing 'providerId', and 'name' attributes.
        :param realm: Realm name (not id).
        :return:      Representation of the required action.
        """

        data = {
            'name': rep['name'],
            'providerId': rep['providerId']
        }

        try:
            return self._request(
                URL_AUTHENTICATION_REGISTER_REQUIRED_ACTION.format(
                    url=self.baseurl,
                    realm=realm
                ),
                method='POST',
                data=json.dumps(data),
            )
        except Exception as e:
            self.fail_request(
                e,
                msg='Unable to register required action %s in realm %s: %s'
                % (rep["name"], realm, str(e))
            )

    def update_required_action(self, alias, rep, realm='master'):
        """
        Update required action.
        :param alias: Alias of required action.
        :param rep:   JSON describing new state of required action.
        :param realm: Realm name (not id).
        :return:      HTTPResponse object on success.
        """

        try:
            return self._request(
                URL_AUTHENTICATION_REQUIRED_ACTIONS_ALIAS.format(
                    url=self.baseurl,
                    alias=quote(alias, safe=''),
                    realm=realm
                ),
                method='PUT',
                data=json.dumps(rep),
            )
        except Exception as e:
            self.fail_request(
                e,
                msg='Unable to update required action %s in realm %s: %s'
                % (alias, realm, str(e))
            )

    def delete_required_action(self, alias, realm='master'):
        """
        Delete required action.
        :param alias: Alias of required action.
        :param realm: Realm name (not id).
        :return:      HTTPResponse object on success.
        """

        try:
            return self._request(
                URL_AUTHENTICATION_REQUIRED_ACTIONS_ALIAS.format(
                    url=self.baseurl,
                    alias=quote(alias, safe=''),
                    realm=realm
                ),
                method='DELETE',
            )
        except Exception as e:
            self.fail_request(
                e,
                msg='Unable to delete required action %s in realm %s: %s'
                % (alias, realm, str(e))
            )

    def get_identity_providers(self, realm='master'):
        """ Fetch representations for identity providers in a realm
        :param realm: realm to be queried
        :return: list of representations for identity providers
        """
        idps_url = URL_IDENTITY_PROVIDERS.format(url=self.baseurl, realm=realm)
        try:
            return self._request_and_deserialize(idps_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of identity providers for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of identity providers for realm %s: %s'
                                     % (realm, str(e)))

    def get_identity_provider(self, alias, realm='master'):
        """ Fetch identity provider representation from a realm using the idp's alias.
        If the identity provider does not exist, None is returned.
        :param alias: Alias of the identity provider to fetch.
        :param realm: Realm in which the identity provider resides; default 'master'.
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return self._request_and_deserialize(idp_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not fetch identity provider %s in realm %s: %s'
                                         % (alias, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not fetch identity provider %s in realm %s: %s'
                                      % (alias, realm, str(e)))

    def create_identity_provider(self, idprep, realm='master'):
        """ Create an identity provider.
        :param idprep: Identity provider representation of the idp to be created.
        :param realm: Realm in which this identity provider resides, default "master".
        :return: HTTPResponse object on success
        """
        idps_url = URL_IDENTITY_PROVIDERS.format(url=self.baseurl, realm=realm)
        try:
            return self._request(idps_url, method='POST', data=json.dumps(idprep))
        except Exception as e:
            self.fail_request(e, msg='Could not create identity provider %s in realm %s: %s'
                                     % (idprep['alias'], realm, str(e)))

    def update_identity_provider(self, idprep, realm='master'):
        """ Update an existing identity provider.
        :param idprep: Identity provider representation of the idp to be updated.
        :param realm: Realm in which this identity provider resides, default "master".
        :return HTTPResponse object on success
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=idprep['alias'])
        try:
            return self._request(idp_url, method='PUT', data=json.dumps(idprep))
        except Exception as e:
            self.fail_request(e, msg='Could not update identity provider %s in realm %s: %s'
                                     % (idprep['alias'], realm, str(e)))

    def delete_identity_provider(self, alias, realm='master'):
        """ Delete an identity provider.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return self._request(idp_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Unable to delete identity provider %s in realm %s: %s'
                                     % (alias, realm, str(e)))

    def get_identity_provider_mappers(self, alias, realm='master'):
        """ Fetch representations for identity provider mappers
        :param alias: Alias of the identity provider.
        :param realm: realm to be queried
        :return: list of representations for identity provider mappers
        """
        mappers_url = URL_IDENTITY_PROVIDER_MAPPERS.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return self._request_and_deserialize(mappers_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of identity provider mappers for idp %s in realm %s: %s'
                                      % (alias, realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of identity provider mappers for idp %s in realm %s: %s'
                                     % (alias, realm, str(e)))

    def fetch_idp_endpoints_import_config_url(self, fromUrl, providerId='oidc', realm='master'):
        """ Import an identity provider configuration through Keycloak server from a well-known URL.
        :param fromUrl: URL to import the identity provider configuration from.
        "param providerId: Provider ID of the identity provider to import, default 'oidc'.
        :param realm: Realm
        :return: IDP endpoins.
        """
        try:
            payload = {
                "providerId": providerId,
                "fromUrl": fromUrl
            }
            idps_url = URL_IDENTITY_PROVIDER_IMPORT.format(url=self.baseurl, realm=realm)
            return self._request_and_deserialize(idps_url, method='POST', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not import the IdP config in realm %s: %s' % (realm, str(e)))

    def get_identity_provider_mapper(self, mid, alias, realm='master'):
        """ Fetch identity provider representation from a realm using the idp's alias.
        If the identity provider does not exist, None is returned.
        :param mid: Unique ID of the mapper to fetch.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which the identity provider resides; default 'master'.
        """
        mapper_url = URL_IDENTITY_PROVIDER_MAPPER.format(url=self.baseurl, realm=realm, alias=alias, id=mid)
        try:
            return self._request_and_deserialize(mapper_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not fetch mapper %s for identity provider %s in realm %s: %s'
                                         % (mid, alias, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not fetch mapper %s for identity provider %s in realm %s: %s'
                                      % (mid, alias, realm, str(e)))

    def create_identity_provider_mapper(self, mapper, alias, realm='master'):
        """ Create an identity provider mapper.
        :param mapper: IdentityProviderMapperRepresentation of the mapper to be created.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        :return: HTTPResponse object on success
        """
        mappers_url = URL_IDENTITY_PROVIDER_MAPPERS.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return self._request(mappers_url, method='POST', data=json.dumps(mapper))
        except Exception as e:
            self.fail_request(e, msg='Could not create identity provider mapper %s for idp %s in realm %s: %s'
                                     % (mapper['name'], alias, realm, str(e)))

    def update_identity_provider_mapper(self, mapper, alias, realm='master'):
        """ Update an existing identity provider.
        :param mapper: IdentityProviderMapperRepresentation of the mapper to be updated.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        :return HTTPResponse object on success
        """
        mapper_url = URL_IDENTITY_PROVIDER_MAPPER.format(url=self.baseurl, realm=realm, alias=alias, id=mapper['id'])
        try:
            return self._request(mapper_url, method='PUT', data=json.dumps(mapper))
        except Exception as e:
            self.fail_request(e, msg='Could not update mapper %s for identity provider %s in realm %s: %s'
                                     % (mapper['id'], alias, realm, str(e)))

    def delete_identity_provider_mapper(self, mid, alias, realm='master'):
        """ Delete an identity provider.
        :param mid: Unique ID of the mapper to delete.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        """
        mapper_url = URL_IDENTITY_PROVIDER_MAPPER.format(url=self.baseurl, realm=realm, alias=alias, id=mid)
        try:
            return self._request(mapper_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Unable to delete mapper %s for identity provider %s in realm %s: %s'
                                     % (mid, alias, realm, str(e)))

    def get_components(self, filter=None, realm='master'):
        """ Fetch representations for components in a realm
        :param realm: realm to be queried
        :param filter: search filter
        :return: list of representations for components
        """
        comps_url = URL_COMPONENTS.format(url=self.baseurl, realm=realm)
        if filter is not None:
            comps_url += '?%s' % filter

        try:
            return self._request_and_deserialize(comps_url, method='GET')
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of components for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.fail_request(e, msg='Could not obtain list of components for realm %s: %s'
                                     % (realm, str(e)))

    def get_component(self, cid, realm='master'):
        """ Fetch component representation from a realm using its cid.
        If the component does not exist, None is returned.
        :param cid: Unique ID of the component to fetch.
        :param realm: Realm in which the component resides; default 'master'.
        """
        comp_url = URL_COMPONENT.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request_and_deserialize(comp_url, method="GET")
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.fail_request(e, msg='Could not fetch component %s in realm %s: %s'
                                         % (cid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not fetch component %s in realm %s: %s'
                                      % (cid, realm, str(e)))

    def create_component(self, comprep, realm='master'):
        """ Create an component.
        :param comprep: Component representation of the component to be created.
        :param realm: Realm in which this component resides, default "master".
        :return: Component representation of the created component
        """
        comps_url = URL_COMPONENTS.format(url=self.baseurl, realm=realm)
        try:
            resp = self._request(comps_url, method='POST', data=json.dumps(comprep))
            comp_url = resp.getheader('Location')
            if comp_url is None:
                self.module.fail_json(msg='Could not create component in realm %s: %s'
                                          % (realm, 'unexpected response'))
            return self._request_and_deserialize(comp_url, method="GET")
        except Exception as e:
            self.fail_request(e, msg='Could not create component in realm %s: %s'
                                     % (realm, str(e)))

    def update_component(self, comprep, realm='master'):
        """ Update an existing component.
        :param comprep: Component representation of the component to be updated.
        :param realm: Realm in which this component resides, default "master".
        :return HTTPResponse object on success
        """
        cid = comprep.get('id')
        if cid is None:
            self.module.fail_json(msg='Cannot update component without id')
        comp_url = URL_COMPONENT.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request(comp_url, method='PUT', data=json.dumps(comprep))
        except Exception as e:
            self.fail_request(e, msg='Could not update component %s in realm %s: %s'
                                     % (cid, realm, str(e)))

    def delete_component(self, cid, realm='master'):
        """ Delete an component.
        :param cid: Unique ID of the component.
        :param realm: Realm in which this component resides, default "master".
        """
        comp_url = URL_COMPONENT.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return self._request(comp_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Unable to delete component %s in realm %s: %s'
                                     % (cid, realm, str(e)))

    def get_authz_authorization_scope_by_name(self, name, client_id, realm):
        url = URL_AUTHZ_AUTHORIZATION_SCOPES.format(url=self.baseurl, client_id=client_id, realm=realm)
        search_url = "%s/search?name=%s" % (url, quote(name, safe=''))

        try:
            return self._request_and_deserialize(search_url, method='GET')
        except Exception:
            return False

    def create_authz_authorization_scope(self, payload, client_id, realm):
        """Create an authorization scope for a Keycloak client"""
        url = URL_AUTHZ_AUTHORIZATION_SCOPES.format(url=self.baseurl, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='POST', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not create authorization scope %s for client %s in realm %s: %s' % (payload['name'], client_id, realm, str(e)))

    def update_authz_authorization_scope(self, payload, id, client_id, realm):
        """Update an authorization scope for a Keycloak client"""
        url = URL_AUTHZ_AUTHORIZATION_SCOPE.format(url=self.baseurl, id=id, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='PUT', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not create update scope %s for client %s in realm %s: %s' % (payload['name'], client_id, realm, str(e)))

    def remove_authz_authorization_scope(self, id, client_id, realm):
        """Remove an authorization scope from a Keycloak client"""
        url = URL_AUTHZ_AUTHORIZATION_SCOPE.format(url=self.baseurl, id=id, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete scope %s for client %s in realm %s: %s' % (id, client_id, realm, str(e)))

    def get_user_by_id(self, user_id, realm='master'):
        """
        Get a User by its ID.
        :param user_id: ID of the user.
        :param realm: Realm
        :return: Representation of the user.
        """
        try:
            user_url = URL_USER.format(
                url=self.baseurl,
                realm=realm,
                id=user_id)
            userrep = json.load(
                self._request(
                    user_url,
                    method='GET'))
            return userrep
        except Exception as e:
            self.fail_request(e, msg='Could not get user %s in realm %s: %s'
                                     % (user_id, realm, str(e)))

    def create_user(self, userrep, realm='master'):
        """
        Create a new User.
        :param userrep: Representation of the user to create
        :param realm: Realm
        :return: Representation of the user created.
        """
        try:
            if 'attributes' in userrep and isinstance(userrep['attributes'], list):
                attributes = copy.deepcopy(userrep['attributes'])
                userrep['attributes'] = self.convert_user_attributes_to_keycloak_dict(attributes=attributes)
            users_url = URL_USERS.format(
                url=self.baseurl,
                realm=realm)
            self._request(users_url,
                          method='POST',
                          data=json.dumps(userrep))
            created_user = self.get_user_by_username(
                username=userrep['username'],
                realm=realm)
            return created_user
        except Exception as e:
            self.fail_request(e, msg='Could not create user %s in realm %s: %s'
                                     % (userrep['username'], realm, str(e)))

    def convert_user_attributes_to_keycloak_dict(self, attributes):
        keycloak_user_attributes_dict = {}
        for attribute in attributes:
            if ('state' not in attribute or attribute['state'] == 'present') and 'name' in attribute:
                keycloak_user_attributes_dict[attribute['name']] = attribute['values'] if 'values' in attribute else []
        return keycloak_user_attributes_dict

    def convert_keycloak_user_attributes_dict_to_module_list(self, attributes):
        module_attributes_list = []
        for key in attributes:
            attr = {}
            attr['name'] = key
            attr['values'] = attributes[key]
            module_attributes_list.append(attr)
        return module_attributes_list

    def update_user(self, userrep, realm='master'):
        """
        Update a User.
        :param userrep: Representation of the user to update. This representation must include the ID of the user.
        :param realm: Realm
        :return: Representation of the updated user.
        """
        try:
            if 'attributes' in userrep and isinstance(userrep['attributes'], list):
                attributes = copy.deepcopy(userrep['attributes'])
                userrep['attributes'] = self.convert_user_attributes_to_keycloak_dict(attributes=attributes)
            user_url = URL_USER.format(
                url=self.baseurl,
                realm=realm,
                id=userrep["id"])
            self._request(
                user_url,
                method='PUT',
                data=json.dumps(userrep))
            updated_user = self.get_user_by_id(
                user_id=userrep['id'],
                realm=realm)
            return updated_user
        except Exception as e:
            self.fail_request(e, msg='Could not update user %s in realm %s: %s'
                                     % (userrep['username'], realm, str(e)))

    def delete_user(self, user_id, realm='master'):
        """
        Delete a User.
        :param user_id: ID of the user to be deleted
        :param realm: Realm
        :return: HTTP response.
        """
        try:
            user_url = URL_USER.format(
                url=self.baseurl,
                realm=realm,
                id=user_id)
            return self._request(
                user_url,
                method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete user %s in realm %s: %s'
                                     % (user_id, realm, str(e)))

    def get_user_groups(self, user_id, realm='master'):
        """
        Get the group names for a user.
        :param user_id: User ID
        :param realm: Realm
        :return: The client group names as a list of strings.
        """
        user_groups = self.get_user_group_details(user_id, realm)
        return [user_group['name'] for user_group in user_groups if 'name' in user_group]

    def get_user_group_details(self, user_id, realm='master'):
        """
        Get the group details for a user.
        :param user_id: User ID
        :param realm: Realm
        :return: The client group details as a list of dictionaries.
        """
        try:
            user_groups_url = URL_USER_GROUPS.format(url=self.baseurl, realm=realm, id=user_id)
            return self._request_and_deserialize(user_groups_url, method='GET')
        except Exception as e:
            self.fail_request(e, msg='Could not get groups for user %s in realm %s: %s'
                                     % (user_id, realm, str(e)))

    def add_user_in_group(self, user_id, group_id, realm='master'):
        """DEPRECATED: Call add_user_to_group(...) instead. This method is scheduled for removal in community.general 13.0.0."""
        return self.add_user_to_group(user_id, group_id, realm)

    def add_user_to_group(self, user_id, group_id, realm='master'):
        """
        Add a user to a group.
        :param user_id: User ID
        :param group_id: Group Id to add the user to.
        :param realm: Realm
        :return: HTTP Response
        """
        try:
            user_group_url = URL_USER_GROUP.format(
                url=self.baseurl,
                realm=realm,
                id=user_id,
                group_id=group_id)
            return self._request(
                user_group_url,
                method='PUT')
        except Exception as e:
            self.fail_request(e, msg='Could not add user %s to group %s in realm %s: %s'
                                     % (user_id, group_id, realm, str(e)))

    def remove_user_from_group(self, user_id, group_id, realm='master'):
        """
        Remove a user from a group for a user.
        :param user_id: User ID
        :param group_id: Group Id to add the user to.
        :param realm: Realm
        :return: HTTP response
        """
        try:
            user_group_url = URL_USER_GROUP.format(
                url=self.baseurl,
                realm=realm,
                id=user_id,
                group_id=group_id)
            return self._request(
                user_group_url,
                method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not remove user %s from group %s in realm %s: %s'
                                     % (user_id, group_id, realm, str(e)))

    def update_user_groups_membership(self, userrep, groups, realm='master'):
        """
        Update user's group membership
        :param userrep: Representation of the user. This representation must include the ID.
        :param realm: Realm
        :return: True if group membership has been changed. False Otherwise.
        """
        try:
            groups_to_add, groups_to_remove = self.extract_groups_to_add_to_and_remove_from_user(groups)
            if not groups_to_add and not groups_to_remove:
                return False

            user_groups = self.get_user_group_details(user_id=userrep['id'], realm=realm)
            user_group_names = [user_group['name'] for user_group in user_groups if 'name' in user_group]
            user_group_paths = [user_group['path'] for user_group in user_groups if 'path' in user_group]

            groups_to_add = [group_to_add for group_to_add in groups_to_add
                             if group_to_add not in user_group_names and group_to_add not in user_group_paths]
            groups_to_remove = [group_to_remove for group_to_remove in groups_to_remove
                                if group_to_remove in user_group_names or group_to_remove in user_group_paths]
            if not groups_to_add and not groups_to_remove:
                return False

            for group_to_add in groups_to_add:
                realm_group = self.find_group_by_path(group_to_add, realm=realm)
                if realm_group:
                    self.add_user_to_group(user_id=userrep['id'], group_id=realm_group['id'], realm=realm)

            for group_to_remove in groups_to_remove:
                realm_group = self.find_group_by_path(group_to_remove, realm=realm)
                if realm_group:
                    self.remove_user_from_group(user_id=userrep['id'], group_id=realm_group['id'], realm=realm)

            return True
        except Exception as e:
            self.module.fail_json(msg='Could not update group membership for user %s in realm %s: %s'
                                      % (userrep['username'], realm, e))

    def extract_groups_to_add_to_and_remove_from_user(self, groups):
        groups_to_add = []
        groups_to_remove = []
        if isinstance(groups, list):
            for group in groups:
                group_name = group['name'] if isinstance(group, dict) and 'name' in group else group
                if isinstance(group, dict):
                    if 'state' not in group or group['state'] == 'present':
                        groups_to_add.append(group_name)
                    else:
                        groups_to_remove.append(group_name)
        return groups_to_add, groups_to_remove

    def find_group_by_path(self, target, realm='master'):
        """
        Finds a realm group by path, e.g. '/my/group'.
        The path is formed by prepending a '/' character to `target` unless it's already present.
        This adds support for finding top level groups by name and subgroups by path.
        """
        groups = self.get_groups(realm=realm)
        path = target if target.startswith('/') else '/' + target
        for segment in path.split('/'):
            if not segment:
                continue
            abort = True
            for group in groups:
                if group['path'] == path:
                    return self.get_group_by_groupid(group['id'], realm=realm)
                if group['name'] == segment:
                    groups = self.get_subgroups(group, realm=realm)
                    abort = False
                    break
            if abort:
                break
        return None

    def convert_user_group_list_of_str_to_list_of_dict(self, groups):
        list_of_groups = []
        if isinstance(groups, list) and len(groups) > 0:
            for group in groups:
                if isinstance(group, str):
                    group_dict = {}
                    group_dict['name'] = group
                    list_of_groups.append(group_dict)
        return list_of_groups

    def create_authz_custom_policy(self, policy_type, payload, client_id, realm):
        """Create a custom policy for a Keycloak client"""
        url = URL_AUTHZ_CUSTOM_POLICY.format(url=self.baseurl, policy_type=policy_type, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='POST', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not create permission %s for client %s in realm %s: %s' % (payload['name'], client_id, realm, str(e)))

    def remove_authz_custom_policy(self, policy_id, client_id, realm):
        """Remove a custom policy from a Keycloak client"""
        url = URL_AUTHZ_CUSTOM_POLICIES.format(url=self.baseurl, client_id=client_id, realm=realm)
        delete_url = "%s/%s" % (url, policy_id)

        try:
            return self._request(delete_url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete custom policy %s for client %s in realm %s: %s' % (id, client_id, realm, str(e)))

    def get_authz_permission_by_name(self, name, client_id, realm):
        """Get authorization permission by name"""
        url = URL_AUTHZ_POLICIES.format(url=self.baseurl, client_id=client_id, realm=realm)
        search_url = "%s/search?name=%s" % (url, name.replace(' ', '%20'))

        try:
            return self._request_and_deserialize(search_url, method='GET')
        except Exception:
            return False

    def create_authz_permission(self, payload, permission_type, client_id, realm):
        """Create an authorization permission for a Keycloak client"""
        url = URL_AUTHZ_PERMISSIONS.format(url=self.baseurl, permission_type=permission_type, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='POST', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not create permission %s for client %s in realm %s: %s' % (payload['name'], client_id, realm, str(e)))

    def remove_authz_permission(self, id, client_id, realm):
        """Create an authorization permission for a Keycloak client"""
        url = URL_AUTHZ_POLICY.format(url=self.baseurl, id=id, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='DELETE')
        except Exception as e:
            self.fail_request(e, msg='Could not delete permission %s for client %s in realm %s: %s' % (id, client_id, realm, str(e)))

    def update_authz_permission(self, payload, permission_type, id, client_id, realm):
        """Update a permission for a Keycloak client"""
        url = URL_AUTHZ_PERMISSION.format(url=self.baseurl, permission_type=permission_type, id=id, client_id=client_id, realm=realm)

        try:
            return self._request(url, method='PUT', data=json.dumps(payload))
        except Exception as e:
            self.fail_request(e, msg='Could not create update permission %s for client %s in realm %s: %s' % (payload['name'], client_id, realm, str(e)))

    def get_authz_resource_by_name(self, name, client_id, realm):
        """Get authorization resource by name"""
        url = URL_AUTHZ_RESOURCES.format(url=self.baseurl, client_id=client_id, realm=realm)
        search_url = "%s/search?name=%s" % (url, name.replace(' ', '%20'))

        try:
            return self._request_and_deserialize(search_url, method='GET')
        except Exception:
            return False

    def get_authz_policy_by_name(self, name, client_id, realm):
        """Get authorization policy by name"""
        url = URL_AUTHZ_POLICIES.format(url=self.baseurl, client_id=client_id, realm=realm)
        search_url = "%s/search?name=%s&permission=false" % (url, name.replace(' ', '%20'))

        try:
            return self._request_and_deserialize(search_url, method='GET')
        except Exception:
            return False

    def get_client_role_scope_from_client(self, clientid, clientscopeid, realm="master"):
        """ Fetch the roles associated with the client's scope for a specific client on the Keycloak server.
        :param clientid: ID of the client from which to obtain the associated roles.
        :param clientscopeid: ID of the client who owns the roles.
        :param realm: Realm from which to obtain the scope.
        :return: The client scope of roles from specified client.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_CLIENTS.format(url=self.baseurl, realm=realm, id=clientid, scopeid=clientscopeid)
        try:
            return self._request_and_deserialize(client_role_scope_url, method='GET')
        except Exception as e:
            self.fail_request(e, msg='Could not fetch roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

    def update_client_role_scope_from_client(self, payload, clientid, clientscopeid, realm="master"):
        """ Update and fetch the roles associated with the client's scope on the Keycloak server.
        :param payload: List of roles to be added to the scope.
        :param clientid: ID of the client to update scope.
        :param clientscopeid: ID of the client who owns the roles.
        :param realm: Realm from which to obtain the clients.
        :return: The client scope of roles from specified client.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_CLIENTS.format(url=self.baseurl, realm=realm, id=clientid, scopeid=clientscopeid)
        try:
            self._request(client_role_scope_url, method='POST', data=json.dumps(payload))

        except Exception as e:
            self.fail_request(e, msg='Could not update roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

        return self.get_client_role_scope_from_client(clientid, clientscopeid, realm)

    def delete_client_role_scope_from_client(self, payload, clientid, clientscopeid, realm="master"):
        """ Delete the roles contains in the payload from the client's scope on the Keycloak server.
        :param payload: List of roles to be deleted.
        :param clientid: ID of the client to delete roles from scope.
        :param clientscopeid: ID of the client who owns the roles.
        :param realm: Realm from which to obtain the clients.
        :return: The client scope of roles from specified client.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_CLIENTS.format(url=self.baseurl, realm=realm, id=clientid, scopeid=clientscopeid)
        try:
            self._request(client_role_scope_url, method='DELETE', data=json.dumps(payload))

        except Exception as e:
            self.fail_request(e, msg='Could not delete roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

        return self.get_client_role_scope_from_client(clientid, clientscopeid, realm)

    def get_client_role_scope_from_realm(self, clientid, realm="master"):
        """ Fetch the realm roles from the client's scope on the Keycloak server.
        :param clientid: ID of the client from which to obtain the associated realm roles.
        :param realm: Realm from which to obtain the clients.
        :return: The client realm roles scope.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_REALM.format(url=self.baseurl, realm=realm, id=clientid)
        try:
            return self._request_and_deserialize(client_role_scope_url, method='GET')
        except Exception as e:
            self.fail_request(e, msg='Could not fetch roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

    def update_client_role_scope_from_realm(self, payload, clientid, realm="master"):
        """ Update and fetch the realm roles from the client's scope on the Keycloak server.
        :param payload: List of realm roles to add.
        :param clientid: ID of the client to update scope.
        :param realm: Realm from which to obtain the clients.
        :return: The client realm roles scope.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_REALM.format(url=self.baseurl, realm=realm, id=clientid)
        try:
            self._request(client_role_scope_url, method='POST', data=json.dumps(payload))

        except Exception as e:
            self.fail_request(e, msg='Could not update roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

        return self.get_client_role_scope_from_realm(clientid, realm)

    def delete_client_role_scope_from_realm(self, payload, clientid, realm="master"):
        """ Delete the realm roles contains in the payload from the client's scope on the Keycloak server.
        :param payload: List of realm roles to delete.
        :param clientid: ID of the client to delete roles from scope.
        :param realm: Realm from which to obtain the clients.
        :return: The client realm roles scope.
        """
        client_role_scope_url = URL_CLIENT_ROLE_SCOPE_REALM.format(url=self.baseurl, realm=realm, id=clientid)
        try:
            self._request(client_role_scope_url, method='DELETE', data=json.dumps(payload))

        except Exception as e:
            self.fail_request(e, msg='Could not delete roles scope for client %s in realm %s: %s' % (clientid, realm, str(e)))

        return self.get_client_role_scope_from_realm(clientid, realm)

    def fail_request(self, e, msg, **kwargs):
        """ Triggers a module failure. This should be called
        when an exception occurs during/after a request.
        Attempts to parse the exception e as an HTTP error
        and append it to msg.

        :param e: exception which triggered the failure
        :param msg: error message to display to the user
        :param kwargs: additional arguments to pass to module.fail_json
        :return: None
        """
        try:
            if isinstance(e, HTTPError):
                msg = "%s: %s" % (msg, to_native(e.read()))
        except Exception:
            pass
        self.module.fail_json(msg, **kwargs)

    def fail_open_url(self, e, msg, **kwargs):
        """ DEPRECATED: Use fail_request instead.

        Triggers a module failure. This should be called
        when an exception occurs during/after a request.
        Attempts to parse the exception e as an HTTP error
        and append it to msg.

        :param e: exception which triggered the failure
        :param msg: error message to display to the user
        :param kwargs: additional arguments to pass to module.fail_json
        :return: None
        """
        return self.fail_request(e, msg, **kwargs)

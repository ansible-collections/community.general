# -*- coding: utf-8 -*-
# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# BSD 2-Clause license (see LICENSES/BSD-2-Clause.txt)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import traceback

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.common.text.converters import to_native, to_text

URL_REALM_INFO = "{url}/realms/{realm}"
URL_REALMS = "{url}/admin/realms"
URL_REALM = "{url}/admin/realms/{realm}"

URL_TOKEN = "{url}/realms/{realm}/protocol/openid-connect/token"
URL_CLIENT = "{url}/admin/realms/{realm}/clients/{id}"
URL_CLIENTS = "{url}/admin/realms/{realm}/clients"

URL_CLIENT_ROLES = "{url}/admin/realms/{realm}/clients/{id}/roles"
URL_CLIENT_ROLE = "{url}/admin/realms/{realm}/clients/{id}/roles/{name}"
URL_CLIENT_ROLE_COMPOSITES = "{url}/admin/realms/{realm}/clients/{id}/roles/{name}/composites"

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

URL_CLIENTSCOPES = "{url}/admin/realms/{realm}/client-scopes"
URL_CLIENTSCOPE = "{url}/admin/realms/{realm}/client-scopes/{id}"
URL_CLIENTSCOPE_PROTOCOLMAPPERS = "{url}/admin/realms/{realm}/client-scopes/{id}/protocol-mappers/models"
URL_CLIENTSCOPE_PROTOCOLMAPPER = "{url}/admin/realms/{realm}/client-scopes/{id}/protocol-mappers/models/{mapper_id}"

URL_CLIENT_GROUP_ROLEMAPPINGS = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}"
URL_CLIENT_GROUP_ROLEMAPPINGS_AVAILABLE = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}/available"
URL_CLIENT_GROUP_ROLEMAPPINGS_COMPOSITE = "{url}/admin/realms/{realm}/groups/{id}/role-mappings/clients/{client}/composite"

URL_USERS = "{url}/admin/realms/{realm}/users"
URL_CLIENT_SERVICE_ACCOUNT_USER = "{url}/admin/realms/{realm}/clients/{id}/service-account-user"
URL_CLIENT_USER_ROLEMAPPINGS = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}"
URL_CLIENT_USER_ROLEMAPPINGS_AVAILABLE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/available"
URL_CLIENT_USER_ROLEMAPPINGS_COMPOSITE = "{url}/admin/realms/{realm}/users/{id}/role-mappings/clients/{client}/composite"

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

URL_IDENTITY_PROVIDERS = "{url}/admin/realms/{realm}/identity-provider/instances"
URL_IDENTITY_PROVIDER = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}"
URL_IDENTITY_PROVIDER_MAPPERS = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}/mappers"
URL_IDENTITY_PROVIDER_MAPPER = "{url}/admin/realms/{realm}/identity-provider/instances/{alias}/mappers/{id}"

URL_COMPONENTS = "{url}/admin/realms/{realm}/components"
URL_COMPONENT = "{url}/admin/realms/{realm}/components/{id}"


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
        http_agent=dict(type='str', default='Ansible'),
    )


def camel(words):
    return words.split('_')[0] + ''.join(x.capitalize() or '_' for x in words.split('_')[1:])


class KeycloakError(Exception):
    pass


def get_token(module_params):
    """ Obtains connection header with token for the authentication,
        token already given or obtained from credentials
        :param module_params: parameters of the module
        :return: connection header
    """
    token = module_params.get('token')
    base_url = module_params.get('auth_keycloak_url')
    http_agent = module_params.get('http_agent')

    if not base_url.lower().startswith(('http', 'https')):
        raise KeycloakError("auth_url '%s' should either start with 'http' or 'https'." % base_url)

    if token is None:
        base_url = module_params.get('auth_keycloak_url')
        validate_certs = module_params.get('validate_certs')
        auth_realm = module_params.get('auth_realm')
        client_id = module_params.get('auth_client_id')
        auth_username = module_params.get('auth_username')
        auth_password = module_params.get('auth_password')
        client_secret = module_params.get('auth_client_secret')
        connection_timeout = module_params.get('connection_timeout')
        auth_url = URL_TOKEN.format(url=base_url, realm=auth_realm)
        temp_payload = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': auth_username,
            'password': auth_password,
        }
        # Remove empty items, for instance missing client_secret
        payload = dict(
            (k, v) for k, v in temp_payload.items() if v is not None)
        try:
            r = json.loads(to_native(open_url(auth_url, method='POST',
                                              validate_certs=validate_certs, http_agent=http_agent, timeout=connection_timeout,
                                              data=urlencode(payload)).read()))
        except ValueError as e:
            raise KeycloakError(
                'API returned invalid JSON when trying to obtain access token from %s: %s'
                % (auth_url, str(e)))
        except Exception as e:
            raise KeycloakError('Could not obtain access token from %s: %s'
                                % (auth_url, str(e)))

        try:
            token = r['access_token']
        except KeyError:
            raise KeycloakError(
                'Could not obtain access token from %s' % auth_url)
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
        for item1 in struct1:
            if isinstance(item1, (list, dict)):
                for item2 in struct2:
                    if not is_struct_included(item1, item2, exclude):
                        return False
            else:
                if item1 not in struct2:
                    return False
        return True
    elif isinstance(struct1, dict) and isinstance(struct2, dict):
        try:
            for key in struct1:
                if not (exclude and key in exclude):
                    if not is_struct_included(struct1[key], struct2[key], exclude):
                        return False
            return True
        except KeyError:
            return False
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

    def get_realm_info_by_id(self, realm='master'):
        """ Obtain realm public info by id

        :param realm: realm id
        :return: dict of real, representation or None if none matching exist
        """
        realm_info_url = URL_REALM_INFO.format(url=self.baseurl, realm=realm)

        try:
            return json.loads(to_native(open_url(realm_info_url, method='GET', http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                      exception=traceback.format_exc())
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())
        except Exception as e:
            self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())

    def get_realm_by_id(self, realm='master'):
        """ Obtain realm representation by id

        :param realm: realm id
        :return: dict of real, representation or None if none matching exist
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return json.loads(to_native(open_url(realm_url, method='GET', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not obtain realm %s: %s' % (realm, str(e)),
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
            return open_url(realm_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(realmrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update realm %s: %s' % (realm, str(e)),
                                  exception=traceback.format_exc())

    def create_realm(self, realmrep):
        """ Create a realm in keycloak
        :param realmrep: Realm representation of realm to be created.
        :return: HTTPResponse object on success
        """
        realm_url = URL_REALMS.format(url=self.baseurl)

        try:
            return open_url(realm_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(realmrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create realm %s: %s' % (realmrep['id'], str(e)),
                                  exception=traceback.format_exc())

    def delete_realm(self, realm="master"):
        """ Delete a realm from Keycloak

        :param realm: realm to be deleted
        :return: HTTPResponse object on success
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return open_url(realm_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete realm %s: %s' % (realm, str(e)),
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
            return json.loads(to_native(open_url(clientlist_url, http_agent=self.http_agent, method='GET', headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of clients for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of clients for realm %s: %s'
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
            return json.loads(to_native(open_url(client_url, method='GET', http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not obtain client %s for realm %s: %s'
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
            return open_url(client_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clientrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update client %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def create_client(self, clientrep, realm="master"):
        """ Create a client in keycloak
        :param clientrep: Client representation of client to be created. Must at least contain field clientId.
        :param realm: realm for client to be created.
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENTS.format(url=self.baseurl, realm=realm)

        try:
            return open_url(client_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clientrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create client %s in realm %s: %s'
                                      % (clientrep['clientId'], realm, str(e)))

    def delete_client(self, id, realm="master"):
        """ Delete a client from Keycloak

        :param id: id (not clientId) of client to be deleted
        :param realm: realm of client to be deleted
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENT.format(url=self.baseurl, realm=realm, id=id)

        try:
            return open_url(client_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete client %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def get_client_roles_by_id(self, cid, realm="master"):
        """ Fetch the roles of the a client on the Keycloak server.

        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        client_roles_url = URL_CLIENT_ROLES.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return json.loads(to_native(open_url(client_roles_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch rolemappings for client %s in realm %s: %s"
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
            rolemappings = json.loads(to_native(open_url(rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                         timeout=self.connection_timeout,
                                                         validate_certs=self.validate_certs).read()))
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.module.fail_json(msg="Could not fetch rolemappings for client %s in group %s, realm %s: %s"
                                      % (cid, gid, realm, str(e)))
        return None

    def get_client_group_available_rolemappings(self, gid, cid, realm="master"):
        """ Fetch the available role of a client in a specified goup on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The rollemappings of specified group and client of the realm (default "master").
        """
        available_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS_AVAILABLE.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            return json.loads(to_native(open_url(available_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
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
            return json.loads(to_native(open_url(composite_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
                                      % (cid, gid, realm, str(e)))

    def get_role_by_id(self, rid, realm="master"):
        """ Fetch a role by its id on the Keycloak server.

        :param rid: ID of the role.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The role.
        """
        client_roles_url = URL_ROLES_BY_ID.format(url=self.baseurl, realm=realm, id=rid)
        try:
            return json.loads(to_native(open_url(client_roles_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch role for id %s in realm %s: %s"
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
            return json.loads(to_native(open_url(client_roles_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch role for id %s and cid %s in realm %s: %s"
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
            open_url(available_rolemappings_url, method="POST", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(roles_rep),
                     validate_certs=self.validate_certs, timeout=self.connection_timeout)
        except Exception as e:
            self.module.fail_json(msg="Could not assign roles to composite role %s and realm %s: %s"
                                      % (rid, realm, str(e)))

    def add_group_rolemapping(self, gid, cid, role_rep, realm="master"):
        """ Fetch the composite role of a client in a specified goup on the Keycloak server.

        :param gid: ID of the group from which to obtain the rolemappings.
        :param cid: ID of the client from which to obtain the rolemappings.
        :param role_rep: Representation of the role to assign.
        :param realm: Realm from which to obtain the rolemappings.
        :return: None.
        """
        available_rolemappings_url = URL_CLIENT_GROUP_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=gid, client=cid)
        try:
            open_url(available_rolemappings_url, method="POST", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                     validate_certs=self.validate_certs, timeout=self.connection_timeout)
        except Exception as e:
            self.module.fail_json(msg="Could not fetch available rolemappings for client %s in group %s, realm %s: %s"
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
            open_url(available_rolemappings_url, method="DELETE", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                     validate_certs=self.validate_certs, timeout=self.connection_timeout)
        except Exception as e:
            self.module.fail_json(msg="Could not delete available rolemappings for client %s in group %s, realm %s: %s"
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
            rolemappings = json.loads(to_native(open_url(rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                         timeout=self.connection_timeout,
                                                         validate_certs=self.validate_certs).read()))
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.module.fail_json(msg="Could not fetch rolemappings for client %s and user %s, realm %s: %s"
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
            return json.loads(to_native(open_url(available_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch effective rolemappings for client %s and user %s, realm %s: %s"
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
            return json.loads(to_native(open_url(composite_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch available rolemappings for user %s of realm %s: %s"
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
            rolemappings = json.loads(to_native(open_url(rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                         timeout=self.connection_timeout,
                                                         validate_certs=self.validate_certs).read()))
            for role in rolemappings:
                if rid == role['id']:
                    return role
        except Exception as e:
            self.module.fail_json(msg="Could not fetch rolemappings for user %s, realm %s: %s"
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
            return json.loads(to_native(open_url(available_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch available rolemappings for user %s of realm %s: %s"
                                      % (uid, realm, str(e)))

    def get_realm_user_composite_rolemappings(self, uid, realm="master"):
        """ Fetch the composite role of a realm for a specified user on the Keycloak server.

        :param uid: ID of the user from which to obtain the rolemappings.
        :param realm: Realm from which to obtain the rolemappings.
        :return: The effective rollemappings of specified client and user of the realm (default "master").
        """
        composite_rolemappings_url = URL_REALM_ROLEMAPPINGS_COMPOSITE.format(url=self.baseurl, realm=realm, id=uid)
        try:
            return json.loads(to_native(open_url(composite_rolemappings_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch effective rolemappings for user %s, realm %s: %s"
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
            return json.loads(to_native(open_url(users_url, method='GET', headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain the user for realm %s and username %s: %s'
                                      % (realm, username, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain the user for realm %s and username %s: %s'
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
            return json.loads(to_native(open_url(service_account_user_url, method='GET', headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain the service-account-user for realm %s and client_id %s: %s'
                                      % (realm, client_id, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain the service-account-user for realm %s and client_id %s: %s'
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
                open_url(user_realm_rolemappings_url, method="POST", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                         validate_certs=self.validate_certs, timeout=self.connection_timeout)
            except Exception as e:
                self.module.fail_json(msg="Could not map roles to userId %s for realm %s and roles %s: %s"
                                          % (uid, realm, json.dumps(role_rep), str(e)))
        else:
            user_client_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid, client=cid)
            try:
                open_url(user_client_rolemappings_url, method="POST", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                         validate_certs=self.validate_certs, timeout=self.connection_timeout)
            except Exception as e:
                self.module.fail_json(msg="Could not map roles to userId %s for client %s, realm %s and roles %s: %s"
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
                open_url(user_realm_rolemappings_url, method="DELETE", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                         validate_certs=self.validate_certs, timeout=self.connection_timeout)
            except Exception as e:
                self.module.fail_json(msg="Could not remove roles %s from userId %s, realm %s: %s"
                                          % (json.dumps(role_rep), uid, realm, str(e)))
        else:
            user_client_rolemappings_url = URL_CLIENT_USER_ROLEMAPPINGS.format(url=self.baseurl, realm=realm, id=uid, client=cid)
            try:
                open_url(user_client_rolemappings_url, method="DELETE", http_agent=self.http_agent, headers=self.restheaders, data=json.dumps(role_rep),
                         validate_certs=self.validate_certs, timeout=self.connection_timeout)
            except Exception as e:
                self.module.fail_json(msg="Could not remove roles %s for client %s from userId %s, realm %s: %s"
                                          % (json.dumps(role_rep), cid, uid, realm, str(e)))

    def get_client_templates(self, realm='master'):
        """ Obtains client template representations for client templates in a realm

        :param realm: realm to be queried
        :return: list of dicts of client representations
        """
        url = URL_CLIENTTEMPLATES.format(url=self.baseurl, realm=realm)

        try:
            return json.loads(to_native(open_url(url, method='GET', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of client templates for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of client templates for realm %s: %s'
                                      % (realm, str(e)))

    def get_client_template_by_id(self, id, realm='master'):
        """ Obtain client template representation by id

        :param id: id (not name) of client template to be queried
        :param realm: client template from this realm
        :return: dict of client template representation or None if none matching exist
        """
        url = URL_CLIENTTEMPLATE.format(url=self.baseurl, id=id, realm=realm)

        try:
            return json.loads(to_native(open_url(url, method='GET', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain client templates %s for realm %s: %s'
                                      % (id, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain client template %s for realm %s: %s'
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
            return open_url(url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clienttrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update client template %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def create_client_template(self, clienttrep, realm="master"):
        """ Create a client in keycloak
        :param clienttrep: Client template representation of client template to be created. Must at least contain field name
        :param realm: realm for client template to be created in
        :return: HTTPResponse object on success
        """
        url = URL_CLIENTTEMPLATES.format(url=self.baseurl, realm=realm)

        try:
            return open_url(url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clienttrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create client template %s in realm %s: %s'
                                      % (clienttrep['clientId'], realm, str(e)))

    def delete_client_template(self, id, realm="master"):
        """ Delete a client template from Keycloak

        :param id: id (not name) of client to be deleted
        :param realm: realm of client template to be deleted
        :return: HTTPResponse object on success
        """
        url = URL_CLIENTTEMPLATE.format(url=self.baseurl, realm=realm, id=id)

        try:
            return open_url(url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete client template %s in realm %s: %s'
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
            return json.loads(to_native(open_url(clientscopes_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch list of clientscopes in realm %s: %s"
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
            return json.loads(to_native(open_url(clientscope_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg="Could not fetch clientscope %s in realm %s: %s"
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
            return open_url(clientscopes_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clientscoperep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Could not create clientscope %s in realm %s: %s"
                                      % (clientscoperep['name'], realm, str(e)))

    def update_clientscope(self, clientscoperep, realm="master"):
        """ Update an existing clientscope.

        :param grouprep: A GroupRepresentation of the updated group.
        :return HTTPResponse object on success
        """
        clientscope_url = URL_CLIENTSCOPE.format(url=self.baseurl, realm=realm, id=clientscoperep['id'])

        try:
            return open_url(clientscope_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(clientscoperep), validate_certs=self.validate_certs)

        except Exception as e:
            self.module.fail_json(msg='Could not update clientscope %s in realm %s: %s'
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

        # only lookup the name if cid isn't provided.
        # in the case that both are provided, prefer the ID, since it's one
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
            return open_url(clientscope_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)

        except Exception as e:
            self.module.fail_json(msg="Unable to delete clientscope %s: %s" % (cid, str(e)))

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
            return json.loads(to_native(open_url(protocolmappers_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch list of protocolmappers in realm %s: %s"
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
            return json.loads(to_native(open_url(protocolmapper_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))

        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg="Could not fetch protocolmapper %s in realm %s: %s"
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
            return open_url(protocolmappers_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(mapper_rep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Could not create protocolmapper %s in realm %s: %s"
                                      % (mapper_rep['name'], realm, str(e)))

    def update_clientscope_protocolmappers(self, cid, mapper_rep, realm="master"):
        """ Update an existing clientscope.

        :param cid: Id of the clientscope.
        :param mapper_rep: A ProtocolMapperRepresentation of the updated protocolmapper.
        :return HTTPResponse object on success
        """
        protocolmapper_url = URL_CLIENTSCOPE_PROTOCOLMAPPER.format(url=self.baseurl, realm=realm, id=cid, mapper_id=mapper_rep['id'])

        try:
            return open_url(protocolmapper_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(mapper_rep), validate_certs=self.validate_certs)

        except Exception as e:
            self.module.fail_json(msg='Could not update protocolmappers for clientscope %s in realm %s: %s'
                                      % (mapper_rep, realm, str(e)))

    def get_groups(self, realm="master"):
        """ Fetch the name and ID of all groups on the Keycloak server.

        To fetch the full data of the group, make a subsequent call to
        get_group_by_groupid, passing in the ID of the group you wish to return.

        :param realm: Return the groups of this realm (default "master").
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            return json.loads(to_native(open_url(groups_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch list of groups in realm %s: %s"
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
            return json.loads(to_native(open_url(groups_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg="Could not fetch group %s in realm %s: %s"
                                          % (gid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg="Could not fetch group %s in realm %s: %s"
                                      % (gid, realm, str(e)))

    def get_group_by_name(self, name, realm="master"):
        """ Fetch a keycloak group within a realm based on its name.

        The Keycloak API does not allow filtering of the Groups resource by name.
        As a result, this method first retrieves the entire list of groups - name and ID -
        then performs a second query to fetch the group.

        If the group does not exist, None is returned.
        :param name: Name of the group to fetch.
        :param realm: Realm in which the group resides; default 'master'
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            all_groups = self.get_groups(realm=realm)

            for group in all_groups:
                if group['name'] == name:
                    return self.get_group_by_groupid(group['id'], realm=realm)

            return None

        except Exception as e:
            self.module.fail_json(msg="Could not fetch group %s in realm %s: %s"
                                      % (name, realm, str(e)))

    def create_group(self, grouprep, realm="master"):
        """ Create a Keycloak group.

        :param grouprep: a GroupRepresentation of the group to be created. Must contain at minimum the field name.
        :return: HTTPResponse object on success
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            return open_url(groups_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(grouprep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Could not create group %s in realm %s: %s"
                                      % (grouprep['name'], realm, str(e)))

    def update_group(self, grouprep, realm="master"):
        """ Update an existing group.

        :param grouprep: A GroupRepresentation of the updated group.
        :return HTTPResponse object on success
        """
        group_url = URL_GROUP.format(url=self.baseurl, realm=realm, groupid=grouprep['id'])

        try:
            return open_url(group_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(grouprep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update group %s in realm %s: %s'
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
        # in the case that both are provided, prefer the ID, since it's one
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
            return open_url(group_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to delete group %s: %s" % (groupid, str(e)))

    def get_realm_roles(self, realm='master'):
        """ Obtains role representations for roles in a realm

        :param realm: realm to be queried
        :return: list of dicts of role representations
        """
        rolelist_url = URL_REALM_ROLES.format(url=self.baseurl, realm=realm)
        try:
            return json.loads(to_native(open_url(rolelist_url, method='GET', http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of roles for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of roles for realm %s: %s'
                                      % (realm, str(e)))

    def get_realm_role(self, name, realm='master'):
        """ Fetch a keycloak role from the provided realm using the role's name.

        If the role does not exist, None is returned.
        :param name: Name of the role to fetch.
        :param realm: Realm in which the role resides; default 'master'.
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(name))
        try:
            return json.loads(to_native(open_url(role_url, method="GET", http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not fetch role %s in realm %s: %s'
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
            return open_url(roles_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(rolerep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create role %s in realm %s: %s'
                                      % (rolerep['name'], realm, str(e)))

    def update_realm_role(self, rolerep, realm='master'):
        """ Update an existing realm role.

        :param rolerep: A RoleRepresentation of the updated role.
        :return HTTPResponse object on success
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(rolerep['name']))
        try:
            return open_url(role_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(rolerep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update role %s in realm %s: %s'
                                      % (rolerep['name'], realm, str(e)))

    def delete_realm_role(self, name, realm='master'):
        """ Delete a realm role.

        :param name: The name of the role.
        :param realm: The realm in which this role resides, default "master".
        """
        role_url = URL_REALM_ROLE.format(url=self.baseurl, realm=realm, name=quote(name))
        try:
            return open_url(role_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete role %s in realm %s: %s'
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
            return json.loads(to_native(open_url(rolelist_url, method='GET', http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of roles for client %s in realm %s: %s'
                                      % (clientid, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of roles for client %s in realm %s: %s'
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
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(name))
        try:
            return json.loads(to_native(open_url(role_url, method="GET", http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not fetch role %s in client %s of realm %s: %s'
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
            return open_url(roles_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(rolerep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create role %s for client %s in realm %s: %s'
                                      % (rolerep['name'], clientid, realm, str(e)))

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
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(rolerep['name']))
        try:
            return open_url(role_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(rolerep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update role %s for client %s in realm %s: %s'
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
        role_url = URL_CLIENT_ROLE.format(url=self.baseurl, realm=realm, id=cid, name=quote(name))
        try:
            return open_url(role_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete role %s for client %s in realm %s: %s'
                                      % (name, clientid, realm, str(e)))

    def get_authentication_flow_by_alias(self, alias, realm='master'):
        """
        Get an authentication flow by it's alias
        :param alias: Alias of the authentication flow to get.
        :param realm: Realm.
        :return: Authentication flow representation.
        """
        try:
            authentication_flow = {}
            # Check if the authentication flow exists on the Keycloak serveraders
            authentications = json.load(open_url(URL_AUTHENTICATION_FLOWS.format(url=self.baseurl, realm=realm), method='GET',
                                                 http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout, validate_certs=self.validate_certs))
            for authentication in authentications:
                if authentication["alias"] == alias:
                    authentication_flow = authentication
                    break
            return authentication_flow
        except Exception as e:
            self.module.fail_json(msg="Unable get authentication flow %s: %s" % (alias, str(e)))

    def delete_authentication_flow_by_id(self, id, realm='master'):
        """
        Delete an authentication flow from Keycloak
        :param id: id of authentication flow to be deleted
        :param realm: realm of client to be deleted
        :return: HTTPResponse object on success
        """
        flow_url = URL_AUTHENTICATION_FLOW.format(url=self.baseurl, realm=realm, id=id)

        try:
            return open_url(flow_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete authentication flow %s in realm %s: %s'
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
            open_url(
                URL_AUTHENTICATION_FLOW_COPY.format(
                    url=self.baseurl,
                    realm=realm,
                    copyfrom=quote(config["copyFrom"])),
                method='POST',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(new_name),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
            flow_list = json.load(
                open_url(
                    URL_AUTHENTICATION_FLOWS.format(url=self.baseurl,
                                                    realm=realm),
                    method='GET',
                    http_agent=self.http_agent, headers=self.restheaders,
                    timeout=self.connection_timeout,
                    validate_certs=self.validate_certs))
            for flow in flow_list:
                if flow["alias"] == config["alias"]:
                    return flow
            return None
        except Exception as e:
            self.module.fail_json(msg='Could not copy authentication flow %s in realm %s: %s'
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
            open_url(
                URL_AUTHENTICATION_FLOWS.format(
                    url=self.baseurl,
                    realm=realm),
                method='POST',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(new_flow),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
            flow_list = json.load(
                open_url(
                    URL_AUTHENTICATION_FLOWS.format(
                        url=self.baseurl,
                        realm=realm),
                    method='GET',
                    http_agent=self.http_agent, headers=self.restheaders,
                    timeout=self.connection_timeout,
                    validate_certs=self.validate_certs))
            for flow in flow_list:
                if flow["alias"] == config["alias"]:
                    return flow
            return None
        except Exception as e:
            self.module.fail_json(msg='Could not create empty authentication flow %s in realm %s: %s'
                                  % (config["alias"], realm, str(e)))

    def update_authentication_executions(self, flowAlias, updatedExec, realm='master'):
        """ Update authentication executions

        :param flowAlias: name of the parent flow
        :param updatedExec: JSON containing updated execution
        :return: HTTPResponse object on success
        """
        try:
            open_url(
                URL_AUTHENTICATION_FLOW_EXECUTIONS.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias)),
                method='PUT',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(updatedExec),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to update executions %s: %s" % (updatedExec, str(e)))

    def add_authenticationConfig_to_execution(self, executionId, authenticationConfig, realm='master'):
        """ Add autenticatorConfig to the execution

        :param executionId: id of execution
        :param authenticationConfig: config to add to the execution
        :return: HTTPResponse object on success
        """
        try:
            open_url(
                URL_AUTHENTICATION_EXECUTION_CONFIG.format(
                    url=self.baseurl,
                    realm=realm,
                    id=executionId),
                method='POST',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(authenticationConfig),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to add authenticationConfig %s: %s" % (executionId, str(e)))

    def create_subflow(self, subflowName, flowAlias, realm='master'):
        """ Create new sublow on the flow

        :param subflowName: name of the subflow to create
        :param flowAlias: name of the parent flow
        :return: HTTPResponse object on success
        """
        try:
            newSubFlow = {}
            newSubFlow["alias"] = subflowName
            newSubFlow["provider"] = "registration-page-form"
            newSubFlow["type"] = "basic-flow"
            open_url(
                URL_AUTHENTICATION_FLOW_EXECUTIONS_FLOW.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias)),
                method='POST',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(newSubFlow),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to create new subflow %s: %s" % (subflowName, str(e)))

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
            open_url(
                URL_AUTHENTICATION_FLOW_EXECUTIONS_EXECUTION.format(
                    url=self.baseurl,
                    realm=realm,
                    flowalias=quote(flowAlias)),
                method='POST',
                http_agent=self.http_agent, headers=self.restheaders,
                data=json.dumps(newExec),
                timeout=self.connection_timeout,
                validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to create new execution %s: %s" % (execution["provider"], str(e)))

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
                    open_url(
                        URL_AUTHENTICATION_EXECUTION_RAISE_PRIORITY.format(
                            url=self.baseurl,
                            realm=realm,
                            id=executionId),
                        method='POST',
                        http_agent=self.http_agent, headers=self.restheaders,
                        timeout=self.connection_timeout,
                        validate_certs=self.validate_certs)
            elif diff < 0:
                for i in range(-diff):
                    open_url(
                        URL_AUTHENTICATION_EXECUTION_LOWER_PRIORITY.format(
                            url=self.baseurl,
                            realm=realm,
                            id=executionId),
                        method='POST',
                        http_agent=self.http_agent, headers=self.restheaders,
                        timeout=self.connection_timeout,
                        validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg="Unable to change execution priority %s: %s" % (executionId, str(e)))

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
                open_url(
                    URL_AUTHENTICATION_FLOW_EXECUTIONS.format(
                        url=self.baseurl,
                        realm=realm,
                        flowalias=quote(config["alias"])),
                    method='GET',
                    http_agent=self.http_agent, headers=self.restheaders,
                    timeout=self.connection_timeout,
                    validate_certs=self.validate_certs))
            for execution in executions:
                if "authenticationConfig" in execution:
                    execConfigId = execution["authenticationConfig"]
                    execConfig = json.load(
                        open_url(
                            URL_AUTHENTICATION_CONFIG.format(
                                url=self.baseurl,
                                realm=realm,
                                id=execConfigId),
                            method='GET',
                            http_agent=self.http_agent, headers=self.restheaders,
                            timeout=self.connection_timeout,
                            validate_certs=self.validate_certs))
                    execution["authenticationConfig"] = execConfig
            return executions
        except Exception as e:
            self.module.fail_json(msg='Could not get executions for authentication flow %s in realm %s: %s'
                                  % (config["alias"], realm, str(e)))

    def get_identity_providers(self, realm='master'):
        """ Fetch representations for identity providers in a realm
        :param realm: realm to be queried
        :return: list of representations for identity providers
        """
        idps_url = URL_IDENTITY_PROVIDERS.format(url=self.baseurl, realm=realm)
        try:
            return json.loads(to_native(open_url(idps_url, method='GET', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of identity providers for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of identity providers for realm %s: %s'
                                      % (realm, str(e)))

    def get_identity_provider(self, alias, realm='master'):
        """ Fetch identity provider representation from a realm using the idp's alias.
        If the identity provider does not exist, None is returned.
        :param alias: Alias of the identity provider to fetch.
        :param realm: Realm in which the identity provider resides; default 'master'.
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return json.loads(to_native(open_url(idp_url, method="GET", http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not fetch identity provider %s in realm %s: %s'
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
            return open_url(idps_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(idprep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create identity provider %s in realm %s: %s'
                                      % (idprep['alias'], realm, str(e)))

    def update_identity_provider(self, idprep, realm='master'):
        """ Update an existing identity provider.
        :param idprep: Identity provider representation of the idp to be updated.
        :param realm: Realm in which this identity provider resides, default "master".
        :return HTTPResponse object on success
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=idprep['alias'])
        try:
            return open_url(idp_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(idprep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update identity provider %s in realm %s: %s'
                                      % (idprep['alias'], realm, str(e)))

    def delete_identity_provider(self, alias, realm='master'):
        """ Delete an identity provider.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        """
        idp_url = URL_IDENTITY_PROVIDER.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return open_url(idp_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete identity provider %s in realm %s: %s'
                                      % (alias, realm, str(e)))

    def get_identity_provider_mappers(self, alias, realm='master'):
        """ Fetch representations for identity provider mappers
        :param alias: Alias of the identity provider.
        :param realm: realm to be queried
        :return: list of representations for identity provider mappers
        """
        mappers_url = URL_IDENTITY_PROVIDER_MAPPERS.format(url=self.baseurl, realm=realm, alias=alias)
        try:
            return json.loads(to_native(open_url(mappers_url, method='GET', http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of identity provider mappers for idp %s in realm %s: %s'
                                      % (alias, realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of identity provider mappers for idp %s in realm %s: %s'
                                      % (alias, realm, str(e)))

    def get_identity_provider_mapper(self, mid, alias, realm='master'):
        """ Fetch identity provider representation from a realm using the idp's alias.
        If the identity provider does not exist, None is returned.
        :param mid: Unique ID of the mapper to fetch.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which the identity provider resides; default 'master'.
        """
        mapper_url = URL_IDENTITY_PROVIDER_MAPPER.format(url=self.baseurl, realm=realm, alias=alias, id=mid)
        try:
            return json.loads(to_native(open_url(mapper_url, method="GET", http_agent=self.http_agent, headers=self.restheaders,
                                                 timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not fetch mapper %s for identity provider %s in realm %s: %s'
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
            return open_url(mappers_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(mapper), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not create identity provider mapper %s for idp %s in realm %s: %s'
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
            return open_url(mapper_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(mapper), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update mapper %s for identity provider %s in realm %s: %s'
                                      % (mapper['id'], alias, realm, str(e)))

    def delete_identity_provider_mapper(self, mid, alias, realm='master'):
        """ Delete an identity provider.
        :param mid: Unique ID of the mapper to delete.
        :param alias: Alias of the identity provider.
        :param realm: Realm in which this identity provider resides, default "master".
        """
        mapper_url = URL_IDENTITY_PROVIDER_MAPPER.format(url=self.baseurl, realm=realm, alias=alias, id=mid)
        try:
            return open_url(mapper_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete mapper %s for identity provider %s in realm %s: %s'
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
            return json.loads(to_native(open_url(comps_url, method='GET', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except ValueError as e:
            self.module.fail_json(msg='API returned incorrect JSON when trying to obtain list of components for realm %s: %s'
                                      % (realm, str(e)))
        except Exception as e:
            self.module.fail_json(msg='Could not obtain list of components for realm %s: %s'
                                      % (realm, str(e)))

    def get_component(self, cid, realm='master'):
        """ Fetch component representation from a realm using its cid.
        If the component does not exist, None is returned.
        :param cid: Unique ID of the component to fetch.
        :param realm: Realm in which the component resides; default 'master'.
        """
        comp_url = URL_COMPONENT.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return json.loads(to_native(open_url(comp_url, method="GET", http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except HTTPError as e:
            if e.code == 404:
                return None
            else:
                self.module.fail_json(msg='Could not fetch component %s in realm %s: %s'
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
            resp = open_url(comps_url, method='POST', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(comprep), validate_certs=self.validate_certs)
            comp_url = resp.getheader('Location')
            if comp_url is None:
                self.module.fail_json(msg='Could not create component in realm %s: %s'
                                          % (realm, 'unexpected response'))
            return json.loads(to_native(open_url(comp_url, method="GET", http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                                                 validate_certs=self.validate_certs).read()))
        except Exception as e:
            self.module.fail_json(msg='Could not create component in realm %s: %s'
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
            return open_url(comp_url, method='PUT', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            data=json.dumps(comprep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update component %s in realm %s: %s'
                                      % (cid, realm, str(e)))

    def delete_component(self, cid, realm='master'):
        """ Delete an component.
        :param cid: Unique ID of the component.
        :param realm: Realm in which this component resides, default "master".
        """
        comp_url = URL_COMPONENT.format(url=self.baseurl, realm=realm, id=cid)
        try:
            return open_url(comp_url, method='DELETE', http_agent=self.http_agent, headers=self.restheaders, timeout=self.connection_timeout,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete component %s in realm %s: %s'
                                      % (cid, realm, str(e)))

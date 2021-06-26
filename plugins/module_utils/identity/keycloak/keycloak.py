# Copyright (c) 2017, Eike Frost <ei@kefro.st>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import traceback

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.common.text.converters import to_native, to_text

URL_REALMS = "{url}/admin/realms"
URL_REALM = "{url}/admin/realms/{realm}"

URL_TOKEN = "{url}/realms/{realm}/protocol/openid-connect/token"
URL_CLIENT = "{url}/admin/realms/{realm}/clients/{id}"
URL_CLIENTS = "{url}/admin/realms/{realm}/clients"
URL_CLIENT_ROLES = "{url}/admin/realms/{realm}/clients/{id}/roles"
URL_REALM_ROLES = "{url}/admin/realms/{realm}/roles"

URL_CLIENTTEMPLATE = "{url}/admin/realms/{realm}/client-templates/{id}"
URL_CLIENTTEMPLATES = "{url}/admin/realms/{realm}/client-templates"
URL_GROUPS = "{url}/admin/realms/{realm}/groups"
URL_GROUP = "{url}/admin/realms/{realm}/groups/{groupid}"

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
        token=dict(type='str', no_log=True),
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
                                              validate_certs=validate_certs,
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
        self.restheaders = connection_header

    def get_realm_by_id(self, realm='master'):
        """ Obtain realm representation by id

        :param realm: realm id
        :return: dict of real, representation or None if none matching exist
        """
        realm_url = URL_REALM.format(url=self.baseurl, realm=realm)

        try:
            return json.loads(to_native(open_url(realm_url, method='GET', headers=self.restheaders,
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
            return open_url(realm_url, method='PUT', headers=self.restheaders,
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
            return open_url(realm_url, method='POST', headers=self.restheaders,
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
            return open_url(realm_url, method='DELETE', headers=self.restheaders,
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
            return json.loads(to_native(open_url(clientlist_url, method='GET', headers=self.restheaders,
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
            return json.loads(to_native(open_url(client_url, method='GET', headers=self.restheaders,
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
            return open_url(client_url, method='PUT', headers=self.restheaders,
                            data=json.dumps(clientrep), validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not update client %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def create_client(self, clientrep, realm="master"):
        """ Create a client in keycloak
        :param clientrep: Client representation of client to be created. Must at least contain field clientId
        :param realm: realm for client to be created
        :return: HTTPResponse object on success
        """
        client_url = URL_CLIENTS.format(url=self.baseurl, realm=realm)

        try:
            return open_url(client_url, method='POST', headers=self.restheaders,
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
            return open_url(client_url, method='DELETE', headers=self.restheaders,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete client %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def get_client_templates(self, realm='master'):
        """ Obtains client template representations for client templates in a realm

        :param realm: realm to be queried
        :return: list of dicts of client representations
        """
        url = URL_CLIENTTEMPLATES.format(url=self.baseurl, realm=realm)

        try:
            return json.loads(to_native(open_url(url, method='GET', headers=self.restheaders,
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
            return json.loads(to_native(open_url(url, method='GET', headers=self.restheaders,
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
            return open_url(url, method='PUT', headers=self.restheaders,
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
            return open_url(url, method='POST', headers=self.restheaders,
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
            return open_url(url, method='DELETE', headers=self.restheaders,
                            validate_certs=self.validate_certs)
        except Exception as e:
            self.module.fail_json(msg='Could not delete client template %s in realm %s: %s'
                                      % (id, realm, str(e)))

    def get_groups(self, realm="master"):
        """ Fetch the name and ID of all groups on the Keycloak server.

        To fetch the full data of the group, make a subsequent call to
        get_group_by_groupid, passing in the ID of the group you wish to return.

        :param realm: Return the groups of this realm (default "master").
        """
        groups_url = URL_GROUPS.format(url=self.baseurl, realm=realm)
        try:
            return json.loads(to_native(open_url(groups_url, method="GET", headers=self.restheaders,
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
            return json.loads(to_native(open_url(groups_url, method="GET", headers=self.restheaders,
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
            return open_url(groups_url, method='POST', headers=self.restheaders,
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
            return open_url(group_url, method='PUT', headers=self.restheaders,
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
            return open_url(group_url, method='DELETE', headers=self.restheaders,
                            validate_certs=self.validate_certs)

        except Exception as e:
            self.module.fail_json(msg="Unable to delete group %s: %s" % (groupid, str(e)))

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
            authentications = json.load(open_url(URL_AUTHENTICATION_FLOWS.format(url=self.baseurl, realm=realm), method='GET', headers=self.restheaders))
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
            return open_url(flow_url, method='DELETE', headers=self.restheaders,
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
                headers=self.restheaders,
                data=json.dumps(new_name))
            flow_list = json.load(
                open_url(
                    URL_AUTHENTICATION_FLOWS.format(url=self.baseurl,
                                                    realm=realm),
                    method='GET',
                    headers=self.restheaders))
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
                headers=self.restheaders,
                data=json.dumps(new_flow))
            flow_list = json.load(
                open_url(
                    URL_AUTHENTICATION_FLOWS.format(
                        url=self.baseurl,
                        realm=realm),
                    method='GET',
                    headers=self.restheaders))
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
                headers=self.restheaders,
                data=json.dumps(updatedExec))
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
                headers=self.restheaders,
                data=json.dumps(authenticationConfig))
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
                headers=self.restheaders,
                data=json.dumps(newSubFlow))
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
                headers=self.restheaders,
                data=json.dumps(newExec))
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
                        headers=self.restheaders)
            elif diff < 0:
                for i in range(-diff):
                    open_url(
                        URL_AUTHENTICATION_EXECUTION_LOWER_PRIORITY.format(
                            url=self.baseurl,
                            realm=realm,
                            id=executionId),
                        method='POST',
                        headers=self.restheaders)
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
                    headers=self.restheaders))
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
                            headers=self.restheaders))
                    execution["authenticationConfig"] = execConfig
            return executions
        except Exception as e:
            self.module.fail_json(msg='Could not get executions for authentication flow %s in realm %s: %s'
                                  % (config["alias"], realm, str(e)))

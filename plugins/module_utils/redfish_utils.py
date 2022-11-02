# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from ansible.module_utils.urls import open_url
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.six.moves import http_client
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlparse

GET_HEADERS = {'accept': 'application/json', 'OData-Version': '4.0'}
POST_HEADERS = {'content-type': 'application/json', 'accept': 'application/json',
                'OData-Version': '4.0'}
PATCH_HEADERS = {'content-type': 'application/json', 'accept': 'application/json',
                 'OData-Version': '4.0'}
DELETE_HEADERS = {'accept': 'application/json', 'OData-Version': '4.0'}

FAIL_MSG = 'Issuing a data modification command without specifying the '\
           'ID of the target %(resource)s resource when there is more '\
           'than one %(resource)s is no longer allowed. Use the `resource_id` '\
           'option to specify the target %(resource)s ID.'


class RedfishUtils(object):

    def __init__(self, creds, root_uri, timeout, module, resource_id=None,
                 data_modification=False, strip_etag_quotes=False):
        self.root_uri = root_uri
        self.creds = creds
        self.timeout = timeout
        self.module = module
        self.service_root = '/redfish/v1/'
        self.resource_id = resource_id
        self.data_modification = data_modification
        self.strip_etag_quotes = strip_etag_quotes
        self._vendor = None
        self._init_session()

    def _auth_params(self, headers):
        """
        Return tuple of required authentication params based on the presence
        of a token in the self.creds dict. If using a token, set the
        X-Auth-Token header in the `headers` param.

        :param headers: dict containing headers to send in request
        :return: tuple of username, password and force_basic_auth
        """
        if self.creds.get('token'):
            username = None
            password = None
            force_basic_auth = False
            headers['X-Auth-Token'] = self.creds['token']
        else:
            username = self.creds['user']
            password = self.creds['pswd']
            force_basic_auth = True
        return username, password, force_basic_auth

    def _check_request_payload(self, req_pyld, cur_pyld, uri):
        """
        Checks the request payload with the values currently held by the
        service. Will check if changes are needed and if properties are
        supported by the service.

        :param req_pyld: dict containing the properties to apply
        :param cur_pyld: dict containing the properties currently set
        :param uri: string containing the URI being modified
        :return: dict containing response information
        """

        change_required = False
        for prop in req_pyld:
            # Check if the property is supported by the service
            if prop not in cur_pyld:
                return {'ret': False,
                        'changed': False,
                        'msg': '%s does not support the property %s' % (uri, prop),
                        'changes_required': False}

            # Perform additional checks based on the type of property
            if isinstance(req_pyld[prop], dict) and isinstance(cur_pyld[prop], dict):
                # If the property is a dictionary, check the nested properties
                sub_resp = self._check_request_payload(req_pyld[prop], cur_pyld[prop], uri)
                if not sub_resp['ret']:
                    # Unsupported property or other error condition; no change
                    return sub_resp
                if sub_resp['changes_required']:
                    # Subordinate dictionary requires changes
                    change_required = True

            else:
                # For other properties, just compare the values

                # Note: This is also a fallthrough for cases where the request
                # payload and current settings do not match in their data type.
                # There are cases where this can be expected, such as when a
                # property is always 'null' in responses, so we want to attempt
                # the PATCH request.

                # Note: This is also a fallthrough for properties that are
                # arrays of objects.  Some services erroneously omit properties
                # within arrays of objects when not configured, and it's
                # expecting the client to provide them anyway.

                if req_pyld[prop] != cur_pyld[prop]:
                    change_required = True

        resp = {'ret': True, 'changes_required': change_required}
        if not change_required:
            # No changes required; all properties set
            resp['changed'] = False
            resp['msg'] = 'Properties in %s are already set' % uri
        return resp

    # The following functions are to send GET/POST/PATCH/DELETE requests
    def get_request(self, uri):
        req_headers = dict(GET_HEADERS)
        username, password, basic_auth = self._auth_params(req_headers)
        try:
            resp = open_url(uri, method="GET", headers=req_headers,
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
            data = json.loads(to_native(resp.read()))
            headers = dict((k.lower(), v) for (k, v) in resp.info().items())
        except HTTPError as e:
            msg = self._get_extended_message(e)
            return {'ret': False,
                    'msg': "HTTP Error %s on GET request to '%s', extended message: '%s'"
                           % (e.code, uri, msg),
                    'status': e.code}
        except URLError as e:
            return {'ret': False, 'msg': "URL Error on GET request to '%s': '%s'"
                                         % (uri, e.reason)}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {'ret': False,
                    'msg': "Failed GET request to '%s': '%s'" % (uri, to_text(e))}
        return {'ret': True, 'data': data, 'headers': headers}

    def post_request(self, uri, pyld):
        req_headers = dict(POST_HEADERS)
        username, password, basic_auth = self._auth_params(req_headers)
        try:
            resp = open_url(uri, data=json.dumps(pyld),
                            headers=req_headers, method="POST",
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
            headers = dict((k.lower(), v) for (k, v) in resp.info().items())
        except HTTPError as e:
            msg = self._get_extended_message(e)
            return {'ret': False,
                    'msg': "HTTP Error %s on POST request to '%s', extended message: '%s'"
                           % (e.code, uri, msg),
                    'status': e.code}
        except URLError as e:
            return {'ret': False, 'msg': "URL Error on POST request to '%s': '%s'"
                                         % (uri, e.reason)}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {'ret': False,
                    'msg': "Failed POST request to '%s': '%s'" % (uri, to_text(e))}
        return {'ret': True, 'headers': headers, 'resp': resp}

    def patch_request(self, uri, pyld, check_pyld=False):
        req_headers = dict(PATCH_HEADERS)
        r = self.get_request(uri)
        if r['ret']:
            # Get etag from etag header or @odata.etag property
            etag = r['headers'].get('etag')
            if not etag:
                etag = r['data'].get('@odata.etag')
            if etag:
                if self.strip_etag_quotes:
                    etag = etag.strip('"')
                req_headers['If-Match'] = etag

        if check_pyld:
            # Check the payload with the current settings to see if changes
            # are needed or if there are unsupported properties
            if r['ret']:
                check_resp = self._check_request_payload(pyld, r['data'], uri)
                if not check_resp.pop('changes_required'):
                    check_resp['changed'] = False
                    return check_resp
            else:
                r['changed'] = False
                return r

        username, password, basic_auth = self._auth_params(req_headers)
        try:
            resp = open_url(uri, data=json.dumps(pyld),
                            headers=req_headers, method="PATCH",
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
        except HTTPError as e:
            msg = self._get_extended_message(e)
            return {'ret': False, 'changed': False,
                    'msg': "HTTP Error %s on PATCH request to '%s', extended message: '%s'"
                           % (e.code, uri, msg),
                    'status': e.code}
        except URLError as e:
            return {'ret': False, 'changed': False,
                    'msg': "URL Error on PATCH request to '%s': '%s'" % (uri, e.reason)}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {'ret': False, 'changed': False,
                    'msg': "Failed PATCH request to '%s': '%s'" % (uri, to_text(e))}
        return {'ret': True, 'changed': True, 'resp': resp, 'msg': 'Modified %s' % uri}

    def delete_request(self, uri, pyld=None):
        req_headers = dict(DELETE_HEADERS)
        username, password, basic_auth = self._auth_params(req_headers)
        try:
            data = json.dumps(pyld) if pyld else None
            resp = open_url(uri, data=data,
                            headers=req_headers, method="DELETE",
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
        except HTTPError as e:
            msg = self._get_extended_message(e)
            return {'ret': False,
                    'msg': "HTTP Error %s on DELETE request to '%s', extended message: '%s'"
                           % (e.code, uri, msg),
                    'status': e.code}
        except URLError as e:
            return {'ret': False, 'msg': "URL Error on DELETE request to '%s': '%s'"
                                         % (uri, e.reason)}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {'ret': False,
                    'msg': "Failed DELETE request to '%s': '%s'" % (uri, to_text(e))}
        return {'ret': True, 'resp': resp}

    @staticmethod
    def _get_extended_message(error):
        """
        Get Redfish ExtendedInfo message from response payload if present
        :param error: an HTTPError exception
        :type error: HTTPError
        :return: the ExtendedInfo message if present, else standard HTTP error
        """
        msg = http_client.responses.get(error.code, '')
        if error.code >= 400:
            try:
                body = error.read().decode('utf-8')
                data = json.loads(body)
                ext_info = data['error']['@Message.ExtendedInfo']
                # if the ExtendedInfo contains a user friendly message send it
                # otherwise try to send the entire contents of ExtendedInfo
                try:
                    msg = ext_info[0]['Message']
                except Exception:
                    msg = str(data['error']['@Message.ExtendedInfo'])
            except Exception:
                pass
        return msg

    def _init_session(self):
        pass

    def _get_vendor(self):
        # If we got the vendor info once, don't get it again
        if self._vendor is not None:
            return {'ret': 'True', 'Vendor': self._vendor}

        # Find the vendor info from the service root
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return {'ret': False, 'Vendor': ''}
        data = response['data']

        if 'Vendor' in data:
            # Extract the vendor string from the Vendor property
            self._vendor = data["Vendor"]
            return {'ret': True, 'Vendor': data["Vendor"]}
        elif 'Oem' in data and len(data['Oem']) > 0:
            # Determine the vendor from the OEM object if needed
            vendor = list(data['Oem'].keys())[0]
            if vendor == 'Hpe' or vendor == 'Hp':
                # HPE uses Pascal-casing for their OEM object
                # Older systems reported 'Hp' (pre-split)
                vendor = 'HPE'
            self._vendor = vendor
            return {'ret': True, 'Vendor': vendor}
        else:
            # Could not determine; use an empty string
            self._vendor = ''
            return {'ret': True, 'Vendor': ''}

    def _find_accountservice_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'AccountService' not in data:
            return {'ret': False, 'msg': "AccountService resource not found"}
        else:
            account_service = data["AccountService"]["@odata.id"]
            response = self.get_request(self.root_uri + account_service)
            if response['ret'] is False:
                return response
            data = response['data']
            accounts = data['Accounts']['@odata.id']
            if accounts[-1:] == '/':
                accounts = accounts[:-1]
            self.accounts_uri = accounts
        return {'ret': True}

    def _find_sessionservice_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'SessionService' not in data:
            return {'ret': False, 'msg': "SessionService resource not found"}
        else:
            session_service = data["SessionService"]["@odata.id"]
            self.session_service_uri = session_service
            response = self.get_request(self.root_uri + session_service)
            if response['ret'] is False:
                return response
            data = response['data']
            sessions = data['Sessions']['@odata.id']
            if sessions[-1:] == '/':
                sessions = sessions[:-1]
            self.sessions_uri = sessions
        return {'ret': True}

    def _get_resource_uri_by_id(self, uris, id_prop):
        for uri in uris:
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                continue
            data = response['data']
            if id_prop == data.get('Id'):
                return uri
        return None

    def _find_systems_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'Systems' not in data:
            return {'ret': False, 'msg': "Systems resource not found"}
        response = self.get_request(self.root_uri + data['Systems']['@odata.id'])
        if response['ret'] is False:
            return response
        self.systems_uris = [
            i['@odata.id'] for i in response['data'].get('Members', [])]
        if not self.systems_uris:
            return {
                'ret': False,
                'msg': "ComputerSystem's Members array is either empty or missing"}
        self.systems_uri = self.systems_uris[0]
        if self.data_modification:
            if self.resource_id:
                self.systems_uri = self._get_resource_uri_by_id(self.systems_uris,
                                                                self.resource_id)
                if not self.systems_uri:
                    return {
                        'ret': False,
                        'msg': "System resource %s not found" % self.resource_id}
            elif len(self.systems_uris) > 1:
                self.module.fail_json(msg=FAIL_MSG % {'resource': 'System'})
        return {'ret': True}

    def _find_updateservice_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'UpdateService' not in data:
            return {'ret': False, 'msg': "UpdateService resource not found"}
        else:
            update = data["UpdateService"]["@odata.id"]
            self.update_uri = update
            response = self.get_request(self.root_uri + update)
            if response['ret'] is False:
                return response
            data = response['data']
            self.firmware_uri = self.software_uri = None
            if 'FirmwareInventory' in data:
                self.firmware_uri = data['FirmwareInventory'][u'@odata.id']
            if 'SoftwareInventory' in data:
                self.software_uri = data['SoftwareInventory'][u'@odata.id']
            return {'ret': True}

    def _find_chassis_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'Chassis' not in data:
            return {'ret': False, 'msg': "Chassis resource not found"}
        chassis = data["Chassis"]["@odata.id"]
        response = self.get_request(self.root_uri + chassis)
        if response['ret'] is False:
            return response
        self.chassis_uris = [
            i['@odata.id'] for i in response['data'].get('Members', [])]
        if not self.chassis_uris:
            return {'ret': False,
                    'msg': "Chassis Members array is either empty or missing"}
        self.chassis_uri = self.chassis_uris[0]
        if self.data_modification:
            if self.resource_id:
                self.chassis_uri = self._get_resource_uri_by_id(self.chassis_uris,
                                                                self.resource_id)
                if not self.chassis_uri:
                    return {
                        'ret': False,
                        'msg': "Chassis resource %s not found" % self.resource_id}
            elif len(self.chassis_uris) > 1:
                self.module.fail_json(msg=FAIL_MSG % {'resource': 'Chassis'})
        return {'ret': True}

    def _find_managers_resource(self):
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'Managers' not in data:
            return {'ret': False, 'msg': "Manager resource not found"}
        manager = data["Managers"]["@odata.id"]
        response = self.get_request(self.root_uri + manager)
        if response['ret'] is False:
            return response
        self.manager_uris = [
            i['@odata.id'] for i in response['data'].get('Members', [])]
        if not self.manager_uris:
            return {'ret': False,
                    'msg': "Managers Members array is either empty or missing"}
        self.manager_uri = self.manager_uris[0]
        if self.data_modification:
            if self.resource_id:
                self.manager_uri = self._get_resource_uri_by_id(self.manager_uris,
                                                                self.resource_id)
                if not self.manager_uri:
                    return {
                        'ret': False,
                        'msg': "Manager resource %s not found" % self.resource_id}
            elif len(self.manager_uris) > 1:
                self.module.fail_json(msg=FAIL_MSG % {'resource': 'Manager'})
        return {'ret': True}

    def _get_all_action_info_values(self, action):
        """Retrieve all parameter values for an Action from ActionInfo.
        Fall back to AllowableValue annotations if no ActionInfo found.
        Return the result in an ActionInfo-like dictionary, keyed
        by the name of the parameter. """
        ai = {}
        if '@Redfish.ActionInfo' in action:
            ai_uri = action['@Redfish.ActionInfo']
            response = self.get_request(self.root_uri + ai_uri)
            if response['ret'] is True:
                data = response['data']
                if 'Parameters' in data:
                    params = data['Parameters']
                    ai = dict((p['Name'], p)
                              for p in params if 'Name' in p)
        if not ai:
            ai = dict((k[:-24],
                       {'AllowableValues': v}) for k, v in action.items()
                      if k.endswith('@Redfish.AllowableValues'))
        return ai

    def _get_allowable_values(self, action, name, default_values=None):
        if default_values is None:
            default_values = []
        ai = self._get_all_action_info_values(action)
        allowable_values = ai.get(name, {}).get('AllowableValues')
        # fallback to default values
        if allowable_values is None:
            allowable_values = default_values
        return allowable_values

    def get_logs(self):
        log_svcs_uri_list = []
        list_of_logs = []
        properties = ['Severity', 'Created', 'EntryType', 'OemRecordFormat',
                      'Message', 'MessageId', 'MessageArgs']

        # Find LogService
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'LogServices' not in data:
            return {'ret': False, 'msg': "LogServices resource not found"}

        # Find all entries in LogServices
        logs_uri = data["LogServices"]["@odata.id"]
        response = self.get_request(self.root_uri + logs_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        for log_svcs_entry in data.get('Members', []):
            response = self.get_request(self.root_uri + log_svcs_entry[u'@odata.id'])
            if response['ret'] is False:
                return response
            _data = response['data']
            if 'Entries' in _data:
                log_svcs_uri_list.append(_data['Entries'][u'@odata.id'])

        # For each entry in LogServices, get log name and all log entries
        for log_svcs_uri in log_svcs_uri_list:
            logs = {}
            list_of_log_entries = []
            response = self.get_request(self.root_uri + log_svcs_uri)
            if response['ret'] is False:
                return response
            data = response['data']
            logs['Description'] = data.get('Description',
                                           'Collection of log entries')
            # Get all log entries for each type of log found
            for logEntry in data.get('Members', []):
                entry = {}
                for prop in properties:
                    if prop in logEntry:
                        entry[prop] = logEntry.get(prop)
                if entry:
                    list_of_log_entries.append(entry)
            log_name = log_svcs_uri.split('/')[-1]
            logs[log_name] = list_of_log_entries
            list_of_logs.append(logs)

        # list_of_logs[logs{list_of_log_entries[entry{}]}]
        return {'ret': True, 'entries': list_of_logs}

    def clear_logs(self):
        # Find LogService
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'LogServices' not in data:
            return {'ret': False, 'msg': "LogServices resource not found"}

        # Find all entries in LogServices
        logs_uri = data["LogServices"]["@odata.id"]
        response = self.get_request(self.root_uri + logs_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        for log_svcs_entry in data[u'Members']:
            response = self.get_request(self.root_uri + log_svcs_entry["@odata.id"])
            if response['ret'] is False:
                return response
            _data = response['data']
            # Check to make sure option is available, otherwise error is ugly
            if "Actions" in _data:
                if "#LogService.ClearLog" in _data[u"Actions"]:
                    self.post_request(self.root_uri + _data[u"Actions"]["#LogService.ClearLog"]["target"], {})
                    if response['ret'] is False:
                        return response
        return {'ret': True}

    def aggregate(self, func, uri_list, uri_name):
        ret = True
        entries = []
        for uri in uri_list:
            inventory = func(uri)
            ret = inventory.pop('ret') and ret
            if 'entries' in inventory:
                entries.append(({uri_name: uri},
                                inventory['entries']))
        return dict(ret=ret, entries=entries)

    def aggregate_chassis(self, func):
        return self.aggregate(func, self.chassis_uris, 'chassis_uri')

    def aggregate_managers(self, func):
        return self.aggregate(func, self.manager_uris, 'manager_uri')

    def aggregate_systems(self, func):
        return self.aggregate(func, self.systems_uris, 'system_uri')

    def get_storage_controller_inventory(self, systems_uri):
        result = {}
        controller_list = []
        controller_results = []
        # Get these entries, but does not fail if not found
        properties = ['CacheSummary', 'FirmwareVersion', 'Identifiers',
                      'Location', 'Manufacturer', 'Model', 'Name', 'Id',
                      'PartNumber', 'SerialNumber', 'SpeedGbps', 'Status']
        key = "StorageControllers"

        # Find Storage service
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        if 'Storage' not in data:
            return {'ret': False, 'msg': "Storage resource not found"}

        # Get a list of all storage controllers and build respective URIs
        storage_uri = data['Storage']["@odata.id"]
        response = self.get_request(self.root_uri + storage_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        # Loop through Members and their StorageControllers
        # and gather properties from each StorageController
        if data[u'Members']:
            for storage_member in data[u'Members']:
                storage_member_uri = storage_member[u'@odata.id']
                response = self.get_request(self.root_uri + storage_member_uri)
                data = response['data']

                if key in data:
                    controller_list = data[key]
                    for controller in controller_list:
                        controller_result = {}
                        for property in properties:
                            if property in controller:
                                controller_result[property] = controller[property]
                        controller_results.append(controller_result)
                result['entries'] = controller_results
            return result
        else:
            return {'ret': False, 'msg': "Storage resource not found"}

    def get_multi_storage_controller_inventory(self):
        return self.aggregate_systems(self.get_storage_controller_inventory)

    def get_disk_inventory(self, systems_uri):
        result = {'entries': []}
        controller_list = []
        # Get these entries, but does not fail if not found
        properties = ['BlockSizeBytes', 'CapableSpeedGbs', 'CapacityBytes',
                      'EncryptionAbility', 'EncryptionStatus',
                      'FailurePredicted', 'HotspareType', 'Id', 'Identifiers',
                      'Manufacturer', 'MediaType', 'Model', 'Name',
                      'PartNumber', 'PhysicalLocation', 'Protocol', 'Revision',
                      'RotationSpeedRPM', 'SerialNumber', 'Status']

        # Find Storage service
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        if 'SimpleStorage' not in data and 'Storage' not in data:
            return {'ret': False, 'msg': "SimpleStorage and Storage resource \
                     not found"}

        if 'Storage' in data:
            # Get a list of all storage controllers and build respective URIs
            storage_uri = data[u'Storage'][u'@odata.id']
            response = self.get_request(self.root_uri + storage_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']

            if data[u'Members']:
                for controller in data[u'Members']:
                    controller_list.append(controller[u'@odata.id'])
                for c in controller_list:
                    uri = self.root_uri + c
                    response = self.get_request(uri)
                    if response['ret'] is False:
                        return response
                    data = response['data']
                    controller_name = 'Controller 1'
                    if 'StorageControllers' in data:
                        sc = data['StorageControllers']
                        if sc:
                            if 'Name' in sc[0]:
                                controller_name = sc[0]['Name']
                            else:
                                sc_id = sc[0].get('Id', '1')
                                controller_name = 'Controller %s' % sc_id
                    drive_results = []
                    if 'Drives' in data:
                        for device in data[u'Drives']:
                            disk_uri = self.root_uri + device[u'@odata.id']
                            response = self.get_request(disk_uri)
                            data = response['data']

                            drive_result = {}
                            for property in properties:
                                if property in data:
                                    if data[property] is not None:
                                        drive_result[property] = data[property]
                            drive_results.append(drive_result)
                    drives = {'Controller': controller_name,
                              'Drives': drive_results}
                    result["entries"].append(drives)

        if 'SimpleStorage' in data:
            # Get a list of all storage controllers and build respective URIs
            storage_uri = data["SimpleStorage"]["@odata.id"]
            response = self.get_request(self.root_uri + storage_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']

            for controller in data[u'Members']:
                controller_list.append(controller[u'@odata.id'])

            for c in controller_list:
                uri = self.root_uri + c
                response = self.get_request(uri)
                if response['ret'] is False:
                    return response
                data = response['data']
                if 'Name' in data:
                    controller_name = data['Name']
                else:
                    sc_id = data.get('Id', '1')
                    controller_name = 'Controller %s' % sc_id
                drive_results = []
                for device in data[u'Devices']:
                    drive_result = {}
                    for property in properties:
                        if property in device:
                            drive_result[property] = device[property]
                    drive_results.append(drive_result)
                drives = {'Controller': controller_name,
                          'Drives': drive_results}
                result["entries"].append(drives)

        return result

    def get_multi_disk_inventory(self):
        return self.aggregate_systems(self.get_disk_inventory)

    def get_volume_inventory(self, systems_uri):
        result = {'entries': []}
        controller_list = []
        volume_list = []
        # Get these entries, but does not fail if not found
        properties = ['Id', 'Name', 'RAIDType', 'VolumeType', 'BlockSizeBytes',
                      'Capacity', 'CapacityBytes', 'CapacitySources',
                      'Encrypted', 'EncryptionTypes', 'Identifiers',
                      'Operations', 'OptimumIOSizeBytes', 'AccessCapabilities',
                      'AllocatedPools', 'Status']

        # Find Storage service
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        if 'SimpleStorage' not in data and 'Storage' not in data:
            return {'ret': False, 'msg': "SimpleStorage and Storage resource \
                     not found"}

        if 'Storage' in data:
            # Get a list of all storage controllers and build respective URIs
            storage_uri = data[u'Storage'][u'@odata.id']
            response = self.get_request(self.root_uri + storage_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']

            if data.get('Members'):
                for controller in data[u'Members']:
                    controller_list.append(controller[u'@odata.id'])
                for c in controller_list:
                    uri = self.root_uri + c
                    response = self.get_request(uri)
                    if response['ret'] is False:
                        return response
                    data = response['data']
                    controller_name = 'Controller 1'
                    if 'StorageControllers' in data:
                        sc = data['StorageControllers']
                        if sc:
                            if 'Name' in sc[0]:
                                controller_name = sc[0]['Name']
                            else:
                                sc_id = sc[0].get('Id', '1')
                                controller_name = 'Controller %s' % sc_id
                    volume_results = []
                    if 'Volumes' in data:
                        # Get a list of all volumes and build respective URIs
                        volumes_uri = data[u'Volumes'][u'@odata.id']
                        response = self.get_request(self.root_uri + volumes_uri)
                        data = response['data']

                        if data.get('Members'):
                            for volume in data[u'Members']:
                                volume_list.append(volume[u'@odata.id'])
                            for v in volume_list:
                                uri = self.root_uri + v
                                response = self.get_request(uri)
                                if response['ret'] is False:
                                    return response
                                data = response['data']

                                volume_result = {}
                                for property in properties:
                                    if property in data:
                                        if data[property] is not None:
                                            volume_result[property] = data[property]

                                # Get related Drives Id
                                drive_id_list = []
                                if 'Links' in data:
                                    if 'Drives' in data[u'Links']:
                                        for link in data[u'Links'][u'Drives']:
                                            drive_id_link = link[u'@odata.id']
                                            drive_id = drive_id_link.split("/")[-1]
                                            drive_id_list.append({'Id': drive_id})
                                        volume_result['Linked_drives'] = drive_id_list
                                volume_results.append(volume_result)
                    volumes = {'Controller': controller_name,
                               'Volumes': volume_results}
                    result["entries"].append(volumes)
        else:
            return {'ret': False, 'msg': "Storage resource not found"}

        return result

    def get_multi_volume_inventory(self):
        return self.aggregate_systems(self.get_volume_inventory)

    def manage_system_indicator_led(self, command):
        return self.manage_indicator_led(command, self.systems_uri)

    def manage_chassis_indicator_led(self, command):
        return self.manage_indicator_led(command, self.chassis_uri)

    def manage_indicator_led(self, command, resource_uri=None):
        # If no resource is specified; default to the Chassis resource
        if resource_uri is None:
            resource_uri = self.chassis_uri

        # Perform a PATCH on the IndicatorLED property based on the requested command
        payloads = {'IndicatorLedOn': 'Lit', 'IndicatorLedOff': 'Off', "IndicatorLedBlink": 'Blinking'}
        if command not in payloads.keys():
            return {'ret': False, 'msg': 'Invalid command (%s)' % command}
        payload = {'IndicatorLED': payloads[command]}
        resp = self.patch_request(self.root_uri + resource_uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Set IndicatorLED to %s' % payloads[command]
        return resp

    def _map_reset_type(self, reset_type, allowable_values):
        equiv_types = {
            'On': 'ForceOn',
            'ForceOn': 'On',
            'ForceOff': 'GracefulShutdown',
            'GracefulShutdown': 'ForceOff',
            'GracefulRestart': 'ForceRestart',
            'ForceRestart': 'GracefulRestart'
        }

        if reset_type in allowable_values:
            return reset_type
        if reset_type not in equiv_types:
            return reset_type
        mapped_type = equiv_types[reset_type]
        if mapped_type in allowable_values:
            return mapped_type
        return reset_type

    def manage_system_power(self, command):
        return self.manage_power(command, self.systems_uri,
                                 '#ComputerSystem.Reset')

    def manage_manager_power(self, command):
        return self.manage_power(command, self.manager_uri,
                                 '#Manager.Reset')

    def manage_power(self, command, resource_uri, action_name):
        key = "Actions"
        reset_type_values = ['On', 'ForceOff', 'GracefulShutdown',
                             'GracefulRestart', 'ForceRestart', 'Nmi',
                             'ForceOn', 'PushPowerButton', 'PowerCycle']

        # command should be PowerOn, PowerForceOff, etc.
        if not command.startswith('Power'):
            return {'ret': False, 'msg': 'Invalid Command (%s)' % command}
        reset_type = command[5:]

        # map Reboot to a ResetType that does a reboot
        if reset_type == 'Reboot':
            reset_type = 'GracefulRestart'

        if reset_type not in reset_type_values:
            return {'ret': False, 'msg': 'Invalid Command (%s)' % command}

        # read the resource and get the current power state
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        power_state = data.get('PowerState')

        # if power is already in target state, nothing to do
        if power_state == "On" and reset_type in ['On', 'ForceOn']:
            return {'ret': True, 'changed': False}
        if power_state == "Off" and reset_type in ['GracefulShutdown', 'ForceOff']:
            return {'ret': True, 'changed': False}

        # get the reset Action and target URI
        if key not in data or action_name not in data[key]:
            return {'ret': False, 'msg': 'Action %s not found' % action_name}
        reset_action = data[key][action_name]
        if 'target' not in reset_action:
            return {'ret': False,
                    'msg': 'target URI missing from Action %s' % action_name}
        action_uri = reset_action['target']

        # get AllowableValues
        ai = self._get_all_action_info_values(reset_action)
        allowable_values = ai.get('ResetType', {}).get('AllowableValues', [])

        # map ResetType to an allowable value if needed
        if reset_type not in allowable_values:
            reset_type = self._map_reset_type(reset_type, allowable_values)

        # define payload
        payload = {'ResetType': reset_type}

        # POST to Action URI
        response = self.post_request(self.root_uri + action_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True}

    def _find_account_uri(self, username=None, acct_id=None):
        if not any((username, acct_id)):
            return {'ret': False, 'msg':
                    'Must provide either account_id or account_username'}

        response = self.get_request(self.root_uri + self.accounts_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        uris = [a.get('@odata.id') for a in data.get('Members', []) if
                a.get('@odata.id')]
        for uri in uris:
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                continue
            data = response['data']
            headers = response['headers']
            if username:
                if username == data.get('UserName'):
                    return {'ret': True, 'data': data,
                            'headers': headers, 'uri': uri}
            if acct_id:
                if acct_id == data.get('Id'):
                    return {'ret': True, 'data': data,
                            'headers': headers, 'uri': uri}

        return {'ret': False, 'no_match': True, 'msg':
                'No account with the given account_id or account_username found'}

    def _find_empty_account_slot(self):
        response = self.get_request(self.root_uri + self.accounts_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        uris = [a.get('@odata.id') for a in data.get('Members', []) if
                a.get('@odata.id')]
        if uris:
            # first slot may be reserved, so move to end of list
            uris += [uris.pop(0)]
        for uri in uris:
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                continue
            data = response['data']
            headers = response['headers']
            if data.get('UserName') == "" and not data.get('Enabled', True):
                return {'ret': True, 'data': data,
                        'headers': headers, 'uri': uri}

        return {'ret': False, 'no_match': True, 'msg':
                'No empty account slot found'}

    def list_users(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        user_list = []
        users_results = []
        # Get these entries, but does not fail if not found
        properties = ['Id', 'Name', 'UserName', 'RoleId', 'Locked', 'Enabled']

        response = self.get_request(self.root_uri + self.accounts_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for users in data.get('Members', []):
            user_list.append(users[u'@odata.id'])   # user_list[] are URIs

        # for each user, get details
        for uri in user_list:
            user = {}
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for property in properties:
                if property in data:
                    user[property] = data[property]

            users_results.append(user)
        result["entries"] = users_results
        return result

    def add_user_via_patch(self, user):
        if user.get('account_id'):
            # If Id slot specified, use it
            response = self._find_account_uri(acct_id=user.get('account_id'))
        else:
            # Otherwise find first empty slot
            response = self._find_empty_account_slot()

        if not response['ret']:
            return response
        uri = response['uri']
        payload = {}
        if user.get('account_username'):
            payload['UserName'] = user.get('account_username')
        if user.get('account_password'):
            payload['Password'] = user.get('account_password')
        if user.get('account_roleid'):
            payload['RoleId'] = user.get('account_roleid')
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def add_user(self, user):
        if not user.get('account_username'):
            return {'ret': False, 'msg':
                    'Must provide account_username for AddUser command'}

        response = self._find_account_uri(username=user.get('account_username'))
        if response['ret']:
            # account_username already exists, nothing to do
            return {'ret': True, 'changed': False}

        response = self.get_request(self.root_uri + self.accounts_uri)
        if not response['ret']:
            return response
        headers = response['headers']

        if 'allow' in headers:
            methods = [m.strip() for m in headers.get('allow').split(',')]
            if 'POST' not in methods:
                # if Allow header present and POST not listed, add via PATCH
                return self.add_user_via_patch(user)

        payload = {}
        if user.get('account_username'):
            payload['UserName'] = user.get('account_username')
        if user.get('account_password'):
            payload['Password'] = user.get('account_password')
        if user.get('account_roleid'):
            payload['RoleId'] = user.get('account_roleid')
        if user.get('account_id'):
            payload['Id'] = user.get('account_id')

        response = self.post_request(self.root_uri + self.accounts_uri, payload)
        if not response['ret']:
            if response.get('status') == 405:
                # if POST returned a 405, try to add via PATCH
                return self.add_user_via_patch(user)
            else:
                return response
        return {'ret': True}

    def enable_user(self, user):
        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            return response
        uri = response['uri']

        payload = {'Enabled': True}
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def delete_user_via_patch(self, user, uri=None, data=None):
        if not uri:
            response = self._find_account_uri(username=user.get('account_username'),
                                              acct_id=user.get('account_id'))
            if not response['ret']:
                return response
            uri = response['uri']
            data = response['data']

        payload = {'UserName': ''}
        if data.get('Enabled', False):
            payload['Enabled'] = False
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def delete_user(self, user):
        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            if response.get('no_match'):
                # account does not exist, nothing to do
                return {'ret': True, 'changed': False}
            else:
                # some error encountered
                return response

        uri = response['uri']
        headers = response['headers']
        data = response['data']

        if 'allow' in headers:
            methods = [m.strip() for m in headers.get('allow').split(',')]
            if 'DELETE' not in methods:
                # if Allow header present and DELETE not listed, del via PATCH
                return self.delete_user_via_patch(user, uri=uri, data=data)

        response = self.delete_request(self.root_uri + uri)
        if not response['ret']:
            if response.get('status') == 405:
                # if DELETE returned a 405, try to delete via PATCH
                return self.delete_user_via_patch(user, uri=uri, data=data)
            else:
                return response
        return {'ret': True}

    def disable_user(self, user):
        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            return response

        uri = response['uri']
        payload = {'Enabled': False}
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def update_user_role(self, user):
        if not user.get('account_roleid'):
            return {'ret': False, 'msg':
                    'Must provide account_roleid for UpdateUserRole command'}

        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            return response

        uri = response['uri']
        payload = {'RoleId': user['account_roleid']}
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def update_user_password(self, user):
        if not user.get('account_password'):
            return {'ret': False, 'msg':
                    'Must provide account_password for UpdateUserPassword command'}

        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            return response

        uri = response['uri']
        payload = {'Password': user['account_password']}
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def update_user_name(self, user):
        if not user.get('account_updatename'):
            return {'ret': False, 'msg':
                    'Must provide account_updatename for UpdateUserName command'}

        response = self._find_account_uri(username=user.get('account_username'),
                                          acct_id=user.get('account_id'))
        if not response['ret']:
            return response

        uri = response['uri']
        payload = {'UserName': user['account_updatename']}
        return self.patch_request(self.root_uri + uri, payload, check_pyld=True)

    def update_accountservice_properties(self, user):
        account_properties = user.get('account_properties')
        if account_properties is None:
            return {'ret': False, 'msg':
                    'Must provide account_properties for UpdateAccountServiceProperties command'}

        # Find the AccountService resource
        response = self.get_request(self.root_uri + self.service_root)
        if response['ret'] is False:
            return response
        data = response['data']
        accountservice_uri = data.get("AccountService", {}).get("@odata.id")
        if accountservice_uri is None:
            return {'ret': False, 'msg': "AccountService resource not found"}

        # Perform a PATCH on the AccountService resource with the requested properties
        resp = self.patch_request(self.root_uri + accountservice_uri, account_properties, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified account service'
        return resp

    def get_sessions(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        session_list = []
        sessions_results = []
        # Get these entries, but does not fail if not found
        properties = ['Description', 'Id', 'Name', 'UserName']

        response = self.get_request(self.root_uri + self.sessions_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for sessions in data[u'Members']:
            session_list.append(sessions[u'@odata.id'])   # session_list[] are URIs

        # for each session, get details
        for uri in session_list:
            session = {}
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for property in properties:
                if property in data:
                    session[property] = data[property]

            sessions_results.append(session)
        result["entries"] = sessions_results
        return result

    def clear_sessions(self):
        response = self.get_request(self.root_uri + self.sessions_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        # if no active sessions, return as success
        if data['Members@odata.count'] == 0:
            return {'ret': True, 'changed': False, 'msg': "There are no active sessions"}

        # loop to delete every active session
        for session in data[u'Members']:
            response = self.delete_request(self.root_uri + session[u'@odata.id'])
            if response['ret'] is False:
                return response

        return {'ret': True, 'changed': True, 'msg': "Cleared all sessions successfully"}

    def create_session(self):
        if not self.creds.get('user') or not self.creds.get('pswd'):
            return {'ret': False, 'msg':
                    'Must provide the username and password parameters for '
                    'the CreateSession command'}

        payload = {
            'UserName': self.creds['user'],
            'Password': self.creds['pswd']
        }
        response = self.post_request(self.root_uri + self.sessions_uri, payload)
        if response['ret'] is False:
            return response

        headers = response['headers']
        if 'x-auth-token' not in headers:
            return {'ret': False, 'msg':
                    'The service did not return the X-Auth-Token header in '
                    'the response from the Sessions collection POST'}

        if 'location' not in headers:
            self.module.warn(
                'The service did not return the Location header for the '
                'session URL in the response from the Sessions collection '
                'POST')
            session_uri = None
        else:
            session_uri = urlparse(headers.get('location')).path

        session = dict()
        session['token'] = headers.get('x-auth-token')
        session['uri'] = session_uri
        return {'ret': True, 'changed': True, 'session': session,
                'msg': 'Session created successfully'}

    def delete_session(self, session_uri):
        if not session_uri:
            return {'ret': False, 'msg':
                    'Must provide the session_uri parameter for the '
                    'DeleteSession command'}

        response = self.delete_request(self.root_uri + session_uri)
        if response['ret'] is False:
            return response

        return {'ret': True, 'changed': True,
                'msg': 'Session deleted successfully'}

    def get_firmware_update_capabilities(self):
        result = {}
        response = self.get_request(self.root_uri + self.update_uri)
        if response['ret'] is False:
            return response

        result['ret'] = True

        result['entries'] = {}

        data = response['data']

        if "Actions" in data:
            actions = data['Actions']
            if len(actions) > 0:
                for key in actions.keys():
                    action = actions.get(key)
                    if 'title' in action:
                        title = action['title']
                    else:
                        title = key
                    result['entries'][title] = action.get('TransferProtocol@Redfish.AllowableValues',
                                                          ["Key TransferProtocol@Redfish.AllowableValues not found"])
            else:
                return {'ret': "False", 'msg': "Actions list is empty."}
        else:
            return {'ret': "False", 'msg': "Key Actions not found."}
        return result

    def _software_inventory(self, uri):
        result = {}
        response = self.get_request(self.root_uri + uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        result['entries'] = []
        for member in data[u'Members']:
            uri = self.root_uri + member[u'@odata.id']
            # Get details for each software or firmware member
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            software = {}
            # Get these standard properties if present
            for key in ['Name', 'Id', 'Status', 'Version', 'Updateable',
                        'SoftwareId', 'LowestSupportedVersion', 'Manufacturer',
                        'ReleaseDate']:
                if key in data:
                    software[key] = data.get(key)
            result['entries'].append(software)
        return result

    def get_firmware_inventory(self):
        if self.firmware_uri is None:
            return {'ret': False, 'msg': 'No FirmwareInventory resource found'}
        else:
            return self._software_inventory(self.firmware_uri)

    def get_software_inventory(self):
        if self.software_uri is None:
            return {'ret': False, 'msg': 'No SoftwareInventory resource found'}
        else:
            return self._software_inventory(self.software_uri)

    def simple_update(self, update_opts):
        image_uri = update_opts.get('update_image_uri')
        protocol = update_opts.get('update_protocol')
        targets = update_opts.get('update_targets')
        creds = update_opts.get('update_creds')

        if not image_uri:
            return {'ret': False, 'msg':
                    'Must specify update_image_uri for the SimpleUpdate command'}

        response = self.get_request(self.root_uri + self.update_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'Actions' not in data:
            return {'ret': False, 'msg': 'Service does not support SimpleUpdate'}
        if '#UpdateService.SimpleUpdate' not in data['Actions']:
            return {'ret': False, 'msg': 'Service does not support SimpleUpdate'}
        action = data['Actions']['#UpdateService.SimpleUpdate']
        if 'target' not in action:
            return {'ret': False, 'msg': 'Service does not support SimpleUpdate'}
        update_uri = action['target']
        if protocol:
            default_values = ['CIFS', 'FTP', 'SFTP', 'HTTP', 'HTTPS', 'NSF',
                              'SCP', 'TFTP', 'OEM', 'NFS']
            allowable_values = self._get_allowable_values(action,
                                                          'TransferProtocol',
                                                          default_values)
            if protocol not in allowable_values:
                return {'ret': False,
                        'msg': 'Specified update_protocol (%s) not supported '
                               'by service. Supported protocols: %s' %
                               (protocol, allowable_values)}
        if targets:
            allowable_values = self._get_allowable_values(action, 'Targets')
            if allowable_values:
                for target in targets:
                    if target not in allowable_values:
                        return {'ret': False,
                                'msg': 'Specified target (%s) not supported '
                                       'by service. Supported targets: %s' %
                                       (target, allowable_values)}

        payload = {
            'ImageURI': image_uri
        }
        if protocol:
            payload["TransferProtocol"] = protocol
        if targets:
            payload["Targets"] = targets
        if creds:
            if creds.get('username'):
                payload["Username"] = creds.get('username')
            if creds.get('password'):
                payload["Password"] = creds.get('password')
        response = self.post_request(self.root_uri + update_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True,
                'msg': "SimpleUpdate requested"}

    def get_bios_attributes(self, systems_uri):
        result = {}
        bios_attributes = {}
        key = "Bios"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        bios_uri = data[key]["@odata.id"]

        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        for attribute in data[u'Attributes'].items():
            bios_attributes[attribute[0]] = attribute[1]
        result["entries"] = bios_attributes
        return result

    def get_multi_bios_attributes(self):
        return self.aggregate_systems(self.get_bios_attributes)

    def _get_boot_options_dict(self, boot):
        # Get these entries from BootOption, if present
        properties = ['DisplayName', 'BootOptionReference']

        # Retrieve BootOptions if present
        if 'BootOptions' in boot and '@odata.id' in boot['BootOptions']:
            boot_options_uri = boot['BootOptions']["@odata.id"]
            # Get BootOptions resource
            response = self.get_request(self.root_uri + boot_options_uri)
            if response['ret'] is False:
                return {}
            data = response['data']

            # Retrieve Members array
            if 'Members' not in data:
                return {}
            members = data['Members']
        else:
            members = []

        # Build dict of BootOptions keyed by BootOptionReference
        boot_options_dict = {}
        for member in members:
            if '@odata.id' not in member:
                return {}
            boot_option_uri = member['@odata.id']
            response = self.get_request(self.root_uri + boot_option_uri)
            if response['ret'] is False:
                return {}
            data = response['data']
            if 'BootOptionReference' not in data:
                return {}
            boot_option_ref = data['BootOptionReference']

            # fetch the props to display for this boot device
            boot_props = {}
            for prop in properties:
                if prop in data:
                    boot_props[prop] = data[prop]

            boot_options_dict[boot_option_ref] = boot_props

        return boot_options_dict

    def get_boot_order(self, systems_uri):
        result = {}

        # Retrieve System resource
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        # Confirm needed Boot properties are present
        if 'Boot' not in data or 'BootOrder' not in data['Boot']:
            return {'ret': False, 'msg': "Key BootOrder not found"}

        boot = data['Boot']
        boot_order = boot['BootOrder']
        boot_options_dict = self._get_boot_options_dict(boot)

        # Build boot device list
        boot_device_list = []
        for ref in boot_order:
            boot_device_list.append(
                boot_options_dict.get(ref, {'BootOptionReference': ref}))

        result["entries"] = boot_device_list
        return result

    def get_multi_boot_order(self):
        return self.aggregate_systems(self.get_boot_order)

    def get_boot_override(self, systems_uri):
        result = {}

        properties = ["BootSourceOverrideEnabled", "BootSourceOverrideTarget",
                      "BootSourceOverrideMode", "UefiTargetBootSourceOverride", "BootSourceOverrideTarget@Redfish.AllowableValues"]

        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if 'Boot' not in data:
            return {'ret': False, 'msg': "Key Boot not found"}

        boot = data['Boot']

        boot_overrides = {}
        if "BootSourceOverrideEnabled" in boot:
            if boot["BootSourceOverrideEnabled"] is not False:
                for property in properties:
                    if property in boot:
                        if boot[property] is not None:
                            boot_overrides[property] = boot[property]
        else:
            return {'ret': False, 'msg': "No boot override is enabled."}

        result['entries'] = boot_overrides
        return result

    def get_multi_boot_override(self):
        return self.aggregate_systems(self.get_boot_override)

    def set_bios_default_settings(self):
        # Find the Bios resource from the requested ComputerSystem resource
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        bios_uri = data.get('Bios', {}).get('@odata.id')
        if bios_uri is None:
            return {'ret': False, 'msg': 'Bios resource not found'}

        # Find the URI of the ResetBios action
        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        reset_bios_uri = data.get('Actions', {}).get('#Bios.ResetBios', {}).get('target')
        if reset_bios_uri is None:
            return {'ret': False, 'msg': 'ResetBios action not found'}

        # Perform the ResetBios action
        response = self.post_request(self.root_uri + reset_bios_uri, {})
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "BIOS set to default settings"}

    def set_boot_override(self, boot_opts):
        # Extract the requested boot override options
        bootdevice = boot_opts.get('bootdevice')
        uefi_target = boot_opts.get('uefi_target')
        boot_next = boot_opts.get('boot_next')
        override_enabled = boot_opts.get('override_enabled')
        boot_override_mode = boot_opts.get('boot_override_mode')
        if not bootdevice and override_enabled != 'Disabled':
            return {'ret': False,
                    'msg': "bootdevice option required for temporary boot override"}

        # Get the current boot override options from the Boot property
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        boot = data.get('Boot')
        if boot is None:
            return {'ret': False, 'msg': "Boot property not found"}
        cur_override_mode = boot.get('BootSourceOverrideMode')

        # Check if the requested target is supported by the system
        if override_enabled != 'Disabled':
            annotation = 'BootSourceOverrideTarget@Redfish.AllowableValues'
            if annotation in boot:
                allowable_values = boot[annotation]
                if isinstance(allowable_values, list) and bootdevice not in allowable_values:
                    return {'ret': False,
                            'msg': "Boot device %s not in list of allowable values (%s)" %
                                   (bootdevice, allowable_values)}

        # Build the request payload based on the desired boot override options
        if override_enabled == 'Disabled':
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': override_enabled,
                    'BootSourceOverrideTarget': 'None'
                }
            }
        elif bootdevice == 'UefiTarget':
            if not uefi_target:
                return {'ret': False,
                        'msg': "uefi_target option required to SetOneTimeBoot for UefiTarget"}
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': override_enabled,
                    'BootSourceOverrideTarget': bootdevice,
                    'UefiTargetBootSourceOverride': uefi_target
                }
            }
            # If needed, also specify UEFI mode
            if cur_override_mode == 'Legacy':
                payload['Boot']['BootSourceOverrideMode'] = 'UEFI'
        elif bootdevice == 'UefiBootNext':
            if not boot_next:
                return {'ret': False,
                        'msg': "boot_next option required to SetOneTimeBoot for UefiBootNext"}
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': override_enabled,
                    'BootSourceOverrideTarget': bootdevice,
                    'BootNext': boot_next
                }
            }
            # If needed, also specify UEFI mode
            if cur_override_mode == 'Legacy':
                payload['Boot']['BootSourceOverrideMode'] = 'UEFI'
        else:
            payload = {
                'Boot': {
                    'BootSourceOverrideEnabled': override_enabled,
                    'BootSourceOverrideTarget': bootdevice
                }
            }
            if boot_override_mode:
                payload['Boot']['BootSourceOverrideMode'] = boot_override_mode

        # Apply the requested boot override request
        resp = self.patch_request(self.root_uri + self.systems_uri, payload, check_pyld=True)
        if resp['ret'] is False:
            # WORKAROUND
            # Older Dell systems do not allow BootSourceOverrideEnabled to be
            # specified with UefiTarget as the target device
            vendor = self._get_vendor()['Vendor']
            if vendor == 'Dell':
                if bootdevice == 'UefiTarget' and override_enabled != 'Disabled':
                    payload['Boot'].pop('BootSourceOverrideEnabled', None)
                    resp = self.patch_request(self.root_uri + self.systems_uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Updated the boot override settings'
        return resp

    def set_bios_attributes(self, attributes):
        # Find the Bios resource from the requested ComputerSystem resource
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        bios_uri = data.get('Bios', {}).get('@odata.id')
        if bios_uri is None:
            return {'ret': False, 'msg': 'Bios resource not found'}

        # Get the current BIOS settings
        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        # Make a copy of the attributes dict
        attrs_to_patch = dict(attributes)
        # List to hold attributes not found
        attrs_bad = {}

        # Check the attributes
        for attr_name, attr_value in attributes.items():
            # Check if attribute exists
            if attr_name not in data[u'Attributes']:
                # Remove and proceed to next attribute if this isn't valid
                attrs_bad.update({attr_name: attr_value})
                del attrs_to_patch[attr_name]
                continue

            # If already set to requested value, remove it from PATCH payload
            if data[u'Attributes'][attr_name] == attributes[attr_name]:
                del attrs_to_patch[attr_name]

        warning = ""
        if attrs_bad:
            warning = "Unsupported attributes %s" % (attrs_bad)

        # Return success w/ changed=False if no attrs need to be changed
        if not attrs_to_patch:
            return {'ret': True, 'changed': False,
                    'msg': "BIOS attributes already set",
                    'warning': warning}

        # Get the SettingsObject URI to apply the attributes
        set_bios_attr_uri = data.get("@Redfish.Settings", {}).get("SettingsObject", {}).get("@odata.id")
        if set_bios_attr_uri is None:
            return {'ret': False, 'msg': "Settings resource for BIOS attributes not found."}

        # Construct payload and issue PATCH command
        payload = {"Attributes": attrs_to_patch}
        response = self.patch_request(self.root_uri + set_bios_attr_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True,
                'msg': "Modified BIOS attributes %s" % (attrs_to_patch),
                'warning': warning}

    def set_boot_order(self, boot_list):
        if not boot_list:
            return {'ret': False,
                    'msg': "boot_order list required for SetBootOrder command"}

        systems_uri = self.systems_uri
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        # Confirm needed Boot properties are present
        if 'Boot' not in data or 'BootOrder' not in data['Boot']:
            return {'ret': False, 'msg': "Key BootOrder not found"}

        boot = data['Boot']
        boot_order = boot['BootOrder']
        boot_options_dict = self._get_boot_options_dict(boot)

        # Verify the requested boot options are valid
        if boot_options_dict:
            boot_option_references = boot_options_dict.keys()
            for ref in boot_list:
                if ref not in boot_option_references:
                    return {'ret': False,
                            'msg': "BootOptionReference %s not found in BootOptions" % ref}

        # Apply the boot order
        payload = {
            'Boot': {
                'BootOrder': boot_list
            }
        }
        resp = self.patch_request(self.root_uri + systems_uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified the boot order'
        return resp

    def set_default_boot_order(self):
        systems_uri = self.systems_uri
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']

        # get the #ComputerSystem.SetDefaultBootOrder Action and target URI
        action = '#ComputerSystem.SetDefaultBootOrder'
        if 'Actions' not in data or action not in data['Actions']:
            return {'ret': False, 'msg': 'Action %s not found' % action}
        if 'target' not in data['Actions'][action]:
            return {'ret': False,
                    'msg': 'target URI missing from Action %s' % action}
        action_uri = data['Actions'][action]['target']

        # POST to Action URI
        payload = {}
        response = self.post_request(self.root_uri + action_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True,
                'msg': "BootOrder set to default"}

    def get_chassis_inventory(self):
        result = {}
        chassis_results = []

        # Get these entries, but does not fail if not found
        properties = ['Name', 'Id', 'ChassisType', 'PartNumber', 'AssetTag',
                      'Manufacturer', 'IndicatorLED', 'SerialNumber', 'Model']

        # Go through list
        for chassis_uri in self.chassis_uris:
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            chassis_result = {}
            for property in properties:
                if property in data:
                    chassis_result[property] = data[property]
            chassis_results.append(chassis_result)

        result["entries"] = chassis_results
        return result

    def get_fan_inventory(self):
        result = {}
        fan_results = []
        key = "Thermal"
        # Get these entries, but does not fail if not found
        properties = ['Name', 'FanName', 'Reading', 'ReadingUnits', 'Status']

        # Go through list
        for chassis_uri in self.chassis_uris:
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            if key in data:
                # match: found an entry for "Thermal" information = fans
                thermal_uri = data[key]["@odata.id"]
                response = self.get_request(self.root_uri + thermal_uri)
                if response['ret'] is False:
                    return response
                result['ret'] = True
                data = response['data']

                # Checking if fans are present
                if u'Fans' in data:
                    for device in data[u'Fans']:
                        fan = {}
                        for property in properties:
                            if property in device:
                                fan[property] = device[property]
                        fan_results.append(fan)
                else:
                    return {'ret': False, 'msg': "No Fans present"}
        result["entries"] = fan_results
        return result

    def get_chassis_power(self):
        result = {}
        key = "Power"

        # Get these entries, but does not fail if not found
        properties = ['Name', 'PowerAllocatedWatts',
                      'PowerAvailableWatts', 'PowerCapacityWatts',
                      'PowerConsumedWatts', 'PowerMetrics',
                      'PowerRequestedWatts', 'RelatedItem', 'Status']

        chassis_power_results = []
        # Go through list
        for chassis_uri in self.chassis_uris:
            chassis_power_result = {}
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            if key in data:
                response = self.get_request(self.root_uri + data[key]['@odata.id'])
                data = response['data']
                if 'PowerControl' in data:
                    if len(data['PowerControl']) > 0:
                        data = data['PowerControl'][0]
                        for property in properties:
                            if property in data:
                                chassis_power_result[property] = data[property]
                chassis_power_results.append(chassis_power_result)

        if len(chassis_power_results) > 0:
            result['entries'] = chassis_power_results
            return result
        else:
            return {'ret': False, 'msg': 'Power information not found.'}

    def get_chassis_thermals(self):
        result = {}
        sensors = []
        key = "Thermal"

        # Get these entries, but does not fail if not found
        properties = ['Name', 'PhysicalContext', 'UpperThresholdCritical',
                      'UpperThresholdFatal', 'UpperThresholdNonCritical',
                      'LowerThresholdCritical', 'LowerThresholdFatal',
                      'LowerThresholdNonCritical', 'MaxReadingRangeTemp',
                      'MinReadingRangeTemp', 'ReadingCelsius', 'RelatedItem',
                      'SensorNumber', 'Status']

        # Go through list
        for chassis_uri in self.chassis_uris:
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            if key in data:
                thermal_uri = data[key]["@odata.id"]
                response = self.get_request(self.root_uri + thermal_uri)
                if response['ret'] is False:
                    return response
                result['ret'] = True
                data = response['data']
                if "Temperatures" in data:
                    for sensor in data[u'Temperatures']:
                        sensor_result = {}
                        for property in properties:
                            if property in sensor:
                                if sensor[property] is not None:
                                    sensor_result[property] = sensor[property]
                        sensors.append(sensor_result)

        if sensors is None:
            return {'ret': False, 'msg': 'Key Temperatures was not found.'}

        result['entries'] = sensors
        return result

    def get_cpu_inventory(self, systems_uri):
        result = {}
        cpu_list = []
        cpu_results = []
        key = "Processors"
        # Get these entries, but does not fail if not found
        properties = ['Id', 'Name', 'Manufacturer', 'Model', 'MaxSpeedMHz',
                      'TotalCores', 'TotalThreads', 'Status']

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        processors_uri = data[key]["@odata.id"]

        # Get a list of all CPUs and build respective URIs
        response = self.get_request(self.root_uri + processors_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for cpu in data[u'Members']:
            cpu_list.append(cpu[u'@odata.id'])

        for c in cpu_list:
            cpu = {}
            uri = self.root_uri + c
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for property in properties:
                if property in data:
                    cpu[property] = data[property]

            cpu_results.append(cpu)
        result["entries"] = cpu_results
        return result

    def get_multi_cpu_inventory(self):
        return self.aggregate_systems(self.get_cpu_inventory)

    def get_memory_inventory(self, systems_uri):
        result = {}
        memory_list = []
        memory_results = []
        key = "Memory"
        # Get these entries, but does not fail if not found
        properties = ['Id', 'SerialNumber', 'MemoryDeviceType', 'PartNumber',
                      'MemoryLocation', 'RankCount', 'CapacityMiB', 'OperatingMemoryModes', 'Status', 'Manufacturer', 'Name']

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        memory_uri = data[key]["@odata.id"]

        # Get a list of all DIMMs and build respective URIs
        response = self.get_request(self.root_uri + memory_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for dimm in data[u'Members']:
            memory_list.append(dimm[u'@odata.id'])

        for m in memory_list:
            dimm = {}
            uri = self.root_uri + m
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']

            if "Status" in data:
                if "State" in data["Status"]:
                    if data["Status"]["State"] == "Absent":
                        continue
            else:
                continue

            for property in properties:
                if property in data:
                    dimm[property] = data[property]

            memory_results.append(dimm)
        result["entries"] = memory_results
        return result

    def get_multi_memory_inventory(self):
        return self.aggregate_systems(self.get_memory_inventory)

    def get_nic(self, resource_uri):
        result = {}
        properties = ['Name', 'Id', 'Description', 'FQDN', 'IPv4Addresses', 'IPv6Addresses',
                      'NameServers', 'MACAddress', 'PermanentMACAddress',
                      'SpeedMbps', 'MTUSize', 'AutoNeg', 'Status']
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        nic = {}
        for property in properties:
            if property in data:
                nic[property] = data[property]
        result['entries'] = nic
        return result

    def get_nic_inventory(self, resource_uri):
        result = {}
        nic_list = []
        nic_results = []
        key = "EthernetInterfaces"

        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        ethernetinterfaces_uri = data[key]["@odata.id"]

        # Get a list of all network controllers and build respective URIs
        response = self.get_request(self.root_uri + ethernetinterfaces_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for nic in data[u'Members']:
            nic_list.append(nic[u'@odata.id'])

        for n in nic_list:
            nic = self.get_nic(n)
            if nic['ret']:
                nic_results.append(nic['entries'])
        result["entries"] = nic_results
        return result

    def get_multi_nic_inventory(self, resource_type):
        ret = True
        entries = []

        #  Given resource_type, use the proper URI
        if resource_type == 'Systems':
            resource_uris = self.systems_uris
        elif resource_type == 'Manager':
            resource_uris = self.manager_uris

        for resource_uri in resource_uris:
            inventory = self.get_nic_inventory(resource_uri)
            ret = inventory.pop('ret') and ret
            if 'entries' in inventory:
                entries.append(({'resource_uri': resource_uri},
                                inventory['entries']))
        return dict(ret=ret, entries=entries)

    def get_virtualmedia(self, resource_uri):
        result = {}
        virtualmedia_list = []
        virtualmedia_results = []
        key = "VirtualMedia"
        # Get these entries, but does not fail if not found
        properties = ['Description', 'ConnectedVia', 'Id', 'MediaTypes',
                      'Image', 'ImageName', 'Name', 'WriteProtected',
                      'TransferMethod', 'TransferProtocolType']

        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        virtualmedia_uri = data[key]["@odata.id"]

        # Get a list of all virtual media and build respective URIs
        response = self.get_request(self.root_uri + virtualmedia_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for virtualmedia in data[u'Members']:
            virtualmedia_list.append(virtualmedia[u'@odata.id'])

        for n in virtualmedia_list:
            virtualmedia = {}
            uri = self.root_uri + n
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']

            for property in properties:
                if property in data:
                    virtualmedia[property] = data[property]

            virtualmedia_results.append(virtualmedia)
        result["entries"] = virtualmedia_results
        return result

    def get_multi_virtualmedia(self, resource_type='Manager'):
        ret = True
        entries = []

        #  Given resource_type, use the proper URI
        if resource_type == 'Systems':
            resource_uris = self.systems_uris
        elif resource_type == 'Manager':
            resource_uris = self.manager_uris

        for resource_uri in resource_uris:
            virtualmedia = self.get_virtualmedia(resource_uri)
            ret = virtualmedia.pop('ret') and ret
            if 'entries' in virtualmedia:
                entries.append(({'resource_uri': resource_uri},
                               virtualmedia['entries']))
        return dict(ret=ret, entries=entries)

    @staticmethod
    def _find_empty_virt_media_slot(resources, media_types,
                                    media_match_strict=True, vendor=''):
        for uri, data in resources.items():
            # check MediaTypes
            if 'MediaTypes' in data and media_types:
                if not set(media_types).intersection(set(data['MediaTypes'])):
                    continue
            else:
                if media_match_strict:
                    continue
            # Base on current Lenovo server capability, filter out slot RDOC1/2 and Remote1/2/3/4 which are not supported to Insert/Eject.
            if vendor == 'Lenovo' and ('RDOC' in uri or 'Remote' in uri):
                continue
            # if ejected, 'Inserted' should be False and 'ImageName' cleared
            if (not data.get('Inserted', False) and
                    not data.get('ImageName')):
                return uri, data
        return None, None

    @staticmethod
    def _virt_media_image_inserted(resources, image_url):
        for uri, data in resources.items():
            if data.get('Image'):
                if urlparse(image_url) == urlparse(data.get('Image')):
                    if data.get('Inserted', False) and data.get('ImageName'):
                        return True
        return False

    @staticmethod
    def _find_virt_media_to_eject(resources, image_url):
        matched_uri, matched_data = None, None
        for uri, data in resources.items():
            if data.get('Image'):
                if urlparse(image_url) == urlparse(data.get('Image')):
                    matched_uri, matched_data = uri, data
                    if data.get('Inserted', True) and data.get('ImageName', 'x'):
                        return uri, data, True
        return matched_uri, matched_data, False

    def _read_virt_media_resources(self, uri_list):
        resources = {}
        headers = {}
        for uri in uri_list:
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                continue
            resources[uri] = response['data']
            headers[uri] = response['headers']
        return resources, headers

    @staticmethod
    def _insert_virt_media_payload(options, param_map, data, ai):
        payload = {
            'Image': options.get('image_url')
        }
        for param, option in param_map.items():
            if options.get(option) is not None and param in data:
                allowable = ai.get(param, {}).get('AllowableValues', [])
                if allowable and options.get(option) not in allowable:
                    return {'ret': False,
                            'msg': "Value '%s' specified for option '%s' not "
                                   "in list of AllowableValues %s" % (
                                       options.get(option), option,
                                       allowable)}
                payload[param] = options.get(option)
        return payload

    def virtual_media_insert_via_patch(self, options, param_map, uri, data, image_only=False):
        # get AllowableValues
        ai = dict((k[:-24],
                   {'AllowableValues': v}) for k, v in data.items()
                  if k.endswith('@Redfish.AllowableValues'))
        # construct payload
        payload = self._insert_virt_media_payload(options, param_map, data, ai)
        if 'Inserted' not in payload and not image_only:
            # Add Inserted to the payload if needed
            payload['Inserted'] = True

        # PATCH the resource
        resp = self.patch_request(self.root_uri + uri, payload, check_pyld=True)
        if resp['ret'] is False:
            # WORKAROUND
            # Older HPE systems with iLO 4 and Supermicro do not support
            # specifying Inserted or WriteProtected
            vendor = self._get_vendor()['Vendor']
            if vendor == 'HPE' or vendor == 'Supermicro':
                payload.pop('Inserted', None)
                payload.pop('WriteProtected', None)
                resp = self.patch_request(self.root_uri + uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'VirtualMedia inserted'
        return resp

    def virtual_media_insert(self, options, resource_type='Manager'):
        param_map = {
            'Inserted': 'inserted',
            'WriteProtected': 'write_protected',
            'UserName': 'username',
            'Password': 'password',
            'TransferProtocolType': 'transfer_protocol_type',
            'TransferMethod': 'transfer_method'
        }
        image_url = options.get('image_url')
        if not image_url:
            return {'ret': False,
                    'msg': "image_url option required for VirtualMediaInsert"}
        media_types = options.get('media_types')

        # locate and read the VirtualMedia resources
        #  Given resource_type, use the proper URI
        if resource_type == 'Systems':
            resource_uri = self.systems_uri
        elif resource_type == 'Manager':
            resource_uri = self.manager_uri
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'VirtualMedia' not in data:
            return {'ret': False, 'msg': "VirtualMedia resource not found"}

        virt_media_uri = data["VirtualMedia"]["@odata.id"]
        response = self.get_request(self.root_uri + virt_media_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        virt_media_list = []
        for member in data[u'Members']:
            virt_media_list.append(member[u'@odata.id'])
        resources, headers = self._read_virt_media_resources(virt_media_list)

        # see if image already inserted; if so, nothing to do
        if self._virt_media_image_inserted(resources, image_url):
            return {'ret': True, 'changed': False,
                    'msg': "VirtualMedia '%s' already inserted" % image_url}

        # find an empty slot to insert the media
        # try first with strict media_type matching
        vendor = self._get_vendor()['Vendor']
        uri, data = self._find_empty_virt_media_slot(
            resources, media_types, media_match_strict=True, vendor=vendor)
        if not uri:
            # if not found, try without strict media_type matching
            uri, data = self._find_empty_virt_media_slot(
                resources, media_types, media_match_strict=False, vendor=vendor)
        if not uri:
            return {'ret': False,
                    'msg': "Unable to find an available VirtualMedia resource "
                           "%s" % ('supporting ' + str(media_types)
                                   if media_types else '')}

        # confirm InsertMedia action found
        if ('Actions' not in data or
                '#VirtualMedia.InsertMedia' not in data['Actions']):
            # try to insert via PATCH if no InsertMedia action found
            h = headers[uri]
            if 'allow' in h:
                methods = [m.strip() for m in h.get('allow').split(',')]
                if 'PATCH' not in methods:
                    # if Allow header present and PATCH missing, return error
                    return {'ret': False,
                            'msg': "%s action not found and PATCH not allowed"
                            % '#VirtualMedia.InsertMedia'}
            return self.virtual_media_insert_via_patch(options, param_map,
                                                       uri, data)

        # get the action property
        action = data['Actions']['#VirtualMedia.InsertMedia']
        if 'target' not in action:
            return {'ret': False,
                    'msg': "target URI missing from Action "
                           "#VirtualMedia.InsertMedia"}
        action_uri = action['target']
        # get ActionInfo or AllowableValues
        ai = self._get_all_action_info_values(action)
        # construct payload
        payload = self._insert_virt_media_payload(options, param_map, data, ai)
        # POST to action
        response = self.post_request(self.root_uri + action_uri, payload)
        if response['ret'] is False and ('Inserted' in payload or 'WriteProtected' in payload):
            # WORKAROUND
            # Older HPE systems with iLO 4 and Supermicro do not support
            # specifying Inserted or WriteProtected
            vendor = self._get_vendor()['Vendor']
            if vendor == 'HPE' or vendor == 'Supermicro':
                payload.pop('Inserted', None)
                payload.pop('WriteProtected', None)
                response = self.post_request(self.root_uri + action_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "VirtualMedia inserted"}

    def virtual_media_eject_via_patch(self, uri, image_only=False):
        # construct payload
        payload = {
            'Inserted': False,
            'Image': None
        }

        # Inserted is not writable
        if image_only:
            del payload['Inserted']

        # PATCH resource
        resp = self.patch_request(self.root_uri + uri, payload, check_pyld=True)
        if resp['ret'] is False and 'Inserted' in payload:
            # WORKAROUND
            # Older HPE systems with iLO 4 and Supermicro do not support
            # specifying Inserted
            vendor = self._get_vendor()['Vendor']
            if vendor == 'HPE' or vendor == 'Supermicro':
                payload.pop('Inserted', None)
                resp = self.patch_request(self.root_uri + uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'VirtualMedia ejected'
        return resp

    def virtual_media_eject(self, options, resource_type='Manager'):
        image_url = options.get('image_url')
        if not image_url:
            return {'ret': False,
                    'msg': "image_url option required for VirtualMediaEject"}

        # locate and read the VirtualMedia resources
        # Given resource_type, use the proper URI
        if resource_type == 'Systems':
            resource_uri = self.systems_uri
        elif resource_type == 'Manager':
            resource_uri = self.manager_uri
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'VirtualMedia' not in data:
            return {'ret': False, 'msg': "VirtualMedia resource not found"}

        virt_media_uri = data["VirtualMedia"]["@odata.id"]
        response = self.get_request(self.root_uri + virt_media_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        virt_media_list = []
        for member in data[u'Members']:
            virt_media_list.append(member[u'@odata.id'])
        resources, headers = self._read_virt_media_resources(virt_media_list)

        # find the VirtualMedia resource to eject
        uri, data, eject = self._find_virt_media_to_eject(resources, image_url)
        if uri and eject:
            if ('Actions' not in data or
                    '#VirtualMedia.EjectMedia' not in data['Actions']):
                # try to eject via PATCH if no EjectMedia action found
                h = headers[uri]
                if 'allow' in h:
                    methods = [m.strip() for m in h.get('allow').split(',')]
                    if 'PATCH' not in methods:
                        # if Allow header present and PATCH missing, return error
                        return {'ret': False,
                                'msg': "%s action not found and PATCH not allowed"
                                       % '#VirtualMedia.EjectMedia'}
                return self.virtual_media_eject_via_patch(uri)
            else:
                # POST to the EjectMedia Action
                action = data['Actions']['#VirtualMedia.EjectMedia']
                if 'target' not in action:
                    return {'ret': False,
                            'msg': "target URI property missing from Action "
                                   "#VirtualMedia.EjectMedia"}
                action_uri = action['target']
                # empty payload for Eject action
                payload = {}
                # POST to action
                response = self.post_request(self.root_uri + action_uri,
                                             payload)
                if response['ret'] is False:
                    return response
                return {'ret': True, 'changed': True,
                        'msg': "VirtualMedia ejected"}
        elif uri and not eject:
            # already ejected: return success but changed=False
            return {'ret': True, 'changed': False,
                    'msg': "VirtualMedia image '%s' already ejected" %
                           image_url}
        else:
            # return failure (no resources matching image_url found)
            return {'ret': False, 'changed': False,
                    'msg': "No VirtualMedia resource found with image '%s' "
                           "inserted" % image_url}

    def get_psu_inventory(self):
        result = {}
        psu_list = []
        psu_results = []
        key = "PowerSupplies"
        # Get these entries, but does not fail if not found
        properties = ['Name', 'Model', 'SerialNumber', 'PartNumber', 'Manufacturer',
                      'FirmwareVersion', 'PowerCapacityWatts', 'PowerSupplyType',
                      'Status']

        # Get a list of all Chassis and build URIs, then get all PowerSupplies
        # from each Power entry in the Chassis
        chassis_uri_list = self.chassis_uris
        for chassis_uri in chassis_uri_list:
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response

            result['ret'] = True
            data = response['data']

            if 'Power' in data:
                power_uri = data[u'Power'][u'@odata.id']
            else:
                continue

            response = self.get_request(self.root_uri + power_uri)
            data = response['data']

            if key not in data:
                return {'ret': False, 'msg': "Key %s not found" % key}

            psu_list = data[key]
            for psu in psu_list:
                psu_not_present = False
                psu_data = {}
                for property in properties:
                    if property in psu:
                        if psu[property] is not None:
                            if property == 'Status':
                                if 'State' in psu[property]:
                                    if psu[property]['State'] == 'Absent':
                                        psu_not_present = True
                            psu_data[property] = psu[property]
                if psu_not_present:
                    continue
                psu_results.append(psu_data)

        result["entries"] = psu_results
        if not result["entries"]:
            return {'ret': False, 'msg': "No PowerSupply objects found"}
        return result

    def get_multi_psu_inventory(self):
        return self.aggregate_systems(self.get_psu_inventory)

    def get_system_inventory(self, systems_uri):
        result = {}
        inventory = {}
        # Get these entries, but does not fail if not found
        properties = ['Status', 'HostName', 'PowerState', 'Model', 'Manufacturer',
                      'PartNumber', 'SystemType', 'AssetTag', 'ServiceTag',
                      'SerialNumber', 'SKU', 'BiosVersion', 'MemorySummary',
                      'ProcessorSummary', 'TrustedModules', 'Name', 'Id']

        response = self.get_request(self.root_uri + systems_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for property in properties:
            if property in data:
                inventory[property] = data[property]

        result["entries"] = inventory
        return result

    def get_multi_system_inventory(self):
        return self.aggregate_systems(self.get_system_inventory)

    def get_network_protocols(self):
        result = {}
        service_result = {}
        # Find NetworkProtocol
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'NetworkProtocol' not in data:
            return {'ret': False, 'msg': "NetworkProtocol resource not found"}
        networkprotocol_uri = data["NetworkProtocol"]["@odata.id"]

        response = self.get_request(self.root_uri + networkprotocol_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        protocol_services = ['SNMP', 'VirtualMedia', 'Telnet', 'SSDP', 'IPMI', 'SSH',
                             'KVMIP', 'NTP', 'HTTP', 'HTTPS', 'DHCP', 'DHCPv6', 'RDP',
                             'RFB']
        for protocol_service in protocol_services:
            if protocol_service in data.keys():
                service_result[protocol_service] = data[protocol_service]

        result['ret'] = True
        result["entries"] = service_result
        return result

    def set_network_protocols(self, manager_services):
        # Check input data validity
        protocol_services = ['SNMP', 'VirtualMedia', 'Telnet', 'SSDP', 'IPMI', 'SSH',
                             'KVMIP', 'NTP', 'HTTP', 'HTTPS', 'DHCP', 'DHCPv6', 'RDP',
                             'RFB']
        protocol_state_onlist = ['true', 'True', True, 'on', 1]
        protocol_state_offlist = ['false', 'False', False, 'off', 0]
        payload = {}
        for service_name in manager_services.keys():
            if service_name not in protocol_services:
                return {'ret': False, 'msg': "Service name %s is invalid" % service_name}
            payload[service_name] = {}
            for service_property in manager_services[service_name].keys():
                value = manager_services[service_name][service_property]
                if service_property in ['ProtocolEnabled', 'protocolenabled']:
                    if value in protocol_state_onlist:
                        payload[service_name]['ProtocolEnabled'] = True
                    elif value in protocol_state_offlist:
                        payload[service_name]['ProtocolEnabled'] = False
                    else:
                        return {'ret': False, 'msg': "Value of property %s is invalid" % service_property}
                elif service_property in ['port', 'Port']:
                    if isinstance(value, int):
                        payload[service_name]['Port'] = value
                    elif isinstance(value, str) and value.isdigit():
                        payload[service_name]['Port'] = int(value)
                    else:
                        return {'ret': False, 'msg': "Value of property %s is invalid" % service_property}
                else:
                    payload[service_name][service_property] = value

        # Find the ManagerNetworkProtocol resource
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        networkprotocol_uri = data.get("NetworkProtocol", {}).get("@odata.id")
        if networkprotocol_uri is None:
            return {'ret': False, 'msg': "NetworkProtocol resource not found"}

        # Modify the ManagerNetworkProtocol resource
        resp = self.patch_request(self.root_uri + networkprotocol_uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified manager network protocol settings'
        return resp

    @staticmethod
    def to_singular(resource_name):
        if resource_name.endswith('ies'):
            resource_name = resource_name[:-3] + 'y'
        elif resource_name.endswith('s'):
            resource_name = resource_name[:-1]
        return resource_name

    def get_health_resource(self, subsystem, uri, health, expanded):
        status = 'Status'

        if expanded:
            d = expanded
        else:
            r = self.get_request(self.root_uri + uri)
            if r.get('ret'):
                d = r.get('data')
            else:
                return

        if 'Members' in d:  # collections case
            for m in d.get('Members'):
                u = m.get('@odata.id')
                r = self.get_request(self.root_uri + u)
                if r.get('ret'):
                    p = r.get('data')
                    if p:
                        e = {self.to_singular(subsystem.lower()) + '_uri': u,
                             status: p.get(status,
                                           "Status not available")}
                        health[subsystem].append(e)
        else:  # non-collections case
            e = {self.to_singular(subsystem.lower()) + '_uri': uri,
                 status: d.get(status,
                               "Status not available")}
            health[subsystem].append(e)

    def get_health_subsystem(self, subsystem, data, health):
        if subsystem in data:
            sub = data.get(subsystem)
            if isinstance(sub, list):
                for r in sub:
                    if '@odata.id' in r:
                        uri = r.get('@odata.id')
                        expanded = None
                        if '#' in uri and len(r) > 1:
                            expanded = r
                        self.get_health_resource(subsystem, uri, health, expanded)
            elif isinstance(sub, dict):
                if '@odata.id' in sub:
                    uri = sub.get('@odata.id')
                    self.get_health_resource(subsystem, uri, health, None)
        elif 'Members' in data:
            for m in data.get('Members'):
                u = m.get('@odata.id')
                r = self.get_request(self.root_uri + u)
                if r.get('ret'):
                    d = r.get('data')
                    self.get_health_subsystem(subsystem, d, health)

    def get_health_report(self, category, uri, subsystems):
        result = {}
        health = {}
        status = 'Status'

        # Get health status of top level resource
        response = self.get_request(self.root_uri + uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        health[category] = {status: data.get(status, "Status not available")}

        # Get health status of subsystems
        for sub in subsystems:
            d = None
            if sub.startswith('Links.'):  # ex: Links.PCIeDevices
                sub = sub[len('Links.'):]
                d = data.get('Links', {})
            elif '.' in sub:  # ex: Thermal.Fans
                p, sub = sub.split('.')
                u = data.get(p, {}).get('@odata.id')
                if u:
                    r = self.get_request(self.root_uri + u)
                    if r['ret']:
                        d = r['data']
                if not d:
                    continue
            else:  # ex: Memory
                d = data
            health[sub] = []
            self.get_health_subsystem(sub, d, health)
            if not health[sub]:
                del health[sub]

        result["entries"] = health
        return result

    def get_system_health_report(self, systems_uri):
        subsystems = ['Processors', 'Memory', 'SimpleStorage', 'Storage',
                      'EthernetInterfaces', 'NetworkInterfaces.NetworkPorts',
                      'NetworkInterfaces.NetworkDeviceFunctions']
        return self.get_health_report('System', systems_uri, subsystems)

    def get_multi_system_health_report(self):
        return self.aggregate_systems(self.get_system_health_report)

    def get_chassis_health_report(self, chassis_uri):
        subsystems = ['Power.PowerSupplies', 'Thermal.Fans',
                      'Links.PCIeDevices']
        return self.get_health_report('Chassis', chassis_uri, subsystems)

    def get_multi_chassis_health_report(self):
        return self.aggregate_chassis(self.get_chassis_health_report)

    def get_manager_health_report(self, manager_uri):
        subsystems = []
        return self.get_health_report('Manager', manager_uri, subsystems)

    def get_multi_manager_health_report(self):
        return self.aggregate_managers(self.get_manager_health_report)

    def set_manager_nic(self, nic_addr, nic_config):
        # Get the manager ethernet interface uri
        nic_info = self.get_manager_ethernet_uri(nic_addr)

        if nic_info.get('nic_addr') is None:
            return nic_info
        else:
            target_ethernet_uri = nic_info['nic_addr']
            target_ethernet_current_setting = nic_info['ethernet_setting']

        # Convert input to payload and check validity
        # Note: Some properties in the EthernetInterface resource are arrays of
        # objects.  The call into this module expects a flattened view, meaning
        # the user specifies exactly one object for an array property.  For
        # example, if a user provides IPv4StaticAddresses in the request to this
        # module, it will turn that into an array of one member.  This pattern
        # should be avoided for future commands in this module, but needs to be
        # preserved here for backwards compatibility.
        payload = {}
        for property in nic_config.keys():
            value = nic_config[property]
            if property in target_ethernet_current_setting and isinstance(value, dict) and isinstance(target_ethernet_current_setting[property], list):
                payload[property] = list()
                payload[property].append(value)
            else:
                payload[property] = value

        # Modify the EthernetInterface resource
        resp = self.patch_request(self.root_uri + target_ethernet_uri, payload, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified manager NIC'
        return resp

    # A helper function to get the EthernetInterface URI
    def get_manager_ethernet_uri(self, nic_addr='null'):
        # Get EthernetInterface collection
        response = self.get_request(self.root_uri + self.manager_uri)
        if not response['ret']:
            return response
        data = response['data']
        if 'EthernetInterfaces' not in data:
            return {'ret': False, 'msg': "EthernetInterfaces resource not found"}
        ethernetinterfaces_uri = data["EthernetInterfaces"]["@odata.id"]
        response = self.get_request(self.root_uri + ethernetinterfaces_uri)
        if not response['ret']:
            return response
        data = response['data']
        uris = [a.get('@odata.id') for a in data.get('Members', []) if
                a.get('@odata.id')]

        # Find target EthernetInterface
        target_ethernet_uri = None
        target_ethernet_current_setting = None
        if nic_addr == 'null':
            # Find root_uri matched EthernetInterface when nic_addr is not specified
            nic_addr = (self.root_uri).split('/')[-1]
            nic_addr = nic_addr.split(':')[0]  # split port if existing
        for uri in uris:
            response = self.get_request(self.root_uri + uri)
            if not response['ret']:
                return response
            data = response['data']
            data_string = json.dumps(data)
            if nic_addr.lower() in data_string.lower():
                target_ethernet_uri = uri
                target_ethernet_current_setting = data
                break

        nic_info = {}
        nic_info['nic_addr'] = target_ethernet_uri
        nic_info['ethernet_setting'] = target_ethernet_current_setting

        if target_ethernet_uri is None:
            return {}
        else:
            return nic_info

    def set_hostinterface_attributes(self, hostinterface_config, hostinterface_id=None):
        if hostinterface_config is None:
            return {'ret': False, 'msg':
                    'Must provide hostinterface_config for SetHostInterface command'}

        # Find the HostInterfaceCollection resource
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        hostinterfaces_uri = data.get("HostInterfaces", {}).get("@odata.id")
        if hostinterfaces_uri is None:
            return {'ret': False, 'msg': "HostInterface resource not found"}
        response = self.get_request(self.root_uri + hostinterfaces_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        uris = [a.get('@odata.id') for a in data.get('Members', []) if a.get('@odata.id')]

        # Capture list of URIs that match a specified HostInterface resource Id
        if hostinterface_id:
            matching_hostinterface_uris = [uri for uri in uris if hostinterface_id in uri.split('/')[-1]]
        if hostinterface_id and matching_hostinterface_uris:
            hostinterface_uri = list.pop(matching_hostinterface_uris)
        elif hostinterface_id and not matching_hostinterface_uris:
            return {'ret': False, 'msg': "HostInterface ID %s not present." % hostinterface_id}
        elif len(uris) == 1:
            hostinterface_uri = list.pop(uris)
        else:
            return {'ret': False, 'msg': "HostInterface ID not defined and multiple interfaces detected."}

        # Modify the HostInterface resource
        resp = self.patch_request(self.root_uri + hostinterface_uri, hostinterface_config, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified host interface'
        return resp

    def get_hostinterfaces(self):
        result = {}
        hostinterface_results = []
        properties = ['Id', 'Name', 'Description', 'HostInterfaceType', 'Status',
                      'InterfaceEnabled', 'ExternallyAccessible', 'AuthenticationModes',
                      'AuthNoneRoleId', 'CredentialBootstrapping']
        manager_uri_list = self.manager_uris
        for manager_uri in manager_uri_list:
            response = self.get_request(self.root_uri + manager_uri)
            if response['ret'] is False:
                return response

            result['ret'] = True
            data = response['data']
            hostinterfaces_uri = data.get("HostInterfaces", {}).get("@odata.id")
            if hostinterfaces_uri is None:
                continue

            response = self.get_request(self.root_uri + hostinterfaces_uri)
            data = response['data']

            if 'Members' in data:
                for hostinterface in data['Members']:
                    hostinterface_uri = hostinterface['@odata.id']
                    hostinterface_response = self.get_request(self.root_uri + hostinterface_uri)
                    # dictionary for capturing individual HostInterface properties
                    hostinterface_data_temp = {}
                    if hostinterface_response['ret'] is False:
                        return hostinterface_response
                    hostinterface_data = hostinterface_response['data']
                    for property in properties:
                        if property in hostinterface_data:
                            if hostinterface_data[property] is not None:
                                hostinterface_data_temp[property] = hostinterface_data[property]
                    # Check for the presence of a ManagerEthernetInterface
                    # object, a link to a _single_ EthernetInterface that the
                    # BMC uses to communicate with the host.
                    if 'ManagerEthernetInterface' in hostinterface_data:
                        interface_uri = hostinterface_data['ManagerEthernetInterface']['@odata.id']
                        interface_response = self.get_nic(interface_uri)
                        if interface_response['ret'] is False:
                            return interface_response
                        hostinterface_data_temp['ManagerEthernetInterface'] = interface_response['entries']

                    # Check for the presence of a HostEthernetInterfaces
                    # object, a link to a _collection_ of EthernetInterfaces
                    # that the host uses to communicate with the BMC.
                    if 'HostEthernetInterfaces' in hostinterface_data:
                        interfaces_uri = hostinterface_data['HostEthernetInterfaces']['@odata.id']
                        interfaces_response = self.get_request(self.root_uri + interfaces_uri)
                        if interfaces_response['ret'] is False:
                            return interfaces_response
                        interfaces_data = interfaces_response['data']
                        if 'Members' in interfaces_data:
                            for interface in interfaces_data['Members']:
                                interface_uri = interface['@odata.id']
                                interface_response = self.get_nic(interface_uri)
                                if interface_response['ret'] is False:
                                    return interface_response
                                # Check if this is the first
                                # HostEthernetInterfaces item and create empty
                                # list if so.
                                if 'HostEthernetInterfaces' not in hostinterface_data_temp:
                                    hostinterface_data_temp['HostEthernetInterfaces'] = []

                                hostinterface_data_temp['HostEthernetInterfaces'].append(interface_response['entries'])

                    hostinterface_results.append(hostinterface_data_temp)
            else:
                continue
        result["entries"] = hostinterface_results
        if not result["entries"]:
            return {'ret': False, 'msg': "No HostInterface objects found"}
        return result

    def get_manager_inventory(self, manager_uri):
        result = {}
        inventory = {}
        # Get these entries, but does not fail if not found
        properties = ['FirmwareVersion', 'ManagerType', 'Manufacturer', 'Model',
                      'PartNumber', 'PowerState', 'SerialNumber', 'Status', 'UUID']

        response = self.get_request(self.root_uri + manager_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for property in properties:
            if property in data:
                inventory[property] = data[property]

        result["entries"] = inventory
        return result

    def get_multi_manager_inventory(self):
        return self.aggregate_managers(self.get_manager_inventory)

    def set_session_service(self, sessions_config):
        if sessions_config is None:
            return {'ret': False, 'msg':
                    'Must provide sessions_config for SetSessionService command'}

        resp = self.patch_request(self.root_uri + self.session_service_uri, sessions_config, check_pyld=True)
        if resp['ret'] and resp['changed']:
            resp['msg'] = 'Modified session service'
        return resp

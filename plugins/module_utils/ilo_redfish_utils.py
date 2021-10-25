# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils


class iLORedfishUtils(RedfishUtils):

    def getiLOSessions(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        session_list = []
        sessions_results = []
        # Get these entries, but does not fail if not found
        properties = ['Description', 'Id', 'Name', 'UserName']

        # Changed self.sessions_uri to Hardcoded string.
        response = self.get_request(
            self.root_uri + self.service_root + "SessionService/Sessions/")
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if 'Oem' in data:
            result["entries"] = "HPE servers will not release session data"
            if data["Oem"]["Hpe"]["Links"]["MySession"]["@odata.id"]:
                current_session = data["Oem"]["Hpe"]["Links"]["MySession"]["@odata.id"]

        for sessions in data[u'Members']:
            # session_list[] are URIs
            session_list.append(sessions[u'@odata.id'])
        # for each session, get details
        for uri in session_list:
            session = {}
            if uri != current_session:
                response = self.get_request(self.root_uri + uri)
                if response['ret'] is False:
                    return response
                data = response['data']
                for property in properties:
                    if property in data:
                        session[property] = data[property]
                sessions_results.append(session)
        result["entries"] = sessions_results
        result["ret"] = True
        return result

    def get_Etherneturi(self):
        key = "EthernetInterfaces"

        response = self.get_request(self.root_uri + self.manager_uri)
        if(response['ret'] is False):
            return response

        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        EthernetInterface_uri = data[key]["@odata.id"]

        response = self.get_request(self.root_uri + EthernetInterface_uri)
        if response['ret'] is False:
            return response

        data = response['data']
        ethernetlist = []

        for ethernet in data[u'Members']:
            ethernetlist.append(ethernet[u'@odata.id'])

        return ethernetlist[0]

    def set_NTPServer(self, mgr_attributes):
        result = {}
        setkey = mgr_attributes['mgr_attr_name']

        ethuri = self.get_Etherneturi()

        response = self.get_request(self.root_uri + ethuri)
        if(response['ret'] is False):
            return response
        result['ret'] = True
        data = response['data']

        # enable_value = "false"

        payload = {"DHCPv4": {
            "UseNTPServers": ""
        }}

        if(data["DHCPv4"]["UseNTPServers"] is True):
            payload["DHCPv4"]["UseNTPServers"] = False
            resDHV4 = self.patch_request(self.root_uri + ethuri, payload)
            if resDHV4['ret'] is False:
                return resDHV4

        payload = {"DHCPv6": {
            "UseNTPServers": ""
        }}

        if(data["DHCPv6"]["UseNTPServers"] is True):
            payload["DHCPv6"]["UseNTPServers"] = False
            resDHV6 = self.patch_request(self.root_uri + ethuri, payload)
            if resDHV6['ret'] is False:
                return resDHV6

        DTuri = self.manager_uri + "DateTime"

        response = self.get_request(self.root_uri + DTuri)
        if(response['ret'] is False):
            return response

        data = response['data']

        NTPlist = data[setkey]
        if(len(NTPlist) == 2):
            NTPlist.pop(0)

        NTPlist.append(mgr_attributes['mgr_attr_value'])

        payload = {}
        payload[setkey] = NTPlist

        response1 = self.patch_request(self.root_uri + DTuri, payload)
        if response1['ret'] is False:
            return response1

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % mgr_attributes['mgr_attr_name']}

    def setTimeZone(self, attr):
        # result = {}
        key = attr['mgr_attr_name']

        uri = self.manager_uri + "DateTime/"
        response = self.get_request(self.root_uri + uri)
        if(response['ret'] is False):
            return response

        data = response["data"]

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        TimeZonelist = data["TimeZoneList"]
        index = ""

        for i in range(0, len(TimeZonelist)):
            if(attr['mgr_attr_value'] in TimeZonelist[i]["Name"]):
                index = TimeZonelist[i]["Index"]
                break

        payload = {key: {"Index": index}}
        # toset = "{\"Index\":" + str(index) + "}"

        # payload = {key: json.loads(toset)}

        response = self.patch_request(self.root_uri + uri, payload)
        if(response['ret'] is False):
            return response

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_DNSserver(self, attr):
        # result = {}
        key = attr['mgr_attr_name']
        # setkey = "Oem"

        uri = self.get_Etherneturi()

        response = self.get_request(self.root_uri + uri)
        if(response['ret'] is False):
            return response

        data = response['data']

        DNSlist = data["Oem"]["Hpe"]["IPv4"][key]

        if(len(DNSlist) == 3):
            DNSlist.pop(0)

        DNSlist.append(attr['mgr_attr_value'])

        payload = {
            "Oem": {
                "Hpe": {
                    "IPv4": {
                        key: DNSlist
                    }
                }
            }
        }

        response = self.patch_request(self.root_uri + uri, payload)
        if(response['ret'] is False):
            return response

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_DomainName(self, attr):
        key = attr['mgr_attr_name']

        Ethuri = self.get_Etherneturi()

        response = self.get_request(self.root_uri + Ethuri)
        if(response['ret'] is False):
            return response

        data = response['data']

        payload = {"DHCPv4": {
            "UseDomainName": ""
        }}

        if(data["DHCPv4"]["UseDomainName"] is True):
            payload["DHCPv4"]["UseDomainName"] = False
            resDHV4 = self.patch_request(self.root_uri + Ethuri, payload)
            if resDHV4['ret'] is False:
                return resDHV4

        payload = {"DHCPv6": {
            "UseDomainName": ""
        }}

        if(data["DHCPv6"]["UseDomainName"] is True):
            payload["DHCPv6"]["UseDomainName"] = False
            resDHV6 = self.patch_request(self.root_uri + Ethuri, payload)
            if resDHV6['ret'] is False:
                return resDHV6

        domain_name = attr['mgr_attr_value']

        payload = {}
        payload = {"Oem": {
            "Hpe": {
                key: domain_name
            }
        }}

        response = self.patch_request(self.root_uri + Ethuri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_WINSRegistration(self, mgrattr):
        Key = mgrattr['mgr_attr_name']

        Ethuri = self.get_Etherneturi()

        payload = {
            "Oem": {
                "Hpe": {
                    "IPv4": {
                        Key: False
                    }
                }
            }
        }

        response = self.patch_request(self.root_uri + Ethuri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % mgrattr['mgr_attr_name']}

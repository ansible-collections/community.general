# from re import S
from ansible.module_utils.redfish_utils import RedfishUtils
import json
# import os
# import os.path


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

    def save_biosconfig(self, id):
        result = self.aggregate(self.get_bios_attributes, id)
        # data = result["entries"][0][1]

        # with open("/home/bhavya/Documents/biosattr_data.json", "w") as outfile:
        #     json.dump(data, outfile)

        return result

    def load_biosconfig(self, id):

        result = {}
        key = "Bios"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uris[0], id)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        bios_uri = data[key]["@odata.id"]

        # Extract proper URI
        response = self.get_request(self.root_uri + bios_uri, id)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        set_bios_attr_uri = data["@Redfish.Settings"]["SettingsObject"]["@odata.id"]

        # f = open(home + "/biosattr_data.json", "r")
        f = ""
        response_attr = json.load(f)
        payload = {"Attributes": response_attr}

        response = self.patch_request(
            self.root_uri + set_bios_attr_uri, payload, id)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified BIOS attribute"}

    def ethernetInterfaceSave(self, id):
        result = {}

        ethuri = self.get_Etherneturi(id)
        response = self.get_request(self.root_uri + ethuri, id)
        if response['ret'] is False:
            return response
        result['ret'] = True
        # data = response['data']

        # with open(home + "/ethernetattr_data.json", "w") as outfile:
        #     json.dump(data, outfile)

        return result

    def ethernetInterfaceLoad(self, id):
        # result = {}

        ethuri = self.get_Etherneturi(id)
        f = ""
        # f = open(home+"/ethernetattr_data.json", "r")
        data = json.load(f)

        ReadOnly = ["@odata.context", "@odata.etag", "@odata.id", "@odata.type", "Id", "IPv6DefaultGateway", "LinkStatus",
                    "MaxIPv6StaticAddresses", "Name", "NameServers", "PermanentMACAddress", "UefiDevicePath", "VLANs", "Description", "IPv6Addresses"]

        ExceptionList = ["AutoNeg", "FQDN", "HostName", "LinkStatus", "MACAddress", "PermanentMACAddress", "SpeedMbps",
                         "Status", "FullDuplex", "IPv4Addresses", "IPv4StaticAddresses", "IPv6StaticAddresses", "IPv6StaticDefaultGateways"]
        OemHPE = ["@odata.context", "@odata.type", "ConfigurationSettings",
                  "InterfaceType", "NICSupportsIPv6", "DomainName", "HostName"]
        # To_rem = []

        payload = {"Oem": {"Hpe": {}}}
        # "AddressOrigin"

        for info in data:
            if info == "Oem":
                for test in data[info]["Hpe"]:
                    if test not in OemHPE:
                        payload[info]["Hpe"][test] = data[info]["Hpe"][test]

            elif info not in ReadOnly and info not in ExceptionList:
                payload[info] = data[info]

        # for info in payload:
        #     if info in To_rem:
        #         for i in range(len(data[info])):
        #             del payload[info][i]["Address"]

        for info in range(len(payload["Oem"]["Hpe"]["IPv6"]["StaticRoutes"])):
            del payload["Oem"]["Hpe"]["IPv6"]["StaticRoutes"][info]["Status"]

        for info in payload:
            if info == "DHCPv6" or info == "DHCPv4":
                for life in payload[info]:
                    payload[info][life] = False

        if "OperatingMode" in payload["DHCPv6"]:
            del payload["DHCPv6"]["OperatingMode"]

        if "OperatingMode" in payload["DHCPv4"]:
            del payload["DHCPv4"]["OperatingMode"]

        # for info in payload:
        #     if info == "DHCPv6" or info == "DHCPv4":
        #         for life in payload[info]:
        #             if life == "OperatingMode":
        #                 del payload[info][life]

        # with open("/home/bhavya/Documents/datacheck_finaleth.json", "w") as outfile:
        #     json.dump(payload, outfile)

        response = self.patch_request(self.root_uri + ethuri, payload, id)

        if response['ret'] is False:
            return response

        return {'ret': True, 'changed': True, 'msg': "Loaded Ethernet Surface"}

    def get_SmartStorage(self, systems_uri, id):
        result = {}
        response = self.get_request(
            self.root_uri + systems_uri + "/SmartStorageConfig")
        if response['ret'] is False:
            return response
        result['ret'] = True
        # data = response['data']

        # with open(home+"/"+systems_uri+"/SS", "w") as outfile:
        #     json.dump(data, outfile)

        return result

    def SmartStorageSave(self, id):
        result = self.aggregate(self.get_SmartStorage, id)
        # data = result["entries"][0][1]

        # with open("/home/bhavya/Documents/SmartStorage_data.json", "w") as outfile:
        #     json.dump(data, outfile)

        return result

    def SmartStorageLoad(self, id):
        # result = {}
        # systems_uri = 1
        f = ""
        # f = open(home+"/"+systems_uri+"/SS", "r")
        response_attr = json.load(f)
        response = self.patch_request(
            self.root_uri + "/SmartStorageConfig/1", response_attr, id)

        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Loaded Smart Storage"}

    def DeleteAllUsers(self, id):
        account_collection_uri = self.root_uri + self.accounts_uri
        account_response = self.get_request(account_collection_uri, id)
        if account_response['ret'] is False:
            return account_response

        data = account_response["data"]

        for account in data["Members"]:
            payload = {}
            response = self.delete_request(
                self.root_uri + account["@odata.id"], payload, id)
            if(response['ret'] is False):
                return response

        return {'ret': True}

    def loadaccounts(self, keepexisting, default, id):
        # uri = self.root_uri + self.accounts_uri
        if keepexisting == 'N':
            # write the code to delete all users in the ilo
            response = self.DeleteAllUsers(id)
            if(response['ret'] is False):
                return response
            print("Delete users")

        fileob = open("/Github/ansible-ilorest-role/ansibleredfish_playbooks/User/acc_details.json", "r")
        response = json.load(fileob)
        for info in response:
            user = {"Oem": {"Hpe": {"Privileges": {}}}}
            if(info != "accounts" and response[info]["data"].get("UserName") != "Administrator"):
                user["username"] = response[info]["data"].get("UserName")
                user["userpswd"] = default
                user["roleid"] = response[info]["data"].get("RoleId")
                user["Oem"]["Hpe"]["Privileges"] = response[info]["data"].get(
                    "Oem").get("Hpe").get("Privileges")
                result = self.AddiLOuser(user, id)
                if(result['ret'] is False):
                    result['value'] = user
                    return result

        return {'ret': True}

    def AddiLOuser(self, user):
        uri = self.root_uri + self.accounts_uri

        payload = {"Oem": {"Hpe": {"Privileges": {}}}}

        response = self.get_request(uri)
        if response['ret'] is False:
            return response

        data = response["data"]
        if "Members" not in data:
            return {'ret': False, 'msg': 'Members not found'}

        for accounts_uri in data['Members']:
            acc_reponse = self.get_request(self.root_uri + accounts_uri["@odata.id"])
            if response['ret'] is False:
                return response
            if acc_reponse['data']['UserName'] == user['username']:
                return {'ret': False, 'msg': 'Account with this Username already exists'}

        if 'usrpriv' in user:
            payload["Oem"]["Hpe"]["Privileges"] = user['usrpriv']

        else:

            PRIVILEGE_DICT = {}

            if(user['roleid'].lower() == "administrator"):
                PRIVILEGE_DICT = {"iLOConfigPriv": True, "VirtualMediaPriv": True, "RemoteConsolePriv": True,
                                  "UserConfigPriv": True, "VirtualPowerAndResetPriv": True,
                                  "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                                  "HostStorageConfigPriv": True, "HostNICConfigPriv": True,
                                  "HostBIOSConfigPriv": True}

            elif(user['roleid'].lower() == "readonly"):
                PRIVILEGE_DICT = {"iLOConfigPriv": False, "VirtualMediaPriv": False, "RemoteConsolePriv": False,
                                  "UserConfigPriv": False, "VirtualPowerAndResetPriv": False,
                                  "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                                  "HostStorageConfigPriv": False, "HostNICConfigPriv": False,
                                  "HostBIOSConfigPriv": False}

            elif(user['roleid'].lower() == "operator"):
                PRIVILEGE_DICT = {"iLOConfigPriv": False, "VirtualMediaPriv": True, "RemoteConsolePriv": True,
                                  "UserConfigPriv": False, "VirtualPowerAndResetPriv": True,
                                  "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                                  "HostStorageConfigPriv": True, "HostNICConfigPriv": True,
                                  "HostBIOSConfigPriv": True}

            for priv in PRIVILEGE_DICT:
                payload["Oem"]["Hpe"]["Privileges"][priv] = PRIVILEGE_DICT[priv]

        payload["UserName"] = user['username']
        payload["Password"] = user['userpswd']
        payload["RoleId"] = user['roleid']

        response = self.post_request(uri, payload)
        if(response['ret'] is False):
            response['value'] = payload
            return response

        return {'ret': True}

    def DeliLOuser(self, user_to_delete):
        account_collection_uri = self.root_uri + self.accounts_uri
        # print(account_collection_uri)
        account_response = self.get_request(account_collection_uri)
        if account_response['ret'] is False:
            return account_response
        # print(account_response)
        data = account_response["data"]

        uri_to_del = None

        for account in data["Members"]:
            response = self.get_request(self.root_uri + account["@odata.id"])
            # print(response)
            account_data = response['data']
            if(account_data["UserName"] == user_to_delete):
                uri_to_del = account["@odata.id"]
                break

        if not uri_to_del:
            return {'ret': False, 'msg': "No account found"}

        payload = {}

        del_uri = self.root_uri + uri_to_del

        response = self.delete_request(del_uri, payload)
        if(response['ret'] is False):
            return response

        return {'ret': True}

    def UpdateiLOpass(self, user):

        account_collection_uri = self.root_uri + self.accounts_uri
        account_response = self.get_request(account_collection_uri)
        if account_response['ret'] is False:
            return account_response
        data = account_response["data"]

        uri_for_pass = ""

        for account in data["Members"]:
            response = self.get_request(self.root_uri + account["@odata.id"])
            # print(response)
            account_data = response['data']
            if(account_data["UserName"] == user['username']):
                uri_for_pass = account["@odata.id"]
                break

        uri = self.root_uri + uri_for_pass
        payload = {'Password': user['userpswd']}

        response = self.patch_request(uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True}

    def UpdateiLOUserRole(self, user):

        account_collection_uri = self.root_uri + self.accounts_uri
        account_response = self.get_request(account_collection_uri)
        if account_response['ret'] is False:
            return account_response
        data = account_response["data"]

        uri_for_role = ""

        for account in data["Members"]:
            response = self.get_request(self.root_uri + account["@odata.id"])
            account_data = response['data']
            if(account_data["UserName"] == user['username']):
                uri_for_role = account["@odata.id"]
                break

        uri = self.root_uri + uri_for_role

        PRIVILEGE_DICT = {}
        if(user['roleid'] == "Administrator"):
            PRIVILEGE_DICT = {"iLOConfigPriv": True, "VirtualMediaPriv": True, "RemoteConsolePriv": True,
                              "UserConfigPriv": True, "VirtualPowerAndResetPriv": True,
                              "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                              "HostStorageConfigPriv": True, "HostNICConfigPriv": True,
                              "HostBIOSConfigPriv": True}

        elif(user['roleid'] == "ReadOnly"):
            PRIVILEGE_DICT = {"iLOConfigPriv": False, "VirtualMediaPriv": False, "RemoteConsolePriv": False,
                              "UserConfigPriv": False, "VirtualPowerAndResetPriv": False,
                              "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                              "HostStorageConfigPriv": False, "HostNICConfigPriv": False,
                              "HostBIOSConfigPriv": False}

        elif(user['roleid'] == "Operator"):
            PRIVILEGE_DICT = {"iLOConfigPriv": False, "VirtualMediaPriv": True, "RemoteConsolePriv": True,
                              "UserConfigPriv": False, "VirtualPowerAndResetPriv": True,
                              "SystemRecoveryConfigPriv": False, "LoginPriv": True,
                              "HostStorageConfigPriv": True, "HostNICConfigPriv": True,
                              "HostBIOSConfigPriv": True}

        payload = {"Oem": {"Hpe": {"Privileges": {}}}}
        for priv in PRIVILEGE_DICT:
            payload["Oem"]["Hpe"]["Privileges"][priv] = PRIVILEGE_DICT[priv]

        payload["RoleId"] = user['roleid']

        response = self.patch_request(uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True}

    def accountSave(self, id):
        result = {}
        user_list = []
        totalaccdetails = {}
        # listing all users has always been slower than other operations, why?
        # Get these entries, but does not fail if not found
        response = self.get_request(self.root_uri + self.accounts_uri, id)
        totalaccdetails["accounts"] = response

        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for users in data["Members"]:
            user_list.append(users[u'@odata.id'])

        for uri in user_list:
            # user = {}
            response = self.get_request(self.root_uri + uri, id)
            if response['ret'] is False:
                return response
            totalaccdetails[response['data']['Id']] = response
            data = response['data']

        with open("/Github/ansible-ilorest-role/ansibleredfish_playbooks/User/acc_details.json", "w") as outfile:
            json.dump(totalaccdetails, outfile)

        return result

    def list_iLOusers(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        user_list = []
        users_results = []
        # Get these entries, but does not fail if not found
        properties = ['Id', 'Name', 'UserName', 'RoleId']

        response = self.get_request(self.root_uri + self.accounts_uri)
        # with open('acc_details.json', 'w') as outfile:
        #     json.dump(response, outfile)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for users in data[u'Members']:
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

    def set_VLANId(self, attr):
        result = {}
        setkey = "VLAN"

        uri = self.get_Etherneturi()

        response = self.get_request(self.root_uri + uri)
        if(response['ret'] is False):
            return response
        result['ret'] = True
        data = response['data']

        if(setkey not in data):
            return {'ret': False, 'msg': "Key %s not found" % setkey}

        mgr_attr = attr['mgr_attr_name']
        mgr_value = attr['mgr_attr_value']
        enable_value = "True"

        if(data['VLAN']['VLANEnable'] is False):
            toset = "{\"VLANEnable\" : \"" + enable_value + \
                "\",\"" + mgr_attr + "\":" + mgr_value + "}"

        else:
            toset = "{\"" + mgr_attr + "\":" + mgr_value + "}"

        info = json.loads(toset)
        info["VLANEnable"] = True

        payload = {setkey: info}

        response = self.patch_request(self.root_uri + uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

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

    def set_HostName(self, mgrattr):

        Key = mgrattr['mgr_attr_name']

        Ethuri = self.get_Etherneturi()

        payload = {
            "Oem": {
                "Hpe": {
                    Key: mgrattr['mgr_attr_value']
                }
            }
        }

        response = self.patch_request(self.root_uri + Ethuri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % mgrattr['mgr_attr_name']}
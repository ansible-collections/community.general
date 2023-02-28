# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.basic import missing_required_lib

import os
import re
import traceback

HAS_IPADDRESS = True
IPADDRESS_IMP_ERR = None
try:
    import ipaddress
except ImportError as e:
    IPADDRESS_IMP_ERR = traceback.format_exc()
    HAS_IPADDRESS = False

HAS_URLLIB3 = True
URLLIB3_IMP_ERR = None
try:
    import urllib3
except ImportError as e:
    URLLIB3_IMP_ERR = traceback.format_exc()
    HAS_URLLIB3 = False


def ilo_certificate_login(root_uri, module, cert_file, key_file):
    if not os.path.exists(cert_file):
        module.fail_json(msg="The client cert file does not exist in the provided path %s" % str(cert_file))

    if not os.path.exists(key_file):
        module.fail_json(msg="The client key file does not exist in the provided path %s" % str(key_file))

    try:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', cert_file=cert_file, key_file=key_file)
        cert_login = http.request('GET', root_uri + "/html/login_cert.html")
    except Exception as e:
        module.fail_json(msg="Server login with certificates failed: %s" % str(e))

    return cert_login.getheader('X-Auth-Token')


class iLORedfishUtils(RedfishUtils):

    def __init__(self, creds, root_uri, timeout, module):
        super().__init__(creds, root_uri, timeout, module)

        if not HAS_IPADDRESS:
            self.module.fail_json(msg=missing_required_lib('ipaddress'), exception=IPADDRESS_IMP_ERR)

        if not HAS_URLLIB3:
            self.module.fail_json(msg=missing_required_lib('urllib3'), exception=URLLIB3_IMP_ERR)

    def get_ilo_sessions(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        session_list = []
        sessions_results = []
        # Get these entries, but does not fail if not found
        properties = ['Description', 'Id', 'Name', 'UserName']

        # Changed self.sessions_uri to Hardcoded string.
        response = self.get_request(
            self.root_uri + self.service_root + "SessionService/Sessions/")
        if not response['ret']:
            return response
        result['ret'] = True
        data = response['data']

        if 'Oem' in data:
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
                if not response['ret']:
                    return response
                data = response['data']
                for property in properties:
                    if property in data:
                        session[property] = data[property]
                sessions_results.append(session)
        result["msg"] = sessions_results
        result["ret"] = True
        return result

    def get_network_boot_settings(self):
        # This method returns network boot settings present in the OOB controller
        result = {}

        uri = self.root_uri + self.service_root + self.systems_uri + "bios/"
        response = self.get_request(uri)
        if not response["ret"]:
            return response

        data = response["data"]

        if 'Oem' in data and 'Hpe' in data["Oem"] and 'Links' in data['Oem']['Hpe'] and 'Boot' in \
                data['Oem']['Hpe']['Links']:
            uri = data['Oem']['Hpe']['Links']['Boot']['@odata.id'] + "settings/"
            response = self.get_request(self.root_uri + uri)
            if not response["ret"]:
                return response
            result["ret"] = True
            self.remove_odata(response)
            result["msg"] = self.remove_odata(response["data"])
        else:
            return {
                "ret": False,
                "msg": "Boot settings uri not found in %s response, %s" % (uri, data)
            }

        return result

    def get_smartstorage_physical_drives(self):
        # This method returns list of physical drives present in the OOB controller
        physical_drives = {}
        physical_drives_count = 0
        result = {}

        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri + "SmartStorage/ArrayControllers/")

        if not response["ret"]:
            return response

        data = response["data"]
        if data["Members@odata.count"] == 0:
            # return physical_drives, physical_drives_count
            result["physical_drives"] = {}
            result["physical_drives_count"] = 0
            return {
                "ret": True,
                "msg": result
            }

        # Get Members of ArrayControllers
        for mem in data["Members"]:
            physical_drive_list = []
            array_url = mem["@odata.id"]
            response = self.get_request(
                self.root_uri + mem["@odata.id"]
            )

            if not response["ret"]:
                return response

            data = response["data"]
            if 'Links' in data and 'PhysicalDrives' in data['Links']:
                log_url = data['Links']['PhysicalDrives']['@odata.id']
            elif 'links' in data and 'PhysicalDrives' in data['links']:
                log_url = data['links']['PhysicalDrives']['href']
            else:
                return {
                    "ret": False,
                    "msg": "Physical drive URI not found in %s response: %s" % (mem["@odata.id"], data)
                }

            # Get list of physical drives URI
            response = self.get_request(
                self.root_uri + log_url
            )

            if not response["ret"]:
                return response

            json_data = response["data"]
            for entry in json_data["Members"]:
                # Get each physical drives details
                response = self.get_request(
                    self.root_uri + entry["@odata.id"]
                )

                if not response["ret"]:
                    return response

                log_data = self.remove_odata(response["data"])
                physical_drive_list.append(log_data)
            physical_drives.update({"array_controller_" + str(array_url.split("/")[-2]): physical_drive_list})
            physical_drives_count = physical_drives_count + len(physical_drive_list)
            result["physical_drives"] = physical_drives
            result["physical_drives_count"] = physical_drives_count

        return {
            "msg": result,
            "ret": True
        }
        # return result

    def get_smartstorage_logical_drives(self, array_controllers=False):
        # This method returns the logical drives details
        logical_drives_details = []
        if array_controllers:
            logical_drives = {}
            logical_drives_count = 0

        result = {}

        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        url = self.root_uri + self.systems_uri + "SmartStorage/"
        response = self.get_request(url)
        if not response["ret"]:
            return response

        json_data = response["data"]
        # Getting Array Controllers details
        if "ArrayControllers" not in json_data["Links"]:
            return {
                "ret": False,
                "msg": "Array Controllers data not found in %s response: %s" % (url, str(json_data))
            }

        response = self.get_request(
            self.root_uri + json_data["Links"]["ArrayControllers"]["@odata.id"]
        )
        if not response["ret"]:
            return response

        json_data = response["data"]

        # Getting details for each member in Array Controllers
        for entry in json_data["Members"]:
            array_url = entry["@odata.id"]
            log = self.get_request(
                self.root_uri + entry["@odata.id"]
            )
            if not response["ret"]:
                return response
            log_details = log["data"]

            # Getting logical drives details
            if "LogicalDrives" not in log_details["Links"]:
                return {
                    "ret": False,
                    "msg": "Logical Drives URI not found in %s response: %s" % (entry["@odata.id"], str(log_details))
                }

            response = self.get_request(
                self.root_uri + log_details["Links"]["LogicalDrives"]["@odata.id"]
            )
            if not response["ret"]:
                return response

            logicalDrivesData = response["data"]

            # Getting details for each member in Logical Drives
            for member in logicalDrivesData["Members"]:
                response = self.get_request(
                    self.root_uri + member["@odata.id"]
                )
                if not response["ret"]:
                    return response
                member_data = self.remove_odata(response["data"])

                # Getting data drives details
                if "DataDrives" not in member_data["Links"]:
                    return {
                        "ret": False,
                        "msg": "Physical Drives information not found in %s response: %s" % (
                            member["@odata.id"], str(member_data))
                    }

                member_data["data_drives"] = []
                response = self.get_request(
                    self.root_uri + member_data["Links"]["DataDrives"]["@odata.id"]
                )
                if not response["ret"]:
                    return response
                data_drive_res = response["data"]

                # Getting details for each member in Data Drives
                for mem in data_drive_res["Members"]:
                    response = self.get_request(
                        self.root_uri + mem["@odata.id"]
                    )
                    if not response["ret"]:
                        return response
                    data_drive_member_details = self.remove_odata(response["data"])
                    member_data["data_drives"].append(data_drive_member_details)
                logical_drives_details.append(member_data)
            if array_controllers:
                logical_drives.update({"array_controller_" + str(array_url.split("/")[-2]): logical_drives_details})
                logical_drives_count = logical_drives_count + len(logical_drives_details)
                result["logical_drives"] = logical_drives
                result["logical_drives_count"] = logical_drives_count
                # result["ret"] = True
                return {
                    "msg": result,
                    "ret": True
                }
            # return result

        result["logical_drives_details"] = logical_drives_details
        # result["ret"] = True
        return {
            "msg": result,
            "ret": True
        }
        # return result

    def remove_odata(self, output):
        # Remove odata variables given in the list
        remove_list = ["@odata.context", "@odata.etag", "@odata.id", "@odata.type"]
        for key in remove_list:
            if key in output:
                output.pop(key)
        return output

    def set_ntp_server(self, mgr_attributes):
        result = {}
        setkey = mgr_attributes['mgr_attr_name']

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        response = self.get_request(self.root_uri + ethuri)
        if not response['ret']:
            return response
        result['ret'] = True
        data = response['data']
        payload = {"DHCPv4": {
            "UseNTPServers": ""
        }}

        if data["DHCPv4"]["UseNTPServers"]:
            payload["DHCPv4"]["UseNTPServers"] = False
            res_dhv4 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv4['ret']:
                return res_dhv4

        payload = {"DHCPv6": {
            "UseNTPServers": ""
        }}

        if data["DHCPv6"]["UseNTPServers"]:
            payload["DHCPv6"]["UseNTPServers"] = False
            res_dhv6 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv6['ret']:
                return res_dhv6

        datetime_uri = self.manager_uri + "DateTime"

        response = self.get_request(self.root_uri + datetime_uri)
        if not response['ret']:
            return response

        data = response['data']

        ntp_list = data[setkey]
        if len(ntp_list) == 2:
            ntp_list.pop(0)

        ntp_list.append(mgr_attributes['mgr_attr_value'])

        payload = {setkey: ntp_list}

        response1 = self.patch_request(self.root_uri + datetime_uri, payload)
        if not response1['ret']:
            return response1

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % mgr_attributes['mgr_attr_name']}

    def set_time_zone(self, attr):
        key = attr['mgr_attr_name']

        uri = self.manager_uri + "DateTime/"
        response = self.get_request(self.root_uri + uri)
        if not response['ret']:
            return response

        data = response["data"]

        if key not in data:
            return {'ret': False, 'changed': False, 'msg': "Key %s not found" % key}

        timezones = data["TimeZoneList"]
        index = ""
        for tz in timezones:
            if attr['mgr_attr_value'] in tz["Name"]:
                index = tz["Index"]
                break

        payload = {key: {"Index": index}}
        response = self.patch_request(self.root_uri + uri, payload)
        if not response['ret']:
            return response

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_dns_server(self, attr):
        key = attr['mgr_attr_name']
        nic_info = self.get_manager_ethernet_uri()
        uri = nic_info["nic_addr"]

        response = self.get_request(self.root_uri + uri)
        if not response['ret']:
            return response

        data = response['data']

        dns_list = data["Oem"]["Hpe"]["IPv4"][key]

        if len(dns_list) == 3:
            dns_list.pop(0)

        dns_list.append(attr['mgr_attr_value'])

        payload = {
            "Oem": {
                "Hpe": {
                    "IPv4": {
                        key: dns_list
                    }
                }
            }
        }

        response = self.patch_request(self.root_uri + uri, payload)
        if not response['ret']:
            return response

        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_domain_name(self, attr):
        key = attr['mgr_attr_name']

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        response = self.get_request(self.root_uri + ethuri)
        if not response['ret']:
            return response

        data = response['data']

        payload = {"DHCPv4": {
            "UseDomainName": ""
        }}

        if data["DHCPv4"]["UseDomainName"]:
            payload["DHCPv4"]["UseDomainName"] = False
            res_dhv4 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv4['ret']:
                return res_dhv4

        payload = {"DHCPv6": {
            "UseDomainName": ""
        }}

        if data["DHCPv6"]["UseDomainName"]:
            payload["DHCPv6"]["UseDomainName"] = False
            res_dhv6 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv6['ret']:
                return res_dhv6

        domain_name = attr['mgr_attr_value']

        payload = {"Oem": {
            "Hpe": {
                key: domain_name
            }
        }}

        response = self.patch_request(self.root_uri + ethuri, payload)
        if not response['ret']:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % attr['mgr_attr_name']}

    def set_wins_registration(self, mgrattr):
        Key = mgrattr['mgr_attr_name']

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        payload = {
            "Oem": {
                "Hpe": {
                    "IPv4": {
                        Key: False
                    }
                }
            }
        }

        response = self.patch_request(self.root_uri + ethuri, payload)
        if not response['ret']:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified %s" % mgrattr['mgr_attr_name']}

    def verify_smartstorage_drive_count(self, raid_details, logical_drives_count):
        if len(raid_details) != logical_drives_count:
            return {
                "ret": False,
                "changed": False,
                "msg": "Logical drive count in raid details is not matching with logical drives present in the server"
            }
        return {
            "ret": True,
            "msg": "Drive count is same as input"
        }

    def verify_smartstorage_logical_drives(self, raid_details, check_length=False):
        # This method verifies logical drives present in the OOB controller against the provided input
        result = self.get_smartstorage_logical_drives()
        if not result["ret"]:
            return result

        logical_drives_details = result["msg"]["logical_drives_details"]
        logical_drives_count = int(len(logical_drives_details))
        if check_length:
            response = self.verify_smartstorage_drive_count(raid_details, logical_drives_count)
            if not response["ret"]:
                return response

        not_available = []
        for raid in raid_details:
            flag = False
            for drive in logical_drives_details:
                if drive["LogicalDriveName"] == raid["LogicalDriveName"]:
                    if ("Raid" + drive["Raid"]) != raid["Raid"]:
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Verification Failed! Raid type mismatch in %s" % drive["LogicalDriveName"]
                        }
                    if len(drive["data_drives"]) != raid["DataDrives"]["DataDriveCount"]:
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Verification Failed! Physical drive count mismatch in %s" % drive[
                                "LogicalDriveName"]
                        }
                    if drive["MediaType"] != raid["DataDrives"]["DataDriveMediaType"]:
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Verification Failed! Media Type mismatch in %s" % drive["LogicalDriveName"]
                        }
                    if drive["InterfaceType"] != raid["DataDrives"]["DataDriveInterfaceType"]:
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Verification Failed! Interface Type mismatch in %s" % drive["LogicalDriveName"]
                        }
                    for data_drive in drive["data_drives"]:
                        if data_drive["CapacityGB"] < raid["DataDrives"]["DataDriveMinimumSizeGiB"]:
                            return {
                                "ret": False,
                                "changed": False,
                                "msg": "Verification Failed! Data Drive minimum size is not satisfied in %s" % drive[
                                    "LogicalDriveName"]
                            }
                    flag = True
            if not flag:
                not_available.append(raid["LogicalDriveName"])
        if not_available:
            return {
                "ret": False,
                "changed": False,
                "msg": "Verification Failed! Logical drives are not matching: %s" % not_available
            }
        else:
            return {
                "ret": True,
                "changed": False,
                "msg": "Logical drives verification completed"
            }

    def verify_uefi_boot_order(self, uefi_boot_order):
        # This method verifies UEFI boot order present in the OOB controller against the provided input
        input_boot_order = uefi_boot_order

        # response = self.get_bios_attributes()
        response = self.get_multi_bios_attributes()

        if not response["ret"]:
            return response

        if response["entries"][0][1]["BootMode"].lower() != "uefi":
            return {
                "ret": False,
                "changed": False,
                "msg": "Server Boot Mode is not UEFI. Hence Boot Order can't be verified"
            }

        response = self.get_network_boot_settings()
        if not response["ret"]:
            return response
        server_boot_order = response["msg"]["PersistentBootConfigOrder"]

        if len(server_boot_order) < len(input_boot_order):
            return {
                "ret": False,
                "changed": False,
                "msg": "Lesser number of elements in Server Boot Order %s than Input Boot Order %s" % (str(len(server_boot_order)), str(len(input_boot_order)))
            }

        for i in range(0, len(input_boot_order)):
            if input_boot_order[i].lower() != server_boot_order[i].lower():
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Input Boot Order %s doesn't match with Server Boot Order %s" % (str(input_boot_order), str(server_boot_order))
                }
        return {
            "ret": True,
            "changed": False,
            "msg": "Input Boot Order matches with the Server Boot Order"
        }

    def delete_all_smartstorage_logical_drives(self):
        # This function deletes all the logical drives
        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        response = self.get_smartstorage_logical_drives()
        if not response["ret"]:
            return response

        if not response["msg"]["logical_drives_details"]:
            return {
                "ret": True,
                "changed": False,
                "msg": "No logical drives present on the server"
            }

        payload = {"LogicalDrives": [], "DataGuard": "Disabled"}

        smartstorageconfig_settings_uri = self.root_uri + self.systems_uri + "smartstorageconfig/settings/"
        response = self.put_request(smartstorageconfig_settings_uri, payload)

        if not response["ret"]:
            return response

        return {
            "ret": True,
            "changed": True,
            "msg": "Delete logical drives request sent. System Reset required."
        }

    def get_unused_smartstorage_drives(self):
        # This function fetches the unconfigured drives
        unused_physical_drives = []

        # Getting smart storage details
        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri + "SmartStorage/")
        if not response["ret"]:
            return response

        json_data = response["data"]
        uri = self.systems_uri + "SmartStorage/"

        # Getting Array Controllers details
        if "ArrayControllers" not in json_data["Links"]:
            return {
                "ret": False,
                "changed": False,
                "msg": "Array Controllers data not found in %s response: %s" % (uri, str(json_data))
            }

        response = self.get_request(self.root_uri + json_data["Links"]["ArrayControllers"]["@odata.id"])

        if not response["ret"]:
            return response

        json_data = response["data"]

        # Getting details for each member in Array Controllers
        for entry in json_data["Members"]:
            log = self.get_request(self.root_uri + entry["@odata.id"])
            if not log["ret"]:
                return log

            log_details = log["data"]

            response = self.get_request(self.root_uri + log_details["Links"]["UnconfiguredDrives"]["@odata.id"])
            if not response["ret"]:
                return response

            json_data = response["data"]
            for entry in json_data["Members"]:
                # Get each physical drives details
                log = self.get_request(self.root_uri + entry["@odata.id"])
                if not log["ret"]:
                    return log

                unused_physical_drives.append(log["data"])

        return {
            "ret": True,
            "changed": False,
            "unused_physical_drives": unused_physical_drives
        }

    def validation_error(self, raid, input_list, missing_param, not_defined, drive_input, command="CreateSmartStorageLogicalDrives"):
        # This function returns error messages for invalid inputs passed to the
        # CreateLogicalDrives and CreateLogicalDrivesWithPArticularPhysicalDrives modules
        if command == "CreateSmartStorageLogicalDrives":
            if missing_param:
                msg = "Input parameters %s are missing to create logical drive. " + \
                      "Mandatory parameters are %s and in data drive details: %s"
                return {
                    "ret": False,
                    "changed": False,
                    "msg": msg % (str(missing_param), str(input_list), str(drive_input))
                }

            if set(raid.keys()) - set(input_list):
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Unsupported input parameters: %s" % str(list(set(raid.keys()) - set(input_list)))
                }

            if set(raid["DataDrives"].keys()) - set(drive_input):
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Unsupported input parameters in data drive details: %s" % str(
                        list(set(raid["DataDrives"].keys()) - set(drive_input)))
                }

            if not_defined:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Input parameters %s should not be empty" % (str(not_defined))
                }

            return {
                "ret": True,
                "changed": False,
                "msg": "Input parameters verified"
            }

        elif command == "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives":
            msg = "Input parameters %s are missing to create logical drive. " + \
                  "Mandatory parameters are %s "
            if missing_param:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": msg % (str(missing_param), str(input_list))
                }

            if set(raid.keys()) - set(input_list):
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Unsupported input parameters: %s" % str(list(set(raid.keys()) - set(input_list)))
                }

            if not_defined:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Input parameters %s should not be empty" % (str(not_defined))
                }

            return {
                "ret": True,
                "changed": False,
                "msg": "Input parameters verified"
            }

    def verify_input_paramters(self, raid_data, command="CreateSmartStorageLogicalDrives"):
        # Verifying input parameters passed to the CreateLogicalDrives and
        # CreateLogicalDrivesWithPArticularPhysicalDrives modules
        if command == "CreateLogicalDrives":
            input_list = ['LogicalDriveName', 'Raid', 'DataDrives']
            drive_input = ['DataDriveCount', 'DataDriveMediaType',
                           'DataDriveInterfaceType', 'DataDriveMinimumSizeGiB']
            for raid in raid_data:
                missing_param = []
                not_defined = []
                for input in input_list:
                    if input not in raid.keys():
                        missing_param.append(input)
                    elif not raid[input]:
                        not_defined.append(input)

                if 'DataDrives' not in raid.keys():
                    missing_param = missing_param + drive_input
                else:
                    for drive in drive_input:
                        if drive not in raid["DataDrives"]:
                            missing_param.append(drive)
                        elif drive != "DataDriveMinimumSizeGiB" and not raid["DataDrives"][drive]:
                            not_defined.append(drive)
                        elif drive == "DataDriveMinimumSizeGiB" and \
                                not raid["DataDrives"]["DataDriveMinimumSizeGiB"] and \
                                raid["DataDrives"]["DataDriveMinimumSizeGiB"] != 0:
                            not_defined.append(drive)

            return self.validation_error(raid, input_list, missing_param, not_defined, drive_input)

        elif command == "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives":
            input_list = ['LogicalDriveName', 'CapacityGB', 'Raid', 'DataDrives']

            for raid in raid_data:
                missing_param = []
                not_defined = []
                for input in input_list:
                    if input not in raid.keys():
                        missing_param.append(input)
                    elif not raid[input]:
                        not_defined.append(input)

            return self.validation_error(raid, input_list, missing_param, not_defined, [], command="CreateLogicalDrivesWithParticularPhysicalDrives")

    def check_smartstorage_physical_drives(self, raid_data, unused_physical_drives, command="CreateSmartStorageLogicalDrives"):
        # Checking and verifying physical drives present in the OOB controller for the
        # CreateLogicalDrives and CreateLogicalDrivesWithPArticularPhysicalDrives modules
        if command == "CreateSmartStorageLogicalDrives":
            raid_data = sorted(raid_data, key=lambda i: i['DataDrives']['DataDriveMinimumSizeGiB'])
            unused_physical_drives = sorted(unused_physical_drives, key=lambda i: i['CapacityGB'])
            for raid in raid_data:
                for i in range(0, int(raid["DataDrives"]["DataDriveCount"])):
                    flag = False
                    unused_drives = unused_physical_drives[:]
                    for phy in unused_physical_drives:
                        if raid["DataDrives"]["DataDriveMediaType"] == phy["MediaType"] and \
                                raid["DataDrives"]["DataDriveInterfaceType"] == phy["InterfaceType"] and \
                                int(raid["DataDrives"]["DataDriveMinimumSizeGiB"]) <= int(phy["CapacityGB"]) * 0.931323:
                            unused_drives.remove(phy)
                            flag = True
                            break
                    if not flag:
                        result = "failed"
                    else:
                        result = unused_drives

                    if str(result) == "failed":
                        msg = "Free physical drive not found with media type: %s," + \
                              " interface type: %s, and minimum capacity: %s"
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": msg % (
                                raid["DataDrives"]["DataDriveMediaType"], raid["DataDrives"]["DataDriveInterfaceType"],
                                str(raid["DataDrives"]["DataDriveMinimumSizeGiB"]))
                        }
                    unused_physical_drives = result

            return {
                "ret": True,
                "changed": False,
                "msg": "Physical drives verified"
            }

        elif command == "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives":
            for raid in raid_data:
                capacity = 0
                for drive in raid["DataDrives"]:
                    for unused_drive in unused_physical_drives:
                        if drive == unused_drive["Location"]:
                            capacity = capacity + unused_drive["CapacityGB"]
                if capacity < raid["CapacityGB"]:
                    return {
                        "ret": False,
                        "changed": False,
                        "msg": "The physical drives provided do not satisfy the capacity provided"
                    }

            return {
                "ret": True,
                "changed": False,
                "msg": "Physical drives verified"
            }

    def check_smartstorage_logical_drives(self, raid, logical_drives_details, command="CreateSmartStorageLogicalDrives"):
        # Checking and verifying logical drives present in the OOB controller for the CreateLogicalDrives
        # and CreateLogicalDrivesWithPArticularPhysicalDrives module
        if command == "CreateSmartStorageLogicalDrives":
            for drive in logical_drives_details:
                if drive["LogicalDriveName"] == raid["LogicalDriveName"]:
                    if ("Raid" + drive["Raid"]) != raid["Raid"] or \
                            len(drive["data_drives"]) != raid["DataDrives"]["DataDriveCount"] or \
                            drive["MediaType"] != raid["DataDrives"]["DataDriveMediaType"] or \
                            drive["InterfaceType"] != raid["DataDrives"]["DataDriveInterfaceType"]:
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Already logical drive exists with same name: '%s', but different details" % str(
                                drive["LogicalDriveName"])
                        }

                    for data_drive in drive["data_drives"]:
                        if int(data_drive["CapacityGB"]) * 0.931323 < raid["DataDrives"]["DataDriveMinimumSizeGiB"]:
                            return {
                                "ret": False,
                                "changed": False,
                                "msg": "Already logical drive exists with same name: '%s', but different details" % str(
                                    drive["LogicalDriveName"])
                            }

                    return {
                        "ret": True,
                        "changed": False,
                        "msg": "Logical drive provided is present in server"
                    }

            return {
                "ret": False,
                "changed": False,
                "msg": "Logical drive provided is not present in server"
            }

        elif command == "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives":
            for drive in logical_drives_details:
                if drive["LogicalDriveName"] == raid["LogicalDriveName"]:
                    if ("Raid" + drive["Raid"]) != raid["Raid"] or \
                            len(drive["data_drives"]) != len(raid["DataDrives"]):
                        return {
                            "ret": False,
                            "changed": False,
                            "msg": "Already logical drive exists with same name: '%s', but different details" % str(
                                drive["LogicalDriveName"])
                        }

                    for data_drive in drive["data_drives"]:
                        if int(data_drive["CapacityGB"]) * 0.931323 < raid["CapacityGB"]:
                            return {
                                "ret": False,
                                "changed": False,
                                "msg": "Already logical drive exists with same name: '%s', but different details" % str(
                                    drive["LogicalDriveName"])
                            }

                    return {
                        "ret": True,
                        "changed": False,
                        "msg": "Logical drive provided is present in server"
                    }

            return {
                "ret": False,
                "changed": False,
                "msg": "Logical drive provided is not present in server"
            }

    def check_smartstorage_physical_drive_count(self, raid_data, unused_physical_drives, command="CreateSmartStorageLogicalDrives"):
        # Check physical drives are available in the OOB controller to create logical drives
        if command == "CreateSmartStorageLogicalDrives":
            needed_phy = 0
            for ld in raid_data:
                needed_phy = needed_phy + int(ld["DataDrives"]["DataDriveCount"])

            # Check available drives
            if not unused_physical_drives:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Free Physical drives are not available in the server"
                }

            if len(unused_physical_drives) < needed_phy:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Less number of Physical drives available in the server"
                }

            return {
                "ret": True,
                "changed": False,
                "msg": "Physical drive count verified"
            }

        elif command == "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives":
            needed_phy_drives = [drive for ld in raid_data for drive in ld["DataDrives"]]
            needed_phy = len(needed_phy_drives)

            # Check available drives
            if not unused_physical_drives:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Free Physical drives are not available in the server"
                }

            if len(unused_physical_drives) < needed_phy:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "Less number of Physical drives available in the server"
                }

            unused_physical_drives_locations = []
            for drive in unused_physical_drives:
                unused_physical_drives_locations.append(drive["Location"])

            for drive in needed_phy_drives:
                if drive not in unused_physical_drives_locations:
                    return {
                        "ret": False,
                        "changed": False,
                        "msg": "The drive %s is not free" % str(drive)
                    }

            return {
                "ret": True,
                "changed": False,
                "msg": "Physical drive count verified"
            }

    def verify_smartstorage_raid_details(self, raid_data):
        # Verifying raid details for CreateLogicalDrivesWithPArticularPhysicalDrives module
        data_drive_locations = []

        for raid in raid_data:
            for drive in raid["DataDrives"]:
                if drive in data_drive_locations:
                    return {
                        "ret": False,
                        "changed": False,
                        "msg": "Same Data Drive provided for multiple logical drives to be created, "
                               "a data drive can be given only once for any logical drive in raid_details"
                    }

                else:
                    data_drive_locations.append(drive)

        return {
            "ret": True,
            "changed": False,
            "msg": "RAID details verified"
        }

    def create_smartstorage_logical_drives(self, raid_data):
        # This function invokes the creation of logical drive.

        # verify input parameters
        response = self.verify_input_paramters(raid_data)
        if not response["ret"]:
            return response

        # Get logical drives from server
        logical_drives_details_response = self.get_smartstorage_logical_drives()
        if not logical_drives_details_response["ret"]:
            return logical_drives_details_response

        logical_drives_details = logical_drives_details_response["msg"]["logical_drives_details"]
        response = self.get_smartstorage_unused_drives()
        if not response["ret"]:
            return response

        unused_physical_drives = response["unused_physical_drives"]

        if logical_drives_details:
            raid_details = raid_data[:]
            for raid in raid_details:
                response = self.check_smartstorage_logical_drives(raid, logical_drives_details)
                if response["ret"]:
                    raid_data.remove(raid)
                elif not response["ret"] and response["msg"] != "Logical drive provided is not present in server":
                    return response

        if not raid_data:
            return {
                "ret": True,
                "changed": False,
                "msg": "Provided logical drives are already present in the server"
            }

        response = self.check_smartstorage_physical_drive_count(raid_data, unused_physical_drives)
        if not response["ret"]:
            return response

        response = self.check_smartstorage_physical_drives(raid_data, unused_physical_drives)
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri + "smartstorageconfig/")
        if not response["ret"]:
            return response

        storage_data = response["data"]

        ld_names = [i["LogicalDriveName"] for i in raid_data]
        LogicalDrives = storage_data["LogicalDrives"]
        body = {"LogicalDrives": LogicalDrives + raid_data, "DataGuard": "Permissive"}
        url = "smartstorageconfig/settings/"
        res = self.put_request(self.root_uri + self.systems_uri + url, body)

        if not res["ret"]:
            return res

        return {
            "ret": True,
            "changed": True,
            "msg": "Create logical drives request sent for %s. System Reset required." % str(ld_names)
        }

    def create_smartstorage_logical_drives_with_particular_physical_drives(self, raid_data):
        # This function invokes the creation of logical drive with paticular physical drives

        # verify input parameters
        response = self.verify_input_paramters(raid_data, "CreateLogicalDrivesWithParticularPhysicalDrives")
        if not response["ret"]:
            return response

        response = self.verify_smartstorage_raid_details(raid_data)
        if not response["ret"]:
            return response

        # Get logical drives from server
        logical_drives_details_response = self.get_smartstorage_logical_drives()
        if not logical_drives_details_response["ret"]:
            return logical_drives_details_response

        logical_drives_details = logical_drives_details_response["msg"]["logical_drives_details"]
        response = self.get_smartstorage_unused_drives()
        if not response["ret"]:
            return response

        unused_physical_drives = response["unused_physical_drives"]

        if logical_drives_details:
            raid_details = raid_data[:]
            for raid in raid_details:
                response = self.check_smartstorage_logical_drives(raid, logical_drives_details, "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives")
                if response["ret"]:
                    raid_data.remove(raid)
                elif not response["ret"] and response["msg"] != "Logical drive provided is not present in server":
                    return response
        if not raid_data:
            return {
                "ret": True,
                "changed": False,
                "msg": "Provided logical drives are already present in the server"
            }

        response = self.check_smartstorage_physical_drive_count(raid_data, unused_physical_drives,
                                                                "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives")
        if not response["ret"]:
            return response

        response = self.check_smartstorage_physical_drives(raid_data, unused_physical_drives, "CreateSmartStorageLogicalDrivesWithParticularPhysicalDrives")
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        response = self.get_request(self.root_uri + self.systems_uri + "smartstorageconfig/")
        if not response["ret"]:
            return response

        storage_data = response["data"]

        ld_names = [i["LogicalDriveName"] for i in raid_data]
        LogicalDrives = storage_data["LogicalDrives"]
        body = {}
        body["LogicalDrives"] = LogicalDrives + raid_data
        body["DataGuard"] = "Permissive"
        url = "smartstorageconfig/settings/"

        res = self.put_request(self.root_uri + self.systems_uri + url, body)

        if not res["ret"]:
            return res

        return {
            "ret": True,
            "changed": True,
            "msg": "Create logical drives request sent for %s. System Reset required." % str(ld_names)
        }

    def delete_specified_smartstorage_logical_drives(self, logical_drives_names):
        # This function makes call to Server through redfish client to delete logical drives
        # in OOB controller whose names are given in the logical_drives_names parameter

        body = {"LogicalDrives": [], "DataGuard": "Permissive"}

        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response

        url = self.systems_uri + "smartstorageconfig/settings/"

        logical_drives_details_response = self.get_smartstorage_logical_drives()
        if not logical_drives_details_response["ret"]:
            return logical_drives_details_response

        logical_drives_details = logical_drives_details_response["msg"]["logical_drives_details"]

        for name in logical_drives_names:
            flag = False
            for drive in logical_drives_details:
                if name == drive["LogicalDriveName"]:
                    body["LogicalDrives"].append({"Actions": [{"Action": "LogicalDriveDelete"}],
                                                  "VolumeUniqueIdentifier": drive["VolumeUniqueIdentifier"]})
                    flag = True
            if not flag:
                return {
                    "ret": False,
                    "changed": False,
                    "msg": "No logical drives on the server match with the given logical drive name %s" % name
                }

        res = self.put_request(self.root_uri + url, body)

        if not res["ret"]:
            return res

        return {
            "ret": True,
            "changed": True,
            "msg": "Delete logical drives request sent for %s. System Reset required." % str(logical_drives_names)
        }

    def delete_all_snmpv3_users(self):
        # This method deletes all SNMPv3 users
        server_snmpv3_users = self.get_snmpv3_users()
        if not server_snmpv3_users["ret"]:
            return server_snmpv3_users

        if not server_snmpv3_users["msg"]:
            return {
                "ret": True,
                "changed": False,
                "msg": "No SNMPv3 users present on the server"
            }

        delete_fail = []
        # Loop over list of SNMPv3 users
        for data in server_snmpv3_users["msg"]:
            # DELETE SNMPv3 user
            uri = self.root_uri + self.manager_uri + "SnmpService/SNMPUsers/"
            response = self.delete_request(uri + data["Id"])
            if not response["ret"]:
                delete_fail.append({"user": data["SecurityName"],
                                    "response": response["msg"]})
        if delete_fail:
            return {
                "ret": False,
                "msg": "Deleting SNMPv3 users failed: %s" % str(delete_fail)
            }

        return {
            "ret": True,
            "changed": True,
            "msg": "SNMPv3 users are deleted"
        }

    def delete_all_snmp_alert_destinations(self):
        # This method deletes all SNMP alert destinations
        server_alert_destinations = self.get_snmp_alert_destinations()
        if not server_alert_destinations["ret"]:
            return server_alert_destinations

        if not server_alert_destinations["msg"]:
            return {
                "ret": True,
                "changed": False,
                "msg": "No SNMP Alert Destinations present on the server"
            }

        delete_fail = []
        # Loop over list of SNMP alert destinations
        for data in server_alert_destinations["msg"]:
            # DELETE SNMP alert destination
            uri = self.root_uri + self.manager_uri + "SnmpService/SNMPAlertDestinations/"
            response = self.delete_request(uri + data["Id"])
            if not response["ret"]:
                delete_fail.append({"AlertDestination": data["AlertDestination"],
                                    "response": response["msg"]})
        if delete_fail:
            return {
                "ret": False,
                "msg": "Deleting SNMP alert destinations failed: %s" % str(delete_fail)
            }

        return {
            "ret": True,
            "changed": True,
            "msg": "SNMP Alert Destinations are deleted"
        }

    def delete_snmpv3_users(self, snmpv3_users):
        # This method deletes provided SNMPv3 users
        server_snmpv3_users = self.get_snmpv3_users()
        if not server_snmpv3_users["ret"]:
            return server_snmpv3_users
        server_snmpv3_users = server_snmpv3_users["msg"]

        snmpv3_users = list(set(snmpv3_users))
        # Validating if SNMPv3 users exists or not
        wrong_user = []
        for user in snmpv3_users:
            if user not in [data["SecurityName"] for data in server_snmpv3_users]:
                wrong_user.append(user)
        if wrong_user:
            return {
                "ret": False,
                "msg": "Provided SNMPv3 users are not present in the server: %s" % str(wrong_user)
            }

        uri = self.root_uri + self.manager_uri + "SnmpService/SNMPUsers/"
        delete_fail = []
        # Loop over list of SNMPv3 users
        for user in snmpv3_users:
            for data in server_snmpv3_users:
                if user == data["SecurityName"]:
                    # DELETE SNMPv3 user
                    response = self.delete_request(uri + data["Id"])
                    if not response["ret"]:
                        delete_fail.append({"user": user,
                                            "response": response["msg"]})
        if delete_fail:
            return {
                "ret": False,
                "msg": "Deleting SNMPv3 users failed: %s" % str(delete_fail)
            }

        return {
            "ret": True,
            "changed": True,
            "msg": "SNMPv3 users are deleted"
        }

    def get_specified_smartstorage_logical_drives(self, logical_drives_names):
        # This method returns logical drives details for provided logical drive names
        result = {}
        logical_drives_names_list = logical_drives_names[:]
        response = self.get_smartstorage_logical_drives()
        if not response["ret"]:
            return response

        logical_drives_details = response["msg"]["logical_drives_details"]

        needed_logical_drives = []

        for drive in logical_drives_details:
            for drive_name in logical_drives_names:
                if drive_name == drive["LogicalDriveName"]:
                    needed_logical_drives.append(drive)
                    logical_drives_names_list.remove(drive_name)

        if logical_drives_names_list:
            return {
                "ret": False,
                "msg": "Logical drives with these names were not found on the server: %s " % str(logical_drives_names_list)
            }

        result["logical_drives_details"] = needed_logical_drives

        return {
            "ret": True,
            "msg": result
        }

    def validate_engine_id(self, user):
        # Validating user Engine ID

        error_msg = "Provided invalid engine ID: '%s'. " \
                    "User Engine ID must be a hexadecimal string" \
                    " with an even number of 10 to 64 characters, " \
                    "excluding the first two characters, " \
                    "0x (for example, 0x0123456789abcdef)"

        if not user['user_engine_id']:
            return {
                "ret": False,
                "msg": error_msg % (str(user['user_engine_id']))
            }

        engine_id = list(user['user_engine_id'])
        if (len(engine_id) < 12 or len(engine_id) > 66) or \
                (not engine_id.startswith("0x")) or \
                (len(engine_id[2:]) % 2 != 0):
            return {
                "ret": False,
                "msg": error_msg % (user['user_engine_id'])
            }
        for id in engine_id[2:]:
            if id.lower() not in set("0123456789abcdef"):
                return {
                    "ret": False,
                    "msg": error_msg % (user['user_engine_id'])
                }
        return {"ret": True}

    def validate_snmpv3user_value(self, user, module):
        # SNMP user value validation
        allowed_list = ['security_name', 'auth_protocol', 'auth_passphrase',
                        'privacy_protocol', 'privacy_passphrase',
                        'user_engine_id']
        validate_dict = {"auth_protocol": ["MD5", "SHA", "SHA256"],
                         "privacy_protocol": ["DES", "AES"]}
        if "security_name" not in user:
            return {
                "ret": False,
                "msg": "Input parameter 'security_name' is missing"
            }
        if not user["security_name"]:
            return {
                "ret": False,
                "msg": "'security_name' value should not be empty"
            }
        if module == "update" and len(user) == 1:
            err_msg = "Provide a minimum of one input parameter for SNMPv3 user: %s. Allowed parameters are: %s"
            return {
                "ret": False,
                "msg": err_msg % (str(user["security_name"]), allowed_list[1:])
            }
        for key, value in validate_dict.items():
            if key in user and user[key] not in value:
                return {
                    "ret": False,
                    "msg": "Given value '%s' is not supported for '%s'" % (user[key], key)
                }

        if not user["auth_passphrase"]:
            return {
                "ret": False,
                "msg": "auth_passphrase value cannot be empty"
            }

        if not user["privacy_passphrase"]:
            return {
                "ret": False,
                "msg": "privacy_passphrase value cannot be empty"
            }

        if ("privacy_passphrase" in user and not len(user["privacy_passphrase"]) >= 8) or \
                ("auth_passphrase" in user and not len(user["auth_passphrase"]) >= 8):
            return {
                "ret": False,
                "msg": "Minimum character length for privacy_passphrase or auth_passphrase is 8"
            }
        if set(user.keys()) - set(allowed_list):
            return {
                "ret": False,
                "msg": "Unsupported input parameters: %s" % str(list(set(user.keys()) - set(allowed_list)))
            }
        return {"ret": True}

    def validate_snmpv3_users_input(self, server_snmpv3_users, snmpv3_users, module):
        # Validating input parameters
        if module == "create" and len(server_snmpv3_users) + len(snmpv3_users) > 8:
            message = "Maximum of 8 SNMPv3 users can be added to a server..." + \
                      "Already server has %s users and provided %s more users"
            return {
                "ret": False,
                "msg": message % (len(server_snmpv3_users), len(snmpv3_users))
            }

        input_list = ['security_name', 'auth_protocol', 'auth_passphrase',
                      'privacy_protocol', 'privacy_passphrase']

        for user in snmpv3_users:
            if module == "create":
                missing_param = [i for i in input_list if i not in user]
                if missing_param:
                    msg = "Input parameter %s is missing to create SNMPv3 user. Mandatory parameters are %s"
                    return {
                        "ret": False,
                        "msg": msg % (str(missing_param), str(input_list))
                    }
            response = self.validate_snmpv3user_value(user, module)
            if not response["ret"]:
                return response

            if 'user_engine_id' in user.keys():
                response = self.validate_engine_id(user)
                if not response["ret"]:
                    return response
        return {"ret": True}

    def check_if_snmpv3user_exists(self, server_snmpv3_users, snmpv3_users):
        # Validating if SNMPv3 users already exists
        existing_user = []
        wrong_user = []
        for user in snmpv3_users:
            flag = False
            for data in server_snmpv3_users:
                if data["SecurityName"] == user["security_name"]:
                    existing_user.append(data["SecurityName"])
                    flag = True
            if not flag:
                wrong_user.append(user["security_name"])
        return existing_user, wrong_user

    def validate_duplicate_entries(self, snmpv3_users):
        # Validating duplicate entry
        duplicate = []
        snmpv3_user_names = [i["security_name"] for i in snmpv3_users]
        for snmp in snmpv3_user_names:
            if snmpv3_user_names.count(snmp) > 1:
                duplicate.append(snmp)
        if duplicate:
            return {
                "ret": False,
                "msg": "Duplicate entries provided for users: %s" % str(list(set(duplicate)))
            }
        return {"ret": True}

    def validate_snmpv3_users(self, server_snmpv3_users, snmpv3_users, module):
        # Validating input parameters
        input_result = self.validate_snmpv3_users_input(server_snmpv3_users, snmpv3_users, module)
        if not input_result["ret"]:
            return input_result

        # Validating duplicate entry
        duplicate_entry_result = self.validate_duplicate_entries(snmpv3_users)
        if not duplicate_entry_result["ret"]:
            return duplicate_entry_result

        # Checking if user already exists
        response = self.check_if_snmpv3user_exists(server_snmpv3_users, snmpv3_users)
        if module == "create" and response[0]:
            message = "Already user exists with same name: %s"
            return {
                "ret": False,
                "msg": message % (str(response[0]))
            }
        if module == "update" and response[1]:
            return {
                "ret": False,
                "msg": "Provided SNMPv3 users are not present in the server: %s" % str(response[1])
            }
        return {"ret": True}

    def update_snmpv3_users(self, snmpv3_users):
        # This method updates SNMPv3 users with provided input
        server_snmpv3_users = self.get_snmpv3_users()
        if not server_snmpv3_users["ret"]:
            return server_snmpv3_users
        server_snmpv3_users = server_snmpv3_users["msg"]

        # Validating input
        validate_result = self.validate_snmpv3_users(server_snmpv3_users, snmpv3_users, "update")
        if not validate_result["ret"]:
            return validate_result

        uri = self.root_uri + self.manager_uri + "SnmpService/SNMPUsers/"
        for user in snmpv3_users:
            # Define payload
            body = {
                "SecurityName": user['security_name']
            }
            if "auth_protocol" in user:
                body["AuthProtocol"] = user['auth_protocol']
            if "auth_passphrase" in user:
                body["AuthPassphrase"] = user['auth_passphrase']
            if "privacy_protocol" in user:
                body["PrivacyProtocol"] = user['privacy_protocol']
            if "privacy_passphrase" in user:
                body["PrivacyPassphrase"] = user['privacy_passphrase']
            if 'user_engine_id' in user:
                body["UserEngineID"] = user['user_engine_id']

            # Get snmpv3 user uri
            for snmp in server_snmpv3_users:
                if user['security_name'] == snmp["SecurityName"]:
                    snmp_id = snmp["Id"]
                    break
            # PATCH on Managers API
            snmp_res = self.patch_request(uri + snmp_id, body)
            if not snmp_res["ret"]:
                return {
                    "ret": False,
                    "msg": snmp_res
                }

        return {"ret": True, "changed": True, "msg": "SNMPv3 users are updated"}

    def create_snmpv3_users(self, snmpv3_users):
        # This method creates SNMPv3 users
        server_snmpv3_users = self.get_snmpv3_users()
        if not server_snmpv3_users["ret"]:
            return server_snmpv3_users
        server_snmpv3_users = server_snmpv3_users["msg"]

        # Validating SNMPv3 users input
        validate_result = self.validate_snmpv3_users(server_snmpv3_users, snmpv3_users, "create")
        if not validate_result["ret"]:
            return validate_result

        for user in snmpv3_users:
            # Define payload
            body = {
                "SecurityName": user['security_name'],
                "AuthProtocol": user['auth_protocol'],
                "AuthPassphrase": user['auth_passphrase'],
                "PrivacyProtocol": user['privacy_protocol'],
                "PrivacyPassphrase": user['privacy_passphrase']
            }
            # Add engine ID if provided
            if 'user_engine_id' in user.keys():
                body["UserEngineID"] = user['user_engine_id']
            # POST on Managers API
            uri = self.root_uri + self.manager_uri + "SnmpService/SNMPUsers/"
            snmp_res = self.post_request(uri, body)
            if not snmp_res["ret"]:
                return {
                    "ret": False,
                    "msg": snmp_res
                }

        return {"ret": True, "changed": True, "msg": "SNMPv3 users are added"}

    def check_snmpv3_username(self, dest):
        if "security_name" not in dest or not dest["security_name"]:
            return {
                "ret": False,
                "msg": "security_name is missing for SNMP Alert protocol: '%s', destination IP: '%s'" % (
                    dest['snmp_alert_protocol'], dest["alert_destination"])
            }

        # Get existing SNMPv3 users from server
        server_snmpv3_users = self.get_snmpv3_users()
        if not server_snmpv3_users["ret"]:
            return server_snmpv3_users
        server_snmpv3_users = server_snmpv3_users["msg"]

        if dest["security_name"] not in [x["SecurityName"] for x in server_snmpv3_users]:
            return {
                "ret": False,
                "msg": "security_name '%s' does not exists, destination IP: '%s'" % (
                    dest['security_name'], dest["alert_destination"])
            }

        return {"ret": True}

    def validate_alert_destinations(self, server_alert_destinations, alert_destinations):
        # Validating input parameters for SNMP alert destinations
        if len(server_alert_destinations) + len(alert_destinations) > 8:
            message = "Maximum of 8 alert destinations can be added to a server..." + \
                      "Already server has %s Alert destinations and provided %s more Alert destinations"
            return {
                "ret": False,
                "msg": message % (len(server_alert_destinations), len(alert_destinations))
            }
        input_list = ['alert_destination', 'snmp_alert_protocol']
        allowed_list = ['alert_destination', 'snmp_alert_protocol', 'trap_community', 'security_name']
        for dest in alert_destinations:
            for input in input_list:
                if input not in dest.keys():
                    return {
                        "ret": False,
                        "msg": "Input parameter '%s' is missing to create alert destination" % input
                    }
            for input in dest.keys():
                if input not in allowed_list:
                    return {
                        "ret": False,
                        "msg": "Unsupported parameter '%s' is provided to create alert destination" % input
                    }

            if not dest["alert_destination"]:
                return {
                    "ret": False,
                    "msg": "Invalid IP address/HostName/FQDN: %s" % dest["alert_destination"]
                }

            if not isinstance(dest["alert_destination"], str):
                return {
                    "ret": False,
                    "msg": "Alert Destination should be of type 'str'"
                }

            temp = str(dest["alert_destination"]).split(".")
            if len(temp) == 4:
                try:
                    ipaddress.ip_address(dest["alert_destination"])
                except Exception as e:
                    return {
                        "ret": False,
                        "msg": "Invalid IP address: %s" % dest["alert_destination"]
                    }
            else:
                if len(str(dest["alert_destination"])) > 255:
                    return {
                        "ret": False,
                        "msg": "Invalid HostName/FQDN: %s" % dest["alert_destination"]
                    }
                if str(dest["alert_destination"])[-1] == ".":
                    hostname = str(dest["alert_destination"])[:-1]
                else:
                    hostname = str(dest["alert_destination"])

                allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
                if not all(allowed.match(x) for x in hostname.split(".")):
                    return {
                        "ret": False,
                        "msg": "Invalid HostName/FQDN: %s" % dest["alert_destination"]
                    }

            if dest['snmp_alert_protocol'].lower() == "snmpv1trap":
                dest['snmp_alert_protocol'] = "SNMPv1Trap"
            elif dest['snmp_alert_protocol'].lower() == "snmpv3trap":
                dest['snmp_alert_protocol'] = "SNMPv3Trap"
            elif dest['snmp_alert_protocol'].lower() == "snmpv3inform":
                dest['snmp_alert_protocol'] = "SNMPv3Inform"
            else:
                return {
                    "ret": False,
                    "msg": "Wrong SNMP Alert protocol '%s' is provided" % dest['snmp_alert_protocol']
                }
            if "trap_community" not in dest or not dest["trap_community"] or dest["trap_community"].lower() in ["na", " "]:
                dest["trap_community"] = ""
            if dest['snmp_alert_protocol'] in ["SNMPv1Trap"]:
                if "security_name" in dest:
                    return {
                        "ret": False,
                        "msg": "security_name is not supported for SNMP Alert protocol: '%s', destination IP: '%s'" % (
                            dest['snmp_alert_protocol'], dest["alert_destination"])
                    }
            if dest['snmp_alert_protocol'] in ["SNMPv3Trap", "SNMPv3Inform"]:
                response = self.check_snmpv3_username(dest)
                if not response["ret"]:
                    return response
        return {
            "ret": True,
            "msg": alert_destinations
        }

    def create_alert_destinations(self, alert_destinations):
        # This method creates SNMP alert destinations
        server_alert_destinations = self.get_snmp_alert_destinations()
        if not server_alert_destinations["ret"]:
            return server_alert_destinations
        server_alert_destinations = server_alert_destinations["msg"]

        # Validating alert destination input
        alert_destinations = self.validate_alert_destinations(server_alert_destinations, alert_destinations)
        if not alert_destinations["ret"]:
            return alert_destinations
        alert_destinations = alert_destinations["msg"]

        for dest in alert_destinations:
            # Define payload
            body = {
                "AlertDestination": str(dest["alert_destination"]),
                "SNMPAlertProtocol": dest['snmp_alert_protocol'],
                "TrapCommunity": dest["trap_community"]
            }
            # Adding SNMP username to Payload for SNMPv3Trap/SNMPv3Inform
            if dest['snmp_alert_protocol'] in ["SNMPv3Trap", "SNMPv3Inform"]:
                body["SecurityName"] = dest["security_name"]
            # POST on Managers API
            uri = self.root_uri + self.manager_uri + "SnmpService/SNMPAlertDestinations/"

            snmp_res = self.post_request(uri, body)
            if not snmp_res["ret"]:
                return {"ret": False, "msg": snmp_res}
        return {
            "ret": True,
            "changed": True,
            "msg": "SNMP Alert Destinations are added"
        }

    def get_server_poststate(self):
        # Get server details
        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response
        server_data = response["data"]

        if "Hpe" in server_data["Oem"]:
            return {
                "ret": True,
                "server_poststate": server_data["Oem"]["Hpe"]["PostState"]
            }
        else:
            return {
                "ret": True,
                "server_poststate": server_data["Oem"]["Hp"]["PostState"]
            }

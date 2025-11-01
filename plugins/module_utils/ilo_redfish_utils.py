# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
import time


class iLORedfishUtils(RedfishUtils):
    def get_ilo_sessions(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        session_list = []
        sessions_results = []
        # Get these entries, but does not fail if not found
        properties = ["Description", "Id", "Name", "UserName"]

        # Changed self.sessions_uri to Hardcoded string.
        response = self.get_request(f"{self.root_uri}{self.service_root}SessionService/Sessions/")
        if not response["ret"]:
            return response
        result["ret"] = True
        data = response["data"]

        current_session = None
        if "Oem" in data:
            if data["Oem"]["Hpe"]["Links"]["MySession"]["@odata.id"]:
                current_session = data["Oem"]["Hpe"]["Links"]["MySession"]["@odata.id"]

        for sessions in data["Members"]:
            # session_list[] are URIs
            session_list.append(sessions["@odata.id"])
        # for each session, get details
        for uri in session_list:
            session = {}
            if uri != current_session:
                response = self.get_request(self.root_uri + uri)
                if not response["ret"]:
                    return response
                data = response["data"]
                for property in properties:
                    if property in data:
                        session[property] = data[property]
                sessions_results.append(session)
        result["msg"] = sessions_results
        result["ret"] = True
        return result

    def set_ntp_server(self, mgr_attributes):
        result = {}
        setkey = mgr_attributes["mgr_attr_name"]

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        response = self.get_request(self.root_uri + ethuri)
        if not response["ret"]:
            return response
        result["ret"] = True
        data = response["data"]
        payload = {"DHCPv4": {"UseNTPServers": ""}}

        if data["DHCPv4"]["UseNTPServers"]:
            payload["DHCPv4"]["UseNTPServers"] = False
            res_dhv4 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv4["ret"]:
                return res_dhv4

        payload = {"DHCPv6": {"UseNTPServers": ""}}

        if data["DHCPv6"]["UseNTPServers"]:
            payload["DHCPv6"]["UseNTPServers"] = False
            res_dhv6 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv6["ret"]:
                return res_dhv6

        datetime_uri = f"{self.manager_uri}DateTime"

        listofips = mgr_attributes["mgr_attr_value"].split(" ")
        if len(listofips) > 2:
            return {"ret": False, "changed": False, "msg": "More than 2 NTP Servers mentioned"}

        ntp_list = []
        for ips in listofips:
            ntp_list.append(ips)

        while len(ntp_list) < 2:
            ntp_list.append("0.0.0.0")

        payload = {setkey: ntp_list}

        response1 = self.patch_request(self.root_uri + datetime_uri, payload)
        if not response1["ret"]:
            return response1

        return {"ret": True, "changed": True, "msg": f"Modified {mgr_attributes['mgr_attr_name']}"}

    def set_time_zone(self, attr):
        key = attr["mgr_attr_name"]

        uri = f"{self.manager_uri}DateTime/"
        response = self.get_request(self.root_uri + uri)
        if not response["ret"]:
            return response

        data = response["data"]

        if key not in data:
            return {"ret": False, "changed": False, "msg": f"Key {key} not found"}

        timezones = data["TimeZoneList"]
        index = ""
        for tz in timezones:
            if attr["mgr_attr_value"] in tz["Name"]:
                index = tz["Index"]
                break

        payload = {key: {"Index": index}}
        response = self.patch_request(self.root_uri + uri, payload)
        if not response["ret"]:
            return response

        return {"ret": True, "changed": True, "msg": f"Modified {attr['mgr_attr_name']}"}

    def set_dns_server(self, attr):
        key = attr["mgr_attr_name"]
        nic_info = self.get_manager_ethernet_uri()
        uri = nic_info["nic_addr"]

        listofips = attr["mgr_attr_value"].split(" ")
        if len(listofips) > 3:
            return {"ret": False, "changed": False, "msg": "More than 3 DNS Servers mentioned"}

        dns_list = []
        for ips in listofips:
            dns_list.append(ips)

        while len(dns_list) < 3:
            dns_list.append("0.0.0.0")

        payload = {"Oem": {"Hpe": {"IPv4": {key: dns_list}}}}

        response = self.patch_request(self.root_uri + uri, payload)
        if not response["ret"]:
            return response

        return {"ret": True, "changed": True, "msg": f"Modified {attr['mgr_attr_name']}"}

    def set_domain_name(self, attr):
        key = attr["mgr_attr_name"]

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        response = self.get_request(self.root_uri + ethuri)
        if not response["ret"]:
            return response

        data = response["data"]

        payload = {"DHCPv4": {"UseDomainName": ""}}

        if data["DHCPv4"]["UseDomainName"]:
            payload["DHCPv4"]["UseDomainName"] = False
            res_dhv4 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv4["ret"]:
                return res_dhv4

        payload = {"DHCPv6": {"UseDomainName": ""}}

        if data["DHCPv6"]["UseDomainName"]:
            payload["DHCPv6"]["UseDomainName"] = False
            res_dhv6 = self.patch_request(self.root_uri + ethuri, payload)
            if not res_dhv6["ret"]:
                return res_dhv6

        domain_name = attr["mgr_attr_value"]

        payload = {"Oem": {"Hpe": {key: domain_name}}}

        response = self.patch_request(self.root_uri + ethuri, payload)
        if not response["ret"]:
            return response
        return {"ret": True, "changed": True, "msg": f"Modified {attr['mgr_attr_name']}"}

    def set_wins_registration(self, mgrattr):
        Key = mgrattr["mgr_attr_name"]

        nic_info = self.get_manager_ethernet_uri()
        ethuri = nic_info["nic_addr"]

        payload = {"Oem": {"Hpe": {"IPv4": {Key: False}}}}

        response = self.patch_request(self.root_uri + ethuri, payload)
        if not response["ret"]:
            return response
        return {"ret": True, "changed": True, "msg": f"Modified {mgrattr['mgr_attr_name']}"}

    def get_server_poststate(self):
        # Get server details
        response = self.get_request(self.root_uri + self.systems_uri)
        if not response["ret"]:
            return response
        server_data = response["data"]

        if "Hpe" in server_data["Oem"]:
            return {"ret": True, "server_poststate": server_data["Oem"]["Hpe"]["PostState"]}
        else:
            return {"ret": True, "server_poststate": server_data["Oem"]["Hp"]["PostState"]}

    def wait_for_ilo_reboot_completion(self, polling_interval=60, max_polling_time=1800):
        # This method checks if OOB controller reboot is completed
        time.sleep(10)

        # Check server poststate
        state = self.get_server_poststate()
        if not state["ret"]:
            return state

        count = int(max_polling_time / polling_interval)
        times = 0

        # When server is powered OFF
        pcount = 0
        while state["server_poststate"] in ["PowerOff", "Off"] and pcount < 5:
            time.sleep(10)
            state = self.get_server_poststate()
            if not state["ret"]:
                return state

            if state["server_poststate"] not in ["PowerOff", "Off"]:
                break
            pcount = pcount + 1
        if state["server_poststate"] in ["PowerOff", "Off"]:
            return {"ret": False, "changed": False, "msg": "Server is powered OFF"}

        # When server is not rebooting
        if state["server_poststate"] in ["InPostDiscoveryComplete", "FinishedPost"]:
            return {"ret": True, "changed": False, "msg": "Server is not rebooting"}

        while state["server_poststate"] not in ["InPostDiscoveryComplete", "FinishedPost"] and count > times:
            state = self.get_server_poststate()
            if not state["ret"]:
                return state

            if state["server_poststate"] in ["InPostDiscoveryComplete", "FinishedPost"]:
                return {"ret": True, "changed": True, "msg": "Server reboot is completed"}
            time.sleep(polling_interval)
            times = times + 1

        return {"ret": False, "changed": False, "msg": f"Server Reboot has failed, server state: {state} "}

# !/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import json
import subprocess
import time

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.urls import open_url
try:
    from requests_toolbelt import MultipartEncoder
    HAS_REQUESTS_TOOLBELT = True
except ImportError:
    HAS_REQUESTS_TOOLBELT = False


REQUESTS_TOOLBELT_REQUIRED = "Requests_toolbelt is required for this module"


def has_requests_toolbelt(module):
    """
    Check Request_toolbelt is installed
    :param module:
    """
    if not HAS_REQUESTS_TOOLBELT:
        module.fail_json(msg=REQUESTS_TOOLBELT_REQUIRED)


supported_models = ["HPE CRAY XD220V", "HPE CRAY XD225V", "HPE CRAY XD295V", "HPE CRAY XD665", "HPE CRAY XD670"]

# To get inventory, update
supported_targets = {
    "HPE CRAY XD220V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD225V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD295V": ["BMC", "BIOS", "MainCPLD", "HDDBPPIC", "PDBPIC"],
    "HPE CRAY XD665": ["BMC", "BIOS", "RT_NVME", "RT_OTHER", "RT_SA", "PDB", "MainCPLD", "UBM6"],
    "HPE CRAY XD670": ["BMCImage1", "BMCImage2", "BIOS", "BIOS2", "BPB_CPLD1", "BPB_CPLD2", "MB_CPLD1", "SCM_CPLD1"],
}

unsupported_targets = ["BMCImage1", "BPB_CPLD1", "BPB_CPLD2", "MB_CPLD1", "SCM_CPLD1"]  # Only of Jakku
# BMCImage1 equivalent to BMC
# BPB_CPLD1 and BPB_CPLD2 together equivalent to BPB_CPLD
# MB_CPLD1 and SCM_CPLD1 together equivalent to MB_CPLD1_SCM_CPLD1
all_targets = ['BMC', 'BMCImage1', 'BMCImage2', 'BIOS', 'BIOS2', 'MainCPLD',
               'MB_CPLD1', 'BPB_CPLD1', 'BPB_CPLD2', 'SCM_CPLD1', 'PDB', 'PDBPIC', 'HDDBPPIC', 'RT_NVME', 'RT_OTHER', 'RT_SA', 'UBM6']

reboot = {
    "BIOS": ["AC_PC_redfish"],
    "BIOS2": ["AC_PC_redfish"],
    "MainCPLD": ["AC_PC_ipmi"],
    "PDB": ["AC_PC_ipmi"],
    "RT_NVME": ["AC_PC_redfish", "AC_PC_ipmi", "AC_PC_redfish"],
    "RT_SA": ["AC_PC_redfish", "AC_PC_ipmi", "AC_PC_redfish"],
    "RT_OTHER": ["AC_PC_redfish", "AC_PC_ipmi", "AC_PC_redfish"],
    "HDDBPPIC": ["AC_PC_redfish"],
    "PDBPIC": ["AC_PC_redfish"]
}

routing = {
    "HPE CRAY XD220V": "0x34 0xa2 0x00 0x19 0xA9",
    "HPE CRAY XD225V": "0x34 0xa2 0x00 0x19 0xA9",
    "HPE CRAY XD295V": "0x34 0xa2 0x00 0x19 0xA9",
    "HPE CRAY XD665": "0x34 0xA2 0x00 0x19 0xa9 0x00"
}


class CrayRedfishUtils(RedfishUtils):
    def post_multi_request(self, uri, headers, payload):
        username, password, basic_auth = self._auth_params(headers)
        try:
            resp = open_url(uri, data=payload, headers=headers, method="POST",
                            url_username=username, url_password=password,
                            force_basic_auth=basic_auth, validate_certs=False,
                            follow_redirects='all',
                            use_proxy=True, timeout=self.timeout)
            resp_headers = dict((k.lower(), v) for (k, v) in resp.info().items())
            return True
        except Exception as e:
            return False

    def get_model(self):
        response = self.get_request(self.root_uri + "/redfish/v1/Systems/Self")
        if response['ret'] is False:
            return "NA"
        try:
            if 'Model' in response['data']:
                model = response['data'][u'Model']
                if model is not None:
                    model = model[:15]
                else:
                    model = 'None'
            else:
                model = 'None'
            return model
        except Exception:
            if 'Model' in response:
                model = response[u'Model']
                if model is not None:
                    model = model[:15]
                else:
                    model = 'None'
            else:
                model = 'None'
            return model

    def power_state(self):
        response = self.get_request(self.root_uri + "/redfish/v1/Systems/Self")
        if response['ret'] is False:
            return "NA"
        try:
            if 'PowerState' in response['data']:
                state = response['data'][u'PowerState']
                if state is None:
                    state = 'None'
            else:
                state = 'None'
            return state
        except Exception:
            if 'PowerState' in response:
                state = response[u'PowerState']
                if state is None:
                    state = 'None'
            else:
                state = 'None'
            return state

    def power_on(self):
        payload = {"ResetType": "On"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(120)

    def power_off(self):
        payload = {"ResetType": "ForceOff"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(120)

    def get_PS_CrayXD670(self, attr):
        IP = attr.get('baseuri')
        option = attr.get('power_state')
        csv_file_name = attr.get('output_file_name')
        if not os.path.exists(csv_file_name):
            f = open(csv_file_name, "w")
            to_write = "IP_Address, Model, Power_State\n"
            f.write(to_write)
            f.close()
        model = self.get_model()
        if model.upper() == "HPE CRAY XD670":
            power_state = self.power_state()
            if option.upper() == "NA":
                lis = [IP, model, power_state]
            elif option.upper() == "ON":
                if power_state.upper() == "OFF":
                    self.power_on()
                power_state = self.power_state()
                lis = [IP, model, power_state]
            elif option.upper() == "OFF":
                if power_state.upper() == "ON":
                    self.power_off()
                power_state = self.power_state()
                lis = [IP, model, power_state]
            else:
                return {'ret': False, 'changed': True, 'msg': 'Must specify the correct required option for power_state'}

        else:
            lis = [IP, model, "unsupported_model"]
        new_data = ", ".join(lis)
        return {'ret': True, 'changed': True, 'msg': str(new_data)}

    def target_supported(self, model, target):
        if target in supported_targets[model.upper()]:
            return True
        return False

    def get_fw_version(self, target):
        try:
            response = self.get_request(self.root_uri + "/redfish/v1/UpdateService/FirmwareInventory" + "/" + target)
            try:
                version = response['data']['Version']
                return version
            except Exception:
                version = response['Version']
                return version
        except Exception:
            return "failed_FI_GET_call/no_version_field"

    def AC_PC_redfish(self):
        payload = {"ResetType": "ForceRestart"}
        target_uri = "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
        response1 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(180)
        target_uri = "/redfish/v1/Chassis/Self/Actions/Chassis.Reset"
        response2 = self.post_request(self.root_uri + target_uri, payload)
        time.sleep(180)
        return response1 or response2

    def AC_PC_ipmi(self, IP, username, password, routing_value):
        try:
            command = 'ipmitool -I lanplus -H ' + IP + ' -U ' + username + ' -P ' + password + ' raw ' + routing_value
            subprocess.run(command, shell=True, check=True, timeout=15, capture_output=True)
            time.sleep(300)
            return True
        except Exception:
            return False

    def get_sys_fw_inventory(self, attr):
        IP = attr.get('baseuri')
        csv_file_name = attr.get('output_file_name')
        if not os.path.exists(csv_file_name):
            f = open(csv_file_name, "w")
            to_write = """IP_Address, Model, BMC, BMCImage1, BMCImage2, BIOS, BIOS2, MainCPLD, MB_CPLD1,
                            BPB_CPLD1, BPB_CPLD2, SCM_CPLD1, PDB, PDBPIC, HDDBPPIC, RT_NVME, RT_OTHER, RT_SA, UBM6\n"""
            f.write(to_write)
            f.close()
        model = self.get_model()
        entry = []
        entry.append(IP)
        if model.upper() not in supported_models:
            entry.append("unsupported_model")
            for target in all_targets:
                entry.append("NA")
        else:
            entry.append(model)
            for target in all_targets:
                if target in supported_targets[model.upper()]:
                    version = self.get_fw_version(target)
                    if version.startswith("failed"):
                        version = "NA"  # "no_comp/no_version"
                else:
                    version = "NA"
                entry.append(version)
        new_data = ", ".join(entry)
        return {'ret': True, 'changed': True, 'msg': str(new_data)}

    def helper_update(self, update_status, target, image_path, image_type, IP, username, password, model):
        before_version = "failed"
        if target != "BPB_CPLD" and target != "SCM_CPLD1" and target != "MB_CPLD1":
            before_version = self.get_fw_version(target)
            after_version = "NA"
        else:
            before_version = "NA"
        if not before_version.startswith("failed"):
            # proceed for update
            response = self.get_request(self.root_uri + "/redfish/v1/UpdateService")
            if response['ret'] is False:
                update_status = "UpdateService api not found"
            else:
                data = response['data']
                if 'MultipartHttpPushUri' in data:
                    headers = {'Expect': 'Continue', 'Content-Type': 'multipart/form-data'}
                    body = {}
                    if target != "BPB_CPLD":
                        targets_uri = '/redfish/v1/UpdateService/FirmwareInventory/' + target + '/'
                        body['UpdateParameters'] = (None, json.dumps({"Targets": [targets_uri]}), 'application/json')
                    else:
                        body['UpdateParameters'] = (None, json.dumps({"Targets":
                                                                      ['/redfish/v1/UpdateService/FirmwareInventory/BPB_CPLD1/',
                                                                       '/redfish/v1/UpdateService/FirmwareInventory/BPB_CPLD2/']}),
                                                    'application/json')
                    body['OemParameters'] = (None, json.dumps({"ImageType": image_type}), 'application/json')
                    with open(image_path, 'rb') as image_path_rb:
                        body['UpdateFile'] = (image_path, image_path_rb, 'application/octet-stream')
                        encoder = MultipartEncoder(body)
                        body = encoder.to_string()
                        headers['Content-Type'] = encoder.content_type

                        response = self.post_multi_request(self.root_uri + data['MultipartHttpPushUri'],
                                                           headers=headers, payload=body)
                        if response is False:
                            update_status = "failed_POST"
                        else:
                            # Add time.sleep (for system to comeback after flashing)
                            time.sleep(300)
                            # Call reboot logic based on target
                            if target in reboot:
                                what_reboots = reboot[target]
                                for reb in what_reboots:
                                    if reb == "AC_PC_redfish":
                                        result = self.AC_PC_redfish()
                                        if not result:
                                            update_status = "reboot_failed"
                                            break
                                        time.sleep(300)
                                    elif reb == "AC_PC_ipmi":
                                        # based on the model end routing code changes
                                        result = self.AC_PC_ipmi(IP, username, password, routing[model.upper()])
                                        if not result:
                                            update_status = "reboot_failed"
                                            break

            # if target=="MB_CPLD1" or "BPB" in target:
            # turn node back to on -- call power_on_node function
            # self.power_on()
            # not required to power on the node as it useful only after physical POWER CYCLE and we can't keep the track of the
            # physical power cycle so skipping it
                            if update_status.lower() == "success":
                                # call version of respective target and store versions after update
                                time.sleep(180)  # extra time requiring as of now for systems under test
                                if target != "BPB_CPLD" and target != "SCM_CPLD1" and target != "MB_CPLD1":
                                    after_version = self.get_fw_version(target)
                            else:
                                if target != "BPB_CPLD" and target != "SCM_CPLD1" and target != "MB_CPLD1":
                                    after_version = "NA"
                                update_status = "failed"

            if target != "BPB_CPLD" and target != "SCM_CPLD1" and target != "MB_CPLD1":
                return before_version, after_version, update_status
            else:
                return update_status

    def system_fw_update(self, attr):
        IP = attr.get('baseuri')
        username = attr.get('username')
        password = attr.get('password')
        image_type = attr.get('update_image_type')
        update_status = "Success"
        is_target_supported = False
        image_path = "NA"
        target = attr.get('update_target')
        image_path_inputs = {
            "HPE CRAY XD220V": attr.get('update_image_path_xd220V'),
            "HPE CRAY XD225V": attr.get('update_image_path_xd225V'),
            "HPE CRAY XD295V": attr.get('update_image_path_xd295V'),
            "HPE CRAY XD665": attr.get('update_image_path_xd665'),
            "HPE CRAY XD670": attr.get('update_image_path_xd670')}
        csv_file_name = attr.get('output_file_name')

        # Have a check that atleast one image path set based out of the above new logic
        if not any(image_path_inputs.values()):
            return {'ret': False, 'changed': True, 'msg': 'Must specify atleast one update_image_path'}

        if target == "" or target.upper() in unsupported_targets:
            return {'ret': False, 'changed': True, 'msg': 'Must specify the correct target for firmware update'}

        model = self.get_model()

        if not os.path.exists(csv_file_name):
            f = open(csv_file_name, "w")
            if target == "BPB_CPLD" or target == "SCM_CPLD1_MB_CPLD1":
                to_write = "IP_Address, Model, Update_Status, Remarks\n"
            else:
                to_write = "IP_Address, Model, " + target + '_Pre_Ver, ' + target + '_Post_Ver, ' + "Update_Status\n"
            f.write(to_write)
            f.close()

        # check if model is Cray XD670 and target is BMC assign default value of BMC as BMCImage1
        if model.upper() == "HPE CRAY XD670" and target == "BMC":
            target = "BMCImage1"

        if model.upper() not in supported_models:
            update_status = "unsupported_model"
            if target == "SCM_CPLD1_MB_CPLD1" or target == "BPB_CPLD":
                lis = [IP, model, update_status, "NA"]
            else:
                lis = [IP, model, "NA", "NA", update_status]
            new_data = ", ".join(lis)
            return {'ret': True, 'changed': True, 'msg': str(new_data)}
        else:
            image_path = image_path_inputs[model.upper()]
            if model.upper() == "HPE CRAY XD670" and "CPLD" in target.upper():
                power_state = self.power_state()
                if power_state.lower() != "on":
                    update_status = "NA"
                    lis = [IP, model, update_status, "node is not ON, please power on the node"]
                    new_data = ", ".join(lis)
                    return {'ret': True, 'changed': True, 'msg': str(new_data)}
                elif target == 'SCM_CPLD1_MB_CPLD1':
                    is_target_supported = True
                    image_paths = image_path_inputs["HPE CRAY XD670"].split()
                    if len(image_paths) != 2:
                        return {'ret': False, 'changed': True, 'msg': '''Must specify exactly 2 image_paths,
                                first for SCM_CPLD1 of Cray XD670 and second for MB_CPLD1 of Cray XD670'''}
                    for img_path in image_paths:
                        if not os.path.isfile(img_path):
                            return {'ret': False, 'changed': True,
                                    'msg': '''Must specify correct image_paths for SCM_CPLD1_MB_CPLD1, first for SCM_CPLD1
                                    of Cray XD670 and second for MB_CPLD1 of Cray XD670'''}

            if target != "SCM_CPLD1_MB_CPLD1" and not os.path.isfile(image_path):
                update_status = "NA_fw_file_absent"
                if target == "BPB_CPLD":
                    lis = [IP, model, update_status, "NA"]
                else:
                    lis = [IP, model, "NA", "NA", update_status]
                new_data = ", ".join(lis)
                return {'ret': True, 'changed': True, 'msg': str(new_data)}
            else:
                if target != "SCM_CPLD1_MB_CPLD1" and target != "BPB_CPLD":
                    is_target_supported = self.target_supported(model, target)
                if model.upper() == "HPE CRAY XD670" and (target == "BMC" or target == "BPB_CPLD"):
                    is_target_supported = True

                if not is_target_supported:
                    update_status = "target_not_supported"
                    if target == "SCM_CPLD1_MB_CPLD1" or target == "BPB_CPLD":
                        lis = [IP, model, update_status, "NA"]
                    else:
                        lis = [IP, model, "NA", "NA", update_status]
                    new_data = ", ".join(lis)
                    return {'ret': True, 'changed': True, 'msg': str(new_data)}
                else:
                    # check if model is Cray XD670 and target is BMC assign default value of BMC as BMCImage1
                    if model.upper() == "HPE CRAY XD670" and target == "BMC":
                        target = "BMCImage1"

                    # call version of respective target and store versions before update
                    if target == "SCM_CPLD1_MB_CPLD1":
                        update_status = self.helper_update(update_status, "SCM_CPLD1", image_paths[0], image_type, IP, username, password, "HPE Cray XD670")
                        if update_status.lower() == "success":
                            # SCM has updates successfully, proceed for MB_CPLD1 update
                            # check node to be off -- call power_off_node function
                            power_state = self.power_state()
                            if power_state.lower() == "on":
                                self.power_off()
                                power_state = self.power_state()
                                if power_state.lower() == "on":
                                    lis = [IP, model, "NA", "MB_CPLD1 requires node off, tried powering off the node, but failed to power off"]
                                    update_status = self.helper_update(update_status, "MB_CPLD1",
                                                                       image_paths[1], image_type, IP, username, password, "HPE Cray XD670")
                                    if update_status.lower() == "success":
                                        remarks = "Please plug out and plug in power cables physically"
                                    else:
                                        remarks = "Please reflash the firmware and DO NOT DO physical power cycle"
                                    lis = [IP, model, update_status, remarks]
                    elif target == "BPB_CPLD":
                        update_status = self.helper_update(update_status, target, image_path, image_type, IP, username, password, model)
                        if update_status.lower() == "success":
                            remarks = "Please plug out and plug in power cables physically"
                        else:
                            remarks = "Please reflash the firmware and DO NOT DO physical power cycle"
                        lis = [IP, model, update_status, remarks]
                    else:
                        bef_ver, aft_ver, update_status = self.helper_update(update_status, target, image_path, image_type, IP, username, password, model)
                        lis = [IP, model, bef_ver, aft_ver, update_status]
                    new_data = ", ".join(lis)
                    return {'ret': True, 'changed': True, 'msg': str(new_data)}

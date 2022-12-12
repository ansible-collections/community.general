# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
import os
import tempfile
import zipfile
import shutil
import sys
import time
import json
from string import ascii_lowercase
from random import choice
import redfish

__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils


class FwpkgError(Exception):
    """Baseclass for all fwpkg exceptions"""

    errcode = 1

    def __init__(self, message=None):
        Exception.__init__(self, message)


class TaskQueueError(FwpkgError):
    """Raised when there is an issue with the current order of taskqueue"""

    pass


class FirmwareUpdateError(FwpkgError):
    """Raised when there is an error while updating firmware"""

    pass


class UploadError(FwpkgError):
    """Raised when the component fails to download"""

    pass


class InvalidFileInputError(FwpkgError):
    """Raised when user enter an invalid file input"""

    pass


class IncompatibleiLOVersionError(FwpkgError):
    """Raised when iLo version is not compatible"""

    pass


class UploadError(FwpkgError):
    """Raised when the component fails to download"""

    pass


class TimeOutError(FwpkgError):
    """Raised when the update service times out"""

    pass


class UnsuccesfulRequest(FwpkgError):
    """ Raised when a HTTP request in unsuccessful"""

    pass


class iLORedfishUtils(RedfishUtils):

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

    def preparefwpkg(self, fwpkg_file):

        imagefiles = []
        tempdir = tempfile.mkdtemp()

        try:
            zfile = zipfile.ZipFile(fwpkg_file)
            zfile.extractall(tempdir)
            zfile.close()
        except Exception as excp:
            raise InvalidFileInputError("Unable to unpack file. " + str(excp))

        files = os.listdir(tempdir)

        if "payload.json" in files:
            with open(os.path.join(tempdir, "payload.json"), encoding="utf-8") as pfile:
                data = pfile.read()
            payloaddata = json.loads(data)
        else:
            raise InvalidFileInputError(
                "Unable to find payload.json in fwpkg file.")

        comptype = self.get_comp_type(payloaddata)

        results = self.get_request(
            self.root_uri + self.service_root + "UpdateService/")
        if not results['ret']:
            raise UnsuccesfulRequest(
                "Request is not completed successfully. " + str(results))

        for device in payloaddata["Devices"]["Device"]:
            for firmwareimage in device["FirmwareImages"]:
                if firmwareimage["FileName"] not in imagefiles:
                    imagefiles.append(firmwareimage["FileName"])

        if comptype == 'A' and payloaddata['PackageFormat'] == 'FWPKG-v2':
            imagefiles = [fwpkg_file]

        return imagefiles, tempdir, comptype

    def get_comp_type(self, payloaddata):

        ctype = ""

        if "Uefi" in payloaddata["UpdatableBy"] and "RuntimeAgent" in payloaddata["UpdatableBy"]:
            ctype = "D"
        elif "UEFI" in payloaddata["UpdatableBy"] and "Bmc" in payloaddata["UpdatableBy"]:
            data = None
            results = self.get_request(
                self.root_uri + self.service_root + "UpdateService/")
            if not results['ret']:
                raise UnsuccesfulRequest(
                    "Request is not completed successfully. " + str(results))

            data1 = results['data']
            if "FirmwareInventory" in data1:
                results = self.get_request(
                    self.root_uri + data1["FirmwareInventory"]["@odata.id"])
                if not results['ret']:
                    raise UnsuccesfulRequest(
                        "Request is not completed successfully. " + str(results))
                data = results['data']
            if data is not None:
                type_set = None
                for fw in data:
                    for device in payloaddata["Devices"]["Device"]:
                        if fw["Oem"]["Hpe"].get("Targets") is not None:
                            if device["Target"] in fw["Oem"]["Hpe"]["Targets"]:
                                if fw["Updateable"] and (payloaddata['PackageFormat'] == 'FWPKG-v2'):
                                    ctype = "A"
                                    type_set = True
                                else:
                                    ctype = "C"
                                    type_set = True
                if type_set is None:
                    raise IncompatibleiLOVersionError(
                        "Cannot flash the component on this server, server is not VROC enabled\n"
                    )
        else:
            for device in payloaddata["Devices"]["Device"]:
                for image in device["FirmwareImages"]:
                    if "DirectFlashOk" not in list(image.keys()):
                        raise InvalidFileInputError(
                            "Cannot flash this firmware.")
                    if image["DirectFlashOk"]:
                        ctype = "A"
                        if image["ResetRequired"]:
                            ctype = "B"
                            break
                    elif image["UefiFlashable"]:
                        ctype = "C"
                        break
                    else:
                        ctype = "D"

        return ctype

    def findcompsig(self, comppath):
        compsig = ""

        cutpath = comppath.split(os.sep)
        _file = cutpath[-1]
        _file_rev = _file[::-1]
        filename = _file[: ((_file_rev.find(".")) * -1) - 1]

        try:
            location = os.sep.join(cutpath[:-1])
        except:
            location = os.curdir

        if not location:
            location = os.curdir

        files = [
            f for f in os.listdir(location) if os.path.isfile(os.path.join(location, f))
        ]

        for filehndl in files:
            if filehndl.startswith(filename) and filehndl.endswith(".compsig"):
                if location != ".":
                    compsig = location + os.sep + filehndl
                else:
                    compsig = filehndl

                break

        return compsig

    def check_and_split(self, options):

        def check_file_rw(filename, rw):
            try:
                fd = open(filename, rw)
                fd.close()
            except IOError:
                raise InvalidFileInputError(
                    "The file '%s' could not be opened for upload" % filename
                )

        maxcompsize = 32 * 1024 * 1024
        filelist = []

        # Get the component filename
        _, filename = os.path.split(options["component"])
        check_file_rw(os.path.normpath(options["component"]), "r")
        size = os.path.getsize(options["component"])

        if not options["componentsig"]:
            if not self.findcompsig(filename):
                return [(filename, options["component"], options["componentsig"], 0)]

        if size > maxcompsize:
            section = 1

            sigpath, _ = os.path.split(options["componentsig"])
            check_file_rw(os.path.normpath(options["componentsig"]), "r")
            filebasename = filename[: filename.rfind(".")]
            tempfoldername = "bmn" + \
                "".join(choice(ascii_lowercase) for i in range(12))

            tempdir = os.path.join(sys.executable, tempfoldername)

            if not os.path.exists(tempdir):
                os.makedirs(tempdir)

            with open(options["component"], "rb") as component:
                while True:
                    data = component.read(maxcompsize)
                    if len(data) != 0:
                        sectionfilename = filebasename + "_part" + str(section)
                        sectionfilepath = os.path.join(
                            tempdir, sectionfilename)

                        sectioncompsigpath = os.path.join(
                            sigpath, sectionfilename + ".compsig"
                        )
                        sigfullpath = os.path.join(tempdir, sigpath)
                        if not os.path.exists(sigfullpath):
                            os.makedirs(sigfullpath)
                        writefile = open(sectionfilepath, "wb")
                        writefile.write(data)
                        writefile.close()

                        item = (
                            filename,
                            sectionfilepath,
                            sectioncompsigpath,
                            section - 1,
                        )

                        filelist.append(item)
                        section += 1

                    if len(data) != maxcompsize:
                        break

            return filelist
        else:
            return [(filename, options["component"], options["componentsig"], 0)]

    def componentvalidation(self, options, filestoupload):
        ret = {}
        ret["validation"] = True
        prevfile = None

        path = "/redfish/v1/UpdateService/ComponentRepository/?$expand=."
        results = self.get_request(self.root_uri + path)
        if not results['ret']:
            raise UnsuccesfulRequest(
                "Request is not completed successfully. " + str(results))
        results = results['data']

        if "Members" in results and results["Members"]:
            for comp in results["Members"]:
                for filehndl in filestoupload:
                    if (
                        comp["Filename"].upper() == str(filehndl[0]).upper()
                        and not options["forceupload"]
                        and prevfile != filehndl[0].upper()
                    ):

                        if not options["overwrite"]:
                            ret["msg"] = "Upload stopped by user due to filename conflict. If you would like to bypass this check include the --forceupload option"
                            ret["validation"] = False
                            break

                    if options["update_repository"]:
                        if (
                            comp["Filename"].upper() == str(
                                filehndl[0]).upper()
                            and prevfile != filehndl[0].upper()
                            and comp["Locked"]
                        ):
                            ret["msg"] = "Error: Component is currently locked by a taskqueue task or installset. \n Remove any installsets or taskqueue tasks containing the file and try again OR use taskqueue command to put the component to installation queue\n"
                            ret["validation"] = False
                            break
                    prevfile = str(comp["Filename"].upper())
        return ret

    def get_update_service_state(self):

        path = "/redfish/v1/UpdateService"
        results = self.get_request(self.root_uri + path)

        if results["ret"]:
            output = results["data"]
            return (output["Oem"]["Hpe"]["State"]).upper(), results["data"]
        else:
            return "UNKNOWN", {}

    def wait_for_state_change(self, wait_time=4800):

        total_time = 0
        state = ""
    
        while total_time < wait_time:
            state, _ = self.get_update_service_state()

            if state == "ERROR":
                return False
            elif state != "COMPLETED" and state != "IDLE" and state != "COMPLETE":
                # Lets try again after 8 seconds
                count = 0

                # fancy spinner
                while count <= 32:
                    time.sleep(0.25)
                    count += 1

                total_time += 8
            else:
                break

        if total_time > wait_time:
            raise TimeOutError(
                "UpdateService in " + state +
                " state for " + str(wait_time) + "s"
            )

        return True

    def uploadfunction(self, filestoupload, options):

        state, result = self.get_update_service_state()
        ret = {}
        if (
            state != "COMPLETED"
            and state != "COMPLETE"
            and state != "ERROR"
            and state != "IDLE"
        ):
            ret["msg"] = "iLO UpdateService is busy. Please try again."
            ret["ret"] = False
            return ret

        etag = ""
        hpe = result["Oem"]["Hpe"]
        urltosend = "/cgi-bin/uploadFile"

        if "PushUpdateUri" in hpe:
            urltosend = hpe["PushUpdateUri"]
        elif "HttpPushUri" in result:
            urltosend = result["HttpPushUri"]
        else:
            ret["msg"] = "Failed to upload component"
            ret["ret"] = False
            return ret

        for item in filestoupload:
            ilo_upload_filename = item[0]

            ilo_upload_compsig_filename = (
                ilo_upload_filename[: ilo_upload_filename.rfind(
                    ".")] + ".compsig"
            )

            componentpath = item[1]
            compsigpath = item[2]

            _, filename = os.path.split(componentpath)

            if not etag:
                etag = "sum" + filename.replace(".", "")
                etag = etag.replace("-", "")
                etag = etag.replace("_", "")

            section_num = item[3]

            user = self.creds['user']
            pwd = self.creds['pswd']
            baseurl = self.root_uri

            redfish_obj = redfish.RedfishClient(base_url=baseurl, username=user, password=pwd)
            redfish_obj.login()
            session_key = redfish_obj.session_key

            parameters = {
                "UpdateRepository": options["update_repository"],
                "UpdateTarget": options["update_target"],
                "ETag": etag,
                "Section": section_num,
                "UpdateRecoverySet": options["update_srs"],
            }

            data = [("sessionKey", session_key), ("parameters", json.dumps(parameters))]

            if not compsigpath:
                compsigpath = self.findcompsig(componentpath)
            if compsigpath:
                with open(compsigpath, "rb") as fle:
                    output = fle.read()
                data.append(
                    (
                        "compsig",
                        (
                            ilo_upload_compsig_filename,
                            output,
                            "application/octet-stream",
                        ),
                    )
                )
                output = None

            with open(componentpath, "rb") as fle:
                output = fle.read()

            data.append(
                ("file", (ilo_upload_filename, output, "application/octet-stream"))
            )

            headers = {'Cookie': 'sessionKey='+session_key, 'X-Auth-Token': session_key, 'OData-Version': '4.0'}

            args = None

            results = redfish_obj.post(str(urltosend), data, args=args, headers=headers)

            if results.status == 200:
                ret["ret"] = True
                ret["msg"] = "Uploaded successfully"
                
            else:
                ret["msg"] = "iLO UpdateService is busy. Please try again."
                ret["ret"] = False
                return ret

            if not self.wait_for_state_change():
                raise UploadError("Error while processing the component.")

        return ret

    def human_readable_time(self, seconds):

        seconds = int(seconds)
        hours = seconds / 3600
        seconds = seconds % 3600
        minutes = seconds / 60
        seconds = seconds % 60

        return "{:02.0f} hour(s) {:02.0f} minute(s) {:02.0f} second(s) ".format(
            hours, minutes, seconds
        )

    def uploadcomp(self, options):
        fwpkg = False
        result = {}
        if options["component"].endswith(".fwpkg"):
            comp, loc, ctype = self.preparefwpkg(options["component"])

        filestoupload = self.check_and_split(options)

        return_val = self.componentvalidation(options, filestoupload)

        if return_val['validation']:
            start_time = time.time()
            result["ret"] = False

            rec_res = self.uploadfunction(filestoupload, options)
            if rec_res["ret"]:
                result["ret"] = True
                result["msg"] = rec_res["msg"] + "\n"
                result["msg"] += str(self.human_readable_time(time.time() - start_time))

            if len(filestoupload) > 1:
                path, _ = os.path.split((filestoupload[0])[1])
                shutil.rmtree(path)
            elif fwpkg:
                if os.path.exists(loc):
                    shutil.rmtree(loc)
        else:
            return_val["ret"] = False
            return return_val

        return result

    def applyfwpkg(self, options, tempdir, components, comptype):

        for component in components:
            if component.endswith(".fwpkg") or component.endswith(".zip"):
                options["component"] = component
            else:
                options["component"] = os.path.join(tempdir, component)

            if comptype in ["A", "B"]:
                options["update_target"] = True
                options["update_repository"] = True

            if options["update_srs"]:
                options["update_srs"] = True

            try:
                ret = self.uploadcomp(options)
                if not ret['ret']:
                    raise UploadError
                return ret
            except UploadError:
                if comptype in ["A", "B"]:
                    results = self.get_request(
                        self.root_uri + self.service_root + "UpdateService/")
                    if not results["ret"]:
                        raise UnsuccesfulRequest(
                            "Request is not completed successfully. " + str(results))

                    if results:
                        check = "Error occured while uploading the firmware"
                        raise UnsuccesfulRequest(check)
                    else:
                        raise FirmwareUpdateError(
                            "Error occurred while updating the firmware."
                        )
                else:
                    raise UploadError("Error uploading component.")

    def flash_firmware(self, options):
        resource = self._find_managers_resource()
        response = self.get_request(self.root_uri + self.manager_uri)
        if response['ret'] is False:
            return response

        version = float(response['data']['FirmwareVersion'][4] + "." + response['data']
                        ['FirmwareVersion'][7] + response['data']['FirmwareVersion'][9:11])
       
        if version <= 5.120 and options["fwpkgfile"].lower().startswith("iegen10"):
            raise IncompatibleiLOVersionError(
                "Please upgrade to iLO 5 1.20 or greater to ensure correct flash of this firmware."
            )

        if not options["fwpkgfile"].endswith(".fwpkg"):
            raise InvalidFileInputError(
                "Invalid file type. Please make sure the file provided is a valid .fwpkg file type."
            )

        result = {}
        tempdir = ""

        try:
            components, tempdir, comptype = self.preparefwpkg(
                options["fwpkgfile"])
            if comptype == "D":
                raise InvalidFileInputError("Unable to flash this fwpkg file.")

            final = self.applyfwpkg(options, tempdir, components, comptype)
            result = {}
            if final["ret"]:
                result["msg"] = final["msg"]+"\n"
                if comptype == "A":
                    result['msg'] += "Firmware has successfully been flashed. \n "
                    if "ilo" in options["fwpkgfile"].lower():
                        result['msg'] += "iLO will reboot to complete flashing. Session will be terminated."

                elif comptype == "B":
                    result['msg'] += "Firmware has successfully been flashed and a reboot is required for this firmware to take effect.\n"

                elif comptype == "C":
                    result['msg'] += "This firmware is set to flash on reboot.\n"
                result['ret'] = True
                result['changed'] = True

            else:
                result["ret"] = False
                result["msg"] = final.get("msg")           

        except (FirmwareUpdateError, UploadError) as excp:
            raise excp

        finally:
            if tempdir:
                shutil.rmtree(tempdir)
        return result
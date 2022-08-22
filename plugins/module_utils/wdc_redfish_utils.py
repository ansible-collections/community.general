# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import datetime
import re
import time
import tarfile

from ansible.module_utils.urls import fetch_file
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils

from ansible.module_utils.six.moves.urllib.parse import urlparse, urlunparse


class WdcRedfishUtils(RedfishUtils):
    """Extension to RedfishUtils to support WDC enclosures."""
    # Status codes returned by WDC FW Update Status
    UPDATE_STATUS_CODE_READY_FOR_FW_UPDATE = 0
    UPDATE_STATUS_CODE_FW_UPDATE_IN_PROGRESS = 1
    UPDATE_STATUS_CODE_FW_UPDATE_COMPLETED_WAITING_FOR_ACTIVATION = 2
    UPDATE_STATUS_CODE_FW_UPDATE_FAILED = 3

    # Status messages returned by WDC FW Update Status
    UPDATE_STATUS_MESSAGE_READY_FOR_FW_UDPATE = "Ready for FW update"
    UDPATE_STATUS_MESSAGE_FW_UPDATE_IN_PROGRESS = "FW update in progress"
    UPDATE_STATUS_MESSAGE_FW_UPDATE_COMPLETED_WAITING_FOR_ACTIVATION = "FW update completed. Waiting for activation."
    UPDATE_STATUS_MESSAGE_FW_UPDATE_FAILED = "FW update failed."

    # Dict keys for resource bodies
    # Standard keys
    ACTIONS = "Actions"
    OEM = "Oem"
    WDC = "WDC"
    TARGET = "target"

    # Keys for specific operations
    CHASSIS_LOCATE = "#Chassis.Locate"
    CHASSIS_POWER_MODE = "#Chassis.PowerMode"

    def __init__(self,
                 creds,
                 root_uris,
                 timeout,
                 module,
                 resource_id,
                 data_modification):
        super(WdcRedfishUtils, self).__init__(creds=creds,
                                              root_uri=root_uris[0],
                                              timeout=timeout,
                                              module=module,
                                              resource_id=resource_id,
                                              data_modification=data_modification)
        # Update the root URI if we cannot perform a Redfish GET to the first one
        self._set_root_uri(root_uris)

    def _set_root_uri(self, root_uris):
        """Set the root URI from a list of options.

        If the current root URI is good, just keep it.  Else cycle through our options until we find a good one.
        A URI is considered good if we can GET uri/redfish/v1.
        """
        for root_uri in root_uris:
            uri = root_uri + "/redfish/v1"
            response = self.get_request(uri)
            if response['ret']:
                self.root_uri = root_uri
                break

    def _find_updateservice_resource(self):
        """Find the update service resource as well as additional WDC-specific resources."""
        response = super(WdcRedfishUtils, self)._find_updateservice_resource()
        if not response['ret']:
            return response
        return self._find_updateservice_additional_uris()

    def _is_enclosure_multi_tenant(self):
        """Determine if the enclosure is multi-tenant.

        The serial number of a multi-tenant enclosure will end in "-A" or "-B".

        :return: True/False if the enclosure is multi-tenant or not; None if unable to determine.
        """
        response = self.get_request(self.root_uri + self.service_root + "Chassis/Enclosure")
        if response['ret'] is False:
            return None
        pattern = r".*-[A,B]"
        data = response['data']
        return re.match(pattern, data['SerialNumber']) is not None

    def _find_updateservice_additional_uris(self):
        """Find & set WDC-specific update service URIs"""
        response = self.get_request(self.root_uri + self._update_uri())
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
        self.simple_update_uri = action['target']

        # Simple update status URI is not provided via GET /redfish/v1/UpdateService
        # So we have to hard code it.
        self.simple_update_status_uri = "{0}/Status".format(self.simple_update_uri)

        # FWActivate URI
        if 'Oem' not in data['Actions']:
            return {'ret': False, 'msg': 'Service does not support OEM operations'}
        if 'WDC' not in data['Actions']['Oem']:
            return {'ret': False, 'msg': 'Service does not support WDC operations'}
        if '#UpdateService.FWActivate' not in data['Actions']['Oem']['WDC']:
            return {'ret': False, 'msg': 'Service does not support FWActivate'}
        action = data['Actions']['Oem']['WDC']['#UpdateService.FWActivate']
        if 'target' not in action:
            return {'ret': False, 'msg': 'Service does not support FWActivate'}
        self.firmware_activate_uri = action['target']
        return {'ret': True}

    def _simple_update_status_uri(self):
        return self.simple_update_status_uri

    def _firmware_activate_uri(self):
        return self.firmware_activate_uri

    def _update_uri(self):
        return self.update_uri

    def get_simple_update_status(self):
        """Issue Redfish HTTP GET to return the simple update status"""
        result = {}
        response = self.get_request(self.root_uri + self._simple_update_status_uri())
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        result['entries'] = data
        return result

    def firmware_activate(self, update_opts):
        """Perform FWActivate using Redfish HTTP API."""
        creds = update_opts.get('update_creds')
        payload = {}
        if creds:
            if creds.get('username'):
                payload["Username"] = creds.get('username')
            if creds.get('password'):
                payload["Password"] = creds.get('password')

        # Make sure the service supports FWActivate
        response = self.get_request(self.root_uri + self._update_uri())
        if response['ret'] is False:
            return response
        data = response['data']
        if 'Actions' not in data:
            return {'ret': False, 'msg': 'Service does not support FWActivate'}

        response = self.post_request(self.root_uri + self._firmware_activate_uri(), payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True,
                'msg': "FWActivate requested"}

    def _get_bundle_version(self,
                            bundle_uri):
        """Get the firmware version from a bundle file, and whether or not it is multi-tenant.

        Only supports HTTP at this time.  Assumes URI exists and is a tarfile.
        Looks for a file oobm-[version].pkg, such as 'oobm-4.0.13.pkg`.  Extracts the version number
        from that filename (in the above example, the version number is "4.0.13".

        To determine if the bundle is multi-tenant or not, it looks inside the .bin file within the tarfile,
        and checks the appropriate byte in the file.

        :param str bundle_uri:  HTTP URI of the firmware bundle.
        :return: Firmware version number contained in the bundle, and whether or not the bundle is multi-tenant.
        Either value will be None if unable to deterine.
        :rtype: str or None, bool or None
        """
        bundle_temp_filename = fetch_file(module=self.module,
                                          url=bundle_uri)
        if not tarfile.is_tarfile(bundle_temp_filename):
            return None, None
        tf = tarfile.open(bundle_temp_filename)
        pattern_pkg = r"oobm-(.+)\.pkg"
        pattern_bin = r"(.*\.bin)"
        bundle_version = None
        is_multi_tenant = None
        for filename in tf.getnames():
            match_pkg = re.match(pattern_pkg, filename)
            if match_pkg is not None:
                bundle_version = match_pkg.group(1)
            match_bin = re.match(pattern_bin, filename)
            if match_bin is not None:
                bin_filename = match_bin.group(1)
                bin_file = tf.extractfile(bin_filename)
                bin_file.seek(11)
                byte_11 = bin_file.read(1)
                is_multi_tenant = byte_11 == b'\x80'

        return bundle_version, is_multi_tenant

    @staticmethod
    def uri_is_http(uri):
        """Return True if the specified URI is http or https.

        :param str uri: A URI.
        :return: True if the URI is http or https, else False
        :rtype: bool
        """
        parsed_bundle_uri = urlparse(uri)
        return parsed_bundle_uri.scheme.lower() in ['http', 'https']

    def update_and_activate(self, update_opts):
        """Update and activate the firmware in a single action.

        Orchestrates the firmware update so that everything can be done in a single command.
        Compares the update version with the already-installed version -- skips update if they are the same.
        Performs retries, handles timeouts as needed.

        """
        # Convert credentials to standard HTTP format
        if update_opts.get("update_creds") is not None and "username" in update_opts["update_creds"] and "password" in update_opts["update_creds"]:
            update_creds = update_opts["update_creds"]
            parsed_url = urlparse(update_opts["update_image_uri"])
            if update_creds:
                original_netloc = parsed_url.netloc
                parsed_url = parsed_url._replace(netloc="{0}:{1}@{2}".format(update_creds.get("username"),
                                                                             update_creds.get("password"),
                                                                             original_netloc))
                update_opts["update_image_uri"] = urlunparse(parsed_url)
                del update_opts["update_creds"]

        # Make sure bundle URI is HTTP(s)
        bundle_uri = update_opts["update_image_uri"]

        if not self.uri_is_http(bundle_uri):
            return {
                'ret': False,
                'msg': 'Bundle URI must be HTTP or HTTPS'
            }
        # Make sure IOM is ready for update
        result = self.get_simple_update_status()
        if result['ret'] is False:
            return result
        update_status = result['entries']
        status_code = update_status['StatusCode']
        status_description = update_status['Description']
        if status_code not in [
            self.UPDATE_STATUS_CODE_READY_FOR_FW_UPDATE,
            self.UPDATE_STATUS_CODE_FW_UPDATE_FAILED
        ]:
            return {
                'ret': False,
                'msg': 'Target is not ready for FW update.  Current status: {0} ({1})'.format(
                    status_code, status_description
                )}

        # Check the FW version in the bundle file, and compare it to what is already on the IOMs

        # Bundle version number
        bundle_firmware_version, is_bundle_multi_tenant = self._get_bundle_version(bundle_uri)
        if bundle_firmware_version is None or is_bundle_multi_tenant is None:
            return {
                'ret': False,
                'msg': 'Unable to extract bundle version or multi-tenant status from update image tarfile'
            }

        # Verify that the bundle is correctly multi-tenant or not
        is_enclosure_multi_tenant = self._is_enclosure_multi_tenant()
        if is_enclosure_multi_tenant != is_bundle_multi_tenant:
            return {
                'ret': False,
                'msg': 'Enclosure multi-tenant is {0} but bundle multi-tenant is {1}'.format(
                    is_enclosure_multi_tenant,
                    is_bundle_multi_tenant,
                )
            }

        # Version number installed on IOMs
        firmware_inventory = self.get_firmware_inventory()
        if not firmware_inventory["ret"]:
            return firmware_inventory
        firmware_inventory_dict = {}
        for entry in firmware_inventory["entries"]:
            firmware_inventory_dict[entry["Id"]] = entry
        iom_a_firmware_version = firmware_inventory_dict.get("IOModuleA_OOBM", {}).get("Version")
        iom_b_firmware_version = firmware_inventory_dict.get("IOModuleB_OOBM", {}).get("Version")
        # If version is None, we will proceed with the update, because we cannot tell
        # for sure that we have a full version match.
        if is_enclosure_multi_tenant:
            # For multi-tenant, only one of the IOMs will be affected by the firmware update,
            # so see if that IOM already has the same firmware version as the bundle.
            firmware_already_installed = bundle_firmware_version == self._get_installed_firmware_version_of_multi_tenant_system(
                iom_a_firmware_version,
                iom_b_firmware_version)
        else:
            # For single-tenant, see if both IOMs already have the same firmware version as the bundle.
            firmware_already_installed = bundle_firmware_version == iom_a_firmware_version == iom_b_firmware_version
        # If this FW already installed, return changed: False, and do not update the firmware.
        if firmware_already_installed:
            return {
                'ret': True,
                'changed': False,
                'msg': 'Version {0} already installed'.format(bundle_firmware_version)
            }

        # Version numbers don't match the bundle -- proceed with update (unless we are in check mode)
        if self.module.check_mode:
            return {
                'ret': True,
                'changed': True,
                'msg': 'Update not performed in check mode.'
            }
        update_successful = False
        retry_interval_seconds = 5
        max_number_of_retries = 5
        retry_number = 0
        while retry_number < max_number_of_retries and not update_successful:
            if retry_number != 0:
                time.sleep(retry_interval_seconds)
            retry_number += 1

            result = self.simple_update(update_opts)
            if result['ret'] is not True:
                # Sometimes a timeout error is returned even though the update actually was requested.
                # Check the update status to see if the update is in progress.
                status_result = self.get_simple_update_status()
                if status_result['ret'] is False:
                    continue
                update_status = status_result['entries']
                status_code = update_status['StatusCode']
                if status_code != self.UPDATE_STATUS_CODE_FW_UPDATE_IN_PROGRESS:
                    # Update is not in progress -- retry until max number of retries
                    continue
                else:
                    update_successful = True
            else:
                update_successful = True
        if not update_successful:
            # Unable to get SimpleUpdate to work.  Return the failure from the SimpleUpdate
            return result

        # Wait for "ready to activate"
        max_wait_minutes = 30
        polling_interval_seconds = 30
        status_code = self.UPDATE_STATUS_CODE_READY_FOR_FW_UPDATE
        start_time = datetime.datetime.now()
        # For a short time, target will still say "ready for firmware update" before it transitions
        # to "update in progress"
        status_codes_for_update_incomplete = [
            self.UPDATE_STATUS_CODE_FW_UPDATE_IN_PROGRESS,
            self.UPDATE_STATUS_CODE_READY_FOR_FW_UPDATE
        ]
        iteration = 0
        while status_code in status_codes_for_update_incomplete \
                and datetime.datetime.now() - start_time < datetime.timedelta(minutes=max_wait_minutes):
            if iteration != 0:
                time.sleep(polling_interval_seconds)
            iteration += 1
            result = self.get_simple_update_status()
            if result['ret'] is False:
                continue  # We may get timeouts, just keep trying until we give up
            update_status = result['entries']
            status_code = update_status['StatusCode']
            status_description = update_status['Description']
            if status_code == self.UPDATE_STATUS_CODE_FW_UPDATE_IN_PROGRESS:
                # Once it says update in progress, "ready for update" is no longer a valid status code
                status_codes_for_update_incomplete = [self.UPDATE_STATUS_CODE_FW_UPDATE_IN_PROGRESS]

        # Update no longer in progress -- verify that it finished
        if status_code != self.UPDATE_STATUS_CODE_FW_UPDATE_COMPLETED_WAITING_FOR_ACTIVATION:
            return {
                'ret': False,
                'msg': 'Target is not ready for FW activation after update.  Current status: {0} ({1})'.format(
                    status_code, status_description
                )}

        self.firmware_activate(update_opts)
        return {'ret': True, 'changed': True,
                'msg': "Firmware updated and activation initiated."}

    def _get_installed_firmware_version_of_multi_tenant_system(self,
                                                               iom_a_firmware_version,
                                                               iom_b_firmware_version):
        """Return the version for the active IOM on a multi-tenant system.

        Only call this on a multi-tenant system.
        Given the installed firmware versions for IOM A, B, this method will determine which IOM is active
        for this tenanat, and return that IOM's firmware version.
        """
        # To determine which IOM we are on, try to GET each IOM resource
        # The one we are on will return valid data.
        # The other will return an error with message "IOM Module A/B cannot be read"
        which_iom_is_this = None
        for iom_letter in ['A', 'B']:
            iom_uri = "Chassis/IOModule{0}FRU".format(iom_letter)
            response = self.get_request(self.root_uri + self.service_root + iom_uri)
            if response['ret'] is False:
                continue
            data = response['data']
            if "Id" in data:  # Assume if there is an "Id", it is valid
                which_iom_is_this = iom_letter
                break
        if which_iom_is_this == 'A':
            return iom_a_firmware_version
        elif which_iom_is_this == 'B':
            return iom_b_firmware_version
        else:
            return None

    @staticmethod
    def _get_led_locate_uri(data):
        """Get the LED locate URI given a resource body."""
        if WdcRedfishUtils.ACTIONS not in data:
            return None
        if WdcRedfishUtils.OEM not in data[WdcRedfishUtils.ACTIONS]:
            return None
        if WdcRedfishUtils.WDC not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM]:
            return None
        if WdcRedfishUtils.CHASSIS_LOCATE not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC]:
            return None
        if WdcRedfishUtils.TARGET not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC][WdcRedfishUtils.CHASSIS_LOCATE]:
            return None
        return data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC][WdcRedfishUtils.CHASSIS_LOCATE][WdcRedfishUtils.TARGET]

    @staticmethod
    def _get_power_mode_uri(data):
        """Get the Power Mode URI given a resource body."""
        if WdcRedfishUtils.ACTIONS not in data:
            return None
        if WdcRedfishUtils.OEM not in data[WdcRedfishUtils.ACTIONS]:
            return None
        if WdcRedfishUtils.WDC not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM]:
            return None
        if WdcRedfishUtils.CHASSIS_POWER_MODE not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC]:
            return None
        if WdcRedfishUtils.TARGET not in data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC][WdcRedfishUtils.CHASSIS_POWER_MODE]:
            return None
        return data[WdcRedfishUtils.ACTIONS][WdcRedfishUtils.OEM][WdcRedfishUtils.WDC][WdcRedfishUtils.CHASSIS_POWER_MODE][WdcRedfishUtils.TARGET]

    def manage_indicator_led(self, command, resource_uri):
        key = 'IndicatorLED'

        payloads = {'IndicatorLedOn': 'On', 'IndicatorLedOff': 'Off'}
        current_led_status_map = {'IndicatorLedOn': 'Blinking', 'IndicatorLedOff': 'Off'}

        result = {}
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}
        current_led_status = data[key]
        if current_led_status == current_led_status_map[command]:
            return {'ret': True, 'changed': False}

        led_locate_uri = self._get_led_locate_uri(data)
        if led_locate_uri is None:
            return {'ret': False, 'msg': 'LED locate URI not found.'}

        if command in payloads.keys():
            payload = {'LocateState': payloads[command]}
            response = self.post_request(self.root_uri + led_locate_uri, payload)
            if response['ret'] is False:
                return response
        else:
            return {'ret': False, 'msg': 'Invalid command'}

        return result

    def manage_chassis_power_mode(self, command):
        return self.manage_power_mode(command, self.chassis_uri)

    def manage_power_mode(self, command, resource_uri=None):
        if resource_uri is None:
            resource_uri = self.chassis_uri

        payloads = {'PowerModeNormal': 'Normal', 'PowerModeLow': 'Low'}
        requested_power_mode = payloads[command]

        result = {}
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        # Make sure the response includes Oem.WDC.PowerMode, and get current power mode
        power_mode = 'PowerMode'
        if WdcRedfishUtils.OEM not in data or WdcRedfishUtils.WDC not in data[WdcRedfishUtils.OEM] or\
                power_mode not in data[WdcRedfishUtils.OEM][WdcRedfishUtils.WDC]:
            return {'ret': False, 'msg': 'Resource does not support Oem.WDC.PowerMode'}
        current_power_mode = data[WdcRedfishUtils.OEM][WdcRedfishUtils.WDC][power_mode]
        if current_power_mode == requested_power_mode:
            return {'ret': True, 'changed': False}

        power_mode_uri = self._get_power_mode_uri(data)
        if power_mode_uri is None:
            return {'ret': False, 'msg': 'Power Mode URI not found.'}

        if command in payloads.keys():
            payload = {'PowerMode': payloads[command]}
            response = self.post_request(self.root_uri + power_mode_uri, payload)
            if response['ret'] is False:
                return response
        else:
            return {'ret': False, 'msg': 'Invalid command'}

        return result

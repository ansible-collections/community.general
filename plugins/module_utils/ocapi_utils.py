# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import os
import uuid
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

from ansible.module_utils.urls import open_url
from ansible.module_utils.common.text.converters import to_native


GET_HEADERS = {"accept": "application/json"}
PUT_HEADERS = {"content-type": "application/json", "accept": "application/json"}
POST_HEADERS = {"content-type": "application/json", "accept": "application/json"}
DELETE_HEADERS = {"accept": "application/json"}

HEALTH_OK = 5


class OcapiUtils:
    def __init__(self, creds, base_uri, proxy_slot_number, timeout, module):
        self.root_uri = base_uri
        self.proxy_slot_number = proxy_slot_number
        self.creds = creds
        self.timeout = timeout
        self.module = module

    def _auth_params(self):
        """
        Return tuple of required authentication params based on the username and password.

        :return: tuple of username, password
        """
        username = self.creds["user"]
        password = self.creds["pswd"]
        force_basic_auth = True
        return username, password, force_basic_auth

    def get_request(self, uri):
        req_headers = dict(GET_HEADERS)
        username, password, basic_auth = self._auth_params()
        try:
            resp = open_url(
                uri,
                method="GET",
                headers=req_headers,
                url_username=username,
                url_password=password,
                force_basic_auth=basic_auth,
                validate_certs=False,
                follow_redirects="all",
                use_proxy=True,
                timeout=self.timeout,
            )
            data = json.loads(to_native(resp.read()))
            headers = {k.lower(): v for (k, v) in resp.info().items()}
        except HTTPError as e:
            return {"ret": False, "msg": f"HTTP Error {e.code} on GET request to '{uri}'", "status": e.code}
        except URLError as e:
            return {"ret": False, "msg": f"URL Error on GET request to '{uri}': '{e.reason}'"}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {"ret": False, "msg": f"Failed GET request to '{uri}': '{e}'"}
        return {"ret": True, "data": data, "headers": headers}

    def delete_request(self, uri, etag=None):
        req_headers = dict(DELETE_HEADERS)
        if etag is not None:
            req_headers["If-Match"] = etag
        username, password, basic_auth = self._auth_params()
        try:
            resp = open_url(
                uri,
                method="DELETE",
                headers=req_headers,
                url_username=username,
                url_password=password,
                force_basic_auth=basic_auth,
                validate_certs=False,
                follow_redirects="all",
                use_proxy=True,
                timeout=self.timeout,
            )
            if resp.status != 204:
                data = json.loads(to_native(resp.read()))
            else:
                data = ""
            headers = {k.lower(): v for (k, v) in resp.info().items()}
        except HTTPError as e:
            return {"ret": False, "msg": f"HTTP Error {e.code} on DELETE request to '{uri}'", "status": e.code}
        except URLError as e:
            return {"ret": False, "msg": f"URL Error on DELETE request to '{uri}': '{e.reason}'"}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {"ret": False, "msg": f"Failed DELETE request to '{uri}': '{e}'"}
        return {"ret": True, "data": data, "headers": headers}

    def put_request(self, uri, payload, etag=None):
        req_headers = dict(PUT_HEADERS)
        if etag is not None:
            req_headers["If-Match"] = etag
        username, password, basic_auth = self._auth_params()
        try:
            resp = open_url(
                uri,
                data=json.dumps(payload),
                headers=req_headers,
                method="PUT",
                url_username=username,
                url_password=password,
                force_basic_auth=basic_auth,
                validate_certs=False,
                follow_redirects="all",
                use_proxy=True,
                timeout=self.timeout,
            )
            headers = {k.lower(): v for (k, v) in resp.info().items()}
        except HTTPError as e:
            return {"ret": False, "msg": f"HTTP Error {e.code} on PUT request to '{uri}'", "status": e.code}
        except URLError as e:
            return {"ret": False, "msg": f"URL Error on PUT request to '{uri}': '{e.reason}'"}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {"ret": False, "msg": f"Failed PUT request to '{uri}': '{e}'"}
        return {"ret": True, "headers": headers, "resp": resp}

    def post_request(self, uri, payload, content_type="application/json", timeout=None):
        req_headers = dict(POST_HEADERS)
        if content_type != "application/json":
            req_headers["content-type"] = content_type
        username, password, basic_auth = self._auth_params()
        if content_type == "application/json":
            request_data = json.dumps(payload)
        else:
            request_data = payload
        try:
            resp = open_url(
                uri,
                data=request_data,
                headers=req_headers,
                method="POST",
                url_username=username,
                url_password=password,
                force_basic_auth=basic_auth,
                validate_certs=False,
                follow_redirects="all",
                use_proxy=True,
                timeout=self.timeout if timeout is None else timeout,
            )
            headers = {k.lower(): v for (k, v) in resp.info().items()}
        except HTTPError as e:
            return {"ret": False, "msg": f"HTTP Error {e.code} on POST request to '{uri}'", "status": e.code}
        except URLError as e:
            return {"ret": False, "msg": f"URL Error on POST request to '{uri}': '{e.reason}'"}
        # Almost all errors should be caught above, but just in case
        except Exception as e:
            return {"ret": False, "msg": f"Failed POST request to '{uri}': '{e}'"}
        return {"ret": True, "headers": headers, "resp": resp}

    def get_uri_with_slot_number_query_param(self, uri):
        """Return the URI with proxy slot number added as a query param, if there is one.

        If a proxy slot number is provided, to access it, we must append it as a query parameter.
        This method returns the given URI with the slotnumber query param added, if there is one.
        If there is not a proxy slot number, it just returns the URI as it was passed in.
        """
        if self.proxy_slot_number is not None:
            parsed_url = urlparse(uri)
            return parsed_url._replace(query=f"slotnumber={self.proxy_slot_number}").geturl()
        else:
            return uri

    def manage_system_power(self, command):
        """Process a command to manage the system power.

        :param str command: The Ansible command being processed.
        """
        if command == "PowerGracefulRestart":
            resource_uri = self.root_uri
            resource_uri = self.get_uri_with_slot_number_query_param(resource_uri)

            # Get the resource so that we have the Etag
            response = self.get_request(resource_uri)
            if "etag" not in response["headers"]:
                return {"ret": False, "msg": "Etag not found in response."}
            etag = response["headers"]["etag"]
            if response["ret"] is False:
                return response

            # Issue the PUT to do the reboot (unless we are in check mode)
            if self.module.check_mode:
                return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
            payload = {"Reboot": True}
            response = self.put_request(resource_uri, payload, etag)
            if response["ret"] is False:
                return response
        elif command.startswith("PowerMode"):
            return self.manage_power_mode(command)
        else:
            return {"ret": False, "msg": f"Invalid command: {command}"}

        return {"ret": True}

    def manage_chassis_indicator_led(self, command):
        """Process a command to manage the chassis indicator LED.

        :param string command: The Ansible command being processed.
        """
        return self.manage_indicator_led(command, self.root_uri)

    def manage_indicator_led(self, command, resource_uri=None):
        """Process a command to manage an indicator LED.

        :param string command: The Ansible command being processed.
        :param string resource_uri: URI of the resource whose indicator LED is being managed.
        """
        key = "IndicatorLED"
        if resource_uri is None:
            resource_uri = self.root_uri
        resource_uri = self.get_uri_with_slot_number_query_param(resource_uri)

        payloads = {"IndicatorLedOn": {"ID": 2}, "IndicatorLedOff": {"ID": 4}}

        response = self.get_request(resource_uri)
        if "etag" not in response["headers"]:
            return {"ret": False, "msg": "Etag not found in response."}
        etag = response["headers"]["etag"]
        if response["ret"] is False:
            return response
        data = response["data"]
        if key not in data:
            return {"ret": False, "msg": f"Key {key} not found"}
        if "ID" not in data[key]:
            return {"ret": False, "msg": "IndicatorLED for resource has no ID."}

        if command in payloads.keys():
            # See if the LED is already set as requested.
            current_led_status = data[key]["ID"]
            if current_led_status == payloads[command]["ID"]:
                return {"ret": True, "changed": False}

            # Set the LED (unless we are in check mode)
            if self.module.check_mode:
                return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
            payload = {"IndicatorLED": payloads[command]}
            response = self.put_request(resource_uri, payload, etag)
            if response["ret"] is False:
                return response
        else:
            return {"ret": False, "msg": "Invalid command"}

        return {"ret": True}

    def manage_power_mode(self, command):
        key = "PowerState"
        resource_uri = self.get_uri_with_slot_number_query_param(self.root_uri)

        payloads = {"PowerModeNormal": 2, "PowerModeLow": 4}

        response = self.get_request(resource_uri)
        if "etag" not in response["headers"]:
            return {"ret": False, "msg": "Etag not found in response."}
        etag = response["headers"]["etag"]
        if response["ret"] is False:
            return response
        data = response["data"]
        if key not in data:
            return {"ret": False, "msg": f"Key {key} not found"}
        if "ID" not in data[key]:
            return {"ret": False, "msg": "PowerState for resource has no ID."}

        if command in payloads.keys():
            # See if the PowerState is already set as requested.
            current_power_state = data[key]["ID"]
            if current_power_state == payloads[command]:
                return {"ret": True, "changed": False}

            # Set the Power State (unless we are in check mode)
            if self.module.check_mode:
                return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
            payload = {"PowerState": {"ID": payloads[command]}}
            response = self.put_request(resource_uri, payload, etag)
            if response["ret"] is False:
                return response
        else:
            return {"ret": False, "msg": f"Invalid command: {command}"}

        return {"ret": True}

    def prepare_multipart_firmware_upload(self, filename):
        """Prepare a multipart/form-data body for OCAPI firmware upload.

        :arg filename: The name of the file to upload.
        :returns: tuple of (content_type, body) where ``content_type`` is
            the ``multipart/form-data`` ``Content-Type`` header including
            ``boundary`` and ``body`` is the prepared bytestring body

        Prepares the body to include "FirmwareFile" field with the contents of the file.
        Because some OCAPI targets do not support Base-64 encoding for multipart/form-data,
        this method sends the file as binary.
        """
        boundary = str(uuid.uuid4())  # Generate a random boundary
        body = f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="FirmwareFile"; filename="{to_native(os.path.basename(filename))}"\r\n'
        body += "Content-Type: application/octet-stream\r\n\r\n"
        body_bytes = bytearray(body, "utf-8")
        with open(filename, "rb") as f:
            body_bytes += f.read()
        body_bytes += bytearray(f"\r\n--{boundary}--", "utf-8")
        return (f"multipart/form-data; boundary={boundary}", body_bytes)

    def upload_firmware_image(self, update_image_path):
        """Perform Firmware Upload to the OCAPI storage device.

        :param str update_image_path: The path/filename of the firmware image, on the local filesystem.
        """
        if not (os.path.exists(update_image_path) and os.path.isfile(update_image_path)):
            return {"ret": False, "msg": "File does not exist."}
        url = f"{self.root_uri}OperatingSystem"
        url = self.get_uri_with_slot_number_query_param(url)
        content_type, b_form_data = self.prepare_multipart_firmware_upload(update_image_path)

        # Post the firmware (unless we are in check mode)
        if self.module.check_mode:
            return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
        result = self.post_request(url, b_form_data, content_type=content_type, timeout=300)
        if result["ret"] is False:
            return result
        return {"ret": True}

    def update_firmware_image(self):
        """Perform a Firmware Update on the OCAPI storage device."""
        resource_uri = self.root_uri
        resource_uri = self.get_uri_with_slot_number_query_param(resource_uri)
        # We have to do a GET to obtain the Etag.  It's required on the PUT.
        response = self.get_request(resource_uri)
        if response["ret"] is False:
            return response
        if "etag" not in response["headers"]:
            return {"ret": False, "msg": "Etag not found in response."}
        etag = response["headers"]["etag"]

        # Issue the PUT (unless we are in check mode)
        if self.module.check_mode:
            return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
        payload = {"FirmwareUpdate": True}
        response = self.put_request(resource_uri, payload, etag)
        if response["ret"] is False:
            return response

        return {"ret": True, "jobUri": response["headers"]["location"]}

    def activate_firmware_image(self):
        """Perform a Firmware Activate on the OCAPI storage device."""
        resource_uri = self.root_uri
        resource_uri = self.get_uri_with_slot_number_query_param(resource_uri)
        # We have to do a GET to obtain the Etag.  It's required on the PUT.
        response = self.get_request(resource_uri)
        if "etag" not in response["headers"]:
            return {"ret": False, "msg": "Etag not found in response."}
        etag = response["headers"]["etag"]
        if response["ret"] is False:
            return response

        # Issue the PUT (unless we are in check mode)
        if self.module.check_mode:
            return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}
        payload = {"FirmwareActivate": True}
        response = self.put_request(resource_uri, payload, etag)
        if response["ret"] is False:
            return response

        return {"ret": True, "jobUri": response["headers"]["location"]}

    def get_job_status(self, job_uri):
        """Get the status of a job.

        :param str job_uri: The URI of the job's status monitor.
        """
        job_uri = self.get_uri_with_slot_number_query_param(job_uri)
        response = self.get_request(job_uri)
        if response["ret"] is False:
            if response.get("status") == 404:
                # Job not found -- assume 0%
                return {
                    "ret": True,
                    "percentComplete": 0,
                    "operationStatus": "Not Available",
                    "operationStatusId": 1,
                    "operationHealth": None,
                    "operationHealthId": None,
                    "details": "Job does not exist.",
                    "jobExists": False,
                }
            else:
                return response
        details = response["data"]["Status"].get("Details")
        if isinstance(details, str):
            details = [details]
        health_list = response["data"]["Status"]["Health"]
        return_value = {
            "ret": True,
            "percentComplete": response["data"]["PercentComplete"],
            "operationStatus": response["data"]["Status"]["State"]["Name"],
            "operationStatusId": response["data"]["Status"]["State"]["ID"],
            "operationHealth": health_list[0]["Name"] if len(health_list) > 0 else None,
            "operationHealthId": health_list[0]["ID"] if len(health_list) > 0 else None,
            "details": details,
            "jobExists": True,
        }
        return return_value

    def delete_job(self, job_uri):
        """Delete the OCAPI job referenced by the specified job_uri."""
        job_uri = self.get_uri_with_slot_number_query_param(job_uri)
        # We have to do a GET to obtain the Etag.  It's required on the DELETE.
        response = self.get_request(job_uri)

        if response["ret"] is True:
            if "etag" not in response["headers"]:
                return {"ret": False, "msg": "Etag not found in response."}
            else:
                etag = response["headers"]["etag"]

            if response["data"]["PercentComplete"] != 100:
                return {"ret": False, "changed": False, "msg": "Cannot delete job because it is in progress."}

        if response["ret"] is False:
            if response["status"] == 404:
                return {"ret": True, "changed": False, "msg": "Job already deleted."}
            return response
        if self.module.check_mode:
            return {"ret": True, "changed": True, "msg": "Update not performed in check mode."}

        # Do the DELETE (unless we are in check mode)
        response = self.delete_request(job_uri, etag)
        if response["ret"] is False:
            if response["status"] == 404:
                return {"ret": True, "changed": False}
            elif response["status"] == 409:
                return {"ret": False, "changed": False, "msg": "Cannot delete job because it is in progress."}
            return response
        return {"ret": True, "changed": True}

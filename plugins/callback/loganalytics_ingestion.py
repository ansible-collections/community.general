#!/usr/bin/env python
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = """
name: loganalytics_ingestion
type: notification
short_description: Posts task results to an Azure Log Analytics workspace using the new Logs Ingestion API
author:
  - Wade Cline (@wtcline-intc) <wade.cline@intel.com>
  - Sriramoju Vishal Bharath (@vsh47) <sriramoju.vishal.bharath@intel.com>
  - Cyrus Li (@zhcli) <cyrus1006@gmail.com>
description:
  - This callback plugin will post task results in JSON format to an Azure Log Analytics workspace using the new Logs Ingestion API.
version_added: "12.4.0"
requirements:
  - The callback plugin has been enabled.
  - An Azure Log Analytics workspace has been established.
  - A Data Collection Rule (DCR) and custom table are created.
options:
  dce_url:
    description: URL of the Data Collection Endpoint (DCE) for Azure Logs Ingestion API.
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_DCE_URL
    ini:
      - section: callback_loganalytics
        key: dce_url
  dcr_id:
    description: Data Collection Rule (DCR) ID for the Azure Log Ingestion API.
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_DCR_ID
    ini:
      - section: callback_loganalytics
        key: dcr_id
  disable_attempts:
    description:
      - When O(disable_on_failure=true), number of plugin failures that must occur before the plugin is disabled.
      - This helps prevent outright plugin failure from a single, transient network issue.
    type: int
    default: 3
    env:
      - name: ANSIBLE_LOGANALYTICS_DISABLE_ATTEMPTS
    ini:
      - section: callback_loganalytics
        key: disable_attempts
  disable_on_failure:
    description: Stop trying to send data on plugin failure.
    type: bool
    default: true
    env:
      - name: ANSIBLE_LOGANALYTICS_DISABLE_ON_FAILURE
    ini:
      - section: callback_loganalytics
        key: disable_on_failure
  client_id:
    description: Client ID of the Azure App registration for OAuth2 authentication ("Modern Authentication").
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_CLIENT_ID
    ini:
      - section: callback_loganalytics
        key: client_id
  client_secret:
    description: Client Secret of the Azure App registration.
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_CLIENT_SECRET
    ini:
      - section: callback_loganalytics
        key: client_secret
  include_content:
    description: Send the content to the Azure Log Analytics workspace.
    type: bool
    default: false
    env:
      - name: ANSIBLE_LOGANALYTICS_INCLUDE_CONTENT
    ini:
      - section: callback_loganalytics
        key: include_content
  include_task_args:
    description: Send the task args to the Azure Log Analytics workspace.
    type: bool
    default: false
    env:
      - name: ANSIBLE_LOGANALYTICS_INCLUDE_TASK_ARGS
    ini:
      - section: callback_loganalytics
        key: include_task_args
  stream_name:
    description: The name of the stream used to send the logs to the Azure Log Analytics workspace.
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_STREAM_NAME
    ini:
      - section: callback_loganalytics
        key: stream_name
  tenant_id:
    description: Tenant ID for the Azure Active Directory.
    type: str
    required: true
    env:
      - name: ANSIBLE_LOGANALYTICS_TENANT_ID
    ini:
      - section: callback_loganalytics
        key: tenant_id
  timeout:
    description: Timeout for the HTTP requests to the Azure Log Analytics API.
    type: int
    default: 2
    env:
      - name: ANSIBLE_LOGANALYTICS_TIMEOUT
    ini:
      - section: callback_loganalytics
        key: timeout
seealso:
  - name: Logs Ingestion API
    description: Overview of Logs Ingestion API in Azure Monitor
    link: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview
notes:
  - Triple verbosity logging (C(-vvv)) can be used to generate JSON sample data for creating the table schema in Azure Log Analytics.
    Search for the string C(Event Data:) in the output in order to locate the data sample.
"""

EXAMPLES = """
examples: |
  Enable the plugin in ansible.cfg:
    [defaults]
    callback_enabled = community.general.loganalytics_ingestion
  Set the environment variables:
    export ANSIBLE_LOGANALYTICS_DCE_URL=https://my-dce.ingest.monitor.azure.com
    export ANSIBLE_LOGANALYTICS_DCR_ID=dcr-xxxxxx
    export ANSIBLE_LOGANALYTICS_CLIENT_ID=xxxxxxxx
    export ANSIBLE_LOGANALYTICS_CLIENT_SECRET=xxxxxxxx
    export ANSIBLE_LOGANALYTICS_TENANT_ID=xxxxxxxx
    export ANSIBLE_LOGANALYTICS_STREAM_NAME=Custom-MyTable
"""

import getpass
import json
import socket
import uuid
from datetime import datetime, timedelta, timezone
from os.path import basename
from urllib.parse import urlencode

from ansible.module_utils.urls import open_url
from ansible.plugins.callback import CallbackBase
from ansible.utils.display import Display

display = Display()


class AzureLogAnalyticsIngestionSource:
    def __init__(
        self,
        dce_url,
        dcr_id,
        disable_attempts,
        disable_on_failure,
        client_id,
        client_secret,
        tenant_id,
        stream_name,
        include_task_args,
        include_content,
        timeout,
        fqcn,
    ):
        self.dce_url = dce_url
        self.dcr_id = dcr_id
        self.disabled = False
        self.disable_attempts = disable_attempts
        self.disable_on_failure = disable_on_failure
        self.client_id = client_id
        self.client_secret = client_secret
        self.failures = 0
        self.tenant_id = tenant_id
        self.stream_name = stream_name
        self.include_task_args = include_task_args
        self.include_content = include_content
        self.token_expiration_time = None
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        self.user = getpass.getuser()
        self.timeout = timeout
        self.fqcn = fqcn

        self.bearer_token = self.get_bearer_token()

    # OAuth2 authentication method to get a Bearer token
    # This replaces the shared_key authentication mechanism
    def get_bearer_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                # The scope value comes from https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview#headers
                # and https://learn.microsoft.com/en-us/entra/identity-platform/scopes-oidc#the-default-scope
                "scope": "https://monitor.azure.com/.default",
            }
        )
        response = open_url(url, data=data, force=True, headers=headers, method="POST", timeout=self.timeout)
        j = json.loads(response.read().decode("utf-8"))
        self.token_expiration_time = datetime.now() + timedelta(seconds=j.get("expires_in"))
        return j.get("access_token")

    def is_token_valid(self):
        return datetime.now() + timedelta(seconds=10) < self.token_expiration_time

    # Method to send event data to the Azure Logs Ingestion API
    # This replaces the legacy API call and now uses the Logs Ingestion API endpoint
    def send_event(self, event_data):
        if not self.is_token_valid():
            self.bearer_token = self.get_bearer_token()
        ingestion_url = (
            f"{self.dce_url}/dataCollectionRules/{self.dcr_id}/streams/{self.stream_name}?api-version=2023-01-01"
        )
        headers = {"Authorization": f"Bearer {self.bearer_token}", "Content-Type": "application/json"}
        open_url(ingestion_url, data=json.dumps(event_data), headers=headers, method="POST", timeout=self.timeout)

    def _rfc1123date(self):
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # This method wraps the private method with the appropriate error handling.
    def send_to_loganalytics(self, playbook_name, result, state):
        if self.disabled:
            return
        try:
            self._send_to_loganalytics(playbook_name, result, state)
        except Exception as e:
            display.warning(f"{self.fqcn} callback plugin failure: {e}.")
            if self.disable_on_failure:
                self.failures += 1
                if self.failures >= self.disable_attempts:
                    display.warning(
                        f"{self.fqcn} callback plugin failures exceed maximum of '{self.disable_attempts}'!  Disabling plugin!"
                    )
                    self.disabled = True
                else:
                    display.v(f"{self.fqcn} callback plugin failure {self.failures}/{self.disable_attempts}")

    def _send_to_loganalytics(self, playbook_name, result, state):
        ansible_role = str(result._task._role) if result._task._role else None

        # Include/Exclude task args
        if not self.include_task_args:
            result._task_fields.pop("args", None)

        # Include/Exclude content
        if not self.include_content:
            result._result.pop("content", None)

        # Build the event data
        event_data = [
            {
                "TimeGenerated": self._rfc1123date(),
                "Host": result._host.name,
                "User": self.user,
                "Playbook": playbook_name,
                "Role": ansible_role,
                "TaskName": result._task.get_name(),
                "Task": result._task_fields,
                "Action": result._task_fields["action"],
                "State": state,
                "Result": result._result,
                "Session": self.session,
            }
        ]

        # The data displayed here can be used as a sample file in order to create the table's schema.
        display.vvv(f"Event Data: {json.dumps(event_data)}")

        self.send_event(event_data)


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "loganalytics_ingestion"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super().__init__(display=display)
        self.start_datetimes = {}
        self.playbook_name = None
        self.azure_loganalytics = None
        self.fqcn = f"community.general.{self.CALLBACK_NAME}"

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        # Set options for the new Azure Logs Ingestion API configuration
        self.client_id = self.get_option("client_id")
        self.client_secret = self.get_option("client_secret")
        self.dce_url = self.get_option("dce_url")
        self.dcr_id = self.get_option("dcr_id")
        self.disable_attempts = self.get_option("disable_attempts")
        self.disable_on_failure = self.get_option("disable_on_failure")
        self.include_content = self.get_option("include_content")
        self.include_task_args = self.get_option("include_task_args")
        self.stream_name = self.get_option("stream_name")
        self.tenant_id = self.get_option("tenant_id")
        self.timeout = self.get_option("timeout")

        # Initialize the AzureLogAnalyticsIngestionSource with the new settings
        self.azure_loganalytics = AzureLogAnalyticsIngestionSource(
            self.dce_url,
            self.dcr_id,
            self.disable_attempts,
            self.disable_on_failure,
            self.client_id,
            self.client_secret,
            self.tenant_id,
            self.stream_name,
            self.include_task_args,
            self.include_content,
            self.timeout,
            self.fqcn,
        )

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = basename(playbook._file_name)

    # Build event data and send it to the Logs Ingestion API
    def v2_runner_on_failed(self, result, **kwargs):
        self.azure_loganalytics.send_to_loganalytics(self.playbook_name, result, "FAILED")

    def v2_runner_on_ok(self, result, **kwargs):
        self.azure_loganalytics.send_to_loganalytics(self.playbook_name, result, "OK")

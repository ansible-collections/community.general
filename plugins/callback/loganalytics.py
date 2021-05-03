# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: loganalytics
    type: aggregate
    short_description: Posts task results to Azure Log Analytics
    author: "Cyrus Li (@zhcli) <cyrus1006@gmail.com>"
    description:
      - This callback plugin will post task results in JSON formatted to an Azure Log Analytics workspace.
      - Credits to authors of splunk callback plugin.
    version_added: "2.4.0"
    requirements:
      - Whitelisting this callback plugin.
      - An Azure log analytics work space has been established.
    options:
      workspace_id:
        description: Workspace ID of the Azure log analytics workspace.
        required: true
        env:
          - name: WORKSPACE_ID
        ini:
          - section: callback_loganalytics
            key: workspace_id
      shared_key:
        description: Shared key to connect to Azure log analytics workspace.
        required: true
        env:
          - name: WORKSPACE_SHARED_KEY
        ini:
          - section: callback_loganalytics
            key: shared_key
'''

EXAMPLES = '''
examples: |
  Whitelist the plugin in ansible.cfg:
    [defaults]
    callback_whitelist = community.general.loganalytics
  Set the environment variable:
    export WORKSPACE_ID=01234567-0123-0123-0123-01234567890a
    export WORKSPACE_SHARED_KEY=dZD0kCbKl3ehZG6LHFMuhtE0yHiFCmetzFMc2u+roXIUQuatqU924SsAAAAPemhjbGlAemhjbGktTUJQAQIDBA==
  Or configure the plugin in ansible.cfg in the callback_loganalytics block:
    [callback_loganalytics]
    workspace_id = 01234567-0123-0123-0123-01234567890a
    shared_key = dZD0kCbKl3ehZG6LHFMuhtE0yHiFCmetzFMc2u+roXIUQuatqU924SsAAAAPemhjbGlAemhjbGktTUJQAQIDBA==
'''

import hashlib
import hmac
import base64
import logging
import json
import uuid
import socket
import getpass

from datetime import datetime
from os.path import basename

from ansible.module_utils.urls import open_url
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


class AzureLogAnalyticsSource(object):
    def __init__(self):
        self.ansible_check_mode = False
        self.ansible_playbook = ""
        self.ansible_version = ""
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        self.user = getpass.getuser()
        self.extra_vars = ""

    def __build_signature(self, date, workspace_id, shared_key, content_length):
        # Build authorisation signature for Azure log analytics API call
        sigs = "POST\n{0}\napplication/json\nx-ms-date:{1}\n/api/logs".format(
            str(content_length), date)
        utf8_sigs = sigs.encode('utf-8')
        decoded_shared_key = base64.b64decode(shared_key)
        hmac_sha256_sigs = hmac.new(
            decoded_shared_key, utf8_sigs, digestmod=hashlib.sha256).digest()
        encoded_hash = base64.b64encode(hmac_sha256_sigs).decode('utf-8')
        signature = "SharedKey {0}:{1}".format(workspace_id, encoded_hash)
        return signature

    def __build_workspace_url(self, workspace_id):
        return "https://{0}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01".format(workspace_id)

    def __rfc1123date(self):
        return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    def send_event(self, workspace_id, shared_key, state, result, runtime):
        if result._task_fields['args'].get('_ansible_check_mode') is True:
            self.ansible_check_mode = True

        if result._task_fields['args'].get('_ansible_version'):
            self.ansible_version = \
                result._task_fields['args'].get('_ansible_version')

        if result._task._role:
            ansible_role = str(result._task._role)
        else:
            ansible_role = None

        data = {}
        data['uuid'] = result._task._uuid
        data['session'] = self.session
        data['status'] = state
        data['timestamp'] = self.__rfc1123date()
        data['host'] = self.host
        data['user'] = self.user
        data['runtime'] = runtime
        data['ansible_version'] = self.ansible_version
        data['ansible_check_mode'] = self.ansible_check_mode
        data['ansible_host'] = result._host.name
        data['ansible_playbook'] = self.ansible_playbook
        data['ansible_role'] = ansible_role
        data['ansible_task'] = result._task_fields
        # Removing args since it can contain sensitive data
        if 'args' in data['ansible_task']:
            data['ansible_task'].pop('args')
        data['ansible_result'] = result._result
        if 'content' in data['ansible_result']:
            data['ansible_result'].pop('content')

        # Adding extra vars info
        data['extra_vars'] = self.extra_vars

        # Preparing the playbook logs as JSON format and send to Azure log analytics
        jsondata = json.dumps({'event': data}, cls=AnsibleJSONEncoder, sort_keys=True)
        content_length = len(jsondata)
        rfc1123date = self.__rfc1123date()
        signature = self.__build_signature(rfc1123date, workspace_id, shared_key, content_length)
        workspace_url = self.__build_workspace_url(workspace_id)

        open_url(
            workspace_url,
            jsondata,
            headers={
                'content-type': 'application/json',
                'Authorization': signature,
                'Log-Type': 'ansible_playbook',
                'x-ms-date': rfc1123date
            },
            method='POST'
        )


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'loganalytics'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.start_datetimes = {}  # Collect task start times
        self.workspace_id = None
        self.shared_key = None
        self.loganalytics = AzureLogAnalyticsSource()

    def _seconds_since_start(self, result):
        return (
            datetime.utcnow() -
            self.start_datetimes[result._task._uuid]
        ).total_seconds()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)
        self.workspace_id = self.get_option('workspace_id')
        self.shared_key = self.get_option('shared_key')

    def v2_playbook_on_play_start(self, play):
        vm = play.get_variable_manager()
        extra_vars = vm.extra_vars
        self.loganalytics.extra_vars = extra_vars

    def v2_playbook_on_start(self, playbook):
        self.loganalytics.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_playbook_on_handler_task_start(self, task):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_runner_on_ok(self, result, **kwargs):
        self.loganalytics.send_event(
            self.workspace_id,
            self.shared_key,
            'OK',
            result,
            self._seconds_since_start(result)
        )

    def v2_runner_on_skipped(self, result, **kwargs):
        self.loganalytics.send_event(
            self.workspace_id,
            self.shared_key,
            'SKIPPED',
            result,
            self._seconds_since_start(result)
        )

    def v2_runner_on_failed(self, result, **kwargs):
        self.loganalytics.send_event(
            self.workspace_id,
            self.shared_key,
            'FAILED',
            result,
            self._seconds_since_start(result)
        )

    def runner_on_async_failed(self, result, **kwargs):
        self.loganalytics.send_event(
            self.workspace_id,
            self.shared_key,
            'FAILED',
            result,
            self._seconds_since_start(result)
        )

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.loganalytics.send_event(
            self.workspace_id,
            self.shared_key,
            'UNREACHABLE',
            result,
            self._seconds_since_start(result)
        )

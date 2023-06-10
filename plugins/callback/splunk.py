# -*- coding: utf-8 -*-
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: splunk
    type: notification
    short_description: Sends task result events to Splunk HTTP Event Collector
    author: "Stuart Hirst (!UNKNOWN) <support@convergingdata.com>"
    description:
      - This callback plugin will send task results as JSON formatted events to a Splunk HTTP collector.
      - The companion Splunk Monitoring & Diagnostics App is available here U(https://splunkbase.splunk.com/app/4023/).
      - Credit to "Ryan Currah (@ryancurrah)" for original source upon which this is based.
    requirements:
      - Whitelisting this callback plugin
      - 'Create a HTTP Event Collector in Splunk'
      - 'Define the URL and token in C(ansible.cfg)'
    options:
      url:
        description: URL to the Splunk HTTP collector source.
        env:
          - name: SPLUNK_URL
        ini:
          - section: callback_splunk
            key: url
      authtoken:
        description: Token to authenticate the connection to the Splunk HTTP collector.
        env:
          - name: SPLUNK_AUTHTOKEN
        ini:
          - section: callback_splunk
            key: authtoken
      validate_certs:
        description: Whether to validate certificates for connections to HEC. It is not recommended to set to
                     V(false) except when you are sure that nobody can intercept the connection
                     between this plugin and HEC, as setting it to V(false) allows man-in-the-middle attacks!
        env:
          - name: SPLUNK_VALIDATE_CERTS
        ini:
          - section: callback_splunk
            key: validate_certs
        type: bool
        default: true
        version_added: '1.0.0'
      include_milliseconds:
        description: Whether to include milliseconds as part of the generated timestamp field in the event
                     sent to the Splunk HTTP collector.
        env:
          - name: SPLUNK_INCLUDE_MILLISECONDS
        ini:
          - section: callback_splunk
            key: include_milliseconds
        type: bool
        default: false
        version_added: 2.0.0
      batch:
        description:
          - Correlation ID which can be set across multiple playbook executions.
        env:
          - name: SPLUNK_BATCH
        ini:
          - section: callback_splunk
            key: batch
        type: str
        version_added: 3.3.0
'''

EXAMPLES = '''
examples: >
  To enable, add this to your ansible.cfg file in the defaults block
    [defaults]
    callback_whitelist = community.general.splunk
  Set the environment variable
    export SPLUNK_URL=http://mysplunkinstance.datapaas.io:8088/services/collector/event
    export SPLUNK_AUTHTOKEN=f23blad6-5965-4537-bf69-5b5a545blabla88
  Set the ansible.cfg variable in the callback_splunk block
    [callback_splunk]
    url = http://mysplunkinstance.datapaas.io:8088/services/collector/event
    authtoken = f23blad6-5965-4537-bf69-5b5a545blabla88
'''

import json
import uuid
import socket
import getpass

from datetime import datetime
from os.path import basename

from ansible.module_utils.urls import open_url
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


class SplunkHTTPCollectorSource(object):
    def __init__(self):
        self.ansible_check_mode = False
        self.ansible_playbook = ""
        self.ansible_version = ""
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.user = getpass.getuser()

    def send_event(self, url, authtoken, validate_certs, include_milliseconds, batch, state, result, runtime):
        if result._task_fields['args'].get('_ansible_check_mode') is True:
            self.ansible_check_mode = True

        if result._task_fields['args'].get('_ansible_version'):
            self.ansible_version = \
                result._task_fields['args'].get('_ansible_version')

        if result._task._role:
            ansible_role = str(result._task._role)
        else:
            ansible_role = None

        if 'args' in result._task_fields:
            del result._task_fields['args']

        data = {}
        data['uuid'] = result._task._uuid
        data['session'] = self.session
        if batch is not None:
            data['batch'] = batch
        data['status'] = state

        if include_milliseconds:
            time_format = '%Y-%m-%d %H:%M:%S.%f +0000'
        else:
            time_format = '%Y-%m-%d %H:%M:%S +0000'

        data['timestamp'] = datetime.utcnow().strftime(time_format)
        data['host'] = self.host
        data['ip_address'] = self.ip_address
        data['user'] = self.user
        data['runtime'] = runtime
        data['ansible_version'] = self.ansible_version
        data['ansible_check_mode'] = self.ansible_check_mode
        data['ansible_host'] = result._host.name
        data['ansible_playbook'] = self.ansible_playbook
        data['ansible_role'] = ansible_role
        data['ansible_task'] = result._task_fields
        data['ansible_result'] = result._result

        # This wraps the json payload in and outer json event needed by Splunk
        jsondata = json.dumps(data, cls=AnsibleJSONEncoder, sort_keys=True)
        jsondata = '{"event":' + jsondata + "}"

        open_url(
            url,
            jsondata,
            headers={
                'Content-type': 'application/json',
                'Authorization': 'Splunk ' + authtoken
            },
            method='POST',
            validate_certs=validate_certs
        )


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.splunk'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.start_datetimes = {}  # Collect task start times
        self.url = None
        self.authtoken = None
        self.validate_certs = None
        self.include_milliseconds = None
        self.batch = None
        self.splunk = SplunkHTTPCollectorSource()

    def _runtime(self, result):
        return (
            datetime.utcnow() -
            self.start_datetimes[result._task._uuid]
        ).total_seconds()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        self.url = self.get_option('url')

        if self.url is None:
            self.disabled = True
            self._display.warning('Splunk HTTP collector source URL was '
                                  'not provided. The Splunk HTTP collector '
                                  'source URL can be provided using the '
                                  '`SPLUNK_URL` environment variable or '
                                  'in the ansible.cfg file.')

        self.authtoken = self.get_option('authtoken')

        if self.authtoken is None:
            self.disabled = True
            self._display.warning('Splunk HTTP collector requires an authentication'
                                  'token. The Splunk HTTP collector '
                                  'authentication token can be provided using the '
                                  '`SPLUNK_AUTHTOKEN` environment variable or '
                                  'in the ansible.cfg file.')

        self.validate_certs = self.get_option('validate_certs')

        self.include_milliseconds = self.get_option('include_milliseconds')

        self.batch = self.get_option('batch')

    def v2_playbook_on_start(self, playbook):
        self.splunk.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_playbook_on_handler_task_start(self, task):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_runner_on_ok(self, result, **kwargs):
        self.splunk.send_event(
            self.url,
            self.authtoken,
            self.validate_certs,
            self.include_milliseconds,
            self.batch,
            'OK',
            result,
            self._runtime(result)
        )

    def v2_runner_on_skipped(self, result, **kwargs):
        self.splunk.send_event(
            self.url,
            self.authtoken,
            self.validate_certs,
            self.include_milliseconds,
            self.batch,
            'SKIPPED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_failed(self, result, **kwargs):
        self.splunk.send_event(
            self.url,
            self.authtoken,
            self.validate_certs,
            self.include_milliseconds,
            self.batch,
            'FAILED',
            result,
            self._runtime(result)
        )

    def runner_on_async_failed(self, result, **kwargs):
        self.splunk.send_event(
            self.url,
            self.authtoken,
            self.validate_certs,
            self.include_milliseconds,
            self.batch,
            'FAILED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.splunk.send_event(
            self.url,
            self.authtoken,
            self.validate_certs,
            self.include_milliseconds,
            self.batch,
            'UNREACHABLE',
            result,
            self._runtime(result)
        )

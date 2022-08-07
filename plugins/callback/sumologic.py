# -*- coding: utf-8 -*-
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
name: sumologic
type: aggregate
short_description: Sends task result events to Sumologic
author: "Ryan Currah (@ryancurrah)"
description:
  - This callback plugin will send task results as JSON formatted events to a Sumologic HTTP collector source
requirements:
  - Whitelisting this callback plugin
  - 'Create a HTTP collector source in Sumologic and specify a custom timestamp format of C(yyyy-MM-dd HH:mm:ss ZZZZ) and a custom timestamp locator
    of C("timestamp": "(.*)")'
options:
  url:
    description: URL to the Sumologic HTTP collector source
    env:
      - name: SUMOLOGIC_URL
    ini:
      - section: callback_sumologic
        key: url
'''

EXAMPLES = '''
examples: >
  To enable, add this to your ansible.cfg file in the defaults block
    [defaults]
    callback_whitelist = community.general.sumologic

  Set the environment variable
    export SUMOLOGIC_URL=https://endpoint1.collection.us2.sumologic.com/receiver/v1/http/R8moSv1d8EW9LAUFZJ6dbxCFxwLH6kfCdcBfddlfxCbLuL-BN5twcTpMk__pYy_cDmp==

  Set the ansible.cfg variable in the callback_sumologic block
    [callback_sumologic]
    url = https://endpoint1.collection.us2.sumologic.com/receiver/v1/http/R8moSv1d8EW9LAUFZJ6dbxCFxwLH6kfCdcBfddlfxCbLuL-BN5twcTpMk__pYy_cDmp==
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


class SumologicHTTPCollectorSource(object):
    def __init__(self):
        self.ansible_check_mode = False
        self.ansible_playbook = ""
        self.ansible_version = ""
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.user = getpass.getuser()

    def send_event(self, url, state, result, runtime):
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
        data['status'] = state
        data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S '
                                                       '+0000')
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

        open_url(
            url,
            data=json.dumps(data, cls=AnsibleJSONEncoder, sort_keys=True),
            headers={
                'Content-type': 'application/json',
                'X-Sumo-Host': data['ansible_host']
            },
            method='POST'
        )


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.sumologic'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.start_datetimes = {}  # Collect task start times
        self.url = None
        self.sumologic = SumologicHTTPCollectorSource()

    def _runtime(self, result):
        return (
            datetime.utcnow() -
            self.start_datetimes[result._task._uuid]
        ).total_seconds()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.url = self.get_option('url')

        if self.url is None:
            self.disabled = True
            self._display.warning('Sumologic HTTP collector source URL was '
                                  'not provided. The Sumologic HTTP collector '
                                  'source URL can be provided using the '
                                  '`SUMOLOGIC_URL` environment variable or '
                                  'in the ansible.cfg file.')

    def v2_playbook_on_start(self, playbook):
        self.sumologic.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_playbook_on_handler_task_start(self, task):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_runner_on_ok(self, result, **kwargs):
        self.sumologic.send_event(
            self.url,
            'OK',
            result,
            self._runtime(result)
        )

    def v2_runner_on_skipped(self, result, **kwargs):
        self.sumologic.send_event(
            self.url,
            'SKIPPED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_failed(self, result, **kwargs):
        self.sumologic.send_event(
            self.url,
            'FAILED',
            result,
            self._runtime(result)
        )

    def runner_on_async_failed(self, result, **kwargs):
        self.sumologic.send_event(
            self.url,
            'FAILED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.sumologic.send_event(
            self.url,
            'UNREACHABLE',
            result,
            self._runtime(result)
        )

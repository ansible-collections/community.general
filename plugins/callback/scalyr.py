# Copyright: (c) 2020, Martin Migasiewicz <migasiew.nk@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
callback: scalyr
type: aggregate
short_description: Sends task result events to Scalyr
author: Martin Migasiewicz (@martinm82)
version_added: 1.3.0
description:
  - This callback plugin will send task results as JSON formatted events to Scalyr.
requirements:
  - Whitelisting this callback plugin.
  - Create a Log Access Write Key in Scalyr (https://app.eu.scalyr.com/keys)
  - Define the Scalyr API URL and API key as an environment variable, in ansible.cfg or as hostvars.
    - When using the hostvars method the variable(s) need to be present as 'localhost' variables.
  - Heavily inspired by splunk and sumologic callbacks
options:
  scalyr_api_url:
    description: URL to the Scalyr API endpoint.
    default: https://app.eu.scalyr.com/api/addEvents
    env:
      - name: SCALYR_API_URL
    ini:
      - section: callback_scalyr
        key: scalyr_api_url
    type: string
  scalyr_api_authtoken:
    description: Token to authenticate the connection to Scalyr (with write access).
    env:
      - name: SCALYR_API_AUTHTOKEN
    ini:
      - section: callback_scalyr
        key: scalyr_api_authtoken
    type: string
'''

EXAMPLES = '''
examples: |
  To enable, add this to your ansible.cfg file in the defaults block
    [defaults]
    callback_whitelist = community.general.scalyr

  Set the environment variable
    export SCALYR_API_URL=https://app.eu.scalyr.com/api/addEvents
    export SCALYR_API_AUTHTOKEN=XXXXXXXXXXXXXXXXXXXXXmlQ0-

  Or set the ansible.cfg variable in the callback_scalyr block
    [callback_scalyr]
    scalry_api_url = https://app.eu.scalyr.com/api/addEvents
    scalyr_api_authtoken = XXXXXXXXXXXXXXXXXXXXXmlQ0-

  Or define as hostvars (supports as well Ansible vault)
    scalry_api_url: https://app.eu.scalyr.com/api/addEvents
    scalyr_api_authtoken: XXXXXXXXXXXXXXXXXXXXXmlQ0-
'''

import getpass
import json
import socket
import uuid

from datetime import datetime
from os.path import basename

from ansible.module_utils.urls import open_url
from ansible.module_utils.ansible_release import __version__ as ansible_version
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


def nanoTime():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000000000)


class ScalyrLogSource(object):
    def __init__(self):
        self.ansible_check_mode = False
        self.ansible_playbook = ""
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.user = getpass.getuser()

    def send_event(self, url, authtoken, state, result, runtime):
        """Send the Ansible task result to the Scalyr API.

        Args:
            url ([string]): Scalyr API URL to where the event will be sent.
            authtoken ([string]): Log Access Write Key to authenticate against the Scalyr API.
            state ([string]): State of the task itself.
            result ([ansible.executor.task_result.TaskResult]): The Ansible task result.
            runtime ([int]): Duration of the task.
        """
        if 'args' in result._task_fields:
            if result._task_fields['args'].get('_ansible_check_mode') is True:
                self.ansible_check_mode = True
            # Remove uninteresting data
            del result._task_fields['args']

        if result._task._role:
            ansible_role = str(result._task._role)
        else:
            ansible_role = None

        data = {
            "token": str(authtoken),
            "session": str(self.session),
            "sessionInfo": {
                "serverHost": result._host.get_name(),
                "logfile": "ansible.log",
                "parser": ""
            },
            "events": [
                {
                    "ts": str(nanoTime()),
                    "sev": 3,
                    "attrs": {
                        "uuid": result._task._uuid,
                        "status": state,
                        "runtime": runtime,
                        "user": self.user,
                        "ansible_controller_host": self.host,
                        "ansible_version": ansible_version,
                        "ansible_check_mode": self.ansible_check_mode,
                        "ansible_host": result._host.get_name(),
                        "ansible_playbook": self.ansible_playbook,
                        "ansible_role": ansible_role,
                        "ansible_task": result._task_fields,
                        "ansible_result": result._result
                    }
                }
            ]
        }

        payload = json.dumps(data, cls=AnsibleJSONEncoder, sort_keys=True)
        open_url(
            url,
            data=payload,
            headers={
                'Content-type': 'application/json'
            },
            method='POST'
        )


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.scalyr'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.start_datetimes = {}  # Collect task start times
        self.url = None
        self.authtoken = None
        self.scalyr = ScalyrLogSource()

    def _runtime(self, result):
        return (
            datetime.utcnow() -
            self.start_datetimes[result._task._uuid]
        ).total_seconds()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.url = self.get_option('scalyr_api_url')
        self.authtoken = self.get_option('scalyr_api_authtoken')

    def v2_playbook_on_play_start(self, play):
        hostvars = play.get_variable_manager()._hostvars

        if self.url is None:
            if not hostvars or 'scalyr_api_url' not in hostvars['localhost']:
                self.disabled = True
                self._display.warning('Scalyr API URL was '
                                      'not provided. The Scalyr API URL '
                                      'can be provided using the '
                                      '`SCALYR_API_URL` environment variable, '
                                      'in the ansible.cfg file or as a hostvar.')
            else:
                self.url = hostvars['localhost']['scalyr_api_url']

        if self.authtoken is None:
            if not hostvars or 'scalyr_api_authtoken' not in hostvars['localhost']:
                self.disabled = True
                self._display.warning('Scalyr requires a Log Access Write Key'
                                      'token. The Scalyr API key can be '
                                      'provided using the '
                                      '`SCALYR_API_AUTHTOKEN` environment variable, '
                                      'in the ansible.cfg file or as a hostvar.')
            else:
                self.authtoken = hostvars['localhost']['scalyr_api_authtoken']

    def v2_playbook_on_start(self, playbook):
        self.scalyr.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_playbook_on_handler_task_start(self, task):
        self.start_datetimes[task._uuid] = datetime.utcnow()

    def v2_runner_on_ok(self, result, **kwargs):
        self.scalyr.send_event(
            self.url,
            self.authtoken,
            'OK',
            result,
            self._runtime(result)
        )

    def v2_runner_on_skipped(self, result, **kwargs):
        self.scalyr.send_event(
            self.url,
            self.authtoken,
            'SKIPPED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_failed(self, result, **kwargs):
        self.scalyr.send_event(
            self.url,
            self.authtoken,
            'FAILED',
            result,
            self._runtime(result)
        )

    def runner_on_async_failed(self, result, **kwargs):
        self.scalyr.send_event(
            self.url,
            self.authtoken,
            'FAILED',
            result,
            self._runtime(result)
        )

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.scalyr.send_event(
            self.url,
            self.authtoken,
            'UNREACHABLE',
            result,
            self._runtime(result)
        )

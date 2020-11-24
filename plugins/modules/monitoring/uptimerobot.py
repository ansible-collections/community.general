#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: uptimerobot
short_description: Create, remove, pause and start monitors in Uptime Robot
description:
    - This module lets you create, remove, pause and start monitors in Uptime Robot.
author:
- "Nate Kingsley (@nate-kingsley)"
- "Ninjiner (@Ninjiner)"
requirements:
    - Valid Uptime Robot API Key
options:
    state:
        description:
            - Define whether or not the monitor should be running or paused.
            - C(created) and C(absent) were added in community.general 1.3.0.
        required: true
        choices: [ "started", "paused", "created", "absent", "present" ]
    url:
        description:
            - URL to be checked.
        type: str
        required: true
        version_added: '1.3.0'
    name:
        description:
            - The friendly name of the monitor.
        type: str
        required: true
        version_added: '1.3.0'
    check_type:
        description:
            - The kind of check, that will be performed on the url.
        choices: [ "http", "ping" ]
        version_added: '1.3.0'
    monitorid:
        description:
            - ID of the monitor to check.
        type: int
        required: false
    apikey:
        description:
            - Uptime Robot API key.
        type: str
        required: true
'''

EXAMPLES = '''
# Pause the monitor with an ID of 12345.
- community.general.uptimerobot:
    name: My domain
    url: https://www.my-domain.com
    apikey: 12345-1234512345
    state: paused
# Create an http checking monitor for https://www.my-domain.com
- community.general.uptimerobot:
    state: created
    url: https://www.my-domain.com
    name: My domain
    check_type: http
    apikey: 12345-1234512345
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import Request
from ansible.module_utils._text import to_text

API_BASE = "https://api.uptimerobot.com/v2/"

API_FORMAT = 'json'
API_NOJSONCALLBACK = 1
CHANGED_STATE = False
SUPPORTS_CHECK_MODE = False


class UptimeRobot:
    def __init__(self, params, api_methods):
        self.headers = {
            'Content-Type': "application/json"
        }
        self.uri = ''
        self.api_methods = api_methods
        self.params = self.check_dict(params)
        self.body = json.dumps(self.params)
        for state, method in self.api_methods.items():
            if state == self.params['status']:
                self.api_method = method

    def get_monitor_id(self, fname):
        monitors = self.get_monitors()
        for m_dict in monitors['monitors']:
            if m_dict['friendly_name'] == fname:
                mid = m_dict['id']
                return mid

    def get_monitors(self):
        self.body = {}
        self.body['api_key'] = self.params['api_key']
        self.body = json.dumps(self.body)
        self.uri = API_BASE + "getMonitors"
        state = self.api_call()
        return state

    def api_call(self):
        req = Request()
        state = req.post(url=self.uri, data=self.body, headers=self.headers)
        json_response = json.loads(to_text(state.read(), errors='surrogate_or_strict'))
        return json_response

    def api_request(self):
        self.uri = API_BASE + self.api_method
        state = self.api_call()
        return state, self.api_method

    def check_dict(self, dictionary):
        tmp = {}
        for k, v in dictionary.items():
            if v != '':
                tmp[k] = v
            if k == 'type':
                tmp[k] = 3 if v == 'ping' else 1

        if dictionary['status'] != 'created':
            tmp['id'] = self.get_monitor_id(dictionary['friendly_name'])
        dictionary.clear()
        return tmp


def main():
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    api_methods = dict(
        started='editMonitor',
        present='newMonitor',
        paused='editMonitor',
        absent='deleteMonitor',
        created='newMonitor'
    )

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            url=dict(type='str', required=True),
            check_type=dict(required=False, choices=['http', 'ping']),
            state=dict(required=True, choices=['started', 'paused', 'absent', 'created', 'present']),
            apikey=dict(type='str', required=True, no_log=True),
            monitorid=dict(type='int', required=False)
        ),
        supports_check_mode=SUPPORTS_CHECK_MODE
    )

    params = dict(
        api_key=module.params['apikey'],
        monitorID=module.params['monitorid'],
        friendly_name=module.params['name'],
        url=module.params['url'],
        type=module.params['check_type'],
        status=module.params['state'],
        format=API_FORMAT,
        noJsonCallback=API_NOJSONCALLBACK
    )

    uprobot = UptimeRobot(params, api_methods)
    state, api_method = uprobot.api_request()
    result['message'] = state['stat']
    result['original_message'] = state
    if result['message'] != 'ok':
        module.fail_json(msg='Could not perform action {0}'.format(api_method))

    module.exit_json(**result)


if __name__ == '__main__':
    main()

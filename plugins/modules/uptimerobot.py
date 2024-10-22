#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''

module: uptimerobot
short_description: Interact with Uptime Robot monitoring
description:
    - This module will let you manage your Uptime Robot Monitoring
author:
    - "Nate Kingsley (@nate-kingsley)"
    - "Leon Thiel (@thieleon)"
requirements:
    - Valid Uptime Robot API Key
    - python requests module
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    api_key:
        type: str
        description:
            - Uptime Robot API key.
        required: true
    action:
        type: str
        description:
            - Uptime Robot API action.
        required: true
    params:
        type: dict
        description:
            - required data for api call. See https://uptimerobot.com/api/
        required: false
notes:
    - See the uptimerobot api description on \
        https://uptimerobot.com/api/ for more information about \
        required params.
'''

EXAMPLES = '''
- name: Create a new monitor of type 1 (http), \
    url "http://example.com" and name "My new monitor"
  community.general.uptimerobot:
    api_key: 12345-1234512345
    action: newMonitor
    params:
        friendly_name: "My new monitor"
        url: "http://example.com"
        type: 1

- name: Enable the monitor with an ID of 12345
  community.general.uptimerobot:
    api_key: 12345-1234512345
    action: editMonitor
    params:
        status: 1
'''

from ansible.module_utils.six.moves.urllib.parse import urlencode
import requests

API_URL = "https://api.uptimerobot.com/v2/"
API_FORMAT = 'json'
API_NOJSONCALLBACK = 1
SUPPORTS_CHECK_MODE = False


def uptimerobot_api_call(action, params, module=None):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cache-control': "no-cache",
    }

    payload = urlencode(params)

    response = requests.post(API_URL + action, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('API request failed',
                        response.status_code, response.text)


if __name__ == '__main__':
    from ansible.module_utils.basic import AnsibleModule

    def main():
        module = AnsibleModule(
            argument_spec=dict(
                api_key=dict(type='str', required=True, aliases=['apikey']),
                action=dict(
                    type='str',
                    required=True,
                    choices=[
                        'getAccountDetails',
                        'getMonitors',
                        'newMonitor',
                        'editMonitor',
                        'deleteMonitor',
                        'resetMonitor',
                        'getAlertContacts',
                        'newAlertContact',
                        'editAlertContact',
                        'deleteAlertContact',
                        'getMWindows',
                        'newMWindow',
                        'editMWindow',
                        'deleteMWindow',
                        'getPSPs',
                        'newPSP',
                        'editPSP',
                        'deletePSP',
                        # for backwards compatibility
                        'started',
                        'paused'
                    ],
                    aliases=['state']
                ),
                params=dict(type='dict', required=False),
                # for backwards compatibility
                state=dict(type='str', required=False),
                monitorid=dict(type='str', required=False)
            ),
            supports_check_mode=SUPPORTS_CHECK_MODE
        )

        # collect necessary information for the api call
        params = module.params['params'] or dict()
        action = module.params['action']
        params['api_key'] = module.params['api_key']
        params['format'] = API_FORMAT
        params['noJsonCallback'] = API_NOJSONCALLBACK

        # test for backwards compatibility
        if module.params['action'] in ['started', 'paused']:
            action = 'editMonitor'
            params['status'] = 1 if module.params['action'] == 'started' else 0
            params['id'] = module.params['monitorid']
            
        try:
            result = uptimerobot_api_call(action, params, module=module)
            module.exit_json(changed=True, result=result)
        except Exception as e:
            module.fail_json(msg=str(e))

    main()

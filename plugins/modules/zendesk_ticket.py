#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Luis Valle (levalle232@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import Request

def create_ticket(host, username, password, body, severity, subject):

    changed = False
    url = f'{host}/api/v2/tickets'
    payload = {
        "ticket": {
            "comment": {
                "body": body
            },
            "priority": severity,
            "subject": subject
        }
    }
    headers = {
        "Content-Type": "application/json",
    }

    try:
        request = Request(url_username=username, url_password=password, headers=headers)
        response = request.post(url, data=json.dumps(payload))
        if response.getcode() == 201:
            changed = True
            return {
                'changed': changed,
                'response': json.load(response),
            }
    except Exception as e:
        return {
            'changed': changed,
            'msg': to_native(e)
        }

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True, aliases=['user']),
            password=dict(type='str', required=True, aliases=['pass'], no_log=True),
            state=dict(type='str', required=True,
                       choices=['present', 'absent', 'update']),
            body=dict(type='str', required=False, default=''),
            severity=dict(type='str', required=False, default=''),
            subject=dict(type='str', required=True)
        ),
        supports_check_mode=False
    )

    host = module.params['host']
    username = module.params['username']
    password = module.params['password']
    state = module.params['state']
    body = module.params['body']
    severity = module.params['severity']
    subject = module.params['subject']

    if state == 'present':
        result = create_ticket(host, username, password, body, severity, subject)

    if 'msg' in result:
        module.fail_json(**result)
    else:
        module.exit_json(**result)

if __name__ == '__main__':
    main()

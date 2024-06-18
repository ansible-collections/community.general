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

class ZENDESK_API:
    def __init__(self, username, password, token, host):
        self.username = username
        self.password = password
        self.token = token
        self.host = host
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def api_token(self):
        if self.token:
            request = Request(url_username=f"{self.username}/token", url_password=self.token, headers=self.headers)
        else:
            request = Request(url_username=self.username, url_password=self.password, headers=self.headers)
        return request

    def create_ticket(self, body, priority, subject):
        changed = False
        url = f'{self.host}/api/v2/tickets'
        payload = {
            "ticket": {
                "comment": {
                    "body": body
                },
                "priority": priority,
                "subject": subject
            }
        }

        request = self.api_token()

        try:
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
    
    def close_ticket(self, ticket_id, status, body):
        url = f'{self.host}/api/v2/tickets/{ticket_id}'
        payload = {
            "ticket": {
                "status": status,
                "comment": {
                    "body": body
                }
            }
        }

        request = self.api_token()

        try:
            response = request.patch(url, data=json.dumps(payload))
            if response.getcode() in [200, 204]:
                return {
                    'changed': True,
                    'response': json.load(response),
                }
        except Exception as e:
            return {
                'changed': False,
                'msg': to_native(e)
            }
def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True, aliases=['user']),
            password=dict(type='str', required=False, aliases=['pass'], no_log=True),
            status=dict(type='str', required=True,
                       choices=['new', 'closed', 'resolved']),
            body=dict(type='str', required=False, default=''),
            priority=dict(type='str', required=False, choices=['urgent', 'high', 'normal', 'low']),
            subject=dict(type='str', required=False),
            token=dict(type='str', required=False, no_log=False),
            ticket_id=dict(type='int')
        ),
        supports_check_mode=False
    )

    host = module.params['host']
    username = module.params['username']
    password = module.params['password']
    status = module.params['status']
    body = module.params['body']
    priority = module.params['priority']
    subject = module.params['subject']
    token = module.params['token']
    ticket_id = module.params['ticket_id']

    if not password and not token:
        module.fail_json(msg="Either 'password' or 'token' must be provided.")
    
    zendesk_api = ZENDESK_API(username, password, token, host)

    if status == 'new':
        if not subject or not priority:
            module.fail_json(msg="Both 'subject' and 'priority' must be provided when creating a new ticket.")
        result = zendesk_api.create_ticket(body, priority, subject)
    elif status in ['closed', 'resolved']:
        if not ticket_id:
            module.fail_json(msg="The 'ticket_id' must be provided when the status is 'closed'")
        result = zendesk_api.close_ticket(ticket_id, status, body)
        
    if 'msg' in result:
        module.fail_json(**result)
    else:
        module.exit_json(**result)

if __name__ == '__main__':
    main()

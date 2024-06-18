#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Luis Valle (levalle232@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: zendesk_ticket
short_description: Manages tickets in Zendesk
description: 
  - This module allows you to create and delete tickets in Zendesk.
  - Authentication is handled by the ZENDESK_API class.
author: "Luis Valle (@elchico2007)"
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  host:
    type: str
    description: The URL of the Zendesk instance.
    required: true
  username:
    type: str
    description: The Zendesk account username.
    required: true
    aliases: ['user']
  password:
    type: str
    description: The Zendesk account password.
    required: false
    aliases: ['pass']
    no_log: true
  token:
    type: str
    description: The API token for authentication.
    required: false
    no_log: true
  body:
    type: str
    description: The body of the ticket.
    default: ''
  priority:
    type: str
    description: The priority of the ticket.
    choices: ['urgent', 'high', 'normal', 'low']
    default: normal
  status:
    type: str
    description: The status of the ticket.
    choices: ['new', 'closed', 'resolved']
    required: true
  ticket_id:
    type: int
    description: The ID of the ticket to be closed or resolved.
    required: false
  subject:
    type: str
    description: The subject of the ticket.
    required: false
examples:
  - name: Create a new ticket
    community.general.zendesk_ticket:
      username: 'your_username'
      token: 'your_api_token'
      host: 'https://yourcompany.zendesk.com'
      body: 'This is a sample ticket'
      priority: 'normal'
      subject: 'New Ticket'
      status: 'new'
  - name: Close a ticket
    community.general.zendesk_ticket:
      username: 'your_username'
      token: 'your_api_token'
      host: 'https://yourcompany.zendesk.com'
      ticket_id: 12345
      status: 'closed'
  - name: Resolve a ticket
    community.general.zendesk_ticket:
      username: 'your_username'
      token: 'your_api_token'
      host: 'https://yourcompany.zendesk.com'
      ticket_id: 12345
      status: 'resolved'
      body: 'Issue has been resolved'
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import Request


class ZENDESK_API:
    """
    Handles interactions with the Zendesk API for ticket management.

    Attributes:
        username (str): Zendesk account username.
        password (str): Zendesk account password (optional if token is used).
        token (str): API token for authentication (optional if password is used).
        host (str): URL of the Zendesk instance.
        headers (dict): Default headers for API requests.
    """
    def __init__(self, username, password, token, host):
        """
        Initializes the ZENDESK_API object with authentication credentials.

        Args:
            username (str): Zendesk account username.
            password (str): Zendesk account password.
            token (str): API token for authentication.
            host (str): URL of the Zendesk instance.
        """
        self.username = username
        self.password = password
        self.token = token
        self.host = host
        self.headers = {
            "Content-Type": "application/json",
        }

    def api_aut(self):
        """
        Configures and returns a Request object with authentication headers.

        Returns:
            Request: Configured Request object for API calls.
        """
        if self.token:
            request = Request(url_username=f'{self.username}/token', url_password=self.token, headers=self.headers)
        else:
            request = Request(url_username=self.username, url_password=self.password, headers=self.headers)
        return request

    def create_ticket(self, body, priority, subject):
        """
        Creates a new ticket in Zendesk.

        Args:
            body (str): The text body of the ticket.
            priority (str): The priority of the ticket (e.g., 'urgent', 'high', 'normal', 'low').
            subject (str): The subject of the ticket.

        Returns:
            dict: A dictionary containing the result of the ticket creation operation.
        """
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

        request = self.api_aut()

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
        """
        Closes or resolves a ticket in Zendesk.

        Args:
            ticket_id (int): The ID of the ticket to be closed or resolved.
            status (str): The new status for the ticket ('closed' or 'resolved').
            body (str): An optional comment to add to the ticket.

        Returns:
            dict: A dictionary containing the result of the ticket update operation.
        """
        url = f'{self.host}/api/v2/tickets/{ticket_id}'
        payload = {
            "ticket": {
                "status": status,
                "comment": {
                    "body": body
                }
            }
        }

        request = self.api_aut()

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
            status=dict(type='str', required=True, choices=['new', 'closed', 'resolved']),
            body=dict(type='str', default=''),
            priority=dict(type='str', choices=['urgent', 'high', 'normal', 'low'], default='normal'),
            subject=dict(type='str'),
            token=dict(type='str', required=False, no_log=True),
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

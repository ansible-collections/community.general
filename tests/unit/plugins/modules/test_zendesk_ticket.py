# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Luis Valle <levalle232@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.modules import zendesk_ticket
from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args, AnsibleExitJson, AnsibleFailJson
from httmock import HTTMock, response, urlmatch
import json

@urlmatch(netloc=r'(.*\.)?zendesk\.com$')
def zendesk_api_mock(request):
    return response(201, json.dumps({
        "ticket": {
            "id": 35436,
            "subject": "Test Ticket",
            "status": "new",
            "priority": "high",
            "description": "This is a test ticket body",
            "created_at": "2023-05-22T10:00:00Z",
            "updated_at": "2023-05-22T10:00:00Z",
            "requester_id": 20978392,
            "submitter_id": 76872,
            "assignee_id": 235323,
            "organization_id": 509974,
            "group_id": 98738,
            "tags": ["test", "mock"],
            "url": "https://example.zendesk.com/api/v2/tickets/35436.json"
        }
    }), {'Content-Type': 'application/json'},
    request)

class TestZendeskTicket(ModuleTestCase):
    def setUp(self):
        super(TestZendeskTicket, self).setUp()
        self.module = zendesk_ticket

    def tearDown(self):
        super(TestZendeskTicket, self).tearDown()

    def test_with_no_parameters(self):
        """
        Test that the module fails when no parameters are provided.
        """
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_create_ticket_no_password_or_token(self):
        """
        Test that the module fails when neither password nor token is provided.
        """
        ticket_data = {
            'url': 'http://zendesk.com',
            'username': 'your_username',
            'ticket_id': 28,
            'status': 'new',
            'body': 'This is a test ticket body',
            'priority': 'high',
            'subject': 'Test Ticket'
        }
        set_module_args(ticket_data)
        with self.assertRaises(AnsibleFailJson) as exc_info:
            self.module.main()
        result = exc_info.exception.args[0]
        self.assertTrue(result['failed'])
        self.assertEqual(result['msg'], 'one of the following is required: password, token')

    def test_resolve_ticket_idempotency_with_mock(self):
        """
        Test the module's behavior when attempting to resolve a non-existent ticket.
        """
        ticket_data = {
            'url': 'http://zendesk.com',
            'username': 'your_username',
            'password': 'your_password',
            'ticket_id': 35436,
            'status': 'closed',
            'body': 'Ticket is resolved.'
        }
        set_module_args(ticket_data)

        with self.assertRaises(AnsibleFailJson) as exc_info:
            self.module.main()

        result = exc_info.exception.args[0]
        self.assertTrue(result['failed'])
        self.assertEqual(result['msg'], 'Ticket ID 35436 does not exist.')

    def test_create_ticket_with_mock(self):
        set_module_args({
            'url': 'https://your_company.zendesk.com',
            'username': 'user',
            'token': 'test_token',
            'status': 'new',
            'subject': 'Test Ticket',
            'body': 'This is a test ticket body',
            'priority': 'high'
        })

        with HTTMock(zendesk_api_mock):
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['ticket']['id'], 35436)
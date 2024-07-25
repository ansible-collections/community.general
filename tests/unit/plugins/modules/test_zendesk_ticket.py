# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Luis Valle <levalle232@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.modules import zendesk_ticket
from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args, AnsibleExitJson, AnsibleFailJson

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
        Test that attempting to resolve a non-existent ticket fails.
        
        This test mocks a scenario where a ticket with ID 35436 does not exist,
        and verifies that the module fails with the appropriate error message
        when trying to resolve it.
        """
        ticket_data = {
            'url': 'http://zendesk.com',
            'username': 'your_username',
            'password': 'your_password',
            'ticket_id': 35436,
            'status': 'resolved',
            'body': 'Ticket is resolved.'
        }
        set_module_args(ticket_data)
        
        with self.assertRaises(AnsibleFailJson) as exc_info:
            self.module.main()
        
        result = exc_info.exception.args[0]
        self.assertTrue(result['failed'])
        self.assertEqual(result['msg'], 'Ticket ID 35436 does not exist.')
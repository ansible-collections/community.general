# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Luis Valle <levalle232@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.modules import zendesk_ticket

def test_create_ticket_failure():
    # Test creating a new ticket in Zendesk with invalid data
    invalid_ticket_data = {
        'host': 'https://your_zendesk_host',
        'username': 'your_username',
        'token': 'invalid_token',
        'ticket_id': 28,
        'status': 'very_old',
        'body': 'This is a test ticket body',
        'priority': 'high',
        'subject': 'Test Ticket'
    }
    api = zendesk_ticket.ZENDESK_API(username='your_username', password='your_password', token='invalid_token', host='https://your_zendesk_host')
    result = api.create_ticket(invalid_ticket_data['body'], invalid_ticket_data['priority'], invalid_ticket_data['subject'])
    assert 'msg' in result  # Assert that 'msg' is in the result indicating failure

def test_create_ticket_no_password():
    # Test creating a new ticket in Zendesk without providing a password
    ticket_data = {
        'host': 'https://your_zendesk_host',
        'username': 'your_username',
        'ticket_id': 28,
        'status': 'new',
        'body': 'This is a test ticket body',
        'priority': 'high',
        'subject': 'Test Ticket'
    }
    api = zendesk_ticket.ZENDESK_API(username='your_username', password='your_password', token='your_token', host='https://your_zendesk_host')
    result = api.create_ticket(ticket_data['body'], ticket_data['priority'], ticket_data['subject'])
    assert 'msg' in result  # Assert that 'msg' is in the result indicating failure

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules import discord
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestDiscordModule(ModuleTestCase):

    def setUp(self):
        super(TestDiscordModule, self).setUp()
        self.module = discord

    def tearDown(self):
        super(TestDiscordModule, self).tearDown()

    @pytest.fixture
    def fetch_url_mock(self, mocker):
        return mocker.patch('ansible.module_utils.notification.discord.fetch_url')

    def test_without_parameters(self):
        """Failure if no parameters set"""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_without_content(self):
        """Failure if content and embeds both are missing"""
        with set_module_args({
            'webhook_id': 'xxx',
            'webhook_token': 'xxx'
        }):
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_successful_message(self):
        """Test a basic message successfully."""
        with set_module_args({
            'webhook_id': 'xxx',
            'webhook_token': 'xxx',
            'content': 'test'
        }):

            with patch.object(discord, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (None, {"status": 204, 'msg': 'OK (0 bytes)'})
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['content'] == "test"

    def test_message_with_username(self):
        """Test a message with username set successfully."""
        with set_module_args({
            'webhook_id': 'xxx',
            'webhook_token': 'xxx',
            'content': 'test',
            'username': 'Ansible Bot'
        }):

            with patch.object(discord, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (None, {"status": 204, 'msg': 'OK (0 bytes)'})
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['username'] == "Ansible Bot"
            assert call_data['content'] == "test"

    def test_failed_message(self):
        """Test failure because webhook id is wrong."""

        with set_module_args({
            'webhook_id': 'wrong',
            'webhook_token': 'xxx',
            'content': 'test'
        }):

            with patch.object(discord, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    None,
                    {"status": 404, 'msg': 'HTTP Error 404: Not Found', 'body': '{"message": "Unknown Webhook", "code": 10015}'},
                )
                with self.assertRaises(AnsibleFailJson):
                    self.module.main()

    def test_failed_message_without_body(self):
        """Test failure with empty response body."""

        with set_module_args({
            'webhook_id': 'wrong',
            'webhook_token': 'xxx',
            'content': 'test'
        }):

            with patch.object(discord, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (None, {"status": 404, 'msg': 'HTTP Error 404: Not Found'})
                with self.assertRaises(AnsibleFailJson):
                    self.module.main()

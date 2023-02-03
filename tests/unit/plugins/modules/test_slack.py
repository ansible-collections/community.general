# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from ansible_collections.community.general.tests.unit.compat.mock import Mock, patch
from ansible_collections.community.general.plugins.modules import slack
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestSlackModule(ModuleTestCase):

    def setUp(self):
        super(TestSlackModule, self).setUp()
        self.module = slack

    def tearDown(self):
        super(TestSlackModule, self).tearDown()

    @pytest.fixture
    def fetch_url_mock(self, mocker):
        return mocker.patch('ansible.module_utils.notification.slack.fetch_url')

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_invalid_old_token(self):
        """Failure if there is an old style token"""
        set_module_args({
            'token': 'test',
        })
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_successful_message(self):
        """tests sending a message. This is example 1 from the docs"""
        set_module_args({
            'token': 'XXXX/YYYY/ZZZZ',
            'msg': 'test'
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 200})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['username'] == "Ansible"
            assert call_data['text'] == "test"
            assert fetch_url_mock.call_args[1]['url'] == "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"

    def test_failed_message(self):
        """tests failing to send a message"""

        set_module_args({
            'token': 'XXXX/YYYY/ZZZZ',
            'msg': 'test'
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 404, 'msg': 'test'})
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_message_with_thread(self):
        """tests sending a message with a thread"""
        set_module_args({
            'token': 'XXXX/YYYY/ZZZZ',
            'msg': 'test',
            'thread_id': '100.00'
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 200})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['username'] == "Ansible"
            assert call_data['text'] == "test"
            assert call_data['thread_ts'] == '100.00'
            assert fetch_url_mock.call_args[1]['url'] == "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"

    # https://github.com/ansible-collections/community.general/issues/1097
    def test_ts_in_message_does_not_cause_edit(self):
        set_module_args({
            'token': 'xoxa-123456789abcdef',
            'msg': 'test with ts'
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            mock_response = Mock()
            mock_response.read.return_value = '{"fake":"data"}'
            fetch_url_mock.return_value = (mock_response, {"status": 200})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            self.assertEquals(fetch_url_mock.call_args[1]['url'], "https://slack.com/api/chat.postMessage")

    def test_edit_message(self):
        set_module_args({
            'token': 'xoxa-123456789abcdef',
            'msg': 'test2',
            'message_id': '12345'
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            mock_response = Mock()
            mock_response.read.return_value = '{"messages":[{"ts":"12345","msg":"test1"}]}'
            fetch_url_mock.side_effect = [
                (mock_response, {"status": 200}),
                (mock_response, {"status": 200}),
            ]
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 2)
            self.assertEquals(fetch_url_mock.call_args[1]['url'], "https://slack.com/api/chat.update")
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            self.assertEquals(call_data['ts'], "12345")

    def test_message_with_blocks(self):
        """tests sending a message with blocks"""
        set_module_args({
            'token': 'XXXX/YYYY/ZZZZ',
            'msg': 'test',
            'blocks': [{
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*test*'
                },
                'accessory': {
                    'type': 'image',
                    'image_url': 'https://docs.ansible.com/favicon.ico',
                    'alt_text': 'test'
                }
            }, {
                'type': 'section',
                'text': {
                    'type': 'plain_text',
                    'text': 'test',
                    'emoji': True
                }
            }]
        })

        with patch.object(slack, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 200})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['username'] == "Ansible"
            assert call_data['blocks'][1]['text']['text'] == "test"
            assert fetch_url_mock.call_args[1]['url'] == "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"

    def test_message_with_invalid_color(self):
        """tests sending invalid color value to module"""
        set_module_args({
            'token': 'XXXX/YYYY/ZZZZ',
            'msg': 'test',
            'color': 'aa',
        })
        with self.assertRaises(AnsibleFailJson) as exec_info:
            self.module.main()

        msg = "Color value specified should be either one of" \
              " ['normal', 'good', 'warning', 'danger'] or any valid" \
              " hex value with length 3 or 6."
        assert exec_info.exception.args[0]['msg'] == msg


color_test = [
    ('#111111', True),
    ('#00aabb', True),
    ('#abc', True),
    ('#gghhjj', False),
    ('#ghj', False),
    ('#a', False),
    ('#aaaaaaaa', False),
    ('', False),
    ('aaaa', False),
    ('$00aabb', False),
    ('$00a', False),
]


@pytest.mark.parametrize("color_value, ret_status", color_test)
def test_is_valid_hex_color(color_value, ret_status):
    generated_value = slack.is_valid_hex_color(color_value)
    assert generated_value == ret_status

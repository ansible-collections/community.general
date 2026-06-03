# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import google_chat

WEBHOOK = "https://chat.googleapis.com/v1/spaces/SPACE_ID/messages?key=KEY&token=TOKEN"


def make_response(payload):
    """Build a fake fetch_url file-like response whose read() returns JSON text."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps(payload)
    return mock_response


class TestGoogleChatModule(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = google_chat

    def tearDown(self):
        super().tearDown()

    def test_without_required_parameters(self):
        """Failure must occur when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_missing_text(self):
        """Failure when webhook_url is given but text is missing"""
        with set_module_args({"webhook_url": WEBHOOK}):
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_missing_webhook_url(self):
        """Failure when text is given but webhook_url is missing"""
        with set_module_args({"text": "test"}):
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_invalid_message_reply_option(self):
        """Failure when message_reply_option is not one of the valid choices"""
        with set_module_args({"webhook_url": WEBHOOK, "text": "test", "message_reply_option": "BOGUS"}):
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_successful_message(self):
        """tests sending a plain message"""
        with set_module_args({"webhook_url": WEBHOOK, "text": "test"}):
            with patch.object(google_chat, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    make_response({"name": "spaces/AAAA/messages/BBBB.BBBB"}),
                    {"status": 200},
                )
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()

        self.assertTrue(fetch_url_mock.call_count, 1)
        call_data = json.loads(fetch_url_mock.call_args[1]["data"])
        assert call_data["text"] == "test"
        assert "thread" not in call_data
        assert fetch_url_mock.call_args[1]["url"] == WEBHOOK
        assert fetch_url_mock.call_args[1]["method"] == "POST"
        assert result.exception.args[0]["changed"]
        assert result.exception.args[0]["name"] == "spaces/AAAA/messages/BBBB.BBBB"

    def test_failed_message(self):
        """tests failing to send a message (non-200 response)"""
        with set_module_args({"webhook_url": WEBHOOK, "text": "test"}):
            with patch.object(google_chat, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    None,
                    {"status": 404, "msg": "not found", "body": b"NOT_FOUND"},
                )
                with self.assertRaises(AnsibleFailJson) as result:
                    self.module.main()

        assert "Google Chat" in result.exception.args[0]["msg"]
        assert "404" in result.exception.args[0]["msg"]

    def test_message_with_thread(self):
        """tests sending a message with a thread_key and reading back the thread name"""
        with set_module_args({"webhook_url": WEBHOOK, "text": "test", "thread_key": "deploy-1"}):
            with patch.object(google_chat, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    make_response(
                        {
                            "name": "spaces/AAAA/messages/BBBB.BBBB",
                            "thread": {"name": "spaces/AAAA/threads/CCCC"},
                        }
                    ),
                    {"status": 200},
                )
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()

        self.assertTrue(fetch_url_mock.call_count, 1)
        call_data = json.loads(fetch_url_mock.call_args[1]["data"])
        assert call_data["text"] == "test"
        assert call_data["thread"]["threadKey"] == "deploy-1"
        assert result.exception.args[0]["thread_name"] == "spaces/AAAA/threads/CCCC"

    def test_message_reply_option_appended_to_url(self):
        """message_reply_option must be added as a query parameter with & (webhook already has ?)"""
        with set_module_args(
            {
                "webhook_url": WEBHOOK,
                "text": "test",
                "thread_key": "deploy-1",
                "message_reply_option": "REPLY_MESSAGE_OR_FAIL",
            }
        ):
            with patch.object(google_chat, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    make_response({"name": "spaces/AAAA/messages/BBBB.BBBB"}),
                    {"status": 200},
                )
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

        url = fetch_url_mock.call_args[1]["url"]
        assert url == WEBHOOK + "&messageReplyOption=REPLY_MESSAGE_OR_FAIL"

    def test_check_mode(self):
        """check mode reports changed and never calls the API"""
        with set_module_args({"webhook_url": WEBHOOK, "text": "test", "_ansible_check_mode": True}):
            with patch.object(google_chat, "fetch_url") as fetch_url_mock:
                with self.assertRaises(AnsibleExitJson) as result:
                    self.module.main()

        fetch_url_mock.assert_not_called()
        assert result.exception.args[0]["changed"]
        assert "name" not in result.exception.args[0]


def test_build_payload_without_thread():
    payload = google_chat.build_payload("hello", None)
    assert payload == {"text": "hello"}


def test_build_payload_with_thread():
    payload = google_chat.build_payload("hello", "deploy-1")
    assert payload == {"text": "hello", "thread": {"threadKey": "deploy-1"}}


build_url_cases = [
    # (webhook_url, message_reply_option, expected_url)
    (WEBHOOK, None, WEBHOOK),
    (
        WEBHOOK,
        "REPLY_MESSAGE_OR_FAIL",
        WEBHOOK + "&messageReplyOption=REPLY_MESSAGE_OR_FAIL",
    ),
    (
        "https://chat.googleapis.com/v1/spaces/X/messages",
        "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
        "https://chat.googleapis.com/v1/spaces/X/messages?messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
    ),
]


@pytest.mark.parametrize("webhook_url, option, expected", build_url_cases)
def test_build_url(webhook_url, option, expected):
    assert google_chat.build_url(webhook_url, option) == expected

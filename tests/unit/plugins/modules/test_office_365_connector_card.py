# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import office_365_connector_card

WEBHOOK = "https://example.invalid/webhook"


@pytest.fixture(autouse=True)
def patch_module():
    with patch.multiple(
        "ansible.module_utils.basic.AnsibleModule",
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


@pytest.fixture
def fetch_url_mock():
    with patch.object(office_365_connector_card, "fetch_url") as mock:
        yield mock


def run_module(fetch_url_mock, status, msg, expected_exception, args=None, info_extra=None):
    info = {"status": status, "msg": msg}
    if info_extra:
        info.update(info_extra)
    fetch_url_mock.return_value = (None, info)
    module_args = {"webhook": WEBHOOK}
    if args:
        module_args.update(args)
    with pytest.raises(expected_exception) as exc:
        with set_module_args(module_args):
            office_365_connector_card.main()
    assert fetch_url_mock.call_count >= 1
    assert fetch_url_mock.call_args[1]["url"] == WEBHOOK
    assert fetch_url_mock.call_args[1]["method"] == "POST"
    assert fetch_url_mock.call_args[1]["headers"]["Content-Type"] == "application/json"
    return exc.value.args[0], json.loads(fetch_url_mock.call_args[1]["data"])


def test_without_required_parameters():
    with pytest.raises(AnsibleFailJson):
        with set_module_args({}):
            office_365_connector_card.main()


def test_success_200(fetch_url_mock):
    result, payload = run_module(fetch_url_mock, 200, "OK", AnsibleExitJson, args={"text": "hello"})
    assert result["changed"] is True
    assert payload["text"] == "hello"
    assert payload["@type"] == "MessageCard"
    assert payload["@context"] == "http://schema.org/extensions"


def test_success_202_power_automate(fetch_url_mock):
    result, payload = run_module(fetch_url_mock, 202, "Accepted", AnsibleExitJson, args={"text": "hello"})
    assert result["changed"] is True
    assert payload["text"] == "hello"


def test_failure_status(fetch_url_mock):
    result, _payload = run_module(fetch_url_mock, 500, "Internal Server Error", AnsibleFailJson, args={"text": "hello"})
    assert "Internal Server Error" in result["msg"]


def test_success_with_summary_only(fetch_url_mock):
    result, payload = run_module(fetch_url_mock, 200, "OK", AnsibleExitJson, args={"summary": "Deploy finished"})
    assert result["changed"] is True
    assert payload["summary"] == "Deploy finished"
    assert "text" not in payload


def test_success_with_title_and_color(fetch_url_mock):
    result, payload = run_module(
        fetch_url_mock,
        200,
        "OK",
        AnsibleExitJson,
        args={"text": "body", "title": "Card title", "color": "E81123"},
    )
    assert result["changed"] is True
    assert payload["text"] == "body"
    assert payload["title"] == "Card title"
    assert payload["themeColor"] == "E81123"


def test_success_with_actions(fetch_url_mock):
    actions = [
        {
            "@type": "ActionCard",
            "name": "Comment",
            "inputs": [
                {
                    "@type": "TextInput",
                    "id": "comment",
                    "is_multiline": True,
                    "title": "Input title",
                }
            ],
            "actions": [{"@type": "HttpPOST", "name": "Save", "target": "http://example.invalid/save"}],
        },
        {
            "@type": "OpenUri",
            "name": "View",
            "targets": [{"os": "default", "uri": "http://example.invalid"}],
        },
    ]
    result, payload = run_module(fetch_url_mock, 200, "OK", AnsibleExitJson, args={"text": "hello", "actions": actions})
    assert result["changed"] is True
    assert "potentialAction" in payload
    assert payload["potentialAction"][0]["name"] == "Comment"
    assert payload["potentialAction"][0]["inputs"][0]["isMultiline"] is True
    assert payload["potentialAction"][1]["@type"] == "OpenUri"


def test_success_with_sections(fetch_url_mock):
    sections = [
        {
            "title": "Section title",
            "start_group": True,
            "activity_image": "http://example.invalid/img.jpg",
            "activity_title": "Activity title",
            "activity_subtitle": "Activity subtitle",
            "activity_text": "Activity text",
            "text": "Section text",
            "facts": [{"name": "Status", "value": "OK"}],
            "images": [{"image": "http://example.invalid/a.jpg", "title": "alt"}],
            "actions": [{"@type": "HttpPOST", "name": "Save", "target": "http://example.invalid"}],
        }
    ]
    result, payload = run_module(
        fetch_url_mock, 200, "OK", AnsibleExitJson, args={"summary": "summary", "sections": sections}
    )
    assert result["changed"] is True
    section = payload["sections"][0]
    assert section["title"] == "Section title"
    assert section["startGroup"] is True
    assert section["activityImage"] == "http://example.invalid/img.jpg"
    assert section["activityTitle"] == "Activity title"
    assert section["activitySubtitle"] == "Activity subtitle"
    assert section["activityText"] == "Activity text"
    assert section["text"] == "Section text"
    assert section["facts"] == [{"name": "Status", "value": "OK"}]
    assert section["images"][0]["image"] == "http://example.invalid/a.jpg"
    assert section["potentialAction"][0]["name"] == "Save"


def test_check_mode_empty_payload_accepted(fetch_url_mock):
    result, payload = run_module(
        fetch_url_mock,
        400,
        "Bad Request",
        AnsibleExitJson,
        args={"text": "hello", "_ansible_check_mode": True},
        info_extra={"body": office_365_connector_card.OFFICE_365_CARD_EMPTY_PAYLOAD_MSG},
    )
    assert result["changed"] is True
    # check mode validates connectivity with an empty MessageCard payload
    assert "text" not in payload
    assert payload["@type"] == "MessageCard"
    assert fetch_url_mock.call_count == 1


def test_check_mode_invalid_webhook(fetch_url_mock):
    result, _payload = run_module(
        fetch_url_mock,
        400,
        "Bad Request",
        AnsibleFailJson,
        args={"text": "hello", "_ansible_check_mode": True},
        info_extra={"body": "some other error"},
    )
    assert result["msg"] == office_365_connector_card.OFFICE_365_INVALID_WEBHOOK_MSG


def test_check_mode_success_200(fetch_url_mock):
    result, payload = run_module(
        fetch_url_mock,
        200,
        "OK",
        AnsibleExitJson,
        args={"text": "hello", "_ansible_check_mode": True},
    )
    assert result["changed"] is True
    assert "text" not in payload
    assert fetch_url_mock.call_count == 1


def test_non_check_mode_400_fails(fetch_url_mock):
    result, _payload = run_module(
        fetch_url_mock,
        400,
        "Bad Request",
        AnsibleFailJson,
        args={"text": "hello"},
        info_extra={"body": office_365_connector_card.OFFICE_365_CARD_EMPTY_PAYLOAD_MSG},
    )
    assert "Bad Request" in result["msg"]

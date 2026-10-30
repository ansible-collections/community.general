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


def run_module(fetch_url_mock, status, msg, expected_exception):
    fetch_url_mock.return_value = (None, {"status": status, "msg": msg})
    with pytest.raises(expected_exception) as exc:
        with set_module_args({"webhook": WEBHOOK, "text": "hello"}):
            office_365_connector_card.main()
    assert fetch_url_mock.call_count == 1
    assert fetch_url_mock.call_args[1]["url"] == WEBHOOK
    assert json.loads(fetch_url_mock.call_args[1]["data"])["text"] == "hello"
    return exc.value.args[0]


def test_without_required_parameters():
    with pytest.raises(AnsibleFailJson):
        with set_module_args({}):
            office_365_connector_card.main()


def test_success_200(fetch_url_mock):
    result = run_module(fetch_url_mock, 200, "OK", AnsibleExitJson)
    assert result["changed"] is True


def test_success_202_power_automate(fetch_url_mock):
    result = run_module(fetch_url_mock, 202, "Accepted", AnsibleExitJson)
    assert result["changed"] is True


def test_failure_status(fetch_url_mock):
    result = run_module(fetch_url_mock, 500, "Internal Server Error", AnsibleFailJson)
    assert "Internal Server Error" in result["msg"]

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import github_secrets_info

GITHUB_SECRETS_RESPONSE = {
    "total_count": 2,
    "secrets": [
        {
            "name": "SECRET1",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        },
        {
            "name": "SECRET2",
            "created_at": "2026-01-03T00:00:00Z",
            "updated_at": "2026-01-04T00:00:00Z",
        },
    ],
}


def make_fetch_url_response(body, status=200):
    response = MagicMock()
    response.read.return_value = json.dumps(body).encode("utf-8")
    info = {"status": status, "msg": f"OK ({len(json.dumps(body))} bytes)"}
    return (response, info)


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
    with patch.object(github_secrets_info, "fetch_url") as mock:
        yield mock


def test_list_repo_secrets(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(GITHUB_SECRETS_RESPONSE),
        make_fetch_url_response({}, status=200),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets_info.main()

    result = exc.value.args[0]
    assert result["changed"] is False
    assert result["secrets"] == GITHUB_SECRETS_RESPONSE["secrets"]


def test_fail_list_repo_secrets(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response({}, status=404),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets_info.main()

    result = exc.value.args[0]
    assert result["changed"] is False
    assert result["secrets"] == []

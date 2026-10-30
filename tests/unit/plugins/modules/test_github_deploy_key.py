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

from ansible_collections.community.general.plugins.modules import github_deploy_key

KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyMaterial user@example"

EXISTING_KEYS = [
    {"id": 42, "key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyMaterial", "title": "deploy"},
]


def make_response(body, status=200):
    response = MagicMock()
    response.read.return_value = json.dumps(body).encode("utf-8")
    return (response, {"status": status})


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
    with patch.object(github_deploy_key, "fetch_url") as mock:
        yield mock


def module_args(**kwargs):
    args = {
        "owner": "ansible",
        "repo": "example",
        "name": "deploy",
        "key": KEY,
        "token": "secret",
    }
    args.update(kwargs)
    return args


def test_absent_check_mode_existing_key_is_not_deleted(fetch_url_mock):
    fetch_url_mock.return_value = make_response(EXISTING_KEYS)

    with set_module_args(module_args(state="absent", _ansible_check_mode=True)):
        with pytest.raises(AnsibleExitJson) as exc:
            github_deploy_key.main()

    assert exc.value.args[0]["changed"] is True
    methods = [call.kwargs.get("method") for call in fetch_url_mock.call_args_list]
    assert "DELETE" not in methods
    assert methods == ["GET"]


def test_absent_check_mode_missing_key(fetch_url_mock):
    fetch_url_mock.return_value = make_response([])

    with set_module_args(module_args(state="absent", _ansible_check_mode=True)):
        with pytest.raises(AnsibleExitJson) as exc:
            github_deploy_key.main()

    assert exc.value.args[0]["changed"] is False
    methods = [call.kwargs.get("method") for call in fetch_url_mock.call_args_list]
    assert "DELETE" not in methods


def test_absent_deletes_existing_key(fetch_url_mock):
    fetch_url_mock.side_effect = [make_response(EXISTING_KEYS), make_response(None, status=204)]

    with set_module_args(module_args(state="absent")):
        with pytest.raises(AnsibleExitJson) as exc:
            github_deploy_key.main()

    assert exc.value.args[0]["changed"] is True
    assert fetch_url_mock.call_args_list[-1].kwargs["method"] == "DELETE"
    assert fetch_url_mock.call_args_list[-1].args[1].endswith("/repos/ansible/example/keys/42")

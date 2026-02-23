# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import github_secrets

PUBLIC_KEY_PAYLOAD = {
    "key_id": "100",
    "key": "j6gSA9mu5bO8ig+YBNU6oXRhGwd3Z4EFiS9rVmU9gwo=",
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
    with patch.object(github_secrets, "fetch_url") as mock:
        yield mock


def test_encrypt_secret():
    result = github_secrets.encrypt_secret(PUBLIC_KEY_PAYLOAD["key"], "ansible")
    assert isinstance(result, str)
    assert result != "ansible"
    assert len(result) > 70


def test_fail_without_parameters():
    with pytest.raises(AnsibleFailJson):
        with set_module_args({}):
            github_secrets.main()


def test_fail_present_without_value():
    with pytest.raises(AnsibleFailJson) as exc:
        with set_module_args(
            {
                "organization": "myorg",
                "repository": "myrepo",
                "key": "MY_SECRET",
                "value": None,
                "state": "present",
                "token": "ghp_test_token",
            }
        ):
            github_secrets.main()
    assert "value' parameter cannot be empty" in exc.value.args[0]["details"]


def test_fail_org_secret_present_without_visibility():
    with pytest.raises(AnsibleFailJson) as exc:
        with set_module_args(
            {
                "organization": "myorg",
                "key": "ORG_SECRET",
                "value": "org_value",
                "state": "present",
                "token": "ghp_test_token",
            }
        ):
            github_secrets.main()
    assert "'visibility' must be provided" in exc.value.args[0]["details"]


def test_create_repo_secret(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(PUBLIC_KEY_PAYLOAD),
        make_fetch_url_response({}, status=201),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "value": "secret_value",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets.main()

    result = exc.value.args[0]
    assert result["changed"] is True
    assert result["result"]["status"] == 201
    assert result["result"]["response"] == "Secret created"


def test_update_repo_secret(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(PUBLIC_KEY_PAYLOAD),
        make_fetch_url_response({}, status=204),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "value": "new_value",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets.main()

    result = exc.value.args[0]
    assert result["changed"] is True
    assert result["result"]["response"] == "Secret updated"


def test_update_empty_repo_secret(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(PUBLIC_KEY_PAYLOAD),
        make_fetch_url_response({}, status=204),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "value": "",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets.main()

    result = exc.value.args[0]
    assert result["changed"] is True
    assert result["result"]["response"] == "Secret updated"


def test_update_missing_value_repo_secret(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(PUBLIC_KEY_PAYLOAD),
        make_fetch_url_response({}, status=204),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleFailJson) as exc:
            github_secrets.main()

    assert "the following are missing: value" in exc.value.args[0]["msg"]


def test_delete_repo_secret(fetch_url_mock):
    fetch_url_mock.return_value = make_fetch_url_response({}, status=204)

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "state": "absent",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets.main()

    result = exc.value.args[0]
    assert result["changed"] is True
    assert result["result"]["status"] == 204
    assert result["result"]["response"] == "Secret deleted"


def test_delete_dne_repo_secret(fetch_url_mock):
    fetch_url_mock.return_value = make_fetch_url_response({}, status=404)

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "DOES_NOT_EXIST",
            "state": "absent",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleExitJson) as exc:
            github_secrets.main()

    result = exc.value.args[0]
    assert result["changed"] is False
    assert result["result"]["status"] == 404
    assert result["result"]["response"] == "Secret not found"


def test_fail_get_public_key(fetch_url_mock):
    fetch_url_mock.return_value = make_fetch_url_response({}, status=403)

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "value": "secret_value",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleFailJson) as exc:
            github_secrets.main()
    assert "Failed to get public key" in exc.value.args[0]["msg"]


def test_fail_upsert_secret(fetch_url_mock):
    fetch_url_mock.side_effect = [
        make_fetch_url_response(PUBLIC_KEY_PAYLOAD),
        make_fetch_url_response({}, status=422),
    ]

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "value": "secret_value",
            "state": "present",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleFailJson) as exc:
            github_secrets.main()
    assert "Failed to upsert secret" in exc.value.args[0]["msg"]


def test_fail_delete_secret(fetch_url_mock):
    fetch_url_mock.return_value = make_fetch_url_response({}, status=503)

    with set_module_args(
        {
            "organization": "myorg",
            "repository": "myrepo",
            "key": "MY_SECRET",
            "state": "absent",
            "token": "ghp_test_token",
        }
    ):
        with pytest.raises(AnsibleFailJson) as exc:
            github_secrets.main()
    assert "Failed to delete secret" in exc.value.args[0]["msg"]

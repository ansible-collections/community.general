# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


from ansible_collections.community.general.plugins.modules import jenkins_credential
from unittest.mock import (
    MagicMock,
    patch,
    mock_open,
)

import builtins
import json


def test_validate_file_exist_passes_when_file_exists():
    module = MagicMock()
    with patch("os.path.exists", return_value=True):
        jenkins_credential.validate_file_exist(module, "/some/file/path")
        module.fail_json.assert_not_called()


def test_validate_file_exist_fails_when_file_missing():
    module = MagicMock()
    with patch("os.path.exists", return_value=False):
        jenkins_credential.validate_file_exist(module, "/missing/file/path")
        module.fail_json.assert_called_once_with(msg="File not found: /missing/file/path")


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_get_jenkins_crumb_sets_crumb_header(fetch_mock):
    module = MagicMock()
    module.params = {"type": "file", "url": "http://localhost:8080"}
    headers = {}

    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"crumbRequestField": "crumb_field", "crumb": "abc123"}).encode(
        "utf-8"
    )

    fetch_mock.return_value = (
        fake_response,
        {"status": 200, "set-cookie": "JSESSIONID=something; Path=/"},
    )

    crumb_request_field, crumb, session_coockie = jenkins_credential.get_jenkins_crumb(module, headers)

    assert "Cookie" not in headers
    assert "crumb_field" in headers
    assert crumb == "abc123"
    assert headers[crumb_request_field] == crumb


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_get_jenkins_crumb_sets_cookie_if_type_token(fetch_mock):
    module = MagicMock()
    module.params = {"type": "token", "url": "http://localhost:8080"}
    headers = {}

    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"crumbRequestField": "crumb_field", "crumb": "secure"}).encode(
        "utf-8"
    )

    fetch_mock.return_value = (
        fake_response,
        {"status": 200, "set-cookie": "JSESSIONID=token-cookie; Path=/"},
    )

    crumb_request_field, crumb, session_cookie = jenkins_credential.get_jenkins_crumb(module, headers)

    assert "crumb_field" in headers
    assert crumb == "secure"
    assert headers[crumb_request_field] == crumb
    assert headers["Cookie"] == session_cookie


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_get_jenkins_crumb_fails_on_non_200_status(fetch_mock):
    module = MagicMock()
    module.params = {"type": "file", "url": "http://localhost:8080"}
    headers = {}

    fetch_mock.return_value = (MagicMock(), {"status": 403})

    jenkins_credential.get_jenkins_crumb(module, headers)

    module.fail_json.assert_called_once()
    assert "Failed to fetch Jenkins crumb" in module.fail_json.call_args[1]["msg"]


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_get_jenkins_crumb_removes_job_from_url(fetch_mock):
    module = MagicMock()
    module.params = {"type": "file", "url": "http://localhost:8080/job/test"}
    headers = {}

    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"crumbRequestField": "Jenkins-Crumb", "crumb": "xyz"}).encode("utf-8")

    fetch_mock.return_value = (fake_response, {"status": 200, "set-cookie": ""})

    jenkins_credential.get_jenkins_crumb(module, headers)

    url_called = fetch_mock.call_args[0][1]
    assert url_called == "http://localhost:8080/crumbIssuer/api/json"


def test_clean_data_removes_extraneous_fields():
    data = {
        "id": "cred1",
        "description": "test",
        "jenkins_user": "admin",
        "token": "secret",
        "url": "http://localhost:8080",
        "file_path": None,
    }
    expected = {"id": "cred1", "description": "test"}
    result = jenkins_credential.clean_data(data)
    assert result == expected, f"Expected {expected}, got {result}"


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_target_exists_returns_true_on_200(fetch_url_mock):
    module = MagicMock()
    module.params = {
        "url": "http://localhost:8080",
        "location": "system",
        "scope": "_",
        "id": "my-id",
        "jenkins_user": "admin",
        "token": "secret",
        "type": "file",
    }

    fetch_url_mock.return_value = (MagicMock(), {"status": 200})
    assert jenkins_credential.target_exists(module) is True


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_target_exists_returns_false_on_404(fetch_url_mock):
    module = MagicMock()
    module.params = {
        "url": "http://localhost:8080",
        "location": "system",
        "scope": "_",
        "id": "my-id",
        "jenkins_user": "admin",
        "token": "secret",
        "type": "file",
    }

    fetch_url_mock.return_value = (MagicMock(), {"status": 404})
    assert jenkins_credential.target_exists(module) is False


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_target_exists_calls_fail_json_on_unexpected_status(fetch_url_mock):
    module = MagicMock()
    module.params = {
        "url": "http://localhost:8080",
        "location": "system",
        "scope": "_",
        "id": "my-id",
        "jenkins_user": "admin",
        "token": "secret",
        "type": "file",
    }

    fetch_url_mock.return_value = (MagicMock(), {"status": 500})
    jenkins_credential.target_exists(module)
    module.fail_json.assert_called_once()
    assert "Unexpected status code" in module.fail_json.call_args[1]["msg"]


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_target_exists_skips_check_for_token_type(fetch_url_mock):
    module = MagicMock()
    module.params = {
        "type": "token",
        "url": "ignored",
        "location": "ignored",
        "scope": "ignored",
        "id": "ignored",
        "jenkins_user": "ignored",
        "token": "ignored",
    }

    assert jenkins_credential.target_exists(module) is False
    fetch_url_mock.assert_not_called()


@patch("ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url")
def test_delete_target_fails_deleting(fetch_mock):
    module = MagicMock()
    module.params = {
        "type": "token",
        "jenkins_user": "admin",
        "url": "http://localhost:8080",
        "id": "token-id",
        "location": "system",
        "scope": "_",
    }
    headers = {"Authorization": "Basic abc", "Content-Type": "whatever"}

    fetch_mock.return_value = (MagicMock(), {"status": 500})

    jenkins_credential.delete_target(module, headers)

    module.fail_json.assert_called_once()
    assert "Failed to delete" in module.fail_json.call_args[1]["msg"]


@patch(
    "ansible_collections.community.general.plugins.modules.jenkins_credential.fetch_url",
    side_effect=Exception("network error"),
)
def test_delete_target_raises_exception(fetch_mock):
    module = MagicMock()
    module.params = {
        "type": "scope",
        "jenkins_user": "admin",
        "location": "system",
        "url": "http://localhost:8080",
        "id": "domain-id",
        "scope": "_",
    }
    headers = {"Authorization": "Basic auth"}

    jenkins_credential.delete_target(module, headers)

    module.fail_json.assert_called_once()
    assert "Exception during delete" in module.fail_json.call_args[1]["msg"]
    assert "network error" in module.fail_json.call_args[1]["msg"]


def test_read_privateKey_returns_trimmed_contents():
    module = MagicMock()
    module.params = {"private_key_path": "/fake/path/key.pem"}

    mocked_file = mock_open(read_data="\n   \t  -----BEGIN PRIVATE KEY-----\nKEYDATA\n-----END PRIVATE KEY-----   \n\n")
    with patch("builtins.open", mocked_file):
        result = jenkins_credential.read_privateKey(module)

    expected = "-----BEGIN PRIVATE KEY-----\nKEYDATA\n-----END PRIVATE KEY-----"

    assert result == expected
    mocked_file.assert_called_once_with("/fake/path/key.pem", "r")


def test_read_privateKey_handles_file_read_error():
    module = MagicMock()
    module.params = {"private_key_path": "/invalid/path.pem"}

    with patch("builtins.open", side_effect=IOError("cannot read file")):
        jenkins_credential.read_privateKey(module)

    module.fail_json.assert_called_once()
    assert "Failed to read private key file" in module.fail_json.call_args[1]["msg"]


def test_embed_file_into_body_returns_multipart_fields():
    module = MagicMock()
    file_path = "/fake/path/secret.pem"
    credentials = {"id": "my-id"}
    fake_file_content = b"MY SECRET DATA"

    mock = mock_open()
    mock.return_value.read.return_value = fake_file_content

    with patch("os.path.basename", return_value="secret.pem"), patch.object(builtins, "open", mock):
        body, content_type = jenkins_credential.embed_file_into_body(module, file_path, credentials.copy())

    assert "multipart/form-data; boundary=" in content_type

    # Check if file content is embedded in body
    assert b"MY SECRET DATA" in body
    assert b'filename="secret.pem"' in body


def test_embed_file_into_body_fails_when_file_unreadable():
    module = MagicMock()
    file_path = "/fake/path/missing.pem"
    credentials = {"id": "something"}

    with patch("builtins.open", side_effect=IOError("can't read file")):
        jenkins_credential.embed_file_into_body(module, file_path, credentials)

    module.fail_json.assert_called_once()
    assert "Failed to read file" in module.fail_json.call_args[1]["msg"]


def test_embed_file_into_body_injects_file_keys_into_credentials():
    module = MagicMock()
    file_path = "/fake/path/file.txt"
    credentials = {"id": "test"}

    with patch("builtins.open", mock_open(read_data=b"1234")), patch("os.path.basename", return_value="file.txt"):
        jenkins_credential.embed_file_into_body(module, file_path, credentials)

    assert credentials["file"] == "file0"
    assert credentials["fileName"] == "file.txt"

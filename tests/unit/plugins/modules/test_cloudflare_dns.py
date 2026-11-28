# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import cloudflare_dns

ZONE = "example.com"
ZONE_ID = "zone-id-1"


def mx_record(record_id, content, priority):
    return {
        "id": record_id,
        "type": "MX",
        "name": ZONE,
        "content": content,
        "priority": priority,
        "ttl": 1,
        "comment": None,
        "tags": [],
    }


class FakeCloudflareAPI:
    def __init__(self, records):
        self.records = records
        self.calls = []

    def __call__(self, module, url, headers=None, data=None, method="GET", timeout=None):
        parsed = urlparse(url)
        path = parsed.path.split("/client/v4", 1)[-1]
        query = parse_qs(parsed.query)
        payload = json.loads(data) if data else None
        self.calls.append((method, path, query, payload))

        if path == "/zones":
            result = [{"id": ZONE_ID, "name": ZONE}]
        elif path == f"/zones/{ZONE_ID}/dns_records" and method == "GET":
            result = [
                rr
                for rr in self.records
                if rr["type"] == query["type"][0]
                and rr["name"] == query["name"][0]
                and ("content.exact" not in query or rr["content"] == query["content.exact"][0])
            ]
        elif path == f"/zones/{ZONE_ID}/dns_records" and method == "POST":
            result = dict(payload, id="new-record-id")
        elif method == "DELETE":
            result = {"id": path.rsplit("/", 1)[-1]}
        else:
            raise AssertionError(f"Unexpected API call: {method} {url}")

        response = MagicMock()
        response.read.return_value = json.dumps({"success": True, "result": result}).encode("utf-8")
        return response, {"status": 200, "msg": "OK"}

    def calls_with(self, method):
        return [call for call in self.calls if call[0] == method]


@pytest.fixture(autouse=True)
def patch_module(mocker):
    mocker.patch.multiple("ansible.module_utils.basic.AnsibleModule", exit_json=exit_json, fail_json=fail_json)


@pytest.fixture
def fake_api(mocker):
    def install(records):
        api = FakeCloudflareAPI(records)
        mocker.patch.object(cloudflare_dns, "fetch_url", side_effect=api)
        return api

    return install


def run_module(args, check_mode=False):
    module_args = dict(zone=ZONE, type="MX", api_token="secret-token", **args)
    if check_mode:
        module_args["_ansible_check_mode"] = True
    with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
        with set_module_args(module_args):
            cloudflare_dns.main()
    return exc.value.args[0]


def test_create_null_mx(fake_api):
    api = fake_api([])

    result = run_module(dict(value=".", priority=0))

    assert result["changed"] is True
    assert result.get("failed") is not True
    posts = api.calls_with("POST")
    assert len(posts) == 1
    assert posts[0][3]["content"] == "."
    assert posts[0][3]["priority"] == 0


def test_create_null_mx_check_mode(fake_api):
    api = fake_api([])

    result = run_module(dict(value=".", priority=0), check_mode=True)

    assert result["changed"] is True
    assert api.calls_with("POST") == []


def test_null_mx_already_present(fake_api):
    api = fake_api([mx_record("null-mx-id", ".", 0)])

    result = run_module(dict(value=".", priority=0))

    assert result["changed"] is False
    assert api.calls_with("POST") == []
    assert api.calls_with("PUT") == []
    gets = [call for call in api.calls_with("GET") if call[1].endswith("/dns_records")]
    assert gets[0][2]["content.exact"] == ["."]


def test_remove_null_mx_keeps_other_mx_records(fake_api):
    api = fake_api([mx_record("null-mx-id", ".", 0), mx_record("mail-mx-id", "mail.example.com", 10)])

    result = run_module(dict(value=".", state="absent"))

    assert result["changed"] is True
    deletes = api.calls_with("DELETE")
    assert [call[1] for call in deletes] == [f"/zones/{ZONE_ID}/dns_records/null-mx-id"]


def test_mx_value_trailing_dot_is_stripped(fake_api):
    api = fake_api([])

    result = run_module(dict(value="Mail.Example.com.", priority=10))

    assert result["changed"] is True
    posts = api.calls_with("POST")
    assert posts[0][3]["content"] == "mail.example.com"

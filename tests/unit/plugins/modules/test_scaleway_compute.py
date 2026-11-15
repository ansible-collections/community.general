# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils._scaleway import Response, Scaleway
from ansible_collections.community.general.plugins.modules import scaleway_compute

IMAGE_ID = "6a601340-19c1-4ca7-9c1c-0704bcc9f5fe"
IP_ID = "8d4be757-dee6-403d-bea0-d3720506ddfe"
SERVER_ID = "c004b4cd-ef5g-678h-90i1-jk2345678l90"
SERVER_NAME = "foobar"


def make_response(status, body=None):
    info = {"status": status}
    if body is not None:
        info["body"] = json.dumps(body)
    return Response(None, info)


def module_args(public_ip):
    return {
        "api_token": "notrealtoken",
        "project": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
        "region": "par1",
        "name": SERVER_NAME,
        "image": IMAGE_ID,
        "commercial_type": "DEV1-S",
        "public_ip": public_ip,
    }


def fake_get(ip_status):
    def get(path, params=None):
        if path == f"images/{IMAGE_ID}":
            return make_response(200, {"image": {"id": IMAGE_ID}})
        if path == f"ips/{IP_ID}":
            return make_response(ip_status, {"ip": {"id": IP_ID}} if ip_status == 200 else {"message": "not found"})
        if path == "servers":
            return make_response(200, {"servers": []})
        raise AssertionError(f"Unexpected GET {path}")

    return get


@pytest.mark.parametrize(
    "public_ip, expected_ip_data",
    [
        pytest.param("absent", {"dynamic_ip_required": False}, id="absent"),
        pytest.param("dynamic", {"dynamic_ip_required": True}, id="dynamic"),
        pytest.param(IP_ID, {"dynamic_ip_required": False, "public_ip": IP_ID}, id="flexible_ip"),
    ],
)
def test_create_server_public_ip(mocker, capfd, public_ip, expected_ip_data):
    mocker.patch.object(Scaleway, "get", side_effect=fake_get(200))
    mock_post = mocker.patch.object(
        Scaleway,
        "post",
        return_value=make_response(201, {"server": {"id": SERVER_ID, "name": SERVER_NAME, "tags": []}}),
    )

    with set_module_args(module_args(public_ip)):
        with pytest.raises(SystemExit):
            scaleway_compute.main()

    out, err = capfd.readouterr()
    result = json.loads(out)
    assert not result.get("failed"), result
    assert result["changed"]

    mock_post.assert_called_once()
    data = mock_post.call_args.kwargs["data"]
    ip_data = {key: data[key] for key in ("dynamic_ip_required", "public_ip") if key in data}
    assert ip_data == expected_ip_data


def test_create_server_unknown_public_ip(mocker, capfd):
    mocker.patch.object(Scaleway, "get", side_effect=fake_get(404))
    mock_post = mocker.patch.object(Scaleway, "post")

    with set_module_args(module_args(IP_ID)):
        with pytest.raises(SystemExit):
            scaleway_compute.main()

    out, err = capfd.readouterr()
    result = json.loads(out)
    assert result["failed"]
    assert result["msg"] == f"Public IP {IP_ID} not found"
    mock_post.assert_not_called()

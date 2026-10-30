# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils._scaleway import Response, Scaleway
from ansible_collections.community.general.plugins.modules import scaleway_ip

IP_ID = "dd9e8df6-6775-4863-b517-e0b0ee3d7477"
ORGANIZATION = "951df375-e094-4d26-97c1-ba548eeb9c42"
REVERSE = "ip.example.com"
INVALID_REVERSE_DETAILS = [
    {"argument_name": "reverse", "reason": "constraint", "help_message": "reverse does not resolve to the IP"}
]


def make_response(status, body):
    return Response(None, {"status": status, "msg": "HTTP Error", "body": json.dumps(body)})


def make_ip(reverse=None):
    return {"id": IP_ID, "address": "212.47.232.136", "organization": ORGANIZATION, "reverse": reverse, "server": None}


def invalid_reverse_response():
    return make_response(
        400, {"type": "invalid_arguments", "message": "invalid argument(s)", "details": INVALID_REVERSE_DETAILS}
    )


@pytest.fixture
def scw_api(mocker):
    return {
        "get": mocker.patch.object(Scaleway, "get"),
        "post": mocker.patch.object(Scaleway, "post"),
        "patch": mocker.patch.object(Scaleway, "patch"),
    }


def run_module(capfd, args, check_mode=False):
    module_args = {"api_token": "notrealtoken", "region": "par1", "organization": ORGANIZATION}
    module_args.update(args)
    if check_mode:
        module_args["_ansible_check_mode"] = True
    with set_module_args(module_args):
        with pytest.raises(SystemExit):
            scaleway_ip.main()
    out, dummy = capfd.readouterr()
    return json.loads(out)


def test_create_ip(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": []})
    scw_api["post"].return_value = make_response(201, {"ip": make_ip()})

    result = run_module(capfd, {"state": "present"})

    assert result["changed"]
    assert result["scaleway_ip"]["id"] == IP_ID
    scw_api["post"].assert_called_once_with("/ips", data={"organization": ORGANIZATION})
    scw_api["patch"].assert_not_called()


def test_create_ip_with_reverse(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": []})
    scw_api["post"].return_value = make_response(201, {"ip": make_ip()})
    scw_api["patch"].return_value = make_response(200, {"ip": make_ip(reverse=REVERSE)})

    result = run_module(capfd, {"state": "present", "reverse": REVERSE})

    assert result["changed"]
    assert result["scaleway_ip"]["reverse"] == REVERSE
    scw_api["post"].assert_called_once_with("/ips", data={"organization": ORGANIZATION})
    scw_api["patch"].assert_called_once_with(path=f"ips/{IP_ID}", data={"reverse": REVERSE})


def test_create_ip_with_reverse_check_mode(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": []})

    result = run_module(capfd, {"state": "present", "reverse": REVERSE}, check_mode=True)

    assert result["changed"]
    scw_api["post"].assert_not_called()
    scw_api["patch"].assert_not_called()


def test_create_ip_with_reverse_update_fails(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": []})
    scw_api["post"].return_value = make_response(201, {"ip": make_ip()})
    scw_api["patch"].return_value = invalid_reverse_response()

    result = run_module(capfd, {"state": "present", "reverse": REVERSE})

    assert result["failed"]
    assert f"IP {IP_ID} created" in result["msg"]
    assert "[400: invalid argument(s)]" in result["msg"]
    assert "reverse does not resolve to the IP" in result["msg"]


def test_update_reverse(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": [make_ip()]})
    scw_api["patch"].return_value = make_response(200, {"ip": make_ip(reverse=REVERSE)})

    result = run_module(capfd, {"state": "present", "id": IP_ID, "reverse": REVERSE})

    assert result["changed"]
    assert result["scaleway_ip"]["reverse"] == REVERSE
    scw_api["post"].assert_not_called()
    scw_api["patch"].assert_called_once_with(path=f"ips/{IP_ID}", data={"reverse": REVERSE})


def test_update_reverse_unchanged(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": [make_ip(reverse=REVERSE)]})

    result = run_module(capfd, {"state": "present", "id": IP_ID, "reverse": REVERSE})

    assert not result["changed"]
    scw_api["post"].assert_not_called()
    scw_api["patch"].assert_not_called()


def test_update_reverse_fails(capfd, scw_api):
    scw_api["get"].return_value = make_response(200, {"ips": [make_ip()]})
    scw_api["patch"].return_value = invalid_reverse_response()

    result = run_module(capfd, {"state": "present", "id": IP_ID, "reverse": REVERSE})

    assert result["failed"]
    assert result["msg"].startswith("Error during IP attributes update: [400: invalid argument(s)]")
    assert "reverse does not resolve to the IP" in result["msg"]

# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils._scaleway import Response, Scaleway
from ansible_collections.community.general.plugins.modules import scaleway_organization_info

ORGANIZATION_1 = "951df375-e094-4d26-97c1-ba548eeb9c42"
ORGANIZATION_2 = "3f709602-5e6c-4619-b80c-e8432fe0e0e0"


def make_response(status, body):
    return Response(None, {"status": status, "msg": "HTTP Error", "body": json.dumps(body)})


def make_project(project_id, organization_id):
    return {"id": project_id, "name": f"project-{project_id}", "organization_id": organization_id}


@pytest.fixture
def scw_get(mocker):
    return mocker.patch.object(Scaleway, "get")


def run_module(capfd):
    with set_module_args({"api_token": "notrealtoken"}):
        with pytest.raises(SystemExit):
            scaleway_organization_info.main()
    out, dummy = capfd.readouterr()
    return json.loads(out)


def test_organizations_from_projects(capfd, scw_get):
    scw_get.side_effect = [
        make_response(
            200,
            {
                "total_count": 3,
                "projects": [
                    make_project("p1", ORGANIZATION_1),
                    make_project("p2", ORGANIZATION_2),
                ],
            },
        ),
        make_response(200, {"total_count": 3, "projects": [make_project("p3", ORGANIZATION_1)]}),
        make_response(200, {"total_count": 3, "projects": []}),
    ]

    result = run_module(capfd)

    assert not result.get("failed")
    assert result["scaleway_organization_info"] == [{"id": ORGANIZATION_1}, {"id": ORGANIZATION_2}]
    assert scw_get.call_count == 3
    assert all(call.kwargs["path"] == "account/v3/projects" for call in scw_get.call_args_list)


def test_no_projects(capfd, scw_get):
    scw_get.return_value = make_response(200, {"total_count": 0, "projects": []})

    result = run_module(capfd)

    assert not result.get("failed")
    assert result["scaleway_organization_info"] == []
    assert scw_get.call_count == 1


def test_api_error(capfd, scw_get):
    scw_get.return_value = make_response(401, {"message": "authentication is denied", "type": "denied_authentication"})

    result = run_module(capfd)

    assert result["failed"] is True
    assert "authentication is denied" in result["msg"]
    assert "401" in result["msg"]

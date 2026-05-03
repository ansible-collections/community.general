# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import re
import unittest

import pytest
from httmock import response, urlmatch, with_httmock

from ansible_collections.community.general.plugins.modules import github_team

pytest.importorskip("github")


BASE_PARAMS = {
    "username": None,
    "password": None,
    "access_token": "mytoken",
    "api_url": "https://api.github.com",
    "organization": "MyOrganization",
    "name": "my-team",
    "description": None,
    "privacy": None,
    "permission": None,
    "parent_team": None,
    "notification_setting": None,
    "new_name": None,
    "state": "present",
}


def make_params(**overrides):
    params = dict(BASE_PARAMS)
    params.update(overrides)
    return params


TEAM_DATA = {
    "id": 1,
    "name": "my-team",
    "slug": "my-team",
    "description": "A great team",
    "privacy": "closed",
    "permission": "push",
    "notification_setting": "notifications_enabled",
    "url": "https://api.github.com/orgs/MyOrganization/teams/my-team",
    "html_url": "https://github.com/orgs/MyOrganization/teams/my-team",
    "members_url": "https://api.github.com/orgs/MyOrganization/teams/my-team/members{/member}",
    "repositories_url": "https://api.github.com/orgs/MyOrganization/teams/my-team/repos",
    "parent": None,
    "organization": {"login": "MyOrganization", "id": 1},
}


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+$", method="get")
def get_org_mock(url, request):
    match = re.search(r"/orgs/(?P<org>[^/]+)$", request.url)
    org = match.group("org")
    headers = {"content-type": "application/json"}
    content = json.dumps({"login": org, "id": 1, "url": f"https://api.github.com/orgs/{org}"}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+$", method="get")
def get_team_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(TEAM_DATA).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+$", method="get")
def get_team_notfound_mock(url, request):
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams$", method="post")
def create_team_mock(url, request):
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = dict(TEAM_DATA)
    content["name"] = body["name"]
    content["slug"] = body["name"].lower().replace(" ", "-")
    if "description" in body:
        content["description"] = body["description"]
    if "privacy" in body:
        content["privacy"] = body["privacy"]
    if "permission" in body:
        content["permission"] = body["permission"]
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+$", method="patch")
def patch_team_mock(url, request):
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = dict(TEAM_DATA)
    content.update(body)
    if "name" in body:
        content["slug"] = body["name"].lower().replace(" ", "-")
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+$", method="delete")
def delete_team_mock(url, request):
    return response(204, None, None, None, 5, request)


class TestGithubTeam(unittest.TestCase):
    @with_httmock(get_org_mock)
    @with_httmock(get_team_notfound_mock)
    @with_httmock(create_team_mock)
    def test_create_team(self):
        result = github_team.run_module(make_params(description="A great team", privacy="closed", permission="push"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["team"]["name"], "my-team")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_notfound_mock)
    @with_httmock(create_team_mock)
    def test_create_team_minimal(self):
        result = github_team.run_module(make_params())
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["team"]["name"], "my-team")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    def test_idempotency_team_exists(self):
        result = github_team.run_module(make_params(description="A great team", privacy="closed", permission="push"))
        self.assertEqual(result["changed"], False)
        self.assertEqual(result["team"]["name"], "my-team")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(patch_team_mock)
    def test_update_description(self):
        result = github_team.run_module(make_params(description="An updated team"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["team"]["description"], "An updated team")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(patch_team_mock)
    def test_update_privacy(self):
        result = github_team.run_module(make_params(privacy="secret"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["team"]["privacy"], "secret")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(patch_team_mock)
    def test_rename_team(self):
        result = github_team.run_module(make_params(new_name="renamed-team"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["team"]["name"], "renamed-team")

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(delete_team_mock)
    def test_delete_team(self):
        result = github_team.run_module(make_params(state="absent"))
        self.assertEqual(result["changed"], True)
        self.assertNotIn("team", result)

    @with_httmock(get_org_mock)
    @with_httmock(get_team_notfound_mock)
    def test_delete_team_not_found(self):
        result = github_team.run_module(make_params(state="absent"))
        self.assertEqual(result["changed"], False)

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    def test_idempotency_no_params(self):
        result = github_team.run_module(make_params())
        self.assertEqual(result["changed"], False)

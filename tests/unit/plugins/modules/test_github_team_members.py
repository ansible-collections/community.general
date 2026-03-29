# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import re
import unittest

import pytest
from httmock import response, urlmatch, with_httmock

from ansible_collections.community.general.plugins.modules import github_team_members

pytest.importorskip("github")


BASE_PARAMS = {
    "username": None,
    "password": None,
    "access_token": "mytoken",
    "api_url": "https://api.github.com",
    "organization": "MyOrganization",
    "team": "my-team",
    "members": [],
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
    "url": "https://api.github.com/orgs/MyOrganization/teams/my-team",
    "organization": {"login": "MyOrganization", "id": 1},
    "members_url": "https://api.github.com/orgs/MyOrganization/teams/my-team/members{/member}",
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


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+/members$", method="get")
def get_members_empty_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps([]).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+/members$", method="get")
def get_members_mock(url, request):
    # Check if role=maintainer is in the query
    if "role=maintainer" in request.url:
        headers = {"content-type": "application/json"}
        content = json.dumps([{"login": "carol", "id": 3}]).encode("utf-8")
        return response(200, content, headers, None, 5, request)
    else:
        headers = {"content-type": "application/json"}
        content = json.dumps([{"login": "alice", "id": 1}, {"login": "bob", "id": 2}]).encode("utf-8")
        return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/users/[^/]+$", method="get")
def get_user_mock(url, request):
    match = re.search(r"/users/(?P<user>[^/]+)$", request.url)
    username = match.group("user")
    headers = {"content-type": "application/json"}
    content = json.dumps({"login": username, "id": hash(username) % 1000}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+/memberships/[^/]+$", method="put")
def add_membership_mock(url, request):
    match = re.search(r"/memberships/(?P<user>[^/]+)$", request.url)
    username = match.group("user")
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "url": f"https://api.github.com/orgs/MyOrganization/teams/my-team/memberships/{username}",
            "role": body.get("role", "member"),
            "state": "active",
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/[^/]+/teams/[^/]+/memberships/[^/]+$", method="delete")
def remove_membership_mock(url, request):
    return response(204, None, None, None, 5, request)


class TestGithubTeamMembers(unittest.TestCase):
    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_empty_mock)
    @with_httmock(get_user_mock)
    @with_httmock(add_membership_mock)
    def test_add_members_present(self):
        result = github_team_members.run_module(make_params(members=["alice", "bob"], state="present"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(sorted(result["added"]), ["alice", "bob"])
        self.assertEqual(result["removed"], [])

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_mock)
    def test_idempotency_members_present(self):
        result = github_team_members.run_module(make_params(members=["alice", "bob"], state="present"))
        self.assertEqual(result["changed"], False)
        self.assertEqual(result["added"], [])

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_mock)
    @with_httmock(get_user_mock)
    @with_httmock(add_membership_mock)
    def test_update_role(self):
        result = github_team_members.run_module(
            make_params(members=[{"username": "alice", "role": "maintainer"}], state="present")
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["updated"], ["alice"])

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_mock)
    @with_httmock(get_user_mock)
    @with_httmock(remove_membership_mock)
    def test_remove_members_absent(self):
        result = github_team_members.run_module(make_params(members=["alice"], state="absent"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["removed"], ["alice"])

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_empty_mock)
    def test_idempotency_absent_not_member(self):
        result = github_team_members.run_module(make_params(members=["alice"], state="absent"))
        self.assertEqual(result["changed"], False)

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_mock)
    @with_httmock(get_user_mock)
    @with_httmock(add_membership_mock)
    @with_httmock(remove_membership_mock)
    def test_exact_mode(self):
        result = github_team_members.run_module(
            make_params(
                members=[{"username": "alice", "role": "maintainer"}, "dave"],
                state="exact",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertIn("dave", result["added"])
        self.assertIn("alice", result["updated"])
        # bob and carol should be removed (not in desired list)
        self.assertIn("bob", result["removed"])
        self.assertIn("carol", result["removed"])

    @with_httmock(get_org_mock)
    @with_httmock(get_team_mock)
    @with_httmock(get_members_mock)
    def test_exact_mode_idempotent(self):
        result = github_team_members.run_module(
            make_params(
                members=[
                    "alice",
                    "bob",
                    {"username": "carol", "role": "maintainer"},
                ],
                state="exact",
            )
        )
        self.assertEqual(result["changed"], False)

    def test_normalize_bare_string(self):
        result = github_team_members.normalize_member("alice")
        self.assertEqual(result, {"username": "alice", "role": "member"})

    def test_normalize_dict(self):
        result = github_team_members.normalize_member({"username": "carol", "role": "maintainer"})
        self.assertEqual(result, {"username": "carol", "role": "maintainer"})

    def test_normalize_dict_default_role(self):
        result = github_team_members.normalize_member({"username": "dave"})
        self.assertEqual(result, {"username": "dave", "role": "member"})

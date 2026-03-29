# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import re
import unittest

import pytest
from httmock import response, urlmatch, with_httmock

from ansible_collections.community.general.plugins.modules import github_label

pytest.importorskip("github")


BASE_PARAMS = {
    "username": None,
    "password": None,
    "access_token": "mytoken",
    "api_url": "https://api.github.com",
    "organization": "MyOrganization",
    "repo": "myrepo",
    "name": "bug",
    "color": "d73a4a",
    "description": "",
    "new_name": None,
    "state": "present",
}


def make_params(**overrides):
    params = dict(BASE_PARAMS)
    params.update(overrides)
    return params


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+$", method="get")
def get_repo_mock(url, request):
    match = re.search(r"/repos/(?P<owner>[^/]+)/(?P<repo>[^/]+)$", request.url)
    owner = match.group("owner")
    repo = match.group("repo")
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "full_name": f"{owner}/{repo}",
            "url": f"https://api.github.com/repos/{owner}/{repo}",
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/labels/[^/]+$", method="get")
def get_label_mock(url, request):
    match = re.search(r"/repos/[^/]+/[^/]+/labels/(?P<name>[^/]+)$", request.url)
    name = match.group("name")
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "name": name,
            "color": "d73a4a",
            "description": "Something isn't working",
            "url": f"https://api.github.com/repos/MyOrganization/myrepo/labels/{name}",
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/labels/[^/]+$", method="get")
def get_label_notfound_mock(url, request):
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/labels$", method="post")
def create_label_mock(url, request):
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "name": body["name"],
            "color": body["color"],
            "description": body.get("description", ""),
            "url": f"https://api.github.com/repos/MyOrganization/myrepo/labels/{body['name']}",
        }
    ).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/labels/[^/]+$", method="patch")
def patch_label_mock(url, request):
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    name = body.get("new_name", body.get("name", "bug"))
    content = json.dumps(
        {
            "name": name,
            "color": body.get("color", "d73a4a"),
            "description": body.get("description", ""),
            "url": f"https://api.github.com/repos/MyOrganization/myrepo/labels/{name}",
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/labels/[^/]+$", method="delete")
def delete_label_mock(url, request):
    return response(204, None, None, None, 5, request)


class TestGithubLabel(unittest.TestCase):
    @with_httmock(get_repo_mock)
    @with_httmock(get_label_notfound_mock)
    @with_httmock(create_label_mock)
    def test_create_label(self):
        result = github_label.run_module(make_params(description="Something isn't working"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["label"]["name"], "bug")
        self.assertEqual(result["label"]["color"], "d73a4a")
        self.assertEqual(result["label"]["description"], "Something isn't working")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_notfound_mock)
    @with_httmock(create_label_mock)
    def test_create_label_no_description(self):
        result = github_label.run_module(make_params())
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["label"]["name"], "bug")
        self.assertEqual(result["label"]["description"], "")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_mock)
    def test_idempotency_label_exists(self):
        result = github_label.run_module(make_params(description="Something isn't working"))
        self.assertEqual(result["changed"], False)
        self.assertEqual(result["label"]["name"], "bug")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_mock)
    @with_httmock(patch_label_mock)
    def test_update_label_color(self):
        result = github_label.run_module(make_params(color="ff0000", description="Something isn't working"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["label"]["color"], "ff0000")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_mock)
    @with_httmock(patch_label_mock)
    def test_update_label_description(self):
        result = github_label.run_module(make_params(description="New description"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["label"]["description"], "New description")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_mock)
    @with_httmock(patch_label_mock)
    def test_rename_label(self):
        result = github_label.run_module(make_params(new_name="defect", description="Something isn't working"))
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["label"]["name"], "defect")

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_mock)
    @with_httmock(delete_label_mock)
    def test_delete_label(self):
        result = github_label.run_module(make_params(state="absent"))
        self.assertEqual(result["changed"], True)
        self.assertNotIn("label", result)

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_notfound_mock)
    def test_delete_label_not_found(self):
        result = github_label.run_module(make_params(state="absent"))
        self.assertEqual(result["changed"], False)

    @with_httmock(get_repo_mock)
    @with_httmock(get_label_notfound_mock)
    def test_create_label_no_color_fails(self):
        with self.assertRaises(ValueError):
            github_label.run_module(make_params(color=None))

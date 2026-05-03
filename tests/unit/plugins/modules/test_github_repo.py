# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import re
import unittest

import pytest
from httmock import response, urlmatch, with_httmock

from ansible_collections.community.general.plugins.modules import github_repo

pytest.importorskip("github")


BASE_PARAMS = {
    "username": None,
    "password": None,
    "access_token": "mytoken",
    "api_url": "https://api.github.com",
    "force_defaults": False,
    "has_issues": None,
    "has_wiki": None,
    "has_projects": None,
    "has_discussions": None,
    "allow_squash_merge": None,
    "allow_merge_commit": None,
    "allow_rebase_merge": None,
    "delete_branch_on_merge": None,
    "allow_auto_merge": None,
    "squash_merge_commit_title": None,
    "squash_merge_commit_message": None,
    "merge_commit_title": None,
    "merge_commit_message": None,
    "homepage": None,
    "topics": None,
}


FULL_REPO_DATA = {
    "name": "myrepo",
    "full_name": "MyOrganization/myrepo",
    "url": "https://api.github.com/repos/MyOrganization/myrepo",
    "private": False,
    "description": "This your first repo!",
    "default_branch": "master",
    "allow_rebase_merge": True,
    "allow_squash_merge": True,
    "allow_merge_commit": True,
    "allow_auto_merge": False,
    "delete_branch_on_merge": False,
    "has_issues": True,
    "has_wiki": True,
    "has_projects": True,
    "has_discussions": False,
    "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
    "squash_merge_commit_message": "COMMIT_MESSAGES",
    "merge_commit_title": "MERGE_MESSAGE",
    "merge_commit_message": "PR_TITLE",
    "homepage": "",
    "topics": ["existing-topic"],
}


def make_params(**overrides):
    params = dict(BASE_PARAMS)
    params.update(overrides)
    return params


@urlmatch(netloc=r".*")
def debug_mock(url, request):
    print(request.original.__dict__)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/.*", method="get")
def get_orgs_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/orgs/(?P<org>[^/]+)", request.url)
    org = match.group("org")

    # https://docs.github.com/en/rest/reference/orgs#get-an-organization
    headers = {"content-type": "application/json"}
    content = {"login": org, "url": f"https://api.github.com/orgs/{org}"}
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/user", method="get")
def get_user_mock(url, request):
    # https://docs.github.com/en/rest/reference/users#get-the-authenticated-user
    headers = {"content-type": "application/json"}
    content = {"login": "octocat", "url": "https://api.github.com/users/octocat"}
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/.*/.*", method="get")
def get_repo_notfound_mock(url, request):
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+$", method="get")
def get_repo_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    headers = {"content-type": "application/json"}
    content = dict(FULL_REPO_DATA)
    content["full_name"] = f"{org}/{repo}"
    content["url"] = f"https://api.github.com/repos/{org}/{repo}"
    content["name"] = repo
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+$", method="get")
def get_private_repo_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    headers = {"content-type": "application/json"}
    content = dict(FULL_REPO_DATA)
    content["full_name"] = f"{org}/{repo}"
    content["url"] = f"https://api.github.com/repos/{org}/{repo}"
    content["name"] = repo
    content["private"] = True
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/orgs/.*/repos", method="post")
def create_new_org_repo_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/orgs/(?P<org>[^/]+)/repos", request.url)
    org = match.group("org")
    repo = json.loads(request.body)

    headers = {"content-type": "application/json"}
    # https://docs.github.com/en/rest/reference/repos#create-an-organization-repository
    content = {
        "name": repo["name"],
        "full_name": f"{org}/{repo['name']}",
        "private": repo.get("private", False),
        "description": repo.get("description"),
    }
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/user/repos", method="post")
def create_new_user_repo_mock(url, request):
    repo = json.loads(request.body)

    headers = {"content-type": "application/json"}
    # https://docs.github.com/en/rest/reference/repos#create-a-repository-for-the-authenticated-user
    content = {
        "name": repo["name"],
        "full_name": f"octocat/{repo['name']}",
        "private": repo.get("private", False),
        "description": repo.get("description"),
    }
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+$", method="patch")
def patch_repo_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = dict(FULL_REPO_DATA)
    content["name"] = repo
    content["full_name"] = f"{org}/{repo}"
    content["url"] = f"https://api.github.com/repos/{org}/{repo}"
    content.update(body)
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/.*/.*", method="delete")
def delete_repo_mock(url, request):
    # https://docs.github.com/en/rest/reference/repos#delete-a-repository
    return response(204, None, None, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/.*/.*", method="delete")
def delete_repo_notfound_mock(url, request):
    # https://docs.github.com/en/rest/reference/repos#delete-a-repository
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/topics$", method="get")
def get_topics_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps({"names": ["existing-topic"]}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/topics$", method="put")
def put_topics_mock(url, request):
    body = json.loads(request.body)
    headers = {"content-type": "application/json"}
    content = json.dumps({"names": body["names"]}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


class TestGithubRepo(unittest.TestCase):
    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_org_repo_mock)
    def test_create_new_org_repo(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description="Just for fun",
                private=False,
                state="present",
            )
        )

        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["private"], False)
        self.assertEqual(result["repo"]["description"], "Just for fun")

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_org_repo_mock)
    def test_create_new_org_repo_incomplete(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
            )
        )

        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["private"], False)
        self.assertEqual(result["repo"]["description"], None)

    @with_httmock(get_user_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_user_repo_mock)
    def test_create_new_user_repo(self):
        result = github_repo.run_module(
            make_params(
                organization=None,
                name="myrepo",
                description="Just for fun",
                private=True,
                state="present",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["private"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_patch_existing_org_repo(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description="Just for fun",
                private=True,
                state="present",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["private"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_private_repo_mock)
    def test_idempotency_existing_org_private_repo(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
            )
        )
        self.assertEqual(result["changed"], False)
        self.assertEqual(result["repo"]["private"], True)
        self.assertEqual(result["repo"]["description"], "This your first repo!")

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(delete_repo_mock)
    def test_delete_org_repo(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description="Just for fun",
                private=False,
                state="absent",
            )
        )
        self.assertEqual(result["changed"], True)

    @with_httmock(get_user_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(delete_repo_mock)
    def test_delete_user_repo(self):
        result = github_repo.run_module(
            make_params(
                organization=None,
                name="myrepo",
                description="Just for fun",
                private=False,
                state="absent",
            )
        )
        self.assertEqual(result["changed"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(delete_repo_notfound_mock)
    def test_delete_org_repo_notfound(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description="Just for fun",
                private=True,
                state="absent",
            )
        )
        self.assertEqual(result["changed"], False)

    # --- Tests for new settings parameters ---

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_wiki_setting(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                has_wiki=False,
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["has_wiki"], False)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    def test_idempotency_wiki_already_enabled(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                has_wiki=True,
            )
        )
        self.assertEqual(result["changed"], False)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_merge_settings(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                allow_squash_merge=False,
                allow_merge_commit=False,
                allow_rebase_merge=False,
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["allow_squash_merge"], False)
        self.assertEqual(result["repo"]["allow_merge_commit"], False)
        self.assertEqual(result["repo"]["allow_rebase_merge"], False)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_delete_branch_on_merge(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                delete_branch_on_merge=True,
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["delete_branch_on_merge"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_auto_merge(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                allow_auto_merge=True,
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["allow_auto_merge"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_squash_merge_commit_options(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                squash_merge_commit_title="PR_TITLE",
                squash_merge_commit_message="PR_BODY",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["squash_merge_commit_title"], "PR_TITLE")
        self.assertEqual(result["repo"]["squash_merge_commit_message"], "PR_BODY")

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_merge_commit_options(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                merge_commit_title="PR_TITLE",
                merge_commit_message="PR_BODY",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["merge_commit_title"], "PR_TITLE")
        self.assertEqual(result["repo"]["merge_commit_message"], "PR_BODY")

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_discussions(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                has_discussions=True,
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["has_discussions"], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_homepage(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                homepage="https://example.com",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["homepage"], "https://example.com")

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(get_topics_mock)
    @with_httmock(put_topics_mock)
    def test_update_topics(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                topics=["ansible", "automation"],
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertIn("ansible", result["repo"]["topics"])
        self.assertIn("automation", result["repo"]["topics"])

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(get_topics_mock)
    def test_idempotency_topics_unchanged(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                topics=["existing-topic"],
            )
        )
        self.assertEqual(result["changed"], False)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    def test_idempotency_all_settings_match(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                has_issues=True,
                has_wiki=True,
                has_projects=True,
                has_discussions=False,
                allow_squash_merge=True,
                allow_merge_commit=True,
                allow_rebase_merge=True,
                allow_auto_merge=False,
                delete_branch_on_merge=False,
            )
        )
        self.assertEqual(result["changed"], False)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_update_multiple_settings(self):
        result = github_repo.run_module(
            make_params(
                organization="MyOrganization",
                name="myrepo",
                description=None,
                private=None,
                state="present",
                has_wiki=False,
                has_issues=False,
                allow_squash_merge=False,
                delete_branch_on_merge=True,
                homepage="https://example.com",
            )
        )
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["repo"]["has_wiki"], False)
        self.assertEqual(result["repo"]["has_issues"], False)
        self.assertEqual(result["repo"]["allow_squash_merge"], False)
        self.assertEqual(result["repo"]["delete_branch_on_merge"], True)
        self.assertEqual(result["repo"]["homepage"], "https://example.com")

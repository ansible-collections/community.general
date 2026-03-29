# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest

import pytest
from httmock import response, urlmatch, with_httmock

from ansible_collections.community.general.plugins.modules import github_branch_protection

pytest.importorskip("github")


BASE_PARAMS = {
    "username": None,
    "password": None,
    "access_token": "mytoken",
    "api_url": "https://api.github.com",
    "organization": "MyOrganization",
    "repo": "myrepo",
    "branch": "main",
    "state": "present",
    "required_status_checks": None,
    "enforce_admins": False,
    "required_pull_request_reviews": None,
    "restrictions": None,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_linear_history": False,
    "required_conversation_resolution": False,
    "lock_branch": False,
    "allow_fork_syncing": False,
    "block_creations": False,
    "required_signatures": False,
}


def make_params(**overrides):
    params = dict(BASE_PARAMS)
    params.update(overrides)
    return params


REPO_DATA = {
    "full_name": "MyOrganization/myrepo",
    "url": "https://api.github.com/repos/MyOrganization/myrepo",
}


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+$", method="get")
def get_repo_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(REPO_DATA).encode("utf-8")
    return response(200, content, headers, None, 5, request)


BRANCH_UNPROTECTED = {
    "name": "main",
    "protected": False,
    "protection_url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection",
    "commit": {"sha": "abc123"},
}


BRANCH_PROTECTED = {
    "name": "main",
    "protected": True,
    "protection_url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection",
    "commit": {"sha": "abc123"},
    "protection": {
        "enabled": True,
        "required_status_checks": {
            "strict": True,
            "contexts": ["ci/build"],
            "url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection/required_status_checks",
        },
        "enforce_admins": {
            "enabled": True,
            "url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection/enforce_admins",
        },
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 2,
            "dismissal_restrictions": {"users": [], "teams": []},
            "require_last_push_approval": False,
            "url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection/required_pull_request_reviews",
        },
        "restrictions": None,
        "required_linear_history": {"enabled": False},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
        "required_conversation_resolution": {"enabled": False},
        "lock_branch": {"enabled": False},
        "allow_fork_syncing": {"enabled": False},
        "block_creations": {"enabled": False},
        "required_signatures": {
            "enabled": False,
            "url": "https://api.github.com/repos/MyOrganization/myrepo/branches/main/protection/required_signatures",
        },
    },
}


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/branches/[^/]+$", method="get")
def get_branch_unprotected_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(BRANCH_UNPROTECTED).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r"/repos/[^/]+/[^/]+/branches/[^/]+$", method="get")
def get_branch_protected_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(BRANCH_PROTECTED).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/protection$", method="get")
def get_protection_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(BRANCH_PROTECTED["protection"]).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/protection$", method="get")
def get_protection_notfound_mock(url, request):
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/protection$", method="put")
def put_protection_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(BRANCH_PROTECTED["protection"]).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/protection$", method="delete")
def delete_protection_mock(url, request):
    return response(204, None, None, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/protection/enforce_admins$", method="get")
def get_enforce_admins_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps({"enabled": True, "url": request.url}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/required_status_checks$", method="get")
def get_required_status_checks_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "strict": True,
            "contexts": ["ci/build"],
            "url": request.url,
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/required_pull_request_reviews$", method="get")
def get_required_pr_reviews_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps(
        {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 2,
            "dismissal_restrictions": {"users": [], "teams": []},
            "require_last_push_approval": False,
            "url": request.url,
        }
    ).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/required_signatures$", method="get")
def get_required_signatures_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps({"enabled": False, "url": request.url}).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/restrictions$")
def get_restrictions_notfound_mock(url, request):
    return response(404, '{"message": "Not Found"}', "", "Not Found", 5, request)


@urlmatch(netloc=r"api\.github\.com(:[0-9]+)?$", path=r".*/restrictions/(users|teams)$", method="get")
def get_restrictions_empty_mock(url, request):
    headers = {"content-type": "application/json"}
    content = json.dumps([]).encode("utf-8")
    return response(200, content, headers, None, 5, request)


class TestGithubBranchProtection(unittest.TestCase):
    def test_build_desired_state_defaults(self):
        desired = github_branch_protection.build_desired_state(BASE_PARAMS)
        self.assertEqual(desired["enforce_admins"], False)
        self.assertIsNone(desired["required_status_checks"])
        self.assertIsNone(desired["required_pull_request_reviews"])
        self.assertIsNone(desired["restrictions"])
        self.assertEqual(desired["allow_force_pushes"], False)

    def test_build_desired_state_with_status_checks(self):
        params = make_params(
            required_status_checks={"strict": True, "contexts": ["ci/build", "ci/test"]},
        )
        desired = github_branch_protection.build_desired_state(params)
        self.assertEqual(desired["required_status_checks"]["strict"], True)
        self.assertEqual(desired["required_status_checks"]["contexts"], ["ci/build", "ci/test"])

    def test_build_desired_state_with_pr_reviews(self):
        params = make_params(
            required_pull_request_reviews={
                "dismiss_stale_reviews": True,
                "required_approving_review_count": 3,
            },
        )
        desired = github_branch_protection.build_desired_state(params)
        self.assertEqual(desired["required_pull_request_reviews"]["dismiss_stale_reviews"], True)
        self.assertEqual(desired["required_pull_request_reviews"]["required_approving_review_count"], 3)
        self.assertEqual(desired["required_pull_request_reviews"]["require_code_owner_reviews"], False)

    @with_httmock(get_repo_mock)
    @with_httmock(get_branch_protected_mock)
    @with_httmock(delete_protection_mock)
    def test_remove_protection(self):
        result = github_branch_protection.run_module(
            make_params(state="absent"),
            check_mode=False,
        )
        self.assertEqual(result["changed"], True)

    @with_httmock(get_repo_mock)
    @with_httmock(get_branch_unprotected_mock)
    def test_remove_protection_already_unprotected(self):
        result = github_branch_protection.run_module(
            make_params(state="absent"),
            check_mode=False,
        )
        self.assertEqual(result["changed"], False)

    @with_httmock(get_repo_mock)
    @with_httmock(get_branch_unprotected_mock)
    def test_set_protection_on_unprotected_branch_check_mode(self):
        result = github_branch_protection.run_module(
            make_params(enforce_admins=True),
            check_mode=True,
        )
        self.assertEqual(result["changed"], True)
        self.assertIn("protection", result)
        self.assertEqual(result["protection"]["enforce_admins"], True)

    @with_httmock(get_repo_mock)
    @with_httmock(get_branch_unprotected_mock)
    def test_check_mode_with_status_checks(self):
        result = github_branch_protection.run_module(
            make_params(
                enforce_admins=True,
                required_status_checks={"strict": True, "contexts": ["ci/build"]},
            ),
            check_mode=True,
        )
        self.assertEqual(result["changed"], True)
        self.assertIn("protection", result)
        self.assertEqual(result["protection"]["required_status_checks"]["strict"], True)
        self.assertIn("ci/build", result["protection"]["required_status_checks"]["contexts"])

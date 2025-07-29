# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import json
import sys
import pytest
from httmock import with_httmock, urlmatch, response
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import github_repo

GITHUB_MINIMUM_PYTHON_VERSION = (2, 7)


pytest.importorskip('github')


@urlmatch(netloc=r'.*')
def debug_mock(url, request):
    print(request.original.__dict__)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/orgs/.*', method="get")
def get_orgs_mock(url, request):
    match = re.search(r"api\.github\.com(:[0-9]+)?/orgs/(?P<org>[^/]+)", request.url)
    org = match.group("org")

    # https://docs.github.com/en/rest/reference/orgs#get-an-organization
    headers = {'content-type': 'application/json'}
    content = {
        "login": org,
        "url": "https://api.github.com/orgs/{0}".format(org)
    }
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user', method="get")
def get_user_mock(url, request):
    # https://docs.github.com/en/rest/reference/users#get-the-authenticated-user
    headers = {'content-type': 'application/json'}
    content = {
        "login": "octocat",
        "url": "https://api.github.com/users/octocat"
    }
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="get")
def get_repo_notfound_mock(url, request):
    return response(404, "{\"message\": \"Not Found\"}", "", "Not Found", 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="get")
def get_repo_mock(url, request):
    match = re.search(
        r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    # https://docs.github.com/en/rest/reference/repos#get-a-repository
    headers = {'content-type': 'application/json'}
    content = {
        "name": repo,
        "full_name": "{0}/{1}".format(org, repo),
        "url": "https://api.github.com/repos/{0}/{1}".format(org, repo),
        "private": False,
        "description": "This your first repo!",
        "default_branch": "master",
        "allow_rebase_merge": True
    }
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="get")
def get_private_repo_mock(url, request):
    match = re.search(
        r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    # https://docs.github.com/en/rest/reference/repos#get-a-repository
    headers = {'content-type': 'application/json'}
    content = {
        "name": repo,
        "full_name": "{0}/{1}".format(org, repo),
        "url": "https://api.github.com/repos/{0}/{1}".format(org, repo),
        "private": True,
        "description": "This your first repo!",
        "default_branch": "master",
        "allow_rebase_merge": True
    }
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/orgs/.*/repos', method="post")
def create_new_org_repo_mock(url, request):
    match = re.search(
        r"api\.github\.com(:[0-9]+)?/orgs/(?P<org>[^/]+)/repos", request.url)
    org = match.group("org")
    repo = json.loads(request.body)

    headers = {'content-type': 'application/json'}
    # https://docs.github.com/en/rest/reference/repos#create-an-organization-repository
    content = {
        "name": repo['name'],
        "full_name": "{0}/{1}".format(org, repo['name']),
        "private": repo.get('private', False),
        "description": repo.get('description')
    }
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/repos', method="post")
def create_new_user_repo_mock(url, request):
    repo = json.loads(request.body)

    headers = {'content-type': 'application/json'}
    # https://docs.github.com/en/rest/reference/repos#create-a-repository-for-the-authenticated-user
    content = {
        "name": repo['name'],
        "full_name": "{0}/{1}".format("octocat", repo['name']),
        "private": repo.get('private', False),
        "description": repo.get('description')
    }
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="patch")
def patch_repo_mock(url, request):
    match = re.search(
        r"api\.github\.com(:[0-9]+)?/repos/(?P<org>[^/]+)/(?P<repo>[^/]+)", request.url)
    org = match.group("org")
    repo = match.group("repo")

    body = json.loads(request.body)
    headers = {'content-type': 'application/json'}
    # https://docs.github.com/en/rest/reference/repos#update-a-repository
    content = {
        "name": repo,
        "full_name": "{0}/{1}".format(org, repo),
        "url": "https://api.github.com/repos/{0}/{1}".format(org, repo),
        "private": body.get('private', False),
        "description": body.get('description'),
        "default_branch": "master",
        "allow_rebase_merge": True
    }
    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="delete")
def delete_repo_mock(url, request):
    # https://docs.github.com/en/rest/reference/repos#delete-a-repository
    return response(204, None, None, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/repos/.*/.*', method="delete")
def delete_repo_notfound_mock(url, request):
    # https://docs.github.com/en/rest/reference/repos#delete-a-repository
    return response(404, "{\"message\": \"Not Found\"}", "", "Not Found", 5, request)


class TestGithubRepo(unittest.TestCase):
    def setUp(self):
        if sys.version_info < GITHUB_MINIMUM_PYTHON_VERSION:
            self.skipTest("Python %s+ is needed for PyGithub" %
                          ",".join(map(str, GITHUB_MINIMUM_PYTHON_VERSION)))

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_org_repo_mock)
    def test_create_new_org_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": "Just for fun",
            "private": False,
            "state": "present",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })

        self.assertEqual(result['changed'], True)
        self.assertEqual(result['repo']['private'], False)
        self.assertEqual(result['repo']['description'], 'Just for fun')

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_org_repo_mock)
    def test_create_new_org_repo_incomplete(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": None,
            "private": None,
            "state": "present",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })

        self.assertEqual(result['changed'], True)
        self.assertEqual(result['repo']['private'], False)
        self.assertEqual(result['repo']['description'], None)

    @with_httmock(get_user_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(create_new_user_repo_mock)
    def test_create_new_user_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": None,
            "name": "myrepo",
            "description": "Just for fun",
            "private": True,
            "state": "present",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['repo']['private'], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(patch_repo_mock)
    def test_patch_existing_org_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": "Just for fun",
            "private": True,
            "state": "present",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['repo']['private'], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_private_repo_mock)
    def test_idempotency_existing_org_private_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": None,
            "private": None,
            "state": "present",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['repo']['private'], True)
        self.assertEqual(result['repo']['description'], 'This your first repo!')

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(delete_repo_mock)
    def test_delete_org_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": "Just for fun",
            "private": False,
            "state": "absent",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], True)

    @with_httmock(get_user_mock)
    @with_httmock(get_repo_mock)
    @with_httmock(delete_repo_mock)
    def test_delete_user_repo(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": None,
            "name": "myrepo",
            "description": "Just for fun",
            "private": False,
            "state": "absent",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], True)

    @with_httmock(get_orgs_mock)
    @with_httmock(get_repo_notfound_mock)
    @with_httmock(delete_repo_notfound_mock)
    def test_delete_org_repo_notfound(self):
        result = github_repo.run_module({
            'username': None,
            'password': None,
            "access_token": "mytoken",
            "organization": "MyOrganization",
            "name": "myrepo",
            "description": "Just for fun",
            "private": True,
            "state": "absent",
            "api_url": "https://api.github.com",
            "force_defaults": False,
        })
        self.assertEqual(result['changed'], False)


if __name__ == "__main__":
    unittest.main()

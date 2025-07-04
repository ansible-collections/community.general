# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zoran Krleza (zoran.krleza@true-north.hr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import gitlab

from ansible_collections.community.general.plugins.modules.gitlab_project_access_token import GitLabProjectAccessToken

# python-gitlab 3.1+ is needed for python-gitlab access tokens api
PYTHON_GITLAB_MINIMAL_VERSION = (3, 1)


def python_gitlab_version_match_requirement():
    return tuple(map(int, gitlab.__version__.split('.'))) >= PYTHON_GITLAB_MINIMAL_VERSION


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         resp_get_user,
                         resp_get_project,
                         resp_list_project_access_tokens,
                         resp_create_project_access_tokens,
                         resp_revoke_project_access_tokens)

except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object
    resp_list_project_access_tokens = _dummy
    resp_create_project_access_tokens = _dummy
    resp_revoke_project_access_tokens = _dummy
    resp_get_user = _dummy
    resp_get_project = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabProjectAccessToken(GitlabModuleTestCase):
    @with_httmock(resp_get_user)
    def setUp(self):
        super(TestGitlabProjectAccessToken, self).setUp()
        if not python_gitlab_version_match_requirement():
            self.skipTest("python-gitlab %s+ is needed for gitlab_project_access_token" % ",".join(map(str, PYTHON_GITLAB_MINIMAL_VERSION)))

        self.moduleUtil = GitLabProjectAccessToken(module=self.mock_module, gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_get_project)
    @with_httmock(resp_list_project_access_tokens)
    def test_find_access_token(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.find_access_token(project, "test-token")
        self.assertEqual(rvalue, False)
        self.assertIsNotNone(self.moduleUtil.access_token_object)
        self.assertEqual(self.moduleUtil.access_token_object.id, 691)
        self.assertFalse(self.moduleUtil.access_token_object.revoked)

    @with_httmock(resp_get_project)
    @with_httmock(resp_list_project_access_tokens)
    def test_find_access_token_old_format(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.find_access_token(project, "test-token-no-revoked")
        self.assertEqual(rvalue, False)
        self.assertIsNotNone(self.moduleUtil.access_token_object)
        self.assertEqual(self.moduleUtil.access_token_object.id, 695)
        self.assertFalse(hasattr(self.moduleUtil.access_token_object, "revoked"))

    @with_httmock(resp_get_project)
    @with_httmock(resp_list_project_access_tokens)
    def test_find_revoked_access_token(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.find_access_token(project, "test-token-three")
        self.assertEqual(rvalue, False)
        self.assertIsNone(self.moduleUtil.access_token_object)

    @with_httmock(resp_get_project)
    @with_httmock(resp_list_project_access_tokens)
    def test_find_access_token_negative(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.find_access_token(project, "nonexisting")
        self.assertEqual(rvalue, False)
        self.assertIsNone(self.moduleUtil.access_token_object)

    @with_httmock(resp_get_project)
    @with_httmock(resp_create_project_access_tokens)
    def test_create_access_token(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.create_access_token(project, {'name': "tokenXYZ", 'scopes': ["api"], 'access_level': 20, 'expires_at': "2024-12-31"})
        self.assertEqual(rvalue, True)
        self.assertIsNotNone(self.moduleUtil.access_token_object)

    @with_httmock(resp_get_project)
    @with_httmock(resp_list_project_access_tokens)
    @with_httmock(resp_revoke_project_access_tokens)
    def test_revoke_access_token(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertIsNotNone(project)

        rvalue = self.moduleUtil.find_access_token(project, "test-token")
        self.assertEqual(rvalue, False)
        self.assertIsNotNone(self.moduleUtil.access_token_object)

        rvalue = self.moduleUtil.revoke_access_token()
        self.assertEqual(rvalue, True)

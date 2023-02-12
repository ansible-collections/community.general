# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from ansible_collections.community.general.plugins.modules.gitlab_protected_branch import GitlabProtectedBranch


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         python_version_match_requirement, python_gitlab_module_version,
                         python_gitlab_version_match_requirement,
                         resp_get_protected_branch, resp_get_project_by_name,
                         resp_get_protected_branch_not_exist,
                         resp_delete_protected_branch, resp_get_user)

    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import Project  # noqa: F401, pylint: disable=unused-import
    gitlab_req_version = python_gitlab_version_match_requirement()
    gitlab_module_version = python_gitlab_module_version()
    if LooseVersion(gitlab_module_version) < LooseVersion(gitlab_req_version):
        pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing (Wrong  version)"))
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabProtectedBranch(GitlabModuleTestCase):
    @with_httmock(resp_get_project_by_name)
    @with_httmock(resp_get_user)
    def setUp(self):
        super(TestGitlabProtectedBranch, self).setUp()

        self.gitlab_instance.user = self.gitlab_instance.users.get(1)
        self.moduleUtil = GitlabProtectedBranch(module=self.mock_module, project="foo-bar/diaspora-client", gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_get_protected_branch)
    def test_protected_branch_exist(self):
        rvalue = self.moduleUtil.protected_branch_exist(name="master")
        self.assertEqual(rvalue.name, "master")

    @with_httmock(resp_get_protected_branch_not_exist)
    def test_protected_branch_exist_not_exist(self):
        rvalue = self.moduleUtil.protected_branch_exist(name="master")
        self.assertEqual(rvalue, False)

    @with_httmock(resp_get_protected_branch)
    def test_compare_protected_branch(self):
        rvalue = self.moduleUtil.compare_protected_branch(name="master", merge_access_levels="maintainer", push_access_level="maintainer")
        self.assertEqual(rvalue, True)

    @with_httmock(resp_get_protected_branch)
    def test_compare_protected_branch_different_settings(self):
        rvalue = self.moduleUtil.compare_protected_branch(name="master", merge_access_levels="developer", push_access_level="maintainer")
        self.assertEqual(rvalue, False)

    @with_httmock(resp_get_protected_branch)
    @with_httmock(resp_delete_protected_branch)
    def test_delete_protected_branch(self):
        rvalue = self.moduleUtil.delete_protected_branch(name="master")
        self.assertEqual(rvalue, None)

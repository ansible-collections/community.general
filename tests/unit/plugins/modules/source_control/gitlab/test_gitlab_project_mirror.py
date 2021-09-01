# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Bidlingmaier (Max-Florian.Bidlingmaier@sap.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from distutils.version import LooseVersion

from ansible_collections.community.general.plugins.modules.source_control.gitlab.gitlab_project_mirror import GitlabProjectMirror


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         python_version_match_requirement, python_gitlab_module_version,
                         python_gitlab_version_match_requirement,
                         resp_get_project_by_name,
                         resp_remote_mirrors_list,
                         resp_remote_mirrors_create,
                        )

    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import Project
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


class TestGitlabProjectMirror(GitlabModuleTestCase):
    @with_httmock(resp_get_project_by_name)
    def setUp(self):
        super(TestGitlabProjectMirror, self).setUp()

        self.moduleUtil = GitLabProjectMirror(module=self.mock_module, gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_remote_mirrors_list)
    @with_httmock(resp_remote_mirrors_create)
    def test_createOrUpdateMirror(self):
        rvalue = self.moduleUtil.createOrUpdateMirror(mirror_url='https://*****:*****@example.com/gitlab/example.git', mirror_enabled=True)
        self.assertEqual(rvalue, True)

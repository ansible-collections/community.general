# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Raphaël Droz (raphael.droz@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.source_control.gitlab.gitlab_service import GitLabServices


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         python_version_match_requirement,
                         resp_get_project_by_name, resp_get_project)
    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import Project

except ImportError as e:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object
    resp_get_project_by_name = _dummy
    resp_get_project = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabService(GitlabModuleTestCase):
    def setUp(self):
        super(TestGitlabService, self).setUp()

    @with_httmock(resp_get_project)
    @with_httmock(resp_get_project_by_name)
    def test_exist_service(self):
        project = self.gitlab_instance.projects.get(1)
        self.assertEqual(type(project), Project)

        remote_service = project.services.get(1)

        # self.moduleUtil = GitLabServices(module=self.mock_module, gitlab_instance=self.gitlab_instance)
        self.moduleUtil = GitLabServices(module=self.mock_module, name="asana")

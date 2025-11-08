# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules.gitlab_project import GitLabProject


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (
        GitlabModuleTestCase,
        resp_get_group,
        resp_get_project_by_name,
        resp_create_project,
        resp_get_project,
        resp_delete_project,
        resp_get_user,
    )

    # GitLab module requirements
    from gitlab.v4.objects import Project
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object  # type: ignore
    resp_get_group = _dummy
    resp_get_project_by_name = _dummy
    resp_create_project = _dummy
    resp_get_project = _dummy
    resp_delete_project = _dummy
    resp_get_user = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabProject(GitlabModuleTestCase):
    @with_httmock(resp_get_user)
    def setUp(self):
        super().setUp()

        self.gitlab_instance.user = self.gitlab_instance.users.get(1)
        self.moduleUtil = GitLabProject(module=self.mock_module, gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_get_group)
    @with_httmock(resp_get_project_by_name)
    def test_project_exist(self):
        group = self.gitlab_instance.groups.get(1)

        rvalue = self.moduleUtil.exists_project(group, "diaspora-client")

        self.assertEqual(rvalue, True)

        rvalue = self.moduleUtil.exists_project(group, "missing-project")

        self.assertEqual(rvalue, False)

    @with_httmock(resp_get_group)
    @with_httmock(resp_create_project)
    def test_create_project(self):
        group = self.gitlab_instance.groups.get(1)
        project = self.moduleUtil.create_project(
            group, {"name": "Diaspora Client", "path": "diaspora-client", "namespace_id": group.id}
        )

        self.assertEqual(type(project), Project)
        self.assertEqual(project.name, "Diaspora Client")

    @with_httmock(resp_get_project)
    def test_update_project(self):
        project = self.gitlab_instance.projects.get(1)

        changed, newProject = self.moduleUtil.update_project(project, {"name": "New Name"})

        self.assertEqual(changed, True)
        self.assertEqual(type(newProject), Project)
        self.assertEqual(newProject.name, "New Name")

        changed, newProject = self.moduleUtil.update_project(project, {"name": "New Name"})

        self.assertEqual(changed, False)
        self.assertEqual(newProject.name, "New Name")

    @with_httmock(resp_get_project)
    def test_update_project_merge_method(self):
        project = self.gitlab_instance.projects.get(1)

        # merge_method should be 'merge' by default
        self.assertEqual(project.merge_method, "merge")

        changed, newProject = self.moduleUtil.update_project(
            project, {"name": "New Name", "merge_method": "rebase_merge"}
        )

        self.assertEqual(changed, True)
        self.assertEqual(type(newProject), Project)
        self.assertEqual(newProject.name, "New Name")
        self.assertEqual(newProject.merge_method, "rebase_merge")

        changed, newProject = self.moduleUtil.update_project(
            project, {"name": "New Name", "merge_method": "rebase_merge"}
        )

        self.assertEqual(changed, False)
        self.assertEqual(newProject.name, "New Name")
        self.assertEqual(newProject.merge_method, "rebase_merge")

    @with_httmock(resp_get_group)
    @with_httmock(resp_get_project_by_name)
    @with_httmock(resp_delete_project)
    def test_delete_project(self):
        group = self.gitlab_instance.groups.get(1)

        self.moduleUtil.exists_project(group, "diaspora-client")

        rvalue = self.moduleUtil.delete_project()

        self.assertEqual(rvalue, None)

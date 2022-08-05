# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.source_control.gitlab.gitlab_group import GitLabGroup


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (GitlabModuleTestCase,
                         python_version_match_requirement,
                         resp_get_group, resp_get_missing_group, resp_create_group,
                         resp_create_subgroup, resp_delete_group, resp_find_group_project)

    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import Group
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object
    resp_get_group = _dummy
    resp_get_missing_group = _dummy
    resp_create_group = _dummy
    resp_create_subgroup = _dummy
    resp_delete_group = _dummy
    resp_find_group_project = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabGroup(GitlabModuleTestCase):
    def setUp(self):
        super(TestGitlabGroup, self).setUp()

        self.moduleUtil = GitLabGroup(module=self.mock_module, gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_get_group)
    def test_exist_group(self):
        rvalue = self.moduleUtil.exists_group(1)

        self.assertEqual(rvalue, True)

    @with_httmock(resp_get_missing_group)
    def test_exist_group(self):
        rvalue = self.moduleUtil.exists_group(1)

        self.assertEqual(rvalue, False)

    @with_httmock(resp_create_group)
    def test_create_group(self):
        group = self.moduleUtil.create_group({'name': "Foobar Group",
                                              'path': "foo-bar",
                                              'description': "An interesting group",
                                              'project_creation_level': "developer",
                                              'subgroup_creation_level': "maintainer",
                                              'require_two_factor_authentication': True,
                                              })

        self.assertEqual(type(group), Group)
        self.assertEqual(group.name, "Foobar Group")
        self.assertEqual(group.path, "foo-bar")
        self.assertEqual(group.description, "An interesting group")
        self.assertEqual(group.project_creation_level, "developer")
        self.assertEqual(group.subgroup_creation_level, "maintainer")
        self.assertEqual(group.require_two_factor_authentication, True)
        self.assertEqual(group.id, 1)

    @with_httmock(resp_create_subgroup)
    def test_create_subgroup(self):
        group = self.moduleUtil.create_group({'name': "BarFoo Group",
                                              'path': "bar-foo",
                                              'parent_id': 1,
                                              'project_creation_level': "noone",
                                              'require_two_factor_authentication': True,
                                              })

        self.assertEqual(type(group), Group)
        self.assertEqual(group.name, "BarFoo Group")
        self.assertEqual(group.full_path, "foo-bar/bar-foo")
        self.assertEqual(group.project_creation_level, "noone")
        self.assertEqual(group.require_two_factor_authentication, True)
        self.assertEqual(group.id, 2)
        self.assertEqual(group.parent_id, 1)

    @with_httmock(resp_get_group)
    def test_update_group(self):
        group = self.gitlab_instance.groups.get(1)
        changed, newGroup = self.moduleUtil.update_group(group, {'name': "BarFoo Group",
                                                                 'visibility': "private",
                                                                 'project_creation_level': "maintainer",
                                                                 'require_two_factor_authentication': True,
                                                                 })

        self.assertEqual(changed, True)
        self.assertEqual(newGroup.name, "BarFoo Group")
        self.assertEqual(newGroup.visibility, "private")
        self.assertEqual(newGroup.project_creation_level, "maintainer")
        self.assertEqual(newGroup.require_two_factor_authentication, True)

        changed, newGroup = self.moduleUtil.update_group(group, {'name': "BarFoo Group"})

        self.assertEqual(changed, False)

    @with_httmock(resp_get_group)
    @with_httmock(resp_find_group_project)
    @with_httmock(resp_delete_group)
    def test_delete_group(self):
        self.moduleUtil.exists_group(1)

        print(self.moduleUtil.group_object.projects)

        rvalue = self.moduleUtil.delete_group()

        self.assertEqual(rvalue, None)

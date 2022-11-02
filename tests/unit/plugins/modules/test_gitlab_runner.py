# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.gitlab_runner import GitLabRunner


def _dummy(x):
    """Dummy function.  Only used as a placeholder for toplevel definitions when the test is going
    to be skipped anyway"""
    return x


pytestmark = []
try:
    from .gitlab import (FakeAnsibleModule,
                         GitlabModuleTestCase,
                         python_version_match_requirement,
                         resp_find_runners_all,
                         resp_find_runners_list, resp_get_runner,
                         resp_create_runner, resp_delete_runner)

    # GitLab module requirements
    if python_version_match_requirement():
        from gitlab.v4.objects import Runner
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load gitlab module required for testing"))
    # Need to set these to something so that we don't fail when parsing
    GitlabModuleTestCase = object
    resp_find_runners_list = _dummy
    resp_get_runner = _dummy
    resp_create_runner = _dummy
    resp_delete_runner = _dummy

# Unit tests requirements
try:
    from httmock import with_httmock  # noqa
except ImportError:
    pytestmark.append(pytest.mark.skip("Could not load httmock module required for testing"))
    with_httmock = _dummy


class TestGitlabRunner(GitlabModuleTestCase):
    def setUp(self):
        super(TestGitlabRunner, self).setUp()

        self.module_util_all = GitLabRunner(module=FakeAnsibleModule({"owned": False}), gitlab_instance=self.gitlab_instance)
        self.module_util_owned = GitLabRunner(module=FakeAnsibleModule({"owned": True}), gitlab_instance=self.gitlab_instance)

    @with_httmock(resp_find_runners_all)
    @with_httmock(resp_get_runner)
    def test_runner_exist_all(self):
        rvalue = self.module_util_all.exists_runner("test-1-20150125")

        self.assertEqual(rvalue, True)

        rvalue = self.module_util_all.exists_runner("test-3-00000000")

        self.assertEqual(rvalue, False)

    @with_httmock(resp_find_runners_list)
    @with_httmock(resp_get_runner)
    def test_runner_exist_owned(self):
        rvalue = self.module_util_owned.exists_runner("test-1-20201214")

        self.assertEqual(rvalue, True)

        rvalue = self.module_util_owned.exists_runner("test-3-00000000")

        self.assertEqual(rvalue, False)

    @with_httmock(resp_create_runner)
    def test_create_runner(self):
        runner = self.module_util_all.create_runner({"token": "token", "description": "test-1-20150125"})

        self.assertEqual(type(runner), Runner)
        self.assertEqual(runner.description, "test-1-20150125")

    @with_httmock(resp_find_runners_all)
    @with_httmock(resp_get_runner)
    def test_update_runner(self):
        runner = self.module_util_all.find_runner("test-1-20150125")

        changed, newRunner = self.module_util_all.update_runner(runner, {"description": "Runner description"})

        self.assertEqual(changed, True)
        self.assertEqual(type(newRunner), Runner)
        self.assertEqual(newRunner.description, "Runner description")

        changed, newRunner = self.module_util_all.update_runner(runner, {"description": "Runner description"})

        self.assertEqual(changed, False)
        self.assertEqual(newRunner.description, "Runner description")

    @with_httmock(resp_find_runners_all)
    @with_httmock(resp_get_runner)
    @with_httmock(resp_delete_runner)
    def test_delete_runner(self):
        self.module_util_all.exists_runner("test-1-20150125")

        rvalue = self.module_util_all.delete_runner()

        self.assertEqual(rvalue, None)

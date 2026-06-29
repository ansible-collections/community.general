# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules.archive import common_path, create_module, get_archive


class TestArchive(ModuleTestCase):
    def setUp(self):
        super().setUp()

        self.mock_os_path_isdir = patch("os.path.isdir")
        self.os_path_isdir = self.mock_os_path_isdir.start()

    def tearDown(self):
        self.os_path_isdir = self.mock_os_path_isdir.stop()

    def test_archive_removal_safety(self):
        with set_module_args(dict(path=["/foo", "/bar", "/baz"], dest="/foo/destination.tgz", remove=True)):
            module = create_module()

        self.os_path_isdir.side_effect = [True, False, False, True]

        module.fail_json = Mock()

        archive = get_archive(module)

        module.fail_json.assert_called_once_with(
            path=b", ".join(archive.paths),
            msg="Error, created archive can not be contained in source paths when remove=true",
        )


PATHS: tuple[tuple[list[str | bytes], str | bytes], ...] = (
    ([], ""),
    (["/"], "/"),
    ([b"/"], b"/"),
    (["/foo", "/bar", "/baz", "/foobar", "/barbaz", "/foo/bar"], "/"),
    ([b"/foo", b"/bar", b"/baz", b"/foobar", b"/barbaz", b"/foo/bar"], b"/"),
    (["/foo/bar/baz", "/foo/bar"], "/foo/"),
    (["/foo/bar/baz", "/foo/bar/"], "/foo/bar/"),
)


@pytest.mark.parametrize("paths,root", PATHS)
def test_common_path(paths: list[str | bytes], root: str | bytes) -> None:
    assert common_path(paths) == root

# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.tests.unit.compat.mock import Mock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args
from ansible_collections.community.general.plugins.modules.files.archive import get_archive, common_path


class TestArchive(ModuleTestCase):
    def setUp(self):
        super(TestArchive, self).setUp()

        self.mock_os_path_isdir = patch('os.path.isdir')
        self.os_path_isdir = self.mock_os_path_isdir.start()

    def tearDown(self):
        self.os_path_isdir = self.mock_os_path_isdir.stop()

    def test_archive_removal_safety(self):
        set_module_args(
            dict(
                path=['/foo', '/bar', '/baz'],
                dest='/foo/destination.tgz',
                remove=True
            )
        )

        module = AnsibleModule(
            argument_spec=dict(
                path=dict(type='list', elements='path', required=True),
                format=dict(type='str', default='gz', choices=['bz2', 'gz', 'tar', 'xz', 'zip']),
                dest=dict(type='path'),
                exclude_path=dict(type='list', elements='path', default=[]),
                exclusion_patterns=dict(type='list', elements='path'),
                force_archive=dict(type='bool', default=False),
                remove=dict(type='bool', default=False),
            ),
            add_file_common_args=True,
            supports_check_mode=True,
        )

        self.os_path_isdir.side_effect = [True, False, False, True]

        module.fail_json = Mock()

        archive = get_archive(module)

        module.fail_json.assert_called_once_with(
            path=b', '.join(archive.paths),
            msg='Error, created archive can not be contained in source paths when remove=true'
        )


PATHS = (
    ([], ''),
    (['/'], '/'),
    ([b'/'], b'/'),
    (['/foo', '/bar', '/baz', '/foobar', '/barbaz', '/foo/bar'], '/'),
    ([b'/foo', b'/bar', b'/baz', b'/foobar', b'/barbaz', b'/foo/bar'], b'/'),
    (['/foo/bar/baz', '/foo/bar'], '/foo/'),
    (['/foo/bar/baz', '/foo/bar/'], '/foo/bar/'),
)


@pytest.mark.parametrize("paths,root", PATHS)
def test_common_path(paths, root):
    assert common_path(paths) == root

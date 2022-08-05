# -*- coding: utf-8 -*-

# Copyright (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.modules.files import sapcar_extract
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of SAPCAR"""
    return "/tmp/sapcar"


class Testsapcar_extract(ModuleTestCase):
    """Main class for testing sapcar_extract module."""

    def setUp(self):
        """Setup."""
        super(Testsapcar_extract, self).setUp()
        self.module = sapcar_extract
        self.mock_get_bin_path = patch.object(basic.AnsibleModule, 'get_bin_path', get_bin_path)
        self.mock_get_bin_path.start()
        self.addCleanup(self.mock_get_bin_path.stop)  # ensure that the patching is 'undone'

    def tearDown(self):
        """Teardown."""
        super(Testsapcar_extract, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_sapcar_extract(self):
        """Check that result is changed."""
        set_module_args({
            'path': "/tmp/HANA_CLIENT_REV2_00_053_00_LINUX_X86_64.SAR",
            'dest': "/tmp/test2",
            'binary_path': "/tmp/sapcar"
        })
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, '', ''  # successful execution, no output
            with self.assertRaises(AnsibleExitJson) as result:
                sapcar_extract.main()
                self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(run_command.call_count, 1)

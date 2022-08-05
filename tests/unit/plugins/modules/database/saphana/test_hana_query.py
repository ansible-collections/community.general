# -*- coding: utf-8 -*-

# Copyright (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.modules.database.saphana import hana_query
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of hdbsql"""
    return "/usr/sap/HDB/HDB01/exe/hdbsql"


class Testhana_query(ModuleTestCase):
    """Main class for testing hana_query module."""

    def setUp(self):
        """Setup."""
        super(Testhana_query, self).setUp()
        self.module = hana_query
        self.mock_get_bin_path = patch.object(basic.AnsibleModule, 'get_bin_path', get_bin_path)
        self.mock_get_bin_path.start()
        self.addCleanup(self.mock_get_bin_path.stop)  # ensure that the patching is 'undone'

    def tearDown(self):
        """Teardown."""
        super(Testhana_query, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_hana_query(self):
        """Check that result is processed."""
        set_module_args({
            'sid': "HDB",
            'instance': "01",
            'encrypted': False,
            'host': "localhost",
            'user': "SYSTEM",
            'password': "1234Qwer",
            'database': "HDB",
            'query': "SELECT * FROM users;"
        })
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'username,name\n  testuser,test user  \n myuser, my user   \n', ''
            with self.assertRaises(AnsibleExitJson) as result:
                hana_query.main()
            self.assertEqual(result.exception.args[0]['query_result'], [[
                {'username': 'testuser', 'name': 'test user'},
                {'username': 'myuser', 'name': 'my user'},
            ]])
        self.assertEqual(run_command.call_count, 1)

    def test_hana_userstore_query(self):
        """Check that result is processed with userstore."""
        set_module_args({
            'sid': "HDB",
            'instance': "01",
            'encrypted': False,
            'host': "localhost",
            'user': "SYSTEM",
            'userstore': True,
            'database': "HDB",
            'query': "SELECT * FROM users;"
        })
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'username,name\n  testuser,test user  \n myuser, my user   \n', ''
            with self.assertRaises(AnsibleExitJson) as result:
                hana_query.main()
            self.assertEqual(result.exception.args[0]['query_result'], [[
                {'username': 'testuser', 'name': 'test user'},
                {'username': 'myuser', 'name': 'my user'},
            ]])
        self.assertEqual(run_command.call_count, 1)

    def test_hana_failed_no_passwd(self):
        """Check that result is failed with no password."""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'sid': "HDB",
                'instance': "01",
                'encrypted': False,
                'host': "localhost",
                'user': "SYSTEM",
                'database': "HDB",
                'query': "SELECT * FROM users;"
            })
            self.module.main()

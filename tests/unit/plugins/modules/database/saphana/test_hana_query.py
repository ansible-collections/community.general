# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

<<<<<<< HEAD
<<<<<<< HEAD
from ansible_collections.community.general.plugins.modules import hana_query
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
=======
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
=======
>>>>>>> 61aafaec... change test
from ansible_collections.community.general.plugins.modules import hana_query
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils import basic

def get_bin_path(*args, **kwargs):
    """Function to return path of hdbsql"""
    return "/usr/sap/HDB/HDB01/exe/hdbsql"


class Testhana_query(ModuleTestCase):
    """Main class for testing hana_query module."""

    def setUp(self):
<<<<<<< HEAD
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
>>>>>>> 8358dba9... change hana_query add test
=======
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
>>>>>>> 61aafaec... change test
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    def test_hana_query(self):
        """Check that result is changed."""
=======

=======
>>>>>>> 2d09b71d... change test
    def test_ensure_command_called(self):
>>>>>>> 8358dba9... change hana_query add test
=======
    def test_hana_query(self):
        """Check that result is changed."""
>>>>>>> 61aafaec... change test
        set_module_args({
            'sid': "HDB",
            'instance': "01",
            'encrypted': False,
            'host': "localhost",
            'user': "SYSTEM",
            'password': "1234Qwer",
            'database': "HDB",
<<<<<<< HEAD
            'query': "SELECT * FROM users;"
        })
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, '', ''  # successful execution, no output
            with self.assertRaises(AnsibleExitJson) as result:
                hana_query.main()
                self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(run_command.call_count, 1)
=======
            'query': "SELECT * FROM users:"
        })
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, '', ''  # successful execution, no output
            with self.assertRaises(AnsibleExitJson) as result:
                hana_query.main()
                self.assertTrue(result.exception.args[0]['changed'])

<<<<<<< HEAD
        mock_run_command.assert_called_once_with('/usr/sap/HDB/HDB01/exe/hdbsql')
<<<<<<< HEAD
>>>>>>> 8358dba9... change hana_query add test
=======
>>>>>>> 2d09b71d... change test
=======
        self.assertEqual(run_command.call_count, 2)
>>>>>>> 61aafaec... change test

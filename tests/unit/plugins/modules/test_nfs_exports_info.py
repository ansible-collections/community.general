# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Samaneh Yousefnezhad <s.yousefnezhad@um.ac.ir>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_print_statements, print_function)
__metaclass__ = type

import pytest
from unittest.mock import patch, mock_open

from ansible_collections.community.general.plugins.modules import nfs_exports_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase

MOCK_EXPORTS_DATA = """
/data/shared   192.168.1.0/24(rw,sync,no_subtree_check)
/mnt/backup    192.168.1.50(ro,async)
"""


class TestNfsExportsInfoModule(ModuleTestCase):
    def setUp(self):
        super(TestNfsExportsInfoModule, self).setUp()
        self.module = nfs_exports_info

    def test_module_without_exports_file(self):
        with patch('os.path.exists', return_value=False):
            with pytest.raises(AnsibleExitJson) as result:
                self.run_module()
            
            assert result.value.args[0]['exports'] == []
            assert result.value.args[0]['changed'] is False

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=MOCK_EXPORTS_DATA)
    def test_module_with_valid_exports(self, mock_file, mock_exists):
        """تست پارس کردن موفق فایل nfs exports"""
        with pytest.raises(AnsibleExitJson) as result:
            self.run_module()

        response = result.value.args[0]
        assert response['changed'] is False
        assert len(response['exports']) == 2
        
        assert response['exports'][0]['path'] == '/data/shared'
        assert response['exports'][0]['client'] == '192.168.1.0/24'
        assert 'rw' in response['exports'][0]['options']

        assert response['exports'][1]['path'] == '/mnt/backup'
        assert response['exports'][1]['client'] == '192.168.1.50'
        assert 'ro' in response['exports'][1]['options']

    def run_module(self, module_args=None):
        if module_args is None:
            module_args = {}
        
        with patch('ansible.module_utils.basic.AnsibleModule.exit_json', side_effect=AnsibleExitJson):
            with patch('ansible.module_utils.basic.AnsibleModule.fail_json', side_effect=AnsibleFailJson):
                self.module.main()

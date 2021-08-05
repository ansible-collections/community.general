# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.general.plugins.modules.system import sap_task_list_execute


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_task_list_execute

    def tearDown(self):
        super(TestSAPRfcModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_error_no_task_list(self):
        """tests fail to exec task list"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "task_to_execute": "SAP_BASIS_SSL_CHECK"
        })

        with patch.object(self.module, 'Connection') as conn:
            conn.return_value = ''
            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'The task list does not exsist.')

    def test_success(self):
        """test execute task list success"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "task_to_execute": "SAP_BASIS_SSL_CHECK"
        })
        with patch.object(self.module, 'XML') as XML:
            XML.input = b'''<?xml version="1.0" encoding="utf-8"?>
                            <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
                            <asx:values>
                                <VERSION>1.2</VERSION>
                                <SESSION>
                                <TASKLIST>SAP_BASIS_SSL_CHECK</TASKLIST>
                                </SESSION>
                            </asx:values>
                            </asx:abap>'''
            with patch.object(self.module, 'xml_dict') as xml_dict:
                xml_dict.return_value = {'{http://www.sap.com/abapxml}values': {'SESSION': {'TASKLIST': 'SAP_BASIS_SSL_CHECK'}}}
                with self.assertRaises(AnsibleExitJson) as result:
                    sap_task_list_execute.main()
        self.assertEqual(result.exception.args[0]['out'], 'SAP_BASIS_SSL_CHECK')

    def test_success_no_log(self):
        """test execute task list success without logs"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "task_to_execute": "SAP_BASIS_SSL_CHECK"
        })
        with patch.object(self.module, 'XML') as XML:
            XML.input = ''
            with self.assertRaises(AnsibleExitJson) as result:
                sap_task_list_execute.main()
        self.assertEqual(result.exception.args[0]['out'], 'No logs available.')

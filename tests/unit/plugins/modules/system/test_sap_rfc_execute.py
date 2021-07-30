# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.general.plugins.modules.system import sap_rfc_execute


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_rfc_execute

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

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['changed'], True)

    def test_show(self):
        """tests show success"""

        set_module_args({
            "state": "show",
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "task_to_execute": "SAP_BASIS_SSL_CHECK"
        })

        with patch.object(self.module, 'call_rfc_method') as show_list:
            show_list.return_value = {'ET_PARAM_DEF':
                                      [{'TASKNAME': 'CL_STCT_CHECK_SEC_CRYPTO', 'LNR': 1, 'FIELDNAME': 'P_OPT1', 'MANDATORY': '',
                                        'DATATYPE': 'CHAR', 'LENG': '000001', 'DECIMALS': '000000', 'LOWERCASE': '',
                                        'OUTPUTLEN': '000001', 'SIGNFLAG': '', 'CONVEXIT': '', 'DDTEXT': 'Warning', 'PASSWORD': '',
                                        'READ_ONLY': '', 'CHECKBOX': '', 'RADIOBUTTON': 'X', 'RB_GROUP': 'ICM', 'DEFAULTVAL': 'X'}]}
            with self.assertRaises(AnsibleExitJson) as success:
                sap_rfc_execute.main()
            self.assertEqual(success.exception.args[0]['results'][0], ['CL_STCT_CHECK_SEC_CRYPTO', 'P_OPT1', 'X'])

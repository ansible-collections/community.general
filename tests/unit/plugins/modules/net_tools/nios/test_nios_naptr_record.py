# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.general.plugins.modules.net_tools.nios import nios_naptr_record
from ansible_collections.community.general.plugins.module_utils.net_tools.nios import api
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosNAPTRRecordModule(TestNiosModule):

    module = nios_naptr_record

    def setUp(self):
        super(TestNiosNAPTRRecordModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.community.general.plugins.modules.net_tools.nios.nios_naptr_record.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.community.general.plugins.modules.net_tools.nios.nios_naptr_record.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.community.general.plugins.modules.net_tools.nios.nios_naptr_record.WapiModule.run')
        self.mock_wapi_run.start()
        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible_collections.community.general.plugins.module_utils.net_tools.nios.api.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosNAPTRRecordModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_wapi_run.stop()
        self.mock_check_type_dict.stop()

    def _get_wapi(self, test_object):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=test_object)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        return wapi

    def load_fixtures(self, commands=None):
        self.exec_command.return_value = (0, load_fixture('nios_result.txt').strip(), None)
        self.load_config.return_value = dict(diff=None, session='session')

    def test_nios_naptr_record_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': '*.subscriber-100.ansiblezone.com',
                              'order': '1000', 'preference': '10', 'replacement': 'replacement1.network.ansiblezone.com',
                              'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "name": {"ib_req": True},
            "order": {"ib_req": True},
            "preference": {"ib_req": True},
            "replacement": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi.__dict__)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': self.mock_check_type_dict_obj().__getitem__(),
                                                                  'order': '1000', 'preference': '10',
                                                                  'replacement': 'replacement1.network.ansiblezone.com'})

    def test_nios_naptr_record_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': '*.subscriber-100.ansiblezone.com',
                              'order': '1000', 'preference': '10', 'replacement': 'replacement1.network.ansiblezone.com',
                              'comment': 'updated comment', 'extattrs': None}

        test_object = [
            {
                "comment": "test comment",
                "_ref": "naptrrecord/ZG5zLm5ldHdvcmtfdmlldyQw:default/true",
                "name": "*.subscriber-100.ansiblezone.com",
                "order": "1000",
                "preference": "10",
                "replacement": "replacement1.network.ansiblezone.com",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "order": {"ib_req": True},
            "preference": {"ib_req": True},
            "replacement": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])

    def test_nios_naptr_record_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': '*.subscriber-100.ansiblezone.com',
                              'order': '1000', 'preference': '10', 'replacement': 'replacement1.network.ansiblezone.com',
                              'comment': None, 'extattrs': None}

        ref = "naptrrecord/ZG5zLm5ldHdvcmtfdmlldyQw:default/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "*.subscriber-100.ansiblezone.com",
            "order": "1000",
            "preference": "10",
            "replacement": "replacement1.network.ansiblezone.com",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "order": {"ib_req": True},
            "preference": {"ib_req": True},
            "replacement": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

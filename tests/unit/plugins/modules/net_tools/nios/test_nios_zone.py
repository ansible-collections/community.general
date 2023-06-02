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


from ansible_collections.community.general.plugins.modules.net_tools.nios import nios_zone
from ansible_collections.community.general.plugins.module_utils.net_tools.nios import api
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosZoneModule(TestNiosModule):

    module = nios_zone

    def setUp(self):
        super(TestNiosZoneModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.community.general.plugins.modules.net_tools.nios.nios_zone.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}
        self.mock_wapi = patch('ansible_collections.community.general.plugins.modules.net_tools.nios.nios_zone.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.community.general.plugins.modules.net_tools.nios.nios_zone.WapiModule.run')
        self.mock_wapi_run.start()
        self.load_config = self.mock_wapi_run.start()

    def tearDown(self):
        super(TestNiosZoneModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_wapi_run.stop()

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

    def test_nios_zone_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'fqdn': 'ansible.com',
                              'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "fqdn": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'fqdn': 'ansible.com'})

    def test_nios_zone_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'fqdn': 'ansible.com',
                              'comment': None, 'extattrs': None}

        ref = "zone/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "fqdn": "ansible.com",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "fqdn": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_zone_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'fqdn': 'ansible.com',
                              'comment': 'updated comment', 'extattrs': None}

        test_object = [
            {
                "comment": "test comment",
                "_ref": "zone/ZG5zLm5ldHdvcmtfdmlldyQw:default/true",
                "fqdn": "ansible.com",
                "extattrs": {'Site': {'value': 'test'}}
            }
        ]

        test_spec = {
            "fqdn": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])

    def test_nios_zone_create_using_grid_primary_secondaries(self):
        self.module.params = {'provider': None, 'state': 'present', 'fqdn': 'ansible.com',
                              'grid_primary': [{"name": "gridprimary.grid.com"}],
                              'grid_secondaries': [{"name": "gridsecondary1.grid.com"},
                                                   {"name": "gridsecondary2.grid.com"}],
                              'restart_if_needed': True,
                              'comment': None, 'extattrs': None}

        test_object = None
        grid_spec = dict(
            name=dict(required=True),
        )
        test_spec = {
            "fqdn": {"ib_req": True},
            "grid_primary": {},
            "grid_secondaries": {},
            "restart_if_needed": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'fqdn': 'ansible.com',
                                                                  "grid_primary": [{"name": "gridprimary.grid.com"}],
                                                                  "grid_secondaries": [{"name": "gridsecondary1.grid.com"},
                                                                                       {"name": "gridsecondary2.grid.com"}],
                                                                  "restart_if_needed": True
                                                                  })

    def test_nios_zone_remove_using_grid_primary_secondaries(self):
        self.module.params = {'provider': None, 'state': 'absent', 'fqdn': 'ansible.com',
                              'grid_primary': [{"name": "gridprimary.grid.com"}],
                              'grid_secondaries': [{"name": "gridsecondary1.grid.com"},
                                                   {"name": "gridsecondary2.grid.com"}],
                              'restart_if_needed': True,
                              'comment': None, 'extattrs': None}

        ref = "zone/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "fqdn": "ansible.com",
            "grid_primary": [{"name": "gridprimary.grid.com"}],
            "grid_secondaries": [{"name": "gridsecondary1.grid.com"}, {"name": "gridsecondary2.grid.com"}],
            "restart_if_needed": True,
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "fqdn": {"ib_req": True},
            "grid_primary": {},
            "grid_secondaries": {},
            "restart_if_needed": {},
            "comment": {},
            "extattrs": {}
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_zone_create_using_name_server_group(self):
        self.module.params = {'provider': None, 'state': 'present', 'fqdn': 'ansible.com',
                              'ns_group': 'examplensg', 'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "fqdn": {"ib_req": True},
            "ns_group": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'fqdn': 'ansible.com',
                                                                  'ns_group': 'examplensg'})

    def test_nios_zone_remove_using_name_server_group(self):
        self.module.params = {'provider': None, 'state': 'absent', 'fqdn': 'ansible.com',
                              'ns_group': 'examplensg', 'comment': None, 'extattrs': None}

        ref = "zone/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "fqdn": "ansible.com",
            "ns_group": "examplensg",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "fqdn": {"ib_req": True},
            "ns_group": {},
            "comment": {},
            "extattrs": {}
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_zone_create_using_zone_format(self):
        self.module.params = {'provider': None, 'state': 'present', 'fqdn': '10.10.10.in-addr.arpa',
                              'zone_format': 'IPV4', 'comment': None, 'extattrs': None}

        test_object = None

        test_spec = {
            "fqdn": {"ib_req": True},
            "zone_format": {},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'fqdn': '10.10.10.in-addr.arpa',
                                                                  'zone_format': 'IPV4'})

    def test_nios_zone_remove_using_using_zone_format(self):
        self.module.params = {'provider': None, 'state': 'absent', 'fqdn': 'ansible.com',
                              'zone_format': 'IPV4', 'comment': None, 'extattrs': None}

        ref = "zone/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "fqdn": "ansible.com",
            "zone_format": "IPV4",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "fqdn": {"ib_req": True},
            "zone_format": {},
            "comment": {},
            "extattrs": {}
        }
        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

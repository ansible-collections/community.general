# (c) 2019 Red Hat Inc.
#
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

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules.network.cloudengine import ce_is_is_interface
from ansible_collections.community.general.tests.unit.modules.network.cloudengine.ce_module import TestCloudEngineModule, load_fixture
from ansible_collections.community.general.tests.unit.modules.utils import set_module_args


class TestCloudEngineLacpModule(TestCloudEngineModule):
    module = ce_is_is_interface

    def setUp(self):
        super(TestCloudEngineLacpModule, self).setUp()

        self.mock_get_config = patch('ansible_collections.community.general.plugins.modules.network.cloudengine.ce_is_is_interface.get_nc_config')
        self.get_nc_config = self.mock_get_config.start()

        self.mock_set_config = patch('ansible_collections.community.general.plugins.modules.network.cloudengine.ce_is_is_interface.set_nc_config')
        self.set_nc_config = self.mock_set_config.start()
        self.set_nc_config.return_value = None

        self.before = load_fixture('ce_is_is_interface', 'before_interface.txt')
        self.after = load_fixture('ce_is_is_interface', 'after_interface.txt')

    def tearDown(self):
        super(TestCloudEngineLacpModule, self).tearDown()
        self.mock_set_config.stop()
        self.mock_get_config.stop()

    def test_isis_interface_present(self):
        update = ['interface 10GE1/0/1',
                  'isis enable 100',
                  'isis circuit-level level-1',
                  'isis dis-priority 10 level-1',
                  'isis ppp-negotiation 2-way',
                  'isis cost 10 level-2']
        self.get_nc_config.side_effect = (self.before, self.after)
        config = dict(
            instance_id=100,
            ifname='10GE1/0/1',
            leveltype='level_1',
            level1dispriority=10,
            silentenable=True,
            silentcost=True,
            typep2penable=True,
            snpacheck=True,
            p2pnegotiationmode='2_way',
            p2ppeeripignore=True,
            ppposicpcheckenable=True,
            level2cost=10
        )
        set_module_args(config)
        result = self.execute_module(changed=True)
        print(result['updates'])
        self.assertEquals(sorted(result['updates']), sorted(update))

    def test_isis_interface_absent(self):
        update = ['interface 10GE1/0/1',
                  'undo isis enable',
                  'undo isis circuit-level',
                  'undo isis ppp-negotiation']
        self.get_nc_config.side_effect = (self.after, self.before)
        config = dict(
            instance_id=100,
            ifname='10GE1/0/1',
            leveltype='level_1',
            level1dispriority=10,
            silentenable=True,
            silentcost=True,
            typep2penable=True,
            snpacheck=True,
            p2pnegotiationmode='2_way',
            p2ppeeripignore=True,
            ppposicpcheckenable=True,
            level2cost=10,
            state='absent'
        )
        set_module_args(config)
        result = self.execute_module(changed=True)
        self.assertEquals(sorted(result['updates']), sorted(update))

# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Hani Audah (@haudah) <haudah@vmware.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.plugins.modules.database.misc import redis_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

import re

# mock different possible output from the pcs command
_PCS_NO_CLUSTER = "Error: cluster is not currently running on this node"

config_template = """
Cluster Name: mycluster
Corosync Nodes:
 %s
Pacemaker Nodes:
 %s

Cluster Properties:
 cluster-infrastructure: corosync
 cluster-name: mycluster
 dc-version: 2.0.4-6.el8_3.1-2deceaa3ae
 have-watchdog: false

"""

_PCS_CLUSTER_CONFIG_OK = config_template % (("host1 host2",)*2)
_PCS_CLUSTER_CONFIG_MISSING_NODE = config_template % (("host1",)*2)


class TestPacemakerClusterModule(ModuleTestCase):

    def setUp(self):
        super(TestPacemakerClusterModule, self).setUp()
        # needed to keep track of how many times different run_commands were called
        self.config_call_count = 0
        self.create_call_count = 0
        self.create_call = ""
        self.property_call_count = 0
        self.property_call = ""
        # the initial pcs configuration will be different
        self.initial_config = ""

    def tearDown(self):
        super(TestPacemakerClusterModule, self).tearDown()

    def patch_redis_client(self, **kwds):
        return patch('ansible_collections.community.general.plugins.modules.database.misc.redis_info.redis_client', autospec=True, **kwds)

    # returns no_cluster_status
    # accepts cluster creation
    def fake_run_command(self, cmd):
        # first time called -> getting config
        if cmd.startswith("pcs config"):
            self.config_call_count += 1
            return (1, "", self.initial_config)
        elif cmd.startswith("pcs cluster setup"):
            self.create_call_count += 1
            self.create_call = cmd
            # std out for cluster creation isn't really needed
            return (1, "", "")
        elif cmd.startswith("pcs property"):
            self.property_call_count += 1
            self.property_call = cmd
            return (1, "", "")

    def test_new_cluster(self):
        set_module_args({
            'name': 'lbcluster',
            'state': 'online',
            'nodes': ['host1', 'host2'],
            'pcs_user': 'dummy_user',
            'pcs_password': 'dummy_pass',
        })

        self.initial_config = _PCS_NO_CLUSTER

        with patch.object(basic.AnsibleModule, 'run_command', side_effect=self.fake_run_command) as run_command:
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        # make sure the right number of pcs calls were made
        self.assertEqual(self.config_call_count, 1)
        self.assertEqual(self.create_call_count, 1)
        self.assertEqual(self.property_call_count, 1)
        # and make sure the proper creation command was called
        self.assertTrue(re.search(r'pcs cluster setup lbcluster', self.create_call) is not None)

    def test_without_required_parameters(self):
        """Failure must occur when any required parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_without_parameters(self):
        """Test without parameters"""
        with self.patch_redis_client(side_effect=FakeRedisClient) as redis_client:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({})
                self.module.main()
            self.assertEqual(redis_client.call_count, 1)
            self.assertEqual(redis_client.call_args, ({'host': 'localhost', 'port': 6379, 'password': None},))
            self.assertEqual(result.exception.args[0]['info']['redis_version'], '999.999.999')

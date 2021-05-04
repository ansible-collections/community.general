# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Hani Audah (@haudah) <haudah@vmware.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from enum import Enum
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.plugins.modules.clustering.pacemaker import pacemaker_cluster
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

class ClusterStatus(Enum):
    DOESNT_EXIST = 0
    DOWN = 1
    MISSING_NODE = 2
    MISSING_PROPERTIES = 3
    OK = 4

configs = {}
configs[ClusterStatus.DOESNT_EXIST] = """
Cluster Name: 
"""
configs[ClusterStatus.DOWN] = """
Cluster Name: mycluster
"""
configs[ClusterStatus.MISSING_NODE] = config_template % (("host1",)*2)
configs[ClusterStatus.OK] = config_template % (("host1 host2",)*2)

config_errors = {}
config_errors[ClusterStatus.DOWN] = """
Error error running crm_mon, is pacemaker running?
"""
config_errors[ClusterStatus.DOESNT_EXIST] = """
Error: unable to get crm_config

Error: error running crm_mon, is pacemaker running?
"""

status_ok = """
Cluster Status:
 Cluster Summary:
   * Stack: corosync
   * Current DC: host1 (version 2.0.4-6.el8_3.1-2deceaa3ae) - partition with quorum
   * Last updated: Tue May  4 19:36:12 2021
   * Last change:  Mon May  3 21:13:39 2021 by hacluster via crmd on lb02.haramco.org
   * 1 node configured
   * 0 resource instances configured
 Node List:
   * Online: [ host1 ]

PCSD Status:
  host1: Online
"""

nodes_status_template = """
Corosync Nodes:
 Online: %s
 Offline:
Pacemaker Nodes:
 Online: %s
 Standby:
 Standby with resource(s) running:
 Maintenance:
 Offline:
Pacemaker Remote Nodes:
 Online:
 Standby:
 Standby with resource(s) running:
 Maintenance:
 Offline:
"""

class TestPacemakerClusterModule(ModuleTestCase):

    def setUp(self):
        super(TestPacemakerClusterModule, self).setUp()
        self.module = pacemaker_cluster
        # needed to keep track of how many times different run_commands were called
        self.config_call_count = 0
        self.create_call_count = 0
        self.create_call = ""
        self.property_call_count = 0
        self.property_call = ""
        self.start_call_count = 0
        self.auth_call_count = 0
        # the initial pcs configuration will be different
        self.initial_status = None

    def tearDown(self):
        super(TestPacemakerClusterModule, self).tearDown()

    def patch_redis_client(self, **kwds):
        return patch('ansible_collections.community.general.plugins.modules.database.misc.redis_info.redis_client', autospec=True, **kwds)

    # mock all the commands that pcs would be expected to handle
    def fake_run_command(self, cmd):
        # just for terseness
        initial_status = self.initial_status
        # where needed for assertions, keep track of # of times pcs commands were called
        if cmd.startswith("pcs config"):
            self.config_call_count += 1
            # special case where cluster WAS down but was started up
            if initial_status == ClusterStatus.DOWN and self.start_call_count > 0:
                return (0, configs[ClusterStatus.OK], "")
            elif initial_status == ClusterStatus.DOESNT_EXIST and self.create_call_count > 0:
                return (0, configs[ClusterStatus.OK], "")
            return (1 if initial_status in [ClusterStatus.DOWN, ClusterStatus.DOESNT_EXIST] else 0, configs[initial_status], config_errors[initial_status])
        elif cmd.startswith("pcs cluster setup"):
            self.create_call_count += 1
            self.create_call = cmd
            # output for cluster creation isn't really needed
            return (0, "", "")
        elif cmd.startswith("pcs property"):
            self.property_call_count += 1
            self.property_call = cmd
            # output when setting properties isn't really needed
            return (0, "", "")
        elif cmd.startswith("pcs cluster status"):
            if not(initial_status in [ClusterStatus.DOWN, ClusterStatus.DOESNT_EXIST]) or \
                initial_status == ClusterStatus.DOESNT_EXIST and self.create_call_count > 0:
                return (0, status_ok, "")
            else:
                return (1, "", _PCS_NO_CLUSTER)
        elif cmd.startswith("pcs host auth"):
            self.auth_call_count += 1
            # output when authing isn't really needed
            return (0, "", "")
        elif cmd.startswith("pcs nodes status both"):
            # missing node AND node wasn't added in a previous call
            if initial_status == ClusterStatus.MISSING_NODES and self.add_nodes_call_count == 0:
                return (0, nodes_status_template % (("host1",) * 2), "")
            else:
                return (0, nodes_status_template % (("host1 host2",) * 2), "")

    def test_new_cluster(self):
        set_module_args({
            'name': 'lbcluster',
            'state': 'online',
            'nodes': ['host1', 'host2'],
            'pcs_user': 'dummy_user',
            'pcs_password': 'dummy_pass',
        })

        self.initial_status = ClusterStatus.DOESNT_EXIST

        with patch.object(basic.AnsibleModule, 'run_command', side_effect=self.fake_run_command) as run_command:
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        # make sure the right number of pcs calls were made
        self.assertEqual(self.create_call_count, 1)
        self.assertEqual(self.property_call_count, 1)
        self.assertEqual(self.auth_call_count, 1)
        # and make sure the proper creation command was called
        self.assertTrue(re.search(r'pcs cluster setup lbcluster', self.create_call) is not None)

    def test_without_required_parameters(self):
        """Failure must occur when any required parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

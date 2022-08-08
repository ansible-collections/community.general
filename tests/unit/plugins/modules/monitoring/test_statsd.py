# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.monitoring import statsd
from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class FakeStatsD(MagicMock):

    def incr(self, *args, **kwargs):
        pass

    def gauge(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass


class TestStatsDModule(ModuleTestCase):

    def setUp(self):
        super(TestStatsDModule, self).setUp()
        statsd.HAS_STATSD = True
        self.module = statsd

    def tearDown(self):
        super(TestStatsDModule, self).tearDown()

    def patch_udp_statsd_client(self, **kwargs):
        return patch('ansible_collections.community.general.plugins.modules.monitoring.statsd.udp_statsd_client', autospec=True, **kwargs)

    def patch_tcp_statsd_client(self, **kwargs):
        return patch('ansible_collections.community.general.plugins.modules.monitoring.statsd.tcp_statsd_client', autospec=True, **kwargs)

    def test_udp_without_parameters(self):
        """Test udp without parameters"""
        with self.patch_udp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleFailJson) as result:
                set_module_args({})
                self.module.main()

    def test_tcp_without_parameters(self):
        """Test tcp without parameters"""
        with self.patch_tcp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleFailJson) as result:
                set_module_args({})
                self.module.main()

    def test_udp_with_parameters(self):
        """Test udp with parameters"""
        with self.patch_udp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'metric': 'my_counter',
                    'metric_type': 'counter',
                    'value': 1,
                })
                self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'Sent counter my_counter -> 1 to StatsD')
            self.assertEqual(result.exception.args[0]['changed'], True)
        with self.patch_udp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'metric': 'my_gauge',
                    'metric_type': 'gauge',
                    'value': 3,
                })
                self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'Sent gauge my_gauge -> 3 (delta=False) to StatsD')
            self.assertEqual(result.exception.args[0]['changed'], True)

    def test_tcp_with_parameters(self):
        """Test tcp with parameters"""
        with self.patch_tcp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'protocol': 'tcp',
                    'metric': 'my_counter',
                    'metric_type': 'counter',
                    'value': 1,
                })
                self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'Sent counter my_counter -> 1 to StatsD')
            self.assertEqual(result.exception.args[0]['changed'], True)
        with self.patch_tcp_statsd_client(side_effect=FakeStatsD) as fake_statsd:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'protocol': 'tcp',
                    'metric': 'my_gauge',
                    'metric_type': 'gauge',
                    'value': 3,
                })
                self.module.main()
            self.assertEqual(result.exception.args[0]['msg'], 'Sent gauge my_gauge -> 3 (delta=False) to StatsD')
            self.assertEqual(result.exception.args[0]['changed'], True)

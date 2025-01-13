# -*- coding: utf-8 -*-

# Copyright (c) 2020, Pavlo Bashynskyi (@levonet) <levonet@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.general.plugins.modules import redis_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class FakeRedisClient(MagicMock):

    def ping(self):
        pass

    def info(self):
        return {'redis_version': '999.999.999'}


class FakeRedisClientFail(MagicMock):

    def ping(self):
        raise Exception('Test Error')

    def info(self):
        pass


class TestRedisInfoModule(ModuleTestCase):

    def setUp(self):
        super(TestRedisInfoModule, self).setUp()
        redis_info.HAS_REDIS_PACKAGE = True
        self.module = redis_info

    def tearDown(self):
        super(TestRedisInfoModule, self).tearDown()

    def patch_redis_client(self, **kwds):
        return patch('ansible_collections.community.general.plugins.modules.redis_info.redis_client', autospec=True, **kwds)

    def test_without_parameters(self):
        """Test without parameters"""
        with self.patch_redis_client(side_effect=FakeRedisClient) as redis_client:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({})
                self.module.main()
            self.assertEqual(redis_client.call_count, 1)
            self.assertEqual(redis_client.call_args, ({'host': 'localhost',
                                                       'port': 6379,
                                                       'password': None,
                                                       'ssl': False,
                                                       'ssl_ca_certs': None,
                                                       'ssl_certfile': None,
                                                       'ssl_keyfile': None,
                                                       'ssl_cert_reqs': 'required'},))
            self.assertEqual(result.exception.args[0]['info']['redis_version'], '999.999.999')

    def test_with_parameters(self):
        """Test with all parameters"""
        with self.patch_redis_client(side_effect=FakeRedisClient) as redis_client:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'login_host': 'test',
                    'login_port': 1234,
                    'login_password': 'PASS'
                })
                self.module.main()
            self.assertEqual(redis_client.call_count, 1)
            self.assertEqual(redis_client.call_args, ({'host': 'test',
                                                       'port': 1234,
                                                       'password': 'PASS',
                                                       'ssl': False,
                                                       'ssl_ca_certs': None,
                                                       'ssl_certfile': None,
                                                       'ssl_keyfile': None,
                                                       'ssl_cert_reqs': 'required'},))
            self.assertEqual(result.exception.args[0]['info']['redis_version'], '999.999.999')

    def test_with_tls_parameters(self):
        """Test with tls parameters"""
        with self.patch_redis_client(side_effect=FakeRedisClient) as redis_client:
            with self.assertRaises(AnsibleExitJson) as result:
                set_module_args({
                    'login_host': 'test',
                    'login_port': 1234,
                    'login_password': 'PASS',
                    'tls': True,
                    'ca_certs': '/etc/ssl/ca.pem',
                    'client_cert_file': '/etc/ssl/client.pem',
                    'client_key_file': '/etc/ssl/client.key',
                    'validate_certs': False
                })
                self.module.main()
            self.assertEqual(redis_client.call_count, 1)
            self.assertEqual(redis_client.call_args, ({'host': 'test',
                                                       'port': 1234,
                                                       'password': 'PASS',
                                                       'ssl': True,
                                                       'ssl_ca_certs': '/etc/ssl/ca.pem',
                                                       'ssl_certfile': '/etc/ssl/client.pem',
                                                       'ssl_keyfile': '/etc/ssl/client.key',
                                                       'ssl_cert_reqs': None},))
            self.assertEqual(result.exception.args[0]['info']['redis_version'], '999.999.999')

    def test_with_fail_client(self):
        """Test failure message"""
        with self.patch_redis_client(side_effect=FakeRedisClientFail) as redis_client:
            with self.assertRaises(AnsibleFailJson) as result:
                set_module_args({})
                self.module.main()
            self.assertEqual(redis_client.call_count, 1)
            self.assertEqual(result.exception.args[0]['msg'], 'unable to connect to database: Test Error')

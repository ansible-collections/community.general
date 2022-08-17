# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import io
import json
import re
import uuid
from urllib3.response import HTTPResponse

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.community.general.plugins.modules.monitoring import circonus_annotation
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestCirconusAnnotation(ModuleTestCase):

    def setUp(self):
        super(TestCirconusAnnotation, self).setUp()
        self.module = circonus_annotation

    def tearDown(self):
        super(TestCirconusAnnotation, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_add_annotation(self):
        """Check that result is changed"""
        set_module_args({
            'category': 'test category',
            'description': 'test description',
            'title': 'test title',
            'api_key': str(uuid.uuid4()),
        })

        cid = '/annotation/100000'

        def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
            data = {
                '_cid': cid,
                '_created': 1502146995,
                '_last_modified': 1502146995,
                '_last_modified_by': '/user/1000',
                'category': 'test category',
                'description': 'test description',
                'rel_metrics': [],
                'start': 1502145480,
                'stop': None,
                'title': 'test title',
            }
            raw = to_bytes(json.dumps(data))
            resp = HTTPResponse(body=io.BytesIO(raw), preload_content=False)
            resp.status = 200
            resp.reason = 'OK'
            resp.headers = {'X-Circonus-API-Version': '2.00'}
            return self.build_response(request, resp)

        with patch('requests.adapters.HTTPAdapter.send', autospec=True, side_effect=send) as send:
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])
            self.assertEqual(result.exception.args[0]['annotation']['_cid'], cid)
        self.assertEqual(send.call_count, 1)

    def test_add_annotation_unicode(self):
        """Check that result is changed.
           Note: it seems there is a bug which prevent to create an annotation
           with a non-ASCII category if this category already exists, in such
           case an Internal Server Error (500) occurs."""
        set_module_args({
            'category': 'new catégorÿ',
            'description': 'test description',
            'title': 'test title',
            'api_key': str(uuid.uuid4()),
        })

        cid = '/annotation/100000'

        def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
            data = {
                '_cid': '/annotation/100000',
                '_created': 1502236928,
                '_last_modified': 1502236928,
                '_last_modified_by': '/user/1000',
                # use res['annotation']['category'].encode('latin1').decode('utf8')
                'category': u'new cat\xc3\xa9gor\xc3\xbf',
                'description': 'test description',
                'rel_metrics': [],
                'start': 1502236927,
                'stop': 1502236927,
                'title': 'test title',
            }

            raw = to_bytes(json.dumps(data), encoding='latin1')
            resp = HTTPResponse(body=io.BytesIO(raw), preload_content=False)
            resp.status = 200
            resp.reason = 'OK'
            resp.headers = {'X-Circonus-API-Version': '2.00'}
            return self.build_response(request, resp)

        with patch('requests.adapters.HTTPAdapter.send', autospec=True, side_effect=send) as send:
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])
            self.assertEqual(result.exception.args[0]['annotation']['_cid'], cid)
        self.assertEqual(send.call_count, 1)

    def test_auth_failure(self):
        """Check that an error is raised when authentication failed"""
        set_module_args({
            'category': 'test category',
            'description': 'test description',
            'title': 'test title',
            'api_key': str(uuid.uuid4()),
        })

        cid = '/annotation/100000'

        def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
            data = {
                '_cid': cid,
                '_created': 1502146995,
                '_last_modified': 1502146995,
                '_last_modified_by': '/user/1000',
                'category': 'test category',
                'description': 'test description',
                'rel_metrics': [],
                'start': 1502145480,
                'stop': None,
                'title': 'test title',
            }
            raw = to_bytes(json.dumps(data))
            resp = HTTPResponse(body=io.BytesIO(raw), preload_content=False)
            resp.status = 403
            resp.reason = 'Forbidden'
            resp.headers = {'X-Circonus-API-Version': '2.00'}
            return self.build_response(request, resp)

        with patch('requests.adapters.HTTPAdapter.send', autospec=True, side_effect=send) as send:
            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()
            self.assertTrue(result.exception.args[0]['failed'])
            self.assertTrue(re.match(r'\b403\b', result.exception.args[0]['reason']))
        self.assertEqual(send.call_count, 1)

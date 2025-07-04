# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import pagerduty_alert
import json
import pytest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class PagerDutyAlertsTest(unittest.TestCase):
    def _assert_incident_api(self, module, url, method, headers):
        self.assertTrue('https://api.pagerduty.com/incidents' in url, 'url must contain REST API v2 network path')
        self.assertTrue('service_ids%5B%5D=service_id' in url, 'url must contain service id to filter incidents')
        self.assertTrue('sort_by=incident_number%3Adesc' in url, 'url should contain sorting parameter')
        self.assertTrue('time_zone=UTC' in url, 'url should contain time zone parameter')
        return Response(), {'status': 200}

    def _assert_compatibility_header(self, module, url, method, headers):
        self.assertEqual(
            'application/vnd.pagerduty+json;version=2',
            headers.get('Accept'),
            'Accept:application/vnd.pagerduty+json;version=2 HTTP header not found'
        )
        return Response(), {'status': 200}

    def _assert_incident_key(self, module, url, method, headers):
        self.assertTrue('incident_key=incident_key_value' in url, 'url must contain incident key')
        return Response(), {'status': 200}

    def test_incident_url(self):
        pagerduty_alert.check(None, 'name', 'state', 'service_id', 'integration_key', 'api_key', http_call=self._assert_incident_api)

    def test_compatibility_header(self):
        pagerduty_alert.check(None, 'name', 'state', 'service_id', 'integration_key', 'api_key', http_call=self._assert_compatibility_header)

    def test_incident_key_in_url_when_it_is_given(self):
        pagerduty_alert.check(
            None, 'name', 'state', 'service_id', 'integration_key', 'api_key', incident_key='incident_key_value', http_call=self._assert_incident_key
        )


class Response(object):
    def read(self):
        return '{"incidents":[{"id": "incident_id", "status": "triggered"}]}'


class TestPagerDutyAlertModule(ModuleTestCase):
    def setUp(self):
        super(TestPagerDutyAlertModule, self).setUp()
        self.module = pagerduty_alert

    def tearDown(self):
        super(TestPagerDutyAlertModule, self).tearDown()

    @pytest.fixture
    def fetch_url_mock(self, mocker):
        return mocker.patch('ansible.module_utils.monitoring.pagerduty_change.fetch_url')

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_ensure_alert_created_with_minimal_data(self):
        with set_module_args({
            'state': 'triggered',
            'api_version': 'v2',
            'integration_key': 'test',
            'source': 'My Ansible Script',
            'desc': 'Description for alert'
        }):

            with patch.object(pagerduty_alert, 'fetch_url') as fetch_url_mock:
                fetch_url_mock.return_value = (Response(), {"status": 202})
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

            assert fetch_url_mock.call_count == 1
            url = fetch_url_mock.call_args[0][1]
            json_data = fetch_url_mock.call_args[1]['data']
            data = json.loads(json_data)

            assert url == 'https://events.pagerduty.com/v2/enqueue'
            assert data['routing_key'] == 'test'
            assert data['event_action'] == 'trigger'
            assert data['payload']['summary'] == 'Description for alert'
            assert data['payload']['source'] == 'My Ansible Script'
            assert data['payload']['severity'] == 'critical'
            assert data['payload']['timestamp'] is not None

    def test_ensure_alert_created_with_full_data(self):
        with set_module_args({
            'api_version': 'v2',
            'component': 'mysql',
            'custom_details': {'environment': 'production', 'notes': 'this is a test note'},
            'desc': 'Description for alert',
            'incident_class': 'ping failure',
            'integration_key': 'test',
            'link_url': 'https://pagerduty.com',
            'link_text': 'PagerDuty',
            'state': 'triggered',
            'source': 'My Ansible Script',
        }):

            with patch.object(pagerduty_alert, 'fetch_url') as fetch_url_mock:
                fetch_url_mock.return_value = (Response(), {"status": 202})
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

            assert fetch_url_mock.call_count == 1
            url = fetch_url_mock.call_args[0][1]
            json_data = fetch_url_mock.call_args[1]['data']
            data = json.loads(json_data)

            assert url == 'https://events.pagerduty.com/v2/enqueue'
            assert data['routing_key'] == 'test'
            assert data['payload']['summary'] == 'Description for alert'
            assert data['payload']['source'] == 'My Ansible Script'
            assert data['payload']['class'] == 'ping failure'
            assert data['payload']['component'] == 'mysql'
            assert data['payload']['custom_details']['environment'] == 'production'
            assert data['payload']['custom_details']['notes'] == 'this is a test note'
            assert data['links'][0]['href'] == 'https://pagerduty.com'
            assert data['links'][0]['text'] == 'PagerDuty'

    def test_ensure_alert_acknowledged(self):
        with set_module_args({
            'state': 'acknowledged',
            'api_version': 'v2',
            'integration_key': 'test',
            'incident_key': 'incident_test_id',
        }):

            with patch.object(pagerduty_alert, 'fetch_url') as fetch_url_mock:
                fetch_url_mock.return_value = (Response(), {"status": 202})
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

            assert fetch_url_mock.call_count == 1
            url = fetch_url_mock.call_args[0][1]
            json_data = fetch_url_mock.call_args[1]['data']
            data = json.loads(json_data)

            assert url == 'https://events.pagerduty.com/v2/enqueue'
            assert data['routing_key'] == 'test'
            assert data['event_action'] == 'acknowledge'
            assert data['dedup_key'] == 'incident_test_id'

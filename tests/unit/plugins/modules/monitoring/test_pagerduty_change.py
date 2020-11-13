# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)from __future__ import (absolute_import, division, print_function)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules.monitoring import pagerduty_change
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestPagerDutyChangeModule(ModuleTestCase):
    def setUp(self):
        super(TestPagerDutyChangeModule, self).setUp()
        self.module = pagerduty_change

    def tearDown(self):
        super(TestPagerDutyChangeModule, self).tearDown()

    @pytest.fixture
    def fetch_url_mock(self, mocker):
        return mocker.patch('ansible.module_utils.monitoring.pagerduty_change.fetch_url')

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_ensure_change_event_created_with_minimal_data(self):
        set_module_args({
            'integration_key': 'test',
            'summary': 'Testing'
        })

        with patch.object(pagerduty_change, 'fetch_url') as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 202})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            assert fetch_url_mock.call_count == 1
            url = fetch_url_mock.call_args[0][1]
            json_data = fetch_url_mock.call_args[1]['data']
            data = json.loads(json_data)

            assert url == 'https://events.pagerduty.com/v2/change/enqueue'
            assert data['routing_key'] == 'test'
            assert data['payload']['summary'] == 'Testing'
            assert data['payload']['source'] == 'Ansible'

    def test_ensure_change_event_created_with_full_data(self):
        set_module_args({
            'integration_key': 'test',
            'summary': 'Testing',
            'source': 'My Ansible Script',
            'user': 'ansible',
            'repo': 'github.com/ansible/ansible',
            'revision': '8c67432',
            'environment': 'production',
            'link_url': 'https://pagerduty.com',
            'link_text': 'PagerDuty'
        })

        with patch.object(pagerduty_change, 'fetch_url') as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 202})
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            assert fetch_url_mock.call_count == 1
            url = fetch_url_mock.call_args[0][1]
            json_data = fetch_url_mock.call_args[1]['data']
            data = json.loads(json_data)

            assert url == 'https://events.pagerduty.com/v2/change/enqueue'
            assert data['routing_key'] == 'test'
            assert data['payload']['summary'] == 'Testing'
            assert data['payload']['source'] == 'My Ansible Script'
            assert data['payload']['custom_details']['user'] == 'ansible'
            assert data['payload']['custom_details']['repo'] == 'github.com/ansible/ansible'
            assert data['payload']['custom_details']['revision'] == '8c67432'
            assert data['payload']['custom_details']['environment'] == 'production'
            assert data['links'][0]['href'] == 'https://pagerduty.com'
            assert data['links'][0]['text'] == 'PagerDuty'

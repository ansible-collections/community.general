# (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.general.plugins.module_utils.hetzner import BASE_URL
from ansible_collections.community.general.plugins.modules.net_tools import hetzner_failover_ip_info


class TestHetznerFailoverIPInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.general.plugins.modules.net_tools.hetzner_failover_ip_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.general.plugins.module_utils.hetzner.fetch_url'

    # Tests for state (routed and unrouted)

    def test_unrouted(self, mocker):
        result = self.run_module_success(mocker, hetzner_failover_ip_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': None,
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['value'] is None
        assert result['state'] == 'unrouted'
        assert result['failover_ip'] == '1.2.3.4'
        assert result['server_ip'] == '2.3.4.5'
        assert result['server_number'] == 2345

    def test_routed(self, mocker):
        result = self.run_module_success(mocker, hetzner_failover_ip_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'
        assert result['failover_ip'] == '1.2.3.4'
        assert result['server_ip'] == '2.3.4.5'
        assert result['server_number'] == 2345

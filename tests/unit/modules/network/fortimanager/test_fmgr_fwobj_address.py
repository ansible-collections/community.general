# Copyright 2018 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
from ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager import FortiManagerHandler
import pytest

try:
    from ansible_collections.community.general.plugins.modules.network.fortimanager import fmgr_fwobj_address
except ImportError:
    pytest.skip("Could not load required modules for testing", allow_module_level=True)


def load_fixtures():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures') + "/{filename}.json".format(
        filename=os.path.splitext(os.path.basename(__file__))[0])
    try:
        with open(fixture_path, "r") as fixture_file:
            fixture_data = json.load(fixture_file)
    except IOError:
        return []
    return [fixture_data]


@pytest.fixture(autouse=True)
def module_mock(mocker):
    connection_class_mock = mocker.patch('ansible.module_utils.basic.AnsibleModule')
    return connection_class_mock


@pytest.fixture(autouse=True)
def connection_mock(mocker):
    connection_class_mock = mocker.patch('ansible_collections.community.general.plugins.modules.network.fortimanager.fmgr_fwobj_address.Connection')
    return connection_class_mock


@pytest.fixture(scope="function", params=load_fixtures())
def fixture_data(request):
    func_name = request.function.__name__.replace("test_", "")
    return request.param.get(func_name, None)


fmg_instance = FortiManagerHandler(connection_mock, module_mock)


def test_fmgr_fwobj_ipv4(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)

    # Test using fixture 1 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 2 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[1]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 3 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[2]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 4 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[3]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 5 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[4]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 6 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[5]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 7 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[6]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 8 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[7]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 9 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[8]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 10 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[9]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 11 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[10]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 12 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[11]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 13 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[12]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 14 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[13]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 15 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[14]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 16 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[15]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 17 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[16]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 18 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv4(fmg_instance, fixture_data[17]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0


def test_fmgr_fwobj_ipv6(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)

    # Test using fixture 1 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv6(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 2 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv6(fmg_instance, fixture_data[1]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -3
    # Test using fixture 3 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv6(fmg_instance, fixture_data[2]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 4 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv6(fmg_instance, fixture_data[3]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 5 #
    output = fmgr_fwobj_address.fmgr_fwobj_ipv6(fmg_instance, fixture_data[4]['paramgram_used'])
    assert output['raw_response']['status']['code'] == -10131


def test_fmgr_fwobj_multicast(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)

    # Test using fixture 1 #
    output = fmgr_fwobj_address.fmgr_fwobj_multicast(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 2 #
    output = fmgr_fwobj_address.fmgr_fwobj_multicast(fmg_instance, fixture_data[1]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 3 #
    output = fmgr_fwobj_address.fmgr_fwobj_multicast(fmg_instance, fixture_data[2]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0

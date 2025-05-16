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
    from ansible_collections.community.general.plugins.modules.network.fortimanager import fmgr_device_config
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
    connection_class_mock = mocker.patch('ansible_collections.community.general.plugins.modules.network.fortimanager.fmgr_device_config.Connection')
    return connection_class_mock


@pytest.fixture(scope="function", params=load_fixtures())
def fixture_data(request):
    func_name = request.function.__name__.replace("test_", "")
    return request.param.get(func_name, None)


fmg_instance = FortiManagerHandler(connection_mock, module_mock)


def test_update_device_hostname(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # adom: ansible
    # interface: None
    # device_unique_name: FGT1
    # install_config: disable
    # device_hostname: ansible-fgt01
    # interface_ip: None
    # interface_allow_access: None
    # mode: update
    ##################################################
    ##################################################
    # adom: ansible
    # interface: None
    # device_unique_name: FGT2
    # install_config: disable
    # device_hostname: ansible-fgt02
    # interface_ip: None
    # interface_allow_access: None
    # mode: update
    ##################################################
    ##################################################
    # adom: ansible
    # interface: None
    # device_unique_name: FGT3
    # install_config: disable
    # device_hostname: ansible-fgt03
    # interface_ip: None
    # interface_allow_access: None
    # mode: update
    ##################################################

    # Test using fixture 1 #
    output = fmgr_device_config.update_device_hostname(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 2 #
    output = fmgr_device_config.update_device_hostname(fmg_instance, fixture_data[1]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 3 #
    output = fmgr_device_config.update_device_hostname(fmg_instance, fixture_data[2]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0


def test_update_device_interface(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # adom: ansible
    # install_config: disable
    # device_unique_name: FGT1
    # interface: port2
    # device_hostname: None
    # interface_ip: 10.1.1.1/24
    # interface_allow_access: ping, telnet, https, http
    # mode: update
    ##################################################
    ##################################################
    # adom: ansible
    # install_config: disable
    # device_unique_name: FGT2
    # interface: port2
    # device_hostname: None
    # interface_ip: 10.1.2.1/24
    # interface_allow_access: ping, telnet, https, http
    # mode: update
    ##################################################
    ##################################################
    # adom: ansible
    # install_config: disable
    # device_unique_name: FGT3
    # interface: port2
    # device_hostname: None
    # interface_ip: 10.1.3.1/24
    # interface_allow_access: ping, telnet, https, http
    # mode: update
    ##################################################

    # Test using fixture 1 #
    output = fmgr_device_config.update_device_interface(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 2 #
    output = fmgr_device_config.update_device_interface(fmg_instance, fixture_data[1]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0
    # Test using fixture 3 #
    output = fmgr_device_config.update_device_interface(fmg_instance, fixture_data[2]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0


def test_exec_config(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # adom: ansible
    # interface: None
    # device_unique_name: FGT1
    # install_config: enable
    # device_hostname: None
    # interface_ip: None
    # interface_allow_access: None
    # mode: exec
    ##################################################
    ##################################################
    # adom: ansible
    # install_config: enable
    # device_unique_name: FGT2, FGT3
    # interface: None
    # device_hostname: None
    # interface_ip: None
    # interface_allow_access: None
    # mode: exec
    ##################################################

    # Test using fixture 1 #
    output = fmgr_device_config.exec_config(fmg_instance, fixture_data[0]['paramgram_used'])
    assert isinstance(output['raw_response'], dict) is True
    # Test using fixture 2 #
    output = fmgr_device_config.exec_config(fmg_instance, fixture_data[1]['paramgram_used'])
    assert isinstance(output['raw_response'], dict) is True

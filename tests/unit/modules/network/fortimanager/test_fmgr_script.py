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
    from ansible_collections.community.general.plugins.modules.network.fortimanager import fmgr_script
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
    connection_class_mock = mocker.patch('ansible_collections.community.general.plugins.modules.network.fortimanager.fmgr_script.Connection')
    return connection_class_mock


@pytest.fixture(scope="function", params=load_fixtures())
def fixture_data(request):
    func_name = request.function.__name__.replace("test_", "")
    return request.param.get(func_name, None)


fmg_instance = FortiManagerHandler(connection_mock, module_mock)


def test_set_script(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # script_content: get system status
    # adom: ansible
    # script_scope: None
    # script_name: TestScript
    # script_target: remote_device
    # mode: set
    # script_description: Create by Ansible
    # script_package: None
    # vdom: root
    # script_type: cli
    ##################################################

    # Test using fixture 1 #
    output = fmgr_script.set_script(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0


def test_delete_script(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # vdom: root
    # script_target: None
    # script_content: None
    # adom: ansible
    # script_description: None
    # script_package: None
    # mode: delete
    # script_scope: None
    # script_name: TestScript
    # script_type: None
    ##################################################

    # Test using fixture 1 #
    output = fmgr_script.delete_script(fmg_instance, fixture_data[0]['paramgram_used'])
    assert output['raw_response']['status']['code'] == 0


def test_execute_script(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # script_content: None
    # adom: ansible
    # script_scope: FGT1
    # script_name: TestScript
    # script_target: None
    # mode: exec
    # script_description: None
    # script_package: None
    # vdom: root
    # script_type: None
    ##################################################

    # Test using fixture 1 #
    output = fmgr_script.execute_script(fmg_instance, fixture_data[0]['paramgram_used'])
    assert isinstance(output['raw_response'], dict) is True

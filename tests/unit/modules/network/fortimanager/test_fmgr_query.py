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
    from ansible_collections.community.general.plugins.modules.network.fortimanager import fmgr_query
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
    connection_class_mock = mocker.patch('ansible_collections.community.general.plugins.modules.network.fortimanager.fmgr_query.Connection')
    return connection_class_mock


@pytest.fixture(scope="function", params=load_fixtures())
def fixture_data(request):
    func_name = request.function.__name__.replace("test_", "")
    return request.param.get(func_name, None)


fmg_instance = FortiManagerHandler(connection_mock, module_mock)


def test_fmgr_get_custom(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # custom_endpoint: /dvmdb/adom/ansible/script
    # device_ip: None
    # device_unique_name: None
    # task_id: None
    # adom: ansible
    # nodes: None
    # object: custom
    # device_serial: None
    # custom_dict: {'type': 'cli'}
    # mode: get
    ##################################################

    # Test using fixture 1 #
    output = fmgr_query.fmgr_get_custom(fmg_instance, fixture_data[0]['paramgram_used'])
    assert isinstance(output['raw_response'], list) is True


def test_fmgr_get_task_status(fixture_data, mocker):
    mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortimanager.fortimanager.FortiManagerHandler.process_request',
                 side_effect=fixture_data)
    #  Fixture sets used:###########################

    ##################################################
    # custom_endpoint: None
    # object: task
    # task_id: 247
    # adom: ansible
    # device_ip: None
    # custom_dict: None
    # device_unique_name: None
    # nodes: None
    # device_serial: None
    # mode: get
    ##################################################

    # Test using fixture 1 #
    output = fmgr_query.fmgr_get_task_status(fmg_instance, fixture_data[0]['paramgram_used'])
    assert isinstance(output['raw_response'], dict) is True

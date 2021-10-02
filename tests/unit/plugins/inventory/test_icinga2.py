# -*- coding: utf-8 -*-
# Copyright (c) 2021, Cliff Hults <cliff.hlts@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# The API responses used in these tests were recorded from PVE version 6.2.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.icinga2 import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.icinga2.yml') is False


def check_api():
    return True


# NOTE: when updating/adding replies to this function,
# be sure to only add only the _contents_ of the 'data' dict in the API reply
def query_hosts(hosts=None, attrs=None, joins=None, host_filter=None):
    # _get_hosts - list of dicts
    json_host_data = [
        {
            'attrs': {
                'address': 'test-host1.home.local',
                'groups': ['home_servers', 'servers_dell'],
                'state': 0.0,
                'state_type': 1.0
            },
            'joins': {},
            'meta': {},
            'name': 'test-host1',
            'type': 'Host'
        },
        {
            'attrs': {
                'address': 'test-host2.home.local',
                'groups': ['home_servers', 'servers_hp'],
                'state': 1.0,
                'state_type': 1.0
            },
            'joins': {},
            'meta': {},
            'name': 'test-host2',
            'type': 'Host'
        }
    ]
    return json_host_data


def test_populate(inventory, mocker):
    # module settings
    inventory.icinga2_user = 'ansible'
    inventory.icinga2_password = 'password'
    inventory.icinga2_url = 'https://localhost:5665' + '/v1'

    # bypass authentication and API fetch calls
    inventory._check_api = mocker.MagicMock(side_effect=check_api)
    inventory._query_hosts = mocker.MagicMock(side_effect=query_hosts)
    inventory._populate()

    # get different hosts
    host1_info = inventory.inventory.get_host('test-host1.home.local')
    print(host1_info)
    host2_info = inventory.inventory.get_host('test-host2.home.local')
    print(host2_info)

    # check if host in the home_servers group
    assert 'home_servers' in inventory.inventory.groups
    group1_data = inventory.inventory.groups['home_servers']
    group1_test_data = [host1_info, host2_info]
    print(group1_data.hosts)
    print(group1_test_data)
    assert group1_data.hosts == group1_test_data
    # Test servers_hp group
    group2_data = inventory.inventory.groups['servers_hp']
    group2_test_data = [host2_info]
    print(group2_data.hosts)
    print(group2_test_data)
    assert group2_data.hosts == group2_test_data

    # check if host state rules apply properyl
    assert host1_info.get_vars()['state'] == 'on'
    assert host2_info.get_vars()['state'] == 'off'

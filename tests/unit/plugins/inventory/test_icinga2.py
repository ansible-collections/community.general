# -*- coding: utf-8 -*-
# Copyright (c) 2020, Jeffrey van Pelt <jeff@vanpelt.one>
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
def query_hosts(attrs):
    # _get_hosts
    json_host_data = {
        [
            {
                'attrs': {
                    'address': 'test-host1.home.local',
                    'groups': ['home-servers', 'servers-dell'],
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
                    'groups': ['home-servers', 'servers-hp'],
                    'state': 1.0,
                    'state_type': 1.0
                },
                'joins': {},
                'meta': {},
                'name': 'test-host2',
                'type': 'Host'
            }
        ]
    }
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
    host_info1 = inventory.inventory.get_host('test-host1')
    host_info2 = inventory.inventory.get_host('test-host2')

    # check if host in the home-servers group
    assert 'home-servers' in inventory.inventory.groups
    group_data = inventory.inventory.groups['home-servers']
    assert 'test-host1' in group_data.hosts

    # check if host state rules apply properyl
    assert host_info1.get_vars()['state'] == 'on'
    assert host_info2.get_vars()['state'] == 'off'

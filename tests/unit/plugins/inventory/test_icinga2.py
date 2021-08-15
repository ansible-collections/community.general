# -*- coding: utf-8 -*-
# Copyright (c) 2020, Jeffrey van Pelt <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# The API responses used in these tests were recorded from PVE version 6.2.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.icinga2 import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.icinga2.yml') is False


def get_auth():
    return True


# NOTE: when updating/adding replies to this function,
# be sure to only add only the _contents_ of the 'data' dict in the API reply
def get_json(url):
    if url == "https://localhost:8006/v1/objects/hosts":
        # _get_nodes
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
                        'address': 'test-host2.home.local'
                        'groups': ['home-servers', 'servers-hp'],
                        'state': 0.0,
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
    inventory._get_auth = mocker.MagicMock(side_effect=get_auth)
    inventory._get_json = mocker.MagicMock(side_effect=get_json)
    inventory._get_vm_status = mocker.MagicMock(side_effect=get_vm_status)
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory._populate()

    # get different hosts
    host_qemu = inventory.inventory.get_host('test-qemu')
    host_qemu_windows = inventory.inventory.get_host('test-qemu-windows')
    host_qemu_multi_nic = inventory.inventory.get_host('test-qemu-multi-nic')
    host_qemu_template = inventory.inventory.get_host('test-qemu-template')
    host_lxc = inventory.inventory.get_host('test-lxc')
    host_node = inventory.inventory.get_host('testnode')

    # check if qemu-test is in the icinga2_pool_test group
    assert 'icinga2_pool_test' in inventory.inventory.groups
    group_qemu = inventory.inventory.groups['icinga2_pool_test']
    assert group_qemu.hosts == [host_qemu]

    # check if qemu-test has eth0 interface in agent_interfaces fact
    assert 'eth0' in [d['name'] for d in host_qemu.get_vars()['icinga2_agent_interfaces']]

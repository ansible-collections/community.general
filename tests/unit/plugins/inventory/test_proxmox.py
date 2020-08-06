# -*- coding: utf-8 -*-
# Copyright (c) 2020, Robert Kaussow <mail@thegeeklab.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.inventory.proxmox import InventoryModule


@pytest.fixture
def inventory():
    return InventoryModule()


def test_get_nodes(inventory):
    nodes = [{
        'status': 'online',
        'type': 'node',
        'id': 'node/testnode',
        'node': 'testnode'
    }]

    assert ['testnode'] == inventory._get_nodes(nodes, 'node')

def test_get_pools(inventory):
    pools = [{'poolid': 'testpool'}]

    assert ['testpool'] == inventory._get_pools(pools, 'pool')

def test_get_vm_info(inventory):
    pve_list = [{
        'vmid': '100',
        'name': 'test',
        'status': 'running',
    }]

    config_variables = {
        'test': {
            'proxmox_vmid': '100',
            'proxmox_name': 'test',
        }
    }

    config_variables = {
        'test': {
            'proxmox_status': 'running',
        }
    }

    assert config_variables == inventory._get_vm_config(pve_list, 'localhost', 'lxc', 100, 'test')
    assert status_variables == inventory._get_vm_status(pve_list, 'localhost', 'lxc', 100, 'test')


def test_get_ip_address(inventory, mocker):
    networks = {
        'result': [{
            'ip-addresses': [{
                'ip-address': '10.0.0.1',
                'prefix': 26,
                'ip-address-type': 'ipv4'
            }],
            'name':
            'eth0'
        }]
    }
    inventory.client = mocker.MagicMock()
    inventory.client.nodes.return_value.get.return_value = networks

    assert '10.0.0.1' == inventory._get_ip_address('qemu', None, None)


def test_exclude(inventory, mocker):
    def get_option(name, *args, **kwargs):
        if name == 'exclude_state':
            return ['stopped']

        return []

    inventory.get_option = mocker.MagicMock(side_effect=get_option)

    pve_list = [{
        'status': 'running',
        'vmid': '100',
        'name': 'test',
    }, {
        'status': 'stopped',
        'vmid': '101',
        'name': 'stop',
    }]

    filtered = [{
        'status': 'running',
        'vmid': '100',
        'name': 'test',
    }]

    assert filtered == inventory._exclude(pve_list)

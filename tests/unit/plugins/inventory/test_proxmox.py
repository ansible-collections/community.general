# -*- coding: utf-8 -*-
# Copyright (c) 2020, Robert Kaussow <mail@thegeeklab.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

proxmox = pytest.importorskip('proxmoxer')

from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.inventory.proxmox import InventoryModule


@pytest.fixture
def inventory():
    return InventoryModule()


def test_get_names(inventory):
    nodes = [{
        'status': 'online',
        'type': 'node',
        'id': 'node/testnode',
        'node': 'testnode'
    }]
    pools = [{'poolid': 'testpool'}]

    assert ['testnode'] == inventory._get_names(nodes, 'node')
    assert ['testpool'] == inventory._get_names(pools, 'pool')


def test_get_variables(inventory):
    pve_list = [{
        'status': 'running',
        'vmid': '100',
        'name': 'test',
    }]

    variables = {
        'test': {
            'proxmox_status': 'running',
            'proxmox_vmid': '100',
            'proxmox_name': 'test',
        }
    }

    assert variables == inventory._get_variables(pve_list, 'qemu')


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

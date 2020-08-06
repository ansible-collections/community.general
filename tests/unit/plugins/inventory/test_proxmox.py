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


def test_get_nodes(inventory, mocker):
    nodes = [{
        'status': 'online',
        'type': 'node',
        'id': 'node/testnode',
        'node': 'testnode'
    }]

    inventory.client = mocker.MagicMock()
    inventory.client.nodes.return_value.get.return_value = nodes
    assert ['testnode'] == inventory._get_nodes()
#
#
#def test_get_pools(inventory):
#    pools = [{'poolid': 'testpool'}]
#
#    assert ['testpool'] == inventory._get_pools(pools)
#
#
#def test_get_vm_info(inventory):
#    pve_list = [{
#        'vmid': '100',
#        'name': 'test',
#        'status': 'running',
#    }]
#
#    config_variables = {
#        'test': {
#            'proxmox_vmid': '100',
#            'proxmox_name': 'test',
#        }
#    }
#
#    config_variables = {
#        'test': {
#            'proxmox_status': 'running',
#        }
#    }
#
#    assert config_variables == inventory._get_vm_config(pve_list, 'localhost', 'lxc', 100)
#    assert status_variables == inventory._get_vm_status(pve_list, 'localhost', 'lxc', 100)

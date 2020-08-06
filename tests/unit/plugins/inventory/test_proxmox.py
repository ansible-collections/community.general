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

def test_populate(inventory, mocker):
    def get_auth():
        return True


    def get_option(name, *args, **kwargs):
        return ['proxmox_']


    def get_nodes():
        return { "data": [
            {
                "type": "node",
                "cpu": 0.01,
                "maxdisk": 500,
                "mem": 500,
                "node": "testnode",
                "id": "node/testnode",
                "maxcpu": 1,
                "status": "online",
                "ssl_fingerprint": "xx",
                "disk": 1000,
                "maxmem": 1000,
                "uptime": 10000,
                "level": "" } ]
            }


    def get_pools():
        return {"data":[{"poolid":"test"}]}


    def get_lxc_per_node():
        return { "data": [
            {
                "cpus": 1,
                "name": "test",
                "cpu": 0.01,
                "diskwrite": 0,
                "lock": "",
                "maxmem": 1000,
                "template": "",
                "diskread": 0,
                "mem": 1000,
                "swap": 0,
                "type": "lxc",
                "maxswap": 0,
                "maxdisk": "1000",
                "netout": 1000,
                "pid": "1000",
                "netin": 1000,
                "status": "running",
                "vmid": "100",
                "disk": "1000",
                "uptime": 1000 } ]
            }


    def get_qemu_per_node():
        return { "data": [
            {
                "name": "test-qemu",
                "cpus": 1,
                "mem": 1000,
                "template": "",
                "diskread": 0,
                "cpu": 0.01,
                "maxmem": 1000,
                "diskwrite": 0,
                "netout": 1000,
                "pid": "1001",
                "netin": 1000,
                "maxdisk": 1000,
                "vmid": "101",
                "uptime": 1000,
                "disk": 0,
                "status": "running" } ]
            }


    # module settings
    inventory._options['group_prefix'] = 'proxmox_'
    inventory._options['facts_prefix'] = 'proxmox_'

    # bypass authentication
    inventory._get_auth = mocker.MagicMock(side_effect=get_auth)

    # bypass fetch calls and feed fake replies (see above)
    inventory._get_option = mocker.MagicMock(side_effect=get_option)
    inventory._get_nodes = mocker.MagicMock(side_effect=get_nodes)

    # build inventory, breaks on missing add_group functions
    inventory._populate()

    # always fail for now
    assert 0

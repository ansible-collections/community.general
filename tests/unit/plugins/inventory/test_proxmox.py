# -*- coding: utf-8 -*-
# Copyright (c) 2020, Robert Kaussow <mail@thegeeklab.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.proxmox import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.proxmox.yml') is False


def get_auth():
    return True


def get_nodes():
    return [{"type": "node",
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
             "level": ""}]


def get_pools():
    return [{"poolid": "test"}]


def get_lxc_per_node(node):
    return [{"cpus": 1,
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
             "uptime": 1000}]


def get_qemu_per_node(node):
    return [{"name": "test-qemu",
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
             "status": "running"}]


def get_members_per_pool(pool):
    return [{"uptime": 1000,
             "template": 0,
             "id": "qemu/101",
             "mem": 1000,
             "status": "running",
             "cpu": 0.01,
             "maxmem": 1000,
             "diskwrite": 1000,
             "name": "test-qemu",
             "netout": 1000,
             "netin": 1000,
             "vmid": 101,
             "node": "testnode",
             "maxcpu": 1,
             "type": "qemu",
             "maxdisk": 1000,
             "disk": 0,
             "diskread": 1000}]


def get_node_ip(node):
    return [{"families": ["inet"],
             "priority": 3,
             "active": 1,
             "cidr": "10.1.1.2/24",
             "iface": "eth0",
             "method": "static",
             "exists": 1,
             "type": "eth",
             "netmask": "24",
             "gateway": "10.1.1.1",
             "address": "10.1.1.2",
             "method6": "manual",
             "autostart": 1},
            {"method6": "manual",
             "autostart": 1,
             "type": "OVSPort",
             "exists": 1,
             "method": "manual",
             "iface": "eth1",
             "ovs_bridge": "vmbr0",
             "active": 1,
             "families": ["inet"],
             "priority": 5,
             "ovs_type": "OVSPort"},
            {"type": "OVSBridge",
             "method": "manual",
             "iface": "vmbr0",
             "families": ["inet"],
             "priority": 4,
             "ovs_ports": "eth1",
             "ovs_type": "OVSBridge",
             "method6": "manual",
             "autostart": 1,
             "active": 1}]


def get_vm_status(node, vmtype, vmid, name):
    return True


def get_option(option):
    if option == 'group_prefix':
        return 'proxmox_'
    else:
        return False


def test_populate(inventory, mocker):
    # module settings
    inventory.proxmox_user = 'root@pam'
    inventory.proxmox_password = 'password'
    inventory.proxmox_url = 'https://localhost:8006'

    # bypass authentication and API fetch calls
    inventory._get_auth = mocker.MagicMock(side_effect=get_auth)
    inventory._get_nodes = mocker.MagicMock(side_effect=get_nodes)
    inventory._get_pools = mocker.MagicMock(side_effect=get_pools)
    inventory._get_lxc_per_node = mocker.MagicMock(side_effect=get_lxc_per_node)
    inventory._get_qemu_per_node = mocker.MagicMock(side_effect=get_qemu_per_node)
    inventory._get_members_per_pool = mocker.MagicMock(side_effect=get_members_per_pool)
    inventory._get_node_ip = mocker.MagicMock(side_effect=get_node_ip)
    inventory._get_vm_status = mocker.MagicMock(side_effect=get_vm_status)
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory._populate()

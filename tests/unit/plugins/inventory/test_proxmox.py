# -*- coding: utf-8 -*-
# Copyright (c) 2020, Jeffrey van Pelt <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The API responses used in these tests were recorded from PVE version 6.2.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.proxmox import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.proxmox.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.proxmox.yml') is False


def get_auth():
    return True


# NOTE: when updating/adding replies to this function,
# be sure to only add only the _contents_ of the 'data' dict in the API reply
def get_json(url):
    if url == "https://localhost:8006/api2/json/nodes":
        # _get_nodes
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
                 "level": ""},
                {"type": "node",
                 "node": "testnode2",
                 "id": "node/testnode2",
                 "status": "offline",
                 "ssl_fingerprint": "yy"}]
    elif url == "https://localhost:8006/api2/json/pools":
        # _get_pools
        return [{"poolid": "test"}]
    elif url == "https://localhost:8006/api2/json/nodes/testnode/lxc":
        # _get_lxc_per_node
        return [{"cpus": 1,
                 "name": "test-lxc",
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
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu":
        # _get_qemu_per_node
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
                 "status": "running"},
                {"name": "test-qemu-windows",
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
                 "vmid": "102",
                 "uptime": 1000,
                 "disk": 0,
                 "status": "running"},
                {"name": "test-qemu-multi-nic",
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
                 "vmid": "103",
                 "uptime": 1000,
                 "disk": 0,
                 "status": "running"},
                {"name": "test-qemu-template",
                 "cpus": 1,
                 "mem": 0,
                 "template": 1,
                 "diskread": 0,
                 "cpu": 0,
                 "maxmem": 1000,
                 "diskwrite": 0,
                 "netout": 0,
                 "pid": "1001",
                 "netin": 0,
                 "maxdisk": 1000,
                 "vmid": "9001",
                 "uptime": 0,
                 "disk": 0,
                 "status": "stopped"}]
    elif url == "https://localhost:8006/api2/json/pools/test":
        # _get_members_per_pool
        return {"members": [{"uptime": 1000,
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
                             "diskread": 1000}]}
    elif url == "https://localhost:8006/api2/json/nodes/testnode/network":
        # _get_node_ip
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
    elif url == "https://localhost:8006/api2/json/nodes/testnode/lxc/100/config":
        # _get_vm_config (lxc)
        return {
            "console": 1,
            "rootfs": "local-lvm:vm-100-disk-0,size=4G",
            "cmode": "tty",
            "description": "A testnode",
            "cores": 1,
            "hostname": "test-lxc",
            "arch": "amd64",
            "tty": 2,
            "swap": 0,
            "cpulimit": "0",
            "net0": "name=eth0,bridge=vmbr0,gw=10.1.1.1,hwaddr=FF:FF:FF:FF:FF:FF,ip=10.1.1.3/24,type=veth",
            "ostype": "ubuntu",
            "digest": "123456789abcdef0123456789abcdef01234567890",
            "protection": 0,
            "memory": 1000,
            "onboot": 0,
            "cpuunits": 1024,
            "tags": "one, two, three",
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/101/config":
        # _get_vm_config (qemu)
        return {
            "tags": "one, two, three",
            "cores": 1,
            "ide2": "none,media=cdrom",
            "memory": 1000,
            "kvm": 1,
            "digest": "0123456789abcdef0123456789abcdef0123456789",
            "description": "A test qemu",
            "sockets": 1,
            "onboot": 1,
            "vmgenid": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "numa": 0,
            "bootdisk": "scsi0",
            "cpu": "host",
            "name": "test-qemu",
            "ostype": "l26",
            "hotplug": "network,disk,usb",
            "scsi0": "local-lvm:vm-101-disk-0,size=8G",
            "net0": "virtio=ff:ff:ff:ff:ff:ff,bridge=vmbr0,firewall=1",
            "agent": "1,fstrim_cloned_disks=1",
            "bios": "seabios",
            "ide0": "local-lvm:vm-101-cloudinit,media=cdrom,size=4M",
            "boot": "cdn",
            "scsihw": "virtio-scsi-pci",
            "smbios1": "uuid=ffffffff-ffff-ffff-ffff-ffffffffffff"
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/102/config":
        # _get_vm_config (qemu)
        return {
            "numa": 0,
            "digest": "460add1531a7068d2ae62d54f67e8fb9493dece9",
            "ide2": "none,media=cdrom",
            "bootdisk": "sata0",
            "name": "test-qemu-windows",
            "balloon": 0,
            "cpulimit": "4",
            "agent": "1",
            "cores": 6,
            "sata0": "storage:vm-102-disk-0,size=100G",
            "memory": 10240,
            "smbios1": "uuid=127301fc-0122-48d5-8fc5-c04fa78d8146",
            "scsihw": "virtio-scsi-pci",
            "sockets": 1,
            "ostype": "win8",
            "net0": "virtio=ff:ff:ff:ff:ff:ff,bridge=vmbr0",
            "onboot": 1
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/103/config":
        # _get_vm_config (qemu)
        return {
            'scsi1': 'storage:vm-103-disk-3,size=30G',
            'sockets': 1,
            'memory': 8192,
            'ostype': 'l26',
            'scsihw': 'virtio-scsi-pci',
            "net0": "virtio=ff:ff:ff:ff:ff:ff,bridge=vmbr0",
            "net1": "virtio=ff:ff:ff:ff:ff:ff,bridge=vmbr1",
            'bootdisk': 'scsi0',
            'scsi0': 'storage:vm-103-disk-0,size=10G',
            'name': 'test-qemu-multi-nic',
            'cores': 4,
            'digest': '51b7599f869b9a3f564804a0aed290f3de803292',
            'smbios1': 'uuid=863b31c3-42ca-4a92-aed7-4111f342f70a',
            'agent': '1,type=virtio',
            'ide2': 'none,media=cdrom',
            'balloon': 0,
            'numa': 0,
            'scsi2': 'storage:vm-103-disk-2,size=10G',
            'serial0': 'socket',
            'vmgenid': 'ddfb79b2-b484-4d66-88e7-6e76f2d1be77',
            'onboot': 1,
            'tablet': 0
        }

    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/101/agent/network-get-interfaces":
        # _get_agent_network_interfaces
        return {"result": [
            {
                "hardware-address": "00:00:00:00:00:00",
                "ip-addresses": [
                    {
                        "prefix": 8,
                        "ip-address-type": "ipv4",
                        "ip-address": "127.0.0.1"
                    },
                    {
                        "ip-address-type": "ipv6",
                        "ip-address": "::1",
                        "prefix": 128
                    }],
                "statistics": {
                    "rx-errs": 0,
                    "rx-bytes": 163244,
                    "rx-packets": 1623,
                    "rx-dropped": 0,
                    "tx-dropped": 0,
                    "tx-packets": 1623,
                    "tx-bytes": 163244,
                    "tx-errs": 0},
                "name": "lo"},
            {
                "statistics": {
                    "rx-packets": 4025,
                    "rx-dropped": 12,
                    "rx-bytes": 324105,
                    "rx-errs": 0,
                    "tx-errs": 0,
                    "tx-bytes": 368860,
                    "tx-packets": 3479,
                    "tx-dropped": 0},
                "name": "eth0",
                "ip-addresses": [
                    {
                        "prefix": 24,
                        "ip-address-type": "ipv4",
                        "ip-address": "10.1.2.3"
                    },
                    {
                        "prefix": 64,
                        "ip-address": "fd8c:4687:e88d:1be3:5b70:7b88:c79c:293",
                        "ip-address-type": "ipv6"
                    }],
                "hardware-address": "ff:ff:ff:ff:ff:ff"
            },
            {
                "hardware-address": "ff:ff:ff:ff:ff:ff",
                "ip-addresses": [
                    {
                        "prefix": 16,
                        "ip-address": "10.10.2.3",
                        "ip-address-type": "ipv4"
                    }],
                "name": "docker0",
                "statistics": {
                    "rx-bytes": 0,
                    "rx-errs": 0,
                    "rx-dropped": 0,
                    "rx-packets": 0,
                    "tx-packets": 0,
                    "tx-dropped": 0,
                    "tx-errs": 0,
                    "tx-bytes": 0
                }}]}
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/102/agent/network-get-interfaces":
        # _get_agent_network_interfaces
        return {"result": {'error': {'desc': 'this feature or command is not currently supported', 'class': 'Unsupported'}}}
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/103/agent/network-get-interfaces":
        # _get_agent_network_interfaces
        return {
            "result": [
                {
                    "statistics": {
                        "tx-errs": 0,
                        "rx-errs": 0,
                        "rx-dropped": 0,
                        "tx-bytes": 48132932372,
                        "tx-dropped": 0,
                        "rx-bytes": 48132932372,
                        "tx-packets": 178578980,
                        "rx-packets": 178578980
                    },
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "ip-addresses": [
                        {
                            "ip-address-type": "ipv4",
                            "prefix": 8,
                            "ip-address": "127.0.0.1"
                        }
                    ],
                    "name": "lo"
                },
                {
                    "name": "eth0",
                    "ip-addresses": [
                        {
                            "ip-address-type": "ipv4",
                            "prefix": 24,
                            "ip-address": "172.16.0.143"
                        }
                    ],
                    "statistics": {
                        "rx-errs": 0,
                        "tx-errs": 0,
                        "rx-packets": 660028,
                        "tx-packets": 304599,
                        "tx-dropped": 0,
                        "rx-bytes": 1846743499,
                        "tx-bytes": 1287844926,
                        "rx-dropped": 0
                    },
                    "hardware-address": "ff:ff:ff:ff:ff:ff"
                },
                {
                    "name": "eth1",
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "statistics": {
                        "rx-bytes": 235717091946,
                        "tx-dropped": 0,
                        "rx-dropped": 0,
                        "tx-bytes": 123411636251,
                        "rx-packets": 540431277,
                        "tx-packets": 468411864,
                        "rx-errs": 0,
                        "tx-errs": 0
                    },
                    "ip-addresses": [
                        {
                            "ip-address": "10.0.0.133",
                            "prefix": 24,
                            "ip-address-type": "ipv4"
                        }
                    ]
                },
                {
                    "name": "docker0",
                    "ip-addresses": [
                        {
                            "ip-address": "172.17.0.1",
                            "prefix": 16,
                            "ip-address-type": "ipv4"
                        }
                    ],
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "statistics": {
                        "rx-errs": 0,
                        "tx-errs": 0,
                        "rx-packets": 0,
                        "tx-packets": 0,
                        "tx-dropped": 0,
                        "rx-bytes": 0,
                        "rx-dropped": 0,
                        "tx-bytes": 0
                    }
                },
                {
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "name": "datapath"
                },
                {
                    "name": "weave",
                    "ip-addresses": [
                        {
                            "ip-address": "10.42.0.1",
                            "ip-address-type": "ipv4",
                            "prefix": 16
                        }
                    ],
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "statistics": {
                        "rx-bytes": 127289123306,
                        "tx-dropped": 0,
                        "rx-dropped": 0,
                        "tx-bytes": 43827573343,
                        "rx-packets": 132750542,
                        "tx-packets": 74218762,
                        "rx-errs": 0,
                        "tx-errs": 0
                    }
                },
                {
                    "name": "vethwe-datapath",
                    "hardware-address": "ff:ff:ff:ff:ff:ff"
                },
                {
                    "name": "vethwe-bridge",
                    "hardware-address": "ff:ff:ff:ff:ff:ff"
                },
                {
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "name": "vxlan-6784"
                },
                {
                    "name": "vethwepl0dfe1fe",
                    "hardware-address": "ff:ff:ff:ff:ff:ff"
                },
                {
                    "name": "vethweplf1e7715",
                    "hardware-address": "ff:ff:ff:ff:ff:ff"
                },
                {
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "name": "vethwepl9d244a1"
                },
                {
                    "hardware-address": "ff:ff:ff:ff:ff:ff",
                    "name": "vethwepl2ca477b"
                },
                {
                    "name": "nomacorip",
                }
            ]
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/lxc/100/status/current":
        # _get_vm_status (lxc)
        return {
            "swap": 0,
            "name": "test-lxc",
            "diskread": 0,
            "vmid": 100,
            "diskwrite": 0,
            "pid": 9000,
            "mem": 89980928,
            "netin": 1950776396424,
            "disk": 4998168576,
            "cpu": 0.00163430613110039,
            "type": "lxc",
            "uptime": 6793736,
            "maxmem": 1073741824,
            "status": "running",
            "cpus": "1",
            "ha": {
                "group": 'null',
                "state": "started",
                "managed": 1
            },
            "maxdisk": 3348329267200,
            "netout": 1947793356037,
            "maxswap": 1073741824
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/101/status/current":
        # _get_vm_status (qemu)
        return {
            "status": "stopped",
            "uptime": 0,
            "maxmem": 5364514816,
            "maxdisk": 34359738368,
            "netout": 0,
            "cpus": 2,
            "ha": {
                "managed": 0
            },
            "diskread": 0,
            "vmid": 101,
            "diskwrite": 0,
            "name": "test-qemu",
            "cpu": 0,
            "disk": 0,
            "netin": 0,
            "mem": 0,
            "qmpstatus": "stopped"
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/102/status/current":
        # _get_vm_status (qemu)
        return {
            "status": "stopped",
            "uptime": 0,
            "maxmem": 5364514816,
            "maxdisk": 34359738368,
            "netout": 0,
            "cpus": 2,
            "ha": {
                "managed": 0
            },
            "diskread": 0,
            "vmid": 102,
            "diskwrite": 0,
            "name": "test-qemu-windows",
            "cpu": 0,
            "disk": 0,
            "netin": 0,
            "mem": 0,
            "qmpstatus": "prelaunch"
        }
    elif url == "https://localhost:8006/api2/json/nodes/testnode/qemu/103/status/current":
        # _get_vm_status (qemu)
        return {
            "status": "stopped",
            "uptime": 0,
            "maxmem": 5364514816,
            "maxdisk": 34359738368,
            "netout": 0,
            "cpus": 2,
            "ha": {
                "managed": 0
            },
            "diskread": 0,
            "vmid": 103,
            "diskwrite": 0,
            "name": "test-qemu-multi-nic",
            "cpu": 0,
            "disk": 0,
            "netin": 0,
            "mem": 0,
            "qmpstatus": "paused"
        }


def get_vm_snapshots(node, properties, vmtype, vmid, name):
    return [
        {"description": "",
         "name": "clean",
         "snaptime": 1000,
         "vmstate": 0
         },
        {"name": "current",
         "digest": "1234689abcdf",
         "running": 0,
         "description": "You are here!",
         "parent": "clean"
         }]


def get_option(opts):
    def fn(option):
        default = opts.get('default', False)
        return opts.get(option, default)
    return fn


def test_populate(inventory, mocker):
    # module settings
    inventory.proxmox_user = 'root@pam'
    inventory.proxmox_password = 'password'
    inventory.proxmox_url = 'https://localhost:8006'
    inventory.group_prefix = 'proxmox_'
    inventory.facts_prefix = 'proxmox_'
    inventory.strict = False

    opts = {
        'group_prefix': 'proxmox_',
        'facts_prefix': 'proxmox_',
        'want_facts': True,
        'want_proxmox_nodes_ansible_host': True,
        'qemu_extended_statuses': True
    }

    # bypass authentication and API fetch calls
    inventory._get_auth = mocker.MagicMock(side_effect=get_auth)
    inventory._get_json = mocker.MagicMock(side_effect=get_json)
    inventory._get_vm_snapshots = mocker.MagicMock(side_effect=get_vm_snapshots)
    inventory.get_option = mocker.MagicMock(side_effect=get_option(opts))
    inventory._can_add_host = mocker.MagicMock(return_value=True)
    inventory._populate()

    # get different hosts
    host_qemu = inventory.inventory.get_host('test-qemu')
    host_qemu_windows = inventory.inventory.get_host('test-qemu-windows')
    host_qemu_multi_nic = inventory.inventory.get_host('test-qemu-multi-nic')
    host_qemu_template = inventory.inventory.get_host('test-qemu-template')
    host_lxc = inventory.inventory.get_host('test-lxc')

    # check if qemu-test is in the proxmox_pool_test group
    assert 'proxmox_pool_test' in inventory.inventory.groups
    group_qemu = inventory.inventory.groups['proxmox_pool_test']
    assert group_qemu.hosts == [host_qemu]

    # check if qemu-test has eth0 interface in agent_interfaces fact
    assert 'eth0' in [d['name'] for d in host_qemu.get_vars()['proxmox_agent_interfaces']]

    # check if qemu-multi-nic has multiple network interfaces
    for iface_name in ['eth0', 'eth1', 'weave']:
        assert iface_name in [d['name'] for d in host_qemu_multi_nic.get_vars()['proxmox_agent_interfaces']]

    # check if interface with no mac-address or ip-address defaults correctly
    assert [iface for iface in host_qemu_multi_nic.get_vars()['proxmox_agent_interfaces']
            if iface['name'] == 'nomacorip'
            and iface['mac-address'] == ''
            and iface['ip-addresses'] == []
            ]

    # check to make sure qemu-windows doesn't have proxmox_agent_interfaces
    assert "proxmox_agent_interfaces" not in host_qemu_windows.get_vars()

    # check if lxc-test has been discovered correctly
    group_lxc = inventory.inventory.groups['proxmox_all_lxc']
    assert group_lxc.hosts == [host_lxc]

    # check if qemu template is not present
    assert host_qemu_template is None

    # check that offline node is in inventory
    assert inventory.inventory.get_host('testnode2')

    # make sure that ['prelaunch', 'paused'] are in the group list
    for group in ['paused', 'prelaunch']:
        assert ('%sall_%s' % (inventory.group_prefix, group)) in inventory.inventory.groups

    # check if qemu-windows is in the prelaunch group
    group_prelaunch = inventory.inventory.groups['proxmox_all_prelaunch']
    assert group_prelaunch.hosts == [host_qemu_windows]

    # check if qemu-multi-nic is in the paused group
    group_paused = inventory.inventory.groups['proxmox_all_paused']
    assert group_paused.hosts == [host_qemu_multi_nic]


def test_populate_missing_qemu_extended_groups(inventory, mocker):
    # module settings
    inventory.proxmox_user = 'root@pam'
    inventory.proxmox_password = 'password'
    inventory.proxmox_url = 'https://localhost:8006'
    inventory.group_prefix = 'proxmox_'
    inventory.facts_prefix = 'proxmox_'
    inventory.strict = False

    opts = {
        'group_prefix': 'proxmox_',
        'facts_prefix': 'proxmox_',
        'want_facts': True,
        'want_proxmox_nodes_ansible_host': True,
        'qemu_extended_statuses': False
    }

    # bypass authentication and API fetch calls
    inventory._get_auth = mocker.MagicMock(side_effect=get_auth)
    inventory._get_json = mocker.MagicMock(side_effect=get_json)
    inventory._get_vm_snapshots = mocker.MagicMock(side_effect=get_vm_snapshots)
    inventory.get_option = mocker.MagicMock(side_effect=get_option(opts))
    inventory._can_add_host = mocker.MagicMock(return_value=True)
    inventory._populate()

    # make sure that ['prelaunch', 'paused'] are not in the group list
    for group in ['paused', 'prelaunch']:
        assert ('%sall_%s' % (inventory.group_prefix, group)) not in inventory.inventory.groups

# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Sergei Antipov <greendayonfire at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

proxmoxer = pytest.importorskip("proxmoxer")
mandatory_py_version = pytest.mark.skipif(
    sys.version_info < (2, 7),
    reason="The proxmoxer dependency requires python2.7 or higher",
)

from ansible_collections.community.general.plugins.modules import proxmox_vm_info
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils

NODE1 = "pve"
NODE2 = "pve2"
RAW_CLUSTER_OUTPUT = [
    {
        "cpu": 0.174069059487628,
        "disk": 0,
        "diskread": 6656,
        "diskwrite": 0,
        "id": "qemu/100",
        "maxcpu": 1,
        "maxdisk": 34359738368,
        "maxmem": 4294967296,
        "mem": 35304543,
        "name": "pxe.home.arpa",
        "netin": 416956,
        "netout": 17330,
        "node": NODE1,
        "status": "running",
        "template": 0,
        "type": "qemu",
        "uptime": 669,
        "vmid": 100,
    },
    {
        "cpu": 0,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "qemu/101",
        "maxcpu": 1,
        "maxdisk": 0,
        "maxmem": 536870912,
        "mem": 0,
        "name": "test1",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "template": 0,
        "type": "qemu",
        "uptime": 0,
        "vmid": 101,
    },
    {
        "cpu": 0,
        "disk": 352190464,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/102",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "mem": 28192768,
        "name": "test-lxc.home.arpa",
        "netin": 102757,
        "netout": 446,
        "node": NODE1,
        "status": "running",
        "template": 0,
        "type": "lxc",
        "uptime": 161,
        "vmid": 102,
    },
    {
        "cpu": 0,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/103",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "mem": 0,
        "name": "test1-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "template": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": 103,
    },
    {
        "cpu": 0,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/104",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "mem": 0,
        "name": "test-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "template": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": 104,
    },
    {
        "cpu": 0,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/105",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "mem": 0,
        "name": "",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "template": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": 105,
    },
]
RAW_LXC_OUTPUT = [
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "test1-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "status": "stopped",
        "swap": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": "103",
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 352190464,
        "diskread": 0,
        "diskwrite": 0,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 28192768,
        "name": "test-lxc.home.arpa",
        "netin": 102757,
        "netout": 446,
        "pid": 4076752,
        "status": "running",
        "swap": 0,
        "type": "lxc",
        "uptime": 161,
        "vmid": "102",
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "test-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "status": "stopped",
        "swap": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": "104",
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "",
        "netin": 0,
        "netout": 0,
        "status": "stopped",
        "swap": 0,
        "type": "lxc",
        "uptime": 0,
        "vmid": "105",
    },
]
RAW_QEMU_OUTPUT = [
    {
        "cpu": 0,
        "cpus": 1,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "maxdisk": 0,
        "maxmem": 536870912,
        "mem": 0,
        "name": "test1",
        "netin": 0,
        "netout": 0,
        "status": "stopped",
        "uptime": 0,
        "vmid": 101,
    },
    {
        "cpu": 0.174069059487628,
        "cpus": 1,
        "disk": 0,
        "diskread": 6656,
        "diskwrite": 0,
        "maxdisk": 34359738368,
        "maxmem": 4294967296,
        "mem": 35304543,
        "name": "pxe.home.arpa",
        "netin": 416956,
        "netout": 17330,
        "pid": 4076688,
        "status": "running",
        "uptime": 669,
        "vmid": 100,
    },
]
EXPECTED_VMS_OUTPUT = [
    {
        "cpu": 0.174069059487628,
        "cpus": 1,
        "disk": 0,
        "diskread": 6656,
        "diskwrite": 0,
        "id": "qemu/100",
        "maxcpu": 1,
        "maxdisk": 34359738368,
        "maxmem": 4294967296,
        "mem": 35304543,
        "name": "pxe.home.arpa",
        "netin": 416956,
        "netout": 17330,
        "node": NODE1,
        "pid": 4076688,
        "status": "running",
        "template": False,
        "type": "qemu",
        "uptime": 669,
        "vmid": 100,
    },
    {
        "cpu": 0,
        "cpus": 1,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "qemu/101",
        "maxcpu": 1,
        "maxdisk": 0,
        "maxmem": 536870912,
        "mem": 0,
        "name": "test1",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "template": False,
        "type": "qemu",
        "uptime": 0,
        "vmid": 101,
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 352190464,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/102",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 28192768,
        "name": "test-lxc.home.arpa",
        "netin": 102757,
        "netout": 446,
        "node": NODE1,
        "pid": 4076752,
        "status": "running",
        "swap": 0,
        "template": False,
        "type": "lxc",
        "uptime": 161,
        "vmid": 102,
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/103",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "test1-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "swap": 0,
        "template": False,
        "type": "lxc",
        "uptime": 0,
        "vmid": 103,
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/104",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "test-lxc.home.arpa",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "swap": 0,
        "template": False,
        "type": "lxc",
        "uptime": 0,
        "vmid": 104,
    },
    {
        "cpu": 0,
        "cpus": 2,
        "disk": 0,
        "diskread": 0,
        "diskwrite": 0,
        "id": "lxc/105",
        "maxcpu": 2,
        "maxdisk": 10737418240,
        "maxmem": 536870912,
        "maxswap": 536870912,
        "mem": 0,
        "name": "",
        "netin": 0,
        "netout": 0,
        "node": NODE2,
        "pool": "pool1",
        "status": "stopped",
        "swap": 0,
        "template": False,
        "type": "lxc",
        "uptime": 0,
        "vmid": 105,
    },
]


def get_module_args(type="all", node=None, vmid=None, name=None, config="none"):
    return {
        "api_host": "host",
        "api_user": "user",
        "api_password": "password",
        "node": node,
        "type": type,
        "vmid": vmid,
        "name": name,
        "config": config,
    }


class TestProxmoxVmInfoModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxVmInfoModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_vm_info
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.connect_mock.return_value.nodes.return_value.lxc.return_value.get.return_value = (
            RAW_LXC_OUTPUT
        )
        self.connect_mock.return_value.nodes.return_value.qemu.return_value.get.return_value = (
            RAW_QEMU_OUTPUT
        )
        self.connect_mock.return_value.cluster.return_value.resources.return_value.get.return_value = (
            RAW_CLUSTER_OUTPUT
        )
        self.connect_mock.return_value.nodes.get.return_value = [{"node": NODE1}]

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxVmInfoModule, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args({})
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "missing required arguments: api_host, api_user"

    def test_get_lxc_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args(get_module_args(type="lxc"))
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["type"] == "lxc"]
            self.module.main()

        result = exc_info.value.args[0]
        assert result["changed"] is False
        assert result["proxmox_vms"] == expected_output

    def test_get_qemu_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args(get_module_args(type="qemu"))
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["type"] == "qemu"]
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output

    def test_get_all_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args(get_module_args())
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == EXPECTED_VMS_OUTPUT

    def test_vmid_is_converted_to_int(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args(get_module_args(type="lxc"))
            self.module.main()

        result = exc_info.value.args[0]
        assert isinstance(result["proxmox_vms"][0]["vmid"], int)

    def test_get_specific_lxc_vm_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 102
            expected_output = [
                vm
                for vm in EXPECTED_VMS_OUTPUT
                if vm["vmid"] == vmid and vm["type"] == "lxc"
            ]
            set_module_args(get_module_args(type="lxc", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_specific_qemu_vm_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 100
            expected_output = [
                vm
                for vm in EXPECTED_VMS_OUTPUT
                if vm["vmid"] == vmid and vm["type"] == "qemu"
            ]
            set_module_args(get_module_args(type="qemu", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_specific_vm_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 100
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["vmid"] == vmid]
            set_module_args(get_module_args(type="all", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_specific_vm_information_by_using_name(self):
        name = "test1-lxc.home.arpa"
        self.connect_mock.return_value.cluster.resources.get.return_value = [
            {"name": name, "vmid": "103"}
        ]

        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["name"] == name]
            set_module_args(get_module_args(type="all", name=name))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_multiple_vms_with_the_same_name(self):
        name = "test-lxc.home.arpa"
        self.connect_mock.return_value.cluster.resources.get.return_value = [
            {"name": name, "vmid": "102"},
            {"name": name, "vmid": "104"},
        ]

        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["name"] == name]
            set_module_args(get_module_args(type="all", name=name))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 2

    def test_get_vm_with_an_empty_name(self):
        name = ""
        self.connect_mock.return_value.cluster.resources.get.return_value = [
            {"name": name, "vmid": "105"},
        ]

        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["name"] == name]
            set_module_args(get_module_args(type="all", name=name))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_all_lxc_vms_from_specific_node(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [
                vm
                for vm in EXPECTED_VMS_OUTPUT
                if vm["node"] == NODE1 and vm["type"] == "lxc"
            ]
            set_module_args(get_module_args(type="lxc", node=NODE1))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_all_qemu_vms_from_specific_node(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [
                vm
                for vm in EXPECTED_VMS_OUTPUT
                if vm["node"] == NODE1 and vm["type"] == "qemu"
            ]
            set_module_args(get_module_args(type="qemu", node=NODE1))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_all_vms_from_specific_node(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["node"] == NODE1]
            set_module_args(get_module_args(node=NODE1))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 2

    def test_module_returns_empty_list_when_vm_does_not_exist(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 200
            set_module_args(get_module_args(type="all", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == []

    def test_module_fail_when_qemu_request_fails(self):
        self.connect_mock.return_value.nodes.return_value.qemu.return_value.get.side_effect = IOError(
            "Some mocked connection error."
        )
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args(get_module_args(type="qemu"))
            self.module.main()

        result = exc_info.value.args[0]
        assert "Failed to retrieve QEMU VMs information:" in result["msg"]

    def test_module_fail_when_lxc_request_fails(self):
        self.connect_mock.return_value.nodes.return_value.lxc.return_value.get.side_effect = IOError(
            "Some mocked connection error."
        )
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args(get_module_args(type="lxc"))
            self.module.main()

        result = exc_info.value.args[0]
        assert "Failed to retrieve LXC VMs information:" in result["msg"]

    def test_module_fail_when_cluster_resources_request_fails(self):
        self.connect_mock.return_value.cluster.return_value.resources.return_value.get.side_effect = IOError(
            "Some mocked connection error."
        )
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args(get_module_args())
            self.module.main()

        result = exc_info.value.args[0]
        assert (
            "Failed to retrieve VMs information from cluster resources:"
            in result["msg"]
        )

    def test_module_fail_when_node_does_not_exist(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args(get_module_args(type="all", node="NODE3"))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "Node NODE3 doesn't exist in PVE cluster"

    def test_call_to_get_vmid_is_not_used_when_vmid_provided(self):
        with patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible.get_vmid"
        ) as get_vmid_mock:
            with pytest.raises(AnsibleExitJson):
                vmid = 100
                set_module_args(
                    get_module_args(type="all", vmid=vmid, name="something")
                )
                self.module.main()

        assert get_vmid_mock.call_count == 0

    def test_config_returned_when_specified_qemu_vm_with_config(self):
        config_vm_value = {
            'scsi0': 'local-lvm:vm-101-disk-0,iothread=1,size=32G',
            'net0': 'virtio=4E:79:9F:A8:EE:E4,bridge=vmbr0,firewall=1',
            'scsihw': 'virtio-scsi-single',
            'cores': 1,
            'name': 'test1',
            'ostype': 'l26',
            'boot': 'order=scsi0;ide2;net0',
            'memory': 2048,
            'sockets': 1,
        }
        (self.connect_mock.return_value.nodes.return_value.qemu.return_value.
         config.return_value.get.return_value) = config_vm_value

        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 101
            set_module_args(get_module_args(
                type="qemu",
                vmid=vmid,
                config="current",
            ))
            expected_output = [vm for vm in EXPECTED_VMS_OUTPUT if vm["vmid"] == vmid]
            expected_output[0]["config"] = config_vm_value
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output

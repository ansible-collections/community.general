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

NODE = "pve"
LXC_VMS = [
    {
        "uptime": 47,
        "maxswap": 536870912,
        "diskread": 0,
        "name": "test-lxc.home.arpa",
        "status": "running",
        "vmid": "102",
        "type": "lxc",
        "swap": 0,
        "cpus": 2,
        "mem": 29134848,
        "maxdisk": 10737418240,
        "diskwrite": 0,
        "netin": 35729,
        "netout": 446,
        "pid": 1412780,
        "maxmem": 536870912,
        "disk": 307625984,
        "cpu": 0,
    },
    {
        "netin": 0,
        "netout": 0,
        "cpu": 0,
        "maxmem": 536870912,
        "disk": 0,
        "name": "test1-lxc.home.arpa",
        "diskread": 0,
        "status": "stopped",
        "vmid": "103",
        "type": "lxc",
        "swap": 0,
        "uptime": 0,
        "maxswap": 536870912,
        "diskwrite": 0,
        "cpus": 2,
        "mem": 0,
        "maxdisk": 10737418240,
    },
]
QEMU_VMS = [
    {
        "vmid": 101,
        "diskread": 0,
        "status": "stopped",
        "name": "test1",
        "uptime": 0,
        "diskwrite": 0,
        "cpus": 1,
        "mem": 0,
        "maxdisk": 0,
        "netout": 0,
        "netin": 0,
        "cpu": 0,
        "maxmem": 536870912,
        "disk": 0,
    },
    {
        "netout": 4113,
        "netin": 22738,
        "pid": 1947197,
        "maxmem": 4294967296,
        "disk": 0,
        "cpu": 0.0795350949559682,
        "uptime": 41,
        "vmid": 100,
        "status": "running",
        "diskread": 0,
        "name": "pxe.home.arpa",
        "cpus": 1,
        "mem": 35315629,
        "maxdisk": 34359738368,
        "diskwrite": 0,
    },
]


def get_module_args(type="all", vmid=None, name=None):
    return {
        "api_host": "host",
        "api_user": "user",
        "api_password": "password",
        "node": NODE,
        "type": type,
        "vmid": vmid,
        "name": name,
    }


def normalized_expected_vms_output(vms):
    result = [vm.copy() for vm in vms]
    for vm in result:
        if "type" not in vm:
            # response for QEMU VMs doesn't contain type field, adding it
            vm["type"] = "qemu"
        vm["vmid"] = int(vm["vmid"])
    return result


class TestProxmoxVmInfoModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxVmInfoModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_vm_info
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.connect_mock.return_value.nodes.return_value.lxc.return_value.get.return_value = (
            LXC_VMS
        )
        self.connect_mock.return_value.nodes.return_value.qemu.return_value.get.return_value = (
            QEMU_VMS
        )
        self.connect_mock.return_value.nodes.get.return_value = [{"node": NODE}]

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxVmInfoModule, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args({})
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "missing required arguments: api_host, api_user, node"

    def test_get_lxc_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args(get_module_args(type="lxc"))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["changed"] is False
        assert result["proxmox_vms"] == LXC_VMS

    def test_get_qemu_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = normalized_expected_vms_output(QEMU_VMS)
            set_module_args(get_module_args(type="qemu"))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output

    def test_get_all_vms_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            qemu_output = normalized_expected_vms_output(QEMU_VMS)
            expected_output = qemu_output + LXC_VMS

            set_module_args(get_module_args())
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output

    def test_vmid_is_converted_to_int(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = normalized_expected_vms_output(LXC_VMS)
            set_module_args(get_module_args(type="lxc"))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert isinstance(result["proxmox_vms"][0]["vmid"], int)

    def test_get_specific_lxc_vm_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 102
            expected_output = [
                vm
                for vm in normalized_expected_vms_output(LXC_VMS)
                if vm["vmid"] == vmid
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
                for vm in normalized_expected_vms_output(QEMU_VMS)
                if vm["vmid"] == vmid
            ]
            set_module_args(get_module_args(type="qemu", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_specific_vm_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = 100
            expected_output = [
                vm
                for vm in normalized_expected_vms_output(QEMU_VMS + LXC_VMS)
                if vm["vmid"] == vmid
            ]
            set_module_args(get_module_args(type="all", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_get_specific_vm_information_by_using_name(self):
        name = "test-lxc.home.arpa"
        self.connect_mock.return_value.cluster.resources.get.return_value = [
            {"name": name, "vmid": "102"}
        ]

        with pytest.raises(AnsibleExitJson) as exc_info:
            expected_output = [
                vm
                for vm in normalized_expected_vms_output(QEMU_VMS + LXC_VMS)
                if vm["name"] == name
            ]
            set_module_args(get_module_args(type="all", name=name))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["proxmox_vms"] == expected_output
        assert len(result["proxmox_vms"]) == 1

    def test_module_fail_when_vm_does_not_exist_on_node(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            vmid = 200
            set_module_args(get_module_args(type="all", vmid=vmid))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "VM with vmid 200 doesn't exist on node pve"

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

    def test_module_fail_when_node_does_not_exist(self):
        self.connect_mock.return_value.nodes.get.return_value = []
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args(get_module_args(type="all"))
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "Node pve doesn't exist in PVE cluster"

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

# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Ansible Project
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

from ansible_collections.community.general.plugins.modules import proxmox_kvm
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import (
    patch,
    DEFAULT,
)
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils


class TestProxmoxKvmModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxKvmModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_kvm
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect"
        ).start()
        self.get_node_mock = patch.object(
            proxmox_utils.ProxmoxAnsible, "get_node"
        ).start()
        self.get_vm_mock = patch.object(proxmox_utils.ProxmoxAnsible, "get_vm").start()
        self.create_vm_mock = patch.object(
            proxmox_kvm.ProxmoxKvmAnsible, "create_vm"
        ).start()

    def tearDown(self):
        self.create_vm_mock.stop()
        self.get_vm_mock.stop()
        self.get_node_mock.stop()
        self.connect_mock.stop()
        super(TestProxmoxKvmModule, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_module_exits_unchaged_when_provided_vmid_exists(self):
        with set_module_args(
            {
                "api_host": "host",
                "api_user": "user",
                "api_password": "password",
                "vmid": "100",
                "node": "pve",
            }
        ):
            self.get_vm_mock.return_value = [{"vmid": "100"}]
            with pytest.raises(AnsibleExitJson) as exc_info:
                self.module.main()

        assert self.get_vm_mock.call_count == 1
        result = exc_info.value.args[0]
        assert result["changed"] is False
        assert result["msg"] == "VM with vmid <100> already exists"

    def test_vm_created_when_vmid_not_exist_but_name_already_exist(self):
        with set_module_args(
            {
                "api_host": "host",
                "api_user": "user",
                "api_password": "password",
                "vmid": "100",
                "name": "existing.vm.local",
                "node": "pve",
            }
        ):
            self.get_vm_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc_info:
                self.module.main()

        assert self.get_vm_mock.call_count == 1
        assert self.get_node_mock.call_count == 1
        result = exc_info.value.args[0]
        assert result["changed"] is True
        assert result["msg"] == "VM existing.vm.local with vmid 100 deployed"

    def test_vm_not_created_when_name_already_exist_and_vmid_not_set(self):
        with set_module_args(
            {
                "api_host": "host",
                "api_user": "user",
                "api_password": "password",
                "name": "existing.vm.local",
                "node": "pve",
            }
        ):
            with patch.object(proxmox_utils.ProxmoxAnsible, "get_vmid") as get_vmid_mock:
                get_vmid_mock.return_value = {
                    "vmid": 100,
                    "name": "existing.vm.local",
                }
                with pytest.raises(AnsibleExitJson) as exc_info:
                    self.module.main()

        assert get_vmid_mock.call_count == 1
        result = exc_info.value.args[0]
        assert result["changed"] is False

    def test_vm_created_when_name_doesnt_exist_and_vmid_not_set(self):
        with set_module_args(
            {
                "api_host": "host",
                "api_user": "user",
                "api_password": "password",
                "name": "existing.vm.local",
                "node": "pve",
            }
        ):
            self.get_vm_mock.return_value = None
            with patch.multiple(
                proxmox_utils.ProxmoxAnsible, get_vmid=DEFAULT, get_nextvmid=DEFAULT
            ) as utils_mock:
                utils_mock["get_vmid"].return_value = None
                utils_mock["get_nextvmid"].return_value = 101
                with pytest.raises(AnsibleExitJson) as exc_info:
                    self.module.main()

        assert utils_mock["get_vmid"].call_count == 1
        assert utils_mock["get_nextvmid"].call_count == 1
        result = exc_info.value.args[0]
        assert result["changed"] is True
        assert result["msg"] == "VM existing.vm.local with vmid 101 deployed"

    def test_parse_mac(self):
        assert (
            proxmox_kvm.parse_mac("virtio=00:11:22:AA:BB:CC,bridge=vmbr0,firewall=1")
            == "00:11:22:AA:BB:CC"
        )

    def test_parse_dev(self):
        assert (
            proxmox_kvm.parse_dev("local-lvm:vm-1000-disk-0,format=qcow2")
            == "local-lvm:vm-1000-disk-0"
        )
        assert (
            proxmox_kvm.parse_dev("local-lvm:vm-101-disk-1,size=8G")
            == "local-lvm:vm-101-disk-1"
        )
        assert (
            proxmox_kvm.parse_dev("local-zfs:vm-1001-disk-0")
            == "local-zfs:vm-1001-disk-0"
        )

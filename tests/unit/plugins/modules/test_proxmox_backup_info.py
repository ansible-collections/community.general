# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Marzieh Raoufnezhad <raoufnezhad at gmail.com>
# Copyright (c) 2024 Maryam Mayabi <mayabi.ahm at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

proxmoxer = pytest.importorskip("proxmoxer")

from ansible_collections.community.general.plugins.modules import proxmox_backup_info
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils

RESOURCE_LIST = [
    {
        "uptime": 0,
        "diskwrite": 0,
        "name": "test01",
        "maxcpu": 0,
        "node": "NODE1",
        "mem": 0,
        "netout": 0,
        "netin": 0,
        "maxmem": 0,
        "diskread": 0,
        "disk": 0,
        "maxdisk": 0,
        "status": "running",
        "cpu": 0,
        "id": "qemu/100",
        "template": 0,
        "vmid": 100,
        "type": "qemu"
    },
    {
        "uptime": 0,
        "diskwrite": 0,
        "name": "test02",
        "maxcpu": 0,
        "node": "NODE1",
        "mem": 0,
        "netout": 0,
        "netin": 0,
        "maxmem": 0,
        "diskread": 0,
        "disk": 0,
        "maxdisk": 0,
        "status": "running",
        "cpu": 0,
        "id": "qemu/101",
        "template": 0,
        "vmid": 101,
        "type": "qemu"
    },
    {
        "uptime": 0,
        "diskwrite": 0,
        "name": "test03",
        "maxcpu": 0,
        "node": "NODE2",
        "mem": 0,
        "netout": 0,
        "netin": 0,
        "maxmem": 0,
        "diskread": 0,
        "disk": 0,
        "maxdisk": 0,
        "status": "running",
        "cpu": 0,
        "id": "qemu/102",
        "template": 0,
        "vmid": 102,
        "type": "qemu"
    }
]
BACKUP_JOBS = [
    {
        "type": "vzdump",
        "id": "backup-83831498-c631",
        "storage": "local",
        "vmid": "100",
        "enabled": 1,
        "next-run": 1735138800,
        "mailnotification": "always",
        "schedule": "06,18:30",
        "mode": "snapshot",
        "notes-template": "guestname"
    },
    {
        "schedule": "sat 15:00",
        "notes-template": "guestname",
        "mode": "snapshot",
        "mailnotification": "always",
        "next-run": 1735385400,
        "type": "vzdump",
        "enabled": 1,
        "vmid": "100,101,102",
        "storage": "local",
        "id": "backup-70025700-2302",
    }
]

EXPECTED_BACKUP_OUTPUT = [
    {
        "bktype": "vzdump",
        "enabled": 1,
        "id": "backup-83831498-c631",
        "mode": "snapshot",
        "next-run": "2024-12-25 15:00:00",
        "schedule": "06,18:30",
        "storage": "local",
        "vm_name": "test01",
        "vmid": "100"
    },
    {
        "bktype": "vzdump",
        "enabled": 1,
        "id": "backup-70025700-2302",
        "mode": "snapshot",
        "next-run": "2024-12-28 11:30:00",
        "schedule": "sat 15:00",
        "storage": "local",
        "vm_name": "test01",
        "vmid": "100"
    },
    {
        "bktype": "vzdump",
        "enabled": 1,
        "id": "backup-70025700-2302",
        "mode": "snapshot",
        "next-run": "2024-12-28 11:30:00",
        "schedule": "sat 15:00",
        "storage": "local",
        "vm_name": "test02",
        "vmid": "101"
    },
    {
        "bktype": "vzdump",
        "enabled": 1,
        "id": "backup-70025700-2302",
        "mode": "snapshot",
        "next-run": "2024-12-28 11:30:00",
        "schedule": "sat 15:00",
        "storage": "local",
        "vm_name": "test03",
        "vmid": "102"
    }
]
EXPECTED_BACKUP_JOBS_OUTPUT = [
    {
        "enabled": 1,
        "id": "backup-83831498-c631",
        "mailnotification": "always",
        "mode": "snapshot",
        "next-run": 1735138800,
        "notes-template": "guestname",
        "schedule": "06,18:30",
        "storage": "local",
        "type": "vzdump",
        "vmid": "100"
    },
    {
        "enabled": 1,
        "id": "backup-70025700-2302",
        "mailnotification": "always",
        "mode": "snapshot",
        "next-run": 1735385400,
        "notes-template": "guestname",
        "schedule": "sat 15:00",
        "storage": "local",
        "type": "vzdump",
        "vmid": "100,101,102"
    }
]


class TestProxmoxBackupInfoModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxBackupInfoModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_backup_info
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.connect_mock.return_value.cluster.resources.get.return_value = (
            RESOURCE_LIST
        )
        self.connect_mock.return_value.cluster.backup.get.return_value = (
            BACKUP_JOBS
        )

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxBackupInfoModule, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            with set_module_args({}):
                self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "missing required arguments: api_host, api_user"

    def test_get_all_backups_information(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            with set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret'
            }):
                self.module.main()

        result = exc_info.value.args[0]
        assert result["backup_info"] == EXPECTED_BACKUP_OUTPUT

    def test_get_specific_backup_information_by_vmname(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmname = 'test01'
            expected_output = [
                backup for backup in EXPECTED_BACKUP_OUTPUT if backup["vm_name"] == vmname
            ]
            with set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret',
                'vm_name': vmname
            }):
                self.module.main()

        result = exc_info.value.args[0]
        assert result["backup_info"] == expected_output
        assert len(result["backup_info"]) == 2

    def test_get_specific_backup_information_by_vmid(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            vmid = "101"
            expected_output = [
                backup for backup in EXPECTED_BACKUP_OUTPUT if backup["vmid"] == vmid
            ]
            with set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret',
                'vm_id': vmid
            }):
                self.module.main()
        result = exc_info.value.args[0]
        assert result["backup_info"] == expected_output
        assert len(result["backup_info"]) == 1

    def test_get_specific_backup_information_by_backupjobs(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            backupjobs = True
            with set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret',
                'backup_jobs': backupjobs
            }):
                self.module.main()

        result = exc_info.value.args[0]
        assert result["backup_info"] == EXPECTED_BACKUP_JOBS_OUTPUT

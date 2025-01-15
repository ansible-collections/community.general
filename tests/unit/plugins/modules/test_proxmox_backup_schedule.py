# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Marzieh Raoufnezhad <raoufnezhad at gmail.com>
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

from ansible_collections.community.general.plugins.modules import proxmox_backup_schedule
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
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
    },
    {
        "uptime": 0,
        "diskwrite": 0,
        "name": "test04",
        "maxcpu": 0,
        "node": "NODE3",
        "mem": 0,
        "netout": 0,
        "netin": 0,
        "maxmem": 0,
        "diskread": 0,
        "disk": 0,
        "maxdisk": 0,
        "status": "running",
        "cpu": 0,
        "id": "qemu/103",
        "template": 0,
        "vmid": 103,
        "type": "qemu"
    },
    {
        "uptime": 0,
        "diskwrite": 0,
        "name": "test05",
        "maxcpu": 0,
        "node": "NODE3",
        "mem": 0,
        "netout": 0,
        "netin": 0,
        "maxmem": 0,
        "diskread": 0,
        "disk": 0,
        "maxdisk": 0,
        "status": "running",
        "cpu": 0,
        "id": "qemu/105",
        "template": 0,
        "vmid": 105,
        "type": "qemu"
    }
]

BACKUP_JOBS = [
    {
        "type": "vzdump",
        "id": "backup-001",
        "storage": "local",
        "vmid": "100,101",
        "enabled": 1,
        "next-run": 1735138800,
        "mailnotification": "always",
        "schedule": "06,18:30",
        "mode": "snapshot",
        "notes-template": "{{guestname}}"
    },
    {
        "schedule": "sat 15:00",
        "notes-template": "{{guestname}}",
        "mode": "snapshot",
        "mailnotification": "always",
        "next-run": 1735385400,
        "type": "vzdump",
        "enabled": 1,
        "vmid": "101,102,103",
        "storage": "local",
        "id": "backup-002",
    }
]

BACKUP_JOB_SPECIFIC_BKID = {
    "enabled": 1,
    "id": "backup-001",
    "mailnotification": "always",
    "mode": "snapshot",
    "compress": "zstd",
    "notes-template": "{{guestname}}",
    "schedule": "06,18:30",
    "storage": "local",
    "type": "vzdump",
    "vmid": "100,101"
}
EXPECTED_UPDATE_BACKUP_SCHEDULE = "True"
EXPECTED_DEL_BACKUP_SCHEDULE = ["backup-001", "backup-002"]


class TestProxmoxBackupScheduleModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxBackupScheduleModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_backup_schedule
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.connect_mock.return_value.cluster.resources.get.return_value = (
            RESOURCE_LIST
        )
        self.connect_mock.return_value.cluster.backup.get.side_effect = (
            lambda backup_id=None: BACKUP_JOBS if backup_id is None else [job for job in BACKUP_JOBS if job['id'] == backup_id]
        )

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxBackupScheduleModule, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            set_module_args({})
            self.module.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "missing required arguments: api_host, api_user, backup_action"

    def test_update_vmid_in_backup(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret',
                'vm_name': 'test05',
                'backup_id': 'backup-001',
                'backup_action': 'update_vmid'
            })
            self.module.main()

        result = exc_info.value.args[0]

        assert result['changed'] is True
        assert result['backup_schedule'] == EXPECTED_UPDATE_BACKUP_SCHEDULE

    def test_delete_vmid_from_backup(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            set_module_args({
                'api_host': 'proxmoxhost',
                'api_user': 'root@pam',
                'api_password': 'supersecret',
                'vm_id': 101,
                'backup_action': 'delete_vmid'
            })
            self.module.main()

        result = exc_info.value.args[0]
        assert result['changed'] is True
        assert result['backup_schedule'] == EXPECTED_DEL_BACKUP_SCHEDULE


if __name__ == '__main__':
    pytest.main([__file__])

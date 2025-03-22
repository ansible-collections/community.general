# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
import \
    ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.general.plugins.modules import proxmox_backup
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, set_module_args, ModuleTestCase)
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch

__metaclass__ = type

import pytest

proxmoxer = pytest.importorskip('proxmoxer')


MINIMAL_PERMISSIONS = {
    '/sdn/zones': {'Datastore.AllocateSpace': 1, 'Datastore.Audit': 1},
    '/nodes': {'Datastore.AllocateSpace': 1, 'Datastore.Audit': 1},
    '/sdn': {'Datastore.AllocateSpace': 1, 'Datastore.Audit': 1},
    '/vms': {'VM.Audit': 1,
             'Sys.Audit': 1,
             'Mapping.Audit': 1,
             'VM.Backup': 1,
             'Datastore.Audit': 1,
             'SDN.Audit': 1,
             'Pool.Audit': 1},
    '/': {'Datastore.Audit': 1, 'Datastore.AllocateSpace': 1},
    '/storage/local-zfs': {'Datastore.AllocateSpace': 1,
                           'Datastore.Audit': 1},
    '/storage': {'Datastore.AllocateSpace': 1, 'Datastore.Audit': 1},
    '/access': {'Datastore.AllocateSpace': 1, 'Datastore.Audit': 1},
    '/vms/101': {'VM.Backup': 1,
                 'Mapping.Audit': 1,
                 'Datastore.AllocateSpace': 0,
                 'Sys.Audit': 1,
                 'VM.Audit': 1,
                 'SDN.Audit': 1,
                 'Pool.Audit': 1,
                 'Datastore.Audit': 1},
    '/vms/100': {'VM.Backup': 1,
                 'Mapping.Audit': 1,
                 'Datastore.AllocateSpace': 0,
                 'Sys.Audit': 1,
                 'VM.Audit': 1,
                 'SDN.Audit': 1,
                 'Pool.Audit': 1,
                 'Datastore.Audit': 1},
    '/pool': {'Datastore.Audit': 1, 'Datastore.AllocateSpace': 1}, }

STORAGE = [{'type': 'pbs',
            'username': 'test@pbs',
            'datastore': 'Backup-Pool',
            'server': '10.0.0.1',
            'shared': 1,
            'fingerprint': '94:fd:ac:e7:d5:36:0e:11:5b:23:05:40:d2:a4:e1:8a:c1:52:41:01:07:28:c0:4d:c5:ee:df:7f:7c:03:ab:41',
            'prune-backups': 'keep-all=1',
            'storage': 'backup',
            'content': 'backup',
            'digest': 'ca46a68d7699de061c139d714892682ea7c9d681'},
           {'nodes': 'node1,node2,node3',
            'sparse': 1,
            'type': 'zfspool',
            'content': 'rootdir,images',
            'digest': 'ca46a68d7699de061c139d714892682ea7c9d681',
            'pool': 'rpool/data',
            'storage': 'local-zfs'}]


VMS = [{"diskwrite": 0,
        "vmid": 100,
        "node": "node1",
        "id": "lxc/100",
        "maxdisk": 10000,
        "template": 0,
        "disk": 10000,
        "uptime": 10000,
        "maxmem": 10000,
        "maxcpu": 1,
        "netin": 10000,
        "type": "lxc",
        "netout": 10000,
        "mem": 10000,
        "diskread": 10000,
        "cpu": 0.01,
        "name": "test-lxc",
        "status": "running"},
       {"diskwrite": 0,
        "vmid": 101,
        "node": "node2",
        "id": "kvm/101",
        "maxdisk": 10000,
        "template": 0,
        "disk": 10000,
        "uptime": 10000,
        "maxmem": 10000,
        "maxcpu": 1,
        "netin": 10000,
        "type": "lxc",
        "netout": 10000,
        "mem": 10000,
        "diskread": 10000,
        "cpu": 0.01,
        "name": "test-kvm",
        "status": "running"}
       ]

NODES = [{'level': '',
          'type': 'node',
          'node': 'node1',
          'status': 'online',
          'id': 'node/node1',
          'cgroup-mode': 2},
         {'status': 'online',
          'id': 'node/node2',
          'cgroup-mode': 2,
          'level': '',
          'node': 'node2',
          'type': 'node'},
         {'status': 'online',
          'id': 'node/node3',
          'cgroup-mode': 2,
          'level': '',
          'node': 'node3',
          'type': 'node'},
         ]

TASK_API_RETURN = {
    "node1": {
        'starttime': 1732606253,
        'status': 'stopped',
        'type': 'vzdump',
        'pstart': 517463911,
        'upid': 'UPID:node1:003F8C63:1E7FB79C:67449780:vzdump:100:root@pam:',
        'id': '100',
        'node': 'hypervisor',
        'pid': 541669,
        'user': 'test@pve',
        'exitstatus': 'OK'},
    "node2": {
        'starttime': 1732606253,
        'status': 'stopped',
        'type': 'vzdump',
        'pstart': 517463911,
        'upid': 'UPID:node2:000029DD:1599528B:6108F068:vzdump:101:root@pam:',
        'id': '101',
        'node': 'hypervisor',
        'pid': 541669,
        'user': 'test@pve',
        'exitstatus': 'OK'},
}


VZDUMP_API_RETURN = {
    "node1": "UPID:node1:003F8C63:1E7FB79C:67449780:vzdump:100:root@pam:",
    "node2": "UPID:node2:000029DD:1599528B:6108F068:vzdump:101:root@pam:",
    "node3": "OK",
}


TASKLOG_API_RETURN = {"node1": [{'n': 1,
                                 't': "INFO: starting new backup job: vzdump 100 --mode snapshot --node node1 "
                                      "--notes-template '{{guestname}}' --storage backup --notification-mode auto"},
                                {'t': 'INFO: Starting Backup of VM 100 (lxc)',
                                 'n': 2},
                                {'n': 23, 't': 'INFO: adding notes to backup'},
                                {'n': 24,
                                 't': 'INFO: Finished Backup of VM 100 (00:00:03)'},
                                {'n': 25,
                                 't': 'INFO: Backup finished at 2024-11-25 16:28:03'},
                                {'t': 'INFO: Backup job finished successfully',
                                 'n': 26},
                                {'n': 27, 't': 'TASK OK'}],
                      "node2": [{'n': 1,
                                 't': "INFO: starting new backup job: vzdump 101 --mode snapshot --node node2 "
                                      "--notes-template '{{guestname}}' --storage backup --notification-mode auto"},
                                {'t': 'INFO: Starting Backup of VM 101 (kvm)',
                                 'n': 2},
                                {'n': 24,
                                 't': 'INFO: Finished Backup of VM 100 (00:00:03)'},
                                {'n': 25,
                                 't': 'INFO: Backup finished at 2024-11-25 16:28:03'},
                                {'t': 'INFO: Backup job finished successfully',
                                 'n': 26},
                                {'n': 27, 't': 'TASK OK'}],
                      }


def return_valid_resources(resource_type, *args, **kwargs):
    if resource_type == "vm":
        return VMS
    if resource_type == "node":
        return NODES


def return_vzdump_api(node, *args, **kwargs):
    if node in ("node1", "node2", "node3"):
        return VZDUMP_API_RETURN[node]


def return_logs_api(node, *args, **kwargs):
    if node in ("node1", "node2"):
        return TASKLOG_API_RETURN[node]


def return_task_status_api(node, *args, **kwargs):
    if node in ("node1", "node2"):
        return TASK_API_RETURN[node]


class TestProxmoxBackup(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxBackup, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_backup
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.mock_get_permissions = patch.object(
            proxmox_backup.ProxmoxBackupAnsible, "_get_permissions").start()
        self.mock_get_storages = patch.object(proxmox_utils.ProxmoxAnsible,
                                              "get_storages").start()
        self.mock_get_resources = patch.object(
            proxmox_backup.ProxmoxBackupAnsible, "_get_resources").start()
        self.mock_get_tasklog = patch.object(
            proxmox_backup.ProxmoxBackupAnsible, "_get_tasklog").start()
        self.mock_post_vzdump = patch.object(
            proxmox_backup.ProxmoxBackupAnsible, "_post_vzdump").start()
        self.mock_get_taskok = patch.object(
            proxmox_backup.ProxmoxBackupAnsible, "_get_taskok").start()
        self.mock_get_permissions.return_value = MINIMAL_PERMISSIONS
        self.mock_get_storages.return_value = STORAGE
        self.mock_get_resources.side_effect = return_valid_resources
        self.mock_get_taskok.side_effect = return_task_status_api
        self.mock_get_tasklog.side_effect = return_logs_api
        self.mock_post_vzdump.side_effect = return_vzdump_api

    def tearDown(self):
        self.connect_mock.stop()
        self.mock_get_permissions.stop()
        self.mock_get_storages.stop()
        self.mock_get_resources.stop()
        super(TestProxmoxBackup, self).tearDown()

    def test_proxmox_backup_without_argument(self):
        with set_module_args({}):
            with pytest.raises(AnsibleFailJson):
                proxmox_backup.main()

    def test_create_backup_check_mode(self):
        with set_module_args(
            {
                "api_user": "root@pam",
                "api_password": "secret",
                "api_host": "127.0.0.1",
                "mode": "all",
                "storage": "backup",
                "_ansible_check_mode": True,
            }
        ):
            with pytest.raises(AnsibleExitJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]

        assert result["changed"] is True
        assert result["msg"] == "Backups would be created"
        assert len(result["backups"]) == 0
        assert self.mock_get_taskok.call_count == 0
        assert self.mock_get_tasklog.call_count == 0
        assert self.mock_post_vzdump.call_count == 0

    def test_create_backup_all_mode(self):
        with set_module_args({
            "api_user": "root@pam",
            "api_password": "secret",
            "api_host": "127.0.0.1",
            "mode": "all",
            "storage": "backup",
        }):
            with pytest.raises(AnsibleExitJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]
        assert result["changed"] is True
        assert result["msg"] == "Backup tasks created"
        for backup_result in result["backups"]:
            assert backup_result["upid"] in {
                VZDUMP_API_RETURN[key] for key in VZDUMP_API_RETURN}
        assert self.mock_get_taskok.call_count == 0
        assert self.mock_post_vzdump.call_count == 3

    def test_create_backup_include_mode_with_wait(self):
        with set_module_args({
            "api_user": "root@pam",
            "api_password": "secret",
            "api_host": "127.0.0.1",
            "mode": "include",
            "node": "node1",
            "storage": "backup",
            "vmids": [100],
            "wait": True
        }):
            with pytest.raises(AnsibleExitJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]
        assert result["changed"] is True
        assert result["msg"] == "Backups succeeded"
        for backup_result in result["backups"]:
            assert backup_result["upid"] in {
                VZDUMP_API_RETURN[key] for key in VZDUMP_API_RETURN}
        assert self.mock_get_taskok.call_count == 1
        assert self.mock_post_vzdump.call_count == 1

    def test_fail_insufficient_permissions(self):
        with set_module_args({
            "api_user": "root@pam",
            "api_password": "secret",
            "api_host": "127.0.0.1",
            "mode": "include",
            "storage": "backup",
            "performance_tweaks": "max-workers=2",
            "vmids": [100],
            "wait": True
        }):
            with pytest.raises(AnsibleFailJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "Insufficient permission: Performance_tweaks and bandwidth require 'Sys.Modify' permission for '/'"
        assert self.mock_get_taskok.call_count == 0
        assert self.mock_post_vzdump.call_count == 0

    def test_fail_missing_node(self):
        with set_module_args({
            "api_user": "root@pam",
            "api_password": "secret",
            "api_host": "127.0.0.1",
            "mode": "include",
            "storage": "backup",
            "node": "nonexistingnode",
            "vmids": [100],
            "wait": True
        }):
            with pytest.raises(AnsibleFailJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "Node nonexistingnode was specified, but does not exist on the cluster"
        assert self.mock_get_taskok.call_count == 0
        assert self.mock_post_vzdump.call_count == 0

    def test_fail_missing_storage(self):
        with set_module_args({
            "api_user": "root@pam",
            "api_password": "secret",
            "api_host": "127.0.0.1",
            "mode": "include",
            "storage": "nonexistingstorage",
            "vmids": [100],
            "wait": True
        }):
            with pytest.raises(AnsibleFailJson) as exc_info:
                proxmox_backup.main()

        result = exc_info.value.args[0]
        assert result["msg"] == "Storage nonexistingstorage does not exist in the cluster"
        assert self.mock_get_taskok.call_count == 0
        assert self.mock_post_vzdump.call_count == 0

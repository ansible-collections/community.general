#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup
short_description: Backup management of instances in Proxmox VE cluster
version_added: 10.0.0
description:
  - Allows you to create/delete/restore backups for a given instance in Proxmox VE cluster.
  - Supports both KVM and LXC.
  - Offers the GUI functionality of creating a single backup as well as using the run-now functionality from the cluster backup.
  - The mininum required privileges to use this module are VM.Backup and Datastore.AllocateSpace
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 10.0.0
options:
  bandwidth:
    description:
      - Limit I/O bandwidth (in KiB/s). V(0) is unlimited.
    type: int
  backup_mode:
    description:
      - The mode how proxmox performs backups.
      - Check U(https://pve.proxmox.com/pve-docs/chapter-vzdump.html#_backup_modes) for an explanation of the differences.
    type: str
    choices: ['snapshot', 'suspend', 'stop']
    default: snapshot
  compress:
    description:
      - Enable additional compression of the backup archive.
      - V(0) will use the proxmox recommended value (currently zstd).
      - If a proxmox backup server is the storage backend, V(0) or V(zstd) is required.
    type: str
    choices: [ '0', '1', 'gzip', 'lzo', 'zstd' ]
  compression_threads:
    description:
      - The number of threads zstd will use to compress the backup.
      - 0 uses 50% of the available cores, anything larger then 0 will use exactly as many threads.
      - Requires V(compress) to be zstd.
    type: int
  description:
    description:
      - Specify the description for the backup.
      - Template string for generating notes for the backup(s). 
      - Can contain variables which will be replaced by their values. 
      - Currently supported are {{cluster}}, {{guestname}}, {{node}}, and {{vmid}}, but more might be added in the future. 
      - Needs to be a single line, newline and backslash need to be escaped as '\n' and '\\' respectively.
    default: '{{guestname}}'
    type: str
  fleecing:
    description:
      - Enable backup fleecing. Works only for virtual machines and their disks.
      - Must be entered as a string, containing key-value pairs in a list:
      - [[enabled=]<1|0>] [,storage=<storage ID>]]
    type: str
  notification_mode:
    description:
      - Determine which notification system to use.
    type: str
    choices: ['auto','legacy-sendmail', 'notification-system']
    default: auto
  mode:
    description:
      - Specifices the mode to select backup targets.
    type: list
    contains: str
    choices: ['include', 'all', 'pool']
    required: true
  node:
    description:
      - Only execute the backup job for the given node.
    type: str
  performance_tweaks:
    description:
      - Enable other performance-related settings.
      - Must be entered as a string, containing comma separated key-value pairs:
      - [max-workers=<integer>] [,pbs-entries-max=<integer>]
    type: str
  pool:
    description:
      - Specify a pool name for the of guests to the given pool.
      - Required, when O(mode) is V(pool).
      - Also required, when your user only has VM.Backup permission for this single pool.
    type: str
  protected:
    description:
      - Mark backups as protected.
    type: bool
  retention:
    description:
      - Use these retention options instead of those from the storage configuration.
      - Enter as a comma-separated list of key-value pairs. Options are:
      - [keep-all=<1|0>] [,keep-daily=<N>] [,keep-hourly=<N>] [,keep-last=<N>] [,keep-monthly=<N>] [,keep-weekly=<N>] [,keep-yearly=<N>]
      - Requires Datastore.Allocate permission for the storage endpoint.
    type: str
  storage:
    description:
      - Store the backup archive on this storage on the proxmox host.
    type: str
    required: true
  vmids:
    description:
      - The instance ids to be backed up.
      - Only valid, if O(mode) is V(include).
    type: list
    contains: int
  wait:
    description:
      - Wait for the backup to be finished.
    type: bool
    default: false
  wait_timeout:
    description:
      - Seconds to wait for the backup to be finished.
      - Will only be evaluated, if O(wait) is V(true)
    type: int
    default: 10
notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
requirements: [ "proxmoxer", "requests" ]
author: IamLunchbox
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
'''

EXAMPLES = r'''
- name: Backup all vms in the proxmox cluster to storage mypbs
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    storage: mypbs
    all: true

- name: Backup vmid 100 to storage mypbs and set an individual retention
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    backup-mode: stop
    retention: keep-daily=5, keep-last=14, keep-monthly=4, keep-weekly=4, keep-yearly=0
    storage: mypbs
    vmid: 100
'''

RETURN = r'''#'''

import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxBackupAnsible(ProxmoxAnsible):

    def _get_permissions(self) -> dict:
        return self.proxmox_api.access.permissions.get()

    def _get_resources(self, resource_type=None) -> dict:
        return self.proxmox_api.cluster.resources.get(type=resource_type)

    def _get_relevant_nodes(self, node) -> list:
        nodes = [item['node'] for item in self._get_resources("node") if item['status'] == "online"]
        if node and node not in nodes:
            self.module.fail_json(msg=f'Node {node} was specified, but does not exist on the cluster')
        elif node:
            return [node]
        return nodes

    def _check_storage_permissions(self, permissions: dict, storage: str, bandwidth: int, performance: str, retention: bool) -> None:
        # Check for Datastore.AllocateSpace in the permission tree
        if "/" in permissions.keys() and permissions["/"].get("Datastore.AllocateSpace", 0) == 1:
            pass
        elif "/storage" in permissions.keys() and permissions["/storage"].get("Datastore.AllocateSpace", 0) == 1:
            pass
        elif f"/storage/{storage}" in permissions.keys() and permissions[f"/storage/{storage}"].get("Datastore.AllocateSpace", 0) == 1:
            pass
        else:
            self.module.exit_json(changed=False,
                                  msg="Insufficient permission: Datastore.AllocateSpace is missing.")
        if (bandwidth or performance) and permissions["/"].get("Sys.Modify", 0) == 0:
            self.module.exit_json(changed=False,
                                  msg="Insufficient permission: Requested performance tweaks or bandwidth settings require Sys.Modify /.")
        if retention:
            if "/" in permissions.keys() and permissions["/"].get(
                    "Datastore.Allocate", 0) == 1:
                pass
            elif "/storage" in permissions.keys() and permissions["/storage"].get("Datastore.Allocate", 0) == 1:
                pass
            elif f"/storage/{storage}" in permissions.keys() and permissions[f"/storage/{storage}"].get("Datastore.Allocate", 0) == 1:
                pass
            else:
                self.module.exit_json(changed=False,
                                      msg="Insufficient permissions: Custom retention was requested, but Datastore.Allocate is missing.")

    def _check_vmid_backup_permission(self, permissions, vmids, pool) -> None:
        sufficient_permissions = False
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif "/vms" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif pool and f"/pool/{pool}" in permissions.keys() and permissions[f"/pool/{pool}"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif pool and f"/pool/{pool}/vms" in permissions.keys() and permissions[f"/pool/{pool}/vms"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True

        if not sufficient_permissions:
            # Since VM.Backup can be given for each vmid at a time, iterate through all of them
            # and check, if the permission is set
            failed_vmids = []
            for vm in vmids:
                if f"/vms/{str(vm)}" in permissions.keys() and permissions[f"/vms/{str(vm)}"].get("VM.Backup", 1) == 0:
                    failed_vmids.append(str(vm))
            if failed_vmids:
                self.module.exit_json(changed=False,
                                      msg=f"Insufficient permissions: You dont have the VM.Backup permission for VMID {', '.join(failed_vmids)}.")
            sufficient_permissions = True
        # Finally, when no check succeeded, fail
        if not sufficient_permissions:
            self.module.exit_json(changed=False,
                                  msg="Insufficient permissions: You dont have the VM.Backup permission.")

    def _check_general_backup_permission(self, permissions, pool) -> None:
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            pass
        elif "/vms" in permissions.keys() and permissions["vms"].get("VM.Backup", 0) == 1:
            pass
        elif pool and f"/pool/{pool}" in permissions.keys() and permissions[f"/pool/{pool}"].get(
                "VM.Backup", 0) == 1:
            pass
        else:
            self.module.exit_json(changed=False,
                                  msg="Insufficient permissions: You dont have the VM.Backup permission.")

    def _check_if_storage_exists(self, storage: str, node: str) -> None:
        storages = self.get_storages(type=None)
        # Loop through all cluster storages and find out, if one has the correct name
        validated_storagepath = [storageentry for storageentry in storages if storageentry['storage'] == storage]
        if not validated_storagepath:
            self.module.exit_json(changed=False,
                                  msg=f"The storage {storage} does not exist in the cluster")

        # Check if the node specified for backups has access to the configured storage
        # validated_storagepath[0].get('shared') will be either 0 if unshared, None if unset or 1 if shared
        if node and not validated_storagepath[0].get('shared'):
            if node not in validated_storagepath[0].get('nodes').split(","):
                self.module.exit_json(changed=False,
                                      msg=f"The storage {storage} is not accessible for node {node}")

    def _check_vmids(self, vmids: list) -> None:
        vm_resources = self._get_resources("vm")
        if not vm_resources:
            self.module.warn(msg="VM.Audit permission is missing or there are no VMs. This task will fail if one VMID does not exist.")
        vmids_not_found = [vm for vm in vmids if vm not in [current_vm['vmid'] for current_vm in vm_resources]]
        if vmids_not_found:
            self.module.warn(msg=f"VMIDs {', '.join(vmids_not_found)} not found. This task will fail if one VMID does not exist.")

    def _wait_for_timeout(self, timeout: int, tasks: dict) -> None:
        while timeout:
            for node in tasks:
                if not tasks[node]["status"]:
                    try:
                        status = self.proxmox_api.nodes(node).tasks(
                            tasks[node]['upid']).status.get()
                        if status['status'] == 'stopped' and status['exitstatus'] == 'OK':
                            tasks[node].update({"status": "success"})
                        if status['status'] == 'stopped' and status['exitstatus'] in ('job errors',):
                            tasks[node].update({"status": "failed"})
                    except Exception as e:
                        self.module.fail_json(
                            msg=f'Unable to retrieve API task ID from node {node}: {e}')
            time.sleep(1)
            timeout -= 1
        else:
            logs = []
            for node in tasks:
                if not tasks[node]["status"] or tasks[node]["status"] != "success":
                    logs.append(f"{node}: {self.proxmox_api.nodes(node).tasks(tasks['node']['upid']).log.get()[-4]['t']}")
            self.module.fail_json(
                msg=f"Reached timeout while waiting for creating VM snapshot. "
                    f"These are the last log lines from the timeouted and failed nodes: {', '.join(logs)}")
        logs = []
        for node in tasks:
            if tasks[node]["status"] != "success":
                logs.append(
                    f"{node}: {self.proxmox_api.nodes(node).tasks(tasks['node']['upid']).log.get()[-4]['t']}")
        if logs:
            self.module.fail_json(
                msg=f"An error occured creating the backups. "
                    f"These are the last log lines from the failed nodes: {', '.join(logs)}")

    def permission_check(self, storage: str, mode: str, node: str, bandwidth: int, performance_tweaks: str, retention: bool, pool: str, vmids: list) -> None:
        permissions = self._get_permissions()
        self._check_if_storage_exists(storage, node)
        self._check_storage_permissions(permissions, storage, bandwidth, performance_tweaks, retention)

        if mode == "include":
            self._check_vmid_backup_permission(permissions, vmids, pool)
        else:
            self._check_general_backup_permission(permissions, pool)

    def prepare_request_parameters(self, module_arguments: dict) -> dict:
        # ensure only valid post parameters are passed to proxmox
        # list of dict items to replace with (new_val, old_val)
        post_params = [("bwlimit", "bandwidth"),
                       ("compress", "compress"),
                       ("fleecing", "fleecing"),
                       ("mode", "backup_mode"),
                       ("notes-template", "description"),
                       ("notification-mode", "notification_mode"),
                       ("performance", "performance_tweaks"),
                       ("pool", "pool"),
                       ("protected", "protected"),
                       ("prune-backups", "retention"),
                       ("storage", "storage"),
                       ("zstd", "compression_threads"),
                       ("vmid", "vmids")]
        request_body = {}
        for new, old in post_params:
            if module_arguments.get(old):
                request_body.update({new: module_arguments[old]})
        # Create comma separated list from vmids, the API expects so
        if request_body.get("vmid"):
            request_body.update({"vmid": ",".join(request_body.get("vmid"))})

        # remove pool option
        if request_body.get("vmid") or request_body.get("all"):
            if request_body.get("pool"):
                request_body.pop("pool")

        # remove whitespaces from option strings
        for key in ("prune-backups", "performance"):
            if request_body.get(key):
                request_body.update(
                    {key: request_body.get(key).replace(" ", "")})
        # convert booleans to 0/1
        for key in ("all", "protected"):
            if request_body.get(key):
                request_body.update({key: 1})

        return request_body

    def backup_create(self, module_arguments: dict, check_mode: bool) -> bool:
        request_body = self.prepare_request_parameters(module_arguments)
        if module_arguments['mode'] == "include":
            self._check_vmids(module_arguments['vmid'])
        node_endpoints = self._get_relevant_nodes(module_arguments['node'])
        # stop here, before anything gets changed
        if check_mode:
            return True

        task_ids = {}
        for node in node_endpoints:
            upid = self.proxmox_api.node(node).vzdump.post(**request_body)
            task_ids.update({node: {"upid": upid, "status": None}})

        # proxmox.api_task_ok does not suffice, since it only is true at `stopped` and `ok`
        if module_arguments['wait']:
            self._wait_for_timeout(module_arguments['wait_timeout'], task_ids)
        return True


def main():
    module_args = proxmox_auth_argument_spec()
    backup_args = {'bandwidth': {'type': 'int'},
                   'backup_mode': {'type': 'str','choices': ['snapshot', 'suspend', 'stop'],'default': 'snapshot'},
                   'compress': {'type': 'str', 'choices': ['0', '1', 'gzip', 'lzo', 'zstd']},
                   'compression_threads': {'type': 'int'},
                   'description': {'type': 'str', 'default': '{{guestname}}'},
                   'fleecing': {'type': 'str'},
                   'notification_mode': {'type': 'str', 'default': 'auto', 'choices': ['auto', 'legacy-sendmail', 'notification-system']},
                   'mode': {'type': 'str', 'required': True, 'choices': ['include', 'all', 'pool']},
                   'node': {'type': 'str'},
                   'performance_tweaks': {'type': 'str'},
                   'pool': {'type': 'str'},
                   'protected': {'type': 'bool'},
                   'retention': {'type': 'str'},
                   'storage': {'type': 'str', 'required': True},
                   'vmids': {'type': 'list', 'elements': 'int'},
                   'wait': {'type': 'bool', 'default': False},
                   'wait_timeout': {'type': 'int', 'default': 10}}
    module_args.update(backup_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ('mode', 'include', ('vmids',), True),
            ('mode', 'pool', ('pool',))]
        )
    proxmox = ProxmoxBackupAnsible(module)

    bandwidth = module.params['bandwidth']
    mode = module.params['mode']
    node = module.params['node']
    performance_tweaks = module.params['performance_tweaks']
    pool = module.params['pool']
    retention = module.params['retention']
    storage = module.params['storage']
    vmids = module.params['vmids']

    proxmox.permission_check(storage, mode, node, bandwidth, performance_tweaks, retention, pool, vmids)

    try:
        if proxmox.backup_create(dict(module.params), check_mode=module.check_mode):
            if module.check_mode:
                module.exit_json(changed=False, msg="Backups would be created")
            elif module.params['wait']:
                module.exit_json(changed=True, msg="Backups created and no errors reported")
            else:
                module.exit_json(changed=True, msg="Backups issued towards proxmox")

    except Exception as e:
        module.fail_json(msg=f"Creating backups failed with exception: {to_native(e)}")


if __name__ == '__main__':
    main()

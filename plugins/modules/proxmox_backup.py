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
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 10.0.0
options:
  bandwidth: # bwlimit
    description:
      - Limit I/O bandwidth (in KiB/s). V(0) is unlimited.
    type: int
  backup_mode: # mode
    description:
      - The mode how proxmox performs backups.
      - Check U(https://pve.proxmox.com/pve-docs/chapter-vzdump.html#_backup_modes) for an explanation of the differences.
    type: str
    choices: ['snapshot', 'suspend', 'stop']
    default: snapshot
  compress:
    description:
      - Enable additional compression of the backup archive.
      - O(0) will use the proxmox recommended value (currently zstd).
      - If a proxmox backup server is the storage backend, O(0) or O(zstd) is required.
    type: str
    choices: [ '0', '1', 'gzip', 'lzo', 'zstd' ]
  compression_threads: # zstd
    description:
      - The number of threads zstd will use to compress the backup.
      - 0 uses 50% of the available cores, anything larger then 0 will use exactly as many threads.
      - Requires O(compress) to be zstd.
    type: int
  description: # notes-template
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
  hostnames:
    description:
      - Instance names to be backed up or to exclude.
      - Will be ignored if vmids are provided.
    type: list
    contains: str
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
      - Will fail if you specify vmids, which reside on different nodes.
    type: str
  performance_tweaks: # performance
    description:
      - Enable other performance-related settings.
      - Must be entered as a string, containing comma separated key-value pairs:
      - [max-workers=<integer>] [,pbs-entries-max=<integer>]
    type: str
  poolname: #pool
    description:
      - Specify a poolname for the of guests to the given pool.
      - Required, when O(mode) is V(pool).
      - Also required, when your user only has VM.Backup permission for this single pool.
    type: str
  protected:
    description:
      - Mark backups as protected.
    type: bool
  retention: # prune-backups
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
  timeout:
    description:
      - Time to wait for the proxmox api to answer to backup tasks.
      type: int
      default: 10
  vmids:
    description:
      - The instance ids to be backed up or to exclude.
      - If not set, vmids will be fetched from PromoxAPI based on the hostnames. 
    type: list
    contains: int

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
    # def snapshot(self, vm, vmid):
    #     return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).snapshot
    #
    # def vmconfig(self, vm, vmid):
    #     return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).config
    #
    # def vmstatus(self, vm, vmid):
    #     return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).status
    # def _container_mp_get(self, vm, vmid):
    #     cfg = self.vmconfig(vm, vmid).get()
    #     mountpoints = {}
    #     for key, value in cfg.items():
    #         if key.startswith('mp'):
    #             mountpoints[key] = value
    #     return mountpoints
    #
    # def _container_mp_disable(self, vm, vmid, timeout, unbind, mountpoints, vmstatus):
    #     # shutdown container if running
    #     if vmstatus == 'running':
    #         self.shutdown_instance(vm, vmid, timeout)
    #     # delete all mountpoints configs
    #     self.vmconfig(vm, vmid).put(delete=' '.join(mountpoints))
    #
    # def _container_mp_restore(self, vm, vmid, timeout, unbind, mountpoints, vmstatus):
    #     # NOTE: requires auth as `root@pam`, API tokens are not supported
    #     # see https://pve.proxmox.com/pve-docs/api-viewer/#/nodes/{node}/lxc/{vmid}/config
    #     # restore original config
    #     self.vmconfig(vm, vmid).put(**mountpoints)
    #     # start container (if was running before snap)
    #     if vmstatus == 'running':
    #         self.start_instance(vm, vmid, timeout)
    #
    # def start_instance(self, vm, vmid, timeout):
    #     taskid = self.vmstatus(vm, vmid).start.post()
    #     while timeout:
    #         if self.api_task_ok(vm['node'], taskid):
    #             return True
    #         timeout -= 1
    #         if timeout == 0:
    #             self.module.fail_json(msg='Reached timeout while waiting for VM to start. Last line in task before timeout: %s' %
    #                                   self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
    #         time.sleep(1)
    #     return False
    #
    # def shutdown_instance(self, vm, vmid, timeout):
    #     taskid = self.vmstatus(vm, vmid).shutdown.post()
    #     while timeout:
    #         if self.api_task_ok(vm['node'], taskid):
    #             return True
    #         timeout -= 1
    #         if timeout == 0:
    #             self.module.fail_json(msg='Reached timeout while waiting for VM to stop. Last line in task before timeout: %s' %
    #                                   self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
    #         time.sleep(1)
    #     return False
    #
    # def snapshot_retention(self, vm, vmid, retention):
    #     # ignore the last snapshot, which is the current state
    #     snapshots = self.snapshot(vm, vmid).get()[:-1]
    #     if retention > 0 and len(snapshots) > retention:
    #         # sort by age, oldest first
    #         for snap in sorted(snapshots, key=lambda x: x['snaptime'])[:len(snapshots) - retention]:
    #             self.snapshot(vm, vmid)(snap['name']).delete()
    # def snapshot_remove(self, vm, vmid, timeout, snapname, force):
    #     if self.module.check_mode:
    #         return True
    #
    #     taskid = self.snapshot(vm, vmid).delete(snapname, force=int(force))
    #     while timeout:
    #         if self.api_task_ok(vm['node'], taskid):
    #             return True
    #         if timeout == 0:
    #             self.module.fail_json(msg='Reached timeout while waiting for removing VM snapshot. Last line in task before timeout: %s' %
    #                                   self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
    #
    #         time.sleep(1)
    #         timeout -= 1
    #     return False
    #
    # def snapshot_rollback(self, vm, vmid, timeout, snapname):
    #     if self.module.check_mode:
    #         return True
    #
    #     taskid = self.snapshot(vm, vmid)(snapname).post("rollback")
    #     while timeout:
    #         if self.api_task_ok(vm['node'], taskid):
    #             return True
    #         if timeout == 0:
    #             self.module.fail_json(msg='Reached timeout while waiting for rolling back VM snapshot. Last line in task before timeout: %s' %
    #                                   self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
    #
    #         time.sleep(1)
    #         timeout -= 1
    #     return False

    def check_permissions(self,storage,bandwidth,performance,retention) -> dict:
        permissions = self.proxmox_api.access.permissions.get()
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
            elif "/storage" in permissions.keys() and permissions[
                "/storage"].get("Datastore.Allocate", 0) == 1:
                pass
            elif f"/storage/{storage}" in permissions.keys() and permissions[
                f"/storage/{storage}"].get("Datastore.Allocate", 0) == 1:
                pass
            else:
                self.module.exit_json(changed=False,
                                      msg="Insufficient permissions: Custom retention was requested, but Datastore.Allocate is missing.")
        return permissions

    def check_vmid_permissions(self, permissions, vmids, poolname):
        sufficient_permissions = False
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif "/vms" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif poolname and f"/pool/{poolname}" in permissions.keys() and permissions[f"/pool/{poolname}"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True

        if not sufficient_permissions:
            # Since VM.Backup can be given for each vmid at a time, iterate through all of them
            # and check, if the permission is set
            failed_vmids = []
            for vm in vmids:
                if f"/vms/{str(vm)}" in permissions.keys() and permissions[
                    f"/vms/{str(vm)}"].get("VM.Backup", 1) == 0:
                    failed_vmids.append(str(vm))
            if failed_vmids:
                self.module.exit_json(changed=False,
                                      msg=f"Insufficient permissions: You dont have the VM.Backup permission for VMIDs {', '.join(failed_vmids)}.")
            sufficient_permissions = True
        # Finally, when not check succeeded, fail this check
        if not sufficient_permissions:
            self.module.exit_json(changed=False,
                                  msg=f"Insufficient permissions: You dont have the VM.Backup permission.")

    def check_pool_permissions(self, permissions, poolname):
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            pass
        elif "/vms" and "/vms" in permissions.keys() and permissions["vms"].get(
                "VM.Backup", 0) == 1:
            pass
        elif poolname and f"/pool/{poolname}" in permissions.keys() and permissions[f"/pool/{poolname}"].get(
                "VM.Backup", 0) == 1:
            pass
        else:
            self.module.exit_json(changed=False,
                                  msg=f"Insufficient permissions: You dont have the VM.Backup permission.")

    def check_all_permissions(self, permissions, poolname):
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            pass
        elif "/vms" and "/vms" in permissions.keys() and permissions["vms"].get(
                "VM.Backup", 0) == 1:
            pass
        elif poolname and f"/pool/{poolname}" in permissions.keys() and permissions[f"/pool/{poolname}"].get(
                "VM.Backup", 0) == 1:
            pass
        else:
            self.module.exit_json(changed=False,
                                  msg=f"Insufficient permissions: You dont have the VM.Backup permission."

    def check_vmids_for_consistency(self,vmids,hostnames,node) -> list:
        # derive vmid from hostnames
        if not vmids and hostnames:
            vmids = []
            for host in hostnames:
                vmids.append(self.get_vmid(host))
        if not vmids:
            self.module.exit_json(changed=False, msg="A vmid-specific mode was specified, but no vmids for filtering could be obtained")
        # Check, that the vms exist - get_vm() will throw and error if it does not
        for vm in vmids:
            vminfo = self.get_vm(vm)
            # TODO - verify with breakpoint, that this actually returns the expected dict
            if node and vminfo['node'] != node:
                self.module.exit_json(changed=False, msg="Node %s was specified, but vmid %s does not reside there" % (node, vm))
        return vmids

    def check_if_storage_exists(self, storage, node):
        storages = self.get_storages(type=None)
        # Loop through all cluster storages and find out, if one has the correct name
        validated_storagepath = [storageentry for storageentry in storages if storageentry['storage'] == storage]
        if not validated_storagepath:
            self.module.exit_json(changed=False,
                                  msg="The storage %s does not exist in the cluster" % storage)
        # Check if the node specified for backups has access to the configured storage
        # validated_storagepath[0].get('shared') will be either 0 if unshared, None if unset or 1 if shared
        if node and not validated_storagepath[0].get('shared'):
            if not node in validated_storagepath[0].get('nodes').split(","):
                self.module.exit_json(changed=False,
                                      msg="The storage %s is not accessible for node" % (storage,node))

    def backup_create(self,params: dict):

        while params['timeout']:
            if self.api_task_ok(vm['node'], taskid):
                break
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for creating VM snapshot. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
            timeout -= 1
        if vm['type'] == 'lxc' and unbind is True and mountpoints:
            self._container_mp_restore(vm, vmid, timeout, unbind, mountpoints, vmstatus)

        self.snapshot_retention(vm, vmid, retention)
        return timeout > 0




def main():
    module_args = proxmox_auth_argument_spec()
    backup_args = dict(
        bandwidth=dict(type='int'),
        backup_mode=dict(type='str', choices=['snapshot', 'suspend', 'stop'], default="snapshot"),
        compress=dict(type='str' ,default='0', choices=['0', '1', 'gzip', 'lzo', 'zstd']),
        compression_threads=dict(type='int', default=1),
        description=dict(type='str', default='{{guestname}}'),
        fleecing=dict(type='str', default=None),
        hostnames=dict(type='list', elements='str',default=None),
        notification_mode=dict(type='str', default='auto', choices=['auto','legacy-sendmail', 'notification-system']),
        mode=dict(type='str', required=True, choices=['include', 'exclude', 'all', 'pool']),
        node=dict(type='str'),
        performance_tweaks=dict(type='str'),
        poolname=dict(type='str'),
        protected=dict(type='bool'),
        retention=dict(type='str'),
        storage=dict(type='str', required=True),
        timeout=dict(type='int',default=10),
        vmids=dict(type='list', elements='int')
    )
    module_args.update(backup_args)
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[('vmids','hostnames')]
    )

    proxmox = ProxmoxBackupAnsible(module)
    bandwidth = module.params['bandwidth']
    hostnames = module.params['hostnames']
    mode = module.params['mode']
    node = module.params['node']
    performance_tweaks = module.params['performance_tweaks']
    poolname = module.params['poolname']
    retention = module.params['retention']
    storage = module.params['storage']
    vmids = module.params['vmids']

    proxmox.check_if_storage_exists(storage, node)
    all_permissions = proxmox.check_permissions(storage,bandwidth,performance_tweaks,retention)

    if mode == "include":
        vmids = proxmox.check_vmids_for_consistency(vmids, hostnames, node)
        proxmox.check_vmid_permissions(all_permissions,vmids,poolname)
    elif mode == "all":
        proxmox.check_all_permissions(all_permissions,poolname)
    else:
        proxmox.check_pool_permissions(all_permissions,poolname)

    try:
        if proxmox.backup_create(dict(module.params)):
            if module.check_mode:
                module.exit_json(changed=False, msg="Backup would be created")
            else:
                module.exit_json(changed=True, msg="Backup created")

    except Exception as e:
        module.fail_json(msg="Creating backups failed with exception: %s" % to_native(e))

if __name__ == '__main__':
    main()

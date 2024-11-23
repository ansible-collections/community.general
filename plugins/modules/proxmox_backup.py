#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, IamLunchbox <r.grieger@hotmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: proxmox_backup
author: "Raphael Grieger (@IamLunchbox) <r.grieger@hotmail.com>"
short_description: Start a VM backup in Proxmox VE cluster
version_added: 10.0.0
description:
  - Allows you to create backups of KVM and LXC guests in Proxmox VE cluster.
  - Offers the GUI functionality of creating a single backup as well as using the run-now functionality from the cluster backup schedule.
  - The mininum required privileges to use this module are VM.Backup and Datastore.AllocateSpace.
  - Most options are optional and if unspecified will be chosen by the Cluster and its default values.
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
      - Limit the I/O bandwidth (in KiB/s) to send the backup. 0 is unlimited.
    type: int
  backup_mode:
    description:
      - The mode how proxmox performs backups. The default is, to create a runtime snapshot including memory.
      - Check U(https://pve.proxmox.com/pve-docs/chapter-vzdump.html#_backup_modes) for an explanation of the differences.
    type: str
    choices: ['snapshot', 'suspend', 'stop']
    default: snapshot
  compress:
    description:
      - Enable additional compression of the backup archive.
      - 0 will use the proxmox recommended value, depending on your storage target.
    type: str
    choices: [ '0', '1', 'gzip', 'lzo', 'zstd' ]
  compression_threads:
    description:
      - The number of threads zstd will use to compress the backup.
      - 0 uses 50% of the available cores, anything larger then 0 will use exactly as many threads.
      - Is ignored if you specify O(compress=gzip) or O(compress=lzo)
    type: int
  description:
    description:
      - Specify the description for the backup.
      - Template string for generating notes for the backup(s).
      - Can contain variables which will be replaced by their values.
      - Currently supported are {{cluster}}, {{guestname}}, {{node}}, and {{vmid}}, but more might be added in the future.
      - Needs to be a single line, newline and backslash need to be escaped as `\n` and `\\` respectively.
    default: '{{guestname}}'
    type: str
  fleecing:
    description:
      - Enable backup fleecing. Works only for virtual machines and their disks.
      - Must be entered as a string, containing key-value pairs in a list.
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
    choices: ['include', 'all', 'pool']
    required: true
    type: str
  node:
    description:
      - Only execute the backup job for the given node.
      - This option is usually used if O(mode=all).
      - If you specify a node id and your vmids or pool do not reside there, they will not be backed up!
    type: str
  performance_tweaks:
    description:
      - Enable other performance-related settings.
      - Must be entered as a string, containing comma separated key-value pairs.
    type: str
  pool:
    description:
      - Specify a pool name to limit backups to guests to the given pool.
      - Required, when O(mode=pool).
      - Also required, when your user only has VM.Backup permission for this single pool.
    type: str
  protected:
    description:
      - Mark backups as protected.
      - "Might fail the task due to this bug: U(https://bugzilla.proxmox.com/show_bug.cgi?id=4289)"
    type: bool
  retention:
    description:
      - >
        Use custom retention options instead of those from the default cluster
        configuration (which is usually 'keep-all').
      - Requires Datastore.Allocate permission at the storage endpoint.
      - >
        Specifying a retention time other than V(keep-all=1) might trigger pruning on the datastore,
        if an existing backup would be pruned due to your specified timeframe and
        will need Datastore.Modify or Datastore.Prune permissions on the backup storage.
      - >
        If you are unsure, if your cluster uses keep-all as a default, you can set
        V(keep-all=1) to safeguard against unintended pruning or permission errors.
    type: str
  storage:
    description:
      - Store the backup archive on this storage on the proxmox host.
    type: str
    required: true
  vmids:
    description:
      - The instance ids to be backed up.
      - Only valid, if O(mode=include).
    type: list
    elements: int
  wait:
    description:
      - Wait for the backup to be finished.
    type: bool
    default: false
  wait_timeout:
    description:
      - Seconds to wait for the backup to be finished.
      - Will only be evaluated, if O(wait=true).
    type: int
    default: 10
notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
requirements: ["proxmoxer", "requests"]
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
    mode: all

- name: Backup VMID 100 by stopping it and set an individual retention
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    backup-mode: stop
    mode: include
    retention: keep-daily=5, keep-last=14, keep-monthly=4, keep-weekly=4, keep-yearly=0
    storage: mypbs
    vmid: [100]

- name: Backup all vms on node mynode to storage mypbs
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: anotherclusternode
    storage: mypbs
    mode: all
    node: mynode

- name: Use all the options, since you have all permissions
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: rootpassword
    api_host: node1
    bandwidth: 1000
    backup_mode: suspend
    compress: zstd
    compression_threads: 0
    description: test123
    mode: include
    node: node1
    notification_mode: notification-system
    protected: true
    retention: keep-monthly=1 ,keep-weekly=1
    storage: mypbs
    vmids: [100]
    wait: true
    wait_timeout: 30
'''

RETURN = r'''
backups:
  description: List of nodes and their task IDs.
  returned: on success
  type: list
  elements: dict
  contains:
    node:
      description: Node id.
      returned: on success
      type: str
    status:
      description: Last known task status. Will be unknown, if O(wait=false).
      returned: on success
      type: str
      choices: ['unknown', 'success', 'failed']
    upid:
      description: Proxmox cluster UPID, which is needed to lookup task info.
      returned: on success
      type: str
'''

import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxBackupAnsible(ProxmoxAnsible):

    def _get_permissions(self) -> dict:
        return self.proxmox_api.access.permissions.get()

    def _get_resources(self, resource_type=None) -> dict:
        return self.proxmox_api.cluster.resources.get(type=resource_type)

    def _post_backup_request(self, request_body: dict, node_endpoints: list) -> list:
        task_ids = []

        for node in node_endpoints:
            upid = self.proxmox_api.nodes(node).vzdump.post(**request_body)
            task_ids.extend([{"node": node, "upid": upid, "status": "unknown", "log": "%s" % self.proxmox_api.nodes(node).tasks(upid).log.get()[-4:]}])
        return task_ids

    def _check_relevant_nodes(self, node: str) -> list:
        nodes = [item["node"] for item in self._get_resources("node") if item["status"] == "online"]
        if node and node not in nodes:
            self.module.fail_json(msg="Node %s was specified, but does not exist on the cluster" % node)
        elif node:
            return [node]
        return nodes

    def _check_storage_permissions(self, permissions: dict, storage: str, bandwidth: int, performance: str, retention: bool) -> None:
        # Check for Datastore.AllocateSpace in the permission tree
        if "/" in permissions.keys() and permissions["/"].get("Datastore.AllocateSpace", 0) == 1:
            pass
        elif "/storage" in permissions.keys() and permissions["/storage"].get("Datastore.AllocateSpace", 0) == 1:
            pass
        elif "/storage/" + storage in permissions.keys() and permissions["/storage/" + storage].get("Datastore.AllocateSpace", 0) == 1:
            pass
        else:
            self.module.fail_json(changed=False,
                                  msg="Insufficient permission: Datastore.AllocateSpace is missing.")
        if (bandwidth or performance) and permissions["/"].get("Sys.Modify", 0) == 0:
            self.module.fail_json(changed=False,
                                  msg="Insufficient permission: Performance_tweaks and bandwidth require 'Sys.Modify' permission for '/'.")
        if retention:
            if "/" in permissions.keys() and permissions["/"].get(
                    "Datastore.Allocate", 0) == 1:
                pass
            elif "/storage" in permissions.keys() and permissions["/storage"].get("Datastore.Allocate", 0) == 1:
                pass
            elif "/storage/" + storage in permissions.keys() and permissions["/storage/" + storage].get("Datastore.Allocate", 0) == 1:
                pass
            else:
                self.module.fail_json(changed=False,
                                      msg="Insufficient permissions: Custom retention was requested, but Datastore.Allocate is missing.")

    def _check_vmid_backup_permission(self, permissions, vmids, pool) -> None:
        sufficient_permissions = False
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif "/vms" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif pool and "/pool/" + pool in permissions.keys() and permissions["/pool/" + pool].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True
        elif pool and "/pool/" + pool + "/vms" in permissions.keys() and permissions["/pool/" + pool + "/vms"].get(
                "VM.Backup", 0) == 1:
            sufficient_permissions = True

        if not sufficient_permissions:
            # Since VM.Backup can be given for each vmid at a time, iterate through all of them
            # and check, if the permission is set
            failed_vmids = []
            for vm in vmids:
                if "/vms/" + str(vm) in permissions.keys() and permissions["/vms/" + str(vm)].get("VM.Backup", 1) == 0:
                    failed_vmids.append(str(vm))
            if failed_vmids:
                self.module.fail_json(changed=False, msg="Insufficient permissions: "
                                                         "You dont have the VM.Backup permission for VMID %s."
                                                         % ', '.join(failed_vmids))
            sufficient_permissions = True
        # Finally, when no check succeeded, fail
        if not sufficient_permissions:
            self.module.fail_json(changed=False, msg="Insufficient permissions: You dont have the VM.Backup permission.")

    def _check_general_backup_permission(self, permissions, pool) -> None:
        if "/" in permissions.keys() and permissions["/"].get(
                "VM.Backup", 0) == 1:
            pass
        elif "/vms" in permissions.keys() and permissions["/vms"].get("VM.Backup", 0) == 1:
            pass
        elif pool and "/pool/" + pool in permissions.keys() and permissions["/pool/" + pool].get(
                "VM.Backup", 0) == 1:
            pass
        else:
            self.module.fail_json(changed=False, msg="Insufficient permissions: You dont have the VM.Backup permission.")

    def _check_if_storage_exists(self, storage: str, node: str) -> None:
        storages = self.get_storages(type=None)
        # Loop through all cluster storages and find out, if one has the correct name
        validated_storagepath = [storageentry for storageentry in storages if storageentry['storage'] == storage]
        if not validated_storagepath:
            self.module.fail_json(changed=False,
                                  msg="The storage %s does not exist in the cluster." % storage)

        # Check if the node specified for backups has access to the configured storage
        # validated_storagepath[0].get('shared') will be either 0 if unshared, None if unset or 1 if shared
        if node and not validated_storagepath[0].get('shared'):
            if node not in validated_storagepath[0].get('nodes').split(","):
                self.module.fail_json(changed=False, msg="The storage %s is not accessible for node %s." % (storage, node))

    def _check_vmids(self, vmids: list) -> None:
        vm_resources = [vm['vmid'] for vm in self._get_resources("vm")]
        if not vm_resources:
            self.module.warn(msg="VM.Audit permission is missing or there are no VMs. This task will fail if one VMID does not exist.")
        vmids_not_found = [vm for vm in vmids if vm not in vm_resources]
        if vmids_not_found:
            self.module.warn(msg="VMIDs %s not found. This task will fail if one VMID does not exist." % ', '.join(vmids_not_found))

    def _wait_for_timeout(self, timeout: int, raw_tasks: list) -> list:

        # filter all entries, which did not get a task id from the Cluster
        tasks = []
        for node in raw_tasks:
            if node["upid"] != "OK":
                tasks.append(node)

        start_time = time.time()
        # iterate through the task ids and check their values
        while True:
            for node in tasks:
                if node["status"] == "unknown":
                    try:
                        # proxmox.api_task_ok does not suffice, since it only is true at `stopped` and `ok`
                        status = self.proxmox_api.nodes(node["node"]).tasks(node["upid"]).status.get()
                        if status["status"] == "stopped" and status["exitstatus"] == "OK":
                            node["status"] = "success"
                        if status["status"] == "stopped" and status["exitstatus"] in ("job errors",):
                            node["status"] = "failed"
                    except Exception as e:
                        self.module.fail_json(
                            msg='Unable to retrieve API task ID from node %s: %s' % (node["node"], e))
            if len([item for item in tasks if item["status"] != "unknown"]) == len(tasks):
                break
            if time.time() > start_time + timeout:
                timeouted_nodes = [node["node"] for node in tasks if node["status"] == "unknown"]
                failed_nodes = [node["node"] for node in tasks if node["status"] == "failed"]
                if failed_nodes:
                    self.module.fail_json(
                        msg="Reached timeout while waiting for backup task. "
                            "Nodes, who reached the timeout: %s. "
                            "Nodes, which failed: %s" % (', '.join(timeouted_nodes), ', '.join(failed_nodes)))
                self.module.fail_json(
                    msg="Reached timeout while waiting for creating VM snapshot. "
                        "Nodes who reached the timeout: %s." % (', '.join(timeouted_nodes)))
            time.sleep(1)
        error_logs = []
        for node in tasks:
            if node["status"] == "failed":
                error_logs.append("%s: %s" % (node, self.proxmox_api.nodes(node["node"]).tasks(node["upid"]).log.get()[-4:]))
        if error_logs:
            self.module.fail_json(msg="An error occured creating the backups. "
                                      "These are the last log lines from the failed nodes: %s" % ', '.join(error_logs))

        for node in tasks:
            node["log"] = "%s" % self.proxmox_api.nodes(node["node"]).tasks(node['upid']).log.get()[-4:]
        return tasks

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

        # Set mode specific values
        if module_arguments["mode"] == "include":
            request_body.pop("pool", None)
            request_body["all"] = 0
        elif module_arguments["mode"] == "all":
            request_body.pop("vmid", None)
            request_body.pop("pool", None)
            request_body["all"] = 1
        elif module_arguments["mode"] == "pool":
            request_body.pop("vmid", None)
            request_body["all"] = 0

        # Create comma separated list from vmids, the API expects so
        if request_body.get("vmid"):
            request_body.update({"vmid": ",".join([str(vmid) for vmid in request_body.get("vmid")])})

        # remove whitespaces from option strings
        for key in ("prune-backups", "performance"):
            if request_body.get(key):
                request_body[key] = request_body[key].replace(" ", "")
        # convert booleans to 0/1
        for key in ("protected",):
            if request_body.get(key):
                request_body[key] = 1
        return request_body

    def backup_create(self, module_arguments: dict, check_mode: bool) -> list:
        request_body = self.prepare_request_parameters(module_arguments)
        if module_arguments["mode"] == "include":
            self._check_vmids(module_arguments["vmids"])
        node_endpoints = self._check_relevant_nodes(module_arguments["node"])
        # stop here, before anything gets changed
        if check_mode:
            return []

        task_ids = self._post_backup_request(request_body, node_endpoints)
        updated_task_ids = []
        if module_arguments["wait"]:
            updated_task_ids = self._wait_for_timeout(module_arguments["wait_timeout"], task_ids)
        return updated_task_ids if updated_task_ids else task_ids


def main():
    module_args = proxmox_auth_argument_spec()
    backup_args = {'bandwidth': {'type': 'int'},
                   'backup_mode': {'type': 'str', 'choices': ['snapshot', 'suspend', 'stop'], 'default': 'snapshot'},
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
            ('mode', 'pool', ('pool',))
        ]
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
        result = proxmox.backup_create(dict(module.params), check_mode=module.check_mode)
        if module.check_mode:
            module.exit_json(changed=False, msg="Backups would be created")
        elif module.params['wait']:
            module.exit_json(backups=result, changed=True, msg="Backups created and no errors reported")
        else:
            module.exit_json(backups=result, changed=True, msg="Backups issued towards proxmox")

    except Exception as e:
        module.fail_json(msg="Creating backups failed with exception: %s" % to_native(e))


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, IamLunchbox <r.grieger@hotmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: proxmox_backup
author: "Raphael Grieger (@IamLunchbox) <r.grieger@hotmail.com>"
short_description: Start a VM backup in Proxmox VE cluster
version_added: 10.1.0
description:
  - Allows you to create backups of KVM and LXC guests in Proxmox VE cluster.
  - Offers the GUI functionality of creating a single backup as well as using the run-now functionality from the cluster backup
    schedule.
  - The mininum required privileges to use this module are C(VM.Backup) and C(Datastore.AllocateSpace) for the respective
    VMs and storage.
  - Most options are optional and if unspecified will be chosen by the Cluster and its default values.
  - Note that this module B(is not idempotent). It always starts a new backup (when not in check mode).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  backup_mode:
    description:
      - The mode how Proxmox performs backups. The default is, to create a runtime snapshot including memory.
      - Check U(https://pve.proxmox.com/pve-docs/chapter-vzdump.html#_backup_modes) for an explanation of the differences.
    type: str
    choices: ["snapshot", "suspend", "stop"]
    default: snapshot
  bandwidth:
    description:
      - Limit the I/O bandwidth (in KiB/s) to write backup. V(0) is unlimited.
    type: int
  change_detection_mode:
    description:
      - Set the change detection mode (available from Proxmox VE 8.3).
      - It is only used when backing up containers, Proxmox silently ignores this option when applied to kvm guests.
    type: str
    choices: ["legacy", "data", "metadata"]
  compress:
    description:
      - Enable additional compression of the backup archive.
      - V(0) will use the Proxmox recommended value, depending on your storage target.
    type: str
    choices: ["0", "1", "gzip", "lzo", "zstd"]
  compression_threads:
    description:
      - The number of threads zstd will use to compress the backup.
      - V(0) uses 50% of the available cores, anything larger than V(0) will use exactly as many threads.
      - Is ignored if you specify O(compress=gzip) or O(compress=lzo).
    type: int
  description:
    description:
      - Specify the description of the backup.
      - Needs to be a single line, newline and backslash need to be escaped as V(\\n) and V(\\\\) respectively.
      - If you need variable interpolation, you can set the content as usual through ansible jinja templating and/or let Proxmox
        substitute templates.
      - Proxmox currently supports V({{cluster}}), V({{guestname}}), V({{node}}), and V({{vmid}}) as templating variables.
        Since this is also a jinja delimiter, you need to set these values as raw jinja.
    default: "{{guestname}}"
    type: str
  fleecing:
    description:
      - Enable backup fleecing. Works only for virtual machines and their disks.
      - Must be entered as a string, containing key-value pairs in a list.
    type: str
  mode:
    description:
      - Specifices the mode to select backup targets.
    choices: ["include", "all", "pool"]
    required: true
    type: str
  node:
    description:
      - Only execute the backup job for the given node.
      - This option is usually used if O(mode=all).
      - If you specify a node ID and your vmids or pool do not reside there, they will not be backed up!
    type: str
  notification_mode:
    description:
      - Determine which notification system to use.
    type: str
    choices: ["auto", "legacy-sendmail", "notification-system"]
    default: auto
  performance_tweaks:
    description:
      - Enable other performance-related settings.
      - Must be entered as a string, containing comma separated key-value pairs.
      - 'For example: V(max-workers=2,pbs-entries-max=2).'
    type: str
  pool:
    description:
      - Specify a pool name to limit backups to guests to the given pool.
      - Required, when O(mode=pool).
      - Also required, when your user only has VM.Backup permission for this single pool.
    type: str
  protected:
    description:
      - Marks backups as protected.
      - '"Might fail, when the PBS backend has verify enabled due to this bug: U(https://bugzilla.proxmox.com/show_bug.cgi?id=4289)".'
    type: bool
  retention:
    description:
      - Use custom retention options instead of those from the default cluster configuration (which is usually V("keep-all=1")).
      - Always requires Datastore.Allocate permission at the storage endpoint.
      - Specifying a retention time other than V(keep-all=1) might trigger pruning on the datastore, if an existing backup
        should be deleted due to your specified timeframe.
      - Deleting requires C(Datastore.Modify) or C(Datastore.Prune) permissions on the backup storage.
    type: str
  storage:
    description:
      - Store the backup archive on this storage.
    type: str
    required: true
  vmids:
    description:
      - The instance IDs to be backed up.
      - Only valid, if O(mode=include).
    type: list
    elements: int
  wait:
    description:
      - Wait for the backup to be finished.
      - Fails, if job does not succeed successfully within the given timeout.
    type: bool
    default: false
  wait_timeout:
    description:
      - Seconds to wait for the backup to be finished.
      - Will only be evaluated, if O(wait=true).
    type: int
    default: 10
requirements: ["proxmoxer", "requests"]
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Backup all vms in the Proxmox cluster to storage mypbs
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: secret
    api_host: node1
    storage: mypbs
    mode: all

- name: Backup VMID 100 by stopping it and set an individual retention
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: secret
    api_host: node1
    backup-mode: stop
    mode: include
    retention: keep-daily=5, keep-last=14, keep-monthly=4, keep-weekly=4, keep-yearly=0
    storage: mypbs
    vmid: [100]

- name: Backup all vms on node node2 to storage mypbs and wait for the task to finish
  community.general.proxmox_backup:
    api_user: test@pve
    api_password: 1q2w3e
    api_host: node2
    storage: mypbs
    mode: all
    node: node2
    wait: true
    wait_timeout: 30

- name: Use all the options
  community.general.proxmox_backup:
    api_user: root@pam
    api_password: secret
    api_host: node1
    bandwidth: 1000
    backup_mode: suspend
    compress: zstd
    compression_threads: 0
    description: A single backup for {% raw %}{{ guestname }}{% endraw %}
    mode: include
    notification_mode: notification-system
    protected: true
    retention: keep-monthly=1, keep-weekly=1
    storage: mypbs
    vmids:
      - 100
      - 101
"""

RETURN = r"""
backups:
  description: List of nodes and their task IDs.
  returned: on success
  type: list
  elements: dict
  contains:
    node:
      description: Node ID.
      returned: on success
      type: str
    status:
      description: Last known task status. Will be unknown, if O(wait=false).
      returned: on success
      type: str
      choices: ["unknown", "success", "failed"]
    upid:
      description: >-
        Proxmox cluster UPID, which is needed to lookup task info. Returns OK, when a cluster node did not create a task after
        being called, for example due to no matching targets.
      returned: on success
      type: str
"""

import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible, proxmox_auth_argument_spec


def has_permission(permission_tree, permission, search_scopes, default=0, expected=1):
    return any(permission_tree.get(scope, {}).get(permission, default) == expected for scope in search_scopes)


class ProxmoxBackupAnsible(ProxmoxAnsible):

    def _get_permissions(self):
        return self.proxmox_api.access.permissions.get()

    def _get_resources(self, resource_type=None):
        return self.proxmox_api.cluster.resources.get(type=resource_type)

    def _get_tasklog(self, node, upid):
        return self.proxmox_api.nodes(node).tasks(upid).log.get()

    def _get_taskok(self, node, upid):
        return self.proxmox_api.nodes(node).tasks(upid).status.get()

    def _post_vzdump(self, node, request_body):
        return self.proxmox_api.nodes(node).vzdump.post(**request_body)

    def request_backup(
            self,
            request_body,
            node_endpoints):
        task_ids = []

        for node in node_endpoints:
            upid = self._post_vzdump(node, request_body)
            if upid != "OK":
                tasklog = ", ".join(logentry["t"] for logentry in self._get_tasklog(node, upid))
            else:
                tasklog = ""
            task_ids.extend([{"node": node, "upid": upid, "status": "unknown", "log": "%s" % tasklog}])
        return task_ids

    def check_relevant_nodes(self, node):
        nodes = [
            item["node"]
            for item in self._get_resources("node")
            if item["status"] == "online"
        ]
        if node and node not in nodes:
            self.module.fail_json(msg="Node %s was specified, but does not exist on the cluster" % node)
        elif node:
            return [node]
        return nodes

    def check_storage_permissions(
            self,
            permissions,
            storage,
            bandwidth,
            performance,
            retention):
        # Check for Datastore.AllocateSpace in the permission tree
        if not has_permission(permissions, "Datastore.AllocateSpace", search_scopes=["/", "/storage/", "/storage/" + storage]):
            self.module.fail_json(changed=False, msg="Insufficient permission: Datastore.AllocateSpace is missing")

        if (bandwidth or performance) and has_permission(permissions, "Sys.Modify", search_scopes=["/"], expected=0):
            self.module.fail_json(changed=False, msg="Insufficient permission: Performance_tweaks and bandwidth require 'Sys.Modify' permission for '/'")

        if retention:
            if not has_permission(permissions, "Datastore.Allocate", search_scopes=["/", "/storage", "/storage/" + storage]):
                self.module.fail_json(changed=False, msg="Insufficient permissions: Custom retention was requested, but Datastore.Allocate is missing")

    def check_vmid_backup_permission(self, permissions, vmids, pool):
        sufficient_permissions = has_permission(permissions, "VM.Backup", search_scopes=["/", "/vms"])
        if pool and not sufficient_permissions:
            sufficient_permissions = has_permission(permissions, "VM.Backup", search_scopes=["/pool/" + pool, "/pool/" + pool + "/vms"])

        if not sufficient_permissions:
            # Since VM.Backup can be given for each vmid at a time, iterate through all of them
            # and check, if the permission is set
            failed_vmids = []
            for vm in vmids:
                vm_path = "/vms/" + str(vm)
                if has_permission(permissions, "VM.Backup", search_scopes=[vm_path], default=1, expected=0):
                    failed_vmids.append(str(vm))
            if failed_vmids:
                self.module.fail_json(
                    changed=False, msg="Insufficient permissions: "
                    "You dont have the VM.Backup permission for VMID %s" %
                    ", ".join(failed_vmids))
            sufficient_permissions = True
        # Finally, when no check succeeded, fail
        if not sufficient_permissions:
            self.module.fail_json(changed=False, msg="Insufficient permissions: You do not have the VM.Backup permission")

    def check_general_backup_permission(self, permissions, pool):
        if not has_permission(permissions, "VM.Backup", search_scopes=["/", "/vms"] + (["/pool/" + pool] if pool else [])):
            self.module.fail_json(changed=False, msg="Insufficient permissions: You dont have the VM.Backup permission")

    def check_if_storage_exists(self, storage, node):
        storages = self.get_storages(type=None)
        # Loop through all cluster storages and get all matching storages
        validated_storagepath = [storageentry for storageentry in storages if storageentry["storage"] == storage]
        if not validated_storagepath:
            self.module.fail_json(
                changed=False,
                msg="Storage %s does not exist in the cluster" %
                storage)

    def check_vmids(self, vmids):
        cluster_vmids = [vm["vmid"] for vm in self._get_resources("vm")]
        if not cluster_vmids:
            self.module.warn(
                "VM.Audit permission is missing or there are no VMs. This task might fail if one VMID does not exist")
            return
        vmids_not_found = [str(vm) for vm in vmids if vm not in cluster_vmids]
        if vmids_not_found:
            self.module.warn(
                "VMIDs %s not found. This task will fail if one VMID does not exist" %
                ", ".join(vmids_not_found))

    def wait_for_timeout(self, timeout, raw_tasks):

        # filter all entries, which did not get a task id from the Cluster
        tasks = []
        ok_tasks = []
        for node in raw_tasks:
            if node["upid"] != "OK":
                tasks.append(node)
            else:
                ok_tasks.append(node)

        start_time = time.time()
        # iterate through the task ids and check their values
        while True:
            for node in tasks:
                if node["status"] == "unknown":
                    try:
                        # proxmox.api_task_ok does not suffice, since it only
                        # is true at `stopped` and `ok`
                        status = self._get_taskok(node["node"], node["upid"])
                        if status["status"] == "stopped" and status["exitstatus"] == "OK":
                            node["status"] = "success"
                        if status["status"] == "stopped" and status["exitstatus"] == "job errors":
                            node["status"] = "failed"
                    except Exception as e:
                        self.module.fail_json(msg="Unable to retrieve API task ID from node %s: %s" % (node["node"], e))
            if len([item for item in tasks if item["status"] != "unknown"]) == len(tasks):
                break
            if time.time() > start_time + timeout:
                timeouted_nodes = [
                    node["node"]
                    for node in tasks
                    if node["status"] == "unknown"
                ]
                failed_nodes = [node["node"] for node in tasks if node["status"] == "failed"]
                if failed_nodes:
                    self.module.fail_json(
                        msg="Reached timeout while waiting for backup task. "
                        "Nodes, who reached the timeout: %s. "
                        "Nodes, which failed: %s" %
                        (", ".join(timeouted_nodes), ", ".join(failed_nodes)))
                self.module.fail_json(
                    msg="Reached timeout while waiting for creating VM snapshot. "
                    "Nodes who reached the timeout: %s" %
                    ", ".join(timeouted_nodes))
            time.sleep(1)

        error_logs = []
        for node in tasks:
            if node["status"] == "failed":
                tasklog = ", ".join([logentry["t"] for logentry in self._get_tasklog(node["node"], node["upid"])])
                error_logs.append("%s: %s" % (node, tasklog))
        if error_logs:
            self.module.fail_json(
                msg="An error occured creating the backups. "
                "These are the last log lines from the failed nodes: %s" %
                ", ".join(error_logs))

        for node in tasks:
            tasklog = ", ".join([logentry["t"] for logentry in self._get_tasklog(node["node"], node["upid"])])
            node["log"] = tasklog

        # Finally, reattach ok tasks to show, that all nodes were contacted
        tasks.extend(ok_tasks)
        return tasks

    def permission_check(
            self,
            storage,
            mode,
            node,
            bandwidth,
            performance_tweaks,
            retention,
            pool,
            vmids):
        permissions = self._get_permissions()
        self.check_if_storage_exists(storage, node)
        self.check_storage_permissions(
            permissions, storage, bandwidth, performance_tweaks, retention)
        if mode == "include":
            self.check_vmid_backup_permission(permissions, vmids, pool)
        else:
            self.check_general_backup_permission(permissions, pool)

    def prepare_request_parameters(self, module_arguments):
        # ensure only valid post parameters are passed to proxmox
        # list of dict items to replace with (new_val, old_val)
        post_params = [("bwlimit", "bandwidth"),
                       ("compress", "compress"),
                       ("fleecing", "fleecing"),
                       ("mode", "backup_mode"),
                       ("notes-template", "description"),
                       ("notification-mode", "notification_mode"),
                       ("pbs-change-detection-mode", "change_detection_mode"),
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
            request_body.update({"vmid": ",".join(str(vmid) for vmid in request_body["vmid"])})

        # remove whitespaces from option strings
        for key in ("prune-backups", "performance"):
            if request_body.get(key):
                request_body[key] = request_body[key].replace(" ", "")
        # convert booleans to 0/1
        for key in ("protected",):
            if request_body.get(key):
                request_body[key] = 1
        return request_body

    def backup_create(
            self,
            module_arguments,
            check_mode,
            node_endpoints):
        request_body = self.prepare_request_parameters(module_arguments)
        # stop here, before anything gets changed
        if check_mode:
            return []

        task_ids = self.request_backup(request_body, node_endpoints)
        updated_task_ids = []
        if module_arguments["wait"]:
            updated_task_ids = self.wait_for_timeout(
                module_arguments["wait_timeout"], task_ids)
        return updated_task_ids if updated_task_ids else task_ids


def main():
    module_args = proxmox_auth_argument_spec()
    backup_args = {
        "backup_mode": {"type": "str", "default": "snapshot", "choices": ["snapshot", "suspend", "stop"]},
        "bandwidth": {"type": "int"},
        "change_detection_mode": {"type": "str", "choices": ["legacy", "data", "metadata"]},
        "compress": {"type": "str", "choices": ["0", "1", "gzip", "lzo", "zstd"]},
        "compression_threads": {"type": "int"},
        "description": {"type": "str", "default": "{{guestname}}"},
        "fleecing": {"type": "str"},
        "mode": {"type": "str", "required": True, "choices": ["include", "all", "pool"]},
        "node": {"type": "str"},
        "notification_mode": {"type": "str", "default": "auto", "choices": ["auto", "legacy-sendmail", "notification-system"]},
        "performance_tweaks": {"type": "str"},
        "pool": {"type": "str"},
        "protected": {"type": "bool"},
        "retention": {"type": "str"},
        "storage": {"type": "str", "required": True},
        "vmids": {"type": "list", "elements": "int"},
        "wait": {"type": "bool", "default": False},
        "wait_timeout": {"type": "int", "default": 10}}
    module_args.update(backup_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("mode", "include", ("vmids",), True),
            ("mode", "pool", ("pool",))
        ]
    )
    proxmox = ProxmoxBackupAnsible(module)
    bandwidth = module.params["bandwidth"]
    mode = module.params["mode"]
    node = module.params["node"]
    performance_tweaks = module.params["performance_tweaks"]
    pool = module.params["pool"]
    retention = module.params["retention"]
    storage = module.params["storage"]
    vmids = module.params["vmids"]

    proxmox.permission_check(
        storage,
        mode,
        node,
        bandwidth,
        performance_tweaks,
        retention,
        pool,
        vmids)
    if module.params["mode"] == "include":
        proxmox.check_vmids(module.params["vmids"])
    node_endpoints = proxmox.check_relevant_nodes(module.params["node"])
    try:
        result = proxmox.backup_create(module.params, module.check_mode, node_endpoints)
    except Exception as e:
        module.fail_json(msg="Creating backups failed with exception: %s" % to_native(e))

    if module.check_mode:
        module.exit_json(backups=result, changed=True, msg="Backups would be created")

    elif len([entry for entry in result if entry["upid"] == "OK"]) == len(result):
        module.exit_json(backups=result, changed=False, msg="Backup request sent to proxmox, no tasks created")

    elif module.params["wait"]:
        module.exit_json(backups=result, changed=True, msg="Backups succeeded")

    else:
        module.exit_json(backups=result, changed=True,
                         msg="Backup tasks created")


if __name__ == "__main__":
    main()

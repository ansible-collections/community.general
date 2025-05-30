#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: proxmox_snap
short_description: Snapshot management of instances in Proxmox VE cluster
version_added: 2.0.0
description:
  - Allows you to create/delete/restore snapshots from instances in Proxmox VE cluster.
  - Supports both KVM and LXC, OpenVZ has not been tested, as it is no longer supported on Proxmox VE.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 9.0.0
options:
  hostname:
    description:
      - The instance name.
    type: str
  vmid:
    description:
      - The instance ID.
      - If not set, will be fetched from PromoxAPI based on the hostname.
    type: str
  state:
    description:
      - Indicate desired state of the instance snapshot.
      - The V(rollback) value was added in community.general 4.8.0.
    choices: ['present', 'absent', 'rollback']
    default: present
    type: str
  force:
    description:
      - For removal from config file, even if removing disk snapshot fails.
    default: false
    type: bool
  unbind:
    description:
      - This option only applies to LXC containers.
      - Allows to snapshot a container even if it has configured mountpoints.
      - Temporarily disables all configured mountpoints, takes snapshot, and finally restores original configuration.
      - If running, the container will be stopped and restarted to apply config changes.
      - Due to restrictions in the Proxmox API this option can only be used authenticating as V(root@pam) with O(api_password),
        API tokens do not work either.
      - See U(https://pve.proxmox.com/pve-docs/api-viewer/#/nodes/{node}/lxc/{vmid}/config) (PUT tab) for more details.
    default: false
    type: bool
    version_added: 5.7.0
  vmstate:
    description:
      - Snapshot includes RAM.
    default: false
    type: bool
  description:
    description:
      - Specify the description for the snapshot. Only used on the configuration web interface.
      - This is saved as a comment inside the configuration file.
    type: str
  timeout:
    description:
      - Timeout for operations.
    default: 30
    type: int
  snapname:
    description:
      - Name of the snapshot that has to be created/deleted/restored.
    default: 'ansible_snap'
    type: str
  retention:
    description:
      - Remove old snapshots if there are more than O(retention) snapshots.
      - If O(retention) is set to V(0), all snapshots will be kept.
      - This is only used when O(state=present) and when an actual snapshot is created. If no snapshot is created, all existing
        snapshots will be kept.
    default: 0
    type: int
    version_added: 7.1.0

notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
requirements: ["proxmoxer", "requests"]
author: Jeffrey van Pelt (@Thulium-Drake)
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Create new container snapshot
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: present
    snapname: pre-updates

- name: Create new container snapshot and keep only the 2 newest snapshots
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: present
    snapname: snapshot-42
    retention: 2

- name: Create new snapshot for a container with configured mountpoints
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: present
    unbind: true # requires root@pam+password auth, API tokens are not supported
    snapname: pre-updates

- name: Remove container snapshot
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: absent
    snapname: pre-updates

- name: Rollback container snapshot
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: rollback
    snapname: pre-updates
"""

RETURN = r"""#"""

import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxSnapAnsible(ProxmoxAnsible):
    def snapshot(self, vm, vmid):
        return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).snapshot

    def vmconfig(self, vm, vmid):
        return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).config

    def vmstatus(self, vm, vmid):
        return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).status

    def _container_mp_get(self, vm, vmid):
        cfg = self.vmconfig(vm, vmid).get()
        mountpoints = {}
        for key, value in cfg.items():
            if key.startswith('mp'):
                mountpoints[key] = value
        return mountpoints

    def _container_mp_disable(self, vm, vmid, timeout, unbind, mountpoints, vmstatus):
        # shutdown container if running
        if vmstatus == 'running':
            self.shutdown_instance(vm, vmid, timeout)
        # delete all mountpoints configs
        self.vmconfig(vm, vmid).put(delete=' '.join(mountpoints))

    def _container_mp_restore(self, vm, vmid, timeout, unbind, mountpoints, vmstatus):
        # NOTE: requires auth as `root@pam`, API tokens are not supported
        # see https://pve.proxmox.com/pve-docs/api-viewer/#/nodes/{node}/lxc/{vmid}/config
        # restore original config
        self.vmconfig(vm, vmid).put(**mountpoints)
        # start container (if was running before snap)
        if vmstatus == 'running':
            self.start_instance(vm, vmid, timeout)

    def start_instance(self, vm, vmid, timeout):
        taskid = self.vmstatus(vm, vmid).start.post()
        while timeout >= 0:
            if self.api_task_ok(vm['node'], taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for VM to start. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
            time.sleep(1)
        return False

    def shutdown_instance(self, vm, vmid, timeout):
        taskid = self.vmstatus(vm, vmid).shutdown.post()
        while timeout >= 0:
            if self.api_task_ok(vm['node'], taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for VM to stop. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])
            time.sleep(1)
        return False

    def snapshot_retention(self, vm, vmid, retention):
        # ignore the last snapshot, which is the current state
        snapshots = self.snapshot(vm, vmid).get()[:-1]
        if retention > 0 and len(snapshots) > retention:
            # sort by age, oldest first
            for snap in sorted(snapshots, key=lambda x: x['snaptime'])[:len(snapshots) - retention]:
                self.snapshot(vm, vmid)(snap['name']).delete()

    def snapshot_create(self, vm, vmid, timeout, snapname, description, vmstate, unbind, retention):
        if self.module.check_mode:
            return True

        if vm['type'] == 'lxc':
            if unbind is True:
                # check if credentials will work
                # WARN: it is crucial this check runs here!
                # The correct permissions are required only to reconfig mounts.
                # Not checking now would allow to remove the configuration BUT
                # fail later, leaving the container in a misconfigured state.
                if (
                    self.module.params['api_user'] != 'root@pam'
                    or not self.module.params['api_password']
                ):
                    self.module.fail_json(msg='`unbind=True` requires authentication as `root@pam` with `api_password`, API tokens are not supported.')
                    return False
                mountpoints = self._container_mp_get(vm, vmid)
                vmstatus = self.vmstatus(vm, vmid).current().get()['status']
                if mountpoints:
                    self._container_mp_disable(vm, vmid, timeout, unbind, mountpoints, vmstatus)
            taskid = self.snapshot(vm, vmid).post(snapname=snapname, description=description)
        else:
            taskid = self.snapshot(vm, vmid).post(snapname=snapname, description=description, vmstate=int(vmstate))

        while timeout >= 0:
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

    def snapshot_remove(self, vm, vmid, timeout, snapname, force):
        if self.module.check_mode:
            return True

        taskid = self.snapshot(vm, vmid).delete(snapname, force=int(force))
        while timeout >= 0:
            if self.api_task_ok(vm['node'], taskid):
                return True
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for removing VM snapshot. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
            timeout -= 1
        return False

    def snapshot_rollback(self, vm, vmid, timeout, snapname):
        if self.module.check_mode:
            return True

        taskid = self.snapshot(vm, vmid)(snapname).post("rollback")
        while timeout >= 0:
            if self.api_task_ok(vm['node'], taskid):
                return True
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for rolling back VM snapshot. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
            timeout -= 1
        return False


def main():
    module_args = proxmox_auth_argument_spec()
    snap_args = dict(
        vmid=dict(required=False),
        hostname=dict(),
        timeout=dict(type='int', default=30),
        state=dict(default='present', choices=['present', 'absent', 'rollback']),
        description=dict(type='str'),
        snapname=dict(type='str', default='ansible_snap'),
        force=dict(type='bool', default=False),
        unbind=dict(type='bool', default=False),
        vmstate=dict(type='bool', default=False),
        retention=dict(type='int', default=0),
    )
    module_args.update(snap_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    proxmox = ProxmoxSnapAnsible(module)

    state = module.params['state']
    vmid = module.params['vmid']
    hostname = module.params['hostname']
    description = module.params['description']
    snapname = module.params['snapname']
    timeout = module.params['timeout']
    force = module.params['force']
    unbind = module.params['unbind']
    vmstate = module.params['vmstate']
    retention = module.params['retention']

    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and hostname:
        vmid = proxmox.get_vmid(hostname)
    elif not vmid:
        module.exit_json(changed=False, msg="Vmid could not be fetched for the following action: %s" % state)

    vm = proxmox.get_vm(vmid)

    if state == 'present':
        try:
            for i in proxmox.snapshot(vm, vmid).get():
                if i['name'] == snapname:
                    module.exit_json(changed=False, msg="Snapshot %s is already present" % snapname)

            if proxmox.snapshot_create(vm, vmid, timeout, snapname, description, vmstate, unbind, retention):
                if module.check_mode:
                    module.exit_json(changed=False, msg="Snapshot %s would be created" % snapname)
                else:
                    module.exit_json(changed=True, msg="Snapshot %s created" % snapname)

        except Exception as e:
            module.fail_json(msg="Creating snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, to_native(e)))

    elif state == 'absent':
        try:
            snap_exist = False

            for i in proxmox.snapshot(vm, vmid).get():
                if i['name'] == snapname:
                    snap_exist = True
                    continue

            if not snap_exist:
                module.exit_json(changed=False, msg="Snapshot %s does not exist" % snapname)
            else:
                if proxmox.snapshot_remove(vm, vmid, timeout, snapname, force):
                    if module.check_mode:
                        module.exit_json(changed=False, msg="Snapshot %s would be removed" % snapname)
                    else:
                        module.exit_json(changed=True, msg="Snapshot %s removed" % snapname)

        except Exception as e:
            module.fail_json(msg="Removing snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, to_native(e)))
    elif state == 'rollback':
        try:
            snap_exist = False

            for i in proxmox.snapshot(vm, vmid).get():
                if i['name'] == snapname:
                    snap_exist = True
                    continue

            if not snap_exist:
                module.exit_json(changed=False, msg="Snapshot %s does not exist" % snapname)
            if proxmox.snapshot_rollback(vm, vmid, timeout, snapname):
                if module.check_mode:
                    module.exit_json(changed=True, msg="Snapshot %s would be rolled back" % snapname)
                else:
                    module.exit_json(changed=True, msg="Snapshot %s rolled back" % snapname)

        except Exception as e:
            module.fail_json(msg="Rollback of snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, to_native(e)))


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_snap
short_description: Snapshot management of instances in Proxmox VE cluster
version_added: 2.0.0
description:
  - Allows you to create/delete/restore snapshots from instances in Proxmox VE cluster.
  - Supports both KVM and LXC, OpenVZ has not been tested, as it is no longer supported on Proxmox VE.
options:
  hostname:
    description:
      - The instance name.
    type: str
  vmid:
    description:
      - The instance id.
      - If not set, will be fetched from PromoxAPI based on the hostname.
    type: str
  state:
    description:
     - Indicate desired state of the instance snapshot.
     - The C(rollback) value was added in community.general 4.8.0.
    choices: ['present', 'absent', 'rollback']
    default: present
    type: str
  force:
    description:
      - For removal from config file, even if removing disk snapshot fails.
    default: no
    type: bool
  vmstate:
    description:
      - Snapshot includes RAM.
    default: no
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

notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
  - Supports C(check_mode).
requirements: [ "proxmoxer", "python >= 2.7", "requests" ]
author: Jeffrey van Pelt (@Thulium-Drake)
extends_documentation_fragment:
    - community.general.proxmox.documentation
'''

EXAMPLES = r'''
- name: Create new container snapshot
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: present
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
'''

RETURN = r'''#'''

import time
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR)


class ProxmoxSnapAnsible(ProxmoxAnsible):
    def snapshot(self, vm, vmid):
        return getattr(self.proxmox_api.nodes(vm['node']), vm['type'])(vmid).snapshot

    def snapshot_create(self, vm, vmid, timeout, snapname, description, vmstate):
        if self.module.check_mode:
            return True

        if vm['type'] == 'lxc':
            taskid = self.snapshot(vm, vmid).post(snapname=snapname, description=description)
        else:
            taskid = self.snapshot(vm, vmid).post(snapname=snapname, description=description, vmstate=int(vmstate))
        while timeout:
            status_data = self.proxmox_api.nodes(vm['node']).tasks(taskid).status.get()
            if status_data['status'] == 'stopped' and status_data['exitstatus'] == 'OK':
                return True
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for creating VM snapshot. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
            timeout -= 1
        return False

    def snapshot_remove(self, vm, vmid, timeout, snapname, force):
        if self.module.check_mode:
            return True

        taskid = self.snapshot(vm, vmid).delete(snapname, force=int(force))
        while timeout:
            status_data = self.proxmox_api.nodes(vm['node']).tasks(taskid).status.get()
            if status_data['status'] == 'stopped' and status_data['exitstatus'] == 'OK':
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
        while timeout:
            status_data = self.proxmox_api.nodes(vm['node']).tasks(taskid).status.get()
            if status_data['status'] == 'stopped' and status_data['exitstatus'] == 'OK':
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
        force=dict(type='bool', default='no'),
        vmstate=dict(type='bool', default='no'),
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
    vmstate = module.params['vmstate']

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

            if proxmox.snapshot_create(vm, vmid, timeout, snapname, description, vmstate):
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

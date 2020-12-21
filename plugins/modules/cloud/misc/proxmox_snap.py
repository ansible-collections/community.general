#!/usr/bin/python
# -*- coding: utf-8 -*-

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
  - Allows you to create/delete snapshots from instances in Proxmox VE cluster.
  - Supports both KVM and LXC, OpenVZ has not been tested, as it is no longer supported on Proxmox VE.
options:
  api_host:
    description:
      - The host of the Proxmox VE cluster.
    required: true
    type: str
  api_user:
    description:
      - The user to authenticate with.
    required: true
    type: str
  api_password:
    description:
      - The password to authenticate with.
      - You can use PROXMOX_PASSWORD environment variable.
    type: str
  hostname:
    description:
      - The instance name.
    type: str
  vmid:
    description:
      - The instance id.
      - If not set, will be fetched from PromoxAPI based on the hostname.
    type: str
  validate_certs:
    description:
      - Enable / disable https certificate verification.
    type: bool
    default: no
  state:
    description:
     - Indicate desired state of the instance snapshot.
    choices: ['present', 'absent']
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
      - Name of the snapshot that has to be created.
    default: 'ansible_snap'
    type: str

notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
  - Supports C(check_mode).
requirements: [ "proxmoxer", "python >= 2.7", "requests" ]
author: Jeffrey van Pelt (@Thulium-Drake)
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
'''

RETURN = r'''#'''

import os
import time
import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    PROXMOXER_IMP_ERR = traceback.format_exc()
    HAS_PROXMOXER = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native


VZ_TYPE = None


def get_vmid(proxmox, hostname):
    return [vm['vmid'] for vm in proxmox.cluster.resources.get(type='vm') if 'name' in vm and vm['name'] == hostname]


def get_instance(proxmox, vmid):
    return [vm for vm in proxmox.cluster.resources.get(type='vm') if int(vm['vmid']) == int(vmid)]


def snapshot_create(module, proxmox, vm, vmid, timeout, snapname, description, vmstate):
    if module.check_mode:
        return True

    if VZ_TYPE == 'lxc':
        taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).snapshot.post(snapname=snapname, description=description)
    else:
        taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).snapshot.post(snapname=snapname, description=description, vmstate=int(vmstate))
    while timeout:
        if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for creating VM snapshot. Last line in task before timeout: %s' %
                                 proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def snapshot_remove(module, proxmox, vm, vmid, timeout, snapname, force):
    if module.check_mode:
        return True

    taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).snapshot.delete(snapname, force=int(force))
    while timeout:
        if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for removing VM snapshot. Last line in task before timeout: %s' %
                                 proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def setup_api(api_host, api_user, api_password, validate_certs):
    api = ProxmoxAPI(api_host, user=api_user, password=api_password, verify_ssl=validate_certs)
    return api


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(required=True),
            api_user=dict(required=True),
            api_password=dict(no_log=True),
            vmid=dict(required=False),
            validate_certs=dict(type='bool', default='no'),
            hostname=dict(),
            timeout=dict(type='int', default=30),
            state=dict(default='present', choices=['present', 'absent']),
            description=dict(type='str'),
            snapname=dict(type='str', default='ansible_snap'),
            force=dict(type='bool', default='no'),
            vmstate=dict(type='bool', default='no'),
        ),
        supports_check_mode=True
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('python-proxmoxer'),
                         exception=PROXMOXER_IMP_ERR)

    state = module.params['state']
    api_user = module.params['api_user']
    api_host = module.params['api_host']
    api_password = module.params['api_password']
    vmid = module.params['vmid']
    validate_certs = module.params['validate_certs']
    hostname = module.params['hostname']
    description = module.params['description']
    snapname = module.params['snapname']
    timeout = module.params['timeout']
    force = module.params['force']
    vmstate = module.params['vmstate']

    # If password not set get it from PROXMOX_PASSWORD env
    if not api_password:
        try:
            api_password = os.environ['PROXMOX_PASSWORD']
        except KeyError as e:
            module.fail_json(msg='You should set api_password param or use PROXMOX_PASSWORD environment variable' % to_native(e))

    try:
        proxmox = setup_api(api_host, api_user, api_password, validate_certs)

    except Exception as e:
        module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % to_native(e))

    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and hostname:
        hosts = get_vmid(proxmox, hostname)
        if len(hosts) == 0:
            module.fail_json(msg="Vmid could not be fetched => Hostname does not exist (action: %s)" % state)
        vmid = hosts[0]
    elif not vmid:
        module.exit_json(changed=False, msg="Vmid could not be fetched for the following action: %s" % state)

    vm = get_instance(proxmox, vmid)

    global VZ_TYPE
    VZ_TYPE = vm[0]['type']

    if state == 'present':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.fail_json(msg='VM with vmid = %s not exists in cluster' % vmid)

            for i in getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).snapshot.get():
                if i['name'] == snapname:
                    module.exit_json(changed=False, msg="Snapshot %s is already present" % snapname)

            if snapshot_create(module, proxmox, vm, vmid, timeout, snapname, description, vmstate):
                if module.check_mode:
                    module.exit_json(changed=False, msg="Snapshot %s would be created" % snapname)
                else:
                    module.exit_json(changed=True, msg="Snapshot %s created" % snapname)

        except Exception as e:
            module.fail_json(msg="Creating snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, to_native(e)))

    elif state == 'absent':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.fail_json(msg='VM with vmid = %s not exists in cluster' % vmid)

            snap_exist = False

            for i in getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).snapshot.get():
                if i['name'] == snapname:
                    snap_exist = True
                    continue

            if not snap_exist:
                module.exit_json(changed=False, msg="Snapshot %s does not exist" % snapname)
            else:
                if snapshot_remove(module, proxmox, vm, vmid, timeout, snapname, force):
                    if module.check_mode:
                        module.exit_json(changed=False, msg="Snapshot %s would be removed" % snapname)
                    else:
                        module.exit_json(changed=True, msg="Snapshot %s removed" % snapname)

        except Exception as e:
            module.fail_json(msg="Removing snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, to_native(e)))


if __name__ == '__main__':
    main()

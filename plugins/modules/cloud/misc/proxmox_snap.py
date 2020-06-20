#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_snap
short_description: snapshot management of instances in Proxmox VE cluster
version_added: 1.0.0
description:
  - allows you to create/delete snapshots from instances in Proxmox VE cluster
options:
  api_host:
    description:
      - the host of the Proxmox VE cluster
    required: true
    type: str
  api_user:
    description:
      - the user to authenticate with
    required: true
    type: str
  api_password:
    description:
      - the password to authenticate with
      - you can use PROXMOX_PASSWORD environment variable
    type: str
  hostname:
    description:
      - the instance name
    type: str
  vmid:
    description:
      - the instance id
      - if not set, will be fetched from PromoxAPI based on the hostname
    type: int
  validate_certs:
    description:
      - enable / disable https certificate verification
    type: bool
    default: 'no'
  state:
    description:
     - Indicate desired state of the instance snapshot
    choices: ['present', 'absent']
    default: present
    type: str
  force:
    description:
      - For removal from config file, even if removing disk snapshot fails.
    default: 'no'
    type: bool
  vmstate:
    description:
      - Snapshot includes RAM
    default: 'no'
    type: bool
  description:
    description:
      - Specify the description for the snapshot. Only used on the configuration web interface.
      - This is saved as a comment inside the configuration file.
    type: str
  timeout:
    description:
      - timeout for operations
    default: 30
    type: int
  snapname:
    description:
      - Name of the snapshot that has to be created
    default: 'ansible_snap'
    type: str

notes:
  - Requires proxmoxer and requests modules on host. This modules can be installed with pip.
requirements: [ "proxmoxer", "python >= 2.7", "requests" ]
author: Jeffrey van Pelt (@Thulium-Drake)
'''

EXAMPLES = r'''
- name: Create new container snapshot
  proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: present
    snapname: pre-updates

- name: Remove container snapshot
  proxmox:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    state: absent
    snapname: pre-updates

- name: Make snapshots of multiple machines
  hosts: all
  gather_facts: false
  tasks:
    - name: make snapshots using the vmid
      proxmox_snap:
        api_user: root@pam
        api_password: 1q2w3e
        api_host: node1
        vmid: "{{ proxmox_vmid }}"
        state: present
        snapname: test
        vmstate: true
      delegate_to: localhost
    - name: remove snapshots using the inventory hostname
      proxmox_snap:
        api_user: root@pam
        api_password: 1q2w3e
        api_host: node1
        hostname: "{{ inventory_hostname }}"
        state: absent
        snapname: test
        force: true
      delegate_to: localhost
'''

import os
import time
import traceback
from distutils.version import LooseVersion

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


VZ_TYPE = None


def get_vmid(proxmox, hostname):
    return [vm['vmid'] for vm in proxmox.cluster.resources.get(type='vm') if 'name' in vm and vm['name'] == hostname]


def get_instance(proxmox, vmid):
    return [vm for vm in proxmox.cluster.resources.get(type='vm') if vm['vmid'] == int(vmid)]


def proxmox_version(proxmox):
    apireturn = proxmox.version.get()
    return LooseVersion(apireturn['version'])


def snapshot_create(module, proxmox, vm, vmid, timeout, snapname, description, vmstate):
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(type='str', required=True),
            api_user=dict(type='str', required=True),
            api_password=dict(type='str', no_log=True),
            vmid=dict(type='int', required=False),
            hostname=dict(type='str', required=False),
            validate_certs=dict(type='bool', default='no'),
            timeout=dict(type='int', default=30),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            description=dict(type='str'),
            snapname=dict(type='str', default='ansible_snap'),
            force=dict(type='bool', default='no'),
            vmstate=dict(type='bool', default='no'),
        )
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg='proxmoxer required for this module')

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
            module.fail_json(msg='You should set api_password param or use PROXMOX_PASSWORD environment variable')

    try:
        proxmox = ProxmoxAPI(api_host, user=api_user, password=api_password, verify_ssl=validate_certs)

    except Exception as e:
        module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and hostname:
        hosts = get_vmid(proxmox, hostname)
        if len(hosts) == 0:
            module.fail_json(msg="Vmid could not be fetched => Hostname doesn't exist (action: %s)" % state)
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
                module.exit_json(changed=True, msg="Snapshot %s created" % snapname)
        except Exception as e:
            module.fail_json(msg="Creating snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, e))

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
                    module.exit_json(changed=True, msg="Snapshot %s removed" % snapname)
        except Exception as e:
            module.fail_json(msg="Removing snapshot %s of VM %s failed with exception: %s" % (snapname, vmid, e))


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Castor Sky (@castorsky) <csky57@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_disk
short_description: Management of a disk of a Qemu(KVM) VM in a Proxmox VE cluster.
version_added: 5.5.0
description:
  - Allows you to perform some supported operations on a disk in Qemu(KVM) Virtual Machines in a Proxmox VE cluster.
author: "Castor Sky (@castorsky) <csky57@gmail.com>"
options:
  name:
    description:
      - The unique name of the VM.
      - You can specify either I(name) or I(vmid) or both of them.
    type: str
  vmid:
    description:
      - The unique ID of the VM.
      - You can specify either I(vmid) or I(name) or both of them.
    type: int
  disk:
    description:
      - The disk key (C(unused[n]), C(ide[n]), C(sata[n]), C(scsi[n]) or C(virtio[n])) you want to operate on.
    type: str
    required: True
  state:
    description:
      - Indicates desired state of the disk.
      - >
        I(state=present) intended only for creating new disk (with or without replacing existing disk,
        see I(force_replace) option).
      - For changing options in existing disk use I(state=updated)
      - When I(state=detached) and disk is C(unused[n]) it will be left in same state (not removed).
    type: str
    choices: ['present', 'updated', 'grown', 'detached', 'moved', 'absent']
    default: present
  force_replace:
    description:
      - Force replace existing attached disk with the new one leaving old disk unused.
      - When disk exists and I(force_replace=False) creation will be silently skipped.
    type: bool
    default: False
  storage:
    description:
      - The drive's backing storage.
      - Used primarily when I(state) is C(present) or C(moved).
    type: str
  size:
    description:
      - For I(state=present) I(size) is desired volume size in GB to allocate.
      - >
        For I(state=grown) C(size) is the new size of volume. With the C(+) sign
        the value is added to the actual size of the volume
        and without it, the value is taken as an absolute one.
    type: str
  bwlimit:
    description:
      - Override I/O bandwidth limit (in KB/s).
      - Used only when I(state=moved).
    type: int
  delete_moved:
    description:
      - Delete the original disk after successful copy.
      - By default the original disk is kept as unused disk.
      - Used only when I(state=moved).
    type: bool
  target_disk:
    description:
      - The config key the disk will be moved to on the target VM (for example, C(ide0) or C(scsi1)).
      - Default is the source disk key.
      - Used only when I(state=moved).
    type: str
  target_storage:
    description:
      - Target storage.
      - Used only when I(state=moved).
    type: str
  target_vmid:
    description:
      - The (unique) ID of the VM.
      - Used only when I(state=moved).
    type: int
  timeout:
    description:
      - Timeout to wait when moving disk.
      - Used only when I(state=moved).
    type: int
    default: 600
  aio:
    description:
      - AIO type to use.
    type: str
    choices: ['native', 'threads', 'io_uring']
  backup:
    description:
      - Whether the drive should be included when making backups.
    type: bool
  bps:
    description:
      - Maximum r/w speed in bytes per second.
    type: int
  bps_max_length:
    description:
      - Maximum length of I/O bursts in seconds.
    type: int
  bps_rd:
    description:
      - Maximum read speed in bytes per second.
    type: int
  bps_rd_max_length:
    description:
      - Maximum length of read I/O bursts in seconds.
    type: int
  bps_wr:
    description:
      - Maximum write speed in bytes per second.
    type: int
  bps_wr_max_length:
    description:
      - Maximum length of write I/O bursts in seconds.
    type: int
  cache:
    description:
      - The drive's cache mode.
    type: str
    choices: ['none', 'writethrough', 'writeback', 'unsafe', 'directsync']
  cyls:
    description:
      - Force the drive's physical geometry to have a specific cylinder count.
    type: int
  detect_zeroes:
    description:
      - Controls whether to detect and try to optimize writes of zeroes.
    type: bool
  discard:
    description:
      - Controls whether to pass discard/trim requests to the underlying storage.
    type: str
    choices: ['ignore', 'on']
  format:
    description:
      - The drive's backing file's data format.
    type: str
    choices: ['raw', 'cow', 'qcow', 'qed', 'qcow2', 'vmdk', 'cloop']
  heads:
    description:
      - Force the drive's physical geometry to have a specific head count.
    type: int
  import_from:
    description:
      - Import volume from this existing one. To use this parameter you have to specify C(size=0) when creating disk.
      - Volume string format
      - C(<STORAGE>:<VMID>/<FULL_NAME>) or C(<ABSOLUTE_PATH>/<FULL_NAME>)
      - Attention! Only root can use absolute paths.
    type: str
  iops:
    description:
      - Maximum r/w I/O in operations per second.
    type: int
  iops_max:
    description:
      - Maximum unthrottled r/w I/O pool in operations per second.
    type: int
  iops_max_length:
    description:
      - Maximum length of I/O bursts in seconds.
    type: int
  iops_rd:
    description:
      - Maximum read I/O in operations per second.
    type: int
  iops_rd_max:
    description:
      - Maximum unthrottled read I/O pool in operations per second.
    type: int
  iops_rd_max_length:
    description:
      - Maximum length of read I/O bursts in seconds.
    type: int
  iops_wr:
    description:
      - Maximum write I/O in operations per second.
    type: int
  iops_wr_max:
    description:
      - Maximum unthrottled write I/O pool in operations per second.
    type: int
  iops_wr_max_length:
    description:
      - Maximum length of write I/O bursts in seconds.
    type: int
  iothread:
    description:
      - Whether to use iothreads for this drive (only for SCSI and VirtIO)
    type: bool
  mpbs:
    description:
      - Maximum r/w speed in megabytes per second.
    type: int
  mpbs_max:
    description:
      - Maximum unthrottled r/w pool in megabytes per second.
    type: int
  mpbs_rd:
    description:
      - Maximum read speed in megabytes per second.
    type: int
  mpbs_rd_max:
    description:
      - Maximum unthrottled read pool in megabytes per second.
    type: int
  mpbs_wr:
    description:
      - Maximum write speed in megabytes per second.
    type: int
  mpbs_wr_max:
    description:
      - Maximum unthrottled write pool in megabytes per second.
    type: int
  media:
    description:
      - The drive's media type.
    type: str
    choices: ['cdrom', 'disk']
  queues:
    description:
      - Number of queues (SCSI only).
    type: int
  replicate:
    description:
      - Whether the drive should considered for replication jobs.
    type: bool
  rerror:
    description:
      - Read error action.
    type: str
    choices: ['ignore', 'report', 'stop']
  ro:
    description:
      - Whether the drive is read-only.
    type: bool
  scsiblock:
    description:
      - Whether to use scsi-block for full passthrough of host block device.
      - Can lead to I/O errors in combination with low memory or high memory fragmentation on host.
    type: bool
  secs:
    description:
      - Force the drive's physical geometry to have a specific sector count.
    type: int
  serial:
    description:
      - The drive's reported serial number, url-encoded, up to 20 bytes long.
    type: str
  shared:
    description:
      - Mark this locally-managed volume as available on all nodes.
      - This option does not share the volume automatically, it assumes it is shared already!
    type: bool
  snapshot:
    description:
      - Controls qemu's snapshot mode feature.
      - If activated, changes made to the disk are temporary and will be discarded when the VM is shutdown.
    type: bool
  ssd:
    description:
      - Whether to expose this drive as an SSD, rather than a rotational hard disk.
    type: bool
  trans:
    description:
      - Force disk geometry bios translation mode.
    type: str
    choices: ['auto', 'lba', 'none']
  werror:
    description:
      - Write error action.
    type: str
    choices: ['enospc', 'ignore', 'report', 'stop']
  wwn:
    description:
      - The drive's worldwide name, encoded as 16 bytes hex string, prefixed by C(0x).
    type: str
extends_documentation_fragment:
  - community.general.proxmox.documentation
'''

EXAMPLES = '''
- name: Create new disk in VM (do not rewrite in case it exists already)
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    name: vm-name
    disk: scsi3
    backup: True
    cache: none
    storage: local-zfs
    size: 5
    state: present

- name: Create new disk in VM (force rewrite in case it exists already)
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: scsi3
    format: qcow2
    storage: local
    size: 16
    force_replace: True
    state: present

- name: Update existing disk
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: ide0
    backup: False
    ro: True
    aio: native
    state: updated

- name: Grow existing disk
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: sata4
    size: +5G
    state: grown

- name: Detach disk (leave it unused)
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    name: vm-name
    disk: virtio0
    state: detached

- name: Move disk to another storage
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_password: secret
    vmid: 101
    disk: scsi7
    target_storage: local
    format: qcow2
    state: moved

- name: Move disk from one VM to another
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: scsi7
    target_vmid: 201
    state: moved

- name: Remove disk permanently
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_password: secret
    vmid: 101
    disk: scsi4
    state: absent
'''

RETURN = '''
vmid:
  description: The VM vmid.
  returned: success
  type: int
  sample: 101
msg:
  description: A short message
  returned: always
  type: str
  sample: "Disk scsi3 created in VM 101"
'''

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec,
                                                                                ProxmoxAnsible)
from re import compile, match, sub
from time import sleep


def disk_conf_str_to_dict(config_string):
    config = config_string.split(',')
    storage_volume = config.pop(0).split(':')
    config.sort()
    storage_name = storage_volume[0]
    volume_name = storage_volume[1]
    config_current = dict(
        volume='%s:%s' % (storage_name, volume_name),
        storage_name=storage_name,
        volume_name=volume_name
    )

    for option in config:
        k, v = option.split('=')
        config_current[k] = v

    return config_current


class ProxmoxDiskAnsible(ProxmoxAnsible):
    create_update_fields = [
        'aio', 'backup', 'bps', 'bps_max_length', 'bps_rd', 'bps_rd_max_length', 'bps_wr', 'bps_wr_max_length',
        'cache', 'cyls', 'detect_zeroes', 'discard', 'format', 'heads', 'import_from', 'iops', 'iops_max',
        'iops_max_length', 'iops_rd', 'iops_rd_max', 'iops_rd_max_length', 'iops_wr', 'iops_wr_max',
        'iops_wr_max_length', 'iothread', 'mpbs', 'mpbs_max', 'mpbs_rd', 'mpbs_rd_max', 'mpbs_wr', 'mpbs_wr_max',
        'media', 'queues', 'replicate', 'rerror', 'ro', 'scsiblock', 'secs', 'serial', 'shared', 'snapshot',
        'ssd', 'trans', 'werror', 'wwn'
    ]
    supported_ranges = dict(
        ide=range(0, 4),
        scsi=range(0, 31),
        sata=range(0, 6),
        virtio=range(0, 16),
        unused=range(0, 256)
    )

    def sanitize_params(self):
        # Sanitize parameters dictionary:
        # - Remove not defined args
        # - Ensure True and False converted to int.
        # - Remove unnecessary parameters
        params = dict((k, v) for k, v in self.module.params.items() if v is not None and k in self.create_update_fields)
        params.update(dict((k, int(v)) for k, v in params.items() if isinstance(v, bool)))
        return params

    def create_disk(self, disk, vmid, vm, vm_config):
        # Would not replace existing disk without 'force' flag
        force_replace = self.module.params['force_replace']
        if not force_replace and disk in vm_config:
            self.module.exit_json(
                changed=False,
                vmid=vmid,
                msg="Disk %s already exists in VM %s." % (disk, vmid)
            )

        params = self.sanitize_params()
        import_string = params.pop('import_from', None)
        if import_string and self.module.params["size"] != "0":
            self.module.fail_json(vmid=vmid, msg='Only size=0 is acceptable with <import_from> parameter.')

        config_str = "%s:%s" % (self.module.params["storage"], self.module.params["size"])
        if import_string:
            config_str += ',import-from=%s' % import_string

        for k, v in params.items():
            config_str += ',%s=%s' % (k, v)

        disk_config = {self.module.params["disk"]: config_str}
        self.proxmox_api.nodes(vm['node']).qemu(vmid).config.set(**disk_config)

    def update_disk(self, disk, vmid, vm, vm_config):
        disk_config = disk_conf_str_to_dict(vm_config[disk])
        config_str = disk_config["volume"]
        params = self.sanitize_params()

        for k, v in params.items():
            config_str += ',%s=%s' % (k, v)

        disk_config = {self.module.params["disk"]: config_str}
        self.proxmox_api.nodes(vm['node']).qemu(vmid).config.set(**disk_config)

    def move_disk(self, disk, vmid, vm, vm_config):
        params = dict()
        params['disk'] = disk
        params['vmid'] = vmid
        params['bwlimit'] = self.module.params['bwlimit']
        params['storage'] = self.module.params['target_storage']
        params['target-disk'] = self.module.params['target_disk']
        params['target-vmid'] = self.module.params['target_vmid']
        params['format'] = self.module.params['format']
        params['delete'] = 1 if self.module.params.get('delete_moved', False) else 0
        # Remove not defined args
        params = dict((k, v) for k, v in params.items() if v is not None)

        taskid = self.proxmox_api.nodes(vm['node']).qemu(vmid).move_disk.post(**params)
        timeout = self.module.params['timeout']
        while timeout:
            status_data = self.proxmox_api.nodes(vm['node']).tasks(taskid).status.get()
            if status_data['status'] == 'stopped' and status_data['exitstatus'] == 'OK':
                return True
            if timeout <= 0:
                self.module.fail_json(
                    msg='Reached timeout while waiting for moving VM disk. Last line in task before timeout: %s' %
                        self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            sleep(1)
            timeout -= 1
        return False


def main():
    module_args = proxmox_auth_argument_spec()
    disk_args = dict(
        # Proxmox native parameters
        aio=dict(choices=['native', 'threads', 'io_uring']),
        backup=dict(type='bool'),
        bps=dict(type='int'),
        bps_max_length=dict(type='int'),
        bps_rd=dict(type='int'),
        bps_rd_max_length=dict(type='int'),
        bps_wr=dict(type='int'),
        bps_wr_max_length=dict(type='int'),
        cache=dict(choices=['none', 'writethrough', 'writeback', 'unsafe', 'directsync']),
        cyls=dict(type='int'),
        detect_zeroes=dict(type='bool'),
        discard=dict(choices=['ignore', 'on']),
        format=dict(choices=['raw', 'cow', 'qcow', 'qed', 'qcow2', 'vmdk', 'cloop']),
        heads=dict(type='int'),
        import_from=dict(type='str'),
        iops=dict(type='int'),
        iops_max=dict(type='int'),
        iops_max_length=dict(type='int'),
        iops_rd=dict(type='int'),
        iops_rd_max=dict(type='int'),
        iops_rd_max_length=dict(type='int'),
        iops_wr=dict(type='int'),
        iops_wr_max=dict(type='int'),
        iops_wr_max_length=dict(type='int'),
        iothread=dict(type='bool'),
        mpbs=dict(type='int'),
        mpbs_max=dict(type='int'),
        mpbs_rd=dict(type='int'),
        mpbs_rd_max=dict(type='int'),
        mpbs_wr=dict(type='int'),
        mpbs_wr_max=dict(type='int'),
        media=dict(choices=['cdrom', 'disk']),
        queues=dict(type='int'),
        replicate=dict(type='bool'),
        rerror=dict(choices=['ignore', 'report', 'stop']),
        ro=dict(type='bool'),
        scsiblock=dict(type='bool'),
        secs=dict(type='int'),
        serial=dict(type='str'),
        shared=dict(type='bool'),
        snapshot=dict(type='bool'),
        ssd=dict(type='bool'),
        trans=dict(choices=['auto', 'lba', 'none']),
        werror=dict(choices=['enospc', 'ignore', 'report', 'stop']),
        wwn=dict(type='str'),

        # Disk moving relates parameters
        bwlimit=dict(type='int'),
        target_storage=dict(type='str'),
        target_disk=dict(type='str'),
        target_vmid=dict(type='int'),
        delete_moved=dict(type='bool'),
        timeout=dict(type='int', default='600'),

        # Module related parameters
        name=dict(type='str'),
        vmid=dict(type='int'),
        disk=dict(type='str', required=True),
        storage=dict(type='str'),
        size=dict(type='str'),
        state=dict(choices=['present', 'updated', 'grown', 'detached', 'moved', 'absent'], default='present'),
        force_replace=dict(type='bool', default=False),
    )

    module_args.update(disk_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('name', 'vmid'), ('api_password', 'api_token_id')],
        required_if=[
            ('state', 'present', ('storage', 'size')),
            ('state', 'grown', ['size'])
        ],
        required_by={'target_disk': 'target_vmid'},
        supports_check_mode=False,
        mutually_exclusive=[('target_vmid', 'target_storage')]
    )

    proxmox = ProxmoxDiskAnsible(module)

    disk = module.params['disk']
    # Verify disk name has appropriate name
    disk_regex = compile(r'^([a-z]+)([0-9]+)$')
    disk_bus = sub(disk_regex, r'\1', disk)
    disk_number = int(sub(disk_regex, r'\2', disk))
    if disk_bus not in proxmox.supported_ranges:
        proxmox.module.fail_json(msg='Unsupported disk bus: %s' % disk_bus)
    elif disk_number not in proxmox.supported_ranges[disk_bus]:
        bus_range = proxmox.supported_ranges[disk_bus]
        proxmox.module.fail_json(msg='Disk %s number not in range %s..%s ' % (disk, bus_range[0], bus_range[-1]))

    name = module.params['name']
    state = module.params['state']
    vmid = module.params['vmid'] or proxmox.get_vmid(name)

    # Ensure VM id exists and retrieve its config
    vm = None
    vm_config = None
    try:
        vm = proxmox.get_vm(vmid)
        vm_config = proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).config.get()
    except Exception as e:
        proxmox.module.fail_json(msg='Getting information for VM %s failed with exception: %s' % (vmid, str(e)))

    if state == 'present':
        try:
            proxmox.create_disk(disk, vmid, vm, vm_config)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s created in VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to create disk %s in VM %s: %s' % (disk, vmid, str(e)))

    # Do not try to perform actions on missing disk
    if disk not in vm_config and state in ['absent', 'updated', 'grown', 'detached', 'moved']:
        module.fail_json(vmid=vmid, msg='Unable to process missing disk %s in VM %s' % (disk, vmid))

    elif state == 'absent':
        try:
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).unlink.put(vmid=vmid, idlist=disk, force=1)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s removed from VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to remove disk %s from VM %s: %s' % (disk, vmid, str(e)))

    elif state == 'updated':
        try:
            proxmox.update_disk(disk, vmid, vm, vm_config)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s updated in VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(msg="Failed to updated disk %s in VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'detached':
        try:
            if disk_bus == 'unused':
                module.exit_json(changed=False, vmid=vmid, msg='Disk %s already detached in VM %s' % (disk, vmid))
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).unlink.put(vmid=vmid, idlist=disk, force=0)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s detached from VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(msg="Failed to detach disk %s from VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'moved':
        try:
            proxmox.move_disk(disk, vmid, vm, vm_config)
            disk_config = disk_conf_str_to_dict(vm_config[disk])
            module.exit_json(
                changed=True,
                vmid=vmid,
                storage=disk_config["storage_name"],
                msg="Disk %s moved from VM %s storage %s" % (disk, vmid, disk_config["storage_name"]))
        except Exception as e:
            module.fail_json(msg="Failed to move disk %s in VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'grown':
        try:
            size = module.params['size']
            if not match(r'^\+?\d+(\.\d+)?[KMGT]?$', size):
                module.exit_json(vmid=vmid, msg="Unrecognized size pattern for disk %s: %s" % (disk, size))
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).resize.set(vmid=vmid, disk=disk, size=size)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s resized in VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(msg="Failed to resize disk %s in VM %s with exception: %s" % (disk, vmid, str(e)))


if __name__ == '__main__':
    main()

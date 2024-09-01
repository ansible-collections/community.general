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
short_description: Management of a disk of a Qemu(KVM) VM in a Proxmox VE cluster
version_added: 5.7.0
description:
  - Allows you to perform some supported operations on a disk in Qemu(KVM) Virtual Machines in a Proxmox VE cluster.
author: "Castor Sky (@castorsky) <csky57@gmail.com>"
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
  action_group:
    version_added: 9.0.0
options:
  name:
    description:
      - The unique name of the VM.
      - You can specify either O(name) or O(vmid) or both of them.
    type: str
  vmid:
    description:
      - The unique ID of the VM.
      - You can specify either O(vmid) or O(name) or both of them.
    type: int
  disk:
    description:
      - The disk key (V(unused[n]), V(ide[n]), V(sata[n]), V(scsi[n]) or V(virtio[n])) you want to operate on.
      - Disk buses (IDE, SATA and so on) have fixed ranges of V(n) that accepted by Proxmox API.
      - >
        For IDE: 0-3;
        for SCSI: 0-30;
        for SATA: 0-5;
        for VirtIO: 0-15;
        for Unused: 0-255.
    type: str
    required: true
  state:
    description:
      - Indicates desired state of the disk.
      - >
        O(state=present) can be used to create, replace disk or update options in existing disk. It will create missing
        disk or update options in existing one by default. See the O(create) parameter description to control behavior
        of this option.
      - Some updates on options (like O(cache)) are not being applied instantly and require VM restart.
      - >
        Use O(state=detached) to detach existing disk from VM but do not remove it entirely.
        When O(state=detached) and disk is V(unused[n]) it will be left in same state (not removed).
      - >
        O(state=moved) may be used to change backing storage for the disk in bounds of the same VM
        or to send the disk to another VM (using the same backing storage).
      - >
        O(state=resized) intended to change the disk size. As of Proxmox 7.2 you can only increase the disk size
        because shrinking disks is not supported by the PVE API and has to be done manually.
      - To entirely remove the disk from backing storage use O(state=absent).
    type: str
    choices: ['present', 'resized', 'detached', 'moved', 'absent']
    default: present
  create:
    description:
      - With O(create) flag you can control behavior of O(state=present).
      - When O(create=disabled) it will not create new disk (if not exists) but will update options in existing disk.
      - When O(create=regular) it will either create new disk (if not exists) or update options in existing disk.
      - When O(create=forced) it will always create new disk (if disk exists it will be detached and left unused).
    type: str
    choices: ['disabled', 'regular', 'forced']
    default: regular
  storage:
    description:
      - The drive's backing storage.
      - Used only when O(state) is V(present).
    type: str
  size:
    description:
      - Desired volume size in GB to allocate when O(state=present) (specify O(size) without suffix).
      - >
        New (or additional) size of volume when O(state=resized). With the V(+) sign
        the value is added to the actual size of the volume
        and without it, the value is taken as an absolute one.
    type: str
  bwlimit:
    description:
      - Override I/O bandwidth limit (in KB/s).
      - Used only when O(state=moved).
    type: int
  delete_moved:
    description:
      - Delete the original disk after successful copy.
      - By default the original disk is kept as unused disk.
      - Used only when O(state=moved).
    type: bool
  target_disk:
    description:
      - The config key the disk will be moved to on the target VM (for example, V(ide0) or V(scsi1)).
      - Default is the source disk key.
      - Used only when O(state=moved).
    type: str
  target_storage:
    description:
      - Move the disk to this storage when O(state=moved).
      - You can move between storages only in scope of one VM.
      - Mutually exclusive with O(target_vmid).
      - Consider increasing O(timeout) in case of large disk images or slow storage backend.
    type: str
  target_vmid:
    description:
      - The (unique) ID of the VM where disk will be placed when O(state=moved).
      - You can move disk between VMs only when the same storage is used.
      - Mutually exclusive with O(target_vmid).
    type: int
  timeout:
    description:
      - Timeout in seconds to wait for slow operations such as importing disk or moving disk between storages.
      - Used only when O(state) is V(present) or V(moved).
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
  bps_max_length:
    description:
      - Maximum length of total r/w I/O bursts in seconds.
    type: int
  bps_rd_max_length:
    description:
      - Maximum length of read I/O bursts in seconds.
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
      - Control whether to detect and try to optimize writes of zeroes.
    type: bool
  discard:
    description:
      - Control whether to pass discard/trim requests to the underlying storage.
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
      - Import volume from this existing one.
      - Volume string format
      - C(<STORAGE>:<VMID>/<FULL_NAME>) or C(<ABSOLUTE_PATH>/<FULL_NAME>)
      - Attention! Only root can use absolute paths.
      - This parameter is mutually exclusive with O(size).
      - Increase O(timeout) parameter when importing large disk images or using slow storage.
    type: str
  iops:
    description:
      - Maximum total r/w I/O in operations per second.
      - You can specify either total limit or per operation (mutually exclusive with O(iops_rd) and O(iops_wr)).
    type: int
  iops_max:
    description:
      - Maximum unthrottled total r/w I/O pool in operations per second.
    type: int
  iops_max_length:
    description:
      - Maximum length of total r/w I/O bursts in seconds.
    type: int
  iops_rd:
    description:
      - Maximum read I/O in operations per second.
      - You can specify either read or total limit (mutually exclusive with O(iops)).
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
      - You can specify either write or total limit (mutually exclusive with O(iops)).
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
  mbps:
    description:
      - Maximum total r/w speed in megabytes per second.
      - Can be fractional but use with caution - fractionals less than 1 are not supported officially.
      - You can specify either total limit or per operation (mutually exclusive with O(mbps_rd) and O(mbps_wr)).
    type: float
  mbps_max:
    description:
      - Maximum unthrottled total r/w pool in megabytes per second.
    type: float
  mbps_rd:
    description:
      - Maximum read speed in megabytes per second.
      - You can specify either read or total limit (mutually exclusive with O(mbps)).
    type: float
  mbps_rd_max:
    description:
      - Maximum unthrottled read pool in megabytes per second.
    type: float
  mbps_wr:
    description:
      - Maximum write speed in megabytes per second.
      - You can specify either write or total limit (mutually exclusive with O(mbps)).
    type: float
  mbps_wr_max:
    description:
      - Maximum unthrottled write pool in megabytes per second.
    type: float
  media:
    description:
      - The drive's media type.
    type: str
    choices: ['cdrom', 'disk']
  iso_image:
    description:
      - The ISO image to be mounted on the specified in O(disk) CD-ROM.
      - O(media=cdrom) needs to be specified for this option to work.
      - "Image string format:"
      - V(<STORAGE>:iso/<ISO_NAME>) to mount ISO.
      - V(cdrom) to use physical CD/DVD drive.
      - V(none) to unmount image from existent CD-ROM or create empty CD-ROM drive.
    type: str
    version_added: 8.1.0
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
      - Control qemu's snapshot mode feature.
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
      - The drive's worldwide name, encoded as 16 bytes hex string, prefixed by V(0x).
    type: str
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
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
    backup: true
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
    create: forced
    state: present

- name: Update existing disk
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: ide0
    backup: false
    ro: true
    aio: native
    state: present

- name: Grow existing disk
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: sata4
    size: +5G
    state: resized

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

- name: Mount ISO image on CD-ROM (create drive if missing)
  community.general.proxmox_disk:
    api_host: node1
    api_user: root@pam
    api_token_id: token1
    api_token_secret: some-token-data
    vmid: 101
    disk: ide2
    media: cdrom
    iso_image: local:iso/favorite_distro_amd64.iso
    state: present
'''

RETURN = '''
vmid:
  description: The VM vmid.
  returned: success
  type: int
  sample: 101
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Disk scsi3 created in VM 101"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec,
                                                                                ProxmoxAnsible)
from re import compile, match, sub
from time import sleep


def disk_conf_str_to_dict(config_string):
    """
    Transform Proxmox configuration string for disk element into dictionary which has
    volume option parsed in '{ storage }:{ volume }' format and other options parsed
    in '{ option }={ value }' format. This dictionary will be compared afterward with
    attributes that user passed to this module in playbook.\n
    config_string examples:
      - local-lvm:vm-100-disk-0,ssd=1,discard=on,size=25G
      - local:iso/new-vm-ignition.iso,media=cdrom,size=70k
      - none,media=cdrom
    :param config_string: Retrieved from Proxmox API configuration string
    :return: Dictionary with volume option divided into parts ('volume_name', 'storage_name', 'volume') \n
        and other options as key:value.
    """
    config = config_string.split(',')

    # When empty CD-ROM drive present, the volume part of config string is "none".
    storage_volume = config.pop(0)
    if storage_volume in ["none", "cdrom"]:
        config_current = dict(
            volume=storage_volume,
            storage_name=None,
            volume_name=None,
            size=None,
        )
    else:
        storage_volume = storage_volume.split(':')
        storage_name = storage_volume[0]
        volume_name = storage_volume[1]
        config_current = dict(
            volume='%s:%s' % (storage_name, volume_name),
            storage_name=storage_name,
            volume_name=volume_name,
        )

    config.sort()
    for option in config:
        k, v = option.split('=')
        config_current[k] = v

    return config_current


class ProxmoxDiskAnsible(ProxmoxAnsible):
    create_update_fields = [
        'aio', 'backup', 'bps_max_length', 'bps_rd_max_length', 'bps_wr_max_length',
        'cache', 'cyls', 'detect_zeroes', 'discard', 'format', 'heads', 'import_from', 'iops', 'iops_max',
        'iops_max_length', 'iops_rd', 'iops_rd_max', 'iops_rd_max_length', 'iops_wr', 'iops_wr_max',
        'iops_wr_max_length', 'iothread', 'mbps', 'mbps_max', 'mbps_rd', 'mbps_rd_max', 'mbps_wr', 'mbps_wr_max',
        'media', 'queues', 'replicate', 'rerror', 'ro', 'scsiblock', 'secs', 'serial', 'shared', 'snapshot',
        'ssd', 'trans', 'werror', 'wwn'
    ]
    supported_bus_num_ranges = dict(
        ide=range(0, 4),
        scsi=range(0, 31),
        sata=range(0, 6),
        virtio=range(0, 16),
        unused=range(0, 256)
    )

    def get_create_attributes(self):
        # Sanitize parameters dictionary:
        # - Remove not defined args
        # - Ensure True and False converted to int.
        # - Remove unnecessary parameters
        params = {
            k: int(v) if isinstance(v, bool) else v
            for k, v in self.module.params.items()
            if v is not None and k in self.create_update_fields
        }
        return params

    def wait_till_complete_or_timeout(self, node_name, task_id):
        timeout = self.module.params['timeout']
        while timeout:
            if self.api_task_ok(node_name, task_id):
                return True
            timeout -= 1
            if timeout <= 0:
                return False
            sleep(1)

    def create_disk(self, disk, vmid, vm, vm_config):
        create = self.module.params['create']
        if create == 'disabled' and disk not in vm_config:
            # NOOP
            return False, "Disk %s not found in VM %s and creation was disabled in parameters." % (disk, vmid)

        timeout_str = "Reached timeout. Last line in task before timeout: %s"
        if (create == 'regular' and disk not in vm_config) or (create == 'forced'):
            # CREATE
            playbook_config = self.get_create_attributes()
            import_string = playbook_config.pop('import_from', None)
            iso_image = self.module.params.get('iso_image', None)

            if import_string:
                # When 'import_from' option is present in task options.
                config_str = "%s:%s,import-from=%s" % (self.module.params["storage"], "0", import_string)
                timeout_str = "Reached timeout while importing VM disk. Last line in task before timeout: %s"
                ok_str = "Disk %s imported into VM %s"
            elif iso_image is not None:
                # disk=<busN>, media=cdrom, iso_image=<ISO_NAME>
                config_str = iso_image
                ok_str = "CD-ROM was created on %s bus in VM %s"
            else:
                config_str = self.module.params["storage"]
                if self.module.params.get("media") != "cdrom":
                    config_str += ":%s" % (self.module.params["size"])
                ok_str = "Disk %s created in VM %s"
                timeout_str = "Reached timeout while creating VM disk. Last line in task before timeout: %s"

            for k, v in playbook_config.items():
                config_str += ',%s=%s' % (k, v)

            disk_config_to_apply = {self.module.params["disk"]: config_str}

        if create in ['disabled', 'regular'] and disk in vm_config:
            # UPDATE
            ok_str = "Disk %s updated in VM %s"
            iso_image = self.module.params.get('iso_image', None)

            proxmox_config = disk_conf_str_to_dict(vm_config[disk])
            # 'import_from' fails on disk updates
            playbook_config = self.get_create_attributes()
            playbook_config.pop('import_from', None)

            # Begin composing configuration string
            if iso_image is not None:
                config_str = iso_image
            else:
                config_str = proxmox_config["volume"]
            # Append all mandatory fields from playbook_config
            for k, v in playbook_config.items():
                config_str += ',%s=%s' % (k, v)

            # Append to playbook_config fields which are constants for disk images
            for option in ['size', 'storage_name', 'volume', 'volume_name']:
                playbook_config.update({option: proxmox_config[option]})
            # CD-ROM is special disk device and its disk image is subject to change
            if iso_image is not None:
                playbook_config['volume'] = iso_image
            # Values in params are numbers, but strings are needed to compare with disk_config
            playbook_config = {k: str(v) for k, v in playbook_config.items()}

            # Now compare old and new config to detect if changes are needed
            if proxmox_config == playbook_config:
                return False, "Disk %s is up to date in VM %s" % (disk, vmid)

            disk_config_to_apply = {self.module.params["disk"]: config_str}

        current_task_id = self.proxmox_api.nodes(vm['node']).qemu(vmid).config.post(**disk_config_to_apply)
        task_success = self.wait_till_complete_or_timeout(vm['node'], current_task_id)
        if task_success:
            return True, ok_str % (disk, vmid)
        else:
            self.module.fail_json(
                msg=timeout_str % self.proxmox_api.nodes(vm['node']).tasks(current_task_id).log.get()[:1]
            )

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
        params = {k: v for k, v in params.items() if v is not None}

        if params.get('storage', False):
            disk_config = disk_conf_str_to_dict(vm_config[disk])
            if params['storage'] == disk_config['storage_name']:
                return False

        task_id = self.proxmox_api.nodes(vm['node']).qemu(vmid).move_disk.post(**params)
        task_success = self.wait_till_complete_or_timeout(vm['node'], task_id)
        if task_success:
            return True
        else:
            self.module.fail_json(
                msg='Reached timeout while waiting for moving VM disk. Last line in task before timeout: %s' %
                    self.proxmox_api.nodes(vm['node']).tasks(task_id).log.get()[:1]
            )


def main():
    module_args = proxmox_auth_argument_spec()
    disk_args = dict(
        # Proxmox native parameters
        aio=dict(type='str', choices=['native', 'threads', 'io_uring']),
        backup=dict(type='bool'),
        bps_max_length=dict(type='int'),
        bps_rd_max_length=dict(type='int'),
        bps_wr_max_length=dict(type='int'),
        cache=dict(type='str', choices=['none', 'writethrough', 'writeback', 'unsafe', 'directsync']),
        cyls=dict(type='int'),
        detect_zeroes=dict(type='bool'),
        discard=dict(type='str', choices=['ignore', 'on']),
        format=dict(type='str', choices=['raw', 'cow', 'qcow', 'qed', 'qcow2', 'vmdk', 'cloop']),
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
        iso_image=dict(type='str'),
        mbps=dict(type='float'),
        mbps_max=dict(type='float'),
        mbps_rd=dict(type='float'),
        mbps_rd_max=dict(type='float'),
        mbps_wr=dict(type='float'),
        mbps_wr_max=dict(type='float'),
        media=dict(type='str', choices=['cdrom', 'disk']),
        queues=dict(type='int'),
        replicate=dict(type='bool'),
        rerror=dict(type='str', choices=['ignore', 'report', 'stop']),
        ro=dict(type='bool'),
        scsiblock=dict(type='bool'),
        secs=dict(type='int'),
        serial=dict(type='str'),
        shared=dict(type='bool'),
        snapshot=dict(type='bool'),
        ssd=dict(type='bool'),
        trans=dict(type='str', choices=['auto', 'lba', 'none']),
        werror=dict(type='str', choices=['enospc', 'ignore', 'report', 'stop']),
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
        state=dict(type='str', choices=['present', 'resized', 'detached', 'moved', 'absent'],
                   default='present'),
        create=dict(type='str', choices=['disabled', 'regular', 'forced'], default='regular'),
    )

    module_args.update(disk_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('name', 'vmid'), ('api_password', 'api_token_id')],
        required_if=[
            ('create', 'forced', ['storage']),
            ('state', 'resized', ['size']),
        ],
        required_by={
            'target_disk': 'target_vmid',
            'mbps_max': 'mbps',
            'mbps_rd_max': 'mbps_rd',
            'mbps_wr_max': 'mbps_wr',
            'bps_max_length': 'mbps_max',
            'bps_rd_max_length': 'mbps_rd_max',
            'bps_wr_max_length': 'mbps_wr_max',
            'iops_max': 'iops',
            'iops_rd_max': 'iops_rd',
            'iops_wr_max': 'iops_wr',
            'iops_max_length': 'iops_max',
            'iops_rd_max_length': 'iops_rd_max',
            'iops_wr_max_length': 'iops_wr_max',
            'iso_image': 'media',
        },
        supports_check_mode=False,
        mutually_exclusive=[
            ('target_vmid', 'target_storage'),
            ('mbps', 'mbps_rd'),
            ('mbps', 'mbps_wr'),
            ('iops', 'iops_rd'),
            ('iops', 'iops_wr'),
            ('import_from', 'size'),
        ]
    )

    proxmox = ProxmoxDiskAnsible(module)

    disk = module.params['disk']
    # Verify disk name has appropriate name
    disk_regex = compile(r'^([a-z]+)([0-9]+)$')
    disk_bus = sub(disk_regex, r'\1', disk)
    disk_number = int(sub(disk_regex, r'\2', disk))
    if disk_bus not in proxmox.supported_bus_num_ranges:
        proxmox.module.fail_json(msg='Unsupported disk bus: %s' % disk_bus)
    elif disk_number not in proxmox.supported_bus_num_ranges[disk_bus]:
        bus_range = proxmox.supported_bus_num_ranges[disk_bus]
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

    # Do not try to perform actions on missing disk
    if disk not in vm_config and state in ['resized', 'moved']:
        module.fail_json(vmid=vmid, msg='Unable to process missing disk %s in VM %s' % (disk, vmid))

    if state == 'present':
        try:
            success, message = proxmox.create_disk(disk, vmid, vm, vm_config)
            if success:
                module.exit_json(changed=True, vmid=vmid, msg=message)
            else:
                module.exit_json(changed=False, vmid=vmid, msg=message)
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to create/update disk %s in VM %s: %s' % (disk, vmid, str(e)))

    elif state == 'detached':
        try:
            if disk_bus == 'unused':
                module.exit_json(changed=False, vmid=vmid, msg='Disk %s already detached in VM %s' % (disk, vmid))
            if disk not in vm_config:
                module.exit_json(changed=False, vmid=vmid, msg="Disk %s not present in VM %s config" % (disk, vmid))
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).unlink.put(idlist=disk, force=0)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s detached from VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(msg="Failed to detach disk %s from VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'moved':
        try:
            disk_config = disk_conf_str_to_dict(vm_config[disk])
            disk_storage = disk_config["storage_name"]
            if proxmox.move_disk(disk, vmid, vm, vm_config):
                module.exit_json(changed=True, vmid=vmid,
                                 msg="Disk %s moved from VM %s storage %s" % (disk, vmid, disk_storage))
            else:
                module.exit_json(changed=False, vmid=vmid, msg="Disk %s already at %s storage" % (disk, disk_storage))
        except Exception as e:
            module.fail_json(msg="Failed to move disk %s in VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'resized':
        try:
            size = module.params['size']
            if not match(r'^\+?\d+(\.\d+)?[KMGT]?$', size):
                module.fail_json(msg="Unrecognized size pattern for disk %s: %s" % (disk, size))
            disk_config = disk_conf_str_to_dict(vm_config[disk])
            actual_size = disk_config['size']
            if size == actual_size:
                module.exit_json(changed=False, vmid=vmid, msg="Disk %s is already %s size" % (disk, size))
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).resize.set(disk=disk, size=size)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s resized in VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(msg="Failed to resize disk %s in VM %s with exception: %s" % (disk, vmid, str(e)))

    elif state == 'absent':
        try:
            if disk not in vm_config:
                module.exit_json(changed=False, vmid=vmid, msg="Disk %s is already absent in VM %s" % (disk, vmid))
            proxmox.proxmox_api.nodes(vm['node']).qemu(vmid).unlink.put(idlist=disk, force=1)
            module.exit_json(changed=True, vmid=vmid, msg="Disk %s removed from VM %s" % (disk, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to remove disk %s from VM %s: %s' % (disk, vmid, str(e)))


if __name__ == '__main__':
    main()

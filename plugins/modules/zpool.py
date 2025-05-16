#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Tom Hesse <contact@tomhesse.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
module: zpool
short_description: Manage ZFS zpools
description:
  - Create, destroy, and modify ZFS zpools and their vdev layouts, pool properties, and filesystem properties.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: partial
    details:
      - In check_mode, any zpool subcommand that supports the dry-run flag (`-n`) will be run with `-n` and its
        simulated output included in the module's diff results.
  diff_mode:
    support: full
author:
  - Tom Hesse (@tomhesse)
options:
  name:
    description:
      - Name of the zpool to manage.
    required: true
    type: str
  state:
    description:
      - Whether the pool should exist.
    choices: [ present, absent ]
    default: present
    type: str
  disable_new_features:
    description:
      - If true, disable new ZFS feature flags when creating.
    type: bool
    default: false
  force:
    description:
      - If true, force operations (e.g. overwrite existing devices).
    type: bool
    default: false
  pool_properties:
    description:
      - Dictionary of ZFS pool properties to set (e.g. autoexpand, cachefile).
    type: dict
    default: {}
  filesystem_properties:
    description:
      - Dictionary of ZFS filesystem properties to set on the root dataset (e.g. compression, dedup).
    type: dict
    default: {}
  mountpoint:
    description:
      - Filesystem mountpoint for the root dataset.
    type: str
  altroot:
    description:
      - Alternate root for mounting filesystems.
    type: str
  temp_name:
    description:
      - Temporary name used during pool creation.
    type: str
  vdevs:
    description:
      - List of vdev definitions for the pool.
    required: true
    type: list
    elements: dict
    suboptions:
      role:
        description:
          - Special vdev role (e.g. log, cache, spare).
        type: str
        choices: [ log, cache, spare, dedup, special ]
      type:
        description:
          - Vdev topology (stripe, mirror, raidz).
        type: str
        choices: [ stripe, mirror, raidz, raidz1, raidz2, raidz3 ]
        default: stripe
      disks:
        description:
          - List of device paths to include in this vdev.
        type: list
        elements: str
'''

EXAMPLES = r'''
- name: Create pool "tank" on /dev/sda
  community.general.zpool:
    name: tank
    vdevs:
    - disks:
        - /dev/sda

- name: Create mirrored pool "tank"
  community.general.zpool:
    name: tank
    vdevs:
    - type: mirror
      disks:
        - /dev/sda
        - /dev/sdb

- name: Add a cache device to tank
  community.general.zpool:
    name: tank
    vdevs:
    - disks:
        - /dev/sda
    - role: cache
      disks:
        - /dev/nvme0n1

- name: Set pool and filesystem properties
  community.general.zpool:
    name: tank
    pool_properties:
    ashift: 12
    filesystem_properties:
    compression: lz4
    vdevs:
    - disks:
        - /dev/sda

- name: Destroy pool "tank"
  community.general.zpool:
    name: tank
    state: absent
'''

import re
from ansible.module_utils.basic import AnsibleModule


class Zpool(object):

    def __init__(self, module, name, disable_new_features, force, pool_properties, filesystem_properties, mountpoint, altroot, temp_name, vdevs):
        self.module = module
        self.name = name
        self.disable_new_features = disable_new_features
        self.force = force
        self.pool_properties = pool_properties
        self.filesystem_properties = filesystem_properties
        self.mountpoint = mountpoint
        self.altroot = altroot
        self.temp_name = temp_name
        self.vdevs = vdevs
        self.zpool_cmd = module.get_bin_path('zpool', required=True)
        self.zfs_cmd = module.get_bin_path('zfs', required=True)
        self.changed = False

    def exists(self):
        rc, stdout, stderr = self.module.run_command([self.zpool_cmd, 'list', self.name])
        return rc == 0

    def build_create_cmd(self, dry_run=False):
        cmd = [self.zpool_cmd, 'create']

        if self.disable_new_features:
            cmd.append('-d')

        if self.force:
            cmd.append('-f')

        if dry_run:
            cmd.append('-n')

        for prop, value in self.pool_properties.items():
            cmd.extend(['-o', "{}={}".format(prop, value)])

        for prop, value in self.filesystem_properties.items():
            cmd.extend(['-O', "{}={}".format(prop, value)])

        if self.mountpoint:
            cmd.extend(['-m', self.mountpoint])

        if self.altroot:
            cmd.extend(['-R', self.altroot])

        if self.temp_name:
            cmd.extend(['-t', self.temp_name])

        cmd.append(self.name)

        for vdev in self.vdevs:
            role = vdev.get('role')
            vdev_type = vdev.get('type', 'stripe')
            disks = vdev.get('disks', [])
            if role:
                cmd.append(role)
            if vdev_type != 'stripe':
                cmd.append(vdev_type)
            cmd.extend(disks)

        return cmd

    def create(self):
        cmd = self.build_create_cmd(dry_run=self.module.check_mode)
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        self.changed = True
        if self.module.check_mode:
            return {'prepared': stdout}

    def destroy(self):
        if self.module.check_mode:
            self.changed = True
            return
        cmd = [self.zpool_cmd, 'destroy', self.name]
        self.module.run_command(cmd, check_rc=True)
        self.changed = True

    def list_pool_properties(self):
        cmd = [self.zpool_cmd, 'get', '-H', '-o', 'property,value', 'all', self.name]
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        props = {}
        for line in stdout.splitlines():
            prop, value = line.split('\t', 1)
            props[prop] = value
        return props

    def set_pool_properties_if_changed(self):
        current = self.list_pool_properties()
        before = {}
        after = {}
        for prop, value in self.pool_properties.items():
            if current.get(prop) != str(value):
                before[prop] = current.get(prop)
                if not self.module.check_mode:
                    self.module.run_command([self.zpool_cmd, 'set', "{}={}".format(prop, value), self.name], check_rc=True)
                after[prop] = str(value)
                self.changed = True
        return {'before': {'pool_properties': before}, 'after': {'pool_properties': after}}

    def list_filesystem_properties(self):
        cmd = [self.zfs_cmd, 'get', '-H', '-o', 'property,value', 'all', self.name]
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        props = {}
        for line in stdout.splitlines():
            prop, value = line.split('\t', 1)
            props[prop] = value
        return props

    def set_filesystem_properties_if_changed(self):
        current = self.list_filesystem_properties()
        before = {}
        after = {}
        for prop, value in self.filesystem_properties.items():
            if current.get(prop) != str(value):
                before[prop] = current.get(prop)
                if not self.module.check_mode:
                    self.module.run_command([self.zfs_cmd, 'set', "{}={}".format(prop, value), self.name], check_rc=True)
                after[prop] = str(value)
                self.changed = True
        return {'before': {'filesystem_properties': before}, 'after': {'filesystem_properties': after}}

    def base_device(self, device):
        # nvme drives
        match = re.match(r'^(.*?)(p\d+)$', device)
        if match:
            return match.group(1)

        # sata/scsi drives
        match = re.match(r'^(/dev/(?:sd|vd)[a-z])\d+$', device)
        if match:
            return match.group(1)

        return device

    def get_current_layout(self):
        cmd = [self.zpool_cmd, 'status', '-P', '-L', self.name]
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)

        vdevs = []
        current = None
        in_config = False

        def flush_current(current):
            if current:
                if current.get('role') is None:
                    current.pop('role', None)
                vdevs.append(current)
            return None

        for line in stdout.splitlines():
            if not in_config:
                if line.strip().startswith('config:'):
                    in_config = True
                continue

            if not line.strip() or line.strip().startswith('NAME'):
                continue

            partitions = line.split()
            device = partitions[0]

            if device == self.name:
                continue

            if device in ('logs', 'cache', 'spares'):
                current = flush_current(current)
                role = 'spare' if device == 'spares' else device.rstrip('s')
                current = {'role': role, 'type': None, 'disks': []}
                continue

            match_group = re.match(r'^(mirror|raidz\d?)-\d+$', device)
            if match_group:
                if current and current.get('type') is not None:
                    current = flush_current(current)
                kind = match_group.group(1)
                role = current.get('role') if current and current.get('type') is None else None
                current = {'role': role, 'type': kind, 'disks': []}
                continue

            if device.startswith('/dev/'):
                base_device = self.base_device(device)
                if current:
                    if current.get('type') is None:
                        entry = {
                            'type': 'stripe',
                            'disks': [base_device]
                        }
                        if current.get('role'):
                            entry['role'] = current['role']
                        vdevs.append(entry)
                        current = None
                    else:
                        current['disks'].append(base_device)
                else:
                    vdevs.append({'type': 'stripe', 'disks': [base_device]})
                continue

        if current and current.get('type') is not None:
            current = flush_current(current)

        return vdevs

    def diff_layout(self):
        current = self.get_current_layout()
        desired = self.vdevs

        before = {'vdevs': current}
        after = {'vdevs': desired}

        if current != desired:
            self.changed = True

        return {'before': before, 'after': after}

    def add_vdevs(self):
        diff = self.diff_layout()
        before_vdevs = diff['before']['vdevs']
        after_vdevs = diff['after']['vdevs']

        to_add = [vdev for vdev in after_vdevs if vdev not in before_vdevs]
        if not to_add:
            return {}

        cmd = [self.zpool_cmd, 'add']

        if self.force:
            cmd.append('-f')

        if self.module.check_mode:
            cmd.append('-n')

        for prop, value in self.pool_properties.items():
            cmd.extend(['-o', "{}={}".format(prop, value)])

        cmd.append(self.name)

        for vdev in to_add:
            role = vdev.get('role')
            vdev_type = vdev.get('type', 'stripe')
            disks = vdev.get('disks', [])
            if role:
                cmd.append(role)
            if vdev_type != 'stripe':
                cmd.append(vdev_type)
            cmd.extend(disks)

        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        self.changed = True
        if self.module.check_mode:
            return {'prepared': stdout}

    def list_vdevs_with_names(self):
        cmd = [self.zpool_cmd, 'status', '-P', '-L', self.name]
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        in_cfg = False
        saw_pool = False
        vdevs = []
        current = None
        for line in stdout.splitlines():
            if not in_cfg:
                if line.strip().startswith('config:'):
                    in_cfg = True
                continue
            if not line.strip() or line.strip().startswith('NAME'):
                continue
            partitions = line.strip().split()
            device = partitions[0]
            if not saw_pool:
                if device == self.name:
                    saw_pool = True
                continue
            if re.match(r'^(mirror|raidz\d?)\-\d+$', device) or device in ('cache', 'logs', 'spares'):
                if current:
                    vdevs.append(current)
                vdev_type = ('stripe' if device in ('cache', 'logs', 'spares') else ('mirror' if device.startswith('mirror') else 'raidz'))
                current = {'name': device, 'type': vdev_type, 'disks': []}
                continue
            if device.startswith('/dev/') and current:
                current['disks'].append(self.base_device(device))
                continue
            if device.startswith('/dev/'):
                base_device = self.base_device(device)
                vdevs.append({'name': base_device, 'type': 'stripe', 'disks': [base_device]})
        if current:
            vdevs.append(current)
        return vdevs

    def remove_vdevs(self):
        current = self.list_vdevs_with_names()
        current_disks = {disk for vdev in current for disk in vdev['disks']}
        desired_disks = {disk for vdev in self.vdevs for disk in vdev.get('disks', [])}
        gone = current_disks - desired_disks
        to_remove = [vdev['name'] for vdev in current if any(disk in gone for disk in vdev['disks'])]
        if not to_remove:
            return {}
        cmd = [self.zpool_cmd, 'remove']
        if self.module.check_mode:
            cmd.append('-n')
        cmd.append(self.name)
        cmd.extend(to_remove)
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        self.changed = True
        if self.module.check_mode:
            return {'prepared': stdout}
        before = [vdev['name'] for vdev in current]
        after = [name for name in before if name not in to_remove]
        return {'before': {'vdevs': before}, 'after': {'vdevs': after}}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            disable_new_features=dict(type='bool', default=False),
            force=dict(type='bool', default=False),
            pool_properties=dict(type='dict', default={}),
            filesystem_properties=dict(type='dict', default={}),
            mountpoint=dict(type='str', required=False),
            altroot=dict(type='str', required=False),
            temp_name=dict(type='str', required=False),
            vdevs=dict(type='list', required=True, elements='dict'),
        ),
        supports_check_mode=True
    )

    name = module.params.get('name')
    state = module.params.get('state')
    disable_new_features = module.params.get('disable_new_features')
    force = module.params.get('force')
    pool_properties = module.params.get('pool_properties')
    filesystem_properties = module.params.get('filesystem_properties')
    mountpoint = module.params.get('mountpoint')
    altroot = module.params.get('altroot')
    temp_name = module.params.get('temp_name')
    vdevs = module.params.get('vdevs')

    for property_key in ('pool_properties', 'filesystem_properties'):
        for key, value in list(module.params.get(property_key, {}).items()):
            if isinstance(value, bool):
                module.params[property_key][key] = 'on' if value else 'off'

    for idx, vdev in enumerate(vdevs, start=1):
        disks = vdev.get('disks')
        if not isinstance(disks, list) or len(disks) == 0:
            module.fail_json(msg="vdev #{idx}: at least one disk is required (got: {disks!r})".format(idx=idx, disks=disks))

    allowed_types = {'stripe', 'mirror', 'raidz', 'raidz1', 'raidz2', 'raidz3'}
    allowed_roles = {'log', 'cache', 'spare', 'special', 'dedup'}

    for idx, vdev in enumerate(vdevs, start=1):
        vdev_type = vdev.get('type', 'stripe')
        if not isinstance(vdev_type, str) or vdev_type not in allowed_types:
            module.fail_json(
                msg=(
                    "vdev #{idx}: invalid type {vdev!r}; "
                    "must be one of {types}"
                ).format(
                    idx=idx,
                    vdev=vdev_type,
                    types=sorted(allowed_types)
                )
            )

        role = vdev.get('role')
        if role is not None:
            if not isinstance(role, str) or role not in allowed_roles:
                module.fail_json(
                    msg=(
                        "vdev #{idx}: invalid role {role!r}; "
                        "must be one of {roles}"
                    ).format(
                        idx=idx,
                        role=role,
                        roles=sorted(allowed_roles)
                    )
                )

    result = dict(
        name=name,
        state=state,
    )

    zpool = Zpool(module, name, disable_new_features, force, pool_properties, filesystem_properties, mountpoint, altroot, temp_name, vdevs)

    if state == 'present':
        if zpool.exists():
            vdev_layout_diff = zpool.diff_layout()

            add_vdev_diff = zpool.add_vdevs() or {}
            remove_vdev_diff = zpool.remove_vdevs() or {}
            pool_properties_diff = zpool.set_pool_properties_if_changed()
            filesystem_properties_diff = zpool.set_filesystem_properties_if_changed()

            before = {}
            after = {}
            for diff in (vdev_layout_diff, pool_properties_diff, filesystem_properties_diff):
                before.update(diff.get('before', {}))
                after.update(diff.get('after', {}))

            result['diff'] = {'before': before, 'after': after}

            if module.check_mode:
                prepared = ''
                for diff in (add_vdev_diff, remove_vdev_diff):
                    if 'prepared' in diff:
                        prepared += (diff['prepared'] if not prepared else '\n' + diff['prepared'])
                result['diff']['prepared'] = prepared
        else:
            if module.check_mode:
                result['diff'] = zpool.create()
            else:
                before_vdevs = []
                desired_vdevs = zpool.vdevs
                zpool.create()
                result['diff'] = {
                    'before': {'state': 'absent', 'vdevs': before_vdevs},
                    'after': {'state': state, 'vdevs': desired_vdevs},
                }

    elif state == 'absent':
        if zpool.exists():
            before_vdevs = zpool.get_current_layout()
            zpool.destroy()
            result['diff'] = {
                'before': {'state': 'present', 'vdevs': before_vdevs},
                'after': {'state': state, 'vdevs': []},
            }
        else:
            result['diff'] = {}

    result['diff']['before_header'] = name
    result['diff']['after_header'] = name

    result['changed'] = zpool.changed
    module.exit_json(**result)


if __name__ == '__main__':
    main()

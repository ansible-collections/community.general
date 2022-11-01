#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2013, Johan Wiren <johan.wiren.se@gmail.com>
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: zfs
short_description: Manage zfs
description:
  - Manages ZFS file systems, volumes, clones and snapshots
options:
  name:
    description:
      - File system, snapshot or volume name e.g. C(rpool/myfs).
    required: true
    type: str
  state:
    description:
      - Whether to create (C(present)), or remove (C(absent)) a
        file system, snapshot or volume. All parents/children
        will be created/destroyed as needed to reach the desired state.
    choices: [ absent, present ]
    required: true
    type: str
  origin:
    description:
      - Snapshot from which to create a clone.
    type: str
  extra_zfs_properties:
    description:
      - A dictionary of zfs properties to be set.
      - See the zfs(8) man page for more information.
    type: dict
    default: {}
notes:
  - C(check_mode) is supported, but in certain situations it may report a task
    as changed that will not be reported as changed when C(check_mode) is disabled.
    For example, this might occur when the zpool C(altroot) option is set or when
    a size is written using human-readable notation, such as C(1M) or C(1024K),
    instead of as an unqualified byte count, such as C(1048576).
author:
- Johan Wiren (@johanwiren)
'''

EXAMPLES = '''
- name: Create a new file system called myfs in pool rpool with the setuid property turned off
  community.general.zfs:
    name: rpool/myfs
    state: present
    extra_zfs_properties:
      setuid: off

- name: Create a new volume called myvol in pool rpool.
  community.general.zfs:
    name: rpool/myvol
    state: present
    extra_zfs_properties:
      volsize: 10M

- name: Create a snapshot of rpool/myfs file system.
  community.general.zfs:
    name: rpool/myfs@mysnapshot
    state: present

- name: Create a new file system called myfs2 with snapdir enabled
  community.general.zfs:
    name: rpool/myfs2
    state: present
    extra_zfs_properties:
      snapdir: enabled

- name: Create a new file system by cloning a snapshot
  community.general.zfs:
    name: rpool/cloned_fs
    state: present
    origin: rpool/myfs@mysnapshot

- name: Destroy a filesystem
  community.general.zfs:
    name: rpool/myfs
    state: absent
'''

import os

from ansible.module_utils.basic import AnsibleModule


class Zfs(object):

    def __init__(self, module, name, properties):
        self.module = module
        self.name = name
        self.properties = properties
        self.changed = False
        self.zfs_cmd = module.get_bin_path('zfs', True)
        self.zpool_cmd = module.get_bin_path('zpool', True)
        self.pool = name.split('/')[0].split('@')[0]
        self.is_solaris = os.uname()[0] == 'SunOS'
        self.is_openzfs = self.check_openzfs()
        self.enhanced_sharing = self.check_enhanced_sharing()

    def check_openzfs(self):
        cmd = [self.zpool_cmd]
        cmd.extend(['get', 'version'])
        cmd.append(self.pool)
        (rc, out, err) = self.module.run_command(cmd, check_rc=True)
        version = out.splitlines()[-1].split()[2]
        if version == '-':
            return True
        if int(version) == 5000:
            return True
        return False

    def check_enhanced_sharing(self):
        if self.is_solaris and not self.is_openzfs:
            cmd = [self.zpool_cmd]
            cmd.extend(['get', 'version'])
            cmd.append(self.pool)
            (rc, out, err) = self.module.run_command(cmd, check_rc=True)
            version = out.splitlines()[-1].split()[2]
            if int(version) >= 34:
                return True
        return False

    def exists(self):
        cmd = [self.zfs_cmd, 'list', '-t', 'all', self.name]
        (rc, out, err) = self.module.run_command(' '.join(cmd))
        if rc == 0:
            return True
        else:
            return False

    def create(self):
        if self.module.check_mode:
            self.changed = True
            return
        properties = self.properties
        origin = self.module.params.get('origin', None)
        cmd = [self.zfs_cmd]

        if "@" in self.name:
            action = 'snapshot'
        elif origin:
            action = 'clone'
        else:
            action = 'create'

        cmd.append(action)

        if action in ['create', 'clone']:
            cmd += ['-p']

        if properties:
            for prop, value in properties.items():
                if prop == 'volsize':
                    cmd += ['-V', value]
                elif prop == 'volblocksize':
                    cmd += ['-b', value]
                else:
                    cmd += ['-o', '%s="%s"' % (prop, value)]
        if origin and action == 'clone':
            cmd.append(origin)
        cmd.append(self.name)
        (rc, out, err) = self.module.run_command(' '.join(cmd))
        if rc == 0:
            self.changed = True
        else:
            self.module.fail_json(msg=err)

    def destroy(self):
        if self.module.check_mode:
            self.changed = True
            return
        cmd = [self.zfs_cmd, 'destroy', '-R', self.name]
        (rc, out, err) = self.module.run_command(' '.join(cmd))
        if rc == 0:
            self.changed = True
        else:
            self.module.fail_json(msg=err)

    def set_property(self, prop, value):
        if self.module.check_mode:
            self.changed = True
            return
        cmd = [self.zfs_cmd, 'set', prop + '=' + str(value), self.name]
        (rc, out, err) = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg=err)

    def set_properties_if_changed(self):
        diff = {'before': {'extra_zfs_properties': {}}, 'after': {'extra_zfs_properties': {}}}
        current_properties = self.get_current_properties()
        for prop, value in self.properties.items():
            current_value = current_properties.get(prop, None)
            if current_value != value:
                self.set_property(prop, value)
                diff['before']['extra_zfs_properties'][prop] = current_value
                diff['after']['extra_zfs_properties'][prop] = value
        if self.module.check_mode:
            return diff
        updated_properties = self.get_current_properties()
        for prop in self.properties:
            value = updated_properties.get(prop, None)
            if value is None:
                self.module.fail_json(msg="zfsprop was not present after being successfully set: %s" % prop)
            if current_properties.get(prop, None) != value:
                self.changed = True
            if prop in diff['after']['extra_zfs_properties']:
                diff['after']['extra_zfs_properties'][prop] = value
        return diff

    def get_current_properties(self):
        cmd = [self.zfs_cmd, 'get', '-H', '-p', '-o', "property,value,source"]
        if self.enhanced_sharing:
            cmd += ['-e']
        cmd += ['all', self.name]
        rc, out, err = self.module.run_command(" ".join(cmd))
        properties = dict()
        for line in out.splitlines():
            prop, value, source = line.split('\t')
            # include source '-' so that creation-only properties are not removed
            # to avoids errors when the dataset already exists and the property is not changed
            # this scenario is most likely when the same playbook is run more than once
            if source == 'local' or source == 'received' or source == '-':
                properties[prop] = value
        # Add alias for enhanced sharing properties
        if self.enhanced_sharing:
            properties['sharenfs'] = properties.get('share.nfs', None)
            properties['sharesmb'] = properties.get('share.smb', None)
        return properties


def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', required=True, choices=['absent', 'present']),
            origin=dict(type='str', default=None),
            extra_zfs_properties=dict(type='dict', default={}),
        ),
        supports_check_mode=True,
    )

    state = module.params.get('state')
    name = module.params.get('name')

    if module.params.get('origin') and '@' in name:
        module.fail_json(msg='cannot specify origin when operating on a snapshot')

    # Reverse the boolification of zfs properties
    for prop, value in module.params['extra_zfs_properties'].items():
        if isinstance(value, bool):
            if value is True:
                module.params['extra_zfs_properties'][prop] = 'on'
            else:
                module.params['extra_zfs_properties'][prop] = 'off'
        else:
            module.params['extra_zfs_properties'][prop] = value

    result = dict(
        name=name,
        state=state,
    )

    zfs = Zfs(module, name, module.params['extra_zfs_properties'])

    if state == 'present':
        if zfs.exists():
            result['diff'] = zfs.set_properties_if_changed()
        else:
            zfs.create()
            result['diff'] = {'before': {'state': 'absent'}, 'after': {'state': state}}

    elif state == 'absent':
        if zfs.exists():
            zfs.destroy()
            result['diff'] = {'before': {'state': 'present'}, 'after': {'state': state}}
        else:
            result['diff'] = {}

    result['diff']['before_header'] = name
    result['diff']['after_header'] = name

    result.update(zfs.properties)
    result['changed'] = zfs.changed
    module.exit_json(**result)


if __name__ == '__main__':
    main()

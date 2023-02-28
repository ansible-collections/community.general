#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Adam Števko <adam.stevko@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: beadm
short_description: Manage ZFS boot environments on FreeBSD/Solaris/illumos systems
description:
    - Create, delete or activate ZFS boot environments.
    - Mount and unmount ZFS boot environments.
author: Adam Števko (@xen0l)
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
        description:
            - ZFS boot environment name.
        type: str
        required: true
        aliases: [ "be" ]
    snapshot:
        description:
            - If specified, the new boot environment will be cloned from the given
              snapshot or inactive boot environment.
        type: str
    description:
        description:
            - Associate a description with a new boot environment. This option is
              available only on Solarish platforms.
        type: str
    options:
        description:
            - Create the datasets for new BE with specific ZFS properties.
            - Multiple options can be specified.
            - This option is available only on Solarish platforms.
        type: str
    mountpoint:
        description:
            - Path where to mount the ZFS boot environment.
        type: path
    state:
        description:
            - Create or delete ZFS boot environment.
        type: str
        choices: [ absent, activated, mounted, present, unmounted ]
        default: present
    force:
        description:
            - Specifies if the unmount should be forced.
        type: bool
        default: false
'''

EXAMPLES = r'''
- name: Create ZFS boot environment
  community.general.beadm:
    name: upgrade-be
    state: present

- name: Create ZFS boot environment from existing inactive boot environment
  community.general.beadm:
    name: upgrade-be
    snapshot: be@old
    state: present

- name: Create ZFS boot environment with compression enabled and description "upgrade"
  community.general.beadm:
    name: upgrade-be
    options: "compression=on"
    description: upgrade
    state: present

- name: Delete ZFS boot environment
  community.general.beadm:
    name: old-be
    state: absent

- name: Mount ZFS boot environment on /tmp/be
  community.general.beadm:
    name: BE
    mountpoint: /tmp/be
    state: mounted

- name: Unmount ZFS boot environment
  community.general.beadm:
    name: BE
    state: unmounted

- name: Activate ZFS boot environment
  community.general.beadm:
    name: upgrade-be
    state: activated
'''

RETURN = r'''
name:
    description: BE name
    returned: always
    type: str
    sample: pre-upgrade
snapshot:
    description: ZFS snapshot to create BE from
    returned: always
    type: str
    sample: rpool/ROOT/oi-hipster@fresh
description:
    description: BE description
    returned: always
    type: str
    sample: Upgrade from 9.0 to 10.0
options:
    description: BE additional options
    returned: always
    type: str
    sample: compression=on
mountpoint:
    description: BE mountpoint
    returned: always
    type: str
    sample: /mnt/be
state:
    description: state of the target
    returned: always
    type: str
    sample: present
force:
    description: If forced action is wanted
    returned: always
    type: bool
    sample: false
'''

import os
from ansible.module_utils.basic import AnsibleModule


class BE(object):
    def __init__(self, module):
        self.module = module

        self.name = module.params['name']
        self.snapshot = module.params['snapshot']
        self.description = module.params['description']
        self.options = module.params['options']
        self.mountpoint = module.params['mountpoint']
        self.state = module.params['state']
        self.force = module.params['force']
        self.is_freebsd = os.uname()[0] == 'FreeBSD'

    def _beadm_list(self):
        cmd = [self.module.get_bin_path('beadm'), 'list', '-H']
        if '@' in self.name:
            cmd.append('-s')
        return self.module.run_command(cmd)

    def _find_be_by_name(self, out):
        if '@' in self.name:
            for line in out.splitlines():
                if self.is_freebsd:
                    check = line.split()
                    if check == []:
                        continue
                    full_name = check[0].split('/')
                    if full_name == []:
                        continue
                    check[0] = full_name[len(full_name) - 1]
                    if check[0] == self.name:
                        return check
                else:
                    check = line.split(';')
                    if check[0] == self.name:
                        return check
        else:
            for line in out.splitlines():
                if self.is_freebsd:
                    check = line.split()
                    if check[0] == self.name:
                        return check
                else:
                    check = line.split(';')
                    if check[0] == self.name:
                        return check
        return None

    def exists(self):
        (rc, out, dummy) = self._beadm_list()

        if rc == 0:
            if self._find_be_by_name(out):
                return True
            else:
                return False
        else:
            return False

    def is_activated(self):
        (rc, out, dummy) = self._beadm_list()

        if rc == 0:
            line = self._find_be_by_name(out)
            if line is None:
                return False
            if self.is_freebsd:
                if 'R' in line[1]:
                    return True
            else:
                if 'R' in line[2]:
                    return True

        return False

    def activate_be(self):
        cmd = [self.module.get_bin_path('beadm'), 'activate', self.name]
        return self.module.run_command(cmd)

    def create_be(self):
        cmd = [self.module.get_bin_path('beadm'), 'create']

        if self.snapshot:
            cmd.extend(['-e', self.snapshot])
        if not self.is_freebsd:
            if self.description:
                cmd.extend(['-d', self.description])
            if self.options:
                cmd.extend(['-o', self.options])

        cmd.append(self.name)

        return self.module.run_command(cmd)

    def destroy_be(self):
        cmd = [self.module.get_bin_path('beadm'), 'destroy', '-F', self.name]
        return self.module.run_command(cmd)

    def is_mounted(self):
        (rc, out, dummy) = self._beadm_list()

        if rc == 0:
            line = self._find_be_by_name(out)
            if line is None:
                return False
            if self.is_freebsd:
                # On FreeBSD, we exclude currently mounted BE on /, as it is
                # special and can be activated even if it is mounted. That is not
                # possible with non-root BEs.
                if line[2] != '-' and line[2] != '/':
                    return True
            else:
                if line[3]:
                    return True

        return False

    def mount_be(self):
        cmd = [self.module.get_bin_path('beadm'), 'mount', self.name]

        if self.mountpoint:
            cmd.append(self.mountpoint)

        return self.module.run_command(cmd)

    def unmount_be(self):
        cmd = [self.module.get_bin_path('beadm'), 'unmount']
        if self.force:
            cmd.append('-f')
        cmd.append(self.name)

        return self.module.run_command(cmd)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, aliases=['be']),
            snapshot=dict(type='str'),
            description=dict(type='str'),
            options=dict(type='str'),
            mountpoint=dict(type='path'),
            state=dict(type='str', default='present', choices=['absent', 'activated', 'mounted', 'present', 'unmounted']),
            force=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    be = BE(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = be.name
    result['state'] = be.state

    if be.snapshot:
        result['snapshot'] = be.snapshot

    if be.description:
        result['description'] = be.description

    if be.options:
        result['options'] = be.options

    if be.mountpoint:
        result['mountpoint'] = be.mountpoint

    if be.state == 'absent':
        # beadm on FreeBSD and Solarish systems differs in delete behaviour in
        # that we are not allowed to delete activated BE on FreeBSD while on
        # Solarish systems we cannot delete BE if it is mounted. We add mount
        # check for both platforms as BE should be explicitly unmounted before
        # being deleted. On FreeBSD, we also check if the BE is activated.
        if be.exists():
            if not be.is_mounted():
                if module.check_mode:
                    module.exit_json(changed=True)

                if be.is_freebsd:
                    if be.is_activated():
                        module.fail_json(msg='Unable to remove active BE!')

                (rc, out, err) = be.destroy_be()

                if rc != 0:
                    module.fail_json(msg='Error while destroying BE: "%s"' % err,
                                     name=be.name,
                                     stderr=err,
                                     rc=rc)
            else:
                module.fail_json(msg='Unable to remove BE as it is mounted!')

    elif be.state == 'present':
        if not be.exists():
            if module.check_mode:
                module.exit_json(changed=True)

            (rc, out, err) = be.create_be()

            if rc != 0:
                module.fail_json(msg='Error while creating BE: "%s"' % err,
                                 name=be.name,
                                 stderr=err,
                                 rc=rc)

    elif be.state == 'activated':
        if not be.is_activated():
            if module.check_mode:
                module.exit_json(changed=True)

            # On FreeBSD, beadm is unable to activate mounted BEs, so we add
            # an explicit check for that case.
            if be.is_freebsd:
                if be.is_mounted():
                    module.fail_json(msg='Unable to activate mounted BE!')

            (rc, out, err) = be.activate_be()

            if rc != 0:
                module.fail_json(msg='Error while activating BE: "%s"' % err,
                                 name=be.name,
                                 stderr=err,
                                 rc=rc)
    elif be.state == 'mounted':
        if not be.is_mounted():
            if module.check_mode:
                module.exit_json(changed=True)

            (rc, out, err) = be.mount_be()

            if rc != 0:
                module.fail_json(msg='Error while mounting BE: "%s"' % err,
                                 name=be.name,
                                 stderr=err,
                                 rc=rc)

    elif be.state == 'unmounted':
        if be.is_mounted():
            if module.check_mode:
                module.exit_json(changed=True)

            (rc, out, err) = be.unmount_be()

            if rc != 0:
                module.fail_json(msg='Error while unmounting BE: "%s"' % err,
                                 name=be.name,
                                 stderr=err,
                                 rc=rc)

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True

    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


if __name__ == '__main__':
    main()

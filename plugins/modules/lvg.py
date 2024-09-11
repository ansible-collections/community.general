#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Alexander Bulimov <lazywolf0@gmail.com>
# Based on lvol module by Jeroen Hoekx <jeroen.hoekx@dsquare.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
author:
- Alexander Bulimov (@abulimov)
module: lvg
short_description: Configure LVM volume groups
description:
  - This module creates, removes or resizes volume groups.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  vg:
    description:
    - The name of the volume group.
    type: str
    required: true
  pvs:
    description:
    - List of comma-separated devices to use as physical devices in this volume group.
    - Required when creating or resizing volume group.
    - The module will take care of running pvcreate if needed.
    type: list
    elements: str
  pesize:
    description:
    - "The size of the physical extent. O(pesize) must be a power of 2 of at least 1 sector
       (where the sector size is the largest sector size of the PVs currently used in the VG),
       or at least 128KiB."
    - O(pesize) can be optionally suffixed by a UNIT (k/K/m/M/g/G), default unit is megabyte.
    type: str
    default: "4"
  pv_options:
    description:
    - Additional options to pass to C(pvcreate) when creating the volume group.
    type: str
    default: ''
  pvresize:
    description:
    - If V(true), resize the physical volume to the maximum available size.
    type: bool
    default: false
    version_added: '0.2.0'
  vg_options:
    description:
    - Additional options to pass to C(vgcreate) when creating the volume group.
    type: str
    default: ''
  state:
    description:
    - Control if the volume group exists and it's state.
    - The states V(active) and V(inactive) implies V(present) state. Added in 7.1.0
    - "If V(active) or V(inactive), the module manages the VG's logical volumes current state.
       The module also handles the VG's autoactivation state if supported
       unless when creating a volume group and the autoactivation option specified in O(vg_options)."
    type: str
    choices: [ absent, present, active, inactive ]
    default: present
  force:
    description:
    - If V(true), allows to remove volume group with logical volumes.
    type: bool
    default: false
  reset_vg_uuid:
    description:
    - Whether the volume group's UUID is regenerated.
    - This is B(not idempotent). Specifying this parameter always results in a change.
    type: bool
    default: false
    version_added: 7.1.0
  reset_pv_uuid:
    description:
    - Whether the volume group's physical volumes' UUIDs are regenerated.
    - This is B(not idempotent). Specifying this parameter always results in a change.
    type: bool
    default: false
    version_added: 7.1.0
seealso:
- module: community.general.filesystem
- module: community.general.lvol
- module: community.general.parted
notes:
  - This module does not modify PE size for already present volume group.
'''

EXAMPLES = r'''
- name: Create a volume group on top of /dev/sda1 with physical extent size = 32MB
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sda1
    pesize: 32

- name: Create a volume group on top of /dev/sdb with physical extent size = 128KiB
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sdb
    pesize: 128K

# If, for example, we already have VG vg.services on top of /dev/sdb1,
# this VG will be extended by /dev/sdc5.  Or if vg.services was created on
# top of /dev/sda5, we first extend it with /dev/sdb1 and /dev/sdc5,
# and then reduce by /dev/sda5.
- name: Create or resize a volume group on top of /dev/sdb1 and /dev/sdc5.
  community.general.lvg:
    vg: vg.services
    pvs: /dev/sdb1,/dev/sdc5

- name: Remove a volume group with name vg.services
  community.general.lvg:
    vg: vg.services
    state: absent

- name: Create a volume group on top of /dev/sda3 and resize the volume group /dev/sda3 to the maximum possible
  community.general.lvg:
    vg: resizableVG
    pvs: /dev/sda3
    pvresize: true

- name: Deactivate a volume group
  community.general.lvg:
    state: inactive
    vg: vg.services

- name: Activate a volume group
  community.general.lvg:
    state: active
    vg: vg.services

- name: Reset a volume group UUID
  community.general.lvg:
    state: inactive
    vg: vg.services
    reset_vg_uuid: true

- name: Reset both volume group and pv UUID
  community.general.lvg:
    state: inactive
    vg: vg.services
    pvs: /dev/sdb1,/dev/sdc5
    reset_vg_uuid: true
    reset_pv_uuid: true
'''

import itertools
import os

from ansible.module_utils.basic import AnsibleModule

VG_AUTOACTIVATION_OPT = '--setautoactivation'


def parse_vgs(data):
    vgs = []
    for line in data.splitlines():
        parts = line.strip().split(';')
        vgs.append({
            'name': parts[0],
            'pv_count': int(parts[1]),
            'lv_count': int(parts[2]),
        })
    return vgs


def find_mapper_device_name(module, dm_device):
    dmsetup_cmd = module.get_bin_path('dmsetup', True)
    mapper_prefix = '/dev/mapper/'
    rc, dm_name, err = module.run_command([dmsetup_cmd, "info", "-C", "--noheadings", "-o", "name", dm_device])
    if rc != 0:
        module.fail_json(msg="Failed executing dmsetup command.", rc=rc, err=err)
    mapper_device = mapper_prefix + dm_name.rstrip()
    return mapper_device


def parse_pvs(module, data):
    pvs = []
    dm_prefix = '/dev/dm-'
    for line in data.splitlines():
        parts = line.strip().split(';')
        if parts[0].startswith(dm_prefix):
            parts[0] = find_mapper_device_name(module, parts[0])
        pvs.append({
            'name': parts[0],
            'vg_name': parts[1],
        })
    return pvs


def find_vg(module, vg):
    if not vg:
        return None
    vgs_cmd = module.get_bin_path('vgs', True)
    dummy, current_vgs, dummy = module.run_command([vgs_cmd, "--noheadings", "-o", "vg_name,pv_count,lv_count", "--separator", ";"], check_rc=True)

    vgs = parse_vgs(current_vgs)

    for test_vg in vgs:
        if test_vg['name'] == vg:
            this_vg = test_vg
            break
    else:
        this_vg = None

    return this_vg


def is_autoactivation_supported(module, vg_cmd):
    autoactivation_supported = False
    dummy, vgchange_opts, dummy = module.run_command([vg_cmd, '--help'], check_rc=True)

    if VG_AUTOACTIVATION_OPT in vgchange_opts:
        autoactivation_supported = True

    return autoactivation_supported


def activate_vg(module, vg, active):
    changed = False
    vgchange_cmd = module.get_bin_path('vgchange', True)
    vgs_cmd = module.get_bin_path('vgs', True)
    vgs_fields = ['lv_attr']

    autoactivation_enabled = False
    autoactivation_supported = is_autoactivation_supported(module=module, vg_cmd=vgchange_cmd)

    if autoactivation_supported:
        vgs_fields.append('autoactivation')

    vgs_cmd_with_opts = [vgs_cmd, '--noheadings', '-o', ','.join(vgs_fields), '--separator', ';', vg]
    dummy, current_vg_lv_states, dummy = module.run_command(vgs_cmd_with_opts, check_rc=True)

    lv_active_count = 0
    lv_inactive_count = 0

    for line in current_vg_lv_states.splitlines():
        parts = line.strip().split(';')
        if parts[0][4] == 'a':
            lv_active_count += 1
        else:
            lv_inactive_count += 1
        if autoactivation_supported:
            autoactivation_enabled = autoactivation_enabled or parts[1] == 'enabled'

    activate_flag = None
    if active and lv_inactive_count > 0:
        activate_flag = 'y'
    elif not active and lv_active_count > 0:
        activate_flag = 'n'

    # Extra logic necessary because vgchange returns error when autoactivation is already set
    if autoactivation_supported:
        if active and not autoactivation_enabled:
            if module.check_mode:
                changed = True
            else:
                module.run_command([vgchange_cmd, VG_AUTOACTIVATION_OPT, 'y', vg], check_rc=True)
                changed = True
        elif not active and autoactivation_enabled:
            if module.check_mode:
                changed = True
            else:
                module.run_command([vgchange_cmd, VG_AUTOACTIVATION_OPT, 'n', vg], check_rc=True)
                changed = True

    if activate_flag is not None:
        if module.check_mode:
            changed = True
        else:
            module.run_command([vgchange_cmd, '--activate', activate_flag, vg], check_rc=True)
            changed = True

    return changed


def append_vgcreate_options(module, state, vgoptions):
    vgcreate_cmd = module.get_bin_path('vgcreate', True)

    autoactivation_supported = is_autoactivation_supported(module=module, vg_cmd=vgcreate_cmd)

    if autoactivation_supported and state in ['active', 'inactive']:
        if VG_AUTOACTIVATION_OPT not in vgoptions:
            if state == 'active':
                vgoptions += [VG_AUTOACTIVATION_OPT, 'y']
            else:
                vgoptions += [VG_AUTOACTIVATION_OPT, 'n']


def get_pv_values_for_resize(module, device):
    pvdisplay_cmd = module.get_bin_path('pvdisplay', True)
    pvdisplay_ops = ["--units", "b", "--columns", "--noheadings", "--nosuffix", "--separator", ";", "-o", "dev_size,pv_size,pe_start,vg_extent_size"]
    pvdisplay_cmd_device_options = [pvdisplay_cmd, device] + pvdisplay_ops

    dummy, pv_values, dummy = module.run_command(pvdisplay_cmd_device_options, check_rc=True)

    values = pv_values.strip().split(';')

    dev_size = int(values[0])
    pv_size = int(values[1])
    pe_start = int(values[2])
    vg_extent_size = int(values[3])

    return (dev_size, pv_size, pe_start, vg_extent_size)


def resize_pv(module, device):
    changed = False
    pvresize_cmd = module.get_bin_path('pvresize', True)

    dev_size, pv_size, pe_start, vg_extent_size = get_pv_values_for_resize(module=module, device=device)
    if (dev_size - (pe_start + pv_size)) > vg_extent_size:
        if module.check_mode:
            changed = True
        else:
            # If there is a missing pv on the machine, versions of pvresize rc indicates failure.
            rc, out, err = module.run_command([pvresize_cmd, device])
            dummy, new_pv_size, dummy, dummy = get_pv_values_for_resize(module=module, device=device)
            if pv_size == new_pv_size:
                module.fail_json(msg="Failed executing pvresize command.", rc=rc, err=err, out=out)
            else:
                changed = True

    return changed


def reset_uuid_pv(module, device):
    changed = False
    pvs_cmd = module.get_bin_path('pvs', True)
    pvs_cmd_with_opts = [pvs_cmd, '--noheadings', '-o', 'uuid', device]
    pvchange_cmd = module.get_bin_path('pvchange', True)
    pvchange_cmd_with_opts = [pvchange_cmd, '-u', device]

    dummy, orig_uuid, dummy = module.run_command(pvs_cmd_with_opts, check_rc=True)

    if module.check_mode:
        changed = True
    else:
        # If there is a missing pv on the machine, pvchange rc indicates failure.
        pvchange_rc, pvchange_out, pvchange_err = module.run_command(pvchange_cmd_with_opts)
        dummy, new_uuid, dummy = module.run_command(pvs_cmd_with_opts, check_rc=True)
        if orig_uuid.strip() == new_uuid.strip():
            module.fail_json(msg="PV (%s) UUID change failed" % (device), rc=pvchange_rc, err=pvchange_err, out=pvchange_out)
        else:
            changed = True

    return changed


def reset_uuid_vg(module, vg):
    changed = False
    vgchange_cmd = module.get_bin_path('vgchange', True)
    vgchange_cmd_with_opts = [vgchange_cmd, '-u', vg]
    if module.check_mode:
        changed = True
    else:
        module.run_command(vgchange_cmd_with_opts, check_rc=True)
        changed = True

    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vg=dict(type='str', required=True),
            pvs=dict(type='list', elements='str'),
            pesize=dict(type='str', default='4'),
            pv_options=dict(type='str', default=''),
            pvresize=dict(type='bool', default=False),
            vg_options=dict(type='str', default=''),
            state=dict(type='str', default='present', choices=['absent', 'present', 'active', 'inactive']),
            force=dict(type='bool', default=False),
            reset_vg_uuid=dict(type='bool', default=False),
            reset_pv_uuid=dict(type='bool', default=False),
        ),
        required_if=[
            ['reset_pv_uuid', True, ['pvs']],
        ],
        supports_check_mode=True,
    )

    vg = module.params['vg']
    state = module.params['state']
    force = module.boolean(module.params['force'])
    pvresize = module.boolean(module.params['pvresize'])
    pesize = module.params['pesize']
    pvoptions = module.params['pv_options'].split()
    vgoptions = module.params['vg_options'].split()
    reset_vg_uuid = module.boolean(module.params['reset_vg_uuid'])
    reset_pv_uuid = module.boolean(module.params['reset_pv_uuid'])

    this_vg = find_vg(module=module, vg=vg)
    present_state = state in ['present', 'active', 'inactive']
    pvs_required = present_state and this_vg is None
    changed = False

    dev_list = []
    if module.params['pvs']:
        dev_list = list(module.params['pvs'])
    elif pvs_required:
        module.fail_json(msg="No physical volumes given.")

    # LVM always uses real paths not symlinks so replace symlinks with actual path
    for idx, dev in enumerate(dev_list):
        dev_list[idx] = os.path.realpath(dev)

    if present_state:
        # check given devices
        for test_dev in dev_list:
            if not os.path.exists(test_dev):
                module.fail_json(msg="Device %s not found." % test_dev)

        # get pv list
        pvs_cmd = module.get_bin_path('pvs', True)
        if dev_list:
            pvs_filter_pv_name = ' || '.join(
                'pv_name = {0}'.format(x)
                for x in itertools.chain(dev_list, module.params['pvs'])
            )
            pvs_filter_vg_name = 'vg_name = {0}'.format(vg)
            pvs_filter = ["--select", "{0} || {1}".format(pvs_filter_pv_name, pvs_filter_vg_name)]
        else:
            pvs_filter = []
        rc, current_pvs, err = module.run_command([pvs_cmd, "--noheadings", "-o", "pv_name,vg_name", "--separator", ";"] + pvs_filter)
        if rc != 0:
            module.fail_json(msg="Failed executing pvs command.", rc=rc, err=err)

        # check pv for devices
        pvs = parse_pvs(module, current_pvs)
        used_pvs = [pv for pv in pvs if pv['name'] in dev_list and pv['vg_name'] and pv['vg_name'] != vg]
        if used_pvs:
            module.fail_json(msg="Device %s is already in %s volume group." % (used_pvs[0]['name'], used_pvs[0]['vg_name']))

    if this_vg is None:
        if present_state:
            append_vgcreate_options(module=module, state=state, vgoptions=vgoptions)
            # create VG
            if module.check_mode:
                changed = True
            else:
                # create PV
                pvcreate_cmd = module.get_bin_path('pvcreate', True)
                for current_dev in dev_list:
                    rc, dummy, err = module.run_command([pvcreate_cmd] + pvoptions + ['-f', str(current_dev)])
                    if rc == 0:
                        changed = True
                    else:
                        module.fail_json(msg="Creating physical volume '%s' failed" % current_dev, rc=rc, err=err)
                vgcreate_cmd = module.get_bin_path('vgcreate')
                rc, dummy, err = module.run_command([vgcreate_cmd] + vgoptions + ['-s', pesize, vg] + dev_list)
                if rc == 0:
                    changed = True
                else:
                    module.fail_json(msg="Creating volume group '%s' failed" % vg, rc=rc, err=err)
    else:
        if state == 'absent':
            if module.check_mode:
                module.exit_json(changed=True)
            else:
                if this_vg['lv_count'] == 0 or force:
                    # remove VG
                    vgremove_cmd = module.get_bin_path('vgremove', True)
                    rc, dummy, err = module.run_command([vgremove_cmd, "--force", vg])
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to remove volume group %s" % (vg), rc=rc, err=err)
                else:
                    module.fail_json(msg="Refuse to remove non-empty volume group %s without force=true" % (vg))
        # activate/deactivate existing VG
        elif state == 'active':
            changed = activate_vg(module=module, vg=vg, active=True)
        elif state == 'inactive':
            changed = activate_vg(module=module, vg=vg, active=False)

        # reset VG uuid
        if reset_vg_uuid:
            changed = reset_uuid_vg(module=module, vg=vg) or changed

        # resize VG
        if dev_list:
            current_devs = [os.path.realpath(pv['name']) for pv in pvs if pv['vg_name'] == vg]
            devs_to_remove = list(set(current_devs) - set(dev_list))
            devs_to_add = list(set(dev_list) - set(current_devs))

            if current_devs:
                if present_state:
                    for device in current_devs:
                        if pvresize:
                            changed = resize_pv(module=module, device=device) or changed
                        if reset_pv_uuid:
                            changed = reset_uuid_pv(module=module, device=device) or changed

            if devs_to_add or devs_to_remove:
                if module.check_mode:
                    changed = True
                else:
                    if devs_to_add:
                        # create PV
                        pvcreate_cmd = module.get_bin_path('pvcreate', True)
                        for current_dev in devs_to_add:
                            rc, dummy, err = module.run_command([pvcreate_cmd] + pvoptions + ['-f', str(current_dev)])
                            if rc == 0:
                                changed = True
                            else:
                                module.fail_json(msg="Creating physical volume '%s' failed" % current_dev, rc=rc, err=err)
                        # add PV to our VG
                        vgextend_cmd = module.get_bin_path('vgextend', True)
                        rc, dummy, err = module.run_command([vgextend_cmd, vg] + devs_to_add)
                        if rc == 0:
                            changed = True
                        else:
                            module.fail_json(msg="Unable to extend %s by %s." % (vg, ' '.join(devs_to_add)), rc=rc, err=err)

                    # remove some PV from our VG
                    if devs_to_remove:
                        vgreduce_cmd = module.get_bin_path('vgreduce', True)
                        rc, dummy, err = module.run_command([vgreduce_cmd, "--force", vg] + devs_to_remove)
                        if rc == 0:
                            changed = True
                        else:
                            module.fail_json(msg="Unable to reduce %s by %s." % (vg, ' '.join(devs_to_remove)), rc=rc, err=err)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

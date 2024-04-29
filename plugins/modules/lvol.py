#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Jeroen Hoekx <jeroen.hoekx@dsquare.be>, Alexander Bulimov <lazywolf0@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
author:
    - Jeroen Hoekx (@jhoekx)
    - Alexander Bulimov (@abulimov)
    - Raoul Baudach (@unkaputtbar112)
    - Ziga Kern (@zigaSRC)
module: lvol
short_description: Configure LVM logical volumes
description:
  - This module creates, removes or resizes logical volumes.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  vg:
    type: str
    required: true
    description:
    - The volume group this logical volume is part of.
  lv:
    type: str
    description:
    - The name of the logical volume.
  size:
    type: str
    description:
    - The size of the logical volume, according to lvcreate(8) --size, by
      default in megabytes or optionally with one of [bBsSkKmMgGtTpPeE] units; or
      according to lvcreate(8) --extents as a percentage of [VG|PVS|FREE|ORIGIN];
      Float values must begin with a digit.
    - When resizing, apart from specifying an absolute size you may, according to
      lvextend(8)|lvreduce(8) C(--size), specify the amount to extend the logical volume with
      the prefix V(+) or the amount to reduce the logical volume by with prefix V(-).
    - Resizing using V(+) or V(-) was not supported prior to community.general 3.0.0.
    - Please note that when using V(+), V(-), or percentage of FREE, the module is B(not idempotent).
  state:
    type: str
    description:
    - Control if the logical volume exists. If V(present) and the
      volume does not already exist then the O(size) option is required.
    choices: [ absent, present ]
    default: present
  active:
    description:
    - Whether the volume is active and visible to the host.
    type: bool
    default: true
  force:
    description:
    - Shrink or remove operations of volumes requires this switch. Ensures that
      that filesystems get never corrupted/destroyed by mistake.
    type: bool
    default: false
  opts:
    type: str
    description:
    - Free-form options to be passed to the lvcreate command.
  snapshot:
    type: str
    description:
    - The name of a snapshot volume to be configured. When creating a snapshot volume, the O(lv) parameter specifies the origin volume.
  pvs:
    type: list
    elements: str
    description:
    - List of physical volumes (for example V(/dev/sda, /dev/sdb)).
  thinpool:
    type: str
    description:
    - The thin pool volume name. When you want to create a thin provisioned volume, specify a thin pool volume name.
  shrink:
    description:
    - Shrink if current size is higher than size requested.
    type: bool
    default: true
  resizefs:
    description:
    - Resize the underlying filesystem together with the logical volume.
    - Supported for C(ext2), C(ext3), C(ext4), C(reiserfs) and C(XFS) filesystems.
      Attempts to resize other filesystem types will fail.
    type: bool
    default: false
notes:
  - You must specify lv (when managing the state of logical volumes) or thinpool (when managing a thin provisioned volume).
'''

EXAMPLES = '''
- name: Create a logical volume of 512m
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512

- name: Create a logical volume of 512m with disks /dev/sda and /dev/sdb
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512
    pvs:
      - /dev/sda
      - /dev/sdb

- name: Create cache pool logical volume
  community.general.lvol:
    vg: firefly
    lv: lvcache
    size: 512m
    opts: --type cache-pool

- name: Create a logical volume of 512g.
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512g

- name: Create a logical volume the size of all remaining space in the volume group
  community.general.lvol:
    vg: firefly
    lv: test
    size: 100%FREE

- name: Create a logical volume with special options
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512g
    opts: -r 16

- name: Extend the logical volume to 1024m.
  community.general.lvol:
    vg: firefly
    lv: test
    size: 1024

- name: Extend the logical volume to consume all remaining space in the volume group
  community.general.lvol:
    vg: firefly
    lv: test
    size: +100%FREE

- name: Extend the logical volume by given space
  community.general.lvol:
    vg: firefly
    lv: test
    size: +512M

- name: Extend the logical volume to take all remaining space of the PVs and resize the underlying filesystem
  community.general.lvol:
    vg: firefly
    lv: test
    size: 100%PVS
    resizefs: true

- name: Resize the logical volume to % of VG
  community.general.lvol:
    vg: firefly
    lv: test
    size: 80%VG
    force: true

- name: Reduce the logical volume to 512m
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512
    force: true

- name: Reduce the logical volume by given space
  community.general.lvol:
    vg: firefly
    lv: test
    size: -512M
    force: true

- name: Set the logical volume to 512m and do not try to shrink if size is lower than current one
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512
    shrink: false

- name: Remove the logical volume.
  community.general.lvol:
    vg: firefly
    lv: test
    state: absent
    force: true

- name: Create a snapshot volume of the test logical volume.
  community.general.lvol:
    vg: firefly
    lv: test
    snapshot: snap1
    size: 100m

- name: Deactivate a logical volume
  community.general.lvol:
    vg: firefly
    lv: test
    active: false

- name: Create a deactivated logical volume
  community.general.lvol:
    vg: firefly
    lv: test
    size: 512g
    active: false

- name: Create a thin pool of 512g
  community.general.lvol:
    vg: firefly
    thinpool: testpool
    size: 512g

- name: Create a thin volume of 128g
  community.general.lvol:
    vg: firefly
    lv: test
    thinpool: testpool
    size: 128g
'''

import re
import shlex

from ansible.module_utils.basic import AnsibleModule

LVOL_ENV_VARS = dict(
    # make sure we use the C locale when running lvol-related commands
    LANG='C',
    LC_ALL='C',
    LC_MESSAGES='C',
    LC_CTYPE='C',
)


def mkversion(major, minor, patch):
    return (1000 * 1000 * int(major)) + (1000 * int(minor)) + int(patch)


def parse_lvs(data):
    lvs = []
    for line in data.splitlines():
        parts = line.strip().split(';')
        lvs.append({
            'name': parts[0].replace('[', '').replace(']', ''),
            'size': float(parts[1]),
            'active': (parts[2][4] == 'a'),
            'thinpool': (parts[2][0] == 't'),
            'thinvol': (parts[2][0] == 'V'),
        })
    return lvs


def parse_vgs(data):
    vgs = []
    for line in data.splitlines():
        parts = line.strip().split(';')
        vgs.append({
            'name': parts[0],
            'size': float(parts[1]),
            'free': float(parts[2]),
            'ext_size': float(parts[3])
        })
    return vgs


def get_lvm_version(module):
    ver_cmd = module.get_bin_path("lvm", required=True)
    rc, out, err = module.run_command([ver_cmd, "version"])
    if rc != 0:
        return None
    m = re.search(r"LVM version:\s+(\d+)\.(\d+)\.(\d+).*(\d{4}-\d{2}-\d{2})", out)
    if not m:
        return None
    return mkversion(m.group(1), m.group(2), m.group(3))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vg=dict(type='str', required=True),
            lv=dict(type='str'),
            size=dict(type='str'),
            opts=dict(type='str'),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            force=dict(type='bool', default=False),
            shrink=dict(type='bool', default=True),
            active=dict(type='bool', default=True),
            snapshot=dict(type='str'),
            pvs=dict(type='list', elements='str'),
            resizefs=dict(type='bool', default=False),
            thinpool=dict(type='str'),
        ),
        supports_check_mode=True,
        required_one_of=(
            ['lv', 'thinpool'],
        ),
    )

    module.run_command_environ_update = LVOL_ENV_VARS

    # Determine if the "--yes" option should be used
    version_found = get_lvm_version(module)
    if version_found is None:
        module.fail_json(msg="Failed to get LVM version number")
    version_yesopt = mkversion(2, 2, 99)  # First LVM with the "--yes" option
    if version_found >= version_yesopt:
        yesopt = ["--yes"]
    else:
        yesopt = []

    vg = module.params['vg']
    lv = module.params['lv']
    size = module.params['size']
    opts = shlex.split(module.params['opts'] or '')
    state = module.params['state']
    force = module.boolean(module.params['force'])
    shrink = module.boolean(module.params['shrink'])
    active = module.boolean(module.params['active'])
    resizefs = module.boolean(module.params['resizefs'])
    thinpool = module.params['thinpool']
    size_opt = 'L'
    size_unit = 'm'
    size_operator = None
    snapshot = module.params['snapshot']
    pvs = module.params['pvs'] or []

    # Add --test option when running in check-mode
    if module.check_mode:
        test_opt = ['--test']
    else:
        test_opt = []

    if size:
        # LVEXTEND(8)/LVREDUCE(8) -l, -L options: Check for relative value for resizing
        if size.startswith('+'):
            size_operator = '+'
            size = size[1:]
        elif size.startswith('-'):
            size_operator = '-'
            size = size[1:]
        # LVCREATE(8) does not support [+-]

        # LVCREATE(8)/LVEXTEND(8)/LVREDUCE(8) -l --extents option with percentage
        if '%' in size:
            size_parts = size.split('%', 1)
            size_percent = int(size_parts[0])
            if size_percent > 100:
                module.fail_json(msg="Size percentage cannot be larger than 100%")
            size_whole = size_parts[1]
            if size_whole == 'ORIGIN' and snapshot is None:
                module.fail_json(msg="Percentage of ORIGIN supported only for snapshot volumes")
            elif size_whole not in ['VG', 'PVS', 'FREE', 'ORIGIN']:
                module.fail_json(msg="Specify extents as a percentage of VG|PVS|FREE|ORIGIN")
            size_opt = 'l'
            size_unit = ''

        # LVCREATE(8)/LVEXTEND(8)/LVREDUCE(8) -L --size option unit
        if '%' not in size:
            if size[-1].lower() in 'bskmgtpe':
                size_unit = size[-1]
                size = size[0:-1]

            try:
                float(size)
                if not size[0].isdigit():
                    raise ValueError()
            except ValueError:
                module.fail_json(msg="Bad size specification of '%s'" % size)

    # when no unit, megabytes by default
    if size_opt == 'l':
        unit = 'm'
    else:
        unit = size_unit

    # Get information on volume group requested
    vgs_cmd = module.get_bin_path("vgs", required=True)
    rc, current_vgs, err = module.run_command(
        [vgs_cmd, "--noheadings", "--nosuffix", "-o", "vg_name,size,free,vg_extent_size", "--units", unit.lower(), "--separator", ";", vg])

    if rc != 0:
        if state == 'absent':
            module.exit_json(changed=False, stdout="Volume group %s does not exist." % vg)
        else:
            module.fail_json(msg="Volume group %s does not exist." % vg, rc=rc, err=err)

    vgs = parse_vgs(current_vgs)
    this_vg = vgs[0]

    # Get information on logical volume requested
    lvs_cmd = module.get_bin_path("lvs", required=True)
    rc, current_lvs, err = module.run_command(
        [lvs_cmd, "-a", "--noheadings", "--nosuffix", "-o", "lv_name,size,lv_attr", "--units", unit.lower(), "--separator", ";", vg])

    if rc != 0:
        if state == 'absent':
            module.exit_json(changed=False, stdout="Volume group %s does not exist." % vg)
        else:
            module.fail_json(msg="Volume group %s does not exist." % vg, rc=rc, err=err)

    changed = False

    lvs = parse_lvs(current_lvs)

    if snapshot:
        # Check snapshot pre-conditions
        for test_lv in lvs:
            if test_lv['name'] == lv or test_lv['name'] == thinpool:
                if not test_lv['thinpool'] and not thinpool:
                    break
                else:
                    module.fail_json(msg="Snapshots of thin pool LVs are not supported.")
        else:
            module.fail_json(msg="Snapshot origin LV %s does not exist in volume group %s." % (lv, vg))
        check_lv = snapshot
    elif thinpool:
        if lv:
            # Check thin volume pre-conditions
            for test_lv in lvs:
                if test_lv['name'] == thinpool:
                    break
            else:
                module.fail_json(msg="Thin pool LV %s does not exist in volume group %s." % (thinpool, vg))
            check_lv = lv
        else:
            check_lv = thinpool
    else:
        check_lv = lv

    for test_lv in lvs:
        if test_lv['name'] in (check_lv, check_lv.rsplit('/', 1)[-1]):
            this_lv = test_lv
            break
    else:
        this_lv = None

    msg = ''
    if this_lv is None:
        if state == 'present':
            if size_operator is not None:
                if size_operator == "-" or (size_whole not in ["VG", "PVS", "FREE", "ORIGIN", None]):
                    module.fail_json(msg="Bad size specification of '%s%s' for creating LV" % (size_operator, size))
            # Require size argument except for snapshot of thin volumes
            if (lv or thinpool) and not size:
                for test_lv in lvs:
                    if test_lv['name'] == lv and test_lv['thinvol'] and snapshot:
                        break
                else:
                    module.fail_json(msg="No size given.")

            # create LV
            lvcreate_cmd = module.get_bin_path("lvcreate", required=True)
            cmd = [lvcreate_cmd] + test_opt + yesopt
            if snapshot is not None:
                if size:
                    cmd += ["-%s" % size_opt, "%s%s" % (size, size_unit)]
                cmd += ["-s", "-n", snapshot] + opts + ["%s/%s" % (vg, lv)]
            elif thinpool:
                if lv:
                    if size_opt == 'l':
                        module.fail_json(changed=False, msg="Thin volume sizing with percentage not supported.")
                    size_opt = 'V'
                    cmd += ["-n", lv]
                cmd += ["-%s" % size_opt, "%s%s" % (size, size_unit)]
                cmd += opts + ["-T", "%s/%s" % (vg, thinpool)]
            else:
                cmd += ["-n", lv]
                cmd += ["-%s" % size_opt, "%s%s" % (size, size_unit)]
                cmd += opts + [vg] + pvs
            rc, dummy, err = module.run_command(cmd)
            if rc == 0:
                changed = True
            else:
                module.fail_json(msg="Creating logical volume '%s' failed" % lv, rc=rc, err=err)
    else:
        if state == 'absent':
            # remove LV
            if not force:
                module.fail_json(msg="Sorry, no removal of logical volume %s without force=true." % (this_lv['name']))
            lvremove_cmd = module.get_bin_path("lvremove", required=True)
            rc, dummy, err = module.run_command([lvremove_cmd] + test_opt + ["--force", "%s/%s" % (vg, this_lv['name'])])
            if rc == 0:
                module.exit_json(changed=True)
            else:
                module.fail_json(msg="Failed to remove logical volume %s" % (lv), rc=rc, err=err)

        elif not size:
            pass

        elif size_opt == 'l':
            # Resize LV based on % value
            tool = None
            size_free = this_vg['free']
            if size_whole == 'VG' or size_whole == 'PVS':
                size_requested = size_percent * this_vg['size'] / 100
            else:  # size_whole == 'FREE':
                size_requested = size_percent * this_vg['free'] / 100

            if size_operator == '+':
                size_requested += this_lv['size']
            elif size_operator == '-':
                size_requested = this_lv['size'] - size_requested

            # According to latest documentation (LVM2-2.03.11) all tools round down
            size_requested -= (size_requested % this_vg['ext_size'])

            if this_lv['size'] < size_requested:
                if (size_free > 0) and (size_free >= (size_requested - this_lv['size'])):
                    tool = [module.get_bin_path("lvextend", required=True)]
                else:
                    module.fail_json(
                        msg="Logical Volume %s could not be extended. Not enough free space left (%s%s required / %s%s available)" %
                            (this_lv['name'], (size_requested - this_lv['size']), unit, size_free, unit)
                    )
            elif shrink and this_lv['size'] > size_requested + this_vg['ext_size']:  # more than an extent too large
                if size_requested < 1:
                    module.fail_json(msg="Sorry, no shrinking of %s to 0 permitted." % (this_lv['name']))
                elif not force:
                    module.fail_json(msg="Sorry, no shrinking of %s without force=true" % (this_lv['name']))
                else:
                    tool = [module.get_bin_path("lvreduce", required=True), '--force']

            if tool:
                if resizefs:
                    tool += ['--resizefs']
                cmd = tool + test_opt
                if size_operator:
                    cmd += ["-%s" % size_opt, "%s%s%s" % (size_operator, size, size_unit)]
                else:
                    cmd += ["-%s" % size_opt, "%s%s" % (size, size_unit)]
                cmd += ["%s/%s" % (vg, this_lv['name'])] + pvs
                rc, out, err = module.run_command(cmd)
                if "Reached maximum COW size" in out:
                    module.fail_json(msg="Unable to resize %s to %s%s" % (lv, size, size_unit), rc=rc, err=err, out=out)
                elif rc == 0:
                    changed = True
                    msg = "Volume %s resized to %s%s" % (this_lv['name'], size_requested, unit)
                elif "matches existing size" in err or "matches existing size" in out:
                    module.exit_json(changed=False, vg=vg, lv=this_lv['name'], size=this_lv['size'])
                elif "not larger than existing size" in err or "not larger than existing size" in out:
                    module.exit_json(changed=False, vg=vg, lv=this_lv['name'], size=this_lv['size'], msg="Original size is larger than requested size", err=err)
                else:
                    module.fail_json(msg="Unable to resize %s to %s%s" % (lv, size, size_unit), rc=rc, err=err)

        else:
            # resize LV based on absolute values
            tool = None
            if float(size) > this_lv['size'] or size_operator == '+':
                tool = [module.get_bin_path("lvextend", required=True)]
            elif shrink and float(size) < this_lv['size'] or size_operator == '-':
                if float(size) == 0:
                    module.fail_json(msg="Sorry, no shrinking of %s to 0 permitted." % (this_lv['name']))
                if not force:
                    module.fail_json(msg="Sorry, no shrinking of %s without force=true." % (this_lv['name']))
                else:
                    tool = [module.get_bin_path("lvreduce", required=True), '--force']

            if tool:
                if resizefs:
                    tool += ['--resizefs']
                cmd = tool + test_opt
                if size_operator:
                    cmd += ["-%s" % size_opt, "%s%s%s" % (size_operator, size, size_unit)]
                else:
                    cmd += ["-%s" % size_opt, "%s%s" % (size, size_unit)]
                cmd += ["%s/%s" % (vg, this_lv['name'])] + pvs
                rc, out, err = module.run_command(cmd)
                if "Reached maximum COW size" in out:
                    module.fail_json(msg="Unable to resize %s to %s%s" % (lv, size, size_unit), rc=rc, err=err, out=out)
                elif rc == 0:
                    changed = True
                elif "matches existing size" in err or "matches existing size" in out:
                    module.exit_json(changed=False, vg=vg, lv=this_lv['name'], size=this_lv['size'])
                elif "not larger than existing size" in err or "not larger than existing size" in out:
                    module.exit_json(changed=False, vg=vg, lv=this_lv['name'], size=this_lv['size'], msg="Original size is larger than requested size", err=err)
                else:
                    module.fail_json(msg="Unable to resize %s to %s%s" % (lv, size, size_unit), rc=rc, err=err)

    if this_lv is not None:
        if active:
            lvchange_cmd = module.get_bin_path("lvchange", required=True)
            rc, dummy, err = module.run_command([lvchange_cmd, "-ay", "%s/%s" % (vg, this_lv['name'])])
            if rc == 0:
                module.exit_json(changed=((not this_lv['active']) or changed), vg=vg, lv=this_lv['name'], size=this_lv['size'])
            else:
                module.fail_json(msg="Failed to activate logical volume %s" % (lv), rc=rc, err=err)
        else:
            lvchange_cmd = module.get_bin_path("lvchange", required=True)
            rc, dummy, err = module.run_command([lvchange_cmd, "-an", "%s/%s" % (vg, this_lv['name'])])
            if rc == 0:
                module.exit_json(changed=(this_lv['active'] or changed), vg=vg, lv=this_lv['name'], size=this_lv['size'])
            else:
                module.fail_json(msg="Failed to deactivate logical volume %s" % (lv), rc=rc, err=err)

    module.exit_json(changed=changed, msg=msg)


if __name__ == '__main__':
    main()

#!/usr/bin/python

# Copyright (c) 2021, quidame <quidame@poivron.org>
# Copyright (c) 2013, Alexander Bulimov <lazywolf0@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
author:
  - Alexander Bulimov (@abulimov)
  - quidame (@quidame)
module: filesystem
short_description: Makes a filesystem
description:
  - This module creates a filesystem.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - If O(state=present), the filesystem is created if it does not already exist, that is the default behaviour if O(state)
        is omitted.
      - If O(state=absent), filesystem signatures on O(dev) are wiped if it contains a filesystem (as known by C(blkid)).
      - When O(state=absent), all other options but O(dev) are ignored, and the module does not fail if the device O(dev)
        does not actually exist.
    type: str
    choices: [present, absent]
    default: present
    version_added: 1.3.0
  fstype:
    choices: [bcachefs, btrfs, ext2, ext3, ext4, ext4dev, f2fs, lvm, ocfs2, reiserfs, xfs, vfat, swap, ufs]
    description:
      - Filesystem type to be created. This option is required with O(state=present) (or if O(state) is omitted).
      - V(ufs) support has been added in community.general 3.4.0.
      - V(bcachefs) support has been added in community.general 8.6.0.
    type: str
    aliases: [type]
  dev:
    description:
      - Target path to block device (Linux) or character device (FreeBSD) or regular file (both).
      - When setting Linux-specific filesystem types on FreeBSD, this module only works when applying to regular files, also known as
        disk images.
      - Currently V(lvm) (Linux-only) and V(ufs) (FreeBSD-only) do not support a regular file as their target O(dev).
      - Support for character devices on FreeBSD has been added in community.general 3.4.0.
    type: path
    required: true
    aliases: [device]
  force:
    description:
      - If V(true), allows to create new filesystem on devices that already has filesystem.
    type: bool
    default: false
  resizefs:
    description:
      - If V(true), if the block device and filesystem size differ, grow the filesystem into the space.
      - >-
        Supported when O(fstype) is one of: V(bcachefs), V(btrfs), V(ext2), V(ext3), V(ext4), V(ext4dev), V(f2fs), V(lvm), V(xfs), V(ufs) and V(vfat).
        Attempts to resize other filesystem types fail.
      - XFS only grows if mounted. Currently, the module is based on commands from C(util-linux) package to perform operations,
        so resizing of XFS is not supported on FreeBSD systems.
      - VFAT is likely to fail if C(fatresize < 1.04).
      - Mutually exclusive with O(uuid).
    type: bool
    default: false
  opts:
    description:
      - List of options to be passed to C(mkfs) command.
    type: str
  uuid:
    description:
      - Set filesystem's UUID to the given value.
      - The UUID options specified in O(opts) take precedence over this value.
      - See xfs_admin(8) (C(xfs)), tune2fs(8) (C(ext2), C(ext3), C(ext4), C(ext4dev)) for possible values.
      - For O(fstype=lvm) the value is ignored, it resets the PV UUID if set.
      - Supported for O(fstype) being one of V(bcachefs), V(ext2), V(ext3), V(ext4), V(ext4dev), V(lvm), or V(xfs).
      - This is B(not idempotent). Specifying this option always results in a change.
      - Mutually exclusive with O(resizefs).
    type: str
    version_added: 7.1.0
requirements:
  - Uses specific tools related to the O(fstype) for creating or resizing a filesystem (from packages e2fsprogs, xfsprogs,
    dosfstools, and so on).
  - Uses generic tools mostly related to the Operating System (Linux or FreeBSD) or available on both, as C(blkid).
  - On FreeBSD, either C(util-linux) or C(e2fsprogs) package is required.
notes:
  - Potential filesystems on O(dev) are checked using C(blkid). In case C(blkid) is unable to detect a filesystem (and in
    case C(fstyp) on FreeBSD is also unable to detect a filesystem), this filesystem is overwritten even if O(force=false).
  - On FreeBSD systems, both C(e2fsprogs) and C(util-linux) packages provide a C(blkid) command that is compatible with this
    module. However, these packages conflict with each other, and only the C(util-linux) package provides the command required
    to not fail when O(state=absent).
seealso:
  - module: community.general.filesize
  - module: ansible.posix.mount
  - name: xfs_admin(8) manpage for Linux
    description: Manual page of the GNU/Linux's xfs_admin implementation.
    link: https://man7.org/linux/man-pages/man8/xfs_admin.8.html
  - name: tune2fs(8) manpage for Linux
    description: Manual page of the GNU/Linux's tune2fs implementation.
    link: https://man7.org/linux/man-pages/man8/tune2fs.8.html
"""

EXAMPLES = r"""
- name: Create a ext2 filesystem on /dev/sdb1
  community.general.filesystem:
    fstype: ext2
    dev: /dev/sdb1

- name: Create a ext4 filesystem on /dev/sdb1 and check disk blocks
  community.general.filesystem:
    fstype: ext4
    dev: /dev/sdb1
    opts: -cc

- name: Blank filesystem signature on /dev/sdb1
  community.general.filesystem:
    dev: /dev/sdb1
    state: absent

- name: Create a filesystem on top of a regular file
  community.general.filesystem:
    dev: /path/to/disk.img
    fstype: vfat

- name: Reset an xfs filesystem UUID on /dev/sdb1
  community.general.filesystem:
    fstype: xfs
    dev: /dev/sdb1
    uuid: generate

- name: Reset an ext4 filesystem UUID on /dev/sdb1
  community.general.filesystem:
    fstype: ext4
    dev: /dev/sdb1
    uuid: random

- name: Reset an LVM filesystem (PV) UUID on /dev/sdc
  community.general.filesystem:
    fstype: lvm
    dev: /dev/sdc
    uuid: random
"""

import os
import platform
import re
import stat

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


class Device:
    def __init__(self, module, path):
        self.module = module
        self.path = path

    def size(self):
        """Return size in bytes of device. Returns int"""
        statinfo = os.stat(self.path)
        if stat.S_ISBLK(statinfo.st_mode):
            blockdev_cmd = self.module.get_bin_path("blockdev", required=True)
            dummy, out, dummy = self.module.run_command([blockdev_cmd, "--getsize64", self.path], check_rc=True)
            devsize_in_bytes = int(out)
        elif stat.S_ISCHR(statinfo.st_mode) and platform.system() == "FreeBSD":
            diskinfo_cmd = self.module.get_bin_path("diskinfo", required=True)
            dummy, out, dummy = self.module.run_command([diskinfo_cmd, self.path], check_rc=True)
            devsize_in_bytes = int(out.split()[2])
        elif os.path.isfile(self.path):
            devsize_in_bytes = os.path.getsize(self.path)
        else:
            self.module.fail_json(changed=False, msg=f"Target device not supported: {self}")

        return devsize_in_bytes

    def get_mountpoint(self):
        """Return (first) mountpoint of device. Returns None when not mounted."""
        cmd_findmnt = self.module.get_bin_path("findmnt", required=True)

        # find mountpoint
        rc, mountpoint, dummy = self.module.run_command(
            [cmd_findmnt, "--mtab", "--noheadings", "--output", "TARGET", "--source", self.path], check_rc=False
        )
        if rc != 0:
            mountpoint = None
        else:
            mountpoint = mountpoint.split("\n")[0]

        return mountpoint

    def __str__(self):
        return self.path


class Filesystem:
    MKFS: str | None = None
    MKFS_FORCE_FLAGS: list[str] | None = []
    MKFS_SET_UUID_OPTIONS: list[str] | None = None
    MKFS_SET_UUID_EXTRA_OPTIONS: list[str] | None = []
    INFO: str | None = None
    GROW: str | None = None
    GROW_SLACK: int = 0
    GROW_MAX_SPACE_FLAGS: list[str] | None = []
    GROW_MOUNTPOINT_ONLY = False
    CHANGE_UUID: str | None = None
    CHANGE_UUID_OPTION: str | None = None
    CHANGE_UUID_OPTION_HAS_ARG = True

    LANG_ENV = {"LANG": "C", "LC_ALL": "C", "LC_MESSAGES": "C"}

    def __init__(self, module):
        self.module = module

    @property
    def fstype(self):
        return type(self).__name__

    def get_fs_size(self, dev):
        """Return size in bytes of filesystem on device (integer).
        Should query the info with a per-fstype command that can access the
        device whenever it is mounted or not, and parse the command output.
        Parser must ensure to return an integer, or raise a ValueError.
        """
        raise NotImplementedError()

    def create(self, opts, dev, uuid=None):
        if self.module.check_mode:
            return

        if uuid and self.MKFS_SET_UUID_OPTIONS:
            if not (set(self.MKFS_SET_UUID_OPTIONS) & set(opts)):
                opts += [self.MKFS_SET_UUID_OPTIONS[0], uuid] + self.MKFS_SET_UUID_EXTRA_OPTIONS

        mkfs = self.module.get_bin_path(self.MKFS, required=True)
        cmd = [mkfs] + self.MKFS_FORCE_FLAGS + opts + [str(dev)]
        self.module.run_command(cmd, check_rc=True)
        if uuid and self.CHANGE_UUID and self.MKFS_SET_UUID_OPTIONS is None:
            self.change_uuid(new_uuid=uuid, dev=dev)

    def wipefs(self, dev):
        if self.module.check_mode:
            return

        # wipefs comes with util-linux package (as 'blockdev' & 'findmnt' above)
        # that is ported to FreeBSD. The use of dd as a portable fallback is
        # not doable here if it needs get_mountpoint() (to prevent corruption of
        # a mounted filesystem), since 'findmnt' is not available on FreeBSD,
        # even in util-linux port for this OS.
        wipefs = self.module.get_bin_path("wipefs", required=True)
        cmd = [wipefs, "--all", str(dev)]
        self.module.run_command(cmd, check_rc=True)

    def grow_cmd(self, target):
        """Build and return the resizefs commandline as list."""
        cmdline = [self.module.get_bin_path(self.GROW, required=True)]
        cmdline += self.GROW_MAX_SPACE_FLAGS + [target]
        return cmdline

    def grow(self, dev):
        """Get dev and fs size and compare. Returns stdout of used command."""
        devsize_in_bytes = dev.size()

        try:
            fssize_in_bytes = self.get_fs_size(dev)
        except NotImplementedError:
            self.module.fail_json(msg=f"module does not support resizing {self.fstype} filesystem yet")
        except ValueError as err:
            self.module.warn(f"unable to process {self.INFO} output '{err}'")
            self.module.fail_json(msg=f"unable to process {self.INFO} output for {dev}")

        if fssize_in_bytes + self.GROW_SLACK >= devsize_in_bytes:
            self.module.exit_json(changed=False, msg=f"{self.fstype} filesystem is using the whole device {dev}")
        elif self.module.check_mode:
            self.module.exit_json(changed=True, msg=f"resizing filesystem {self.fstype} on device {dev}")

        if self.GROW_MOUNTPOINT_ONLY:
            mountpoint = dev.get_mountpoint()
            if not mountpoint:
                self.module.fail_json(msg=f"{dev} needs to be mounted for {self.fstype} operations")
            grow_target = mountpoint
        else:
            grow_target = str(dev)

        dummy, out, dummy = self.module.run_command(self.grow_cmd(grow_target), check_rc=True)
        return out

    def change_uuid_cmd(self, new_uuid, target):
        """Build and return the UUID change command line as list."""
        cmdline = [self.module.get_bin_path(self.CHANGE_UUID, required=True)]
        if self.CHANGE_UUID_OPTION_HAS_ARG:
            cmdline += [self.CHANGE_UUID_OPTION, new_uuid, target]
        else:
            cmdline += [self.CHANGE_UUID_OPTION, target]
        return cmdline

    def change_uuid(self, new_uuid, dev):
        """Change filesystem UUID. Returns stdout of used command"""
        if self.module.check_mode:
            self.module.exit_json(change=True, msg=f"Changing {self.fstype} filesystem UUID on device {dev}")

        dummy, out, dummy = self.module.run_command(
            self.change_uuid_cmd(new_uuid=new_uuid, target=str(dev)), check_rc=True
        )
        return out


class Ext(Filesystem):
    MKFS_FORCE_FLAGS = ["-F"]
    MKFS_SET_UUID_OPTIONS = ["-U"]
    INFO = "tune2fs"
    GROW = "resize2fs"
    CHANGE_UUID = "tune2fs"
    CHANGE_UUID_OPTION = "-U"

    def get_fs_size(self, dev):
        """Get Block count and Block size and return their product."""
        cmd = self.module.get_bin_path(self.INFO, required=True)
        dummy, out, dummy = self.module.run_command([cmd, "-l", str(dev)], check_rc=True, environ_update=self.LANG_ENV)

        block_count = block_size = None
        for line in out.splitlines():
            if "Block count:" in line:
                block_count = int(line.split(":")[1].strip())
            elif "Block size:" in line:
                block_size = int(line.split(":")[1].strip())
            if None not in (block_size, block_count):
                break
        else:
            raise ValueError(repr(out))

        return block_size * block_count


class Ext2(Ext):
    MKFS = "mkfs.ext2"


class Ext3(Ext):
    MKFS = "mkfs.ext3"


class Ext4(Ext):
    MKFS = "mkfs.ext4"


class XFS(Filesystem):
    MKFS = "mkfs.xfs"
    MKFS_FORCE_FLAGS = ["-f"]
    INFO = "xfs_info"
    GROW = "xfs_growfs"
    # XFS (defaults with 4KiB blocksize) requires at least 64 block of free
    # space to add a new allocation group, avoid resizing (noop, but shown as
    # diff) if the difference between the filesystem and the device is less
    GROW_SLACK = 64 * 4096 - 1
    GROW_MOUNTPOINT_ONLY = True
    CHANGE_UUID = "xfs_admin"
    CHANGE_UUID_OPTION = "-U"

    def get_fs_size(self, dev):
        """Get bsize and blocks and return their product."""
        cmdline = [self.module.get_bin_path(self.INFO, required=True)]

        # Depending on the versions, xfs_info is able to get info from the
        # device, whenever it is mounted or not, or only if unmounted, or
        # only if mounted, or not at all. For any version until now, it is
        # able to query info from the mountpoint. So try it first, and use
        # device as the last resort: it may or may not work.
        mountpoint = dev.get_mountpoint()
        if mountpoint:
            cmdline += [mountpoint]
        else:
            cmdline += [str(dev)]
        dummy, out, dummy = self.module.run_command(cmdline, check_rc=True, environ_update=self.LANG_ENV)

        block_size = block_count = None
        for line in out.splitlines():
            col = line.split("=")
            if col[0].strip() == "data":
                if col[1].strip() == "bsize":
                    block_size = int(col[2].split()[0])
                if col[2].split()[1] == "blocks":
                    block_count = int(col[3].split(",")[0])
            if None not in (block_size, block_count):
                break
        else:
            raise ValueError(repr(out))

        return block_size * block_count


class Reiserfs(Filesystem):
    MKFS = "mkfs.reiserfs"
    MKFS_FORCE_FLAGS = ["-q"]


class Bcachefs(Filesystem):
    MKFS = "mkfs.bcachefs"
    MKFS_FORCE_FLAGS = ["--force"]
    MKFS_SET_UUID_OPTIONS = ["-U", "--uuid"]
    INFO = "bcachefs"
    GROW = "bcachefs"
    GROW_MAX_SPACE_FLAGS = ["device", "resize"]

    def get_fs_size(self, dev):
        """Return size in bytes of filesystem on device (integer)."""
        dummy, stdout, dummy = self.module.run_command(
            [self.module.get_bin_path(self.INFO), "show-super", str(dev)], check_rc=True
        )

        for line in stdout.splitlines():
            if "Size: " in line:
                parts = line.split()
                unit = parts[2]

                base = None
                exp = None

                units_2 = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
                units_10 = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

                try:
                    exp = units_2.index(unit)
                    base = 1024
                except ValueError:
                    exp = units_10.index(unit)
                    base = 1000

                if exp == 0:
                    value = int(parts[1])
                else:
                    value = float(parts[1])

                if base is not None and exp is not None:
                    return int(value * pow(base, exp))

        raise ValueError(repr(stdout))


class Btrfs(Filesystem):
    MKFS = "mkfs.btrfs"
    INFO = "btrfs"
    GROW = "btrfs"
    GROW_MAX_SPACE_FLAGS = ["filesystem", "resize", "max"]
    GROW_MOUNTPOINT_ONLY = True

    def __init__(self, module):
        super().__init__(module)
        mkfs = self.module.get_bin_path(self.MKFS, required=True)
        dummy, stdout, stderr = self.module.run_command([mkfs, "--version"], check_rc=True)
        match = re.search(r" v([0-9.]+)", stdout)
        if not match:
            # v0.20-rc1 use stderr
            match = re.search(r" v([0-9.]+)", stderr)
        if match:
            # v0.20-rc1 doesn't have --force parameter added in following version v3.12
            if LooseVersion(match.group(1)) >= LooseVersion("3.12"):
                self.MKFS_FORCE_FLAGS = ["-f"]
        else:
            # assume version is greater or equal to 3.12
            self.MKFS_FORCE_FLAGS = ["-f"]
            self.module.warn(f"Unable to identify mkfs.btrfs version ({stdout!r}, {stderr!r})")

    def get_fs_size(self, dev):
        """Return size in bytes of filesystem on device (integer)."""
        mountpoint = dev.get_mountpoint()
        if not mountpoint:
            self.module.fail_json(msg=f"{dev} needs to be mounted for {self.fstype} operations")

        dummy, stdout, dummy = self.module.run_command(
            [self.module.get_bin_path(self.INFO), "filesystem", "usage", "-b", mountpoint], check_rc=True
        )
        for line in stdout.splitlines():
            if "Device size" in line:
                return int(line.split()[-1])
        raise ValueError(repr(stdout))


class Ocfs2(Filesystem):
    MKFS = "mkfs.ocfs2"
    MKFS_FORCE_FLAGS = ["-Fx"]


class F2fs(Filesystem):
    MKFS = "mkfs.f2fs"
    INFO = "dump.f2fs"
    GROW = "resize.f2fs"

    def __init__(self, module):
        super().__init__(module)
        mkfs = self.module.get_bin_path(self.MKFS, required=True)
        dummy, out, dummy = self.module.run_command([mkfs, os.devnull], check_rc=False, environ_update=self.LANG_ENV)
        # Looking for "	F2FS-tools: mkfs.f2fs Ver: 1.10.0 (2018-01-30)"
        # mkfs.f2fs displays version since v1.2.0
        match = re.search(r"F2FS-tools: mkfs.f2fs Ver: ([0-9.]+) \(", out)
        if match is not None:
            # Since 1.9.0, mkfs.f2fs check overwrite before make filesystem
            # before that version -f switch wasn't used
            if LooseVersion(match.group(1)) >= LooseVersion("1.9.0"):
                self.MKFS_FORCE_FLAGS = ["-f"]

    def get_fs_size(self, dev):
        """Get sector size and total FS sectors and return their product."""
        cmd = self.module.get_bin_path(self.INFO, required=True)
        dummy, out, dummy = self.module.run_command([cmd, str(dev)], check_rc=True, environ_update=self.LANG_ENV)
        sector_size = sector_count = None
        for line in out.splitlines():
            if "Info: sector size = " in line:
                # expected: 'Info: sector size = 512'
                sector_size = int(line.split()[4])
            elif "Info: total FS sectors = " in line:
                # expected: 'Info: total FS sectors = 102400 (50 MB)'
                sector_count = int(line.split()[5])
            if None not in (sector_size, sector_count):
                break
        else:
            raise ValueError(repr(out))

        return sector_size * sector_count


class VFAT(Filesystem):
    INFO = "fatresize"
    GROW = "fatresize"
    GROW_MAX_SPACE_FLAGS = ["-s", "max"]

    def __init__(self, module):
        super().__init__(module)
        if platform.system() == "FreeBSD":
            self.MKFS = "newfs_msdos"
        else:
            self.MKFS = "mkfs.vfat"

    def get_fs_size(self, dev):
        """Get and return size of filesystem, in bytes."""
        cmd = self.module.get_bin_path(self.INFO, required=True)
        dummy, out, dummy = self.module.run_command(
            [cmd, "--info", str(dev)], check_rc=True, environ_update=self.LANG_ENV
        )
        fssize = None
        for line in out.splitlines()[1:]:
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
            param, value = parts
            if param.strip() in ("Size", "Cur size"):
                fssize = int(value.strip())
                break
        else:
            raise ValueError(repr(out))

        return fssize


class LVM(Filesystem):
    MKFS = "pvcreate"
    MKFS_FORCE_FLAGS = ["-f"]
    MKFS_SET_UUID_OPTIONS = ["-u", "--uuid"]
    MKFS_SET_UUID_EXTRA_OPTIONS = ["--norestorefile"]
    INFO = "pvs"
    GROW = "pvresize"
    CHANGE_UUID = "pvchange"
    CHANGE_UUID_OPTION = "-u"
    CHANGE_UUID_OPTION_HAS_ARG = False

    def get_fs_size(self, dev):
        """Get and return PV size, in bytes."""
        cmd = self.module.get_bin_path(self.INFO, required=True)
        dummy, size, dummy = self.module.run_command(
            [cmd, "--noheadings", "-o", "pv_size", "--units", "b", "--nosuffix", str(dev)], check_rc=True
        )
        pv_size = int(size)
        return pv_size


class Swap(Filesystem):
    MKFS = "mkswap"
    MKFS_FORCE_FLAGS = ["-f"]


class UFS(Filesystem):
    MKFS = "newfs"
    INFO = "dumpfs"
    GROW = "growfs"
    GROW_MAX_SPACE_FLAGS = ["-y"]

    def get_fs_size(self, dev):
        """Get providersize and fragment size and return their product."""
        cmd = self.module.get_bin_path(self.INFO, required=True)
        dummy, out, dummy = self.module.run_command([cmd, str(dev)], check_rc=True, environ_update=self.LANG_ENV)

        fragmentsize = providersize = None
        for line in out.splitlines():
            if line.startswith("fsize"):
                fragmentsize = int(line.split()[1])
            elif "providersize" in line:
                providersize = int(line.split()[-1])
            if None not in (fragmentsize, providersize):
                break
        else:
            raise ValueError(repr(out))

        return fragmentsize * providersize


FILESYSTEMS = {
    "bcachefs": Bcachefs,
    "ext2": Ext2,
    "ext3": Ext3,
    "ext4": Ext4,
    "ext4dev": Ext4,
    "f2fs": F2fs,
    "reiserfs": Reiserfs,
    "xfs": XFS,
    "btrfs": Btrfs,
    "vfat": VFAT,
    "ocfs2": Ocfs2,
    "LVM2_member": LVM,
    "swap": Swap,
    "ufs": UFS,
}


def main():
    friendly_names = {
        "lvm": "LVM2_member",
    }

    fstypes = set(FILESYSTEMS.keys()) - set(friendly_names.values()) | set(friendly_names.keys())

    # There is no "single command" to manipulate filesystems, so we map them all out and their options
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            fstype=dict(type="str", aliases=["type"], choices=list(fstypes)),
            dev=dict(type="path", required=True, aliases=["device"]),
            opts=dict(type="str"),
            force=dict(type="bool", default=False),
            resizefs=dict(type="bool", default=False),
            uuid=dict(type="str"),
        ),
        required_if=[("state", "present", ["fstype"])],
        mutually_exclusive=[
            ("resizefs", "uuid"),
        ],
        supports_check_mode=True,
    )

    state = module.params["state"]
    dev = module.params["dev"]
    fstype = module.params["fstype"]
    opts = module.params["opts"]
    force = module.params["force"]
    resizefs = module.params["resizefs"]
    uuid = module.params["uuid"]

    mkfs_opts = []
    if opts is not None:
        mkfs_opts = opts.split()

    changed = False

    if not os.path.exists(dev):
        msg = f"Device {dev} not found."
        if state == "present":
            module.fail_json(msg=msg)
        else:
            module.exit_json(msg=msg)

    dev = Device(module, dev)

    # In case blkid/fstyp isn't able to identify an existing filesystem, device
    # is considered as empty, then this existing filesystem would be overwritten
    # even if force isn't enabled.
    cmd = module.get_bin_path("blkid", required=True)
    rc, raw_fs, err = module.run_command([cmd, "-c", os.devnull, "-o", "value", "-s", "TYPE", str(dev)])
    fs = raw_fs.strip()
    if not fs and platform.system() == "FreeBSD":
        cmd = module.get_bin_path("fstyp", required=True)
        rc, raw_fs, err = module.run_command([cmd, str(dev)])
        fs = raw_fs.strip()

    if state == "present":
        if fstype in friendly_names:
            fstype = friendly_names[fstype]

        try:
            klass = FILESYSTEMS[fstype]
        except KeyError:
            module.fail_json(changed=False, msg=f"module does not support this filesystem ({fstype}) yet.")

        filesystem = klass(module)

        if uuid and not (filesystem.CHANGE_UUID or filesystem.MKFS_SET_UUID_OPTIONS):
            module.fail_json(
                changed=False, msg=f"module does not support UUID option for this filesystem ({fstype}) yet."
            )

        same_fs = fs and FILESYSTEMS.get(fs) == FILESYSTEMS[fstype]
        if same_fs and not resizefs and not uuid and not force:
            module.exit_json(changed=False)
        elif same_fs:
            if resizefs:
                if not filesystem.GROW:
                    module.fail_json(changed=False, msg=f"module does not support resizing {fstype} filesystem yet.")

                out = filesystem.grow(dev)

                module.exit_json(changed=True, msg=out)
            elif uuid:
                out = filesystem.change_uuid(new_uuid=uuid, dev=dev)

                module.exit_json(changed=True, msg=out)
        elif fs and not force:
            module.fail_json(msg=f"'{dev}' is already used as {fs}, use force=true to overwrite", rc=rc, err=err)

        # create fs
        filesystem.create(opts=mkfs_opts, dev=dev, uuid=uuid)
        changed = True

    elif fs:
        # wipe fs signatures
        filesystem = Filesystem(module)
        filesystem.wipefs(dev)
        changed = True

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()

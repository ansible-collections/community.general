#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: filesize

short_description: Create a file with a given size, or resize it if it exists

description:
  - This module is a simple wrapper around C(dd) to create, extend or truncate
    a file, given its size. It can be used to manage swap files (that require
    contiguous blocks) or alternatively, huge sparse files.

author:
  - quidame (@quidame)

version_added: "3.0.0"

options:
  path:
    description:
      - Path of the regular file to create or resize.
    type: path
    required: true
  size:
    description:
      - Requested size of the file.
      - The value is a number (either C(int) or C(float)) optionally followed
        by a multiplicative suffix, that can be one of C(B) (bytes), C(KB) or
        C(kB) (= 1000B), C(MB) or C(mB) (= 1000kB), C(GB) or C(gB) (= 1000MB),
        and so on for C(T), C(P), C(E), C(Z) and C(Y); or alternatively one of
        C(K), C(k) or C(KiB) (= 1024B); C(M), C(m) or C(MiB) (= 1024KiB);
        C(G), C(g) or C(GiB) (= 1024MiB); and so on.
      - If the multiplicative suffix is not provided, the value is treated as
        an integer number of blocks of I(blocksize) bytes each (float values
        are rounded to the closest integer).
      - When the I(size) value is equal to the current file size, does nothing.
      - When the I(size) value is bigger than the current file size, bytes from
        I(source) (if I(sparse) is not C(false)) are appended to the file
        without truncating it, in other words, without modifying the existing
        bytes of the file.
      - When the I(size) value is smaller than the current file size, it is
        truncated to the requested value without modifying bytes before this
        value.
      - That means that a file of any arbitrary size can be grown to any other
        arbitrary size, and then resized down to its initial size without
        modifying its initial content.
    type: raw
    required: true
  blocksize:
    description:
      - Size of blocks, in bytes if not followed by a multiplicative suffix.
      - The numeric value (before the unit) C(MUST) be an integer (or a C(float)
        if it equals an integer).
      - If not set, the size of blocks is guessed from the OS and commonly
        results in C(512) or C(4096) bytes, that is used internally by the
        module or when I(size) has no unit.
    type: raw
  source:
    description:
      - Device or file that provides input data to provision the file.
      - This parameter is ignored when I(sparse=true).
    type: path
    default: /dev/zero
  force:
    description:
      - Whether or not to overwrite the file if it exists, in other words, to
        truncate it from 0. When C(true), the module is not idempotent, that
        means it always reports I(changed=true).
      - I(force=true) and I(sparse=true) are mutually exclusive.
    type: bool
    default: false
  sparse:
    description:
      - Whether or not the file to create should be a sparse file.
      - This option is effective only on newly created files, or when growing a
        file, only for the bytes to append.
      - This option is not supported on OSes or filesystems not supporting sparse files.
      - I(force=true) and I(sparse=true) are mutually exclusive.
    type: bool
    default: false
  unsafe_writes:
    description:
      - This option is silently ignored. This module always modifies file
        size in-place.

notes:
  - This module supports C(check_mode) and C(diff).

requirements:
  - dd (Data Duplicator) in PATH

extends_documentation_fragment:
  - ansible.builtin.files

seealso:
  - name: dd(1) manpage for Linux
    description: Manual page of the GNU/Linux's dd implementation (from GNU coreutils).
    link: https://man7.org/linux/man-pages/man1/dd.1.html

  - name: dd(1) manpage for IBM AIX
    description: Manual page of the IBM AIX's dd implementation.
    link: https://www.ibm.com/support/knowledgecenter/ssw_aix_72/d_commands/dd.html

  - name: dd(1) manpage for Mac OSX
    description: Manual page of the Mac OSX's dd implementation.
    link: https://www.unix.com/man-page/osx/1/dd/

  - name: dd(1M) manpage for Solaris
    description: Manual page of the Oracle Solaris's dd implementation.
    link: https://docs.oracle.com/cd/E36784_01/html/E36871/dd-1m.html

  - name: dd(1) manpage for FreeBSD
    description: Manual page of the FreeBSD's dd implementation.
    link: https://www.freebsd.org/cgi/man.cgi?dd(1)

  - name: dd(1) manpage for OpenBSD
    description: Manual page of the OpenBSD's dd implementation.
    link: https://man.openbsd.org/dd

  - name: dd(1) manpage for NetBSD
    description: Manual page of the NetBSD's dd implementation.
    link: https://man.netbsd.org/dd.1

  - name: busybox(1) manpage for Linux
    description: Manual page of the GNU/Linux's busybox, that provides its own dd implementation.
    link: https://www.unix.com/man-page/linux/1/busybox
'''

EXAMPLES = r'''
- name: Create a file of 1G filled with null bytes
  community.general.filesize:
    path: /var/bigfile
    size: 1G

- name: Extend the file to 2G (2*1024^3)
  community.general.filesize:
    path: /var/bigfile
    size: 2G

- name: Reduce the file to 2GB (2*1000^3)
  community.general.filesize:
    path: /var/bigfile
    size: 2GB

- name: Fill a file with random bytes for backing a LUKS device
  community.general.filesize:
    path: ~/diskimage.luks
    size: 512.0 MiB
    source: /dev/urandom

- name: Take a backup of MBR boot code into a file, overwriting it if it exists
  community.general.filesize:
    path: /media/sdb1/mbr.bin
    size: 440B
    source: /dev/sda
    force: true

- name: Create/resize a sparse file of/to 8TB
  community.general.filesize:
    path: /var/local/sparsefile
    size: 8TB
    sparse: true

- name: Create a file with specific size and attributes, to be used as swap space
  community.general.filesize:
    path: /var/swapfile
    size: 2G
    blocksize: 512B
    mode: u=rw,go=
    owner: root
    group: root
'''

RETURN = r'''
cmd:
  description: Command executed to create or resize the file.
  type: str
  returned: when changed or failed
  sample: /usr/bin/dd if=/dev/zero of=/var/swapfile bs=1048576 seek=3072 count=1024

filesize:
  description: Dictionary of sizes related to the file.
  type: dict
  returned: always
  contains:
    blocks:
      description: Number of blocks in the file.
      type: int
      sample: 500
    blocksize:
      description: Size of the blocks in bytes.
      type: int
      sample: 1024
    bytes:
      description: Size of the file, in bytes, as the product of C(blocks) and C(blocksize).
      type: int
      sample: 512000
    iec:
      description: Size of the file, in human-readable format, following IEC standard.
      type: str
      sample: 500.0 KiB
    si:
      description: Size of the file, in human-readable format, following SI standard.
      type: str
      sample: 512.0 kB

size_diff:
  description: Difference (positive or negative) between old size and new size, in bytes.
  type: int
  sample: -1234567890
  returned: always

path:
  description: Realpath of the file if it is a symlink, otherwise the same than module's param.
  type: str
  sample: /var/swap0
  returned: always
'''


import re
import os
import math

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


# These are the multiplicative suffixes understood (or returned) by dd and
# others (ls, df, lvresize, lsblk...).
SIZE_UNITS = dict(
    B=1,
    kB=1000**1, KB=1000**1, KiB=1024**1, K=1024**1, k=1024**1,
    MB=1000**2, mB=1000**2, MiB=1024**2, M=1024**2, m=1024**2,
    GB=1000**3, gB=1000**3, GiB=1024**3, G=1024**3, g=1024**3,
    TB=1000**4, tB=1000**4, TiB=1024**4, T=1024**4, t=1024**4,
    PB=1000**5, pB=1000**5, PiB=1024**5, P=1024**5, p=1024**5,
    EB=1000**6, eB=1000**6, EiB=1024**6, E=1024**6, e=1024**6,
    ZB=1000**7, zB=1000**7, ZiB=1024**7, Z=1024**7, z=1024**7,
    YB=1000**8, yB=1000**8, YiB=1024**8, Y=1024**8, y=1024**8,
)


def bytes_to_human(size, iec=False):
    """Return human-readable size (with SI or IEC suffix) from bytes. This is
       only to populate the returned result of the module, not to handle the
       file itself (we only rely on bytes for that).
    """
    unit = 'B'
    for (u, v) in SIZE_UNITS.items():
        if size < v:
            continue
        if iec:
            if 'i' not in u or size / v >= 1024:
                continue
        else:
            if v % 5 or size / v >= 1000:
                continue
        unit = u

    hsize = round(size / SIZE_UNITS[unit], 2)
    if unit == 'B':
        hsize = int(hsize)

    unit = re.sub(r'^(.)', lambda m: m.expand(r'\1').upper(), unit)
    if unit == 'KB':
        unit = 'kB'

    return '%s %s' % (str(hsize), unit)


def smart_blocksize(size, unit, product, bsize):
    """Ensure the total size can be written as blocks*blocksize, with blocks
       and blocksize being integers.
    """
    if not product % bsize:
        return bsize

    # Basically, for a file of 8kB (=8000B), system's block size of 4096 bytes
    # is not usable. The smallest integer number of kB to work with 512B blocks
    # is 64, the nexts are 128, 192, 256, and so on.

    unit_size = SIZE_UNITS[unit]

    if size == int(size):
        if unit_size > SIZE_UNITS['MiB']:
            if unit_size % 5:
                return SIZE_UNITS['MiB']
            return SIZE_UNITS['MB']
        return unit_size

    if unit == 'B':
        raise AssertionError("byte is the smallest unit and requires an integer value")

    if 0 < product < bsize:
        return product

    for bsz in (1024, 1000, 512, 256, 128, 100, 64, 32, 16, 10, 8, 4, 2):
        if not product % bsz:
            return bsz
    return 1


def split_size_unit(string, isint=False):
    """Split a string between the size value (int or float) and the unit.
       Support optional space(s) between the numeric value and the unit.
    """
    unit = re.sub(r'(\d|\.)', r'', string).strip()
    value = float(re.sub(r'%s' % unit, r'', string).strip())
    if isint and unit in ('B', ''):
        if int(value) != value:
            raise AssertionError("invalid blocksize value: bytes require an integer value")

    if not unit:
        unit = None
        product = int(round(value))
    else:
        if unit not in SIZE_UNITS.keys():
            raise AssertionError("invalid size unit (%s): unit must be one of %s, or none." %
                                 (unit, ', '.join(sorted(SIZE_UNITS, key=SIZE_UNITS.get))))
        product = int(round(value * SIZE_UNITS[unit]))
    return value, unit, product


def size_string(value):
    """Convert a raw value to a string, but only if it is an integer, a float
       or a string itself.
    """
    if not isinstance(value, (int, float, str)):
        raise AssertionError("invalid value type (%s): size must be integer, float or string" % type(value))
    return str(value)


def size_spec(args):
    """Return a dictionary with size specifications, especially the size in
       bytes (after rounding it to an integer number of blocks).
    """
    blocksize_in_bytes = split_size_unit(args['blocksize'], True)[2]
    if blocksize_in_bytes == 0:
        raise AssertionError("block size cannot be equal to zero")

    size_value, size_unit, size_result = split_size_unit(args['size'])
    if not size_unit:
        blocks = int(math.ceil(size_value))
    else:
        blocksize_in_bytes = smart_blocksize(size_value, size_unit, size_result, blocksize_in_bytes)
        blocks = int(math.ceil(size_result / blocksize_in_bytes))

    args['size_diff'] = round_bytes = int(blocks * blocksize_in_bytes)
    args['size_spec'] = dict(blocks=blocks, blocksize=blocksize_in_bytes, bytes=round_bytes,
                             iec=bytes_to_human(round_bytes, True),
                             si=bytes_to_human(round_bytes))
    return args['size_spec']


def current_size(args):
    """Return the size of the file at the given location if it exists, or None."""
    path = args['path']
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise AssertionError("%s exists but is not a regular file" % path)
        args['file_size'] = os.stat(path).st_size
    else:
        args['file_size'] = None
    return args['file_size']


def complete_dd_cmdline(args, dd_cmd):
    """Compute dd options to grow or truncate a file."""
    if args['file_size'] == args['size_spec']['bytes'] and not args['force']:
        # Nothing to do.
        return list()

    bs = args['size_spec']['blocksize']

    # For sparse files (create, truncate, grow): write count=0 block.
    if args['sparse']:
        seek = args['size_spec']['blocks']
    elif args['force'] or not os.path.exists(args['path']):     # Create file
        seek = 0
    elif args['size_diff'] < 0:                                 # Truncate file
        seek = args['size_spec']['blocks']
    elif args['size_diff'] % bs:                                # Grow file
        seek = int(args['file_size'] / bs) + 1
    else:
        seek = int(args['file_size'] / bs)

    count = args['size_spec']['blocks'] - seek
    dd_cmd += ['bs=%s' % str(bs), 'seek=%s' % str(seek), 'count=%s' % str(count)]

    return dd_cmd


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            size=dict(type='raw', required=True),
            blocksize=dict(type='raw'),
            source=dict(type='path', default='/dev/zero'),
            sparse=dict(type='bool', default=False),
            force=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
        add_file_common_args=True,
    )
    args = dict(**module.params)
    diff = dict(before=dict(), after=dict())

    if args['sparse'] and args['force']:
        module.fail_json(msg='parameters values are mutually exclusive: force=true|sparse=true')
    if not os.path.exists(os.path.dirname(args['path'])):
        module.fail_json(msg='parent directory of the file must exist prior to run this module')
    if not args['blocksize']:
        args['blocksize'] = str(os.statvfs(os.path.dirname(args['path'])).f_frsize)

    try:
        args['size'] = size_string(args['size'])
        args['blocksize'] = size_string(args['blocksize'])
        initial_filesize = current_size(args)
        size_descriptors = size_spec(args)
    except AssertionError as err:
        module.fail_json(msg=to_native(err))

    expected_filesize = size_descriptors['bytes']
    if initial_filesize:
        args['size_diff'] = expected_filesize - initial_filesize
    diff['after']['size'] = expected_filesize
    diff['before']['size'] = initial_filesize

    result = dict(
        changed=args['force'],
        size_diff=args['size_diff'],
        path=args['path'],
        filesize=size_descriptors)

    dd_bin = module.get_bin_path('dd', True)
    dd_cmd = [dd_bin, 'if=%s' % args['source'], 'of=%s' % args['path']]

    if expected_filesize != initial_filesize or args['force']:
        result['cmd'] = ' '.join(complete_dd_cmdline(args, dd_cmd))
        if module.check_mode:
            result['changed'] = True
        else:
            result['rc'], dummy, result['stderr'] = module.run_command(dd_cmd)

            diff['after']['size'] = result_filesize = result['size_diff'] = current_size(args)
            if initial_filesize:
                result['size_diff'] = result_filesize - initial_filesize
            if not args['force']:
                result['changed'] = result_filesize != initial_filesize

            if result['rc']:
                msg = "dd error while creating file %s with size %s from source %s: see stderr for details" % (
                    args['path'], args['size'], args['source'])
                module.fail_json(msg=msg, **result)
            if result_filesize != expected_filesize:
                msg = "module error while creating file %s with size %s from source %s: file is %s bytes long" % (
                    args['path'], args['size'], args['source'], result_filesize)
                module.fail_json(msg=msg, **result)

    # dd follows symlinks, and so does this module, while file module doesn't.
    # If we call it, this is to manage file's mode, owner and so on, not the
    # symlink's ones.
    file_params = dict(**module.params)
    if os.path.islink(args['path']):
        file_params['path'] = result['path'] = os.path.realpath(args['path'])

    if args['file_size'] is not None:
        file_args = module.load_file_common_arguments(file_params)
        result['changed'] = module.set_fs_attributes_if_different(file_args, result['changed'], diff=diff)
    result['diff'] = diff

    module.exit_json(**result)


if __name__ == '__main__':
    main()

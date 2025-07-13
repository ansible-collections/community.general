#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Stanislav Shamilov <shamilovstas@protonmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: decompress
short_description: Decompresses compressed files
version_added: 10.1.0
description:
  - Decompresses compressed files.
  - The source (compressed) file and destination (decompressed) files are on the remote host.
  - Source file can be deleted after decompression.
extends_documentation_fragment:
  - ansible.builtin.files
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  src:
    description:
      - Remote absolute path for the file to decompress.
    type: path
    required: true
  dest:
    description:
      - The file name of the destination file where the compressed file is decompressed.
      - If the destination file exists, it is truncated and overwritten.
      - If not specified, the destination filename is derived from O(src) by removing the compression format extension. For
        example, when O(src) is V(/path/to/file.txt.gz) and O(format) is V(gz), O(dest) is V(/path/to/file.txt). If the O(src)
        file does not have an extension for the current O(format), the O(dest) filename is made by appending C(_decompressed)
        to the O(src) filename. For instance, when O(src) is V(/path/to/file.myextension), the (dest) filename is V(/path/to/file.myextension_decompressed).
    type: path
  format:
    description:
      - The type of compression to use to decompress.
    type: str
    choices: [gz, bz2, xz]
    default: gz
  remove:
    description:
      - Remove original compressed file after decompression.
    type: bool
    default: false
requirements:
  - Requires C(lzma) (standard library of Python 3) or L(backports.lzma, https://pypi.org/project/backports.lzma/) (Python
    2) if using C(xz) format.
author:
  - Stanislav Shamilov (@shamilovstas)
"""

EXAMPLES = r"""
- name: Decompress file /path/to/file.txt.gz into /path/to/file.txt (gz compression is used by default)
  community.general.decompress:
    src: /path/to/file.txt.gz
    dest: /path/to/file.txt

- name: Decompress file /path/to/file.txt.gz into /path/to/file.txt
  community.general.decompress:
    src: /path/to/file.txt.gz

- name: Decompress file compressed with bzip2
  community.general.decompress:
    src: /path/to/file.txt.bz2
    dest: /path/to/file.bz2
    format: bz2

- name: Decompress file and delete the compressed file afterwards
  community.general.decompress:
    src: /path/to/file.txt.gz
    dest: /path/to/file.txt
    remove: true
"""

RETURN = r"""
dest:
  description: Path to decompressed file.
  type: str
  returned: success
  sample: /path/to/file.txt
"""

import bz2
import filecmp
import gzip
import os
import shutil
import tempfile

from ansible.module_utils import six
from ansible_collections.community.general.plugins.module_utils.mh.module_helper import ModuleHelper
from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("lzma"):
    if six.PY3:
        import lzma
    else:
        from backports import lzma


def lzma_decompress(src):
    return lzma.open(src, "rb")


def bz2_decompress(src):
    if six.PY3:
        return bz2.open(src, "rb")
    else:
        return bz2.BZ2File(src, "rb")


def gzip_decompress(src):
    return gzip.open(src, "rb")


def decompress(b_src, b_dest, handler):
    with handler(b_src) as src_file:
        with open(b_dest, "wb") as dest_file:
            shutil.copyfileobj(src_file, dest_file)


class Decompress(ModuleHelper):
    destination_filename_template = "%s_decompressed"
    output_params = 'dest'

    module = dict(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path'),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz']),
            remove=dict(type='bool', default=False)
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )

    def __init_module__(self):
        self.handlers = {"gz": gzip_decompress, "bz2": bz2_decompress, "xz": lzma_decompress}
        if self.vars.dest is None:
            self.vars.dest = self.get_destination_filename()
        deps.validate(self.module)
        self.configure()

    def configure(self):
        b_dest = to_bytes(self.vars.dest, errors='surrogate_or_strict')
        b_src = to_bytes(self.vars.src, errors='surrogate_or_strict')
        if not os.path.exists(b_src):
            if self.vars.remove and os.path.exists(b_dest):
                self.module.exit_json(changed=False)
            else:
                self.do_raise(msg="Path does not exist: '%s'" % b_src)
        if os.path.isdir(b_src):
            self.do_raise(msg="Cannot decompress directory '%s'" % b_src)
        if os.path.isdir(b_dest):
            self.do_raise(msg="Destination is a directory, cannot decompress: '%s'" % b_dest)

    def __run__(self):
        b_dest = to_bytes(self.vars.dest, errors='surrogate_or_strict')
        b_src = to_bytes(self.vars.src, errors='surrogate_or_strict')

        file_args = self.module.load_file_common_arguments(self.module.params, path=self.vars.dest)
        handler = self.handlers[self.vars.format]
        try:
            tempfd, temppath = tempfile.mkstemp(dir=self.module.tmpdir)
            self.module.add_cleanup_file(temppath)
            b_temppath = to_bytes(temppath, errors='surrogate_or_strict')
            decompress(b_src, b_temppath, handler)
        except OSError as e:
            self.do_raise(msg="Unable to create temporary file '%s'" % to_native(e))

        if os.path.exists(b_dest):
            self.changed = not filecmp.cmp(b_temppath, b_dest, shallow=False)
        else:
            self.changed = True

        if self.changed and not self.module.check_mode:
            try:
                self.module.atomic_move(b_temppath, b_dest)
            except OSError:
                self.do_raise(msg="Unable to move temporary file '%s' to '%s'" % (b_temppath, self.vars.dest))

        if self.vars.remove and not self.check_mode:
            os.remove(b_src)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    def get_destination_filename(self):
        src = self.vars.src
        fmt_extension = ".%s" % self.vars.format
        if src.endswith(fmt_extension) and len(src) > len(fmt_extension):
            filename = src[:-len(fmt_extension)]
        else:
            filename = Decompress.destination_filename_template % src
        return filename


def main():
    Decompress.execute()


if __name__ == '__main__':
    main()

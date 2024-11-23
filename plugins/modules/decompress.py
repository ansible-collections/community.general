#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Stanislav Shamilov <shamilovstas@protonmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
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
      - The file name of the destination file where the compressed file will be decompressed.
      - If the destination file exists, it will be truncated and overwritten.
      - If not specified, the destination filename will be derived from O(src) by removing the compression format
        extension. For example, if O(src) is V(/path/to/file.txt.gz) and O(format) is V(gz), O(dest) will be
        V(/path/to/file.txt). If the O(src) file does not have an extension for the current O(format), the O(dest)
        filename will be made by appending C(_decompressed) to the O(src) filename. For instance, if O(src) is
        V(/path/to/file.myextension), the (dest) filename will be V(/path/to/file.myextension_decompressed).
    type: path
  format:
    description:
      - The type of compression to use to decompress.
    type: str
    choices: [ gz, bz2, xz ]
    default: gz
  remove:
    description:
      - Remove original compressed file after decompression.
    type: bool
    default: false
requirements:
    - Requires C(lzma) (standard library of Python 3) or L(backports.lzma, https://pypi.org/project/backports.lzma/) (Python 2) if using C(xz) format.
author:
  - Stanislav Shamilov (@shamilovstas)
'''

EXAMPLES = r'''
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
'''

RETURN = r'''
dest:
  description: Path to decompressed file
  type: str
  returned: success
  sample: /path/to/file.txt
'''

import bz2
import filecmp
import gzip
import os
import shutil
import tempfile

from traceback import format_exc
from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

LZMA_IMP_ERR = None
if six.PY3:
    try:
        import lzma

        HAS_LZMA = True
    except ImportError:
        LZMA_IMP_ERR = format_exc()
        HAS_LZMA = False
else:
    try:
        from backports import lzma

        HAS_LZMA = True
    except ImportError:
        LZMA_IMP_ERR = format_exc()
        HAS_LZMA = False


def lzma_decompress(src):
    return lzma.open(src, "rb")


def bz2_decompress(src):
    return bz2.open(src, "rb")


def gzip_decompress(src):
    return gzip.open(src, "rb")


def decompress(src, dest, handler):
    b_src = to_native(src, errors='surrogate_or_strict')
    b_dest = to_native(dest, errors='surrogate_or_strict')
    with handler(b_src) as src_file:
        with open(b_dest, "wb") as dest_file:
            shutil.copyfileobj(src_file, dest_file)


class Decompress(object):
    destination_filename_template = "%s_decompressed"

    def __init__(self, module):
        self.src = module.params['src']
        self.fmt = module.params['format']
        self.remove = module.params['remove']
        self.check_mode = module.check_mode
        self.module = module
        self.changed = False
        self.handlers = {"gz": gzip_decompress, "bz2": bz2_decompress, "xz": lzma_decompress}

        dest = module.params['dest']
        if dest is None:
            self.dest = self.get_destination_filename()
        else:
            self.dest = dest
        self.b_dest = to_native(self.dest, errors='surrogate_or_strict')
        self.b_src = to_native(self.src, errors='surrogate_or_strict')

    def configure(self):
        if not os.path.exists(self.b_src):
            self.module.fail_json(msg="Path does not exist: '%s'" % self.b_src)
        if os.path.isdir(self.b_src):
            self.module.fail_json(msg="Cannot decompress directory '%s'" % self.b_src)
        if os.path.exists(self.b_src) and os.path.isdir(self.b_src):
            self.module.fail_json(msg="Destination is a directory, cannot decompress: '%s'" % self.b_src)
        self.fmt = self.module.params['format']
        if self.fmt not in self.handlers:
            self.module.fail_json(msg="Could not decompress '%s' format" % self.fmt)

    def run(self):
        self.configure()
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.dest)
        handler = self.handlers[self.fmt]
        try:
            tempfd, temppath = tempfile.mkstemp(dir=self.module.tmpdir)
            b_temppath = to_native(temppath, errors='surrogate_or_strict')
            decompress(self.b_src, b_temppath, handler)
        except OSError as e:
            self.module.fail_json(msg="Unable to create temporary file '%s'" % to_native(e))

        if os.path.exists(self.b_dest):
            self.changed = not filecmp.cmp(b_temppath, self.b_dest, shallow=False)
        else:
            self.changed = True

        if self.changed and not self.module.check_mode:
            try:
                self.module.atomic_move(b_temppath, self.b_dest)
            except OSError:
                self.module.fail_json(msg="Unable to move temporary file '%s' to '%s'" % (b_temppath, self.dest))

        if os.path.exists(b_temppath):
            os.unlink(b_temppath)
        if self.remove and not self.check_mode:
            os.remove(self.b_src)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    def get_destination_filename(self):
        src = self.src
        fmt_extension = ".%s" % self.fmt
        if src.endswith(fmt_extension) and len(src) > len(fmt_extension):
            filename = src[:-len(fmt_extension)]
        else:
            filename = Decompress.destination_filename_template % src
        return filename


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True),
            dest=dict(type='path'),
            format=dict(type='str', default='gz', choices=['gz', 'bz2', 'xz']),
            remove=dict(type='bool', default=False)
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )
    if not HAS_LZMA and module.params['format'] == 'xz':
        module.fail_json(
            msg=missing_required_lib("lzma or backports.lzma", reason="when using xz format"), exception=LZMA_IMP_ERR
        )

    d = Decompress(module)
    d.run()

    module.exit_json(changed=d.changed, dest=d.dest)


if __name__ == '__main__':
    main()

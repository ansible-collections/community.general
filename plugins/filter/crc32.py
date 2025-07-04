# -*- coding: utf-8 -*-
# Copyright (c) 2022, Julien Riou <julien@riou.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.common.collections import is_string

try:
    from zlib import crc32
    HAS_ZLIB = True
except ImportError:
    HAS_ZLIB = False


DOCUMENTATION = r"""
name: crc32
short_description: Generate a CRC32 checksum
version_added: 5.4.0
description:
  - Checksum a string using CRC32 algorithm and return its hexadecimal representation.
options:
  _input:
    description:
      - The string to checksum.
    type: string
    required: true
author:
  - Julien Riou
"""

EXAMPLES = r"""
- name: Checksum a test string
  ansible.builtin.debug:
    msg: "{{ 'test' | community.general.crc32 }}"
"""

RETURN = r"""
_value:
  description: CRC32 checksum.
  type: string
"""


def crc32s(value):
    if not is_string(value):
        raise AnsibleFilterError('Invalid value type (%s) for crc32 (%r)' %
                                 (type(value), value))

    if not HAS_ZLIB:
        raise AnsibleFilterError('Failed to import zlib module')

    data = to_bytes(value, errors='surrogate_or_strict')
    return "{0:x}".format(crc32(data) & 0xffffffff)


class FilterModule:
    def filters(self):
        return {
            'crc32': crc32s,
        }

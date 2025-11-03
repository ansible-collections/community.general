# Copyright (c) Max Gautier <mg@max.gautier.name>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = r"""
name: accumulate
short_description: Produce a list of accumulated sums of the input list contents
version_added: 10.1.0
author: Max Gautier (@VannTen)
description:
  - Passthrough to the L(Python itertools.accumulate function,https://docs.python.org/3/library/itertools.html#itertools.accumulate).
  - Transforms an input list into the cumulative list of results from applying addition to the elements of the input list.
  - Addition means the default Python implementation of C(+) for input list elements type.
options:
  _input:
    description: A list.
    type: list
    elements: any
    required: true
"""

RETURN = r"""
_value:
  description: A list of cumulated sums of the elements of the input list.
  type: list
  elements: any
"""

EXAMPLES = r"""
- name: Enumerate parent directories of some path
  ansible.builtin.debug:
    var: >
      "/some/path/to/my/file"
      | split('/') | map('split', '/')
      | community.general.accumulate | map('join', '/')
    # Produces: ['', '/some', '/some/path', '/some/path/to', '/some/path/to/my', '/some/path/to/my/file']

- name: Growing string
  ansible.builtin.debug:
    var: "'abc' | community.general.accumulate"
    # Produces ['a', 'ab', 'abc']
"""

from itertools import accumulate
from collections.abc import Sequence

from ansible.errors import AnsibleFilterError


def list_accumulate(sequence):
    if not isinstance(sequence, Sequence):
        raise AnsibleFilterError(f"Invalid value type ({type(sequence)}) for accumulate ({sequence!r})")

    return accumulate(sequence)


class FilterModule:
    def filters(self):
        return {
            "accumulate": list_accumulate,
        }

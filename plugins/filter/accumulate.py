# Copyright (c) Max Gautier <mg@max.gautier.name>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = '''
  name: accumulate
  short_description: Produce a list of accumulated sums of the input list contents.
  version_added: 10.0.0
  author: Max Gautier (@VannTen)
  description:
    - Passthrough to L(python itertools.accumulate function,https://docs.python.org/3/library/itertools.html#itertools.accumulate).
    - Transforms an input list into the cumulative list of results from applying addition to the elements of the input list.
    - Addition means the default python implementation of '+' for input list elements type.
  options:
    _input:
      description: A list
      type: list
      elements: any
      required: true
'''

RETURN = '''
  _value:
    description: A list of cumulated sums of the elements of the input list
    type: list
'''

EXAMPLES = '''
- name: Enumerate parent directories of some path
  ansible.builtin.debug:
    var: >
       "/some/path/to/my/file"
       | split('/') | map('split', '/')
       | community.general.enumerate | map('join', '/')
    # Produces: ['', '/some', '/some/path', '/some/path/to', '/some/path/to/my', '/some/path/to/my/file']
'''

from itertools import accumulate


def list_accumulate(sequence):
    return accumulate(sequence)


class FilterModule(object):

    def filters(self):
        return {
            'accumulate': list_accumulate,
        }

# -*- coding: utf-8 -*-
# Copyright (c) 2020-2024, Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: lists_mergeby
short_description: Merge two or more lists of dictionaries by a given attribute
version_added: 2.0.0
author: Vladimir Botka (@vbotka)
description:
  - Merge two or more lists by attribute O(index). Optional parameters O(recursive) and O(list_merge) control the merging
    of the nested dictionaries and lists.
  - The function C(merge_hash) from C(ansible.utils.vars) is used.
  - To learn details on how to use the parameters O(recursive) and O(list_merge) see Ansible User's Guide chapter "Using filters
    to manipulate data" section R(Combining hashes/dictionaries, combine_filter) or the filter P(ansible.builtin.combine#filter).
positional: another_list, index
options:
  _input:
    description:
      - A list of dictionaries, or a list of lists of dictionaries.
      - The required type of the C(elements) is set to C(raw) because all elements of O(_input) can be either dictionaries
        or lists.
    type: list
    elements: raw
    required: true
  another_list:
    description:
      - Another list of dictionaries, or a list of lists of dictionaries.
      - This parameter can be specified multiple times.
    type: list
    elements: raw
  index:
    description:
      - The dictionary key that must be present in every dictionary in every list that is used to merge the lists.
    type: string
    required: true
  recursive:
    description:
      - Should the combine recursively merge nested dictionaries (hashes).
      - B(Note:) It does not depend on the value of the C(hash_behaviour) setting in C(ansible.cfg).
    type: boolean
    default: false
  list_merge:
    description:
      - Modifies the behaviour when the dictionaries (hashes) to merge contain arrays/lists.
    type: string
    default: replace
    choices:
      - replace
      - keep
      - append
      - prepend
      - append_rp
      - prepend_rp
"""

EXAMPLES = r"""
# Some results below are manually formatted for better readability. The
# dictionaries' keys will be sorted alphabetically in real output.

- name: Example 1. Merge two lists. The results r1 and r2 are the same.
  ansible.builtin.debug:
    msg: |
      r1: {{ r1 }}
      r2: {{ r2 }}
  vars:
    list1:
      - {index: a, value: 123}
      - {index: b, value: 4}
    list2:
      - {index: a, foo: bar}
      - {index: c, foo: baz}
    r1: "{{ list1 | community.general.lists_mergeby(list2, 'index') }}"
    r2: "{{ [list1, list2] | community.general.lists_mergeby('index') }}"

#  r1:
#    - {index: a, foo: bar, value: 123}
#    - {index: b, value: 4}
#    - {index: c, foo: baz}
#  r2:
#    - {index: a, foo: bar, value: 123}
#    - {index: b, value: 4}
#    - {index: c, foo: baz}

- name: Example 2. Merge three lists
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, value: 123}
      - {index: b, value: 4}
    list2:
      - {index: a, foo: bar}
      - {index: c, foo: baz}
    list3:
      - {index: d, foo: qux}
    r: "{{ [list1, list2, list3] | community.general.lists_mergeby('index') }}"

#  r:
#    - {index: a, foo: bar, value: 123}
#    - {index: b, value: 4}
#    - {index: c, foo: baz}
#    - {index: d, foo: qux}

- name: Example 3. Merge single list. The result is the same as 2.
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, value: 123}
      - {index: b, value: 4}
      - {index: a, foo: bar}
      - {index: c, foo: baz}
      - {index: d, foo: qux}
    r: "{{ [list1, []] | community.general.lists_mergeby('index') }}"

#  r:
#    - {index: a, foo: bar, value: 123}
#    - {index: b, value: 4}
#    - {index: c, foo: baz}
#    - {index: d, foo: qux}

- name: Example 4. Merge two lists. By default, replace nested lists.
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, foo: [X1, X2]}
      - {index: b, foo: [X1, X2]}
    list2:
      - {index: a, foo: [Y1, Y2]}
      - {index: b, foo: [Y1, Y2]}
    r: "{{ [list1, list2] | community.general.lists_mergeby('index') }}"

#  r:
#    - {index: a, foo: [Y1, Y2]}
#    - {index: b, foo: [Y1, Y2]}

- name: Example 5. Merge two lists. Append nested lists.
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, foo: [X1, X2]}
      - {index: b, foo: [X1, X2]}
    list2:
      - {index: a, foo: [Y1, Y2]}
      - {index: b, foo: [Y1, Y2]}
    r: "{{ [list1, list2] | community.general.lists_mergeby('index', list_merge='append') }}"

#  r:
#    - {index: a, foo: [X1, X2, Y1, Y2]}
#    - {index: b, foo: [X1, X2, Y1, Y2]}

- name: Example 6. Merge two lists. By default, do not merge nested dictionaries.
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, foo: {x: 1, y: 2}}
      - {index: b, foo: [X1, X2]}
    list2:
      - {index: a, foo: {y: 3, z: 4}}
      - {index: b, foo: [Y1, Y2]}
    r: "{{ [list1, list2] | community.general.lists_mergeby('index') }}"

#  r:
#    - {index: a, foo: {y: 3, z: 4}}
#    - {index: b, foo: [Y1, Y2]}

- name: Example 7. Merge two lists. Merge nested dictionaries too.
  ansible.builtin.debug:
    var: r
  vars:
    list1:
      - {index: a, foo: {x: 1, y: 2}}
      - {index: b, foo: [X1, X2]}
    list2:
      - {index: a, foo: {y: 3, z: 4}}
      - {index: b, foo: [Y1, Y2]}
    r: "{{ [list1, list2] | community.general.lists_mergeby('index', recursive=true) }}"

#  r:
#    - {index: a, foo: {x:1, y: 3, z: 4}}
#    - {index: b, foo: [Y1, Y2]}
"""

RETURN = r"""
_value:
  description: The merged list.
  type: list
  elements: dictionary
"""

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.utils.vars import merge_hash

from collections import defaultdict
from operator import itemgetter


def list_mergeby(x, y, index, recursive=False, list_merge='replace'):
    '''Merge 2 lists by attribute 'index'. The function 'merge_hash'
       from ansible.utils.vars is used.  This function is used by the
       function lists_mergeby.
    '''

    d = defaultdict(dict)
    for lst in (x, y):
        for elem in lst:
            if not isinstance(elem, Mapping):
                msg = "Elements of list arguments for lists_mergeby must be dictionaries. %s is %s"
                raise AnsibleFilterError(msg % (elem, type(elem)))
            if index in elem.keys():
                d[elem[index]].update(merge_hash(d[elem[index]], elem, recursive, list_merge))
    return sorted(d.values(), key=itemgetter(index))


def lists_mergeby(*terms, **kwargs):
    '''Merge 2 or more lists by attribute 'index'. To learn details
       on how to use the parameters 'recursive' and 'list_merge' see
       the filter ansible.builtin.combine.
    '''

    recursive = kwargs.pop('recursive', False)
    list_merge = kwargs.pop('list_merge', 'replace')
    if kwargs:
        raise AnsibleFilterError("'recursive' and 'list_merge' are the only valid keyword arguments.")
    if len(terms) < 2:
        raise AnsibleFilterError("At least one list and index are needed.")

    # allow the user to do `[list1, list2, ...] | lists_mergeby('index')`
    flat_list = []
    for sublist in terms[:-1]:
        if not isinstance(sublist, Sequence):
            msg = ("All arguments before the argument index for community.general.lists_mergeby "
                   "must be lists. %s is %s")
            raise AnsibleFilterError(msg % (sublist, type(sublist)))
        if len(sublist) > 0:
            if all(isinstance(lst, Sequence) for lst in sublist):
                for item in sublist:
                    flat_list.append(item)
            else:
                flat_list.append(sublist)
    lists = flat_list

    if not lists:
        return []

    if len(lists) == 1:
        return lists[0]

    index = terms[-1]

    if not isinstance(index, string_types):
        msg = ("First argument after the lists for community.general.lists_mergeby must be string. "
               "%s is %s")
        raise AnsibleFilterError(msg % (index, type(index)))

    high_to_low_prio_list_iterator = reversed(lists)
    result = next(high_to_low_prio_list_iterator)
    for list in high_to_low_prio_list_iterator:
        result = list_mergeby(list, result, index, recursive, list_merge)

    return result


class FilterModule(object):
    ''' Ansible list filters '''

    def filters(self):
        return {
            'lists_mergeby': lists_mergeby,
        }

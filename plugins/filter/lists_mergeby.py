# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022, Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: lists_mergeby
  short_description: Merge two or more lists of dictionaries by a given attribute
  version_added: 2.0.0
  author: Vladimir Botka (@vbotka)
  description:
    - Merge two or more lists by attribute I(index). Optional parameters 'recursive' and 'list_merge'
      control the merging of the lists in values. The function merge_hash from ansible.utils.vars
      is used. To learn details on how to use the parameters 'recursive' and 'list_merge' see
      Ansible User's Guide chapter "Using filters to manipulate data" section "Combining
      hashes/dictionaries".
  positional: another_list, index
  options:
    _input:
      description: A list of dictionaries.
      type: list
      elements: dictionary
      required: true
    another_list:
      description: Another list of dictionaries. This parameter can be specified multiple times.
      type: list
      elements: dictionary
    index:
      description:
        - The dictionary key that must be present in every dictionary in every list that is used to
          merge the lists.
      type: string
      required: true
    recursive:
      description:
        - Should the combine recursively merge nested dictionaries (hashes).
        - "B(Note:) It does not depend on the value of the C(hash_behaviour) setting in C(ansible.cfg)."
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
'''

EXAMPLES = '''
- name: Merge two lists
  ansible.builtin.debug:
    msg: >-
      {{ list1 | community.general.lists_mergeby(
                    list2,
                    'index',
                    recursive=True,
                    list_merge='append'
                 ) }}"
  vars:
    list1:
      - index: a
        value: 123
      - index: b
        value: 42
    list2:
      - index: a
        foo: bar
      - index: c
        foo: baz
  # Produces the following list of dictionaries:
  #   {
  #     "index": "a",
  #     "foo": "bar",
  #     "value": 123
  #   },
  #   {
  #     "index": "b",
  #     "value": 42
  #   },
  #   {
  #     "index": "c",
  #     "foo": "baz"
  #   }
'''

RETURN = '''
  _value:
    description: The merged list.
    type: list
    elements: dictionary
'''

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.utils.vars import merge_hash
from ansible.release import __version__ as ansible_version
from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from collections import defaultdict
from operator import itemgetter


def list_mergeby(x, y, index, recursive=False, list_merge='replace'):
    ''' Merge 2 lists by attribute 'index'. The function merge_hash from ansible.utils.vars is used.
        This function is used by the function lists_mergeby.
    '''

    d = defaultdict(dict)
    for l in (x, y):
        for elem in l:
            if not isinstance(elem, Mapping):
                msg = "Elements of list arguments for lists_mergeby must be dictionaries. %s is %s"
                raise AnsibleFilterError(msg % (elem, type(elem)))
            if index in elem.keys():
                d[elem[index]].update(merge_hash(d[elem[index]], elem, recursive, list_merge))
    return sorted(d.values(), key=itemgetter(index))


def lists_mergeby(*terms, **kwargs):
    ''' Merge 2 or more lists by attribute 'index'. Optional parameters 'recursive' and 'list_merge'
        control the merging of the lists in values. The function merge_hash from ansible.utils.vars
        is used. To learn details on how to use the parameters 'recursive' and 'list_merge' see
        Ansible User's Guide chapter "Using filters to manipulate data" section "Combining
        hashes/dictionaries".

        Example:
        - debug:
            msg: "{{ list1|
                     community.general.lists_mergeby(list2,
                                                     'index',
                                                     recursive=True,
                                                     list_merge='append')|
                     list }}"
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
            if all(isinstance(l, Sequence) for l in sublist):
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

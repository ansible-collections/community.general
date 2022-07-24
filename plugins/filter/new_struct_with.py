# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
name: new_struct_with
short_description: From a data structure used to update an other, get a new
                   one.
version_added: 5.3.0
author: DEMAREST Maxime (@indelog)
description:
  - Starting from two similar data structure, first one provided by I(_input)
    and called B(base) that acting as the source of data, second provided by
    I(changes) and called B(changes) that acting as update to be applied to
    B(base), creates a new one as result.
  - Basics, this is designed to work on configurations structures provided by
    format like JSON, YAML or TOML by ensuring the presence or the absence of
    some values in keys/items to the result.
  - I(_input) and I(changes) must be both assimilable to dictionaries or lists
    and have same type (both are list or both are dictionary).
  - The update of items in B(base) with items in I(changes) is done by
    comparing the values of all keys/items in I(_input) ans I(changes) that
    have same path in the structure. If compared values in both side are
    assimilable to dictionaries, operate recursively on they.
positional: changes
options:
  _input:
    description:
      - A structure assimilable to a dictionary or a list that acts to
        source of data for the new one.
      - Its type must be a similar to I(changes) (both are lists or
        dictionaries).
      - All of its items that not be updated or removed by keys/items in
        I(changes) be present as they are in the result.
    type: raw
    required: true
extends_documentation_fragment: community.general.new_struct_with
seealso:
  - module: ansible.utils.update_fact
    description: Do something similar in another way.
 '''

EXAMPLES = r'''
- name: result with keys/items in `base` updated by theses in `changes`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=true) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AB: '9'}, B: ['8', '2'], C: '7'}
# "result": {"A": {"AA": "1", "AB": "9"}, "B": ["2", "3", "8"], "C": "7"}}

- name: result with keys/items from `base` without keys/items from `changes`
        that have same value in `base`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false) }}
  vars:
    base: {A: {AA: '1', AB: '2'}, B: ['3', '4'], C: '5'}
    changes: {A: {AA: '1'}, B: ['3', '9'], C: '8'}
# "result": {A: {AB: '2'}, B: ['4'], C: '5'}}

- name: work on lists, all items `base` and `changes` be in the result
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', 'B', {C: '1', D: '2'}, {E: '3'}, 'Z', {C: '1'}]

- name: work on lists, remove items in `changes` from `base` to get result
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false) }}"
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', {C: '1', D: '2'}]

- name: by using `list_as_dict=true`, lists act as dict, so we can recursively
        changes them
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=true,
          list_as_dict=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]

- name: by using `list_as_dict=true`, lists act as dict, with `present=false`
        we can recursively remove items in them
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false,
          list_as_dict=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['A', {C: '1'}]

- name: By default, nested lists/dictionaries that be emptied are removed
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AA: '1'}, B: ['2', '3']}
# "result": {C: '4'}

- name: If use `keep_empty=true`, nested lists/dictionaries emptied are keept
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false,
          keep_empty=true) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AA: '1'}, B: ['2', '3']}
# "result": {A: {}, B: [], C: '4'}

- name: Use `null` value to ignore some items in list to avoid updating
        them when using `dict_as_list=true`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, dict_as_list=true) }}
  vars:
    base: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    changes: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'Z', {DA: '1', DB: '2'}, 'E']

- name: Use `null` value can to ignore some items in list to avoid remove
        them when using `dict_as_list=true` and `present=false`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.new_struct_with(changes, present=false,
          dict_as_list=true) }}
  vars:
    base: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    changes: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'C', {DB: '2'}]

- name: with `remove_null=true`, you can use null value to ensure a key be
        removed not taking care about its actual value
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.intersect_data_with(changes,
          list_as_dict=true, remove_null=true) }}
  vars:
    base: {A: '1', B: '2', C: {CA: '3', CB: '4'}, D: ['DA', 'DB']}
    changes: {B: null, C: {CB: null}, D: null}
# "result": {A: '1', C: {CA: '3'}}
'''

RETURN = r'''
  _result:
    description: A new structure that contains keys/items provided in I(_input)
                 updated with keys/items provided in I(changes) depending on
                 that the used parameters.
    type: raw
'''

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible_collections.community.general.plugins.module_utils.vars import NewStructWith


def new_struct_with(base, changes, present, list_as_dict=False, keep_empty=False, remove_null=False):
    # type: (Mapping|Sequence, Mapping|Sequence, bool, bool, bool, bool) -> list|dict
    try:
        return NewStructWith(base, changes,
                             present=present,
                             list_as_dict=list_as_dict,
                             keep_empty=keep_empty,
                             remove_null=remove_null).get()
    except TypeError as e:
        raise AnsibleFilterError(e)


class FilterModule(object):
    """
    Ansible new_struct_with filter
    """

    def filters(self):
        return {
            'new_struct_with': new_struct_with,
        }

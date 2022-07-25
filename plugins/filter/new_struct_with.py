# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
name: new_struct_with
short_description: Get a new data structure data structure starting from two
                   other, one as a base and the second acting as changes.
version_added: 5.3.0
author: DEMAREST Maxime (@indelog)
description:
  - Get a new data structure starting from two similar other, one called
    B(base) provided by I(_input) that acts as data source and the second
    called C(changes) that acts to add, update or remove keys/items from
    B(base).
  - Basically, this is designed for working on configurations structures provided
    by format like JSON, YAML or TOML to ensuring the presence or the absence
    of some values in keys/items inside.
  - I(_input) and I(changes) must be both assimilable to dictionaries or lists
    and have same type (both are list or both are dictionary).
  - Updating B(base) keys/items with I(changes) keys/items is done by comparing
    their values for a same path in the structure. If the compared values are
    both assimilable to dictionaries, recursively operate on them.
positional: changes
options:
  _input:
    description:
      - A data structure assimilable to a dictionary or a list acting as data
        source to make new one.
      - Must have the same type as I(changes) (both are lists or dictionaries).
      - All of its keys/items which are not be updated or removed by keys/items
        in I(changes) will be present as they are in the result.
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
                 updated with keys/items provided in I(changes) depending to
                 used parameters.
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

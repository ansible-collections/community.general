# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
name: structure_merging
short_description: Get a new data structure by updating the one provided in
                   I(_input) with items of I(changes).
version_added: 5.3.0
author: DEMAREST Maxime (@indelog)
description:
  - Starting from two similar data structure, assimilable to lists or
    dictionaries, provided by I(_input) and I(changes), create a new one by
    updating keys/items of I(_input) by those of I(changes).
  - Items in I(changes) can be used to add or update items from I(_input) or to
    remove them.
  - Basically, this is designed for working on configurations structures provided
    by format like JSON, YAML or TOML to ensuring the presence or the absence
    of some values in keys/items inside.
  - Updating the input keys/items with those in I(changes) is done by comparing
    their values for a same path in the structure. If the compared values are
    both assimilable to dictionaries, recursively operate on them.
positional: changes
options:
  _input:
    description:
      - A data structure assimilable to a dictionary or a list which items act
        as the source of data.
      - Its type must be similar to that of I(changes) (both are lists or both
        are dictionaries).
      - All of its keys/items who not updated or removed by the merging with
        I(changes) will be kept as they are in the result.
    type: raw
    required: true
extends_documentation_fragment: community.general.structure_merging
seealso:
  - module: ansible.utils.update_fact
    description: Do something similar in another way.
 '''

EXAMPLES = r'''
- name: with `present=true`, add or update keys/items with those in `changes`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=true) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AB: '9'}, B: ['8', '2'], C: '7'}
# "result": {"A": {"AA": "1", "AB": "9"}, "B": ["2", "3", "8"], "C": "7"}}

- name: with `present=true`, remove keys/items with those in `changes`
        that have same value in `base`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false) }}
  vars:
    base: {A: {AA: '1', AB: '2'}, B: ['3', '4'], C: '5'}
    changes: {A: {AA: '1'}, B: ['3', '9'], C: '8'}
# "result": {A: {AB: '2'}, B: ['4'], C: '5'}}

- name: merge two list by ensuring that data in `changes` be present
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', 'B', {C: '1', D: '2'}, {E: '3'}, 'Z', {C: '1'}]

- name: merge two list by ensuring that data in `changes` be absent
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false) }}"
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', {C: '1', D: '2'}]

- name: add/update items in list by merging their items by index, like this,
        list acts like dict with the index number as keys
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=true,
          merge_list_by_index=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]

- name: remove items in list by merging their items by index, like this, list
        acts like dict with the index number as keys
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false,
          merge_list_by_index=true) }}
  vars:
    base: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    changes: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['A', {C: '1'}]

- name: by default, nested lists/dictionaries that be emptied are removed
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AA: '1'}, B: ['2', '3']}
# "result": {C: '4'}

- name: if use `keep_empty=true`, nested lists/dictionaries emptied are keept
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false,
          keep_empty=true) }}
  vars:
    base: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    changes: {A: {AA: '1'}, B: ['2', '3']}
# "result": {A: {}, B: [], C: '4'}

- name: use `null` value to ignore some items in list to avoid updating
        them when using `dict_as_list=true`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, dict_as_list=true) }}
  vars:
    base: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    changes: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'Z', {DA: '1', DB: '2'}, 'E']

- name: Use `null` value can to ignore some items in list to avoid remove
        them when using `dict_as_list=true` and `present=false`
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes, present=false,
          dict_as_list=true) }}
  vars:
    base: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    changes: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'C', {DB: '2'}]

- name: with `remove_null=true`, null value can be used to ensure that a key be
        removed not taking care about its actual value
  ansible.builtin.set_fact:
    result: >
      {{ base | community.general.structure_merging(changes,
          merge_list_by_index=true, remove_null=true) }}
  vars:
    base: {A: '1', B: '2', C: {CA: '3', CB: '4'}, D: ['DA', 'DB']}
    changes: {B: null, C: {CB: null}, D: null}
# "result": {A: '1', C: {CA: '3'}}
'''

RETURN = r'''
  _result:
    description: A new data structure that contains keys/items provided in
                 I(_input) updated with keys/items provided in I(changes)
                 depending to used parameters.
    type: raw
'''

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible_collections.community.general.plugins.module_utils.structure_merging import StructureMerging


def structure_merging(base, changes, present, merge_list_by_index=False, keep_empty=False, remove_null=False):
    # type: (Mapping|Sequence, Mapping|Sequence, bool, bool, bool, bool) -> list|dict
    try:
        return StructureMerging(base, changes,
                                present=present,
                                merge_seq_by_index=merge_list_by_index,
                                keep_empty=keep_empty,
                                remove_null=remove_null).get()
    except TypeError as e:
        raise AnsibleFilterError(e)


class FilterModule(object):
    """
    Ansible filter for data structure merging
    """

    def filters(self):
        return {
            'structure_merging': structure_merging,
        }

# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
name: intersect_data_with
short_description: Intersecting an original data structure with modifications
                   to create a new one.
version_added: 5.3.0
author: DEMAREST Maxime (@indelog)
description:
  - Starting from two similar data structure, an original provided by I(_input)
    and modifications provided by I(modifications), creates a new one which is
    an intersection of these.
  - This is designed to easily update configurations structures provided by
    format like JSON, YAML or TOML by ensuring the presence or the absence of
    some values in keys/items to the result.
  - Original and modifications must contain items that be assimilable to
    dictionaries or lists and can themselves contains values that also be
    assimilable to a dictionary or a list.
  - Original data acts as basis for the new one.
  - Modifications are used to add, update or remove keys/items from original
    data.
  - The intersection between original and modifications is done by iterating
    over all keys/items in original and for each which is also exists in
    modification for a same path in the structure, compares their values.
  - When the compared values are in both side assimilable to dictionaries, do a
    recursive intersection.
positional: expected
options:
  _input:
    description:
      - A data structure assimilable to a dictionary or a list that acts to
        basis for the new one.
      - It must be a similar type of structure that I(modifications) (both are
        lists or dictionaries).
      - All of its items that not be updated or remove by the intersection
        with modification data be present as they are in the result.
    type: raw
    required: true
extends_documentation_fragment: community.general.data_intersection
seealso:
  - module: ansible.utils.update_fact
    description: Do something similar in another way.
 '''

EXAMPLES = r'''
- name: Update original data with modifications
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=true) }}
  vars:
    original: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    modifications: {A: {AB: '9'}, B: ['8', '2'], C: '7'}
# "result": {"A": {"AA": "1", "AB": "9"}, "B": ["2", "3", "8"], "C": "7"}}

- name: Ensure that items/values in modifications are not in result
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false) }}
  vars:
    original: {A: {AA: '1', AB: '2'}, B: ['3', '4'], C: '5'}
    modifications: {A: {AA: '1'}, B: ['3', '9'], C: '8'}
# "result": {A: {AB: '2'}, B: ['4'], C: '5'}}

- name: En:suring the presence of values in list in result
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
           modifications, present=true) }}
  vars:
    original: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    modifications: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', 'B', {C: '1', D: '2'}, {E: '3'}, 'Z', {C: '1'}]

- name: Ensuring the absence of values in list in result
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false) }}"
  vars:
    original: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    modifications: ['Z', 'B', {C: '1'}, {E: '3'}]
# "result": ['A', {C: '1', D: '2'}]

- name: Effect of using list_as_dict when intersecting list with presence of
        items in modifications
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=true, list_as_dict=true) }}
  vars:
    original: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    modifications: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]

- name: Effect of using list_as_dict when intersecting list with absence of
        items in modifications
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false, list_as_dict=true) }}
  vars:
    original: ['A', 'B', {C: '1', D: '2'}, {E: '3'}]
    modifications: ['Z', 'B', {C: '9', D: '2'}, {E: '3'}]
# "result": ['A', {C: '1'}]

- name: By default, items that be emptied after the intersection are removed
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false) }}
  vars:
    original: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    modifications: {A: {AA: '1'}, B: ['2', '3']}
# "result": {C: '4'}

- name: When using keep_empty, emptied data still be present in result
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false, keep_empty=true) }}
  vars:
    original: {A: {AA: '1'}, B: ['2', '3'], C: '4'}
    modifications: {A: {AA: '1'}, B: ['2', '3']}
# "result": {A: {}, B: [], C: '4'}

- name: Use `null` to ignore some items in list and avoid to update it by using
        list_as_dict
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, dict_as_list=true) }}
  vars:
    original: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    modifications: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'Z', {DA: '1', DB: '2'}, 'E']

- name: Use `null` to ignore some items in list and avoid to remove it by using
        list_as_dict
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, present=false, dict_as_list=true) }}
  vars:
    original: ['A', 'B', 'C', {DA: '1', DB: '2'}, 'E']
    modifications: [null, null, 'Z', {DA: '1', DB: null}, 'E']
# "result": ['A', 'B', 'C', {DB: '2'}]

- name: Use remove null to ensuring that some items are absent to the result
        regardless of their original value
  ansible.builtin.set_fact:
    result: >
      {{ original | community.general.intersect_data_with(
            modifications, list_as_dict=true, remove_null=true) }}
  vars:
    original: {A: '1', B: '2', C: {CA: '3', CB: '4'}, D: ['DA', 'DB']}
    changes: {B: null, C: {CB: null}, D: null}
# "result": {A: '1', C: {CA: '3'}}
'''

RETURN = r'''
  _result:
    description: A new data structure which is an intersection of original data
                 with modifications and which the format can be a dictionary or
                 a list depending on the format or original data.
    type: raw
'''

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible_collections.community.general.plugins.module_utils.vars import DataIntersection


def intersect_data_with(original, modifications, present, list_as_dict=False, keep_empty=False, remove_null=False):
    # type: (Mapping|Sequence, Mapping|Sequence, bool, bool, bool, bool) -> list|dict
    try:
        return DataIntersection(original, modifications,
                                present=present,
                                list_as_dict=list_as_dict,
                                keep_empty=keep_empty,
                                remove_null=remove_null).get()
    except TypeError as e:
        raise AnsibleFilterError(e)


class FilterModule(object):
    """
    Ansible b_into_a filter
    """

    def filters(self):
        return {
            'intersect_data_with': intersect_data_with,
        }

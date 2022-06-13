# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
name: merge_data
short_description: Compare one data structure with an other I(expected) and
                   ensure that these are presents or absents in the result
                   depending the I(state).
version_added: 5.2.0
author: DEMAREST Maxime (@indelog)
description:
  - Compare data structure provided in I(_input) with data structure provided
    in I(expected).
positional: expected
options:
  _input:
    description:
      - The current data structure that you want to compare with I(expected).
      - This can be one of a dictionary or a list that can contain them self
        other dictionaries and lists.
    type: raw
    required: true
extends_documentation_fragment: community.general.merge_data
 '''

EXAMPLES = r'''
- name: Ensure that the expected data will be present with lists merged by values.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='present') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
    expected:
      B: 3
      C:
        E: [7]
        F: 8
# Produce the following result :
#   "msg": {
#       "A": 1,
#       "B": 3,
#       "C": {
#           "D": 3,
#           "E": [
#               4,
#               5,
#               6,
#               7
#           ],
#           "F": 8
#       }
#   }

- name: Ensure that the expected data will be present with lists merged by index.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='present', list_diff_type='index') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
    expected:
      B: 3
      C:
        E: [null, 6]
        F: 8
# Produce the following result :
#   "msg": {
#       "A": 1,
#       "B": 3,
#       "C": {
#           "D": 3,
#           "E": [
#               4,
#               6,
#               6
#           ],
#           "F": 8
#       }
#   }

- name: Ensure that the expected data will be absent with lists merged by value.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='absent') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
        F: 8
    expected:
      A: 1
      B: 3
      C:
        E: [1, 2, 5]
        F: 8
# Produce the following result :
#   "msg": {
#       "B": 2,
#       "C": {
#           "D": 3,
#           "E": [
#               4,
#               6
#           ]
#       }
#   }

- name: Ensure that the expecte data will be absent with lists merged by index.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='absent', list_diff_type='index') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
        F: 8
    expected:
      A: 1
      B: 3
      C:
        E: [null, 5, 5]
        F: 8
# Produce the following result :
#   "msg": {
#       "B": 2,
#       "C": {
#           "D": 3,
#           "E": [
#               4,
#               6
#           ]
#       }
#   }

- name: Ensure that the result will be identic to the expected data.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='identic') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
        F: 8
    expected:
      Z: 9
      Y: 8
      X:
        W: [7, 6]
# Produce the following result :
#   "msg": {
#       "X": {
#           "W": [
#               7,
#               6
#           ]
#       },
#       "Y": 8,
#       "Z": 9
#   }

- name: With mixed data current=dict expected=list.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='present') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
        F: 8
    expected:
      Z: 9
      Y: 8
      X:
        W: [7, 6]
# Produce the following result :
#   "msg": {
#       "X": {
#           "W": [
#               7,
#               6
#           ]
#       },
#       "Y": 8,
#       "Z": 9
#   }

- name: With mixed data current=list expected=dict.
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='present') }}"
  vars:
    current:
      A: 1
      B: 2
      C:
        D: 3
        E: [4, 5, 6]
        F: 8
    expected:
      Z: 9
      Y: 8
      X:
        W: [7, 6]
# Produce the following result :
#   "msg": [
#       "A",
#       "B",
#       "C"
#   ]

- name: Ignore index with state='present'
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='present', list_diff_type='index') }}"
  vars:
    current:
      - 'A'
      - 'B'
      - 'C'
    expected:
      - null
      - 'Z'
# Produce the following result :
#   "msg": [
#       "A",
#       "Z",
#       "C"
#   ]

- name: Ignore index with state='absent'
  ansible.builtin.debug:
    msg: "{{ current|community.general.merge_data(expected, state='absent', list_diff_type='index') }}"
  vars:
    current:
      - 'A'
      - 'B'
      - 'C'
    expected:
      - null
      - 'B'
# Produce the following result :
#   "msg": [
#       "A",
#       "C"
#   ]
'''

RETURN = r'''
  _result:
    description:
      - Data structure with elements of I(expected) merged with compared data
        according to the I(state).
      - This can be a list or a dictionary depending that the type of
        I(expected).
    type: raw
'''

from ansible.errors import AnsibleFilterError
from ansible_collections.community.general.plugins.module_utils.data_merge import DataMerge


def merge_data(current, expected, *, state, list_diff_type='value'):
    # type: (list | dict, list | dict, str, str) -> list | dict
    data_merge = DataMerge(state, list_diff_type)
    try:
        return data_merge.get_new_merged_data(current, expected)
    except ValueError as e:
        raise AnsibleFilterError(e)


class FilterModule(object):
    """
    Ansible data merge filter
    """

    def filters(self):
        return {
            'merge_data': merge_data,
        }

# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
name: merge_data
short_description: Merge dict or lists by ensuring the comparing datas are
                   presents, absents or identics.
version_added: 5.0.2
author: DEMAREST Maxime (@indelog)
description:
  - Merge two datas, current and expected in form of dict or list.
  - You can have mixed data like dict->list or list->dict. If the two type
    are different, the expected datas are always returned.
  - You have 3 type of merging. You can ensure that the expected data
    will be present or absent to the result or ensure that the result is
    identical to the expected datas.
  - For the list, you have two type of diff. You can check if the expected
    datas are present in a list on the current datas or you can
    check a value at the specific index of the list.
 positional: expected, state, list_diff_type
 options:
   expected:
     type: dict|list
     required: true
      description:
        - The datas that you want to diff with the current and you need to
          ensure that are in corresponding C(state).
   state:
     type: string
     required: true
     choices:
       - present
       - absent
       - identic
      description:
        - If set to C(present), that ensure the expected values are present in
          the result. If an element of dict is absent from current data but
          present in expected it will be added in the result and if a dict
          element is is present in both current and expected, the element value
          will be set to same as in expected datas.
        - If set to C(absent), that ensure the expected values are absent in
          the result. If an element of dict is prensent in expected and
          current datas but with different value it will not be removed. It
          only be removed if the element in current and expected data share the
          same value.
        - If set to C(identic), that ensure the result is identical to the
          expected datas.
    list_diff_type:
      type: string
      required: false
      default: value
      choices:
        - value
        - index
      description:
        - This describes how the lists are compared.
        - If set to C(value), it checks if the expected value is present in the
          list. With this, you cannot do recursive check, the presence of the
          expected value is only done on the first level, but you not need to
          take care of the position of the expected data in the list.
        - If set to C(index), it checks if the expected value is present a
          specific index in the Current datas. With this, you can do
          recursive check, but you need to take care of the position of the
          expected date in the list. If you need to ignore value a previous
          position in list index when you only want operate on specific position
          set the values that you want ignore to C(null) (see examples).
 '''

EXAMPLES = '''
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

- name: Ensure that the result will be identic to the expected datas.
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

- name: With mixed datas current=dict expected=list.
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

- name: With mixed datas current=list expected=dict.
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

RETURN = '''
  _result:
    description: Merged datas.
    type: list | dict
'''

from ansible.errors import AnsibleFilterError
from ansible_collections.community.general.plugins.module_utils.data_merge import DataMerge


def merge_data(current, expected, state, list_diff_type='value'):
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

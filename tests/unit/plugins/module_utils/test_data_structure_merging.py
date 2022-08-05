# -*- coding: utf-8 -*-
# (c) 2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.data_structure_merging import DataStructureMerging

CASES_DataStructureMerging_TEST_GET_RESULT = [
    {
        'id': '00_simple_presence_of_change',
        'present': True,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'remove_null': False,
        'base': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'changes': {'A': {'AB': '9'}, 'B': ['8', '2'], 'C': '7'},
        'expected': {'A': {'AA': '1', 'AB': '9'}, 'B': ['2', '3', '8'], 'C': '7'},
    },
    {
        'id': '01_simple_absence_of_change',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'remove_null': False,
        'base': {'A': {'AA': '1', 'AB': '2'}, 'B': ['3', '4'], 'C': '5'},
        'changes': {'A': {'AA': '1'}, 'B': ['3', '9'], 'C': '8'},
        'expected': {'A': {'AB': '2'}, 'B': ['4'], 'C': '5'},
    },
    {
        'id': '10_with_merge_seq_by_index_changes_present',
        'present': True,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'changes': ['Z', 'B', {'C': '1'}, {'E': '3'}],
        'expected': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}, 'Z', {'C': '1'}],
    },
    {
        'id': '11_with_merge_seq_by_index_modif_absent',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'changes': ['Z', 'B', {'C': '1'}, {'E': '3'}],
        'expected': ['A', {'C': '1', 'D': '2'}],
    },
    {
        'id': '12_with_no_merge_seq_by_index_modif_present',
        'present': True,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'changes': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
        'expected': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
    },
    {
        'id': '13_with_no_merge_seq_by_index_modif_absent',
        'present': False,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'changes': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
        'expected': ['A', {'C': '1'}],
    },
    {
        'id': '20_without_keep_empty',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'remove_null': False,
        'base': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'changes': {'A': {'AA': '1'}, 'B': ['2', '3']},
        'expected': {'C': '4'},
    },
    {
        'id': '21_with_keep_empty',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': True,
        'remove_null': False,
        'base': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'changes': {'A': {'AA': '1'}, 'B': ['2', '3']},
        'expected': {'A': {}, 'B': [], 'C': '4'},
    },
    {
        'id': '30_ignore_none_present',
        'present': True,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E'],
        'changes': [None, None, 'Z', {'DA': '1', 'DB': None}, 'E'],
        'expected': ['A', 'B', 'Z', {'DA': '1', 'DB': '2'}, 'E'],
    },
    {
        'id': '31_ignore_none_absent',
        'present': False,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'remove_null': False,
        'base': ['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E'],
        'changes': [None, None, 'Z', {'DA': '1', 'DB': None}, 'E'],
        'expected': ['A', 'B', 'C', {'DB': '2'}],
    },
    {
        'id': '32_remove_null',
        'present': False,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'remove_null': True,
        'base': {'A': '1', 'B': '2', 'C': {'CA': '3', 'CB': '4'}, 'D': ['DA', 'DB']},
        'changes': {'B': None, 'C': {'CB': None}, 'D': None},
        'expected': {'A': '1', 'C': {'CA': '3'}},
    },
]
CASES_DataStructureMerging_TEST_GET_RESULT_IDS = [item['id'] for item in CASES_DataStructureMerging_TEST_GET_RESULT]

CASES_DataStructureMerging_TEST_ERRORS = [
    {
        'id': '00_not_same_type',
        'base': ['A'],
        'changes': {'A': '1'},
    },
    {
        'id': '10_base_is_not_assimilable_to_dict_or_list',
        'base': 1,
        'changes': {'A': '1'},
    },
    {
        'id': '11_changes_is_not_assimilable_to_dict_or_list',
        'base': {'A': '1'},
        'changes': 1,
    },
    {
        'id': '12_both_are_not_assimilable_to_dict_or_list',
        'base': 1,
        'changes': 2,
    },
    {
        'id': '030_refuse_string',
        'base': 'ABC',
        'changes': ['A', 'B', 'C'],
    },
]
CASES_DataStructureMerging_TEST_ERRORS_IDS = [item['id'] for item in CASES_DataStructureMerging_TEST_ERRORS]


@pytest.mark.parametrize('testcase', CASES_DataStructureMerging_TEST_GET_RESULT, ids=CASES_DataStructureMerging_TEST_GET_RESULT_IDS)
def test_DataStructureMerging(testcase):
    res = DataStructureMerging(testcase['base'],
                               testcase['changes'],
                               testcase['present'],
                               testcase['merge_seq_by_index'],
                               testcase['keep_empty'],
                               testcase['remove_null']).get()
    assert(res == testcase['expected'])


@pytest.mark.parametrize('testcase',
                         CASES_DataStructureMerging_TEST_ERRORS,
                         ids=CASES_DataStructureMerging_TEST_ERRORS_IDS)
def test_DataStructureMerging_error(testcase):
    with pytest.raises(TypeError):
        DataStructureMerging(testcase['base'], testcase['changes'])

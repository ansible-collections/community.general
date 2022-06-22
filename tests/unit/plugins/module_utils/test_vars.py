# -*- coding: utf-8 -*-
# (c) 2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.vars import BintoA

BintoA_LIST_A = ['A', 'B', 'C', ['DA', 'DB'], ['EA', 'EB'], 'F', ['GA', 'GB', 'GC']]

BintoA_LIST_B_TEST_NOT_MERGE_BY_INDEX = ['A', 'C', 'Z', ['DA', 'DB'], ['EA', 'EB', 'EZ'], 'X']
BintoA_LIST_RES_PRESENT_NOT_MERGE_BY_INDEX = [
    'A', 'B', 'C', [
        'DA', 'DB'], [
            'EA', 'EB'], 'F', ['GA', 'GB', 'GC'], 'Z', [
                'EA', 'EB', 'EZ'], 'X']
BintoA_LIST_RES_ABSENT_NOT_MERGE_BY_INDEX = ['B', ['EA', 'EB'], 'F', ['GA', 'GB', 'GC']]

BintoA_LIST_B_TEST_MERGE_BY_INDEX = ['A', 'Z', 'C', ['DZ'], ['EA', 'EZ', 'EX'], 'F', [None, 'GB', 'GZ']]
BintoA_LIST_RES_PRESENT_MERGE_BY_INDEX = [
    'A', 'Z', 'C', [
        'DZ', 'DB'], [
            'EA', 'EZ', 'EX'], 'F', ['GA', 'GB', 'GZ']]
BintoA_LIST_RES_ABSENT_MERGE_BY_INDEX = ['B', ['DA', 'DB'], ['EB'], ['GA', 'GC']]

# NOTE : Keep elements in this dict unsorted ('B' element is before 'A').
BintoA_DICT_A = {
    'B': '2',
    'A': '1',
    'C': {
        'CA': [
            {'A': '1', 'B': '2'},
            {'C': '3', 'D': '4'},
        ],
        'CB': '1',
        'CC': '2',
        'CD': {'DA': '1', 'DB': '2'},
    },
    'F': '4',
    'E': '3',
}

BintoA_DICT_B_TEST_PRESENT = {
    'B': '9',
    'E': '3',
    'C': {
        'CA': [
            {'A': '9', 'B': '8'},
            {'C': '3', 'D': '4'},
        ],
        'CB': '9',
        'CZ': '9',
        'CD': {'DA': '1', 'DB': '9', 'DZ': '8'},
    },
    'F': {
        'FA': '4'
    },
    'G': {
        'GA': '5',
    }
}

BintoA_DICT_B_TEST_ABSENT = {
    'A': '1',
    'C': {
        'CA': [
            {'C': '3', 'D': '4'},
            {'Z': '9', 'Y': '8'},
        ],
        'CB': 9,
        'CD': {'DA': '1', 'DB': '2'},
        'CZ': 8,
    },
    'Z': '8',
    'Y': {
        'YZ': '7',
        'YY': '6',
    },
}

BintoA_DICT_RES_PRESENT = {
    'A': '1',
    'B': '9',
    'C': {
        'CA': [
            {'A': '1', 'B': '2'},
            {'C': '3', 'D': '4'},
            {'A': '9', 'B': '8'},
        ],
        'CB': '9',
        'CZ': '9',
        'CC': '2',
        'CD': {'DA': '1', 'DB': '9', 'DZ': '8'},
    },
    'E': '3',
    'F': {
        'FA': '4'
    },
    'G': {
        'GA': '5',
    }
}

BintoA_DICT_RES_ABSENT = {
    'B': '2',
    'C': {
        'CA': [
            {'A': '1', 'B': '2'},
        ],
        'CB': '1',
        'CC': '2',
    },
    'F': '4',
    'E': '3',
}

BintoA_TEST_CASES_B_IN_A = [
    {
        'id': '010_full_list_present_no_index',
        'present': True,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'val_a': BintoA_LIST_A,
        'val_b': BintoA_LIST_B_TEST_NOT_MERGE_BY_INDEX,
        'val_res': BintoA_LIST_RES_PRESENT_NOT_MERGE_BY_INDEX,
    },
    {
        'id': '020_full_list_present_index',
        'present': True,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'val_a': BintoA_LIST_A,
        'val_b': BintoA_LIST_B_TEST_MERGE_BY_INDEX,
        'val_res': BintoA_LIST_RES_PRESENT_MERGE_BY_INDEX,
    },
    {
        'id': '030_full_list_absent_no_index',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'val_a': BintoA_LIST_A,
        'val_b': BintoA_LIST_B_TEST_NOT_MERGE_BY_INDEX,
        'val_res': BintoA_LIST_RES_ABSENT_NOT_MERGE_BY_INDEX,
    },
    {
        'id': '040_full_list_absent_index',
        'present': False,
        'merge_seq_by_index': True,
        'keep_empty': False,
        'val_a': BintoA_LIST_A,
        'val_b': BintoA_LIST_B_TEST_MERGE_BY_INDEX,
        'val_res': BintoA_LIST_RES_ABSENT_MERGE_BY_INDEX,
    },
    {
        'id': '110_full_dict_present',
        'present': True,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'val_a': BintoA_DICT_A,
        'val_b': BintoA_DICT_B_TEST_PRESENT,
        'val_res': BintoA_DICT_RES_PRESENT,
    },
    {
        'id': '120_full_dict_absent',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': False,
        'val_a': BintoA_DICT_A,
        'val_b': BintoA_DICT_B_TEST_ABSENT,
        'val_res': BintoA_DICT_RES_ABSENT,
    },
    {
        'id': '210_keep_empty',
        'present': False,
        'merge_seq_by_index': False,
        'keep_empty': True,
        'val_a': {'A': ['AA', 'BB'], 'B': {'BA': '1', 'BB': '2'}},
        'val_b': {'A': ['AA', 'BB'], 'B': {'BA': '1', 'BB': '2'}},
        'val_res': {'A': [], 'B': {}},
    },
]
BintoA_TEST_CASE_B_TO_A_IDS = [item['id'] for item in BintoA_TEST_CASES_B_IN_A]

BintoA_TEST_CASES_B_IN_A_VALUE_ERROR = [
    {
        'id': '010_not_same_type',
        'val_a': ['A'],
        'val_b': {'A': '1'},
    },
    {
        'id': '020_not_mapping_or_seq',
        'val_a': ['A'],
        'val_b': {'A': '1'},
    },
    {
        'id': '030_refuse_string',
        'val_a': 'ABC',
        'val_b': ['A', 'B', 'C'],
    },
]
BintoA_TEST_CASE_B_TO_A_VALUE_ERROR_IDS = [item['id'] for item in BintoA_TEST_CASES_B_IN_A_VALUE_ERROR]


@pytest.mark.parametrize('testcase', BintoA_TEST_CASES_B_IN_A, ids=BintoA_TEST_CASE_B_TO_A_IDS)
def test_AinB(testcase):
    res = BintoA(testcase['val_a'],
                 testcase['val_b'],
                 testcase['present'],
                 testcase['merge_seq_by_index'],
                 testcase['keep_empty']).get()
    assert(res == testcase['val_res'])


@pytest.mark.parametrize('testcase',
                         BintoA_TEST_CASES_B_IN_A_VALUE_ERROR,
                         ids=BintoA_TEST_CASE_B_TO_A_VALUE_ERROR_IDS)
def test_AinB_TypeError(testcase):
    with pytest.raises(TypeError):
        BintoA(testcase['val_a'], testcase['val_b'])

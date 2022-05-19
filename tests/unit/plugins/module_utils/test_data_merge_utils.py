# -*- coding: utf-8 -*-
# (c) 2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.data_merge_utils import DataMergeUtils

LIST_CURRENT = ['A', 'B', 'C', ['DA', 'DB'],
                ['EA', 'EB'], 'F', ['GA', 'GB', 'GC']]

LIST_MODIF_VALUE = ['A', 'C', 'Z', ['DA', 'DB'], ['EA', 'EB', 'EZ'], 'X']
LIST_EXPECTED_VALUE_PRESENT = [
    'A', 'B', 'C', [
        'DA', 'DB'], [
            'EA', 'EB'], 'F', ['GA', 'GB', 'GC'], 'Z', [
                'EA', 'EB', 'EZ'], 'X']
LIST_EXPECTED_VALUE_ABSENT = ['B', ['EA', 'EB'], 'F', ['GA', 'GB', 'GC']]

LIST_MODIF_INDEX = ['A', 'Z', 'C', ['DZ'],
                    ['EA', 'EZ', 'EX'], 'F', [None, 'GB', 'GZ']]
LIST_EXPECTED_INDEX_PRESENT = [
    'A', 'Z', 'C', [
        'DZ', 'DB'], [
            'EA', 'EZ', 'EX'], 'F', ['GA', 'GB', 'GZ']]
LIST_EXPECTED_INDEX_ABSENT = ['B', ['DA', 'DB'], ['EB'], ['GA', 'GC']]

LIST_MODIF_IDENTIC = ['Z', 'X', ['YZ', 'YX']]

# NOTE : The fact B is before A and F is before E is wanted.
#        It permit to test sort function on module that use `DataMergeUtils`.
DICT_CURRENT = {
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

DICT_MODIF = {
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

DICT_MODIF_NOT_IN_CURRENT = {
    'A': '9',
    'C': {
        'CA': [
            {'Z': '9', 'Y': '8'},
        ],
    },
    'Z': '8',
    'Y': {
        'YZ': '7',
        'YY': '6',
    },
}

DICT_EXPECTED_PRESENT = {
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

DICT_EXPECTED_ABSENT = {
    'A': '1',
    'B': '2',
    'C': {
        'CA': [
            {'A': '1', 'B': '2'},
        ],
        'CB': '1',
        'CC': '2',
        'CD': {'DB': '2'},
    },
    'F': '4',
}

DATA_MERGE_TEST_CASE_LIST = [
    {
        'id': 'value_present',
        'merge_type': 'present',
        'list_diff_type': 'value',
        'data_current': LIST_CURRENT,
        'data_modif': LIST_MODIF_VALUE,
        'data_expected': LIST_EXPECTED_VALUE_PRESENT,
    },
    {
        'id': 'value_absent',
        'merge_type': 'absent',
        'list_diff_type': 'value',
        'data_current': LIST_CURRENT,
        'data_modif': LIST_MODIF_VALUE,
        'data_expected': LIST_EXPECTED_VALUE_ABSENT,
    },
    {
        'id': 'index_present',
        'merge_type': 'present',
        'list_diff_type': 'index',
        'data_current': LIST_CURRENT,
        'data_modif': LIST_MODIF_INDEX,
        'data_expected': LIST_EXPECTED_INDEX_PRESENT,
    },
    {
        'id': 'index_absent',
        'merge_type': 'absent',
        'list_diff_type': 'index',
        'data_current': LIST_CURRENT,
        'data_modif': LIST_MODIF_INDEX,
        'data_expected': LIST_EXPECTED_INDEX_ABSENT,
    },
    {
        'id': 'identic',
        'merge_type': 'identic',
        'list_diff_type': 'value',
        'data_current': LIST_CURRENT,
        'data_modif': LIST_MODIF_IDENTIC,
        'data_expected': LIST_MODIF_IDENTIC,
    },
]
DATA_MERGE_TEST_CASE_LIST_IDS = (item['id']
                                 for item in DATA_MERGE_TEST_CASE_LIST)

DATA_MERGE_TEST_CASE_DICT = [
    {
        'id': 'present',
        'merge_type': 'present',
        'data_expected': DICT_EXPECTED_PRESENT,
    },
    {
        'id': 'absent',
        'merge_type': 'absent',
        'data_expected': DICT_EXPECTED_ABSENT,
    },
    {
        'id': 'identic',
        'merge_type': 'identic',
        'data_expected': DICT_MODIF,
    },
]
DATA_MERGE_TEST_CASE_DICT_IDS = (item['id']
                                 for item in DATA_MERGE_TEST_CASE_DICT)

DATA_MERGE_TEST_CASE_MIXED = [
    {
        'id': 'present',
        'merge_type': 'present',
        'data_expected': LIST_CURRENT,
    },
    {
        'id': 'absent',
        'merge_type': 'absent',
        'data_expected': DICT_CURRENT,
    },
]
DATA_MERGE_TEST_CASE_MIXED_IDS = (item['id']
                                  for item in DATA_MERGE_TEST_CASE_MIXED)


@pytest.mark.parametrize('testcase', DATA_MERGE_TEST_CASE_LIST,
                         ids=DATA_MERGE_TEST_CASE_LIST_IDS)
def test_merge_list(testcase):
    data_merge_utils = DataMergeUtils(merge_type=testcase['merge_type'], list_diff_type=testcase['list_diff_type'])
    list_merged = data_merge_utils.get_new_merged_list(testcase['data_current'], testcase['data_modif'])
    assert(list_merged == testcase['data_expected'])


@pytest.mark.parametrize('testcase', DATA_MERGE_TEST_CASE_DICT,
                         ids=DATA_MERGE_TEST_CASE_DICT_IDS)
def test_merge_dict(testcase):
    data_merge_utils = DataMergeUtils(merge_type=testcase['merge_type'])
    dict_merged = data_merge_utils.get_new_merged_dict(DICT_CURRENT, DICT_MODIF)
    assert(dict_merged == testcase['data_expected'])


@pytest.mark.parametrize('testcase', DATA_MERGE_TEST_CASE_MIXED,
                         ids=DATA_MERGE_TEST_CASE_MIXED_IDS)
def test_merge_mixed(testcase):
    data_merge_utils = DataMergeUtils(merge_type=testcase['merge_type'])
    list_merged = data_merge_utils.get_new_merged_data(DICT_CURRENT, LIST_CURRENT)
    assert(list_merged == testcase['data_expected'])

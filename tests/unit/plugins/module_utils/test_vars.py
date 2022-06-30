# -*- coding: utf-8 -*-
# (c) 2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.vars import DataIntersection

CASES_DataIntersection_TEST_GET_RESULT = [
    {
        'id': '00_simple_presence_of_change',
        'present': True,
        'list_to_dict': False,
        'keep_empty': False,
        'remove_null': False,
        'original': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'modifs': {'A': {'AB': '9'}, 'B': ['8', '2'], 'C': '7'},
        'expected': {'A': {'AA': '1', 'AB': '9'}, 'B': ['2', '3', '8'], 'C': '7'},
    },
    {
        'id': '01_simple_absence_of_change',
        'present': False,
        'list_to_dict': False,
        'keep_empty': False,
        'remove_null': False,
        'original': {'A': {'AA': '1', 'AB': '2'}, 'B': ['3', '4'], 'C': '5'},
        'modifs': {'A': {'AA': '1'}, 'B': ['3', '9'], 'C': '8'},
        'expected': {'A': {'AB': '2'}, 'B': ['4'], 'C': '5'},
    },
    {
        'id': '10_intersect_list_as_list_modifs_present',
        'present': True,
        'list_to_dict': False,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'modifs': ['Z', 'B', {'C': '1'}, {'E': '3'}],
        'expected': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}, 'Z', {'C': '1'}],
    },
    {
        'id': '11_intersect_list_as_list_modif_absent',
        'present': False,
        'list_to_dict': False,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'modifs': ['Z', 'B', {'C': '1'}, {'E': '3'}],
        'expected': ['A', {'C': '1', 'D': '2'}],
    },
    {
        'id': '12_intersect_list_as_dict_modif_present',
        'present': True,
        'list_to_dict': True,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'modifs': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
        'expected': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
    },
    {
        'id': '13_intersect_list_as_dict_modif_absent',
        'present': False,
        'list_to_dict': True,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}],
        'modifs': ['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}],
        'expected': ['A', {'C': '1'}],
    },
    {
        'id': '20_without_keep_empty',
        'present': False,
        'list_to_dict': False,
        'keep_empty': False,
        'remove_null': False,
        'original': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'modifs': {'A': {'AA': '1'}, 'B': ['2', '3']},
        'expected': {'C': '4'},
    },
    {
        'id': '21_with_keep_empty',
        'present': False,
        'list_to_dict': False,
        'keep_empty': True,
        'remove_null': False,
        'original': {'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'},
        'modifs': {'A': {'AA': '1'}, 'B': ['2', '3']},
        'expected': {'A': {}, 'B': [], 'C': '4'},
    },
    {
        'id': '30_ignore_none_present',
        'present': True,
        'list_to_dict': True,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E'],
        'modifs': [None, None, 'Z', {'DA': '1', 'DB': None}, 'E'],
        'expected': ['A', 'B', 'Z', {'DA': '1', 'DB': '2'}, 'E'],
    },
    {
        'id': '31_ignore_none_absent',
        'present': False,
        'list_to_dict': True,
        'keep_empty': False,
        'remove_null': False,
        'original': ['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E'],
        'modifs': [None, None, 'Z', {'DA': '1', 'DB': None}, 'E'],
        'expected': ['A', 'B', 'C', {'DB': '2'}],
    },
    {
        'id': '32_remove_null',
        'present': False,
        'list_to_dict': True,
        'keep_empty': False,
        'remove_null': True,
        'original': {'A': '1', 'B': '2', 'C': {'CA': '3', 'CB': '4'}, 'D': ['DA', 'DB']},
        'modifs': {'B': None, 'C': {'CB': None}, 'D': None},
        'expected': {'A': '1', 'C': {'CA': '3'}},
    },
]
CASES_DataIntersection_TEST_GET_RESULT_IDS = [item['id'] for item in CASES_DataIntersection_TEST_GET_RESULT]

CASES_DataIntersection_TEST_ERRORS = [
    {
        'id': '00_not_same_type',
        'original': ['A'],
        'modifs': {'A': '1'},
    },
    {
        'id': '10_original_is_not_assimilable_to_dict_or_list',
        'original': 1,
        'modifs': {'A': '1'},
    },
    {
        'id': '11_modifs_is_not_assimilable_to_dict_or_list',
        'original': {'A': '1'},
        'modifs': 1,
    },
    {
        'id': '12_both_are_not_assimilable_to_dict_or_list',
        'original': 1,
        'modifs': 2,
    },
    {
        'id': '030_refuse_string',
        'original': 'ABC',
        'modifs': ['A', 'B', 'C'],
    },
]
CASES_DataIntersection_TEST_ERRORS_IDS = [item['id'] for item in CASES_DataIntersection_TEST_ERRORS]


@pytest.mark.parametrize('testcase', CASES_DataIntersection_TEST_GET_RESULT, ids=CASES_DataIntersection_TEST_GET_RESULT_IDS)
def test_data_intersection(testcase):
    res = DataIntersection(testcase['original'],
                           testcase['modifs'],
                           testcase['present'],
                           testcase['list_to_dict'],
                           testcase['keep_empty'],
                           testcase['remove_null']).get()
    assert(res == testcase['expected'])


@pytest.mark.parametrize('testcase',
                         CASES_DataIntersection_TEST_ERRORS,
                         ids=CASES_DataIntersection_TEST_ERRORS_IDS)
def test_data_intersection_error(testcase):
    with pytest.raises(TypeError):
        DataIntersection(testcase['original'], testcase['modifs'])

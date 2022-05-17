# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy
from enum import Enum
from functools import wraps
from collections.abc import Callable
from typing import Union
from ansible_collections.community.general.plugins.module_utils.mh.deco\
    import basic_annotation_type_checking


class MergeType(Enum):
    """
    Describe the mean of merging data.

    - IDENTIC : Ensure that the result is identical to the expected data.
    - PRESENT : Ensure that an element in expected data must be present in
                the result.  If an element in expected data as different value
                or in not present in the base data, it will be set or added in
                the result.
    - ABSENT :  Ensure that an element is absent in the final result. For the
                dict, if a key is present in the current dict and in the
                expected dict but has different value, the current value will
                be kept in the result.
    """
    IDENTIC = 'identic'
    PRESENT = 'present'
    ABSENT = 'absent'


class ListDiffType(Enum):
    """
    Descibe the mean of merging data for a list.

    - VALUE :   Comparing elements in the list by their values. Search if
                an element in expect list is present or absent, depending on
                the MergType, to the current list.  If it not the case it will
                be added of removed. This not check list recursively, only the
                first level is checked.
    - INDEX :   Comparing elements in the list by their index. For
                MergeType.Persent, it will check if the value of all elements,
                in the current list as the same value as the element in the
                expected list with the same index, and if it not the case, the
                value of the element in the expected list will be set at this
                index position in the result list. For MergeType.ABSENT, it
                will check if the value of an element in the current list as
                the same value as the element with the same index in the
                expected list and if it's the case, the element will not be
                present in the result.
    """
    VALUE = 'value'
    INDEX = 'index'


class DataMergeUtils:
    """
    Utils for merging list or dict depending MergeType.
    """

    def __check_identic(func: Callable) -> Callable:
        """
        Decorator to check if MegreType.IDENTIC an if is the case return the
        "expected" data in all case.
        """
        @wraps(func)
        def wrapped(self,
                    current: Union[list, dict],
                    expected: Union[list, dict]) -> Union[list, dict]:
            if self.get_merge_type() == MergeType.IDENTIC:
                return deepcopy(expected)
            return func(self, current, expected)
        return wrapped

    @basic_annotation_type_checking
    def __init__(self, merge_type: MergeType,
                 list_diff_type: ListDiffType = ListDiffType.VALUE) -> None:
        self.__merge_type = merge_type
        self.__list_diff_type = list_diff_type

    @basic_annotation_type_checking
    def set_merge_type(self, merge_type: MergeType) -> None:
        self.__merge_type = merge_type

    def get_merge_type(self) -> MergeType:
        return self.__merge_type

    @basic_annotation_type_checking
    def set_list_diff_type(self, diff_type: ListDiffType) -> None:
        self.__list_diff_type = diff_type

    def get_list_diff_type(self) -> ListDiffType:
        return self.__list_diff_type

    @basic_annotation_type_checking
    @__check_identic
    def get_new_merged_data(self, current: Union[dict, list], expected:
                            Union[dict, list]) -> Union[dict, list]:
        """
        Getting the merge of two element if it can't be sure that they have the
        same type.
        """
        if not isinstance(current, type(expected)):
            if self.__merge_type == MergeType.PRESENT:
                return deepcopy(expected)
            if self.__merge_type == MergeType.ABSENT:
                return deepcopy(current)
            raise TypeError("Unexpected MergeType")

        if isinstance(current, list):
            return self.get_new_merged_list(current, expected)
        return self.get_new_merged_dict(current, expected)

    @basic_annotation_type_checking
    @__check_identic
    def get_new_merged_dict(self, current: dict, expected: dict) -> dict:
        """
        Getting the merge of two dict depending the MergeType.
        """
        merged = deepcopy(current)
        for key in expected.keys():
            if (isinstance(expected.get(key), (dict, list))
                    and isinstance(current.get(key), (dict, list))):
                merged[key] = self.get_new_merged_data(
                    merged[key], expected[key])
            else:
                if self.__merge_type == MergeType.PRESENT:
                    if expected[key] is None:
                        continue
                    merged[key] = expected[key]
                elif self.__merge_type == MergeType.ABSENT:
                    if merged.get(key) == expected[key]:
                        merged.pop(key)
                else:
                    raise TypeError("Unexpected MergeType")
        return merged

    @basic_annotation_type_checking
    @__check_identic
    def get_new_merged_list(self, current: list, expected: list) -> list:
        """
        Getting the merge of two list depending the MergeType and the
        ListDiffType.
        """
        if self.__list_diff_type == ListDiffType.VALUE:
            return self.__get_new_merged_list_with_value_diff(
                current, expected)
        if self.__list_diff_type == ListDiffType.INDEX:
            return self.__get_new_merged_list_with_index_diff(
                current, expected)
        raise TypeError("Unexpected ListDiffType")

    def __get_new_merged_list_with_value_diff(
            self, current: list, expected: list) -> list:
        if self.__merge_type == MergeType.PRESENT:
            return current + [elem for elem in expected if elem not in current]
        if self.__merge_type == MergeType.ABSENT:
            return [elem for elem in current if elem not in expected]
        raise TypeError("Unexpected MergeType")

    def __get_new_merged_list_with_index_diff(
            self, current: list, expected: list) -> list:
        current_dict = self.__convert_list_to_dict(current)
        expected_dict = self.__convert_list_to_dict(expected)
        merged_dict = self.get_new_merged_dict(current_dict, expected_dict)
        return self.__convert_dict_to_list(merged_dict)

    @staticmethod
    def __convert_list_to_dict(the_list: list) -> dict:
        return dict(list(enumerate(the_list)))

    @staticmethod
    def __convert_dict_to_list(the_dict: dict) -> list:
        return [val for key, val in the_dict.items()]

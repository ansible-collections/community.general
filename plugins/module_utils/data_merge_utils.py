# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy


class DataMergeUtils(object):
    """
    Utils for merging list or dict.
    """

    def __init__(self, merge_type, list_diff_type='value'):
        # type: (str, str) -> None
        self.merge_type = merge_type
        self._list_diff_type = list_diff_type

    @property
    def merge_type(self):
        """
        Describe the mean of merging data.
        """
        return self._merge_type

    @merge_type.setter
    def merge_type(self, value):
        """
        Set the mean of merging data.
        Can be one of :
        - identic : Ensure that the result is identical to the expected data.
        - present : Ensure that an element in expected data must be present in
                    the result.  If an element in expected data as different
                    value or in not present in the base data, it will be set or
                    added in the result.
        - absent  : Ensure that an element is absent in the final result. For
                    the dict, if a key is present in the current dict and in
                    the expected dict but has different value, the current
                    value will be kept in the result.
        """
        if value not in ['identic', 'present', 'absent']:
            raise ValueError('`merge_type` can be only one of `identic`, `present` or `absent`')
        self._merge_type = value

    @property
    def list_diff_type(self):
        """
        Descibe the mean of merging data for a list.
        """
        return self._list_diff_type

    @list_diff_type.setter
    def list_diff_type(self, value):
        """
        Descibe the mean of merging data for a list.
        Can be one of :
        - value :   Comparing elements in the list by their values. Search if
                    an element in expect list is present or absent, depending
                    on the MergType, to the current list.  If it not the case
                    it will be added of removed. This not check list
                    recursively, only the first level is checked.
        - index :   Comparing elements in the list by their index. If
                    `self.merge_type` is `present`, it will check if the value
                    of all elements, in the current list as the same value as
                    the element in the expected list with the same index, and
                    if it not the case, the value of the element in the
                    expected list will be set at this index position in the
                    result list. If `self.merge_type` is `absent`, it will
                    check if the value of an element in the current list as the
                    same value as the element with the same index in the
                    expected list and if it's the case, the element will not be
                    present in the result.
        """
        if value not in ['value', 'index']:
            raise ValueError('`list_diff_type` can be only one of `value` or `index`')
        self._list_diff_type = value

    def get_new_merged_data(self, current, expected):
        # type: (dict | list, dict | list) -> dict | list
        """
        Getting the merge of two element if it can't be sure that they have the
        same type.
        """
        if not isinstance(current, (dict, list)) or not isinstance(expected, (dict, list)):
            raise ValueError('Only dict or list can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return deepcopy(expected)
        if not isinstance(current, type(expected)):
            if self._merge_type == 'present':
                return deepcopy(expected)
            if self._merge_type == 'absent':
                return deepcopy(current)

        if isinstance(current, list):
            return self.get_new_merged_list(current, expected)
        return self.get_new_merged_dict(current, expected)

    def get_new_merged_dict(self, current, expected):
        # type: (dict, dict) -> dict
        """
        Getting the merge of two dict depending the `self.list_diff_type`.
        """
        if not isinstance(current, dict) or not isinstance(expected, dict):
            raise ValueError('Only two dict can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return deepcopy(expected)
        merged = deepcopy(current)
        for key in expected.keys():
            if (isinstance(expected.get(key), (dict, list)) and isinstance(current.get(key), (dict, list))):
                merged[key] = self.get_new_merged_data(merged[key], expected[key])
            else:
                if self._merge_type == 'present':
                    if expected[key] is None:
                        continue
                    merged[key] = expected[key]
                elif self._merge_type == 'absent':
                    if merged.get(key) == expected[key]:
                        merged.pop(key)
                else:
                    raise TypeError("Unexpected merge_type")
        return merged

    def get_new_merged_list(self, current, expected):
        # type (list, list) -> list
        """
        Getting the merge of two list depending the `self.merge_type` and the
        `self.list_diff_type`.
        """
        if not isinstance(current, list) or not isinstance(expected, list):
            raise ValueError('Only two list can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return deepcopy(expected)
        if self._list_diff_type == 'value':
            return self._get_new_merged_list_with_value_diff(current, expected)
        if self._list_diff_type == 'index':
            return self._get_new_merged_list_with_index_diff(current, expected)

    def _get_new_merged_list_with_value_diff(self, current, expected):
        # type: (list, list) -> list
        if self._merge_type == 'present':
            return current + [elem for elem in expected if elem not in current]
        if self._merge_type == 'absent':
            return [elem for elem in current if elem not in expected]

    def _get_new_merged_list_with_index_diff(self, current, expected):
        # type: (list, list) -> list
        current_dict = self._convert_list_to_dict(current)
        expected_dict = self._convert_list_to_dict(expected)
        merged_dict = self.get_new_merged_dict(current_dict, expected_dict)
        return self._convert_dict_to_list(merged_dict)

    @ staticmethod
    def _convert_list_to_dict(the_list):
        # type: (list) -> dict
        return dict(list(enumerate(the_list)))

    @ staticmethod
    def _convert_dict_to_list(the_dict):
        # type: (dict) -> list
        return [val for key, val in the_dict.items()]

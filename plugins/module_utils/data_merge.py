# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import copy


class DataMerge(object):
    """
    Utility to compare two data structure in form of list or dict and to get a
    result with a merging of both.
    The two data structure are identified as :
    - `current` that is you current data,
    - `expected` that is the data that you expect to be present or absent in
      in the final result, depending on `merge_type` value.
    """

    def __init__(self, merge_type, list_diff_type='value'):
        # type: (str, str) -> None
        self.merge_type = merge_type
        self._list_diff_type = list_diff_type

    @property
    def merge_type(self):
        """
        Get how merge data.
        """
        return self._merge_type

    @merge_type.setter
    def merge_type(self, value):
        """
        Set how merge data.
        There is three-way to do that :
        - identic : With this, the obtained result will be exactly identical as
                    `expected`.
        - present : With this, the values present in `expected` will be added
                    to `current` to produce the result. If an element is
                    present in both, `current` and `expected`, this will be the
                    value present in the `expected element that will be kept in
                    the result. If an element is present in `expected` but
                    absent in `current`, it will be added in the result. If an
                    element is only present in `current` it will be present in
                    result as what it is in `current`.
        - absent  : With this, the values present in `expected` will be absent
                    to the result if they have same value in `current`. If an
                    element is present in both, `current` and `expected` with
                    the same value, it will not be present in result. If an
                    element is present in `current` and `expected` but without
                    have same value, or if an element is only present in
                    `current`, it will be present in result as is it in
                    `current`. Elements only present in `expected` will be
                    ignored.

        Example :

        We have following data :
        ```
        current_data = {
            'A': 1,
            'B': 2,
            'C': {
                'D': 3,
                'E': 4,
            }
        }
        expected_data = {
            'A': 1,
            'B': 9,
            'C': {
                'E': 4,
                'F': 8,
            }
        }
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='present')
        result = data_merge.get_new_merged_dict(current_data, expected_data)
        ```
        Get the following in `result` :
        ```
        {
            'A': 1,
            'B': 9,
            'C': {
                'D': 3,
                'E': 4,
                'F': 8,
            }
        }
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='absent')
        result = data_merge.get_new_merged_dict(current_data, expected_data)
        ```
        Get the following in `result` :
        ```
        {
            'B': 2,
            'C': {
                'D': 3,
            }
        }
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='identic')
        result = data_merge.get_new_merged_dict(current_data, expected_data)
        ```
        Get the following in `result` :
        ```
        {
            'A': 1,
            'B': 9,
            'C': {
                'E': 4,
                'F': 8,
            }
        }
        ```
        """
        if value not in ['identic', 'present', 'absent']:
            raise ValueError('`merge_type` can be only one of `identic`, `present` or `absent`')
        self._merge_type = value

    @property
    def list_diff_type(self):
        """
        Get how the list are merged.
        """
        return self._list_diff_type

    @list_diff_type.setter
    def list_diff_type(self, value):
        """
        Set how merge the list.
        There is two-ways to do this :
        - value : With this, if an element is present only in `expected`
                  and `merge_type='present'` it will be added in the result, or
                  if and element is present in both list, `current` and
                  `expected` and `merge_type='absent'` it will no be present in
                  the result. The value are only compared on the first level of
                  the list. This does not do recursive operation on element that
                  contain themselves an another list.
        - index : With this, element of the list are compared like a dict with
                  the index number of element as key. With
                  `merge_type='present'`, if a value at specific index position
                  is only present in `expected` or as different value than in
                  `current`, the `expected` value will be present in the
                  result. With `merge_type='absent'`, if an element with the
                  same index in both compared list share same value, the
                  element will not be present in the result. This can be used
                  to do recursive merge on list as long as you can make sure
                  that compared value share the same index in the both lists.
                  If you need to compare only a specific position in the list
                  and ignore others who are before, you can set the value of
                  these elements to `None` in `expected`.
        Example :

        We have following lists :
        ```
        current_list = [
            'A',
            ['BA'],
            ['CA', 'CB'],
            'D',
        ]
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='present', list_diff_type='value')
        expected_list = [
            'Z',
            ['BA', 'BB', 'BC'],
            'D',
        ]
        result = data_merge.get_new_merged_list(current_list, expected_list)
        ```
        Get the following in `result `:
        ```
        [
            'A',
            ['BA'],
            ['CA', 'CB'],
            'D',
            'Z',
            ['BA', 'BB', 'BC'],
        ]
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='present', list_diff_type='index')
        expected_list = [
            'Z',
            [None, 'BB', 'BC'],
            None,
            'Y',
            'X',
        ]
        result = data_merge.get_new_merged_list(current_list, expected_list)
        ```
        Get the following in `result` :
        ```
        [
            'Z',
            ['BA', 'BB, 'BC'],
            ['CA', 'CB'],
            'Y',
            'X',
        ]
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='absent', list_diff_type='value')
        expected_list = [
            'D',
            ['BA', 'BB'],
            ['CA', 'CB'],
        ]
        result = data_merge.get_new_merged_list(current_list, expected_list)
        ```
        Get the following in `result` :
        ```
        [
            'A',
            ['BA'],
        ]
        ```

        Run :
        ```
        data_merge = DataMerge(merge_type='absent', list_diff_type='index')
        expected_list = [
            'D',
            None,
            ['CA'],
        ]
        result = data_merge.get_new_merged_list(current_list, expected_list)
        ```
        Get the following in `result` :
        ```
        [
            'A',
            ['BA'],
            ['CB'],
            'D',
        ]
        ```
        """
        if value not in ['value', 'index']:
            raise ValueError('`list_diff_type` can be only one of `value` or `index`')
        self._list_diff_type = value

    def get_new_merged_data(self, current, expected):
        # type: (dict | list, dict | list) -> dict | list
        """
        Get the result of merging of two data structure, `current` and `expected`.

        This can be use when the type of current and expected can not be granted.
        If the two data structure are different type :
        - If `merge_type='present'`, `expected` will be returned.
        - If `merge_type='absent'`, `current` will be returned.
        """
        if not isinstance(current, (dict, list)) or not isinstance(expected, (dict, list)):
            raise ValueError('Only dict or list can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return copy(expected)
        if not isinstance(current, type(expected)):
            if self._merge_type == 'present':
                return copy(expected)
            if self._merge_type == 'absent':
                return copy(current)

        if isinstance(current, list):
            return self.get_new_merged_list(current, expected)
        return self.get_new_merged_dict(current, expected)

    def get_new_merged_dict(self, current, expected):
        # type: (dict, dict) -> dict
        """
        Get the result of the merging of the two dict.
        """
        if not isinstance(current, dict) or not isinstance(expected, dict):
            raise ValueError('Only two dict can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return copy(expected)
        merged = copy(current)
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
        Get the result of the merging of the two list.
        """
        if not isinstance(current, list) or not isinstance(expected, list):
            raise ValueError('Only two list can be merged, {0} and {1} given.'.format(type(current), type(expected)))
        if self.merge_type == 'identic':
            return copy(expected)
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

# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy


class DataMerge(object):
    """
    Utils for merging list or dict with two data set with several type of
    merging.
    The two data set are called :
    - `current` that is you current data,
    - `expected` that is that you expect to be present, absent or identic in
      the final result, depending to the `merge_type`.
    """

    def __init__(self, merge_type, list_diff_type='value'):
        # type: (str, str) -> None
        self.merge_type = merge_type
        self._list_diff_type = list_diff_type

    @property
    def merge_type(self):
        """
        Get the way that the data are merged.
        """
        return self._merge_type

    @merge_type.setter
    def merge_type(self, value):
        """
        Set the way that the data are merged.
        Can be one of :
        - identic : The result will be same as `expected`` data.
        - present : If a value of an element is present in both,
                    `current` and `expected`, that the final value of the
                    element will be set to same as in `expected`. If an element
                    is absent in the `current` but present `expected` it will
                    be added. Others elements remain as they where in `current`.
        - absent  : If an element share the same key/value pair in `current`
                    and `expected`, it will not be present in the final result.
                    Others elements remain as they where in `current`.
        """
        if value not in ['identic', 'present', 'absent']:
            raise ValueError('`merge_type` can be only one of `identic`, `present` or `absent`')
        self._merge_type = value

    @property
    def list_diff_type(self):
        """
        Get the way that the list are compared for merging.
        """
        return self._list_diff_type

    @list_diff_type.setter
    def list_diff_type(self, value):
        """
        Set the way that lists are compared for merging.
        They are two :
        - value : This will search if an element in a list is present or absent
                  in another. This do no recursive search in lists, only the
                  firts level is checked (can not compare lists childs of a
                  list).
        - index : This compare lists by differentiating the value of their
                  elements by their index position. In this case it behaves
                  like as it should differentiate two dict which all keys are
                  lists index number. This can be used to do recursive search
                  in lists as long as you can make sure that the values that
                  you want to compare occupy the same position in the both
                  lists.  If you need to compare only a specific position in
                  the list and ignore others who are before, you can set the
                  value of these elements to `None` in `expected`.
        """
        if value not in ['value', 'index']:
            raise ValueError('`list_diff_type` can be only one of `value` or `index`')
        self._list_diff_type = value

    def get_new_merged_data(self, current, expected):
        # type: (dict | list, dict | list) -> dict | list
        """
        Get the result of the merging of the two elements that you can not
        ensure their type (may be list or dict).
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
        Get the result of the merging of the two dict.
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
        Get the result of the merging of the two list.
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

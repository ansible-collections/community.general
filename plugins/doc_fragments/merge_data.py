# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
    description:
      - Compared data structure can be one of list or dictionary.
      - You can compare mixed data structures like a dictionary with a list or a
        list with a dictionary. If the two type are different, then the I(expected)
        data are always returned.
      - There is three-ways to compare data. You can ensure that the I(expected)
        data are present or absent in the result, or you can also ensure that
        the result is identical to expected data.
      - When compared data structures are list or have childes that contain
        lists for the same element, there is two-way to merge them. You can
        ensure that the elements present in I(expected) are present or absent
        in the corresponding list on compared data no mater that the position
        of the element in the list, or you can ensure that the value of
        elements at specific indexs in compared lists are the same.
    options:
      expected:
        type: raw
        required: true
        description:
          - The data structure with elements that you which to find in the
            I(state) in the result.
          - This can be one of a dictionary or a list which contain itself
            other dictionaries and lists.
      state:
        type: string
        required: true
        choices:
          - present
          - absent
        description:
          - Describes how you expect to find the I(expected) data in the
            result.
          - Set it to C(present) if you want to find the elements in
            I(expected) in the result. Only the elements that are present in
            C(expected) are changed (if an element is already present in
            compared data its value is updated, else if it absent, the element
            is added), other elements already present in compared data but
            absent in I(expected) are keept in their state.
          - Set it to C(absent) if you want that the elements in I(expected)
            are absent in the result. An element is removed only if its value
            is the same in both current data and I(expected). Other elements
            are keept in their state.
          - Set it to C(identic) is you want that the result to be exactly
            identical as I(expected).
      list_diff_type:
        type: string
        required: false
        default: value
        choices:
          - value
          - index
        description:
          - When the two data structures compared are list or have children
            that contain lists at the same element, there is two-ways to
            indicate how merging theme.
          - If set to C(value), it checks if the list elements in I(expected)
            are also present in the corresponding element in compared data no
            mater of its position in the list.  This only be able to operate on
            the first level on the list (do not be able to check a list
            recursively).
          - If C(index), it compares elements in the lists by their position.
            This mean that we expect to find the same value for elements at the
            same position in both list. With this you can operate recursively
            on the list.  If you want to check only an element at a specific
            position without to worry about value of the elements that are
            before, set the value for the elements that must be ignored to
            C(null) in I(expected) (see example).
    '''

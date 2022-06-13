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
      - There is three way to compare data. You can ensure that the I(expected)
        data are present or absent to the result or you can also ensure that the
        result is identic to the compared data.
      - When the data structures compared are list or have childes that contain
        lists for the same element, there is two-way to merge them. You can ensure
        that the elements present in I(expected) are present or absent in the
        corresponding list in compared data no mater that the position of the
        element in the list, or you can ensure that the value of elements at
        specific index in compared lists are the same.
    options:
      expected:
        type: raw
        required: true
        description:
          - The data structure that you want to expect to find in the I(state) in
            the result.
          - This can be one of a dictionary or a list that can contain them self
            other dictionaries and lists.
      state:
        type: string
        required: true
        choices:
          - present
          - absent
        description:
          - Describes how you expect to find the I(expected) data in the result.
          - Set it to C(present) is you want that the elements/values pairs in
            I(expected) are present in the result. Only elements that are
            present in C(expected) are changed (values already present in
            compared data are updated and values absent in compared data are
            added), others elements already present in compared data and not
            present in I(expected) are keept in their state.
          - Set it to C(absent) is you want that the elements/values pairs
            present in I(expected) are absent in the result. The element is
            removed only if it share the same key/value in both (or value is
            present in same list), I(expected) and compared data. Other
            elements are keept in their state.
          - Set it to C(identic) is you want that the result to be exactly the
            same as I(expected).
      list_diff_type:
        type: string
        required: false
        default: value
        choices:
          - value
          - index
        description:
          - When the two data structures compared are list or have childes that contain
            lists for the same element, there is two-way to merge them.
          - If C(value), it checks if the corresponding element in I(expected) is
            present or absent in compared data no mater that the position of the
            element in the list. This only can operate on the first level on the
            list (no mean to check a list recursively with this).
          - If C(index), it compares elements in list by their position. That mean
            that we expect to find a value at a determined position in both list.
            With this you can operate recursively on the list but, you need to
            ensure that the value you want to search is at the same position in
            both list.  If you want to check only an element at a specific position
            and, you want to ignore elements which are before set the value for
            that elements to C(null) (see example).
    '''

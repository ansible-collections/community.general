# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
    description:
      - Original and modifications must contain items that be assimilable to
        dictionaries or lists and can themselves contains values that also be
        assimilable to a dictionary or a list.
      - Original data acts as basis for the new one.
      - Modifications are used to add, update or remove keys/items from
        original data.
      - The intersection between original and modifications is done by
        iterating over all keys/items in original and for each which is also
        exists in modification for a same path in the structure, compares their values.
      - When the compared values are in both side assimilable to dictionaries,
        do a recursive intersection.
    options:
      modifications:
        type: raw
        required: true
        description:
          - A data structure assimilable to a dictionary or a list that acts to
            add, update or remove keys/items from original data.
          - It must be a similar type of structure that the original data (both
            are lists or dictionaries).
          - Keys/items that composing it be present or absent to the result
            depending on the state of I(present) and to their path in the
            structure.
      present:
        type: bool
        required: false
        default: true
        description:
          - Set if keys/items in I(modifications) must be present or not to the
            result depending on their path in the structure.
          - C(true) mean that keys/items in I(modifications), acts to
            update or add keys/items from original data to make the result,
            depending on their path in the structure.
          - C(false) mean do not keep in result, keys/items in
            C(modifications) that have the same value for a same path in original
            data.
      list_as_dict:
        type: bool
        required: false
        default: false
        description:
          - Defines the way by the lists and assimilable are intersected.
          - When C(false), simply check if an item in a list from modifications
            side is also present or absent from the corresponding list from
            original side. With this, it is not possible to intersects items
            recursively but, you not need to take care about the position of
            the item in both list.
          - When C(true), acts as if lists are dictionaries with their index
            number as key. With this, values in both lists are compared
            depending on their position and, it becomes possible to
            recursively intersect their items as long as it is possibles to be
            sure of the values position.
      keep_empty:
        type: bool
        required: false
        default: false
        description:
          - Defines if keys with emptied dictionaries or lists must be
            kept or not in the result.
          - This has no effect when I(present) is C(true).
          - When C(false), keys that contain empty dictionary or list after
            the data intersection not be kept in the result.
          - When C(true), keys that contain empty dictionary or list after
            the data intersection be kept in the result.
      remove_null:
        type: bool
        required: false
        default: false
        description:
          - Defines how to treat C(null) value in modifications.
          - When C(false), C(null) value are simply ignored. This can be useful
            when lists are intersected as dictionaries with I(list_as_dict)
            and only an item at a specific position must be updated without
            taking care of value of items that are before.
          - When C(true), all keys with in C(modifications) that have C(null)
            value are not be present in result. This can be used to ensure that
            a key in original data be removed without taking care of the
            value that it can have.
    '''

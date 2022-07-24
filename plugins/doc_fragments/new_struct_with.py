# -*- coding: utf-8 -*-
# Copyright (c) 2022     , DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  changes:
    type: raw
    required: true
    description:
      - A structure assimilable to a dictionary or a list that acts to
        add, update or remove keys/items from B(base) data.
      - It must be a similar type of structure that the B(base) data (both
        are lists or dictionaries).
      - Keys/items that composing it be present or absent in the result
        depending on the used parameters.
  present:
    type: bool
    required: false
    default: true
    description:
      - Indicate if keys/items in I(changes) must be present or not in the
        result depending on their path in the structure.
      - C(true) mean I(changes), acts to updating or adding keys/items from the
        B(base) data to make the result.
      - C(false) mean I(changes), acts to removing keys/items from the B(base)
        data to make the result.
  list_as_dict:
    type: bool
    required: false
    default: false
    description:
      - There are two way to merge list.
      - When C(false), simply check if an item in a list from I(changes) side is
        also present or absent in the corresponding list from original side.
        With this, it is not possible to merge lists recursively but, you not
        need to take care about the position of the item in both list.
      - When C(true), acts as if lists are dictionaries with their index number
        as key. With this, values in both lists are compared depending on their
        position and, it becomes possible to recursively merge their items as
        long as it is possibles to be sure of the position of the values.
  keep_empty:
    type: bool
    required: false
    default: false
    description:
      - Defines if emptied lists or dictionary be kept in result after the data
        updating.
      - This has no effect when I(present) is C(true).
      - When C(false), when list or dictionary keys/items that be emptied, they
        not be keept in the result.
      - When C(true), when list or dictionary keys/items that be emptied, they
        be keept in the result.
  remove_null:
    type: bool
    required: false
    default: false
    description:
      - Defines how to treat C(null) value in I(changes).
      - When C(false), C(null) value are simply ignored. This can be useful
        when lists are merged as dictionaries with using I(list_as_dict) and
        only an item at a specific position must be updated without taking care
        of value of items that are before.
      - When C(true), all keys in C(changes) that have C(null) value be removed
        from base to make the result. This can be used to ensure that a key in
        B(base) data be removed without taking care of its actual value.
'''

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
      - A data structure assimilable to a dictionary or a list that acting to
        add, update or remove keys/items from source data structure.
      - It must have the same type of that the source data structure (both are
        lists or both are dictionaries).
      - Keys/items that composing it be present or absent in the result
        depending on the used parameters.
  present:
    type: bool
    required: false
    default: true
    description:
      - Indicate how keys/items in I(changes) are used to update them in
        the source data structure.
      - If C(yes), acts to adds/updates them.
      - If C(no), acts to remove them.
  merge_list_by_index:
    type: bool
    required: false
    default: false
    description:
      - Set if the lists items are merged depending on their index or not.
      - If C(no), it simply does a diff on items in both lists. The rest
        depends on the value of I(present) parameter. If I(present) is true,
        items that be present in I(changes) but not in the source data
        structure will be added. If I(present) is false items that be present
        in both side will be removed.
      - If C(yes), the differencing is done by comparing values in both lists
        by their index position. This act like merging two dictionary where the
        keys are index number of list items. With this, it is possible to
        operate recursively in lists but by taking care about positions of
        items in both to make sure to comparing correct values.
  keep_empty:
    type: bool
    required: false
    default: false
    description:
      - Defines if emptied lists or dictionary must be kept in the result.
      - This has no effect when I(present) is C(yes).
      - If C(no), does not keeps them.
      - If C(yes), keeps them.
  remove_null:
    type: bool
    required: false
    default: false
    description:
      - Defines how to treat C(null) value in I(changes).
      - If C(no), C(null) value are simply ignored. This can be useful when
        lists are compared as dictionaries by setting I(list_as_dict) to C(yes)
        and need to comparing only items at a specifics positions without
        taking care of items that are before.
      - If C(true), all keys in C(changes) with C(null) value acts to remove
        the corresponding key in B(base) data. This permit to ensure that a key
        in B(base) data be removed without taking care of its actual value.
'''

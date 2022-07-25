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
      - A structure assimilable to a dictionary or a list that acting to
        add, update or remove keys/items from the B(base) data.
      - Must have the same type as B(base) (both are lists or dictionaries).
      - Keys/items that composing it be present or absent in the result
        depending on used parameters.
  present
    type: bool
    required: false
    default: true
    description:
      - Indicate how keys/items in I(changes) are used to update them in
        B(base) data.
      - If C(yes), acts to adds/updates them.
      - If C(no), acts to remove them.
  list_as_dict:
    type: bool
    required: false
    default: false
    description:
      - There is two way to operate on lists.
      - If C(no), simply checks the presence of an item in both lists.
        Depending on the state of I(present), items in list on C(changes) side
        be added or removed from items on B(base) data side. This limit the
        comparison on the first level of the list (it is not possible to recursively
        comparison items whit this) but you not need to take care about the position
        of items.
      - If C(yes), lists are treated as dictionaries by using items index
        number as key. This permits to comparison items depending on their
        position and operate recursively on them as long as it is possibles to
        be sure of the values position.
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

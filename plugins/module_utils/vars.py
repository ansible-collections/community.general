# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.module_utils.six import string_types


class NewStructWith(object):

    # merge list like dict
    def __init__(self, base, changes, present=True,
                 merge_seq_by_index=False, keep_empty=False, remove_null=False):
        # type: (Mapping|Sequence, Mapping|Sequence, bool, bool, bool, bool) -> None
        """
        Starting from two similar data structure, a `base`  that acting as the
        source of data and `changes` that acting to add, update or remove
        keys/items from the `base`, creates a new one similar strucutre.

        `base` and `changes` are two structure that can be assimilable to
        `Mapping` and `Sequence`, excluding string. Both must have similar
        type, if one is a `Mapping` the other too, and if one is a `Sequence`
        the other too.

        This is originally designed to easily update configurations structures
        provided by format like JSON, YAML or TOML by ensuring the presence or
        the absence of some values in keys/items to the result.

        To create the new structure starting from `base` and `changes` iterates
        over all keys/items in `base` and for each which is also exists in
        `changes` for a same path in the structure, compares their values. When
        the compared values in both side are assimilable to dictionaries,
        operate recursively on them.

        `base` data structure acts as basis for the new one. Keys/items that
        composing it be present or absent to the result depending on the
        `present` parameter and to their path in the structure.

        `changes` data structure acts to adding/updating or removing keys/items
        from the original data. Keys/items that composing it be present or
        absent to the result depending on the state of `present` parameter and
        to their path in the structure.

        `present` parameter defines if keys/items in `changes` must be present
        or not to the result depending on their path in the structure.
        - When `True`, keys/items in `changes` are used to update or add
          keys/items at `base`.
        - When `False`, keys/items in `changes` that for a same path in the
          structure, also exists in `base` and have same value in both not be
          present in the result (acts as they are removed from `base`).

        Examples when `present=True` :
        * with this `base` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'}`
        * and this `changes` data :
          `{'A': {'AB': '9'}, 'B': ['8', '2'], 'C': '7'}`
        * get this result :
          `{'A': {'AA': '1', 'AB': '9'}, 'B': ['2', '3', '8'], 'C': '7'}`

        Example when `present=False` :
        * with this `base` data :
          `{'A': {'AA': '1', 'AB': '2'}, 'B': ['3', '4'], 'C': '5'}`
        * and this `changes` data :
          `{'A': {'AA': '1'}, 'B': ['3', '9'], 'C': '8'}`
        * get this result :
          `{'A': {'AB': '2'}, 'B': ['4'], 'C': '5'}`

        `merge_seq_by_index` sequences items can be merged by their values or
        by their index.
        - When `False`, it gets items in the sequence in `change` side that are
          not present in the sequence in `base` side, then it removes or add
          the difference depending on the `present` parameter value. This is
          not recursive but the positions of values in both sequence is not
          important.
        - When `True`, the differencing is done by comparing values on both
          sequence by their index position. This act like merging two dict
          where the keys are index number of sequence items. With this, it is
          possible to operate recursively on sequences but by taking care about
          positions of items in both to make sure to comparing correct
          values.

        Examples when `merge_seq_by_index=False` :
        * with this `base` data :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}]`
        * and this `changes` data :
          `['Z', 'B', {'C': '1'}, {'E': '3'}]`
        * if using `present=True`, get :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}, 'Z', {'C': '1'}]`
        * or if using `present=False`, get :
          `['A', {'C': '1', 'D': '2'}]`

        Examples when `merge_seq_by_index=True` :
        * with this `base` data :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}]`
        * and this `changes` data :
          `['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}]`
        * if using`present=True`, get :
          `['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}]`
        * or if using `present=False`, get :
          `['A', {'C': '1'}]`

        `keep_empty` parameter defines if keys with emptied dictionaries or
        lists must be kept or not in the result. This has no effect when
        `present` parameter is `True`.
        - When `False`, keys that contain empty dictionary or list after the
          update not be kept in the result.
        - When `True`, keys that contain empty dictionary or list after the
          update be kept in the result.

        Examples :
        * with this `base` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'}`
        * and this `changes` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3']}`
        * if using `keep_empty=False` with `present=False`, get :
          `{'C': '4'}`
        * or if using `keep_empty=True` with `present=False`, get :
          `{'A': {}, 'B': [], 'C': '4'}`

        `keep_null` parameter defines how to treat `None` value in `changes`.
        - When `Fase`, `None` value are simply ignored. This can be useful when
          lists are updated as dictionaries (when using `merge_seq_by_index`
          with `True`) and only an item at a specific position must be updated
          without taking care of value of items that are before.
        - When `True`, all keys with in `changes` that have a `None` value are
          not be present in result. This can be used to ensure that a key in
          `base` be removed without taking care of the value that it can have.

        Example that ingoing lists values at specific position with
        `remove_none=False` and `merge_seq_by_index=True` :
        * with this `base` data :
          `['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E']`
        * and this `changes` data :
          `[None, None, 'Z', {'DA': '1', 'DB': None}, 'E']`
        * if using `present=True', get :
          `['A', 'B', 'Z', {'DA': '1', 'DB': '2'}, 'E']`
        * or if using `present=False', get :
          `['A', 'B', 'C', {'DB': '2'}]`

        Example that remove keys/items with `remove_none=True` and `present=False` :
        * with this `base` data :
         `{'A': '1', 'B': '2', 'C': {'CA': '3', 'CB': '4'}, 'D': ['DA', 'DB']}`
        * and this `changes` data :
          `{'B': None, 'C': {'CB': None}, 'D': None}`
        * get :
          `{'A': '1', 'C': {'CA': '3'}}`
        """

        if self._both_are_assimilable_to_dict(base, changes):
            if present:
                self._get_method = self._get_new_dict_with_changes_present
            else:
                self._get_method = self._get_new_dict_with_changes_absent
        elif self._both_are_assimilable_to_list(base, changes):
            if present:
                self._get_method = self._get_new_list_with_changes_present
            else:
                self._get_method = self._get_new_list_with_changes_absent
        else:
            msg = "`base` and `changes` must have the same type and be `Mapping` or `Sequence` except `string_type`, {0} and {1} given"
            raise TypeError(msg.format(type(base), type(changes)))
        self._base = base
        self._changes = changes
        self._present = present
        self._merge_seq_by_index = merge_seq_by_index
        self._keep_empty = keep_empty
        self._remove_none = remove_null

    def get(self):
        # type: () -> dict | list
        """
        Get the new structure depending on initialisation parameters.
        """
        return self._get_method(self._base, self._changes)

    def _get_new_dict_with_changes_present(self, base, changes):
        # type: (Mapping, Mapping) -> dict
        new = {}
        keys_base = base.keys()
        keys_changes = changes.keys()
        keys_all = list(keys_base) + [key for key in keys_changes if key not in keys_base]
        for k in keys_all:
            # Ignoring value of changes[k] when it None permit to avoid to
            # update this item when it explicitly skipped with
            # `merge_seq_by_index=True`.
            if k not in keys_changes or changes[k] is None:
                new[k] = base[k]
            elif self._both_are_assimilable_to_dict(base.get(k), changes[k]):
                new[k] = self._get_new_dict_with_changes_present(base[k], changes[k])
            elif self._both_are_assimilable_to_list(base.get(k), changes[k]):
                new[k] = self._get_new_list_with_changes_present(base[k], changes[k])
            else:
                new[k] = changes[k]
        return new

    def _get_new_dict_with_changes_absent(self, base, changes):
        # type: (Mapping, Mapping) -> dict
        new = {}
        for k, base_elem in base.items():
            changes_elem = changes.get(k)
            if self._both_are_assimilable_to_dict(base_elem, changes_elem):
                res = self._get_new_dict_with_changes_absent(base_elem, changes_elem)
                if len(res) > 0 or self._keep_empty:
                    new[k] = res
            elif self._both_are_assimilable_to_list(base_elem, changes_elem):
                res = self._get_new_list_with_changes_absent(base_elem, changes_elem)
                if len(res) > 0 or self._keep_empty:
                    new[k] = res
            elif not base_elem == changes_elem and not (
                    self._remove_none and changes_elem is None and k in changes.keys()):
                new[k] = base_elem
        return new

    def _get_new_list_with_changes_present(self, base, changes):
        # type: (Sequence, Sequence) -> list
        if self._merge_seq_by_index:
            base_dict = self._convert_generic_sequence_to_dict(base)
            changes_dict = self._convert_generic_sequence_to_dict(changes)
            res_dict = self._get_new_dict_with_changes_present(base_dict, changes_dict)
            new = self._convert_generic_mapping_to_list(res_dict)
        else:
            new = base + [elem for elem in changes if elem not in base]
        return new

    def _get_new_list_with_changes_absent(self, base, changes):
        # type: (Sequence, Sequence) -> list
        if self._merge_seq_by_index:
            base_dict = self._convert_generic_sequence_to_dict(base)
            changes_dict = self._convert_generic_sequence_to_dict(changes)
            new = self._get_new_dict_with_changes_absent(base_dict, changes_dict)
            new = self._convert_generic_mapping_to_list(new)
        else:
            new = [elem for elem in base if elem not in changes]
        return new

    @staticmethod
    def _both_are_assimilable_to_dict(base, changes):
        # type: (any, any) -> bool
        return (isinstance(base, Mapping) and isinstance(changes, Mapping))

    @staticmethod
    def _both_are_assimilable_to_list(base, changes):
        # type (any, any) -> bool
        # Need to ignore string to avoid infinite loop on intersection
        if (isinstance(base, string_types) or isinstance(changes, string_types)):
            return False
        return (isinstance(base, Sequence) and isinstance(changes, Sequence))

    @staticmethod
    def _convert_generic_sequence_to_dict(elem):
        # type: (Sequence) -> dict
        return dict(list(enumerate(elem)))

    @staticmethod
    def _convert_generic_mapping_to_list(elem):
        # type: (Mapping) -> list
        return list(elem.values())

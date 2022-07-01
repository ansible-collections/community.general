# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.module_utils.six import string_types


class DataIntersection(object):

    def __init__(self, original, modifs, present=True,
                 list_as_dict=False, keep_empty=False, remove_null=False):
        # type: (Mapping|Sequence, Mapping|Sequence, bool, bool, bool, bool) -> None
        """
        Starting from two similar data structure, an original and
        modifications, creates a new one which is an intersection of these.

        This is designed to easily update configurations structures provided by
        format like JSON, YAML or TOML by ensuring the presence or the absence
        of some values in keys/items to the result.

        `original` and `modifs` parameter are two data structure with a type
        that can be assimilable to `Mapping` and `Sequence`, excluding string
        type. Both must have similar type, if one is a `Mapping` the other too,
        and if one is a `Sequence` the other too.

        The intersection between `original` and `modifs` is done by iterating
        over all keys/items in `original` and for each which is also exists in
        `modifs` for a same path in the structure, compares their values. When
        the compared values in both side are assimilable to dictionaries, do a
        recursive intersection.

        `original` data structure acts as basis for the new one. Keys/items
        that composing it be present or absent to the result depending on the
        `present` parameter and to their path in the structure.

        `modifs` data structure acts to adding/updating or removing keys/items
        from the original data. Keys/items that composing it be present or
        absent to the result depending on the state of `present` parameter and
        to their path in the structure.

        `present` parameter defines if keys/items in `modifs` must be present
        or not to the result depending on their path in the structure.
        - When `True`, keys/items in `modifs` are used to update or add
          keys/items at `original` data.
        - When `False`, keys/items in `modifs` that for a same path in the
          structure, also exists in `original` and have same value in both are
          not present to the result (acts as they are removed from `original`
          data).

        Examples when `present=True` :
        * with this `original` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'}`
        * and this `modifications` data :
          `{'A': {'AB': '9'}, 'B': ['8', '2'], 'C': '7'}`
        * get this result :
          `{'A': {'AA': '1', 'AB': '9'}, 'B': ['2', '3', '8'], 'C': '7'}`

        Example when `present=False` :
        * with this `original` data :
          `{'A': {'AA': '1', 'AB': '2'}, 'B': ['3', '4'], 'C': '5'}`
        * and this `modifications` data :
          `{'A': {'AA': '1'}, 'B': ['3', '9'], 'C': '8'}`
        * get this result :
          `{'A': {'AB': '2'}, 'B': ['4'], 'C': '5'}`

        `list_as_dict` parameter defines the way by the lists and assimilable
        are intersected.
        - When `false`, simply check if an item in a list from `modifs`
          side is also present or absent from the corresponding list in
          `original` side. With this, it is not possible to intersects items
          recursively but, you not need to take care about the position of
          the item in both list.
        - When `True`, acts as if lists are dictionaries with their index
          number as key. With this, values in both lists are compared
          depending on their position and, it becomes possible to
          recursively intersect their items as long as it is possibles to be
          sure of the values position.

        Examples when `merge_seq_by_index=False` :
        * with this `original` data :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}]`
        * and this `modifs` data :
          `['Z', 'B', {'C': '1'}, {'E': '3'}]`
        * if using `present=True`, get :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}, 'Z', {'C': '1'}]`
        * or if using `present=False`, get :
          `['A', {'C': '1', 'D': '2'}]`

        Examples when `merge_seq_by_index=True` :
        * with this `original` data :
          `['A', 'B', {'C': '1', 'D': '2'}, {'E': '3'}]`
        * and this `modifs` data :
          `['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}]`
        * if using`present=True`, get :
          `['Z', 'B', {'C': '9', 'D': '2'}, {'E': '3'}]`
        * or if using `present=False`, get :
          `['A', {'C': '1'}]`

        `keep_empty` parameter defines if keys with emptied dictionaries or
        lists must be kept or not in the result. This has no effect when
        `present` parameter is `True`.
        - When `False`, keys that contain empty dictionary or list after the
          data intersection not be kept in the result.
        - When `True`, keys that contain empty dictionary or list after the
          data intersection be kept in the result.

        Examples :
        * with this `original` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3'], 'C': '4'}`
        * and this `modifs` data :
          `{'A': {'AA': '1'}, 'B': ['2', '3']}`
        * if using `keep_empty=False` with `present=False`, get :
          `{'C': '4'}`
        * or if using `keep_empty=True` with `present=False`, get :
          `{'A': {}, 'B': [], 'C': '4'}`

        `keep_null` parameter defines how to treat `None` value in `modifs`.
        - When `Fase`, `None` value are simply ignored. This can be useful
          when lists are intersected as dictionaries (when using`list_as_dict`
          with `True`) and only an item at a specific position must be
          updated without taking care of value of items that are before.
        - When `True`, all keys with in `modifs` that have a `None` value are
          not be present in result. This can be used to ensure that a key in
          original data be removed without taking care of the value that it can
          have.

        Example that ingoing lists values at specific position with
        `remove_none=False` and `merge_seq_by_index=True` :
        * with this `original` data :
          `['A', 'B', 'C', {'DA': '1', 'DB': '2'}, 'E']`
        * and this `modifs` data :
          `[None, None, 'Z', {'DA': '1', 'DB': None}, 'E']`
        * if using `present=True', get :
          `['A', 'B', 'Z', {'DA': '1', 'DB': '2'}, 'E']`
        * or if using `present=False', get :
          `['A', 'B', 'C', {'DB': '2'}]`

        Example that remove keys/items with `remove_none=True` and `present=False` :
        * with this `original` data :
         `{'A': '1', 'B': '2', 'C': {'CA': '3', 'CB': '4'}, 'D': ['DA', 'DB']}`
        * and this `modifs` data :
          `{'B': None, 'C': {'CB': None}, 'D': None}`
        * get :
          `{'A': '1', 'C': {'CA': '3'}}`
        """

        if self._both_are_assimilable_to_dict(original, modifs):
            if present:
                self._get_method = self._get_new_dict_with_modif_present
            else:
                self._get_method = self._get_new_dict_with_modif_absent
        elif self._both_are_assimilable_to_list(original, modifs):
            if present:
                self._get_method = self._get_new_list_with_modif_present
            else:
                self._get_method = self._get_new_list_with_modif_absent
        else:
            msg = "`base` and `changes` must have the same type and be `Mapping` or `Sequence` except `string_type`, {0} and {1} given"
            raise TypeError(msg.format(type(original), type(modifs)))
        self._base = original
        self._changes = modifs
        self._present = present
        self._merge_seq_by_index = list_as_dict
        self._keep_empty = keep_empty
        self._remove_none = remove_null

    def get(self):
        # type: () -> dict | list
        """
        Get the new data structure depending on initialisation parameters.
        """
        return self._get_method(self._base, self._changes)

    def _get_new_dict_with_modif_present(self, original, modifs):
        # type: (Mapping, Mapping) -> dict
        new = {}
        keys_base = original.keys()
        keys_changes = modifs.keys()
        keys_all = list(keys_base) + [key for key in keys_changes if key not in keys_base]
        for k in keys_all:
            # Ignoring value of changes[k] when it None permit to avoid to
            # update this item when it explicitly skipped with
            # `merge_seq_by_index=True`.
            if k not in keys_changes or modifs[k] is None:
                new[k] = original[k]
            elif self._both_are_assimilable_to_dict(original.get(k), modifs[k]):
                new[k] = self._get_new_dict_with_modif_present(original[k], modifs[k])
            elif self._both_are_assimilable_to_list(original.get(k), modifs[k]):
                new[k] = self._get_new_list_with_modif_present(original[k], modifs[k])
            else:
                new[k] = modifs[k]
        return new

    def _get_new_dict_with_modif_absent(self, original, modifs):
        # type: (Mapping, Mapping) -> dict
        new = {}
        for k, base_elem in original.items():
            change_elem = modifs.get(k)
            if self._both_are_assimilable_to_dict(base_elem, change_elem):
                intersect_res = self._get_new_dict_with_modif_absent(base_elem, change_elem)
                if len(intersect_res) > 0 or self._keep_empty:
                    new[k] = intersect_res
            elif self._both_are_assimilable_to_list(base_elem, change_elem):
                intersect_res = self._get_new_list_with_modif_absent(base_elem, change_elem)
                if len(intersect_res) > 0 or self._keep_empty:
                    new[k] = intersect_res
            elif not base_elem == change_elem and not (
                    self._remove_none and change_elem is None and k in modifs.keys()):
                new[k] = base_elem
        return new

    def _get_new_list_with_modif_present(self, original, modifs):
        # type: (Sequence, Sequence) -> list
        if self._merge_seq_by_index:
            base_dict = self._convert_generic_sequence_to_dict(original)
            changes_dict = self._convert_generic_sequence_to_dict(modifs)
            res_dict = self._get_new_dict_with_modif_present(base_dict, changes_dict)
            new = self._convert_generic_mapping_to_list(res_dict)
        else:
            new = original + [elem for elem in modifs if elem not in original]
        return new

    def _get_new_list_with_modif_absent(self, original, modifs):
        # type: (Sequence, Sequence) -> list
        if self._merge_seq_by_index:
            base_dict = self._convert_generic_sequence_to_dict(original)
            changes_dict = self._convert_generic_sequence_to_dict(modifs)
            new = self._get_new_dict_with_modif_absent(base_dict, changes_dict)
            new = self._convert_generic_mapping_to_list(new)
        else:
            new = [elem for elem in original if elem not in modifs]
        return new

    @staticmethod
    def _both_are_assimilable_to_dict(original, modifs):
        # type: (any, any) -> bool
        return (isinstance(original, Mapping) and isinstance(modifs, Mapping))

    @staticmethod
    def _both_are_assimilable_to_list(original, modifs):
        # type (any, any) -> bool
        # Need to ignore string to avoid infinite loop on intersection
        if (isinstance(original, string_types) or isinstance(modifs, string_types)):
            return False
        return (isinstance(original, Sequence) and isinstance(modifs, Sequence))

    @staticmethod
    def _convert_generic_sequence_to_dict(elem):
        # type: (Sequence) -> dict
        return dict(list(enumerate(elem)))

    @staticmethod
    def _convert_generic_mapping_to_list(elem):
        # type: (Mapping) -> list
        return [val for key, val in elem.items()]

# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.module_utils.six import string_types


class BintoA(object):

    def __init__(self, a, b, present=True, merge_seq_by_index=False, keep_empty=False):
        if self._both_are_mappings(a, b):
            if present:
                self._f_get = self._new_map_with_b_present
            else:
                self._f_get = self._new_map_with_b_absent
        elif self._both_are_sequences(a, b):
            if present:
                self._f_get = self._new_seq_with_b_present
            else:
                self._f_get = self._new_seq_with_b_absent
        else:
            msg = 'a and b must have the same type and be Mapping or Sequence that is not a string, {0} and {1}'
            msg.format(type(a), type(b))
            raise TypeError(msg)
        self._a = a
        self._b = b
        self._present = present
        self._merge_seq_by_index = merge_seq_by_index
        self._keep_empty = keep_empty

    def get(self):
        return self._f_get(self._a, self._b)

    def _new_map_with_b_present(self, a, b):
        res = {}
        keys_a = a.keys()
        keys_b = b.keys()
        keys = list(keys_a) + [key for key in keys_b if key not in keys_a]
        for k in keys:
            # Ignore value of b[k] when it None permit to avoid to update this
            # item when it explicitly skipped when merge_seq_by_index is used.
            if k not in keys_b or b[k] is None:
                res[k] = a[k]
            elif self._both_are_mappings(a.get(k), b[k]):
                res[k] = self._new_map_with_b_present(a[k], b[k])
            elif self._both_are_sequences(a.get(k), b[k]):
                res[k] = self._new_seq_with_b_present(a[k], b[k])
            else:
                res[k] = b[k]
        return res

    def _new_map_with_b_absent(self, a, b):
        res = {}
        for k, val_a in a.items():
            val_b = b.get(k)
            if self._both_are_mappings(val_a, val_b):
                m_res = self._new_map_with_b_absent(val_a, val_b)
                if len(m_res) > 0 or self._keep_empty:
                    res[k] = m_res
            elif self._both_are_sequences(val_a, val_b):
                m_res = self._new_seq_with_b_absent(val_a, val_b)
                if len(m_res) > 0 or self._keep_empty:
                    res[k] = m_res
            elif not val_a == val_b:
                res[k] = val_a
        return res

    def _new_seq_with_b_present(self, a, b):
        if self._merge_seq_by_index:
            map_a = self._seq_to_map(a)
            map_b = self._seq_to_map(b)
            res = self._new_map_with_b_present(map_a, map_b)
            res = self._map_to_seq(res)
        else:
            res = a + [e for e in b if e not in a]
        return res

    def _new_seq_with_b_absent(self, a, b):
        if self._merge_seq_by_index:
            map_a = self._seq_to_map(a)
            map_b = self._seq_to_map(b)
            res = self._new_map_with_b_absent(map_a, map_b)
            res = self._map_to_seq(res)
        else:
            res = [elem for elem in a if elem not in b]
        return res

    @staticmethod
    def _both_are_mappings(a, b):
        return (isinstance(a, Mapping) and isinstance(b, Mapping))

    @staticmethod
    def _both_are_sequences(a, b):
        # Need to ignore string to avoid infinite loop
        if (isinstance(a, string_types) or isinstance(b, string_types)):
            return False
        return (isinstance(a, Sequence) and isinstance(b, Sequence))

    @staticmethod
    def _seq_to_map(seq):
        # type: (Sequence) -> Mapping
        return dict(list(enumerate(seq)))

    @staticmethod
    def _map_to_seq(map_):
        # type: (Mapping) -> Sequence
        return [val for key, val in map_.items()]

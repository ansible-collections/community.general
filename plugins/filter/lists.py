# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.collections import is_sequence


def remove_duplicates(lst):
    seen = set()
    seen_add = seen.add
    result = []
    for item in lst:
        try:
            if item not in seen:
                seen_add(item)
                result.append(item)
        except TypeError:
            # This happens for unhashable values `item`. If this happens,
            # convert `seen` to a list and continue.
            seen = list(seen)
            seen_add = seen.append
            if item not in seen:
                seen_add(item)
                result.append(item)
    return result


def flatten_list(lst):
    result = []
    for sublist in lst:
        if not is_sequence(sublist):
            msg = "All arguments must be lists. %s is %s"
            raise AnsibleFilterError(msg % (sublist, type(sublist)))
        if len(sublist) > 0:
            if all(is_sequence(sub) for sub in sublist):
                for item in sublist:
                    result.append(item)
            else:
                result.append(sublist)
    return result


def lists_union(*args, **kwargs):
    lists = args
    flatten = kwargs.pop("flatten", False)

    if kwargs:
        # Some unused kwargs remain
        raise AnsibleFilterError(f"lists_union() got unexpected keywords arguments: {', '.join(kwargs.keys())}")

    if flatten:
        lists = flatten_list(args)

    if not lists:
        return []

    if len(lists) == 1:
        return lists[0]

    a = lists[0]
    for b in lists[1:]:
        a = do_union(a, b)
    return remove_duplicates(a)


def do_union(a, b):
    return a + b


def lists_intersect(*args, **kwargs):
    lists = args
    flatten = kwargs.pop("flatten", False)

    if kwargs:
        # Some unused kwargs remain
        raise AnsibleFilterError(f"lists_intersect() got unexpected keywords arguments: {', '.join(kwargs.keys())}")

    if flatten:
        lists = flatten_list(args)

    if not lists:
        return []

    if len(lists) == 1:
        return lists[0]

    a = remove_duplicates(lists[0])
    for b in lists[1:]:
        a = do_intersect(a, b)
    return a


def do_intersect(a, b):
    isect = []
    try:
        other = set(b)
        isect = [item for item in a if item in other]
    except TypeError:
        # This happens for unhashable values,
        # use a list instead and redo.
        other = list(b)
        isect = [item for item in a if item in other]
    return isect


def lists_difference(*args, **kwargs):
    lists = args
    flatten = kwargs.pop("flatten", False)

    if kwargs:
        # Some unused kwargs remain
        raise AnsibleFilterError(f"lists_difference() got unexpected keywords arguments: {', '.join(kwargs.keys())}")

    if flatten:
        lists = flatten_list(args)

    if not lists:
        return []

    if len(lists) == 1:
        return lists[0]

    a = remove_duplicates(lists[0])
    for b in lists[1:]:
        a = do_difference(a, b)
    return a


def do_difference(a, b):
    diff = []
    try:
        other = set(b)
        diff = [item for item in a if item not in other]
    except TypeError:
        # This happens for unhashable values,
        # use a list instead and redo.
        other = list(b)
        diff = [item for item in a if item not in other]
    return diff


def lists_symmetric_difference(*args, **kwargs):
    lists = args
    flatten = kwargs.pop("flatten", False)

    if kwargs:
        # Some unused kwargs remain
        raise AnsibleFilterError(f"lists_difference() got unexpected keywords arguments: {', '.join(kwargs.keys())}")

    if flatten:
        lists = flatten_list(args)

    if not lists:
        return []

    if len(lists) == 1:
        return lists[0]

    a = lists[0]
    for b in lists[1:]:
        a = do_symmetric_difference(a, b)
    return a


def do_symmetric_difference(a, b):
    sym_diff = []
    union = lists_union(a, b)
    try:
        isect = set(a) & set(b)
        sym_diff = [item for item in union if item not in isect]
    except TypeError:
        # This happens for unhashable values,
        # build the intersection of `a` and `b` backed
        # by a list instead of a set and redo.
        isect = lists_intersect(a, b)
        sym_diff = [item for item in union if item not in isect]
    return sym_diff


class FilterModule:
    """Ansible lists jinja2 filters"""

    def filters(self):
        return {
            "lists_union": lists_union,
            "lists_intersect": lists_intersect,
            "lists_difference": lists_difference,
            "lists_symmetric_difference": lists_symmetric_difference,
        }

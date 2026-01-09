# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import typing as t
from collections.abc import Mapping, Sequence

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.collections import is_sequence


def _keys_filter_params(
    data: t.Any, matching_parameter: t.Any
) -> tuple[Sequence[Mapping[str, t.Any]], t.Literal["equal", "starts_with", "ends_with", "regex"]]:
    """test parameters:
    * data must be a list of dictionaries. All keys must be strings.
    * matching_parameter is member of a list.
    """

    mp = matching_parameter
    ml = ["equal", "starts_with", "ends_with", "regex"]

    if not isinstance(data, Sequence):
        msg = f"First argument must be a list. {data!r} is {type(data)}"
        raise AnsibleFilterError(msg)

    for elem in data:
        if not isinstance(elem, Mapping):
            msg = f"The data items must be dictionaries. {elem} is {type(elem)}"
            raise AnsibleFilterError(msg)

    for elem in data:
        if not all(isinstance(item, str) for item in elem.keys()):
            msg = f"Top level keys must be strings. keys: {list(elem.keys())}"
            raise AnsibleFilterError(msg)

    if mp not in ml:
        msg = f"The matching_parameter must be one of {ml}. matching_parameter={mp!r}"
        raise AnsibleFilterError(msg)

    return data, mp


def _keys_filter_target_str(target: t.Any, matching_parameter: t.Any) -> tuple[str, ...] | re.Pattern:
    """
    Test:
    * target is a non-empty string or list.
    * If target is list all items are strings.
    * target is a string or list with single string if matching_parameter=regex.
    Convert target and return:
    * tuple of unique target items, or
    * tuple with single item, or
    * compiled regex if matching_parameter=regex.
    """

    if not isinstance(target, Sequence):
        msg = f"The target must be a string or a list. target is {type(target)}."
        raise AnsibleFilterError(msg)

    if len(target) == 0:
        msg = "The target can't be empty."
        raise AnsibleFilterError(msg)

    if is_sequence(target):
        for elem in target:
            if not isinstance(elem, str):
                msg = f"The target items must be strings. {elem!r} is {type(elem)}"
                raise AnsibleFilterError(msg)

    if matching_parameter == "regex":
        if isinstance(target, str):
            r = target
        else:
            if len(target) > 1:
                msg = "Single item is required in the target list if matching_parameter=regex."
                raise AnsibleFilterError(msg)
            else:
                r = target[0]
        try:
            return re.compile(r)
        except re.error as e:
            msg = f"The target must be a valid regex if matching_parameter=regex. target is {r}"
            raise AnsibleFilterError(msg) from e
    elif isinstance(target, str):
        return (target,)
    else:
        return tuple(set(target))


def _keys_filter_target_dict(
    target: t.Any, matching_parameter: t.Any
) -> list[tuple[str, str]] | list[tuple[re.Pattern, str]]:
    """
    Test:
    * target is a list of dictionaries with attributes 'after' and 'before'.
    * Attributes 'before' must be valid regex if matching_parameter=regex.
    * Otherwise, the attributes 'before' must be strings.
    Convert target and return:
    * iterator that aggregates attributes 'before' and 'after', or
    * iterator that aggregates compiled regex of attributes 'before' and 'after' if matching_parameter=regex.
    """

    if not isinstance(target, list):
        msg = f"The target must be a list. target is {target!r} of type {type(target)}."
        raise AnsibleFilterError(msg)

    if len(target) == 0:
        msg = "The target can't be empty."
        raise AnsibleFilterError(msg)

    for elem in target:
        if not isinstance(elem, Mapping):
            msg = f"The target items must be dictionaries. {elem!r}%s is {type(elem)}"
            raise AnsibleFilterError(msg)
        if not all(k in elem for k in ("before", "after")):
            msg = "All dictionaries in target must include attributes: after, before."
            raise AnsibleFilterError(msg)
        if not isinstance(elem["before"], str):
            msg = f"The attributes before must be strings. {elem['before']!r} is {type(elem['before'])}"
            raise AnsibleFilterError(msg)
        if not isinstance(elem["after"], str):
            msg = f"The attributes after must be strings. {elem['after']!r} is {type(elem['after'])}"
            raise AnsibleFilterError(msg)

    before: list[str] = [d["before"] for d in target]
    after: list[str] = [d["after"] for d in target]

    if matching_parameter == "regex":
        try:
            tr = map(re.compile, before)
            return list(zip(tr, after))
        except re.error as e:
            msg = (
                "The attributes before must be valid regex if matching_parameter=regex."
                " Not all items are valid regex in: %s"
            )
            raise AnsibleFilterError(msg % before) from e
    else:
        return list(zip(before, after))

# Copyright (C) 2021 Eric Lavarde <elavarde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: version_sort
short_description: Sort a list according to version order instead of pure alphabetical one
version_added: 2.2.0
author: Eric L. (@ericzolf)
description:
  - Sort a list according to version order instead of pure alphabetical one.
options:
  _input:
    description: A list of strings to sort.
    type: list
    elements: string
    required: true
  style:
    description:
      - The strategy used to compare versions.
      - Except for V(loose) and V(natural), the strategies split each version into runs of digits and runs of letters,
        ignoring any other characters, and differ in how they order a number, a text, and the end of the version
        when found at the first position where two versions differ.
    type: str
    default: loose
    choices:
      loose: >-
        Compare versions using C(LooseVersion) semantics. This fails when the first differing position holds a number
        in one version and a text in the other.
      natural: Compare runs of digits numerically and everything else, including separators, as text.
      pre_release: Text < end of version < number.
      post_release: End of version < text < number.
      numbers_first: End of version < number < text.
    version_added: 14.0.0
"""

EXAMPLES = r"""
- name: Sort a list of strings by version
  ansible.builtin.set_fact:
    sorted_list: "{{ ['2.1', '2.10', '2.9'] | community.general.version_sort }}"
    # Result is ['2.1', '2.9', '2.10']

- name: Sort a list of strings by version, comparing digits numerically and everything else as text
  ansible.builtin.set_fact:
    sorted_list: "{{ versions | community.general.version_sort(style='natural') }}"
    # Result is ['1.0-alpha', '1.0.1', '1.0alpha', '1.1-SNAPSHOT', '1.1.0-SNAPSHOT']
  vars:
    versions: ['1.1.0-SNAPSHOT', '1.0alpha', '1.1-SNAPSHOT', '1.0.1', '1.0-alpha']

- name: Sort a list of strings by version, placing text suffixes before the release
  ansible.builtin.set_fact:
    sorted_list: "{{ versions | community.general.version_sort(style='pre_release') }}"
    # Result is ['1.0alpha', '1.0rc1', '1.0', '1.0.1']
  vars:
    versions: ['1.0.1', '1.0', '1.0rc1', '1.0alpha']

- name: Sort a list of strings by version, placing text suffixes after the release but before further numbers
  ansible.builtin.set_fact:
    sorted_list: "{{ versions | community.general.version_sort(style='post_release') }}"
    # Result is ['1.0', '1.0alpha', '1.0rc1', '1.0.1']
  vars:
    versions: ['1.0.1', '1.0', '1.0rc1', '1.0alpha']

- name: Sort a list of strings by version, placing further numbers before text suffixes
  ansible.builtin.set_fact:
    sorted_list: "{{ versions | community.general.version_sort(style='numbers_first') }}"
    # Result is ['1.0', '1.0.1', '1.0alpha', '1.0rc1']
  vars:
    versions: ['1.0.1', '1.0', '1.0rc1', '1.0alpha']
"""

RETURN = r"""
_value:
  description: The list of strings sorted by version.
  type: list
  elements: string
"""

import re
import typing as t
from collections.abc import Iterable

from ansible.errors import AnsibleFilterError

from ansible_collections.community.general.plugins.module_utils._version import LooseVersion

_NATURAL_SORT_RE = re.compile(r"(\d+)")
_TOKEN_RE = re.compile(r"(\d+)|([^\W\d_]+)")


def _natural_sort_key(value: str) -> list[int | str]:
    return [int(chunk) if chunk.isdigit() else chunk for chunk in _NATURAL_SORT_RE.split(value)]


def _ranked_sort_key(value: str, end: int, text: int, number: int) -> list[tuple]:
    key: list[tuple] = [
        (number, int(m.group(1))) if m.group(1) else (text, m.group(2)) for m in _TOKEN_RE.finditer(value)
    ]
    key.append((end,))
    return key


def _pre_release_sort_key(value: str) -> list[tuple]:
    return _ranked_sort_key(value, text=0, end=1, number=2)


def _post_release_sort_key(value: str) -> list[tuple]:
    return _ranked_sort_key(value, end=0, text=1, number=2)


def _numbers_first_sort_key(value: str) -> list[tuple]:
    return _ranked_sort_key(value, end=0, number=1, text=2)


_SORT_KEYS: dict[str, t.Callable[[str], t.Any]] = {
    "loose": LooseVersion,
    "natural": _natural_sort_key,
    "pre_release": _pre_release_sort_key,
    "post_release": _post_release_sort_key,
    "numbers_first": _numbers_first_sort_key,
}


def _validate_value(value: t.Any) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise AnsibleFilterError(f"Input must be a list of strings, got {type(value).__name__}")
    items = list(value)
    for index, item in enumerate(items):
        if not isinstance(item, str):
            raise AnsibleFilterError(
                f"Input elements must be strings, got {type(item).__name__} for index {index}: {item!r}"
            )
    return items


def version_sort(value: t.Any, reverse: t.Any = False, *, style: t.Any = "loose") -> list[str]:
    """Sort a list according to the selected style"""
    items = _validate_value(value)
    if not isinstance(reverse, bool):
        raise AnsibleFilterError(f"reverse must be a boolean, got {type(reverse).__name__}")
    if style not in _SORT_KEYS:
        raise AnsibleFilterError(f"style must be one of {', '.join(_SORT_KEYS)}, got {style!r}")
    return sorted(items, key=_SORT_KEYS[style], reverse=reverse)


class FilterModule:
    """Version sort filter"""

    def filters(self):
        return {"version_sort": version_sort}

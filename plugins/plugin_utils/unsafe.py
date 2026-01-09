# Copyright (c) 2023, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import typing as t
from collections.abc import Mapping, Sequence, Set

from ansible.module_utils.common.collections import is_sequence
from ansible.utils.unsafe_proxy import (
    AnsibleUnsafe,
)
from ansible.utils.unsafe_proxy import (
    wrap_var as _make_unsafe,
)

_RE_TEMPLATE_CHARS = re.compile("[{}]")
_RE_TEMPLATE_CHARS_BYTES = re.compile(b"[{}]")


@t.overload
def make_unsafe(value: None) -> None: ...


@t.overload
def make_unsafe(value: Mapping) -> dict: ...


@t.overload
def make_unsafe(value: Set) -> set: ...


@t.overload
def make_unsafe(value: tuple) -> tuple: ...


@t.overload
def make_unsafe(value: list) -> list: ...


@t.overload
def make_unsafe(value: Sequence) -> Sequence: ...


@t.overload
def make_unsafe(value: str) -> str: ...


@t.overload
def make_unsafe(value: bool) -> bool: ...


@t.overload
def make_unsafe(value: int) -> int: ...


@t.overload
def make_unsafe(value: float) -> float: ...


def make_unsafe(value: t.Any) -> t.Any:
    if value is None or isinstance(value, AnsibleUnsafe):
        return value

    if isinstance(value, Mapping):
        return {make_unsafe(key): make_unsafe(val) for key, val in value.items()}
    elif isinstance(value, Set):
        return {make_unsafe(elt) for elt in value}
    elif is_sequence(value):
        return type(value)(make_unsafe(elt) for elt in value)
    elif isinstance(value, bytes):
        if _RE_TEMPLATE_CHARS_BYTES.search(value):
            value = _make_unsafe(value)
        return value
    elif isinstance(value, str):
        if _RE_TEMPLATE_CHARS.search(value):
            value = _make_unsafe(value)
        return value

    return value

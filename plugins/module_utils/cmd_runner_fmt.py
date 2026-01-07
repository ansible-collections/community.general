# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from functools import wraps

from ansible.module_utils.common.collections import is_sequence

if t.TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    ArgFormatType = Callable[[t.Any], Sequence[t.Any]]
    _T = t.TypeVar("_T")


def _ensure_list(value: _T | Sequence[_T]) -> list[_T]:
    return list(value) if is_sequence(value) else [value]  # type: ignore # TODO need type assertion for is_sequence


class _ArgFormat:
    def __init__(
        self,
        func: ArgFormatType,
        ignore_none: bool | None = True,
        ignore_missing_value: bool = False,
    ) -> None:
        self.func = func
        self.ignore_none = ignore_none
        self.ignore_missing_value = ignore_missing_value

    def __call__(self, value: t.Any | None) -> list[str]:
        ignore_none = self.ignore_none if self.ignore_none is not None else True
        if value is None and ignore_none:
            return []
        f = self.func
        return [str(x) for x in f(value)]

    def __str__(self) -> str:
        return f"<ArgFormat: func={self.func}, ignore_none={self.ignore_none}, ignore_missing_value={self.ignore_missing_value}>"

    def __repr__(self) -> str:
        return str(self)


def as_bool(
    args_true: Sequence[t.Any] | t.Any,
    args_false: Sequence[t.Any] | t.Any | None = None,
    ignore_none: bool | None = None,
) -> _ArgFormat:
    if args_false is not None:
        if ignore_none is None:
            ignore_none = False
    else:
        args_false = []
    return _ArgFormat(
        lambda value: _ensure_list(args_true) if value else _ensure_list(args_false), ignore_none=ignore_none
    )


def as_bool_not(args: Sequence[t.Any] | t.Any) -> _ArgFormat:
    return as_bool([], args, ignore_none=False)


def as_optval(arg, ignore_none: bool | None = None) -> _ArgFormat:
    return _ArgFormat(lambda value: [f"{arg}{value}"], ignore_none=ignore_none)


def as_opt_val(arg: str, ignore_none: bool | None = None) -> _ArgFormat:
    return _ArgFormat(lambda value: [arg, value], ignore_none=ignore_none)


def as_opt_eq_val(arg: str, ignore_none: bool | None = None) -> _ArgFormat:
    return _ArgFormat(lambda value: [f"{arg}={value}"], ignore_none=ignore_none)


def as_list(ignore_none: bool | None = None, min_len: int = 0, max_len: int | None = None) -> _ArgFormat:
    def func(value: t.Any) -> list[t.Any]:
        value = _ensure_list(value)
        if len(value) < min_len:
            raise ValueError(f"Parameter must have at least {min_len} element(s)")
        if max_len is not None and len(value) > max_len:
            raise ValueError(f"Parameter must have at most {max_len} element(s)")
        return value

    return _ArgFormat(func, ignore_none=ignore_none)


def as_fixed(*args: t.Any) -> _ArgFormat:
    if len(args) == 1 and is_sequence(args[0]):
        args = args[0]
    return _ArgFormat(lambda value: _ensure_list(args), ignore_none=False, ignore_missing_value=True)


def as_func(func: ArgFormatType, ignore_none: bool | None = None) -> _ArgFormat:
    return _ArgFormat(func, ignore_none=ignore_none)


def as_map(
    _map: Mapping[t.Any, Sequence[t.Any] | t.Any],
    default: Sequence[t.Any] | t.Any | None = None,
    ignore_none: bool | None = None,
) -> _ArgFormat:
    if default is None:
        default = []
    return _ArgFormat(lambda value: _ensure_list(_map.get(value, default)), ignore_none=ignore_none)


def unpack_args(func):
    @wraps(func)
    def wrapper(v):
        return func(*v)

    return wrapper


def unpack_kwargs(func):
    @wraps(func)
    def wrapper(v):
        return func(**v)

    return wrapper


def stack(fmt):
    @wraps(fmt)
    def wrapper(*args, **kwargs):
        new_func = fmt(ignore_none=True, *args, **kwargs)

        def stacking(value):
            stack = [new_func(v) for v in value if v]
            stack = [x for args in stack for x in args]
            return stack

        return _ArgFormat(stacking, ignore_none=True)

    return wrapper


def is_argformat(fmt: object) -> t.TypeGuard[_ArgFormat]:
    return isinstance(fmt, _ArgFormat)

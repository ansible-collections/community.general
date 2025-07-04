# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import wraps

from ansible.module_utils.common.collections import is_sequence


def _ensure_list(value):
    return list(value) if is_sequence(value) else [value]


class _ArgFormat(object):
    # DEPRECATION: set default value for ignore_none to True in community.general 12.0.0
    def __init__(self, func, ignore_none=None, ignore_missing_value=False):
        self.func = func
        self.ignore_none = ignore_none
        self.ignore_missing_value = ignore_missing_value

    # DEPRECATION: remove parameter ctx_ignore_none in community.general 12.0.0
    def __call__(self, value, ctx_ignore_none=True):
        # DEPRECATION: replace ctx_ignore_none with True in community.general 12.0.0
        ignore_none = self.ignore_none if self.ignore_none is not None else ctx_ignore_none
        if value is None and ignore_none:
            return []
        f = self.func
        return [str(x) for x in f(value)]

    def __str__(self):
        return "<ArgFormat: func={0}, ignore_none={1}, ignore_missing_value={2}>".format(
            self.func,
            self.ignore_none,
            self.ignore_missing_value,
        )

    def __repr__(self):
        return str(self)


def as_bool(args_true, args_false=None, ignore_none=None):
    if args_false is not None:
        if ignore_none is None:
            ignore_none = False
    else:
        args_false = []
    return _ArgFormat(lambda value: _ensure_list(args_true) if value else _ensure_list(args_false), ignore_none=ignore_none)


def as_bool_not(args):
    return as_bool([], args, ignore_none=False)


def as_optval(arg, ignore_none=None):
    return _ArgFormat(lambda value: ["{0}{1}".format(arg, value)], ignore_none=ignore_none)


def as_opt_val(arg, ignore_none=None):
    return _ArgFormat(lambda value: [arg, value], ignore_none=ignore_none)


def as_opt_eq_val(arg, ignore_none=None):
    return _ArgFormat(lambda value: ["{0}={1}".format(arg, value)], ignore_none=ignore_none)


def as_list(ignore_none=None, min_len=0, max_len=None):
    def func(value):
        value = _ensure_list(value)
        if len(value) < min_len:
            raise ValueError("Parameter must have at least {0} element(s)".format(min_len))
        if max_len is not None and len(value) > max_len:
            raise ValueError("Parameter must have at most {0} element(s)".format(max_len))
        return value
    return _ArgFormat(func, ignore_none=ignore_none)


def as_fixed(*args):
    if len(args) == 1 and is_sequence(args[0]):
        args = args[0]
    return _ArgFormat(lambda value: _ensure_list(args), ignore_none=False, ignore_missing_value=True)


def as_func(func, ignore_none=None):
    return _ArgFormat(func, ignore_none=ignore_none)


def as_map(_map, default=None, ignore_none=None):
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


def is_argformat(fmt):
    return isinstance(fmt, _ArgFormat)

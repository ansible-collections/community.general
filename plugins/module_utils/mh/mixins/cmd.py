# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import partial


class ArgFormat(object):
    """
    Argument formatter for use as a command line parameter. Used in CmdMixin.
    """
    BOOLEAN = 0
    PRINTF = 1
    FORMAT = 2
    BOOLEAN_NOT = 3

    @staticmethod
    def stars_deco(num):
        if num == 1:
            def deco(f):
                return lambda v: f(*v)
            return deco
        elif num == 2:
            def deco(f):
                return lambda v: f(**v)
            return deco

        return lambda f: f

    def __init__(self, name, fmt=None, style=FORMAT, stars=0):
        """
        THIS CLASS IS BEING DEPRECATED.
        It was never meant to be used outside the scope of CmdMixin, and CmdMixin is being deprecated.
        See the deprecation notice in ``CmdMixin.__init__()`` below.

        Creates a CLI-formatter for one specific argument. The argument may be a module parameter or just a named parameter for
        the CLI command execution.
        :param name: Name of the argument to be formatted
        :param fmt: Either a str to be formatted (using or not printf-style) or a callable that does that
        :param style: Whether arg_format (as str) should use printf-style formatting.
                             Ignored if arg_format is None or not a str (should be callable).
        :param stars: A int with 0, 1 or 2 value, indicating to formatting the value as: value, *value or **value
        """
        def printf_fmt(_fmt, v):
            try:
                return [_fmt % v]
            except TypeError as e:
                if e.args[0] != 'not all arguments converted during string formatting':
                    raise
                return [_fmt]

        _fmts = {
            ArgFormat.BOOLEAN: lambda _fmt, v: ([_fmt] if bool(v) else []),
            ArgFormat.BOOLEAN_NOT: lambda _fmt, v: ([] if bool(v) else [_fmt]),
            ArgFormat.PRINTF: printf_fmt,
            ArgFormat.FORMAT: lambda _fmt, v: [_fmt.format(v)],
        }

        self.name = name
        self.stars = stars
        self.style = style

        if fmt is None:
            fmt = "{0}"
            style = ArgFormat.FORMAT

        if isinstance(fmt, str):
            func = _fmts[style]
            self.arg_format = partial(func, fmt)
        elif isinstance(fmt, list) or isinstance(fmt, tuple):
            self.arg_format = lambda v: [_fmts[style](f, v)[0] for f in fmt]
        elif hasattr(fmt, '__call__'):
            self.arg_format = fmt
        else:
            raise TypeError('Parameter fmt must be either: a string, a list/tuple of '
                            'strings or a function: type={0}, value={1}'.format(type(fmt), fmt))

        if stars:
            self.arg_format = (self.stars_deco(stars))(self.arg_format)

    def to_text(self, value):
        if value is None and self.style != ArgFormat.BOOLEAN_NOT:
            return []
        func = self.arg_format
        return [str(p) for p in func(value)]

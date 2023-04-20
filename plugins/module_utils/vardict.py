# -*- coding: utf-8 -*-
# (c) 2023, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2023, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import copy


class _Variable(object):
    NOTHING = object()

    def __init__(self, diff=False, output=True, change=None, fact=False, verbosity=0):
        self.init = False
        self.initial_value = None
        self.value = None

        self.diff = diff
        self.change = diff if change is None else change
        self.output = output
        self.fact = fact
        self._verbosity = 0
        self._set_verbosity(verbosity)

    @property
    def verbosity(self):
        return self._verbosity

    def _set_verbosity(self, v):
        if not (0 <= v <= 4):
            raise ValueError("verbosity must be an int in the range 0 to 4")
        self._verbosity = v

    def set(self, diff=None, output=None, change=None, fact=None, initial_value=NOTHING, verbosity=None):
        if diff is not None:
            self.diff = diff
        if output is not None:
            self.output = output
        if change is not None:
            self.change = change
        if fact is not None:
            self.fact = fact
        if initial_value is not _Variable.NOTHING:
            self.initial_value = copy.deepcopy(initial_value)
        if verbosity is not None:
            self._set_verbosity(verbosity)

    def set_value(self, value):
        if not self.init:
            self.initial_value = copy.deepcopy(value)
            self.init = True
        self.value = value
        return self

    def is_visible(self, verbosity):
        return self.verbosity <= verbosity

    @property
    def has_changed(self):
        return self.change and (self.initial_value != self.value)

    @property
    def diff_result(self):
        if not (self.diff and self.has_changed):
            return
        return {'before': self.initial_value, 'after': self.value}

    def __str__(self):
        return "<_Variable: value={0}, initial={1}, diff={2}, output={3}, change={4}, verbosity={5}>".format(
            self.value, self.initial_value, self.diff, self.output, self.change, self.verbosity
        )


class VarDict(object):
    reserved_names = ('__vars__', 'var', 'set_meta', 'set', 'output', 'diff', 'facts', 'change_vars', 'has_changed')

    def __init__(self):
        self.__vars__ = dict()

    def __getitem__(self, item):
        return self.__vars__[item].value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getattr__(self, item):
        try:
            return self.__vars__[item].value
        except KeyError:
            return getattr(super(VarDict, self), item)

    def __setattr__(self, key, value):
        if key == '__vars__':
            super(VarDict, self).__setattr__(key, value)
        else:
            self.set(key, value)

    def var(self, name):
        return self.__vars__[name]

    def set_meta(self, name, **kwargs):
        self.var(name).set(**kwargs)

    def set(self, name, value, **kwargs):
        if name in self.reserved_names:
            raise ValueError("Name {0} is reserved".format(name))
        if name in self.__vars__:
            meta = self.var(name)
            meta.set(**kwargs)
        else:
            meta = _Variable(**kwargs)
        meta.set_value(value)
        self.__vars__[name] = meta

    def output(self, verbosity=0):
        return dict((n, v.value) for n, v in self.__vars__.items() if v.output and v.is_visible(verbosity))

    def diff(self, verbosity=0):
        diff_results = [(n, v.diff_result) for n, v in self.__vars__.items() if v.diff_result and v.is_visible(verbosity)]
        if diff_results:
            before = dict((n, dr['before']) for n, dr in diff_results)
            after = dict((n, dr['after']) for n, dr in diff_results)
            return {'before': before, 'after': after}
        return None

    def facts(self):
        facts_result = dict((n, v.value) for n, v in self.__vars__.items() if v.fact)
        return facts_result if facts_result else None

    def change_vars(self):
        return [m.value for m in self.__vars__ if m.change]

    def has_changed(self, v):
        return self.__vars__[v].has_changed

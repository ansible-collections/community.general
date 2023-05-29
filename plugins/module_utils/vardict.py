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

        self.diff = None
        self._change = None
        self.output = None
        self.fact = None
        self._verbosity = None
        self.set_meta(output=output, diff=diff, change=change, fact=fact, verbosity=verbosity)

    def getchange(self):
        return self.diff if self._change is None else self._change

    def setchange(self, value):
        self._change = value

    def getverbosity(self):
        return self._verbosity

    def setverbosity(self, v):
        if not (0 <= v <= 4):
            raise ValueError("verbosity must be an int in the range 0 to 4")
        self._verbosity = v

    change = property(getchange, setchange)
    verbosity = property(getverbosity, setverbosity)

    def set_meta(self, output=None, diff=None, change=None, fact=None, initial_value=NOTHING, verbosity=None):
        """Set the metadata for the variable

        Args:
            output (bool, optional): flag indicating whether the variable should be in the output of the module. Defaults to None.
            diff (bool, optional): flag indicating whether to generate diff mode output for this variable. Defaults to None.
            change (bool, optional): flag indicating whether to track if changes happened to this variable. Defaults to None.
            fact (bool, optional): flag indicating whether the varaiable should be exposed as a fact of the module. Defaults to None.
            initial_value (any, optional): initial value of the variable, to be used with `change`. Defaults to NOTHING.
            verbosity (int, optional): level of verbosity in which this variable is reported by the module as `output`, `fact` or `diff`. Defaults to None.
        """
        if output is not None:
            self.output = output
        if change is not None:
            self.change = change
        if diff is not None:
            self.diff = diff
        if fact is not None:
            self.fact = fact
        if initial_value is not _Variable.NOTHING:
            self.initial_value = copy.deepcopy(initial_value)
        if verbosity is not None:
            self.verbosity = verbosity

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
        if self.diff and self.has_changed:
            return {'before': self.initial_value, 'after': self.value}
        return

    def __str__(self):
        return "<_Variable: value={0!r}, initial={1!r}, diff={2}, output={3}, change={4}, verbosity={5}>".format(
            self.value, self.initial_value, self.diff, self.output, self.change, self.verbosity
        )


class VarDict(object):
    reserved_names = ('__vars__', 'var', 'set_meta', 'set', 'output', 'diff', 'facts', 'has_changed')

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

    def _var(self, name):
        return self.__vars__[name]

    def set_meta(self, name, **kwargs):
        """Set the metadata for the variable

        Args:
            name (str): name of the variable having its metadata changed
            output (bool, optional): flag indicating whether the variable should be in the output of the module. Defaults to None.
            diff (bool, optional): flag indicating whether to generate diff mode output for this variable. Defaults to None.
            change (bool, optional): flag indicating whether to track if changes happened to this variable. Defaults to None.
            fact (bool, optional): flag indicating whether the varaiable should be exposed as a fact of the module. Defaults to None.
            initial_value (any, optional): initial value of the variable, to be used with `change`. Defaults to NOTHING.
            verbosity (int, optional): level of verbosity in which this variable is reported by the module as `output`, `fact` or `diff`. Defaults to None.
        """
        self._var(name).set_meta(**kwargs)

    def set(self, name, value, **kwargs):
        """Set the value and optionally metadata for a variable. The variable is not required to exist prior to calling `set`.

        For details on the accepted metada see the documentation for method `set_meta`.

        Args:
            name (str): name of the variable being changed
            value (any): the value of the variable, it can be of any type

        Raises:
            ValueError: Raised if trying to set a variable with a reserved name.
        """
        if name in self.reserved_names:
            raise ValueError("Name {0} is reserved".format(name))
        if name in self.__vars__:
            var = self._var(name)
            var.set_meta(**kwargs)
        else:
            var = _Variable(**kwargs)
        var.set_value(value)
        self.__vars__[name] = var

    def output(self, verbosity=0):
        return dict((n, v.value) for n, v in self.__vars__.items() if v.output and v.is_visible(verbosity))

    def diff(self, verbosity=0):
        diff_results = [(n, v.diff_result) for n, v in self.__vars__.items() if v.diff_result and v.is_visible(verbosity)]
        if diff_results:
            before = dict((n, dr['before']) for n, dr in diff_results)
            after = dict((n, dr['after']) for n, dr in diff_results)
            return {'before': before, 'after': after}
        return None

    def facts(self, verbosity=0):
        facts_result = dict((n, v.value) for n, v in self.__vars__.items() if v.fact and v.is_visible(verbosity))
        return facts_result if facts_result else None

    @property
    def has_changed(self):
        return any(True for var in self.__vars__.values() if var.has_changed)

    def as_dict(self):
        return dict((name, var.value) for name, var in self.__vars__.items())

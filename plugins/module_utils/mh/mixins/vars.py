# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import copy


class VarMeta(object):
    NOTHING = object()

    def __init__(self, diff=False, output=True, change=None, fact=False):
        self.init = False
        self.initial_value = None
        self.value = None

        self.diff = diff
        self.change = diff if change is None else change
        self.output = output
        self.fact = fact

    def set(self, diff=None, output=None, change=None, fact=None, initial_value=NOTHING):
        if diff is not None:
            self.diff = diff
        if output is not None:
            self.output = output
        if change is not None:
            self.change = change
        if fact is not None:
            self.fact = fact
        if initial_value is not self.NOTHING:
            self.initial_value = copy.deepcopy(initial_value)

    def set_value(self, value):
        if not self.init:
            self.initial_value = copy.deepcopy(value)
            self.init = True
        self.value = value
        return self

    @property
    def has_changed(self):
        return self.change and (self.initial_value != self.value)

    @property
    def diff_result(self):
        return None if not (self.diff and self.has_changed) else {
            'before': self.initial_value,
            'after': self.value,
        }

    def __str__(self):
        return "<VarMeta: value={0}, initial={1}, diff={2}, output={3}, change={4}>".format(
            self.value, self.initial_value, self.diff, self.output, self.change
        )


class VarDict(object):
    def __init__(self):
        self._data = dict()
        self._meta = dict()

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            return getattr(self._data, item)

    def __setattr__(self, key, value):
        if key in ('_data', '_meta'):
            super(VarDict, self).__setattr__(key, value)
        else:
            self.set(key, value)

    def meta(self, name):
        return self._meta[name]

    def set_meta(self, name, **kwargs):
        self.meta(name).set(**kwargs)

    def set(self, name, value, **kwargs):
        if name in ('_data', '_meta'):
            raise ValueError("Names _data and _meta are reserved for use by ModuleHelper")
        self._data[name] = value
        if name in self._meta:
            meta = self.meta(name)
        else:
            meta = VarMeta(**kwargs)
        meta.set_value(value)
        self._meta[name] = meta

    def output(self):
        return dict((k, v) for k, v in self._data.items() if self.meta(k).output)

    def diff(self):
        diff_results = [(k, self.meta(k).diff_result) for k in self._data]
        diff_results = [dr for dr in diff_results if dr[1] is not None]
        if diff_results:
            before = dict((dr[0], dr[1]['before']) for dr in diff_results)
            after = dict((dr[0], dr[1]['after']) for dr in diff_results)
            return {'before': before, 'after': after}
        return None

    def facts(self):
        facts_result = dict((k, v) for k, v in self._data.items() if self._meta[k].fact)
        return facts_result if facts_result else None

    def change_vars(self):
        return [v for v in self._data if self.meta(v).change]

    def has_changed(self, v):
        return self._meta[v].has_changed


class VarsMixin(object):

    def __init__(self, module=None):
        self.vars = VarDict()
        super(VarsMixin, self).__init__(module)

    def update_vars(self, meta=None, **kwargs):
        if meta is None:
            meta = {}
        for k, v in kwargs.items():
            self.vars.set(k, v, **meta)

# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2022, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import traceback
from contextlib import contextmanager

from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.basic import missing_required_lib


_deps = dict()


class _Dependency(object):
    _states = ["pending", "failure", "success"]

    def __init__(self, name, reason=None, url=None, msg=None):
        self.name = name
        self.reason = reason
        self.url = url
        self.msg = msg

        self.state = 0
        self.trace = None
        self.exc = None

    def succeed(self):
        self.state = 2

    def fail(self, exc, trace):
        self.state = 1
        self.exc = exc
        self.trace = trace

    @property
    def message(self):
        if self.msg:
            return to_native(self.msg)
        else:
            return missing_required_lib(self.name, reason=self.reason, url=self.url)

    @property
    def failed(self):
        return self.state == 1

    def validate(self, module):
        if self.failed:
            module.fail_json(msg=self.message, exception=self.trace)

    def __str__(self):
        return "<dependency: {0} [{1}]>".format(self.name, self._states[self.state])


@contextmanager
def declare(name, *args, **kwargs):
    dep = _Dependency(name, *args, **kwargs)
    try:
        yield dep
    except Exception as e:
        dep.fail(e, traceback.format_exc())
    else:
        dep.succeed()
    finally:
        _deps[name] = dep


def _select_names(spec):
    dep_names = sorted(_deps)

    if spec:
        if spec.startswith("-"):
            spec_split = spec[1:].split(":")
            for d in spec_split:
                dep_names.remove(d)
        else:
            spec_split = spec.split(":")
            dep_names = []
            for d in spec_split:
                _deps[d]  # ensure it exists
                dep_names.append(d)

    return dep_names


def validate(module, spec=None):
    for dep in _select_names(spec):
        _deps[dep].validate(module)


def failed(spec=None):
    return any(_deps[d].failed for d in _select_names(spec))


def clear():
    _deps.clear()

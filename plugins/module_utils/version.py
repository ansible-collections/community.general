# -*- coding: utf-8 -*-

# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Provide version object to compare version numbers."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import operator
from functools import wraps
from collections import UserDict

from ansible.module_utils.compat.version import LooseVersion  # noqa: F401, pylint: disable=unused-import


def _version_compare(op):
    @wraps(op)
    def _op(a, b):
        return op(LooseVersion(a), LooseVersion(b))
    return _op


version_ops = UserDict({
    '<=': _version_compare(operator.le),
    '>=': _version_compare(operator.ge),
    '<': _version_compare(operator.lt),
    '>': _version_compare(operator.gt),
    '==': _version_compare(operator.eq),
    '!=': _version_compare(operator.ne),
})

setattr(version_ops, "le", version_ops["<="])
setattr(version_ops, "ge", version_ops[">="])
setattr(version_ops, "lt", version_ops["<"])
setattr(version_ops, "gt", version_ops[">"])
setattr(version_ops, "eq", version_ops["=="])
setattr(version_ops, "ne", version_ops["!="])


def find_op(name):
    if name is None:
        return None, None, None
    for op in version_ops:
        if op in name:
            n, v = name.split(op)
            return n, op, v
    return None, None, None


def name_version_assert(name, existing_version):
    name_, op, op_version = find_op(name)
    if not op:
        return True
    return version_ops[op](existing_version, op_version)

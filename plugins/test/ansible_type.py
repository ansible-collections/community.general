# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = """
name: ansible_type
short_description: Validate input type
version_added: "9.2.0"
author: Vladimir Botka (@vbotka)
description: This test validates input type.
options:
  _input:
    description: Input data.
    type: raw
    required: true
  dtype:
    description: A single data type, or a data types list to be validated.
    type: raw
    required: true
  alias:
    description: Data type aliases.
    default: {}
    type: dictionary
"""

EXAMPLES = """
# Substitution converts str to AnsibleUnicode or _AnsibleTaggedStr
# ----------------------------------------------------------------

---
# String. AnsibleUnicode or _AnsibleTaggedStr.
dtype:
  - AnsibleUnicode
  - _AnsibleTaggedStr
data: "abc"
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

---
# String. AnsibleUnicode/_AnsibleTaggedStr alias str.
alias: {"AnsibleUnicode": "str", "_AnsibleTaggedStr": "str"}
dtype: str
data: "abc"
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

---
# List. All items are AnsibleUnicode/_AnsibleTaggedStr.
dtype:
  - list[AnsibleUnicode]
  - list[_AnsibleTaggedStr]
data: ["a", "b", "c"]
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

---
# Dictionary. All keys and values are AnsibleUnicode/_AnsibleTaggedStr.
dtype:
  - dict[AnsibleUnicode, AnsibleUnicode]
  - dict[_AnsibleTaggedStr, _AnsibleTaggedStr]
data: {"a": "foo", "b": "bar", "c": "baz"}
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

# No substitution and no alias. Type of strings is str
# ----------------------------------------------------

---
# String
dtype: str
result: '{{ "abc" is community.general.ansible_type(dtype) }}'
# result => true

---
# Integer
dtype: int
result: '{{ 123 is community.general.ansible_type(dtype) }}'
# result => true

---
# Float
dtype: float
result: '{{ 123.45 is community.general.ansible_type(dtype) }}'
# result => true

---
# Boolean
dtype: bool
result: '{{ true is community.general.ansible_type(dtype) }}'
# result => true

---
# List. All items are strings.
dtype: list[str]
result: '{{ ["a", "b", "c"] is community.general.ansible_type(dtype) }}'
# result => true

---
# List of dictionaries.
dtype: list[dict]
result: '{{ [{"a": 1}, {"b": 2}] is community.general.ansible_type(dtype) }}'
# result => true

---
# Dictionary. All keys are strings. All values are integers.
dtype: dict[str, int]
result: '{{ {"a": 1} is community.general.ansible_type(dtype) }}'
# result => true

---
# Dictionary. All keys are strings. All values are integers.
dtype: dict[str, int]
result: '{{ {"a": 1, "b": 2} is community.general.ansible_type(dtype) }}'
# result => true

# Type of strings is AnsibleUnicode, _AnsibleTaggedStr, or str
# ------------------------------------------------------------

---
# Dictionary. The keys are integers or strings. All values are strings.
alias:
  AnsibleUnicode: str
  _AnsibleTaggedStr: str
  _AnsibleTaggedInt: int
dtype: dict[int|str, str]
data: {1: 'a', 'b': 'b'}
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

---
# Dictionary. All keys are integers. All values are keys.
alias:
  AnsibleUnicode: str
  _AnsibleTaggedStr: str
  _AnsibleTaggedInt: int
dtype: dict[int, str]
data: {1: 'a', 2: 'b'}
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

---
# Dictionary. All keys are strings. Multiple types values.
alias:
  AnsibleUnicode: str
  _AnsibleTaggedStr: str
  _AnsibleTaggedInt: int
  _AnsibleTaggedFloat: float
dtype: dict[str, bool|dict|float|int|list|str]
data: {'a': 1, 'b': 1.1, 'c': 'abc', 'd': true, 'e': ['x', 'y', 'z'], 'f': {'x': 1, 'y': 2}}
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

---
# List. Multiple types items.
alias:
  AnsibleUnicode: str
  _AnsibleTaggedStr: str
  _AnsibleTaggedInt: int
  _AnsibleTaggedFloat: float
dtype: list[bool|dict|float|int|list|str]
data: [1, 2, 1.1, 'abc', true, ['x', 'y', 'z'], {'x': 1, 'y': 2}]
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

# Option dtype is list
# --------------------

---
# AnsibleUnicode, _AnsibleTaggedStr, or str
dtype: ['AnsibleUnicode', '_AnsibleTaggedStr', 'str']
data: abc
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

---
# float or int
dtype: ['float', 'int', "_AnsibleTaggedInt", "_AnsibleTaggedFloat"]
data: 123
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

---
# float or int
dtype: ['float', 'int', "_AnsibleTaggedInt", "_AnsibleTaggedFloat"]
data: 123.45
result: '{{ data is community.general.ansible_type(dtype) }}'
# result => true

# Multiple alias
# --------------

---
# int alias number
alias:
  int: number
  float: number
  _AnsibleTaggedInt: number
  _AnsibleTaggedFloat: float
dtype: number
data: 123
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true

---
# float alias number
alias:
  int: number
  float: number
  _AnsibleTaggedInt: number
  _AnsibleTaggedFloat: float
dtype: number
data: 123.45
result: '{{ data is community.general.ansible_type(dtype, alias) }}'
# result => true
"""

RETURN = """
_value:
  description: Whether the data type is valid.
  type: bool
"""

from collections.abc import Sequence

from ansible.errors import AnsibleFilterError
from ansible_collections.community.general.plugins.plugin_utils.ansible_type import _ansible_type


def ansible_type(data, dtype, alias=None):
    """Validates data type"""

    if not isinstance(dtype, Sequence):
        msg = "The argument dtype must be a string or a list. dtype is %s."
        raise AnsibleFilterError(msg % (dtype, type(dtype)))

    if isinstance(dtype, str):
        data_types = [dtype]
    else:
        data_types = dtype

    # TODO: expose use_native_type parameter
    return _ansible_type(data, alias) in data_types


class TestModule:
    def tests(self):
        return {"ansible_type": ansible_type}

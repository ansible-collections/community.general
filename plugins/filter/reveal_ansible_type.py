# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: reveal_ansible_type
short_description: Return input type
version_added: "9.2.0"
author: Vladimir Botka (@vbotka)
description: This filter returns input type.
options:
  _input:
    description: Input data.
    type: raw
    required: true
  alias:
    description: Data type aliases.
    default: {}
    type: dictionary
"""

EXAMPLES = r"""
# Substitution converts str to AnsibleUnicode or _AnsibleTaggedStr
# ----------------------------------------------------------------

# String. AnsibleUnicode or _AnsibleTaggedStr.
- data: "abc"
  result: '{{ data | community.general.reveal_ansible_type }}'
# result => AnsibleUnicode (or _AnsibleTaggedStr)

# String. AnsibleUnicode/_AnsibleTaggedStr alias str.
- alias: {"AnsibleUnicode": "str", "_AnsibleTaggedStr": "str"}
  data: "abc"
  result: '{{ data | community.general.reveal_ansible_type(alias) }}'
# result => str

# List. All items are AnsibleUnicode/_AnsibleTaggedStr.
- data: ["a", "b", "c"]
  result: '{{ data | community.general.reveal_ansible_type }}'
# result => list[AnsibleUnicode] or list[_AnsibleTaggedStr]

# Dictionary. All keys and values are AnsibleUnicode/_AnsibleTaggedStr.
- data: {"a": "foo", "b": "bar", "c": "baz"}
  result: '{{ data | community.general.reveal_ansible_type }}'
# result => dict[AnsibleUnicode, AnsibleUnicode] or dict[_AnsibleTaggedStr, _AnsibleTaggedStr]

# No substitution and no alias. Type of strings is str
# ----------------------------------------------------

# String
- result: '{{ "abc" | community.general.reveal_ansible_type }}'
# result => str

# Integer
- result: '{{ 123 | community.general.reveal_ansible_type }}'
# result => int

# Float
- result: '{{ 123.45 | community.general.reveal_ansible_type }}'
# result => float

# Boolean
- result: '{{ true | community.general.reveal_ansible_type }}'
# result => bool

# List. All items are strings.
- result: '{{ ["a", "b", "c"] | community.general.reveal_ansible_type }}'
# result => list[str]

# List of dictionaries.
- result: '{{ [{"a": 1}, {"b": 2}] | community.general.reveal_ansible_type }}'
# result => list[dict]

# Dictionary. All keys are strings. All values are integers.
- result: '{{ {"a": 1} | community.general.reveal_ansible_type }}'
# result => dict[str, int]

# Dictionary. All keys are strings. All values are integers.
- result: '{{ {"a": 1, "b": 2} | community.general.reveal_ansible_type }}'
# result => dict[str, int]

# Type of strings is AnsibleUnicode, _AnsibleTaggedStr, or str
# ------------------------------------------------------------

# Dictionary. The keys are integers or strings. All values are strings.
- alias:
    AnsibleUnicode: str
    _AnsibleTaggedStr: str
    _AnsibleTaggedInt: int
  data: {1: 'a', 'b': 'b'}
  result: '{{ data | community.general.reveal_ansible_type(alias) }}'
# result => dict[int|str, str]

# Dictionary. All keys are integers. All values are keys.
- alias:
    AnsibleUnicode: str
    _AnsibleTaggedStr: str
    _AnsibleTaggedInt: int
  data: {1: 'a', 2: 'b'}
  result: '{{ data | community.general.reveal_ansible_type(alias) }}'
# result => dict[int, str]

# Dictionary. All keys are strings. Multiple types values.
- alias:
    AnsibleUnicode: str
    _AnsibleTaggedStr: str
    _AnsibleTaggedInt: int
    _AnsibleTaggedFloat: float
  data: {'a': 1, 'b': 1.1, 'c': 'abc', 'd': true, 'e': ['x', 'y', 'z'], 'f': {'x': 1, 'y': 2}}
  result: '{{ data | community.general.reveal_ansible_type(alias) }}'
# result => dict[str, bool|dict|float|int|list|str]

# List. Multiple types items.
- alias:
    AnsibleUnicode: str
    _AnsibleTaggedStr: str
    _AnsibleTaggedInt: int
    _AnsibleTaggedFloat: float
  data: [1, 2, 1.1, 'abc', true, ['x', 'y', 'z'], {'x': 1, 'y': 2}]
  result: '{{ data | community.general.reveal_ansible_type(alias) }}'
# result => list[bool|dict|float|int|list|str]
"""

RETURN = r"""
_value:
  description: Type of the data.
  type: str
"""

from ansible_collections.community.general.plugins.plugin_utils.ansible_type import _ansible_type


def reveal_ansible_type(data, alias=None):
    """Returns data type"""

    # TODO: expose use_native_type parameter
    return _ansible_type(data, alias)


class FilterModule:
    def filters(self):
        return {"reveal_ansible_type": reveal_ansible_type}

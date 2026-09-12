# Copyright (c) 2026, Lorenzo Tanganelli <lorenzo.tanganelli@hotmail.it>
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: remove_keys_from_values
short_description: Remove keys from a list of dictionaries or a dictionary based on value content
version_added: "13.5.0"
author:
  - Lorenzo Tanganelli (@tanganellilore)
description:
  - This filter removes keys from a list of dictionaries or a dictionary,
    recursively or not depending on the parameters.
  - The type of values to be removed is defined by the O(values) parameter.
options:
  _input:
    description:
      - A list of dictionaries or a dictionary.
    type: raw
    required: true
  values:
    description:
      - In equal mode, a single value or a list of values to remove.
      - In regex mode, a single regular expression or a list of regular expressions to match.
      - This option must be provided when O(matching_parameter=regex).
      - If this option is omitted in equal mode, keys with values V(''), V([]), V({}), and V(None) are removed,
        which is useful for removing empty keys.
    type: raw
    required: false
  recursive:
    description: Specify if the filter should be applied recursively.
    type: bool
    default: true
    required: false
  matching_parameter:
    description: Specify the matching option for values.
    type: str
    default: equal
    choices:
      equal: Matches values equal to any of the O(values) items.
      regex: Matches values that match one of the regular expressions provided in O(values).
"""

EXAMPLES = r"""
- name: Remove empty values from a list of dictionaries
  ansible.builtin.set_fact:
    my_list:
      - a: foo
        b: ''
        c: []
      - a: bar
        b: {}
        c: null
      - a: ok
        b: {}
        c: null
- name: Remove empty values by default
  ansible.builtin.debug:
    msg: "{{ my_list | community.general.remove_keys_from_values }}"
- name: Remove empty strings
  ansible.builtin.debug:
    msg: "{{ my_list | community.general.remove_keys_from_values(values='') }}"
- name: Remove all empty values
  ansible.builtin.debug:
    msg: "{{ my_list | community.general.remove_keys_from_values(values=['', [], {}, None]) }}"
- name: Remove all empty values without recursion
  ansible.builtin.debug:
    msg: "{{ my_list | community.general.remove_keys_from_values(values=['', [], {}, None], recursive=false) }}"
- name: Remove values from a list of dictionaries
  ansible.builtin.debug:
    msg: "{{ my_list | community.general.remove_keys_from_values(values=['foo', 'bar']) }}"

- name: Remove keys from a dictionary
  ansible.builtin.set_fact:
    my_dict:
      a: foo
      b: ''
      c: []
      d:
        - a: foo
          b: ''
          c: []
        - a: bar
          b: {}
          c: null
- name: Remove empty values from a dictionary
  ansible.builtin.debug:
    msg: "{{ my_dict | community.general.remove_keys_from_values }}"
# returns
# a: foo
# d:
#   - a: foo
#   - a: bar
- name: Remove empty strings from a dictionary
  ansible.builtin.debug:
    msg: "{{ my_dict | community.general.remove_keys_from_values(values='') }}"
# returns
# a: foo
# d:
#   - a: foo
#     c: []
#   - a: bar
#     b: {}
#     c: null
- name: Remove all empty values from the top level only
  ansible.builtin.debug:
    msg: "{{ my_dict | community.general.remove_keys_from_values(values=['', [], {}, None], recursive=false) }}"
# returns
# a: foo
# d:
#   - a: foo
#     b: ''
#     c: []
#   - a: bar
#     b: {}
#     c: null
- name: Remove foo and bar values from a dictionary
  ansible.builtin.debug:
    msg: "{{ my_dict | community.general.remove_keys_from_values(values=['foo', 'bar']) }}"
# returns
# b: ''
# c: []
# d:
#   - b: ''
#     c: []
#   - b: {}
#     c: null
"""

RETURN = r"""
_value:
  description: The list of dictionaries or the dictionary with the keys removed.
  returned: always
  type: raw
"""

import re

from ansible.errors import AnsibleFilterError


def remove_keys_from_values(data, values=None, recursive=True, matching_parameter="equal"):
    """
    Removes keys from dictionaries or lists of dictionaries
    if their values match the specified values or regex patterns.
    """

    if not isinstance(data, (dict, list)):
        raise AnsibleFilterError("Input must be a dictionary or a list.")

    if matching_parameter not in ("equal", "regex"):
        raise AnsibleFilterError("matching_parameter must be 'equal' or 'regex'")

    if matching_parameter == "regex" and values is None:
        raise AnsibleFilterError("values must be provided when matching_parameter='regex'")

    if values is None:
        values = ["", [], {}, None]
    elif not isinstance(values, list):
        values = [values]

    if matching_parameter == "regex":
        try:
            regex_patterns = [re.compile(v) for v in values]
        except re.error as error:
            raise AnsibleFilterError(f"Invalid regex pattern: {error}") from error

    def should_remove(val):
        if matching_parameter == "equal":
            return val in values
        if matching_parameter == "regex" and isinstance(val, str):
            return any(p.match(val) for p in regex_patterns)
        return False

    def clean(obj):
        if isinstance(obj, dict):
            return {
                k: clean(v) if recursive else v
                for k, v in obj.items()
                if not should_remove(clean(v) if recursive else v)
            }
        elif isinstance(obj, list):
            return [clean(i) if recursive else i for i in obj]
        return obj

    return clean(data)


class FilterModule:
    def filters(self):
        return {
            "remove_keys_from_values": remove_keys_from_values,
        }

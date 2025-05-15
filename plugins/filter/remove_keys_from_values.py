# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: remove_keys_from_values
short_description: Remove keys from a list of dictionaries or a dictionary in base of value content
version_added: "10.6.0"
author:
  - Lorenzo Tanganelli (@tanganellilore)
description:
  - This filter removes keys from a list of dictionaries or a dictionary,
  - recursively or not depending on the parameters.
  - The type of values to be removed is defined by the O(values) parameter.
  - The default is to remove keys with values like C(''), C([]), C({}), C(None), usefull for removing empty keys.
options:
  _input:
    description:
      - A list of dictionaries or a dictionary.
    type: raw
    elements: dictionary
    required: true
  values:
    description:
      - A single value or value pattern to remove, or a list of values or values patterns to remove.
      - If O(matching_parameter=regex) there must be equally one pattern provided.
    type: raw
    required: true
  recursive:
    description: Specify if the filter should be applied recursively.
    type: bool
    default: true
    required: false
  matching_parameter:
    description: Specify the matching option of target keys.
    type: str
    default: equal
    choices:
      equal: Matches keys of equally one of the O(target[].before) items.
      regex: Matches keys that match one of the regular expressions provided in O(target[].before).:
"""

EXAMPLES = r"""
- name: Remove empty keys from a list of dictionaries
  set_fact:
    my_list:
      - a: foo
        b: ''
        c: []
      - a: bar
        b: {}
        c: None
      - a: ok
        b: {}
        c: None
  - debug:
      msg: "{{ my_list | remove_empty_keys }}"
  - debug:
      msg: "{{ my_list | remove_empty_keys(values='') }}"
  - debug:
      msg: "{{ my_list | remove_empty_keys(values=['', [], {}, None]) }}"
  - debug:
      msg: "{{ my_list | remove_empty_keys(values=['', [], {}, None], recursive=False) }}"
  - debug:
      msg: "{{ my_list | remove_empty_keys(values=['foo', 'bar']) }}"

- name: Remove keys from a dictionary
  set_fact:
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
          c: None
  - debug:
      msg: "{{ my_dict | remove_empty_keys }}"
  # returns
  # a: foo
  # d:
  #   - a: foo
  #   - a: bar
  - debug:
      msg: "{{ my_dict | remove_empty_keys(values='') }}"
  # returns
  # a: foo
  # d:
  #   - a: foo
  #     c: []
  #   - a: bar
  #     b: {}
  #     c: None

  - debug:
      msg: "{{ my_dict | remove_empty_keys(values=['', [], {}, None], recursive=False) }}"
  # return
  # a: foo
  # d:
  #   - a: foo
  #   - a: bar

  - debug:
      msg: "{{ my_dict | remove_empty_keys(values=['foo', 'bar']) }}"
  # returns
  # b: ''
  # c: []
  # d:
  #   - b: ''
  #     c: []
  #   - b: {}
  #     c: None
"""

RETURN = r"""
_value:
  description: The list of dictionaries or the dictionary with the keys removed.
  returned: always
  type: raw
"""

import re
from ansible.errors import AnsibleFilterError


def remove_keys_from_value(data, values=None, recursive=True):
    """
    Removes keys from dictionaries or lists of dictionaries
    if their value matches any of the specified `values`.
    """
    # Default values to remove
    default_values = ['', [], {}, None]
    if values is None:
        values = default_values
    elif not isinstance(values, list):
        values = [values]

    def should_remove(val):
        return val in values

    def clean(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                val = clean(v) if recursive else v
                if not should_remove(val):
                    new_obj[k] = val
            return new_obj
        elif isinstance(obj, list):
            return [clean(item) if recursive else item for item in obj]
        else:
            return obj

    if isinstance(data, (dict, list)):
        return clean(data)
    else:
        raise AnsibleFilterError("Input must be a dictionary or list of dictionaries.")


def remove_keys_from_values(data, values=None, recursive=True, matching_parameter="equal"):
    """
    Removes keys from dictionaries or lists of dictionaries
    if their values match the specified values or regex patterns.
    """
    
    if not isinstance(data, (dict, list)):
        raise AnsibleFilterError("Input must be a dictionary or a list.")

    if matching_parameter not in ("equal", "regex"):
        raise AnsibleFilterError("matching_parameter must be 'equal' or 'regex'")

    values = values if isinstance(values, list) else [values or '', [], {}, None]

    regex_patterns = []
    if matching_parameter == "regex":
        try:
            regex_patterns = [re.compile(v) for v in values]
        except re.error as e:
            raise AnsibleFilterError(f"Invalid regex pattern: {e}")

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

class FilterModule(object):
    def filters(self):
        return {
            'remove_keys_from_values': remove_keys_from_values
        }

# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: remove_keys
    short_description: Remove specific keys from dictionaries in a list
    version_added: "9.1.0"
    author: Vladimir Botka (@vbotka)
    description: This filter removes only specified keys from a provided list of dictionaries.
    options:
      _input:
        description:
          - A list of dictionaries.
          - All keys must be strings.
        type: list
        elements: dictionary
        required: true
      target:
        description:
          - A list of keys or keys patterns to remove.
          - The interpretation of O(target) depends on the option O(matching_parameter)
          - Single item is required in O(target) list for O(matching_parameter=regex)
          - The O(target) can be a string for O(matching_parameter=regex)
        type: raw
        required: true
      matching_parameter:
        description: Specify the matching option of target keys.
        type: str
        default: equal
        choices:
          equal: Matches keys of exactly one of the O(target) items.
          starts_with: Matches keys that start with one of the O(target) items.
          ends_with: Matches keys that end with one of the O(target) items.
          regex:
            - Matches keys that match the regular expresion provided in O(target).
            - In this case, O(target) must be a regex string or a list with single regex string.
'''

EXAMPLES = '''
  l:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

  # By default match equal keys.
  t: [k0_x0, k1_x1]
  r: "{{ l | remove_keys(target=t) }}"

  # Match keys that starts with any of the items in the target.
  t: [k0, k1]
  r: "{{ l | remove_keys(target=t, matching_parameter='starts_with') }}"

  # Match keys that ends with any of the items in target.
  t: [x0, x1]
  r: "{{ l | remove_keys(target=t, matching_parameter='ends_with') }}"

  # Match keys by the regex.
  t: ['^.*[01]_x.*$']
  r: "{{ l | remove_keys(target=t, matching_parameter='regex') }}"

  # Match keys by the regex. The regex does not have to be in list.
  t: '^.*[01]_x.*$'
  r: "{{ l | remove_keys(target=t, matching_parameter='regex') }}"

  # The results of all examples are all the same.
  r:
    - {k2_x2: [C0], k3_x3: foo}
    - {k2_x2: [C1], k3_x3: bar}
'''

RETURN = '''
  _value:
    description: The list of dictionaries with selected keys.
    type: list
    elements: dictionary
'''

from ansible_collections.community.general.plugins.plugin_utils.keys_filter import (
    _keys_filter_params,
    _keys_filter_target_str)


def remove_keys(data, target=None, matching_parameter='equal'):
    """remove specific keys from dictionaries in a list"""

    # test parameters
    _keys_filter_params(data, target, matching_parameter)
    # test and transform target
    tt = _keys_filter_target_str(target, matching_parameter)

    if matching_parameter == 'equal':
        def keep_key(key):
            return key not in tt
    elif matching_parameter == 'starts_with':
        def keep_key(key):
            return not key.startswith(tt)
    elif matching_parameter == 'ends_with':
        def keep_key(key):
            return not key.endswith(tt)
    elif matching_parameter == 'regex':
        def keep_key(key):
            return tt.match(key) is None

    return [dict((k, v) for k, v in d.items() if keep_key(k)) for d in data]


class FilterModule(object):

    def filters(self):
        return {
            'remove_keys': remove_keys,
        }

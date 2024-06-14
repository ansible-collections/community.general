# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: replace_keys
    short_description: Replace specific keys in a list of dictionaries
    version_added: "9.1.0"
    author:
      - Vladimir Botka (@vbotka)
      - Felix Fontein (@felixfontein)
    description: This filter replaces specified keys in a provided list of dictionaries.
    options:
      _input:
        description:
          - A list of dictionaries.
          - Top level keys must be strings.
        type: list
        elements: dictionary
        required: true
      target:
        description:
          - A list of dictionaries with attributes C(before) and C(after).
          - The value of O(target[].after) replaces key matching O(target[].before).
        type: list
        elements: dictionary
        required: true
        suboptions:
          before:
            description:
              - A key or key pattern to change.
              - The interpretation of O(target[].before) depends on O(matching_parameter).
              - For a key that matches multiple O(target[].before)s, the B(first) matching O(target[].after) will be used.
            type: str
          after:
            description: A matching key change to.
            type: str
      matching_parameter:
        description: Specify the matching option of target keys.
        type: str
        default: equal
        choices:
          equal: Matches keys of exactly one of the O(target[].before) items.
          starts_with: Matches keys that start with one of the O(target[].before) items.
          ends_with: Matches keys that end with one of the O(target[].before) items.
          regex: Matches keys that match one of the regular expressions provided in O(target[].before).
'''

EXAMPLES = '''
  l:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

  # 1) By default, replace keys that are equal any of the attributes before.
  t:
    - {before: k0_x0, after: a0}
    - {before: k1_x1, after: a1}
  r: "{{ l | community.general.replace_keys(target=t) }}"

  # 2) Replace keys that starts with any of the attributes before.
  t:
    - {before: k0, after: a0}
    - {before: k1, after: a1}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='starts_with') }}"

  # 3) Replace keys that ends with any of the attributes before.
  t:
    - {before: x0, after: a0}
    - {before: x1, after: a1}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='ends_with') }}"

  # 4) Replace keys that match any regex of the attributes before.
  t:
    - {before: "^.*0_x.*$", after: a0}
    - {before: "^.*1_x.*$", after: a1}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='regex') }}"

  # The results of above examples 1-4 are all the same.
  r:
    - {a0: A0, a1: B0, k2_x2: [C0], k3_x3: foo}
    - {a0: A1, a1: B1, k2_x2: [C1], k3_x3: bar}

  # 5) If more keys match the same attribute before the last one will be used.
  t:
    - {before: "^.*_x.*$", after: X}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='regex') }}"

  # gives

  r:
    - X: foo
    - X: bar

  # 6) If there are items with equal attribute before the first one will be used.
  t:
    - {before: "^.*_x.*$", after: X}
    - {before: "^.*_x.*$", after: Y}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='regex') }}"

  # gives

  r:
    - X: foo
    - X: bar

  # 7) If there are more matches for a key the first one will be used.
  l:
    - {aaa1: A, bbb1: B, ccc1: C}
    - {aaa2: D, bbb2: E, ccc2: F}
  t:
    - {before: a, after: X}
    - {before: aa, after: Y}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='starts_with') }}"

  # gives

  r:
    - {X: A, bbb1: B, ccc1: C}
    - {X: D, bbb2: E, ccc2: F}
'''

RETURN = '''
  _value:
    description: The list of dictionaries with replaced keys.
    type: list
    elements: dictionary
'''

from ansible_collections.community.general.plugins.plugin_utils.keys_filter import (
    _keys_filter_params,
    _keys_filter_target_dict)


def replace_keys(data, target=None, matching_parameter='equal'):
    """replace specific keys in a list of dictionaries"""

    # test parameters
    _keys_filter_params(data, matching_parameter)
    # test and transform target
    tz = _keys_filter_target_dict(target, matching_parameter)

    if matching_parameter == 'equal':
        def replace_key(key):
            for b, a in tz:
                if key == b:
                    return a
            return key
    elif matching_parameter == 'starts_with':
        def replace_key(key):
            for b, a in tz:
                if key.startswith(b):
                    return a
            return key
    elif matching_parameter == 'ends_with':
        def replace_key(key):
            for b, a in tz:
                if key.endswith(b):
                    return a
            return key
    elif matching_parameter == 'regex':
        def replace_key(key):
            for b, a in tz:
                if b.match(key):
                    return a
            return key

    return [dict((replace_key(k), v) for k, v in d.items()) for d in data]


class FilterModule(object):

    def filters(self):
        return {
            'replace_keys': replace_keys,
        }

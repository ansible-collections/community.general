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
          - The value of C(after) replaces key matching C(before).
        type: list
        elements: dictionary
        required: true
        suboptions:
          before:
            description:
              - A key or key pattern to change.
              - The interpretation of C(before) depends on O(matching_parameter).
              - If more keys match the same C(before) the B(last) one will be used.
              - If there are items with equal C(before) the B(last) one will be used.
              - If there are more matches for a key the B(first) one will be used.
            type: str
          after:
            description: A matching key change to.
            type: str
      matching_parameter:
        description: Specify the matching option of target keys.
        type: str
        default: equal
        choices:
          equal: Matches keys of exactly one of the C(before) items.
          starts_with: Matches keys that start with one of the C(before) items.
          ends_with: Matches keys that end with one of the C(before) items.
          regex:  Matches keys that match one of the regular expresions provided in C(before).
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

  # 6) If there are items with equal attribute before the last one will be used.
  t:
    - {before: "^.*_x.*$", after: X}
    - {before: "^.*_x.*$", after: Y}
  r: "{{ l | community.general.replace_keys(target=t, matching_parameter='regex') }}"

  # gives

  r:
    - Y: foo
    - Y: bar

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
    _keys_filter_params(data, target, matching_parameter)
    # test and transform target
    td = _keys_filter_target_dict(target, matching_parameter)

    before = list(td.keys())
    index = 0  # If there are multiple matches take the first one.

    if matching_parameter == 'starts_with':
        def match_key(key, t):
            return key.startswith(t)
    elif matching_parameter == 'ends_with':
        def match_key(key, t):
            return key.endswith(t)
    elif matching_parameter == 'regex':
        def match_key(key, t):
            return t.match(key)

    # If matching_parameter is 'equal' there may be a single match only.
    if matching_parameter == 'equal':
        def replace_key(key):
            if key in before:
                return td[key]
            else:
                return key
    # Otherwise, there may be multiple matches. In this case, use index.
    else:
        def replace_key(key):
            rl = []
            for t in before:
                if match_key(key, t):
                    rl.append(td[t])
            if rl:
                return rl[index]
            else:
                return key

    return [dict((replace_key(k), v) for k, v in d.items()) for d in data]


class FilterModule(object):

    def filters(self):
        return {
            'replace_keys': replace_keys,
        }

# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: remove_keys
short_description: Remove specific keys from dictionaries in a list
version_added: "9.1.0"
author:
  - Vladimir Botka (@vbotka)
  - Felix Fontein (@felixfontein)
description: This filter removes only specified keys from a provided list of dictionaries.
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
      - A single key or key pattern to remove, or a list of keys or keys patterns to remove.
      - If O(matching_parameter=regex) there must be exactly one pattern provided.
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
"""

EXAMPLES = r"""
- l:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

  # 1) By default match keys that equal any of the items in the target.
- t: [k0_x0, k1_x1]
  r: "{{ l | community.general.remove_keys(target=t) }}"

  # 2) Match keys that start with any of the items in the target.
- t: [k0, k1]
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='starts_with') }}"

  # 3) Match keys that end with any of the items in target.
- t: [x0, x1]
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='ends_with') }}"

  # 4) Match keys by the regex.
- t: ['^.*[01]_x.*$']
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='regex') }}"

  # 5) Match keys by the regex.
- t: '^.*[01]_x.*$'
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='regex') }}"

  # The results of above examples 1-5 are all the same.
- r:
    - {k2_x2: [C0], k3_x3: foo}
    - {k2_x2: [C1], k3_x3: bar}

  # 6) By default match keys that equal the target.
- t: k0_x0
  r: "{{ l | community.general.remove_keys(target=t) }}"

  # 7) Match keys that start with the target.
- t: k0
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='starts_with') }}"

  # 8) Match keys that end with the target.
- t: x0
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='ends_with') }}"

  # 9) Match keys by the regex.
- t: '^.*0_x.*$'
  r: "{{ l | community.general.remove_keys(target=t, matching_parameter='regex') }}"

  # The results of above examples 6-9 are all the same.
- r:
    - {k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k1_x1: B1, k2_x2: [C1], k3_x3: bar}
"""

RETURN = r"""
_value:
  description: The list of dictionaries with selected keys removed.
  type: list
  elements: dictionary
"""

from ansible_collections.community.general.plugins.plugin_utils.keys_filter import (
    _keys_filter_params,
    _keys_filter_target_str)


def remove_keys(data, target=None, matching_parameter='equal'):
    """remove specific keys from dictionaries in a list"""

    # test parameters
    _keys_filter_params(data, matching_parameter)
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

    return [{k: v for k, v in d.items() if keep_key(k)} for d in data]


class FilterModule(object):

    def filters(self):
        return {
            'remove_keys': remove_keys,
        }

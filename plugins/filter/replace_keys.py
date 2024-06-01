# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: replace_keys
    short_description: Replace specific keys in a list of dictionaries.
    version_added: "2.17"
    author: Vladimir Botka (@vbotka)
    description: This filter replaces specified keys in a provided list of dictionaries.
    options:
      _input:
        description: A list of dictionaries.
        type: list
        elements: dictionary
        required: true
      target:
        description:
          - A list of dictionaries containing before and after key values.
          - The interpretation of the *before* keys depends on the option C(matching_parameter)
        type: list
        elements: dictionary
        required: true
        suboptions:
          before:
            description:
              - before attribute key [to change]
              - If before attributes are equal the C(last) one will be used.
              - If more keys match the same before attribute the C(last) key/value will be used.
              - If there are more matches for a key the C(first) one will be used.
            type: str
          after:
            description: after attribute key [change to]
            type: str
      matching_parameter:
        description: Specify the matching option of target keys.
        type: str
        default: equal
        choices:
          - equal
          - starts_with
          - ends_with
          - regex
'''

EXAMPLES = '''

  # By default, this list is used in the below examples
  l:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

  # This list is the result of the below examples if not stated otherwise.
  r:
    - {a0: A0, a1: B0, k2_x2: [C0], k3_x3: foo}
    - {a0: A1, a1: B1, k2_x2: [C1], k3_x3: bar}

  # 1) By C(default) replace keys that are C(equal) to the attribute C(before).
  t:
    - {before: k0_x0, after: a0}
    - {before: k1_x1, after: a1}
  r: "{{ l | replace_keys(target=t) }}"

  # 2) Replace keys that C(starts) with the attribute C(before).
  t:
    - {before: k0, after: a0}
    - {before: k1, after: a1}
  r: "{{ l | replace_keys(target=t, matching_parameter='starts_with') }}"

  # 3) Replace keys that C(ends) with the attribute C(before).
  t:
    - {before: x0, after: a0}
    - {before: x1, after: a1}
  r: "{{ l | replace_keys(target=t, matching_parameter='ends_with') }}"

  # 4) Replace keys by the C(regex) in the attribute C(before).
  t:
    - {before: "^.*0_x.*$", after: a0}
    - {before: "^.*1_x.*$", after: a1}
  r: "{{ l | replace_keys(target=t, matching_parameter='regex') }}"

  # 5) If more keys match the same before attribute the C(last) key/value will be used.
  t:
    - {before: "^.*_x.*$", after: X}
  r: "{{ l | replace_keys(target=t, matching_parameter='regex') }}"

  # gives

  r:
    - X: foo
    - X: bar

  # 6) If before attributes are equal the C(last) one will be used.
  t:
    - {before: "^.*_x.*$", after: X}
    - {before: "^.*_x.*$", after: Y}
  r: "{{ l | replace_keys(target=t, matching_parameter='regex') }}"

  # gives

  r:
    - Y: foo
    - Y: bar

  # 7) If there are more matches for a key the C(first) one will be used.
  l:
    - {aaa1: A, bbb1: B, ccc1: C}
    - {aaa2: D, bbb2: E, ccc2: F}
  t:
    - {before: a, after: X}
    - {before: aa, after: Y}
  r: "{{ l | replace_keys(target=t, matching_parameter='starts_with') }}"

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

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence

import re


def match_key(k, t, mp):
    if mp == 'equal':
        return k == t
    if mp == 'starts_with':
        return k.startswith(t)
    if mp == 'ends_with':
        return k.endswith(t)
    if mp == 'regex':
        return re.match(t, k)


def replace_keys(data, target=None, matching_parameter='equal'):
    """replace specific keys in a list of dictionaries"""

    mp = matching_parameter
    ml = ['equal', 'starts_with', 'ends_with', 'regex']

    before = [d['before'] for d in target]
    after = [d['after'] for d in target]
    td = dict(zip(before, after))
    index = 0

    if not isinstance(data, Sequence):
        msg = "First argument for replace_keys must be a list. %s is %s"
        raise AnsibleFilterError(msg % (data, type(data)))

    for elem in data:
        if not isinstance(elem, Mapping):
            msg = "Elements of the data list for replace_keys must be dictionaries. %s is %s"
            raise AnsibleFilterError(msg % (elem, type(elem)))

    if not isinstance(target, Sequence):
        msg = "The target for replace_keys must be a list. %s is %s"
        raise AnsibleFilterError(msg % (target, type(target)))

    for elem in target:
        if not isinstance(elem, Mapping):
            msg = "Elements of the target list for replace_keys must be dictionaries. %s is %s"
            raise AnsibleFilterError(msg % (elem, type(elem)))
        if not all(k in elem for k in ("before", "after")):
            msg = "Dictionaries in target must include: after, before."
            raise AnsibleFilterError(msg)

    if mp not in ml:
        msg = ("The matching_parameter for replace_keys must be one of %s. matching_parameter is %s")
        raise AnsibleFilterError(msg % (ml, mp))

    if mp == 'regex':
        for r in before:
            try:
                re.compile(r)
                is_valid = True
            except re.error:
                is_valid = False
            if not is_valid:
                msg = ("The before keys in target must be a valid regex if matching_parameter is regex."
                       "%s is not valid regex")
                raise AnsibleFilterError(msg % r)
    else:
        for s in before:
            if not isinstance(s, string_types):
                msg = "The before keys in target must be strings. %s is %s"
                raise AnsibleFilterError(msg % (s, type(s)))

    data_replaced = []
    for i in data:
        row = dict()
        for k, v in i.items():
            element = []
            for t in td.keys():
                if match_key(k, t, mp):
                    element.append(td[t])
            if element:
                row.update({element[index]: v})
            else:
                row.update({k: v})
        data_replaced.append(row)

    return data_replaced


class FilterModule(object):

    def filters(self):
        return {
            'replace_keys': replace_keys,
        }

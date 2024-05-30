# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: keep_keys
    short_description: Keep specific keys from dictionaries in a list.
    version_added: "2.17"
    author: Vladimir Botka (@vbotka)
    description: This filter keeps only specified keys from a provided list of dictionaries.
    options:
      _input:
        description: A list of dictionaries.
        type: list
        elements: dictionary
        required: true
      target:
        description:
          - A list of keys or keys patterns to keep.
          - The interpretation of the list items depends on the option C(matching_parameter)
          - For matching_parameter C(regex) only the first item is taken.
        type: list
        elements: str
        required: true
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
  l:
    - {k0_x0: A0, k1_x1: B0, k2_x2: [C0], k3_x3: foo}
    - {k0_x0: A1, k1_x1: B1, k2_x2: [C1], k3_x3: bar}

  # By default match equal keys.
  t: [k0_x0, k1_x1]
  r: "{{ l | keep_keys(target=t) }}"

  # Match keys that starts with any of the items in the target.
  t: [k0, k1]
  r: "{{ l | keep_keys(target=t, matching_parameter='starts_with') }}"

  # Match keys that ends with any of the items in target.
  t: [x0, x1]
  r: "{{ l | keep_keys(target=t, matching_parameter='ends_with') }}"

  # Match keys by the regex.
  t: ['^.*[01]_x.*$']
  r: "{{ l | keep_keys(target=t, matching_parameter='regex') }}"

  # Match keys by the regex. The regex does not have to be in list.
  t: '^.*[01]_x.*$'
  r: "{{ l | keep_keys(target=t, matching_parameter='regex') }}"

  # The results of all examples are all the same.
  r:
    - {k0_x0: A0, k1_x1: B0}
    - {k0_x0: A1, k1_x1: B1}
'''

RETURN = '''
  _value:
    description: The list of dictionaries with selected keys.
    type: list
    elements: dictionary
'''

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence

import re


def keep_keys(data, target=None, matching_parameter='equal'):
    """keep specific keys from dictionaries in a list"""

    ld = data
    tt = target
    mp = matching_parameter
    ml = ['equal', 'starts_with', 'ends_with', 'regex']

    if not isinstance(ld, Sequence):
        msg = "First argument for keep_keys must be a list. %s is %s"
        raise AnsibleFilterError(msg % (ld, type(ld)))

    for elem in ld:
        if not isinstance(elem, Mapping):
            msg = "Elements of the data list for keep_keys must be dictionaries. %s is %s"
            raise AnsibleFilterError(msg % (elem, type(elem)))

    if mp not in ml:
        msg = ("The matching_parameter for keep_keys must be one of %s. matching_parameter is %s")
        raise AnsibleFilterError(msg % (ml, mp))

    if mp == 'regex':
        if isinstance(target, string_types):
            tt = target
        elif isinstance(target, Sequence):
            tt = target[0]
        else:
            msg = ("The target for keep_keys must be a string or a list if matching_parameter is regex."
                   "target is %s.")
            raise AnsibleFilterError(msg % target)
        try:
            re.compile(tt)
            is_valid = True
        except re.error:
            is_valid = False
        if not is_valid:
            msg = ("The target for keep_keys must be a valid regex if matching_parameter is regex."
                   "target is %s")
            raise AnsibleFilterError(msg % tt)
    else:
        if not isinstance(tt, Sequence):
            msg = ("The target for keep_keys must be a list if matching_parameter is %s. %s is %s")
            raise AnsibleFilterError(msg % (mp, tt, type(tt)))
        for elem in tt:
            if not isinstance(elem, string_types):
                msg = "Elements of the targets for keep_keys must be strings. %s is %s"
                raise AnsibleFilterError(msg % (elem, type(elem)))

    if mp == 'equal':
        my_keys = [[k for k in i.keys() if k in tt] for i in ld]
    elif mp == 'starts_with':
        my_keys = [[k for k in i.keys() if k.startswith(tuple(tt))] for i in ld]
    elif mp == 'ends_with':
        my_keys = [[k for k in i.keys() if k.endswith(tuple(tt))] for i in ld]
    elif mp == 'regex':
        if isinstance(target, string_types):
            tt = target
        else:
            tt = target[0]
        my_keys = [[k for k in i.keys() if re.match(tt, k)] for i in ld]

    return [dict([(k, ld[i][k]) for k in j]) for i, j in enumerate(my_keys)]


class FilterModule(object):

    def filters(self):
        return {
            'keep_keys': keep_keys,
        }

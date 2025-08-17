# -*- coding: utf-8 -*-
# Copyright (c) 2021, Remy Keil <remy.keil@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: counter
short_description: Counts hashable elements in a sequence
version_added: 4.3.0
author: Rémy Keil (@keilr)
description:
  - Counts hashable elements in a sequence.
options:
  _input:
    description: A sequence.
    type: list
    elements: any
    required: true
"""

EXAMPLES = r"""
- name: Count occurrences
  ansible.builtin.debug:
    msg: >-
      {{ [1, 'a', 2, 2, 'a', 'b', 'a'] | community.general.counter }}
    # Produces: {1: 1, 'a': 3, 2: 2, 'b': 1}
"""

RETURN = r"""
_value:
  description: A dictionary with the elements of the sequence as keys, and their number of occurrences in the sequence as
    values.
  type: dictionary
"""

from ansible.errors import AnsibleFilterError
from collections.abc import Sequence
from collections import Counter


def counter(sequence):
    ''' Count elements in a sequence. Returns dict with count result. '''
    if not isinstance(sequence, Sequence):
        raise AnsibleFilterError('Argument for community.general.counter must be a sequence (string or list). %s is %s' %
                                 (sequence, type(sequence)))

    try:
        result = dict(Counter(sequence))
    except TypeError as e:
        raise AnsibleFilterError(
            "community.general.counter needs a sequence with hashable elements (int, float or str) - %s" % (e)
        )
    return result


class FilterModule(object):
    ''' Ansible counter jinja2 filters '''

    def filters(self):
        filters = {
            'counter': counter,
        }

        return filters

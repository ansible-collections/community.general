# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Lavarde <elavarde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: version_sort
short_description: Sort a list according to version order instead of pure alphabetical one
version_added: 2.2.0
author: Eric L. (@ericzolf)
description:
  - Sort a list according to version order instead of pure alphabetical one.
options:
  _input:
    description: A list of strings to sort.
    type: list
    elements: string
    required: true
"""

EXAMPLES = r"""
- name: Convert list of tuples into dictionary
  ansible.builtin.set_fact:
    dictionary: "{{ ['2.1', '2.10', '2.9'] | community.general.version_sort }}"
    # Result is ['2.1', '2.9', '2.10']
"""

RETURN = r"""
_value:
  description: The list of strings sorted by version.
  type: list
  elements: string
"""

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


def version_sort(value, reverse=False):
    '''Sort a list according to loose versions so that e.g. 2.9 is smaller than 2.10'''
    return sorted(value, key=LooseVersion, reverse=reverse)


class FilterModule(object):
    ''' Version sort filter '''

    def filters(self):
        return {
            'version_sort': version_sort
        }

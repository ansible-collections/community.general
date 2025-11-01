# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: groupby_as_dict
short_description: Transform a sequence of dictionaries to a dictionary where the dictionaries are indexed by an attribute
version_added: 3.1.0
author: Felix Fontein (@felixfontein)
description:
  - Transform a sequence of dictionaries to a dictionary where the dictionaries are indexed by an attribute.
  - This filter is similar to the Jinja2 C(groupby) filter. Use the Jinja2 C(groupby) filter if you have multiple entries
    with the same value, or when you need a dictionary with list values, or when you need to use deeply nested attributes.
positional: attribute
options:
  _input:
    description: A list of dictionaries.
    type: list
    elements: dictionary
    required: true
  attribute:
    description: The attribute to use as the key.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Arrange a list of dictionaries as a dictionary of dictionaries
  ansible.builtin.debug:
    msg: "{{ sequence | community.general.groupby_as_dict('key') }}"
  vars:
    sequence:
      - key: value
        foo: bar
      - key: other_value
        baz: bar
  # Produces the following nested structure:
  #
  #  value:
  #    key: value
  #    foo: bar
  #  other_value:
  #    key: other_value
  #    baz: bar
"""

RETURN = r"""
_value:
  description: A dictionary containing the dictionaries from the list as values.
  type: dictionary
"""

from ansible.errors import AnsibleFilterError
from collections.abc import Mapping, Sequence


def groupby_as_dict(sequence, attribute):
    """
    Given a sequence of dictionaries and an attribute name, returns a dictionary mapping
    the value of this attribute to the dictionary.

    If multiple dictionaries in the sequence have the same value for this attribute,
    the filter will fail.
    """
    if not isinstance(sequence, Sequence):
        raise AnsibleFilterError("Input is not a sequence")

    result = dict()
    for list_index, element in enumerate(sequence):
        if not isinstance(element, Mapping):
            raise AnsibleFilterError(f"Sequence element #{list_index} is not a mapping")
        if attribute not in element:
            raise AnsibleFilterError(f"Attribute not contained in element #{list_index} of sequence")
        result_index = element[attribute]
        if result_index in result:
            raise AnsibleFilterError(f"Multiple sequence entries have attribute value {result_index!r}")
        result[result_index] = element
    return result


class FilterModule:
    """Ansible list filters"""

    def filters(self):
        return {
            "groupby_as_dict": groupby_as_dict,
        }

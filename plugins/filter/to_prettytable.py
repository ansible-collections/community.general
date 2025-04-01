# -*- coding: utf-8 -*-
# Copyright (c) 2025, Timur Gadiev <timur@example.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: to_prettytable
  short_description: Format a list of dictionaries as an ASCII table
  version_added: "8.0.0"
  author: Timur Gadiev (@tgadiev)
  description:
    - This filter takes a list of dictionaries and formats it as an ASCII table using the I(prettytable) Python library.
  requirements:
    - prettytable
  options:
    _input:
      description: A list of dictionaries to format.
      type: list
      elements: dictionary
      required: true
    column_order:
      description: List of column names to specify the order of columns in the table.
      type: list
      elements: string
    header_names:
      description: List of custom header names to use instead of dictionary keys.
      type: list
      elements: string
    column_alignments:
      description: Dictionary of column alignments. Keys are column names, values are alignments.
      type: dictionary
      suboptions:
        alignment:
          description: Alignment for the column. Must be one of C(left), C(center), C(right), C(l), C(c), or C(r).
          type: string
          choices: [left, center, right, l, c, r]
'''

EXAMPLES = '''
- name: Display a list of users as a table
  vars:
    users:
      - name: Alice
        age: 25
        role: admin
      - name: Bob
        age: 30
        role: user
  debug:
    msg: "{{ users | community.general.to_prettytable }}"

- name: Display a table with custom column ordering
  debug:
    msg: "{{ users | community.general.to_prettytable('role', 'name', 'age') }}"

- name: Display a table with custom headers
  debug:
    msg: "{{ users | community.general.to_prettytable(header_names=['User Name', 'User Age', 'User Role']) }}"

- name: Display a table with custom alignments
  debug:
    msg: "{{ users | community.general.to_prettytable(column_alignments={'name': 'center', 'age': 'right', 'role': 'left'}) }}"

- name: Combine multiple options
  debug:
    msg: "{{ users | community.general.to_prettytable(
        column_order=['role', 'name', 'age'],
        header_names=['Position', 'Full Name', 'Years'],
        column_alignments={'name': 'center', 'age': 'right', 'role': 'left'}) }}"
'''

RETURN = '''
  _value:
    description: The formatted ASCII table.
    type: string
'''

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

from ansible.errors import AnsibleFilterError
from ansible.module_utils._text import to_text
from ansible.module_utils.six import string_types


def to_prettytable(data, *args, **kwargs):
    """Convert a list of dictionaries to an ASCII table.

    Args:
        data: List of dictionaries to format
        *args: Optional list of column names to specify column order
        **kwargs: Optional keyword arguments:
            - column_order: List of column names to specify the order
            - header_names: List of custom header names
            - column_alignments: Dict of column alignments (left, center, right)

    Returns:
        String containing the ASCII table
    """
    if not HAS_PRETTYTABLE:
        raise AnsibleFilterError(
            'You need to install "prettytable" Python module to use this filter'
        )

    if not isinstance(data, list):
        raise AnsibleFilterError(
            "Expected a list of dictionaries, got a string"
            if isinstance(data, string_types)
            else f"Expected a list of dictionaries, got {type(data).__name__}"
        )

    # Handle empty data
    if not data:
        return "++\n++"

    # Check that all items are dictionaries
    if not all(isinstance(item, dict) for item in data):
        invalid_item = next(item for item in data if not isinstance(item, dict))
        raise AnsibleFilterError(
            "All items in the list must be dictionaries, got a string"
            if isinstance(invalid_item, string_types)
            else f"All items in the list must be dictionaries, got {type(invalid_item).__name__}"
        )

    # Handle positional argument column order
    column_order = kwargs.get('column_order', None)
    if args and not column_order:
        column_order = list(args)

    # Create the table and configure it
    table = prettytable.PrettyTable()

    # Determine field names
    field_names = column_order or list(data[0].keys())

    # Set headers
    header_names = kwargs.get('header_names', None)
    table.field_names = header_names if header_names else field_names

    # Configure alignments
    _configure_alignments(table, field_names, kwargs.get('column_alignments', {}))

    # Add rows
    rows = [[item.get(col, "") for col in field_names] for item in data]
    table.add_rows(rows)

    return to_text(table)


def _configure_alignments(table, field_names, column_alignments):
    """Configure column alignments for the table.

    Args:
        table: The PrettyTable instance to configure
        field_names: List of field names to align
        column_alignments: Dict of column alignments
    """
    valid_alignments = {"left", "center", "right", "l", "c", "r"}

    if not isinstance(column_alignments, dict):
        return

    for col_name, alignment in column_alignments.items():
        if col_name in field_names:
            alignment = alignment.lower()
            if alignment in valid_alignments:
                table.align[col_name] = alignment[0]


class FilterModule(object):
    """Ansible core jinja2 filters."""

    def filters(self):
        return {
            'to_prettytable': to_prettytable
        }

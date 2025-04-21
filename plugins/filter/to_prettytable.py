# -*- coding: utf-8 -*-
# Copyright (c) 2025, Timur Gadiev <tgadiev@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

DOCUMENTATION = '''
  name: to_prettytable
  short_description: Format a list of dictionaries as an ASCII table
  version_added: "10.6.0"
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
      description:
        - >-
          Dictionary where keys are column names and values are alignment settings.
          Valid alignment values are C(left), C(center), C(right), C(l), C(c), or C(r).
        - >-
          For example, V({'name': 'left', 'id': 'right'}) will align the C(name) column to the left
          and the C(id) column to the right.
      type: dictionary
'''

EXAMPLES = '''
---
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

- name: Display a table with selective column output (only show name and role fields)
  debug:
    msg: "{{ users | community.general.to_prettytable(column_order=['name', 'role']) }}"

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

    # Handle empty data
    if not data:
        return "++\n++"

    # Helper function for type error messages
    def type_error(obj, expected):
        type_name = "string" if isinstance(obj, string_types) else type(obj).__name__
        return f"Expected {expected}, got a {type_name}"

    # Validate list type
    if not isinstance(data, list):
        raise AnsibleFilterError(type_error(data, "a list of dictionaries"))

    # Validate dictionary items
    if data and not all(isinstance(item, dict) for item in data):
        invalid_item = next((item for item in data if not isinstance(item, dict)), None)
        raise AnsibleFilterError(type_error(invalid_item, "all items in the list to be dictionaries"))

    # Handle positional argument column order
    column_order = kwargs.pop('column_order', None)
    if column_order is not None and not isinstance(column_order, list):
        raise AnsibleFilterError(type_error(column_order, "a list of column names"))

    # Validate column_order elements are strings if provided
    if column_order is not None:
        for col in column_order:
            if not isinstance(col, string_types):
                raise AnsibleFilterError(type_error(col, "a string for column name"))

    # Handle positional args and validate
    if args:
        if column_order is not None:
            raise AnsibleFilterError("Cannot use both positional arguments and the 'column_order' keyword argument")

        # Validate args contains strings
        for arg in args:
            if not isinstance(arg, string_types):
                raise AnsibleFilterError(type_error(arg, "a string for column name"))
        column_order = list(args)

    # Create the table and configure it
    table = prettytable.PrettyTable()
    # PrettyTable expects all field names to be strings

    # Get the maximum number of fields in the first dictionary
    max_fields = len(data[0].keys())

    # Validate column_order doesn't exceed the number of fields
    if column_order is not None and len(column_order) > max_fields:
        raise AnsibleFilterError(
            f"'column_order' has more elements ({len(column_order)}) than available fields in data ({max_fields})")

    # Determine field names and ensure they are strings
    if column_order:
        field_names = column_order
    else:
        # Use field names from first dictionary, ensuring all are strings
        field_names = [to_text(k) for k in data[0].keys()]

    # Set headers
    header_names = kwargs.pop('header_names', None)
    if header_names is not None and not isinstance(header_names, list):
        raise AnsibleFilterError(type_error(header_names, "a list of header names"))

    # Validate header_names elements are strings if provided
    if header_names is not None:
        for header in header_names:
            if not isinstance(header, string_types):
                raise AnsibleFilterError(type_error(header, "a string for header name"))

    # Validate header_names doesn't exceed the number of fields
    if header_names is not None and len(header_names) > max_fields:
        raise AnsibleFilterError(
            f"'header_names' has more elements ({len(header_names)}) than available fields in data ({max_fields})")

    # Validate that column_order and header_names have the same size if both provided
    if column_order is not None and header_names is not None and len(column_order) != len(header_names):
        raise AnsibleFilterError(
            f"'column_order' and 'header_names' must have the same number of elements. "
            f"Got {len(column_order)} columns and {len(header_names)} headers.")

    table.field_names = header_names if header_names else field_names

    # Get column alignments and validate
    column_alignments = kwargs.pop('column_alignments', {})

    # Validate column_alignments doesn't have more keys than fields
    if isinstance(column_alignments, dict) and len(column_alignments) > max_fields:
        raise AnsibleFilterError(
            f"'column_alignments' has more elements ({len(column_alignments)}) than available fields in data ({max_fields})")

    # Check for unknown parameters
    if kwargs:
        raise AnsibleFilterError(f"Unknown parameter(s) for to_prettytable filter: {', '.join(kwargs.keys())}")

    # Important: Set the field_names FIRST - this must be done before configuring alignments
    # If header_names is provided, use those for the table display instead of field_names
    display_names = header_names if header_names is not None else field_names
    table.field_names = [to_text(name) for name in display_names]

    # Configure alignments AFTER setting field_names
    # The column_alignments dict keys must match the actual field names in the table
    _configure_alignments(table, display_names, column_alignments)

    # Add rows - use add_row instead of add_rows for compatibility with older versions
    # Create a robust mapping between stringified keys and original keys
    key_map = {}
    reverse_key_map = {}

    # Helper function for case-insensitive key lookup - returns the ORIGINAL key to be used for lookup
    def find_key_match(item_dict, lookup_key):
        # Direct key match
        if lookup_key in item_dict:
            return lookup_key

        # Try boolean conversion for 'true'/'false' strings
        if lookup_key.lower() == 'true' and True in item_dict:
            return True
        if lookup_key.lower() == 'false' and False in item_dict:
            return False

        # Try numeric conversion for string numbers
        if lookup_key.isdigit() and int(lookup_key) in item_dict:
            return int(lookup_key)

        # No match found
        return None

    # Build the mapping of string representations to actual keys
    if not column_order:  # Only needed when using original dictionary keys
        first_dict = data[0]
        for orig_key in first_dict.keys():
            # Store string version of the key
            str_key = to_text(orig_key)
            key_map[str_key] = orig_key
            # Also store lowercase version for case-insensitive lookups
            reverse_key_map[str_key.lower()] = orig_key

    # Process each row
    rows = []
    for item in data:
        row = []
        for col in field_names:
            # Try direct mapping first
            if col in key_map:
                row.append(item.get(key_map[col], ""))
            else:
                # Try to find a matching key in the item
                matched_key = find_key_match(item, col)
                if matched_key is not None:
                    row.append(item.get(matched_key, ""))
                else:
                    # Try case-insensitive lookup as last resort
                    lower_col = col.lower()
                    if lower_col in reverse_key_map:
                        row.append(item.get(reverse_key_map[lower_col], ""))
                    else:
                        # No match found
                        row.append("")
        rows.append(row)

    for row in rows:
        table.add_row(row)

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

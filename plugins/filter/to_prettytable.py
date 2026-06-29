# Copyright (c) 2025, Timur Gadiev <tgadiev@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: to_prettytable
short_description: Format a list of dictionaries as an ASCII table
version_added: "10.7.0"
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
      - Dictionary where keys are column names and values are alignment settings. Valid alignment values are C(left), C(center),
        C(right), C(l), C(c), or C(r).
      - "For example, V({'name': 'left', 'id': 'right'}) aligns the C(name) column to the left and the C(id) column to the
        right."
    type: dictionary
"""

EXAMPLES = r"""
- name: Set a list of users
  ansible.builtin.set_fact:
    users:
      - name: Alice
        age: 25
        role: admin
      - name: Bob
        age: 30
        role: user

- name: Display a list of users as a table
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable
      }}

- name: Display a table with custom column ordering
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable(
          column_order=['role', 'name', 'age']
        )
      }}

- name: Display a table with selective column output (only show name and role fields)
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable(
          column_order=['name', 'role']
        )
      }}

- name: Display a table with custom headers
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable(
          header_names=['User Name', 'User Age', 'User Role']
        )
      }}

- name: Display a table with custom alignments
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable(
          column_alignments={'name': 'center', 'age': 'right', 'role': 'left'}
        )
      }}

- name: Combine multiple options
  ansible.builtin.debug:
    msg: >-
      {{
        users | community.general.to_prettytable(
          column_order=['role', 'name', 'age'],
          header_names=['Position', 'Full Name', 'Years'],
          column_alignments={'name': 'center', 'age': 'right', 'role': 'left'}
        )
      }}
"""

RETURN = r"""
_value:
  description: The formatted ASCII table.
  type: string
"""

try:
    import prettytable

    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_text


class TypeValidationError(AnsibleFilterError):
    """Custom exception for type validation errors.

    Args:
        obj: The object with incorrect type
        expected: Description of expected type
    """

    def __init__(self, obj, expected):
        type_name = "string" if isinstance(obj, str) else type(obj).__name__
        super().__init__(f"Expected {expected}, got a {type_name}")


def _validate_list_param(param, param_name, ensure_strings=True):
    """Validate a parameter is a list and optionally ensure all elements are strings.

    Args:
        param: The parameter to validate
        param_name: The name of the parameter for error messages
        ensure_strings: Whether to check that all elements are strings

    Raises:
        AnsibleFilterError: If validation fails
    """
    # Map parameter names to their original error message format
    error_messages = {"column_order": "a list of column names", "header_names": "a list of header names"}

    # Use the specific error message if available, otherwise use a generic one
    error_msg = error_messages.get(param_name, f"a list for {param_name}")

    if not isinstance(param, list):
        raise TypeValidationError(param, error_msg)

    if ensure_strings:
        for item in param:
            if not isinstance(item, str):
                # Maintain original error message format
                if param_name == "column_order":
                    error_msg = "a string for column name"
                elif param_name == "header_names":
                    error_msg = "a string for header name"
                else:
                    error_msg = f"a string for {param_name} element"
                raise TypeValidationError(item, error_msg)


def _match_key(item_dict, lookup_key):
    """Find a matching key in a dictionary, handling type conversion.

    Args:
        item_dict: Dictionary to search in
        lookup_key: Key to look for, possibly needing type conversion

    Returns:
        The matching key or None if no match found
    """
    # Direct key match
    if lookup_key in item_dict:
        return lookup_key

    # Try boolean conversion for 'true'/'false' strings
    if isinstance(lookup_key, str):
        if lookup_key.lower() == "true" and True in item_dict:
            return True
        if lookup_key.lower() == "false" and False in item_dict:
            return False

        # Try numeric conversion for string numbers
        if lookup_key.isdigit() and int(lookup_key) in item_dict:
            return int(lookup_key)

    # No match found
    return None


def _build_key_maps(data):
    """Build mappings between string keys and original keys.

    Args:
        data: List of dictionaries with keys to map

    Returns:
        Tuple of (key_map, reverse_key_map)
    """
    key_map = {}
    reverse_key_map = {}

    # Check if the data list is not empty
    if not data:
        return key_map, reverse_key_map

    first_dict = data[0]
    for orig_key in first_dict.keys():
        # Store string version of the key
        str_key = to_text(orig_key)
        key_map[str_key] = orig_key
        # Also store lowercase version for case-insensitive lookups
        reverse_key_map[str_key.lower()] = orig_key

    return key_map, reverse_key_map


def _configure_alignments(table, field_names, column_alignments):
    """Configure column alignments for the table.

    Args:
        table: The PrettyTable instance to configure
        field_names: List of field names to align
        column_alignments: Dict of column alignments
    """

    if not isinstance(column_alignments, dict):
        return

    for col_name, alignment in column_alignments.items():
        if col_name in field_names:
            # We already validated alignment is a string and a valid value in the main function
            # Just apply it here
            alignment = alignment.lower()
            table.align[col_name] = alignment[0]


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
        raise AnsibleFilterError('You need to install "prettytable" Python module to use this filter')

    # === Input validation ===
    # Validate list type
    if not isinstance(data, list):
        raise TypeValidationError(data, "a list of dictionaries")

    # Validate dictionary items if list is not empty
    if data and not all(isinstance(item, dict) for item in data):
        invalid_item = next((item for item in data if not isinstance(item, dict)), None)
        raise TypeValidationError(invalid_item, "all items in the list to be dictionaries")

    # Get sample dictionary to determine fields - empty if no data
    sample_dict = data[0] if data else {}
    max_fields = len(sample_dict)

    # === Process column order ===
    # Handle both positional and keyword column_order
    column_order = kwargs.pop("column_order", None)

    # Check for conflict between args and column_order
    if args and column_order is not None:
        raise AnsibleFilterError("Cannot use both positional arguments and the 'column_order' keyword argument")

    # Use positional args if provided
    if args:
        column_order = list(args)

    # Validate column_order
    if column_order is not None:
        _validate_list_param(column_order, "column_order")

        # Validate column_order doesn't exceed the number of fields (skip if data is empty)
        if data and len(column_order) > max_fields:
            raise AnsibleFilterError(
                f"'column_order' has more elements ({len(column_order)}) than available fields in data ({max_fields})"
            )

    # === Process headers ===
    # Determine field names and ensure they are strings
    if column_order:
        field_names = column_order
    else:
        # Use field names from first dictionary, ensuring all are strings
        field_names = [to_text(k) for k in sample_dict]

    # Process custom headers
    header_names = kwargs.pop("header_names", None)
    if header_names is not None:
        _validate_list_param(header_names, "header_names")

        # Validate header_names doesn't exceed the number of fields (skip if data is empty)
        if data and len(header_names) > max_fields:
            raise AnsibleFilterError(
                f"'header_names' has more elements ({len(header_names)}) than available fields in data ({max_fields})"
            )

        # Validate that column_order and header_names have the same size if both provided
        if column_order is not None and len(column_order) != len(header_names):
            raise AnsibleFilterError(
                f"'column_order' and 'header_names' must have the same number of elements. "
                f"Got {len(column_order)} columns and {len(header_names)} headers."
            )

    # === Process alignments ===
    # Get column alignments and validate
    column_alignments = kwargs.pop("column_alignments", {})
    valid_alignments = {"left", "center", "right", "l", "c", "r"}

    # Validate column_alignments is a dictionary
    if not isinstance(column_alignments, dict):
        raise TypeValidationError(column_alignments, "a dictionary for column_alignments")

    # Validate column_alignments keys and values
    for key, value in column_alignments.items():
        # Check that keys are strings
        if not isinstance(key, str):
            raise TypeValidationError(key, "a string for column_alignments key")

        # Check that values are strings
        if not isinstance(value, str):
            raise TypeValidationError(value, "a string for column_alignments value")

        # Check that values are valid alignments
        if value.lower() not in valid_alignments:
            raise AnsibleFilterError(
                f"Invalid alignment '{value}' in 'column_alignments'. "
                f"Valid alignments are: {', '.join(sorted(valid_alignments))}"
            )

    # Validate column_alignments doesn't have more keys than fields (skip if data is empty)
    if data and len(column_alignments) > max_fields:
        raise AnsibleFilterError(
            f"'column_alignments' has more elements ({len(column_alignments)}) than available fields in data ({max_fields})"
        )

    # Check for unknown parameters
    if kwargs:
        raise AnsibleFilterError(f"Unknown parameter(s) for to_prettytable filter: {', '.join(sorted(kwargs))}")

    # === Build the table ===
    table = prettytable.PrettyTable()

    # Set the field names for display
    display_names = header_names if header_names is not None else field_names
    table.field_names = [to_text(name) for name in display_names]

    # Configure alignments after setting field_names
    _configure_alignments(table, display_names, column_alignments)

    # Build key maps only if not using explicit column_order and we have data
    key_map = {}
    reverse_key_map = {}
    if not column_order and data:  # Only needed when using original dictionary keys and we have data
        key_map, reverse_key_map = _build_key_maps(data)

    # If we have an empty list with no custom parameters, return a simple empty table
    if not data and not column_order and not header_names and not column_alignments:
        return "++\n++"

    # Process each row if we have data
    for item in data:
        row = []
        for col in field_names:
            # Try direct mapping first
            if col in key_map:
                row.append(item.get(key_map[col], ""))
            else:
                # Try to find a matching key in the item
                matched_key = _match_key(item, col)
                if matched_key is not None:
                    row.append(item.get(matched_key, ""))
                else:
                    # Try case-insensitive lookup as last resort
                    lower_col = col.lower() if isinstance(col, str) else str(col).lower()
                    if lower_col in reverse_key_map:
                        row.append(item.get(reverse_key_map[lower_col], ""))
                    else:
                        # No match found
                        row.append("")
        table.add_row(row)

    return to_text(table)


class FilterModule:
    """Ansible core jinja2 filters."""

    def filters(self):
        return {"to_prettytable": to_prettytable}

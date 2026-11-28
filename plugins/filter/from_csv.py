# Copyright (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# Copyright (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: from_csv
short_description: Converts CSV text input into list of dicts
version_added: 2.3.0
author: Andrew Pantuso (@Ajpantuso)
description:
  - Converts CSV text input into list of dictionaries.
options:
  _input:
    description: A string containing a CSV document.
    type: string
    required: true
  dialect:
    description:
      - The CSV dialect to use when parsing the CSV file.
      - Possible values include V(excel), V(excel-tab) or V(unix).
    type: str
    default: excel
  fieldnames:
    description:
      - A list of field names for every column.
      - This is needed if the CSV does not have a header.
    type: list
    elements: str
  delimiter:
    description:
      - A one-character string used to separate fields.
      - When using this parameter, you change the default value used by O(dialect).
      - The default value depends on the dialect used.
    type: str
  skipinitialspace:
    description:
      - Whether to ignore any whitespaces immediately following the delimiter.
      - When using this parameter, you change the default value used by O(dialect).
      - The default value depends on the dialect used.
    type: bool
  strict:
    description:
      - Whether to raise an exception on bad CSV input.
      - When using this parameter, you change the default value used by O(dialect).
      - The default value depends on the dialect used.
    type: bool
  escapechar:
    description:
      - A one-character string that removes any special meaning from the character following it, for example to use the
        delimiter inside a field.
      - When using this parameter, you change the default value used by O(dialect).
      - The default value depends on the dialect used.
    type: str
    version_added: 14.1.0
"""

EXAMPLES = r"""
- name: Parse a CSV file's contents
  ansible.builtin.debug:
    msg: >-
      {{ csv_data | community.general.from_csv(dialect='unix') }}
  vars:
    csv_data: |
      Column 1,Value
      foo,23
      bar,42
  # Produces the following list of dictionaries:
  #   {
  #     "Column 1": "foo",
  #     "Value": "23",
  #   },
  #   {
  #     "Column 1": "bar",
  #     "Value": "42",
  #   }

- name: Parse CSV data that escapes the delimiter with a backslash
  ansible.builtin.debug:
    msg: >-
      {{ csv_data | community.general.from_csv(delimiter=':', escapechar='\\') }}
  vars:
    csv_data: |
      name:time
      foo:12\:41\:52
  # Produces the following list of dictionaries:
  #   {
  #     "name": "foo",
  #     "time": "12:41:52",
  #   }
"""

RETURN = r"""
_value:
  description: A list with one dictionary per row.
  type: list
  elements: dictionary
"""

from ansible.errors import AnsibleFilterError

from ansible_collections.community.general.plugins.module_utils._csv import (
    CSVError,
    CustomDialectFailureError,
    DialectNotAvailableError,
    initialize_dialect,
    read_csv,
)


def from_csv(
    data, dialect="excel", fieldnames=None, delimiter=None, skipinitialspace=None, strict=None, escapechar=None
):
    if escapechar is not None and not isinstance(escapechar, str):
        raise AnsibleFilterError(f"from_csv's escapechar parameter must be a string, got {type(escapechar)}")

    dialect_params = {
        "delimiter": delimiter,
        "skipinitialspace": skipinitialspace,
        "strict": strict,
        "escapechar": escapechar,
    }

    try:
        dialect = initialize_dialect(dialect, **dialect_params)
    except (CustomDialectFailureError, DialectNotAvailableError) as e:
        raise AnsibleFilterError(str(e)) from e

    reader = read_csv(data, dialect, fieldnames)

    data_list = []

    try:
        for row in reader:
            data_list.append(row)
    except CSVError as e:
        raise AnsibleFilterError(f"Unable to process file: {e}") from e

    return data_list


class FilterModule:
    def filters(self):
        return {"from_csv": from_csv}

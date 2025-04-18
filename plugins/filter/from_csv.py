# -*- coding: utf-8 -*-

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
"""

RETURN = r"""
_value:
  description: A list with one dictionary per row.
  type: list
  elements: dictionary
"""

from ansible.errors import AnsibleFilterError

from ansible_collections.community.general.plugins.module_utils.csv import (initialize_dialect, read_csv, CSVError,
                                                                            DialectNotAvailableError,
                                                                            CustomDialectFailureError)


def from_csv(data, dialect='excel', fieldnames=None, delimiter=None, skipinitialspace=None, strict=None):

    dialect_params = {
        "delimiter": delimiter,
        "skipinitialspace": skipinitialspace,
        "strict": strict,
    }

    try:
        dialect = initialize_dialect(dialect, **dialect_params)
    except (CustomDialectFailureError, DialectNotAvailableError) as e:
        raise AnsibleFilterError(str(e))

    reader = read_csv(data, dialect, fieldnames)

    data_list = []

    try:
        for row in reader:
            data_list.append(row)
    except CSVError as e:
        raise AnsibleFilterError(f"Unable to process file: {e}")

    return data_list


class FilterModule(object):

    def filters(self):
        return {
            'from_csv': from_csv
        }

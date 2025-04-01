#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: prettytable
short_description: Format data into an ASCII table using prettytable
version_added: '10.6.0'
author:
    - Timur Gadiev (@tgadiev)
extends_documentation_fragment:
    - action_common_attributes
    - action_common_attributes.conn
    - action_common_attributes.flow
    - community.general.attributes
    - community.general.attributes.flow
description:
    - This module formats a list of dictionaries into an ASCII table using the B(prettytable) Python library.
    - Useful for creating human-readable output from structured data.
    - Allows customization of column order, headers, and alignments.
    - The table is created with a clean, readable format suitable for terminal output.
requirements:
    - prettytable
attributes:
    action:
        support: full
    async:
        support: none
    become:
        support: none
    bypass_host_loop:
        support: none
    check_mode:
        support: full
    connection:
        support: none
    delegation:
        support: none
        details: This is a pure action plugin that runs entirely on the controller. Delegation has no effect as no tasks are executed on remote hosts.
    diff_mode:
        support: none
    platform:
        support: full
        platforms: all
options:
    data:
        description:
            - List of dictionaries to format into a table.
            - Each dictionary in the list represents a row in the table.
            - Dictionary keys become column headers unless overridden by I(header_names).
            - If the list is empty, an empty table will be created.
            - All items in the list must be dictionaries.
        type: list
        elements: dict
        required: true
    column_order:
        description:
            - List of dictionary keys specifying the order of columns in the output table.
            - If not specified, uses the keys from the first dictionary in the input list.
            - Only the columns specified in this list will be included in the table.
            - Keys must exist in the input dictionaries.
        type: list
        elements: str
        required: false
    header_names:
        description:
            - List of custom header names for the columns.
            - Must match the length of columns being displayed.
            - If not specified, uses the dictionary keys or I(column_order) values as headers.
            - Use this to provide more readable or formatted column headers.
        type: list
        elements: str
        required: false
    column_alignments:
        description:
            - Dictionary mapping column names to their alignment.
            - Keys should be column names (either from input data or I(column_order)).
            - Values must be one of 'left', 'center', 'right' (or 'l', 'c', 'r').
            - Invalid alignment values will be ignored with a warning.
            - Columns not specified default to left alignment.
            - Alignments for non-existent columns are ignored.
        type: dict
        required: false
notes:
    - This is an action plugin, meaning the plugin executes on the controller, rather than on the target host.
    - The prettytable Python library must be installed on the controller.
    - Column alignments are case-insensitive.
    - Missing values in input dictionaries are displayed as empty strings.
seealso:
    - module: ansible.builtin.debug
'''

EXAMPLES = r'''
# Basic usage with a list of dictionaries
- name: Create a table from user data
  community.general.prettytable:
    data:
      - name: Alice
        age: 25
        role: admin
      - name: Bob
        age: 30
        role: user

# Specify column order and custom headers
- name: Create a formatted table with custom headers
  community.general.prettytable:
    data:
      - name: Alice
        age: 25
        role: admin
      - name: Bob
        age: 30
        role: user
    column_order:
      - name
      - role
      - age
    header_names:
      - "User Name"
      - "User Role"
      - "User Age"

# Set column alignments for better number and text formatting
- name: Create table with specific alignments
  community.general.prettytable:
    data:
      - date: "2023-01-01"
        description: "Office supplies"
        amount: 123.45
      - date: "2023-01-02"
        description: "Software license"
        amount: 500.00
    column_alignments:
      amount: right      # Numbers right-aligned
      description: left  # Text left-aligned
      date: center      # Dates centered
'''

# -*- coding: utf-8 -*-
# Copyright (c) 2020, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any, Dict, List, Optional

__metaclass__ = type  # pylint: disable=C0103

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase

try:
    import prettytable

    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False


class ActionModule(ActionBase):
    """Print prettytable from list of dicts."""

    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(
        ("data", "column_order", "header_names", "column_alignments")
    )
    _VALID_ALIGNMENTS = {"left", "center", "right", "l", "c", "r"}

    def run(
        self, tmp: Optional[str] = None, task_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)  # pylint: disable=R1725
        del tmp  # tmp no longer has any effect

        try:
            self._handle_options()

            if not HAS_PRETTYTABLE:
                raise AnsibleError(
                    'You need to install "prettytable" python module before running this module'
                )

            data = self._task.args.get("data")
            if data is None:  # Only check for None, allow empty list
                raise AnsibleError("The 'data' parameter is required")

            if not isinstance(data, list):
                raise AnsibleError(
                    "Expected a list of dictionaries, got a string"
                    if isinstance(data, (str, bytes))
                    else f"Expected a list of dictionaries, got {type(data).__name__}"
                )

            if data and not all(isinstance(item, dict) for item in data):
                invalid_item = next(item for item in data if not isinstance(item, dict))
                raise AnsibleError(
                    "All items in the list must be dictionaries, got a string"
                    if isinstance(invalid_item, (str, bytes))
                    else f"All items in the list must be dictionaries, got {type(invalid_item).__name__}"
                )

            # Special handling for empty data
            if not data:
                result["pretty_table"] = "++\n++"
            else:
                table = self._create_table(data)
                result["pretty_table"] = to_text(table)

            result["_ansible_verbose_always"] = True
            result["failed"] = False

        except (AnsibleError, AnsibleUndefinedVariable) as e:
            result["failed"] = True
            result["msg"] = str(e)

        return result

    def _handle_options(self) -> None:
        """Validate module arguments."""
        argument_spec = {
            "data": {"type": "list", "required": True},
            "column_order": {"type": "list", "elements": "str"},
            "header_names": {"type": "list", "elements": "str"},
            "column_alignments": {"type": "dict"},
        }

        self._options_context = self.validate_argument_spec(argument_spec)

    def _create_table(self, data: List[Dict[str, Any]]) -> prettytable.PrettyTable:
        """Create and configure the prettytable instance.

        Args:
            data: List of dictionaries to format into a table

        Returns:
            Configured PrettyTable instance
        """
        table = prettytable.PrettyTable()

        # Determine field names from data or column_order
        field_names = self._task.args.get("column_order") or list(data[0].keys())

        # Set headers
        header_names = self._task.args.get("header_names")
        table.field_names = header_names if header_names else field_names

        # Configure alignments
        self._configure_alignments(table, field_names)

        # Add rows
        rows = [[item.get(col, "") for col in field_names] for item in data]
        table.add_rows(rows)

        return table

    def _configure_alignments(
        self, table: prettytable.PrettyTable, field_names: List[str]
    ) -> None:
        """Configure column alignments for the table.

        Args:
            table: The PrettyTable instance to configure
            field_names: List of field names to align
        """
        column_alignments = self._task.args.get("column_alignments", {})
        if not isinstance(column_alignments, dict):
            return

        for col_name, alignment in column_alignments.items():
            if col_name in field_names:
                alignment = alignment.lower()
                if alignment in self._VALID_ALIGNMENTS:
                    table.align[col_name] = alignment[0]
                else:
                    self._display.warning(
                        f"Ignored invalid alignment '{alignment}' for column '{col_name}'. "
                        f"Valid alignments are {list(self._VALID_ALIGNMENTS)}"
                    )

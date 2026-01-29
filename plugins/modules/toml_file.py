#!/usr/bin/python

# Copyright (c) 2026, Jose Drowne
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: toml_file
short_description: Manage individual settings in TOML files
version_added: 12.4.0
extends_documentation_fragment:
  - ansible.builtin.files
  - community.general.attributes
description:
  - Manage (add, remove, change) individual settings in a TOML file without having to manage the file as a whole
    with, say, M(ansible.builtin.template) or M(ansible.builtin.assemble).
  - Adds missing tables if they do not exist.
  - Comments and formatting are preserved using the C(tomlkit) library.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  path:
    description:
      - Path to the TOML file; this file is created if required and O(create=true).
    type: path
    required: true
    aliases: [dest]
  table:
    description:
      - Table name in the TOML file.
      - Use dotted notation for nested tables (for example, V(server.database)).
      - For array of tables (C([[table]])), use bracket notation to specify the index
        (for example, V(products[0]) for the first entry, V(products[append]) to append a new entry).
      - Nested arrays of tables are supported (for example, V(servers[1].databases[0])).
      - If omitted or empty string, the key is set at the document root level.
    type: str
  key:
    description:
      - The key to manage within the table (or document root if O(table) is not specified).
      - Use dotted notation to address nested keys (for example, V(connection.timeout)).
      - May be omitted when removing an entire table with O(state=absent).
    type: str
  value:
    description:
      - The value to set for the key.
      - JSON types are automatically converted to appropriate TOML types.
      - Use O(value_type) to force a specific type.
      - Required when O(state=present) and O(key) is specified.
    type: raw
  value_type:
    description:
      - Force the value to be a specific TOML type.
    type: str
    choices:
      auto: Automatically detects the type from the input value.
      string: Forces the value to be a TOML string.
      literal_string: Creates a TOML literal string (single quotes, no escape processing).
      multiline_string: Creates a TOML multi-line basic string (triple double quotes).
      multiline_literal_string: Creates a TOML multi-line literal string (triple single quotes).
      integer: Forces the value to be a TOML integer.
      hex_integer: Forces the value to be a TOML hexadecimal integer (for example, V(0xDEADBEEF)).
      octal_integer: Forces the value to be a TOML octal integer (for example, V(0o755)).
      binary_integer: Forces the value to be a TOML binary integer (for example, V(0b11010110)).
      float: Forces the value to be a TOML float. Supports V(inf), V(-inf), and V(nan).
      boolean: Forces the value to be a TOML boolean.
      datetime: Parses the value as an ISO 8601 offset or local datetime.
      date: Parses the value as a local date (for example, V(1979-05-27)).
      time: Parses the value as a local time (for example, V(07:32:00)).
      array: Ensures the value is a TOML array.
      inline_table: Ensures the value is a TOML inline table.
    default: auto
  state:
    description:
      - If set to V(absent), the specified key (or entire table if no key is specified) is removed.
      - If set to V(present), the specified key is added or updated.
    type: str
    choices: [absent, present]
    default: present
  backup:
    description:
      - Create a backup file including the timestamp information so you can get the original file back
        if you somehow clobbered it incorrectly.
    type: bool
    default: false
  create:
    description:
      - If set to V(false), the module fails if the file does not already exist.
      - By default it creates the file if it is missing.
    type: bool
    default: true
  follow:
    description:
      - This flag indicates that filesystem links, if they exist, should be followed.
      - O(follow=true) can modify O(path) when combined with parameters such as O(mode).
    type: bool
    default: false
requirements:
  - tomlkit
notes:
  - The C(tomlkit) library preserves comments and formatting in TOML files.
  - When O(state=present) and O(key) is specified, O(value) must also be provided.
seealso:
  - module: community.general.ini_file
author:
  - Jose Drowne (@jdrowne)
"""

EXAMPLES = r"""
- name: Set server host in TOML file
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: server
    key: host
    value: localhost

- name: Set nested configuration value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: server.database
    key: port
    value: 5432
    value_type: integer

- name: Set a boolean value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: features
    key: debug
    value: true
    value_type: boolean

- name: Set an array value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: server
    key: allowed_hosts
    value:
      - localhost
      - 127.0.0.1
      - "::1"

- name: Set a value at document root level
  community.general.toml_file:
    path: /etc/myapp/config.toml
    key: title
    value: My Application

- name: Remove a key from a table
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: server
    key: deprecated_option
    state: absent

- name: Remove an entire table
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: obsolete_section
    state: absent

- name: Add entry to array of tables
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: products[append]
    key: name
    value: Hammer

- name: Modify first entry in array of tables
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: products[0]
    key: price
    value: 9.99

- name: Modify nested array of tables
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: servers[0].databases[1]
    key: name
    value: secondary_db

- name: Set an inline table
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: database
    key: connection
    value:
      host: localhost
      port: 5432
    value_type: inline_table

- name: Ensure config exists with backup
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: server
    key: port
    value: 8080
    backup: true

- name: Set infinity value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: limits
    key: max_value
    value: inf
    value_type: float

- name: Set a date value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: project
    key: start_date
    value: "2026-01-17"
    value_type: date

- name: Set a time value
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: schedule
    key: daily_backup
    value: "03:00:00"
    value_type: time

- name: Set a literal string (no escape processing)
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: paths
    key: regex
    value: '\\d+\\.\\d+'
    value_type: literal_string

- name: Set a multiline string
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: messages
    key: welcome
    value: |
      Welcome to our application!
      We hope you enjoy using it.
    value_type: multiline_string

- name: Set a hexadecimal integer
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: display
    key: color
    value: 16777215
    value_type: hex_integer

- name: Set an octal integer (file permissions)
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: files
    key: mode
    value: 493
    value_type: octal_integer

- name: Set a binary integer
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: flags
    key: bits
    value: 170
    value_type: binary_integer
"""

RETURN = r"""
path:
  description: The path to the TOML file.
  returned: success
  type: str
  sample: /etc/myapp/config.toml
backup_file:
  description: The name of the backup file that was created.
  returned: when O(backup=true) and file was modified
  type: str
  sample: /etc/myapp/config.toml.2026-01-17@12:34:56~
"""

import os
import re
import tempfile
import traceback
import typing as t
from dataclasses import dataclass
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("tomlkit"):
    import tomlkit
    from tomlkit.items import AoT, Array, InlineTable, Integer, Table, Trivia


class TomlFileError(Exception):
    pass


# Type alias for array-of-tables index (int for position, "append" for new entry, None for default)
IndexType = int | t.Literal["append"] | None


@dataclass
class TomlParams:
    """Parameters for TOML file operations."""

    path: str
    table: str | None
    key: str | None
    value: t.Any
    value_type: t.Literal[
        "auto",
        "string",
        "literal_string",
        "multiline_string",
        "multiline_literal_string",
        "integer",
        "hex_integer",
        "octal_integer",
        "binary_integer",
        "float",
        "boolean",
        "datetime",
        "date",
        "time",
        "array",
        "inline_table",
    ]
    state: t.Literal["absent", "present"]
    backup: bool
    create: bool
    follow: bool


@dataclass
class NavContext:
    """Context for table navigation operations."""

    parsed: list[tuple[str, IndexType]]
    create: bool


# =============================================================================
# Path Parsing Functions
# =============================================================================


def parse_table_path(table_path: str | None) -> list[tuple[str, IndexType]]:
    """Parse a table path with optional array indices."""
    if table_path is None or table_path == "":
        return []  # Empty list means document root

    result = []
    segment_pattern = re.compile(r"^([^\[\]]+)(?:\[(-?\d+|append)\])?$")

    for segment in table_path.split("."):
        match = segment_pattern.match(segment)
        if not match:
            raise TomlFileError(f"Invalid table path segment: '{segment}'")
        name = match.group(1)
        index_str = match.group(2)
        index: IndexType
        if index_str is None:
            index = None
        elif index_str == "append":
            index = "append"
        else:
            index = int(index_str)
        result.append((name, index))

    return result


def _format_path(parsed: list[tuple[str, IndexType]], up_to: int | None = None) -> str:
    """Format a parsed path back to string for error messages."""
    if up_to is None:
        up_to = len(parsed)
    return ".".join(name + (f"[{idx}]" if idx is not None else "") for name, idx in parsed[:up_to])


# =============================================================================
# Value Conversion Functions (dispatch pattern for O(1) lookup)
# =============================================================================


def _convert_auto(value: t.Any) -> t.Any:
    """Auto-detect and convert value type."""
    if isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _try_parse_datetime_string(value)
    if isinstance(value, list):
        return _convert_list_to_array(value)
    if isinstance(value, dict):
        return _convert_dict_to_inline_table(value)
    return str(value)


def _try_parse_datetime_string(value: str) -> str | datetime:
    """Try parsing string as datetime, return as-is if not."""
    if "T" in value or " " in value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    return value


def _convert_list_to_array(value: list[t.Any]) -> Array:
    """Convert Python list to TOML array."""
    arr = tomlkit.array()
    for item in value:
        arr.append(convert_value(item, "auto"))
    return arr


def _convert_dict_to_inline_table(value: dict[str, t.Any]) -> InlineTable:
    """Convert Python dict to TOML inline table."""
    tbl = tomlkit.inline_table()
    for k, v in value.items():
        tbl[k] = convert_value(v, "auto")
    return tbl


def _convert_string(value: t.Any) -> str:
    return str(value)


def _convert_literal_string(value: t.Any) -> str:
    return tomlkit.string(str(value), literal=True)


def _convert_multiline_string(value: t.Any) -> str:
    return tomlkit.string(str(value), multiline=True)


def _convert_multiline_literal_string(value: t.Any) -> str:
    return tomlkit.string(str(value), literal=True, multiline=True)


def _convert_integer(value: t.Any) -> int:
    return int(value)


def _convert_hex_integer(value: t.Any) -> Integer:
    int_val = int(value) if isinstance(value, int) else int(str(value), 16)
    return Integer(int_val, Trivia(), hex(int_val))


def _convert_octal_integer(value: t.Any) -> Integer:
    int_val = int(value) if isinstance(value, int) else int(str(value), 8)
    return Integer(int_val, Trivia(), oct(int_val))


def _convert_binary_integer(value: t.Any) -> Integer:
    int_val = int(value) if isinstance(value, int) else int(str(value), 2)
    return Integer(int_val, Trivia(), bin(int_val))


def _convert_float(value: t.Any) -> float:
    if isinstance(value, str):
        return float(value.lower())
    return float(value)


def _convert_boolean(value: t.Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on")
    return bool(value)


def _convert_datetime(value: t.Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _convert_date(value: t.Any) -> t.Any:
    from datetime import date as date_type

    if isinstance(value, date_type) and not isinstance(value, datetime):
        return tomlkit.date(value.isoformat())
    return tomlkit.date(str(value))


def _convert_time(value: t.Any) -> t.Any:
    from datetime import time as time_type

    if isinstance(value, time_type):
        return tomlkit.time(value.isoformat())
    return tomlkit.time(str(value))


def _convert_array(value: t.Any) -> Array:
    if isinstance(value, list):
        return _convert_list_to_array(value)
    arr = tomlkit.array()
    arr.append(convert_value(value, "auto"))
    return arr


def _convert_inline_table(value: t.Any) -> InlineTable:
    if not isinstance(value, dict):
        raise ValueError(f"Cannot convert {type(value).__name__} to inline_table")
    return _convert_dict_to_inline_table(value)


# Dispatch dict for O(1) type lookup
_CONVERTERS = {
    "auto": _convert_auto,
    "string": _convert_string,
    "literal_string": _convert_literal_string,
    "multiline_string": _convert_multiline_string,
    "multiline_literal_string": _convert_multiline_literal_string,
    "integer": _convert_integer,
    "hex_integer": _convert_hex_integer,
    "octal_integer": _convert_octal_integer,
    "binary_integer": _convert_binary_integer,
    "float": _convert_float,
    "boolean": _convert_boolean,
    "datetime": _convert_datetime,
    "date": _convert_date,
    "time": _convert_time,
    "array": _convert_array,
    "inline_table": _convert_inline_table,
}


def convert_value(value: t.Any, value_type: str = "auto") -> t.Any:
    """Convert a value to the appropriate TOML type."""
    converter = _CONVERTERS.get(value_type)
    if converter:
        return converter(value)
    return value


# =============================================================================
# Table Navigation Functions (extracted for reduced nesting)
# =============================================================================


def load_toml_document(path: str, create: bool = True) -> tomlkit.TOMLDocument:
    """Load a TOML document from file."""
    if not os.path.exists(path):
        if not create:
            raise TomlFileError(f"Destination {path} does not exist!")
        return tomlkit.document()

    try:
        with open(path, encoding="utf-8") as f:
            return tomlkit.parse(f.read())
    except Exception as e:
        raise TomlFileError(f"Failed to parse TOML file: {e}") from e


def _create_new_aot_entry(current: Table | tomlkit.TOMLDocument, name: str) -> Table:
    """Create a new array of tables with first entry."""
    new_table = tomlkit.table()
    aot = tomlkit.aot()
    aot.append(new_table)
    current[name] = aot
    return new_table


def _create_regular_table(current: Table | tomlkit.TOMLDocument, name: str) -> Table:
    """Create a regular table."""
    new_table = tomlkit.table()
    current[name] = new_table
    return new_table


def _create_table_segment(
    current: Table | tomlkit.TOMLDocument, name: str, index: IndexType, ctx: NavContext, i: int
) -> Table:
    """Create a new table segment when name not in current."""
    if not ctx.create:
        raise TomlFileError(f"Table '{_format_path(ctx.parsed, i + 1)}' does not exist")
    if index == "append":
        return _create_new_aot_entry(current, name)
    if index is not None:
        raise TomlFileError(f"Cannot create table at index {index} - array of tables '{name}' does not exist")
    return _create_regular_table(current, name)


def _get_aot_default(aot: AoT, ctx: NavContext, i: int) -> Table:
    """Get first entry from AoT when no index specified."""
    if len(aot) == 0:
        raise TomlFileError(f"Array of tables '{_format_path(ctx.parsed, i + 1)}' is empty")
    return aot[0]


def _get_aot_at_index(aot: AoT, index: int, ctx: NavContext, i: int) -> Table:
    """Get AoT entry at specific index."""
    if 0 <= index < len(aot):
        return aot[index]
    raise TomlFileError(f"Array of tables index {index} is out of range for '{_format_path(ctx.parsed, i + 1)}'")


def _handle_aot_append(aot: AoT, is_last: bool, ctx: NavContext, i: int) -> Table:
    """Handle AoT[append] - append a new entry to the array of tables."""
    if not is_last:
        raise TomlFileError(f"Cannot use [append] in middle of path '{_format_path(ctx.parsed)}'")
    if not ctx.create:
        raise TomlFileError("Cannot use [append] with state=absent; use [-1] to access the last entry")
    new_table = tomlkit.table()
    new_table.trivia.indent = "\n"
    aot.append(new_table)
    return new_table


def _navigate_aot(aot: AoT, index: IndexType, is_last: bool, ctx: NavContext, i: int) -> Table:
    """Navigate within an array of tables."""
    if index is None:
        return _get_aot_default(aot, ctx, i)
    if index == "append":
        return _handle_aot_append(aot, is_last, ctx, i)
    return _get_aot_at_index(aot, index, ctx, i)


def _navigate_existing_segment(
    current: Table | tomlkit.TOMLDocument, name: str, index: IndexType, ctx: NavContext, i: int
) -> Table | tomlkit.TOMLDocument:
    """Navigate into an existing table segment."""
    item = current[name]
    is_last = i == len(ctx.parsed) - 1
    if isinstance(item, AoT):
        return _navigate_aot(item, index, is_last, ctx, i)
    if isinstance(item, (Table, dict)):
        if index is not None:
            raise TomlFileError(f"'{_format_path(ctx.parsed, i + 1)}' is not an array of tables, cannot use index")
        return item
    raise TomlFileError(f"'{_format_path(ctx.parsed, i + 1)}' is not a table")


def navigate_to_table(
    doc: tomlkit.TOMLDocument, table_path: str | None, create: bool = False
) -> Table | tomlkit.TOMLDocument:
    """Navigate to a table in the document."""
    parsed = parse_table_path(table_path)
    if not parsed:
        return doc

    ctx = NavContext(parsed=parsed, create=create)
    current: Table | tomlkit.TOMLDocument = doc
    for i, (name, index) in enumerate(parsed):
        if name not in current:
            current = _create_table_segment(current, name, index, ctx, i)
        else:
            current = _navigate_existing_segment(current, name, index, ctx, i)
    return current


# =============================================================================
# Key Operations
# =============================================================================


def navigate_to_key_parent(
    target: Table | tomlkit.TOMLDocument, key: str
) -> tuple[Table | InlineTable | tomlkit.TOMLDocument, str]:
    """Navigate to the parent container of a key."""
    parts = key.split(".")
    if len(parts) == 1:
        return target, key

    parent: Table | InlineTable | tomlkit.TOMLDocument = target
    for i, part in enumerate(parts[:-1]):
        if part not in parent:
            new_table = tomlkit.inline_table()
            parent[part] = new_table
            parent = new_table
        else:
            item = parent[part]
            if isinstance(item, (Table, InlineTable, dict)):
                parent = item
            else:
                raise TomlFileError(f"'{'.'.join(parts[: i + 1])}' is not a table, cannot navigate further")

    return parent, parts[-1]


def _values_equal(a: t.Any, b: t.Any) -> bool:
    """Check if two values are equal."""
    if isinstance(a, Array) and isinstance(b, (Array, list)):
        if len(a) != len(b):
            return False
        return all(_values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, (InlineTable, Table)) and isinstance(b, (InlineTable, Table, dict)):
        if len(a) != len(b):
            return False
        return all(k in b and _values_equal(a[k], b[k]) for k in a)
    return a == b


def set_key_value(target: Table | tomlkit.TOMLDocument, key: str, value: t.Any, value_type: str = "auto") -> bool:
    """Set a key to a value in the target table."""
    parent, final_key = navigate_to_key_parent(target, key)
    converted_value = convert_value(value, value_type)

    if final_key in parent:
        existing = parent[final_key]
        if _values_equal(existing, converted_value):
            return False

    parent[final_key] = converted_value
    return True


def remove_key(target: Table | tomlkit.TOMLDocument, key: str) -> bool:
    """Remove a key from the target table."""
    parts = key.split(".")
    parent: Table | InlineTable | tomlkit.TOMLDocument = target
    for part in parts[:-1]:
        if part not in parent:
            return False
        item = parent[part]
        if isinstance(item, (Table, InlineTable, dict)):
            parent = item
        else:
            return False

    final_key = parts[-1]
    if final_key in parent:
        del parent[final_key]
        return True
    return False


# =============================================================================
# Table Removal
# =============================================================================


def remove_table(doc: tomlkit.TOMLDocument, table_path: str) -> bool:
    """Remove a table from the document."""
    parsed = parse_table_path(table_path)
    if not parsed:
        raise TomlFileError("Cannot remove document root")

    if len(parsed) == 1:
        parent: Table | tomlkit.TOMLDocument = doc
    else:
        try:
            parent_path = _format_path(parsed, len(parsed) - 1)
            parent = navigate_to_table(doc, parent_path, create=False)
        except TomlFileError:
            return False

    name, index = parsed[-1]
    if name not in parent:
        return False

    item = parent[name]
    if isinstance(item, AoT) and index is not None:
        return _remove_aot_entry(item, index)

    del parent[name]
    return True


def _remove_aot_entry(aot: AoT, index: int | t.Literal["append"]) -> bool:
    """Remove an entry from an array of tables."""
    if index == "append":
        raise TomlFileError("Cannot use [append] with state=absent; use [-1] to remove the last entry")
    if index == -1:
        if len(aot) > 0:
            del aot[-1]
            return True
        return False
    if 0 <= index < len(aot):
        del aot[index]
        return True
    raise TomlFileError(f"Array of tables index {index} out of range")


# =============================================================================
# Main TOML Operations (extracted for reduced nesting and statements)
# =============================================================================


def _init_diff(path: str, diff_enabled: bool, doc: tomlkit.TOMLDocument) -> dict[str, str]:
    """Initialize the diff dictionary."""
    diff = {
        "before": "",
        "after": "",
        "before_header": f"{path} (content)",
        "after_header": f"{path} (content)",
    }
    if diff_enabled:
        diff["before"] = tomlkit.dumps(doc)
    return diff


def _handle_present(doc: tomlkit.TOMLDocument, params: TomlParams, original_content: str) -> tuple[bool, str]:
    """Handle state=present operations."""
    if params.key:
        if params.value is None:
            raise TomlFileError("Parameter 'value' is required when state=present and key is specified")
        target = navigate_to_table(doc, params.table, create=True)
        changed = set_key_value(target, params.key, params.value, params.value_type)
        msg = "key added" if changed else "OK"
        return changed, msg

    if params.table:
        navigate_to_table(doc, params.table, create=True)
        new_content = tomlkit.dumps(doc)
        if new_content != original_content:
            return True, "table added"
    return False, "nothing to do"


def _handle_absent(doc: tomlkit.TOMLDocument, params: TomlParams) -> tuple[bool, str]:
    """Handle state=absent operations."""
    if params.key:
        try:
            target = navigate_to_table(doc, params.table, create=False)
            changed = remove_key(target, params.key)
            return changed, "key removed" if changed else "key not found"
        except TomlFileError:
            return False, "key not found"

    if params.table:
        changed = remove_table(doc, params.table)
        return changed, "table removed" if changed else "table not found"
    return False, "nothing to do"


def _write_if_changed(
    module: AnsibleModule, target_path: str, doc: tomlkit.TOMLDocument, changed: bool, backup: bool
) -> str | None:
    """Write the document to file if changed."""
    if not changed or module.check_mode:
        return None

    backup_file = None
    if backup and os.path.exists(target_path):
        backup_file = module.backup_local(target_path)

    destpath = os.path.dirname(target_path)
    if destpath and not os.path.exists(destpath):
        os.makedirs(destpath)

    content = tomlkit.dumps(doc)
    encoded_content = to_bytes(content)

    try:
        tmpfd, tmpfile = tempfile.mkstemp(dir=module.tmpdir)
        with os.fdopen(tmpfd, "wb") as f:
            f.write(encoded_content)
    except OSError:
        module.fail_json(msg="Unable to create temporary file", exception=traceback.format_exc())

    try:
        module.atomic_move(tmpfile, os.path.abspath(target_path))
    except OSError:
        module.fail_json(
            msg=f"Unable to move temporary file {tmpfile} to {target_path}", exception=traceback.format_exc()
        )

    return backup_file


def do_toml(module: AnsibleModule, params: TomlParams) -> tuple[bool, str | None, dict[str, str], str]:
    """Execute the main TOML file operation."""
    target_path = os.path.realpath(params.path) if params.follow and os.path.islink(params.path) else params.path
    doc = load_toml_document(target_path, params.create)

    diff = _init_diff(params.path, module._diff, doc)
    original_content = tomlkit.dumps(doc)

    if params.state == "present":
        changed, msg = _handle_present(doc, params, original_content)
    else:
        changed, msg = _handle_absent(doc, params)

    if module._diff:
        diff["after"] = tomlkit.dumps(doc)

    backup_file = _write_if_changed(module, target_path, doc, changed, params.backup)
    return changed, backup_file, diff, msg


# =============================================================================
# Module Entry Point
# =============================================================================


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True, aliases=["dest"]),
            table=dict(type="str"),
            key=dict(type="str", no_log=False),
            value=dict(type="raw"),
            value_type=dict(
                type="str",
                default="auto",
                choices=[
                    "auto",
                    "string",
                    "literal_string",
                    "multiline_string",
                    "multiline_literal_string",
                    "integer",
                    "hex_integer",
                    "octal_integer",
                    "binary_integer",
                    "float",
                    "boolean",
                    "datetime",
                    "date",
                    "time",
                    "array",
                    "inline_table",
                ],
            ),
            state=dict(type="str", default="present", choices=["absent", "present"]),
            backup=dict(type="bool", default=False),
            create=dict(type="bool", default=True),
            follow=dict(type="bool", default=False),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
    )

    deps.validate(module)

    params = TomlParams(
        path=module.params["path"],
        table=module.params["table"],
        key=module.params["key"],
        value=module.params["value"],
        value_type=module.params["value_type"],
        state=module.params["state"],
        backup=module.params["backup"],
        create=module.params["create"],
        follow=module.params["follow"],
    )

    try:
        changed, backup_file, diff, msg = do_toml(module, params)
    except TomlFileError as e:
        module.fail_json(msg=str(e))

    if not module.check_mode and os.path.exists(params.path):
        file_args = module.load_file_common_arguments(module.params)
        changed = module.set_fs_attributes_if_different(file_args, changed)

    results = dict(
        changed=changed,
        diff=diff,
        msg=msg,
        path=params.path,
    )
    if backup_file is not None:
        results["backup_file"] = backup_file

    module.exit_json(**results)


if __name__ == "__main__":
    main()

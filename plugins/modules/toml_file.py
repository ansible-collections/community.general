#!/usr/bin/python

# Copyright (c) 2026, Jose Drowne
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: toml_file
short_description: Manage individual settings in TOML files
version_added: 12.3.0
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
        (for example, V(products[0]) for the first entry, V(products[-1]) to append a new entry).
      - Nested arrays of tables are supported (for example, V(servers[1].databases[0])).
      - If omitted, the key is set at the document root level.
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
    table: products[-1]
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
msg:
  description: A message describing what was done.
  returned: always
  type: str
  sample: key added
backup_file:
  description: The name of the backup file that was created.
  returned: when O(backup=true) and file was modified
  type: str
  sample: /etc/myapp/config.toml.2026-01-17@12:34:56~
diff:
  description: The differences between the old and new file.
  returned: success and diff mode is enabled
  type: dict
  contains:
    before:
      description: The content of the file before modification.
      type: str
    after:
      description: The content of the file after modification.
      type: str
"""

import os
import re
import tempfile
import traceback
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("tomlkit"):
    import tomlkit
    from tomlkit.items import AoT, Array, InlineTable, Integer, Table, Trivia


class TomlFileError(Exception):
    pass


def parse_table_path(table_path: str | None) -> list[tuple[str, int | None]]:
    """Parse a table path with optional array indices.

    Examples:
        "products" -> [("products", None)]
        "products[0]" -> [("products", 0)]
        "products[-1]" -> [("products", -1)]
        "servers[1].databases[0]" -> [("servers", 1), ("databases", 0)]
        "server.database" -> [("server", None), ("database", None)]
    """
    if not table_path:
        return []

    result = []
    segment_pattern = re.compile(r"^([^\[\]]+)(?:\[(-?\d+)\])?$")

    for segment in table_path.split("."):
        match = segment_pattern.match(segment)
        if not match:
            raise TomlFileError(f"Invalid table path segment: '{segment}'")
        name = match.group(1)
        index_str = match.group(2)
        index = int(index_str) if index_str is not None else None
        result.append((name, index))

    return result


def _format_path(parsed: list[tuple[str, int | None]], up_to: int | None = None) -> str:
    """Format a parsed path back to string for error messages."""
    if up_to is None:
        up_to = len(parsed)
    return ".".join(name + (f"[{idx}]" if idx is not None else "") for name, idx in parsed[:up_to])


def load_toml_document(path, create=True):
    if not os.path.exists(path):
        if not create:
            raise TomlFileError(f"Destination {path} does not exist!")
        return tomlkit.document()

    try:
        with open(path, encoding="utf-8") as f:
            return tomlkit.parse(f.read())
    except Exception as e:
        raise TomlFileError(f"Failed to parse TOML file: {e}") from e


def navigate_to_table(doc, table_path, create=False):
    """Navigate to a table in the document.

    The table_path can include array indices using bracket notation:
    - "products[0]" - first entry in products array of tables
    - "products[-1]" - last entry (or append new if create=True)
    - "servers[1].databases[0]" - nested arrays
    """
    parsed = parse_table_path(table_path)
    if not parsed:
        return doc

    current = doc

    for i, (name, index) in enumerate(parsed):
        is_last = i == len(parsed) - 1

        if name not in current:
            if not create:
                raise TomlFileError(f"Table '{_format_path(parsed, i + 1)}' does not exist")

            if index == -1:
                new_table = tomlkit.table()
                aot = tomlkit.aot()
                aot.append(new_table)
                current[name] = aot
                current = new_table
            elif index is not None:
                raise TomlFileError(f"Cannot create table at index {index} - array of tables '{name}' does not exist")
            else:
                new_table = tomlkit.table()
                current[name] = new_table
                current = new_table
        else:
            item = current[name]
            if isinstance(item, AoT):
                if index is not None:
                    if index == -1:
                        if is_last and create:
                            new_table = tomlkit.table()
                            new_table.trivia.indent = '\n'
                            item.append(new_table)
                            current = new_table
                        else:
                            if len(item) == 0:
                                raise TomlFileError(f"Array of tables '{_format_path(parsed, i + 1)}' is empty")
                            current = item[-1]
                    elif 0 <= index < len(item):
                        current = item[index]
                    else:
                        raise TomlFileError(
                            f"Array of tables index {index} is out of range for '{_format_path(parsed, i + 1)}'"
                        )
                else:
                    if len(item) == 0:
                        raise TomlFileError(f"Array of tables '{_format_path(parsed, i + 1)}' is empty")
                    current = item[0]
            elif isinstance(item, (Table, dict)):
                if index is not None:
                    raise TomlFileError(f"'{_format_path(parsed, i + 1)}' is not an array of tables, cannot use index")
                current = item
            else:
                raise TomlFileError(f"'{_format_path(parsed, i + 1)}' is not a table")

    return current


def convert_value(value, value_type="auto"):
    if value_type == "auto":
        if isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            if "T" in value or " " in value:
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
            return value
        if isinstance(value, list):
            arr = tomlkit.array()
            for item in value:
                arr.append(convert_value(item, "auto"))
            return arr
        if isinstance(value, dict):
            tbl = tomlkit.inline_table()
            for k, v in value.items():
                tbl[k] = convert_value(v, "auto")
            return tbl
        return str(value)
    if value_type == "string":
        return str(value)
    if value_type == "literal_string":
        return tomlkit.string(str(value), literal=True)
    if value_type == "multiline_string":
        return tomlkit.string(str(value), multiline=True)
    if value_type == "multiline_literal_string":
        return tomlkit.string(str(value), literal=True, multiline=True)
    if value_type == "integer":
        return int(value)
    if value_type == "hex_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 16)
        return Integer(int_val, Trivia(), hex(int_val))
    if value_type == "octal_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 8)
        return Integer(int_val, Trivia(), oct(int_val))
    if value_type == "binary_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 2)
        return Integer(int_val, Trivia(), bin(int_val))
    if value_type == "float":
        if isinstance(value, str):
            return float(value.lower())
        return float(value)
    if value_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)
    if value_type == "datetime":
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if value_type == "date":
        from datetime import date as date_type

        if isinstance(value, date_type) and not isinstance(value, datetime):
            return tomlkit.date(value.isoformat())
        return tomlkit.date(str(value))
    if value_type == "time":
        from datetime import time as time_type

        if isinstance(value, time_type):
            return tomlkit.time(value.isoformat())
        return tomlkit.time(str(value))
    if value_type == "array":
        if isinstance(value, list):
            arr = tomlkit.array()
            for item in value:
                arr.append(convert_value(item, "auto"))
            return arr
        arr = tomlkit.array()
        arr.append(convert_value(value, "auto"))
        return arr
    if value_type == "inline_table":
        if not isinstance(value, dict):
            raise ValueError(f"Cannot convert {type(value).__name__} to inline_table")
        tbl = tomlkit.inline_table()
        for k, v in value.items():
            tbl[k] = convert_value(v, "auto")
        return tbl
    return value


def navigate_to_key_parent(target, key):
    parts = key.split(".")
    if len(parts) == 1:
        return target, key

    parent = target
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


def set_key_value(target, key, value, value_type="auto"):
    parent, final_key = navigate_to_key_parent(target, key)
    converted_value = convert_value(value, value_type)

    if final_key in parent:
        existing = parent[final_key]
        if _values_equal(existing, converted_value):
            return False

    parent[final_key] = converted_value
    return True


def _values_equal(a, b):
    if isinstance(a, Array) and isinstance(b, (Array, list)):
        if len(a) != len(b):
            return False
        return all(_values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, (InlineTable, Table)) and isinstance(b, (InlineTable, Table, dict)):
        if a.keys() != b.keys():
            return False
        return all(_values_equal(a[k], b[k]) for k in a)
    return a == b


def remove_key(target, key):
    parts = key.split(".")
    parent = target
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


def remove_table(doc, table_path):
    """Remove a table from the document.

    The table_path can include array indices using bracket notation:
    - "products[0]" - remove first entry from products array of tables
    - "products[-1]" - remove last entry
    - "products" - remove entire array of tables
    """
    parsed = parse_table_path(table_path)
    if not parsed:
        raise TomlFileError("Cannot remove document root")

    # Navigate to parent of the target
    if len(parsed) == 1:
        parent = doc
    else:
        try:
            parent_path = _format_path(parsed[:-1])
            parent = navigate_to_table(doc, parent_path, create=False)
        except TomlFileError:
            return False

    name, index = parsed[-1]

    if name not in parent:
        return False

    item = parent[name]
    if isinstance(item, AoT) and index is not None:
        if index == -1:
            if len(item) > 0:
                del item[-1]
                return True
            return False
        elif 0 <= index < len(item):
            del item[index]
            return True
        raise TomlFileError(f"Array of tables index {index} out of range")

    # If it's an AoT but no index specified, or a regular table, remove entirely
    del parent[name]
    return True


def do_toml(
    module,
    path,
    table,
    key,
    value,
    value_type,
    state,
    backup,
    create,
    follow,
):
    diff = {
        "before": "",
        "after": "",
        "before_header": f"{path} (content)",
        "after_header": f"{path} (content)",
    }

    if follow and os.path.islink(path):
        target_path = os.path.realpath(path)
    else:
        target_path = path

    doc = load_toml_document(target_path, create)

    if module._diff:
        diff["before"] = tomlkit.dumps(doc)

    original_content = tomlkit.dumps(doc)
    changed = False
    msg = "OK"

    if state == "present":
        if key:
            if value is None:
                raise TomlFileError("Parameter 'value' is required when state=present and key is specified")

            target = navigate_to_table(doc, table, create=True)
            changed = set_key_value(target, key, value, value_type)

            if changed:
                msg = "key added" if key not in target or changed else "key changed"
        else:
            if table:
                navigate_to_table(doc, table, create=True)
                new_content = tomlkit.dumps(doc)
                if new_content != original_content:
                    changed = True
                    msg = "table added"
            else:
                msg = "nothing to do"
    elif state == "absent":
        if key:
            try:
                target = navigate_to_table(doc, table, create=False)
                changed = remove_key(target, key)
                msg = "key removed" if changed else "key not found"
            except TomlFileError:
                msg = "key not found"
        else:
            if table:
                changed = remove_table(doc, table)
                msg = "table removed" if changed else "table not found"
            else:
                msg = "nothing to do"

    if module._diff:
        diff["after"] = tomlkit.dumps(doc)

    backup_file = None
    if changed and not module.check_mode:
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
            module.fail_json(msg="Unable to create temporary file", traceback=traceback.format_exc())

        try:
            module.atomic_move(tmpfile, os.path.abspath(target_path))
        except OSError:
            module.fail_json(
                msg=f"Unable to move temporary file {tmpfile} to {target_path}",
                traceback=traceback.format_exc(),
            )

    return changed, backup_file, diff, msg


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

    path = module.params["path"]
    table = module.params["table"]
    key = module.params["key"]
    value = module.params["value"]
    value_type = module.params["value_type"]
    state = module.params["state"]
    backup = module.params["backup"]
    create = module.params["create"]
    follow = module.params["follow"]

    try:
        changed, backup_file, diff, msg = do_toml(
            module, path, table, key, value, value_type, state, backup, create, follow
        )
    except TomlFileError as e:
        module.fail_json(msg=str(e))

    if not module.check_mode and os.path.exists(path):
        file_args = module.load_file_common_arguments(module.params)
        changed = module.set_fs_attributes_if_different(file_args, changed)

    results = dict(
        changed=changed,
        diff=diff,
        msg=msg,
        path=path,
    )
    if backup_file is not None:
        results["backup_file"] = backup_file

    module.exit_json(**results)


if __name__ == "__main__":
    main()

#!/usr/bin/python

# Copyright (c) 2026, Jose Drowne
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: toml_file
short_description: Manage individual settings in TOML files
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
      - Path to the TOML file; this file is created if required.
    type: path
    required: true
    aliases: [dest]
  table:
    description:
      - Table name in the TOML file.
      - Use dotted notation for nested tables (for example, V(server.database)).
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
      - YAML types are automatically converted to appropriate TOML types.
      - Use O(value_type) to force a specific type.
      - Required when O(state=present) and O(key) is specified.
    type: raw
  value_type:
    description:
      - Force the value to be a specific TOML type.
      - V(auto) automatically detects the type from the input value.
      - V(string) forces the value to be a TOML string.
      - V(literal_string) creates a TOML literal string (single quotes, no escape processing).
      - V(multiline_string) creates a TOML multi-line basic string (triple double quotes).
      - V(multiline_literal_string) creates a TOML multi-line literal string (triple single quotes).
      - V(integer) forces the value to be a TOML integer.
      - V(hex_integer) forces the value to be a TOML hexadecimal integer (for example, V(0xDEADBEEF)).
      - V(octal_integer) forces the value to be a TOML octal integer (for example, V(0o755)).
      - V(binary_integer) forces the value to be a TOML binary integer (for example, V(0b11010110)).
      - V(float) forces the value to be a TOML float. Supports V(inf), V(-inf), and V(nan).
      - V(boolean) forces the value to be a TOML boolean.
      - V(datetime) parses the value as an ISO 8601 offset or local datetime.
      - V(date) parses the value as a local date (for example, V(1979-05-27)).
      - V(time) parses the value as a local time (for example, V(07:32:00)).
      - V(array) ensures the value is a TOML array.
      - V(inline_table) ensures the value is a TOML inline table.
    type: str
    choices:
      - auto
      - string
      - literal_string
      - multiline_string
      - multiline_literal_string
      - integer
      - hex_integer
      - octal_integer
      - binary_integer
      - float
      - boolean
      - datetime
      - date
      - time
      - array
      - inline_table
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
  array_table_index:
    description:
      - For array of tables (C([[table]])), specify which entry to modify.
      - Use V(-1) to append a new entry to the array of tables.
      - Use V(0) for the first entry, V(1) for the second, and so on.
      - If the table is not an array of tables, this parameter is ignored.
    type: int
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
    table: products
    key: name
    value: Hammer
    array_table_index: -1

- name: Modify first entry in array of tables
  community.general.toml_file:
    path: /etc/myapp/config.toml
    table: products
    key: price
    value: 9.99
    array_table_index: 0

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
  returned: always
  type: str
  sample: /etc/myapp/config.toml
msg:
  description: A message describing what was done.
  returned: always
  type: str
  sample: key added
backup_file:
  description: The name of the backup file that was created.
  returned: when backup=true and file was modified
  type: str
  sample: /etc/myapp/config.toml.2026-01-17@12:34:56~
diff:
  description: The differences between the old and new file.
  returned: when diff mode is enabled
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
import tempfile
import traceback
from datetime import datetime
from typing import Any

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("tomlkit"):
    import tomlkit
    from tomlkit.items import AoT, Array, InlineTable, Integer, Table, Trivia


class TomlFileError(Exception):
    pass


def load_toml_document(path: str, create: bool = True) -> Any:
    if not os.path.exists(path):
        if not create:
            raise TomlFileError(f"Destination {path} does not exist!")
        return tomlkit.document()

    try:
        with open(path, encoding="utf-8") as f:
            return tomlkit.parse(f.read())
    except Exception as e:
        raise TomlFileError(f"Failed to parse TOML file: {e}") from e


def navigate_to_table(
    doc: Any, table_path: str | None, create: bool = False, array_table_index: int | None = None
) -> Any:
    if not table_path:
        return doc

    parts = table_path.split(".")
    current = doc

    for i, part in enumerate(parts):
        is_last = i == len(parts) - 1

        if part not in current:
            if not create:
                raise TomlFileError(f"Table '{'.'.join(parts[: i + 1])}' does not exist")

            if is_last and array_table_index == -1:
                new_table = tomlkit.table()
                aot = tomlkit.aot()
                aot.append(new_table)
                current[part] = aot
                current = new_table
            else:
                new_table = tomlkit.table()
                current[part] = new_table
                current = new_table
        else:
            item = current[part]
            if isinstance(item, AoT):
                if array_table_index is not None:
                    if array_table_index == -1:
                        if is_last:
                            new_table = tomlkit.table()
                            item.append(new_table)
                            current = new_table
                        else:
                            if len(item) == 0:
                                raise TomlFileError(f"Array of tables '{'.'.join(parts[: i + 1])}' is empty")
                            current = item[-1]
                    elif array_table_index < len(item):
                        current = item[array_table_index]
                    else:
                        raise TomlFileError(
                            f"Array of tables index {array_table_index} is out of range for '{'.'.join(parts[: i + 1])}'"
                        )
                else:
                    if len(item) == 0:
                        raise TomlFileError(f"Array of tables '{'.'.join(parts[: i + 1])}' is empty")
                    current = item[0]
            elif isinstance(item, (Table, dict)):
                current = item
            else:
                raise TomlFileError(f"'{'.'.join(parts[: i + 1])}' is not a table")

    return current


def convert_value(value: Any, value_type: str = "auto") -> Any:
    if value_type == "auto":
        if isinstance(value, (bool, int, float)):
            return value
        elif isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if "T" in value or " " in value:
                    return dt
            except (ValueError, AttributeError):
                pass
            return value
        elif isinstance(value, list):
            arr = tomlkit.array()
            for item in value:
                arr.append(convert_value(item, "auto"))
            return arr
        elif isinstance(value, dict):
            tbl = tomlkit.inline_table()
            for k, v in value.items():
                tbl[k] = convert_value(v, "auto")
            return tbl
        else:
            return str(value)
    elif value_type == "string":
        return str(value)
    elif value_type == "literal_string":
        return tomlkit.string(str(value), literal=True)
    elif value_type == "multiline_string":
        return tomlkit.string(str(value), multiline=True)
    elif value_type == "multiline_literal_string":
        return tomlkit.string(str(value), literal=True, multiline=True)
    elif value_type == "integer":
        return int(value)
    elif value_type == "hex_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 16)
        return Integer(int_val, Trivia(), hex(int_val))
    elif value_type == "octal_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 8)
        return Integer(int_val, Trivia(), oct(int_val))
    elif value_type == "binary_integer":
        int_val = int(value) if isinstance(value, int) else int(str(value), 2)
        return Integer(int_val, Trivia(), bin(int_val))
    elif value_type == "float":
        if isinstance(value, str):
            return float(value.lower())
        return float(value)
    elif value_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)
    elif value_type == "datetime":
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    elif value_type == "date":
        from datetime import date as date_type

        if isinstance(value, date_type) and not isinstance(value, datetime):
            return tomlkit.date(value.isoformat())
        return tomlkit.date(str(value))
    elif value_type == "time":
        from datetime import time as time_type

        if isinstance(value, time_type):
            return tomlkit.time(value.isoformat())
        return tomlkit.time(str(value))
    elif value_type == "array":
        if isinstance(value, list):
            arr = tomlkit.array()
            for item in value:
                arr.append(convert_value(item, "auto"))
            return arr
        arr = tomlkit.array()
        arr.append(convert_value(value, "auto"))
        return arr
    elif value_type == "inline_table":
        if isinstance(value, dict):
            tbl = tomlkit.inline_table()
            for k, v in value.items():
                tbl[k] = convert_value(v, "auto")
            return tbl
        raise ValueError(f"Cannot convert {type(value).__name__} to inline_table")
    else:
        return value


def navigate_to_key_parent(target: Any, key: str) -> tuple[Any, str]:
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


def set_key_value(target: Any, key: str, value: Any, value_type: str = "auto") -> bool:
    parent, final_key = navigate_to_key_parent(target, key)
    converted_value = convert_value(value, value_type)

    if final_key in parent:
        existing = parent[final_key]
        if _values_equal(existing, converted_value):
            return False

    parent[final_key] = converted_value
    return True


def _values_equal(a: Any, b: Any) -> bool:
    if isinstance(a, Array) and isinstance(b, (Array, list)):
        a_list = list(a)
        b_list = list(b) if isinstance(b, Array) else b
        if len(a_list) != len(b_list):
            return False
        return all(_values_equal(x, y) for x, y in zip(a_list, b_list))
    elif isinstance(a, (InlineTable, Table)) and isinstance(b, (InlineTable, Table, dict)):
        a_dict = dict(a)
        b_dict = dict(b) if isinstance(b, (InlineTable, Table)) else b
        if set(a_dict.keys()) != set(b_dict.keys()):
            return False
        return all(_values_equal(a_dict[k], b_dict[k]) for k in a_dict)
    else:
        try:
            return a == b
        except Exception:
            return False


def remove_key(target: Any, key: str) -> bool:
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


def remove_table(doc: Any, table_path: str | None, array_table_index: int | None = None) -> bool:
    if not table_path:
        raise TomlFileError("Cannot remove document root")

    parts = table_path.split(".")
    if len(parts) == 1:
        if parts[0] in doc:
            item = doc[parts[0]]
            if isinstance(item, AoT) and array_table_index is not None:
                if array_table_index == -1:
                    if len(item) > 0:
                        del item[-1]
                        return True
                    return False
                elif 0 <= array_table_index < len(item):
                    del item[array_table_index]
                    return True
                raise TomlFileError(f"Array of tables index {array_table_index} out of range")
            del doc[parts[0]]
            return True
        return False

    try:
        parent = navigate_to_table(doc, ".".join(parts[:-1]), create=False)
    except TomlFileError:
        return False

    final_part = parts[-1]
    if final_part in parent:
        item = parent[final_part]
        if isinstance(item, AoT) and array_table_index is not None:
            if array_table_index == -1:
                if len(item) > 0:
                    del item[-1]
                    return True
                return False
            elif 0 <= array_table_index < len(item):
                del item[array_table_index]
                return True
            raise TomlFileError(f"Array of tables index {array_table_index} out of range")
        del parent[final_part]
        return True
    return False


def do_toml(
    module: AnsibleModule,
    path: str,
    table: str | None,
    key: str | None,
    value: Any,
    value_type: str,
    state: str,
    backup: bool,
    create: bool,
    follow: bool,
    array_table_index: int | None,
) -> tuple[bool, str | None, dict[str, str], str]:
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

    try:
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

                target = navigate_to_table(doc, table, create=True, array_table_index=array_table_index)
                changed = set_key_value(target, key, value, value_type)

                if changed:
                    msg = "key added" if key not in target or changed else "key changed"
            else:
                if table:
                    navigate_to_table(doc, table, create=True, array_table_index=array_table_index)
                    new_content = tomlkit.dumps(doc)
                    if new_content != original_content:
                        changed = True
                        msg = "table added"
                else:
                    msg = "nothing to do"
        elif state == "absent":
            if key:
                try:
                    target = navigate_to_table(doc, table, create=False, array_table_index=array_table_index)
                    changed = remove_key(target, key)
                    msg = "key removed" if changed else "key not found"
                except TomlFileError:
                    msg = "key not found"
            else:
                if table:
                    changed = remove_table(doc, table, array_table_index)
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

    except TomlFileError as e:
        return False, None, diff, str(e)


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
            array_table_index=dict(type="int"),
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
    array_table_index = module.params["array_table_index"]

    changed, backup_file, diff, msg = do_toml(
        module, path, table, key, value, value_type, state, backup, create, follow, array_table_index
    )

    if msg and msg not in [
        "OK",
        "key added",
        "key changed",
        "key removed",
        "key not found",
        "table added",
        "table removed",
        "table not found",
        "nothing to do",
    ]:
        module.fail_json(msg=msg)

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

#!/usr/bin/python

# Copyright (c) 2025, Shahar Golshani (@shahargolshani)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: file_remove

short_description: Remove files matching a pattern from a directory

description:
  - This module removes files from a specified directory that match a given pattern.
    The pattern can include wildcards and regular expressions.
  - By default, only files in the specified directory are removed (non-recursive).
    Use the O(recursive) option to search and remove files in subdirectories.

version_added: "12.1.0"

author:
  - Shahar Golshani (@shahargolshani)

extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  path:
    description:
      - Path to the directory where files should be removed.
      - This must be an existing directory.
    type: path
    required: true

  pattern:
    description:
      - Pattern to match files for removal.
      - Supports wildcards (V(*), V(?), V([seq]), V([!seq])) for glob-style matching.
      - Use O(use_regex=true) to interpret this as a regular expression instead.
    type: str
    required: true

  use_regex:
    description:
      - If V(true), O(pattern) is interpreted as a regular expression.
      - If V(false), O(pattern) is interpreted as a glob-style wildcard pattern.
    type: bool
    default: false

  recursive:
    description:
      - If V(true), search for files recursively in subdirectories.
      - If V(false), only files in the specified directory are removed.
    type: bool
    default: false

  file_type:
    description:
      - Type of files to remove.
    type: str
    choices:
      file: remove only regular files.
      link: remove only symbolic links.
      any: remove both files and symbolic links.
    default: file

notes:
  - Directories are never removed by this module, only files and optionally symbolic links.
  - This module will not follow symbolic links when O(recursive=true).
  - Be careful with patterns that might match many files, especially with O(recursive=true).
"""

EXAMPLES = r"""
- name: Remove all log files from /var/log
  community.general.file_remove:
    path: /var/log
    pattern: "*.log"

- name: Remove all temporary files recursively
  community.general.file_remove:
    path: /tmp/myapp
    pattern: "*.tmp"
    recursive: true

- name: Remove files matching a regex pattern
  community.general.file_remove:
    path: /data/backups
    pattern: "backup_[0-9]{8}\\.tar\\.gz"
    use_regex: true

- name: Remove both files and symbolic links
  community.general.file_remove:
    path: /opt/app/cache
    pattern: "cache_*"
    file_type: any

- name: Remove all files starting with 'test_' (check mode)
  community.general.file_remove:
    path: /home/user/tests
    pattern: "test_*"
  check_mode: true
"""

RETURN = r"""
removed_files:
  description: List of files that were removed.
  type: list
  elements: str
  returned: always
  sample: ['/var/log/app.log', '/var/log/error.log']

files_count:
  description: Number of files removed.
  type: int
  returned: success
  sample: 2

path:
  description: The directory path that was searched.
  type: str
  returned: success
  sample: /var/log
"""


import glob
import os
import re
import typing as t

from ansible.module_utils.basic import AnsibleModule


def find_matching_files(
    path: str, pattern: str, use_regex: bool, recursive: bool, file_type: t.Literal["file", "link", "any"]
) -> list[str]:
    """Find all files matching the pattern in the given path."""
    matching_files = []

    if use_regex:
        # Use regular expression matching
        regex = re.compile(pattern)
        if recursive:
            for root, _dirs, files in os.walk(path, followlinks=False):
                for filename in files:
                    if regex.match(filename) or regex.search(filename):
                        full_path = os.path.join(root, filename)
                        if should_include_file(full_path, file_type):
                            matching_files.append(full_path)
        else:
            for filename in os.listdir(path):
                if regex.match(filename) or regex.search(filename):
                    full_path = os.path.join(path, filename)
                    if should_include_file(full_path, file_type):
                        matching_files.append(full_path)
    else:
        # Use glob pattern matching
        if recursive:
            glob_pattern = os.path.join(path, "**", pattern)
            matching_files = [f for f in glob.glob(glob_pattern, recursive=True) if should_include_file(f, file_type)]
        else:
            glob_pattern = os.path.join(path, pattern)
            matching_files = [f for f in glob.glob(glob_pattern) if should_include_file(f, file_type)]

    return sorted(matching_files)


def should_include_file(file_path: str, file_type: t.Literal["file", "link", "any"]) -> bool:
    """Determine if a file should be included based on its type."""
    # Never include directories
    if os.path.isdir(file_path):
        return False

    is_link = os.path.islink(file_path)
    is_file = os.path.isfile(file_path)

    if file_type == "file":
        return is_file and not is_link
    elif file_type == "link":
        return is_link
    else:
        return is_file or is_link


def remove_files(module: AnsibleModule, files: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Remove the specified files and return results."""
    removed_files = []
    failed_files = []

    for file_path in files:
        try:
            if module.check_mode:
                # In check mode, just verify the file exists
                if os.path.exists(file_path):
                    removed_files.append(file_path)
                else:
                    raise FileNotFoundError()
            else:
                # Actually remove the file
                os.remove(file_path)
                removed_files.append(file_path)
        except FileNotFoundError:
            module.warn(f"File not found (likely removed by other process): {file_path}")
        except OSError as e:
            failed_files.append((file_path, str(e)))

    return removed_files, failed_files


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True),
            pattern=dict(type="str", required=True),
            use_regex=dict(type="bool", default=False),
            recursive=dict(type="bool", default=False),
            file_type=dict(type="str", default="file", choices=["file", "link", "any"]),
        ),
        supports_check_mode=True,
    )

    path: str = module.params["path"]
    pattern: str = module.params["pattern"]
    use_regex: bool = module.params["use_regex"]
    recursive: bool = module.params["recursive"]
    file_type: t.Literal["file", "link", "any"] = module.params["file_type"]

    # Validate that the path exists and is a directory
    if not os.path.exists(path):
        module.fail_json(msg=f"Path does not exist: {path}")

    if not os.path.isdir(path):
        module.fail_json(msg=f"Path is not a directory: {path}")

    # Validate regex pattern if use_regex is true
    if use_regex:
        try:
            re.compile(pattern)
        except re.error as e:
            module.fail_json(msg=f"Invalid regular expression pattern: {e}")

    # Find matching files
    try:
        matching_files = find_matching_files(path, pattern, use_regex, recursive, file_type)
    except OSError as e:
        module.fail_json(msg=str(e))

    # Prepare diff information
    diff = dict(before=dict(files=matching_files), after=dict(files=[]))

    # Remove the files
    removed_files, failed_files = remove_files(module, matching_files)

    # Prepare result
    changed = len(removed_files) > 0

    result = dict(
        changed=changed,
        removed_files=removed_files,
        files_count=len(removed_files),
        path=path,
        msg=f"Removed {len(removed_files)} file(s) matching pattern '{pattern}'",
    )

    # Add diff if in diff mode
    if module._diff:
        result["diff"] = diff

    # Report any failures
    if failed_files:
        failure_msg = "; ".join([f"{f}: {e}" for f, e in failed_files])
        module.fail_json(
            msg=f"Failed to remove some files: {failure_msg}",
            removed_files=removed_files,
            failed_files=[f for f, e in failed_files],
        )

    module.exit_json(**result)


if __name__ == "__main__":
    main()

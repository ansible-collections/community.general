#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prevent unwanted files from being added to the source tree."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import os.path
import sys


def main():
    """Main entry point."""
    paths = sys.argv[1:] or sys.stdin.read().splitlines()

    allowed_extensions = (
        '.cs',
        '.ps1',
        '.psm1',
        '.py',
    )

    skip_paths = set([
    ])

    skip_directories = (
    )

    yaml_directories = (
        'plugins/test/',
        'plugins/filter/',
    )

    for path in paths:
        if path in skip_paths:
            continue

        if any(path.startswith(skip_directory) for skip_directory in skip_directories):
            continue

        if os.path.islink(path):
            print('%s: is a symbolic link' % (path, ))
        elif not os.path.isfile(path):
            print('%s: is not a regular file' % (path, ))

        ext = os.path.splitext(path)[1]

        if ext in ('.yml', ) and any(path.startswith(yaml_directory) for yaml_directory in yaml_directories):
            continue

        if ext not in allowed_extensions:
            print('%s: extension must be one of: %s' % (path, ', '.join(allowed_extensions)))


if __name__ == '__main__':
    main()

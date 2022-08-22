#!/usr/bin/env python
# Copyright (c) 2022, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prevent files without a correct license identifier from being added to the source tree."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import glob
import sys


def format_license_list(licenses):
    if not licenses:
        return '(empty)'
    return ', '.join(['"%s"' % license for license in licenses])


def find_licenses(filename, relax=False):
    spdx_license_identifiers = []
    other_license_identifiers = []
    has_copyright = False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip()
                if 'Copyright ' in line:
                    has_copyright = True
                if 'Copyright: ' in line:
                    print('%s: found copyright line with "Copyright:". Please remove the colon.' % (filename, ))
                if 'SPDX-FileCopyrightText: ' in line:
                    has_copyright = True
                idx = line.find('SPDX-License-Identifier: ')
                if idx >= 0:
                    lic_id = line[idx + len('SPDX-License-Identifier: '):]
                    spdx_license_identifiers.extend(lic_id.split(' OR '))
                if 'GNU General Public License' in line:
                    if 'v3.0+' in line:
                        other_license_identifiers.append('GPL-3.0-or-later')
                    if 'version 3 or later' in line:
                        other_license_identifiers.append('GPL-3.0-or-later')
                if 'Simplified BSD License' in line:
                    other_license_identifiers.append('BSD-2-Clause')
                if 'Apache License 2.0' in line:
                    other_license_identifiers.append('Apache-2.0')
                if 'PSF License' in line or 'Python-2.0' in line:
                    other_license_identifiers.append('PSF-2.0')
                if 'MIT License' in line:
                    other_license_identifiers.append('MIT')
    except Exception as exc:
        print('%s: error while processing file: %s' % (filename, exc))
    if len(set(spdx_license_identifiers)) < len(spdx_license_identifiers):
        print('%s: found identical SPDX-License-Identifier values' % (filename, ))
    if other_license_identifiers and set(other_license_identifiers) != set(spdx_license_identifiers):
        print('%s: SPDX-License-Identifier yielded the license list %s, while manual guessing yielded the license list %s' % (
            filename, format_license_list(spdx_license_identifiers), format_license_list(other_license_identifiers)))
    if not has_copyright and not relax:
        print('%s: found no copyright notice' % (filename, ))
    return sorted(spdx_license_identifiers)


def main():
    """Main entry point."""
    paths = sys.argv[1:] or sys.stdin.read().splitlines()

    # The following paths are allowed to have no license identifier
    no_comments_allowed = [
        'changelogs/fragments/*.yml',
        'changelogs/fragments/*.yaml',
    ]

    # These files are completely ignored
    ignore_paths = [
        '.ansible-test-timeout.json',
        '.reuse/dep5',
        'LICENSES/*.txt',
        'COPYING',
    ]

    no_comments_allowed = [fn for pattern in no_comments_allowed for fn in glob.glob(pattern)]
    ignore_paths = [fn for pattern in ignore_paths for fn in glob.glob(pattern)]

    valid_licenses = [license_file[len('LICENSES/'):-len('.txt')] for license_file in glob.glob('LICENSES/*.txt')]

    for path in paths:
        if path.startswith('./'):
            path = path[2:]
        if path in ignore_paths or path.startswith('tests/output/'):
            continue
        if os.stat(path).st_size == 0:
            continue
        if not path.endswith('.license') and os.path.exists(path + '.license'):
            path = path + '.license'
        valid_licenses_for_path = valid_licenses
        if path.startswith('plugins/') and not path.startswith(('plugins/modules/', 'plugins/module_utils/', 'plugins/doc_fragments/')):
            valid_licenses_for_path = [license for license in valid_licenses if license == 'GPL-3.0-or-later']
        licenses = find_licenses(path, relax=path in no_comments_allowed)
        if not licenses:
            if path not in no_comments_allowed:
                print('%s: must have at least one license' % (path, ))
        else:
            for license in licenses:
                if license not in valid_licenses_for_path:
                    print('%s: found not allowed license "%s", must be one of %s' % (
                        path, license, format_license_list(valid_licenses_for_path)))


if __name__ == '__main__':
    main()

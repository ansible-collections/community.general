#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check extra collection docs with antsibull-docs."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import glob
import sys

import yaml


def main():
    """Main entry point."""
    with open('.azure-pipelines/azure-pipelines.yml', 'rb') as f:
        azp = yaml.safe_load(f)

    allowed_targets = set(['azp/generic/1'])
    for stage in azp['stages']:
        if stage['stage'].startswith(('Sanity', 'Unit', 'Generic', 'Summary')):
            continue
        for job in stage['jobs']:
            for group in job['parameters']['groups']:
                allowed_targets.add('azp/posix/{0}'.format(group))

    paths = glob.glob("tests/integration/targets/*/aliases")

    has_errors = False
    for path in paths:
        targets = []
        skip = False
        with open(path, 'r') as f:
            for line in f:
                if '#' in line:
                    line = line[:line.find('#')]
                line = line.strip()
                if line.startswith('needs/'):
                    continue
                if line.startswith('skip/'):
                    continue
                if line.startswith('cloud/'):
                    continue
                if line.startswith('context/'):
                    continue
                if line in ('unsupported', 'disabled', 'hidden'):
                    skip = True
                if line in ('destructive', ):
                    continue
                if '/' not in line:
                    continue
                targets.append(line)
        if skip:
            continue
        if not targets:
            if 'targets/setup_' in path:
                continue
            print('%s: %s' % (path, 'found no targets'))
            has_errors = True
        for target in targets:
            if target not in allowed_targets:
                print('%s: %s' % (path, 'found invalid target "{0}"'.format(target)))
                has_errors = True

    return 1 if has_errors else 0


if __name__ == '__main__':
    sys.exit(main())

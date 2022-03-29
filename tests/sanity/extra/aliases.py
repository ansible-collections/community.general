#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Check extra collection docs with antsibull-lint."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys

import yaml


def main():
    """Main entry point."""
    paths = sys.argv[1:] or sys.stdin.read().splitlines()
    paths = [path for path in paths if path.endswith('/aliases')]

    with open('.azure-pipelines/azure-pipelines.yml', 'rb') as f:
        azp = yaml.safe_load(f)

    allowed_targets = set(['shippable/cloud/group1'])
    for stage in azp['stages']:
        if stage['stage'].startswith(('Sanity', 'Unit', 'Cloud', 'Summary')):
            continue
        for job in stage['jobs']:
            for group in job['parameters']['groups']:
                allowed_targets.add('shippable/posix/group{0}'.format(group))

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
        for target in targets:
            if target not in allowed_targets:
                print('%s: %s' % (path, 'found invalid target "{0}"'.format(target)))


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check extra collection docs with antsibull-docs."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import subprocess


def main():
    """Main entry point."""
    env = os.environ.copy()
    suffix = ':{env}'.format(env=env["ANSIBLE_COLLECTIONS_PATH"]) if 'ANSIBLE_COLLECTIONS_PATH' in env else ''
    env['ANSIBLE_COLLECTIONS_PATH'] = '{root}{suffix}'.format(root=os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))), suffix=suffix)
    p = subprocess.run(
        ['antsibull-docs', 'lint-collection-docs', '--plugin-docs', '--skip-rstcheck', '.'],
        env=env,
        check=False,
    )
    if p.returncode not in (0, 3):
        print('{0}:0:0: unexpected return code {1}'.format(sys.argv[0], p.returncode))


if __name__ == '__main__':
    main()

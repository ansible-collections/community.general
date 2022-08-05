#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Prepends a relative timestamp to each input line from stdin and writes it to stdout."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import time


def main():
    """Main program entry point."""
    start = time.time()

    sys.stdin.reconfigure(errors='surrogateescape')
    sys.stdout.reconfigure(errors='surrogateescape')

    for line in sys.stdin:
        seconds = time.time() - start
        sys.stdout.write('%02d:%02d %s' % (seconds // 60, seconds % 60, line))
        sys.stdout.flush()


if __name__ == '__main__':
    main()

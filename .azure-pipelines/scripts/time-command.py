#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Prepends a relative timestamp to each input line from stdin and writes it to stdout."""

from __future__ import annotations

import sys
import time


def main():
    """Main program entry point."""
    start = time.time()

    sys.stdin.reconfigure(errors="surrogateescape")
    sys.stdout.reconfigure(errors="surrogateescape")

    for line in sys.stdin:
        seconds = int(time.time() - start)
        sys.stdout.write(f"{seconds // 60:02}:{seconds % 60:02} {line}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

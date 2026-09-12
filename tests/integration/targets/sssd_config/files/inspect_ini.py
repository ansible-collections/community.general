# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Read an sssd.conf independently of SSSDConfig and emit JSON."""

from __future__ import annotations

import configparser
import hashlib
import json
import os
import stat
import sys


def main():
    path = sys.argv[1]

    with open(path, "rb") as stream:
        raw = stream.read()

    parser = configparser.RawConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    parser.read_string(raw.decode("utf-8"))

    sections = {section: dict(parser.items(section, raw=True)) for section in parser.sections()}

    result = {
        "mode": format(stat.S_IMODE(os.stat(path).st_mode), "04o"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "sections": sections,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from io import StringIO

from ruamel.yaml import YAML


def main() -> None:
    yaml = YAML(typ='rt')
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Load
    data = yaml.load(sys.stdin)

    # Dump
    sio = StringIO()
    yaml.dump(data, sio)
    print(sio.getvalue().rstrip('\n'))


if __name__ == "__main__":
    main()

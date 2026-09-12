# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Report capabilities from the SSSDConfig schema installed on the target."""

from __future__ import annotations

import json
import platform
import sys

import SSSDConfig as sssdconfig_module  # type: ignore[import-not-found]
from SSSDConfig import SSSDConfig  # type: ignore[import-not-found]


def main():
    config = SSSDConfig()
    config.import_config(sys.argv[1])

    sssd_options = sorted(config.get_service("sssd").list_options())

    result = {
        "module_file": sssdconfig_module.__file__,
        "python": platform.python_version(),
        "sssd_options": sssd_options,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

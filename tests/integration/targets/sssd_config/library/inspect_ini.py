#!/usr/bin/python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = ""
EXAMPLES = ""
RETURN = ""

import configparser
import hashlib
import os
import stat

from ansible.module_utils.basic import AnsibleModule


class CaseSensitiveRawConfigParser(configparser.RawConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True),
        ),
        supports_check_mode=True,
    )
    path = module.params["path"]

    try:
        with open(path, "rb") as stream:
            raw = stream.read()

        parser = CaseSensitiveRawConfigParser(
            interpolation=None,
            strict=False,
        )
        parser.read_string(raw.decode("utf-8"))

        sections = {
            section: dict(parser.items(section, raw=True))
            for section in parser.sections()
        }
        mode = format(stat.S_IMODE(os.stat(path).st_mode), "04o")
        sha256 = hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeError, configparser.Error) as exc:
        module.fail_json(msg=f"Unable to inspect {path}: {exc}")

    module.exit_json(
        changed=False,
        mode=mode,
        sha256=sha256,
        sections=sections,
    )


if __name__ == "__main__":
    main()

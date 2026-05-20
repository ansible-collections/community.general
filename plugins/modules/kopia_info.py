#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_info
short_description: Gather information about a Kopia repository
author:
  - Dexter Le (@munchtoast)
version_added: "13.0.0"
description:
  - Gather read-only information about the current Kopia repository connection and throttle settings.
  - Runs C(kopia repository status) and C(kopia repository throttle get).
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  password:
    description:
      - Repository password used to decrypt repository contents.
    type: str
  config:
    description:
      - Path to the Kopia config file for this repository connection.
      - Defaults to the Kopia default config path when not set.
    type: path
"""

EXAMPLES = r"""
- name: Gather Kopia info
  community.general.kopia_info:
    config: /etc/kopia/root.config
  register: result

- name: Show repository status
  ansible.builtin.debug:
    msg: "{{ result.repository_status }}"

- name: Show throttle settings
  ansible.builtin.debug:
    msg: "{{ result.throttle }}"
"""

RETURN = r"""
repository_status:
  description: Output of C(kopia repository status).
  type: str
  returned: always
  sample: "Connected to repository: s3:/my-bucket/\nConfig file: /etc/kopia/root.config\n..."
throttle:
  description: Output of C(kopia repository throttle get) showing current throttle limits.
  type: str
  returned: always
  sample: "upload-bytes-per-second: 0\ndownload-bytes-per-second: 0"
"""

from ansible_collections.community.general.plugins.module_utils._kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    kopia_runner,
)
from ansible_collections.community.general.plugins.module_utils._module_helper import ModuleHelper


class KopiaInfo(ModuleHelper):
    module = dict(
        argument_spec=dict(**KOPIA_COMMON_ARGUMENT_SPEC),
        supports_check_mode=True,
    )
    output_params = ["repository_status", "throttle"]

    def __init_module__(self):
        self.runner = kopia_runner(self.module)

    def _process_command_output(self, cli_action=""):
        def process(rc, out, err):
            if rc != 0:
                self.do_raise(f"kopia {cli_action} failed with error (rc={rc}): {err}")
            return out.rstrip() if out else None

        return process

    def __run__(self):
        with self.runner(
            "cli_action config",
            output_process=self._process_command_output("repository status"),
        ) as ctx:
            self.vars.set(
                "repository_status",
                ctx.run(cli_action=["repository", "status"]),
                output=True,
            )

        with self.runner(
            "cli_action config",
            output_process=self._process_command_output("repository throttle get"),
        ) as ctx:
            self.vars.set(
                "throttle",
                ctx.run(cli_action=["repository", "throttle", "get"]),
                output=True,
            )


def main():
    KopiaInfo.execute()


if __name__ == "__main__":
    main()

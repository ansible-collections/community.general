#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: drweb_info
version_added: 13.6.0
short_description: Query Dr.Web antivirus through drweb-ctl
description:
  - Retrieve information from Dr.Web for Unix through the C(drweb-ctl)
    command-line utility.
  - Supports license, application, virus database, threat, quarantine,
    configuration and log information.
  - For operations that change state (updating virus databases, scanning,
    reloading configuration, setting configuration keys), use the
    M(community.general.drweb_ctl) module.
author:
  - "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - drweb-ctl >= 11.0
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  command:
    description:
      - Dr.Web information query to perform.
    type: str
    required: true
    choices:
      license:
        - Show the current license information.
      appinfo:
        - Show information about the installed Dr.Web application.
      baseinfo:
        - Show information about the virus databases and scan engine.
      threats:
        - List detected threats.
      quarantine:
        - List quarantined objects.
      cfshow:
        - Show one configuration key when O(parameter) is set,
          or all configuration values otherwise.
      log:
        - Show the last O(lines) lines of the Dr.Web log.
  parameter:
    description:
      - Configuration key to show.
      - Optional for O(command=cfshow).
    type: str
  lines:
    description:
      - Number of last log lines to return for O(command=log).
    type: int
    default: 20
"""

EXAMPLES = r"""
- name: Get Dr.Web license information
  community.general.drweb_info:
    command: license
  register: drweb_license

- name: Show installed Dr.Web application information
  community.general.drweb_info:
    command: appinfo

- name: Show virus database information
  community.general.drweb_info:
    command: baseinfo
  register: baseinfo

- name: Show detected threats
  community.general.drweb_info:
    command: threats
  register: threats

- name: Show quarantine
  community.general.drweb_info:
    command: quarantine

- name: Show one configuration value
  community.general.drweb_info:
    command: cfshow
    parameter: Update.LogLevel
  register: cf

- name: Show the last 50 log lines
  community.general.drweb_info:
    command: log
    lines: 50
  register: drweb_log
"""

RETURN = r"""
drweb_version:
  description:
    - Dr.Web version reported by C(drweb-ctl --version).
  returned: always
  type: str
  sample: "13.0.0"
license:
  description:
    - Parsed license information.
  returned: when O(command=license)
  type: dict
appinfo:
  description:
    - Parsed application information.
  returned: when O(command=appinfo)
  type: dict
baseinfo:
  description:
    - Parsed virus database information.
  returned: when O(command=baseinfo)
  type: dict
threats:
  description:
    - List of detected threats.
  returned: when O(command=threats)
  type: list
  elements: str
quarantine:
  description:
    - List of quarantined objects.
  returned: when O(command=quarantine)
  type: list
  elements: str
cfvalue:
  description:
    - Value returned by C(cfshow).
  returned: when O(command=cfshow)
  type: str
log_lines:
  description:
    - Last N lines of the Dr.Web log.
  returned: when O(command=log)
  type: list
  elements: str
"""

import re

from ansible.module_utils.basic import AnsibleModule

VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+){0,2})")
KV_RE = re.compile(r"^\s*([^:=]+?)\s*[:=]\s*(.*?)\s*$")


class DrwebCtlInfoModule:
    """Dr.Web information module using drweb-ctl (read-only commands)."""

    def __init__(self, module: AnsibleModule, drweb_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.drweb_bin = drweb_bin
        self.command = self.params["command"]
        self.parameter = self.params["parameter"]
        self.lines = self.params["lines"]

    def get_drweb_version(self) -> str:
        rc, stdout, _stderr = self.module.run_command(
            [self.drweb_bin, "--version"],
            check_rc=False,
        )
        if rc == 0 and stdout:
            match = VERSION_RE.search(stdout)
            if match:
                return match.group(1)
        return "unknown"

    def validate_parameters(self) -> None:
        if self.command == "cfshow":
            if self.parameter is not None and not self.parameter:
                self.module.fail_json(msg="'parameter' must not be empty when command=cfshow")

        if self.command == "log" and self.lines < 1:
            self.module.fail_json(msg="'lines' must be greater than zero when command=log")

    def build_command(self) -> list[str]:
        if self.command in {"license", "appinfo", "baseinfo", "threats", "quarantine"}:
            return [self.drweb_bin, self.command]

        if self.command == "cfshow":
            cmd = [self.drweb_bin, "cfshow"]
            if self.parameter:
                cmd.append(self.parameter)
            return cmd

        if self.command == "log":
            return [self.drweb_bin, "log", "-s", str(self.lines)]

        self.module.fail_json(msg=f"Unsupported command: {self.command}")

    @staticmethod
    def parse_kv(stdout: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in stdout.splitlines():
            match = KV_RE.match(line)
            if match:
                result[match.group(1).strip()] = match.group(2).strip()
        return result

    @staticmethod
    def parse_baseinfo(stdout: str) -> dict[str, object]:
        result: dict[str, object] = {}
        result.update(DrwebCtlInfoModule.parse_kv(stdout))
        result["loaded"] = "Virus databases are not loaded" not in stdout
        return result

    @staticmethod
    def parse_threats(stdout: str) -> list[str]:
        result = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            lowered = line.lower()
            if lowered.startswith(("threat", "no threat", "total", "threats:")):
                continue
            result.append(line)
        return result

    @staticmethod
    def parse_quarantine(stdout: str) -> list[str]:
        result = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            lowered = line.lower()
            if lowered.startswith(("quarantine", "no ", "total", "quarantined")):
                continue
            result.append(line)
        return result

    def execute(self) -> dict[str, object]:
        cmd = self.build_command()
        _rc, stdout, _stderr = self.module.run_command(cmd, check_rc=False)

        result: dict[str, object] = {
            "changed": False,
            "drweb_version": self.get_drweb_version(),
        }

        if self.command == "license":
            result["license"] = self.parse_kv(stdout)
        elif self.command == "appinfo":
            result["appinfo"] = self.parse_kv(stdout)
        elif self.command == "baseinfo":
            result["baseinfo"] = self.parse_baseinfo(stdout)
        elif self.command == "threats":
            result["threats"] = self.parse_threats(stdout)
        elif self.command == "quarantine":
            result["quarantine"] = self.parse_quarantine(stdout)
        elif self.command == "cfshow":
            result["cfvalue"] = stdout.strip()
        elif self.command == "log":
            result["log_lines"] = stdout.splitlines()

        return result

    def apply(self) -> dict[str, object]:
        self.validate_parameters()
        return self.execute()


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(
                type="str",
                required=True,
                choices=[
                    "license",
                    "appinfo",
                    "baseinfo",
                    "threats",
                    "quarantine",
                    "cfshow",
                    "log",
                ],
            ),
            parameter=dict(type="str"),
            lines=dict(type="int", default=20),
        ),
        supports_check_mode=True,
    )

    drweb_bin = module.get_bin_path("drweb-ctl", required=True)
    drweb_module = DrwebCtlInfoModule(module, drweb_bin)
    result = drweb_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

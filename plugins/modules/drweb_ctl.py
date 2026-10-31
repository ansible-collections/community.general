#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: drweb_ctl
version_added: 13.6.0
short_description: Manage Dr.Web antivirus through drweb-ctl
description:
  - Perform state-changing operations in Dr.Web for Unix through the
    C(drweb-ctl) command-line utility.
  - Supports virus database updates, on-demand scanning, configuration
    reload and setting configuration keys.
  - For operations that only retrieve information (license, application
    and virus database information, threats, quarantine, showing
    configuration values and reading logs), use the
    M(community.general.drweb_info) module.
author:
  - "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - drweb-ctl >= 11.0
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    details:
      - C(update) and C(reload) report C(changed=true) in check mode without
        executing the command.
      - C(cfset) checks the current configuration value and reports whether
        a change would be required.
      - C(scan) is not executed in check mode.
    support: full
  diff_mode:
    support: none
options:
  command:
    description:
      - Dr.Web operation to perform.
    type: str
    required: true
    choices:
      update:
        - Update Dr.Web virus databases.
      scan:
        - Scan a file or directory.
        - Requires O(path).
      reload:
        - Reload the Dr.Web configuration.
      cfset:
        - Set a configuration key to a value.
        - Requires O(parameter) and O(value).
  path:
    description:
      - Path to scan.
      - Required when O(command=scan).
    type: path
  parameter:
    description:
      - Configuration key to set.
      - Required when O(command=cfset).
    type: str
  value:
    description:
      - Value to assign to O(parameter).
      - Required when O(command=cfset).
    type: str
"""

EXAMPLES = r"""
- name: Update Dr.Web virus databases
  community.general.drweb_ctl:
    command: update

- name: Scan a mounted directory
  community.general.drweb_ctl:
    command: scan
    path: /opt/drweb_work/admin
  register: scan_result

- name: Set Update.LogLevel to debug
  community.general.drweb_ctl:
    command: cfset
    parameter: Update.LogLevel
    value: debug

- name: Reload Dr.Web configuration
  community.general.drweb_ctl:
    command: reload
"""

RETURN = r"""
drweb_version:
  description:
    - Dr.Web version reported by C(drweb-ctl --version).
  returned: when a command is executed
  type: str
  sample: "13.0.0"
cmd:
  description:
    - Command that was executed or would be executed.
  returned: always
  type: list
  elements: str
  sample:
    - /opt/drweb.com/bin/drweb-ctl
    - scan
    - /opt/drweb_work/admin
rc:
  description:
    - Return code of the C(drweb-ctl) invocation.
  returned: when a command is executed
  type: int
stdout:
  description:
    - Raw stdout of the command.
  returned: when a command is executed
  type: str
stderr:
  description:
    - Raw stderr of the command.
  returned: when a command is executed
  type: str
scan_result:
  description:
    - Best-effort parsed scan summary.
  returned: when O(command=scan)
  type: dict
current_value:
  description:
    - Current value of the configuration key before change.
  returned: when O(command=cfset)
  type: str
  sample: "info"
desired_value:
  description:
    - Desired value of the configuration key.
  returned: when O(command=cfset) and check mode is enabled
  type: str
  sample: "debug"
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule

VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+){0,2})")
KV_RE = re.compile(r"^\s*([^:=]+?)\s*[:=]\s*(.*?)\s*$")


class DrwebCtlModule:
    """Dr.Web controller using drweb-ctl (state-changing commands only)."""

    SIDE_EFFECT_COMMANDS = {"update", "reload"}

    def __init__(self, module: AnsibleModule, drweb_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.drweb_bin = drweb_bin
        self.command = self.params["command"]
        self.path = self.params["path"]
        self.parameter = self.params["parameter"]
        self.value = self.params["value"]

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
        if self.command == "scan":
            if not self.path:
                self.module.fail_json(msg="'path' is required when command=scan")
            if not os.path.exists(self.path):
                self.module.fail_json(msg=f"Scan path does not exist: {self.path}")

        if self.command == "cfset":
            if not self.parameter:
                self.module.fail_json(msg="'parameter' is required when command=cfset")
            if self.value is None:
                self.module.fail_json(msg="'value' is required when command=cfset")

    def build_command(self, command: str | None = None) -> list[str]:
        command = command or self.command

        if command in self.SIDE_EFFECT_COMMANDS:
            return [self.drweb_bin, command]

        if command == "scan":
            return [self.drweb_bin, "scan", self.path]

        if command == "cfset":
            return [self.drweb_bin, "cfset", self.parameter, str(self.value)]

        self.module.fail_json(msg=f"Unsupported command: {command}")

    @staticmethod
    def parse_scan(stdout: str) -> dict[str, object]:
        result: dict[str, object] = {
            "scanned": 0,
            "infected": 0,
            "suspicious": 0,
            "raw_summary": "",
        }

        for line in stdout.splitlines():
            stripped = line.strip()

            match = re.search(r"(?:scanned|total)[^\d]*(\d+)", stripped, re.IGNORECASE)
            if match:
                result["scanned"] = int(match.group(1))

            match = re.search(r"infected[^\d]*(\d+)", stripped, re.IGNORECASE)
            if match:
                result["infected"] = int(match.group(1))

            match = re.search(r"suspicious[^\d]*(\d+)", stripped, re.IGNORECASE)
            if match:
                result["suspicious"] = int(match.group(1))

            lowered = stripped.lower()
            if "infected" in lowered or "suspicious" in lowered:
                result["raw_summary"] = stripped

        return result

    @staticmethod
    def parse_cfvalue(stdout: str, parameter: str) -> str | None:
        expected = parameter.strip()
        for line in stdout.splitlines():
            match = KV_RE.match(line)
            if match and match.group(1).strip() == expected:
                return match.group(2).strip()
        return None

    def get_current_cfvalue(self) -> str | None:
        _rc, stdout, _stderr = self.module.run_command(
            [self.drweb_bin, "cfshow", self.parameter],
            check_rc=True,
        )
        return self.parse_cfvalue(stdout, self.parameter)

    def execute_command(self) -> dict[str, object]:
        cmd = self.build_command()
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)

        result: dict[str, object] = {
            "changed": self.command in self.SIDE_EFFECT_COMMANDS,
            "rc": rc,
            "stdout": stdout,
            "stderr": stderr,
            "cmd": cmd,
            "drweb_version": self.get_drweb_version(),
        }

        if self.command == "scan":
            result["scan_result"] = self.parse_scan(stdout)

        return result

    def execute_cfset(self) -> dict[str, object]:
        current_value = self.get_current_cfvalue()
        desired_value = str(self.value)
        cmd = self.build_command("cfset")

        if current_value == desired_value:
            result: dict[str, object] = {
                "changed": False,
                "cmd": cmd,
                "current_value": current_value,
            }
            if not self.module.check_mode:
                result["drweb_version"] = self.get_drweb_version()
            return result

        if self.module.check_mode:
            return {
                "changed": True,
                "cmd": cmd,
                "current_value": current_value,
                "desired_value": desired_value,
            }

        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)
        return {
            "changed": True,
            "rc": rc,
            "stdout": stdout,
            "stderr": stderr,
            "cmd": cmd,
            "drweb_version": self.get_drweb_version(),
        }

    def apply(self) -> dict[str, object]:
        self.validate_parameters()

        if self.command == "cfset":
            return self.execute_cfset()

        cmd = self.build_command()

        if self.module.check_mode:
            if self.command == "scan":
                return {
                    "changed": False,
                    "cmd": cmd,
                    "msg": "Check mode: scan was not executed because scanning is an inspection operation.",
                }
            if self.command in self.SIDE_EFFECT_COMMANDS:
                return {
                    "changed": True,
                    "cmd": cmd,
                    "msg": f"Check mode: would run '{self.command}'.",
                }

        return self.execute_command()


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(
                type="str",
                required=True,
                choices=["update", "scan", "reload", "cfset"],
            ),
            path=dict(type="path"),
            parameter=dict(type="str"),
            value=dict(type="str"),
        ),
        supports_check_mode=True,
    )

    drweb_bin = module.get_bin_path("drweb-ctl", required=True)
    drweb_module = DrwebCtlModule(module, drweb_bin)
    result = drweb_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

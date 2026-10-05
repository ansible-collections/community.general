#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: drweb_ctl
version_added: 13.5.0
short_description: Manage Dr.Web antivirus through drweb-ctl
description:
  - Manage Dr.Web for Unix through the C(drweb-ctl) command-line utility.
  - Supports license and application information, virus database updates,
    on-demand scanning, threats, quarantine, configuration and logs.
author:
  - "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - drweb-ctl >= 11.0
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    description:
      - Read-only commands do not make changes and are skipped in check mode.
      - C(cfset) checks the current configuration value and reports whether
        a change would be required.
      - C(update) and C(reload) report C(changed=true) in check mode without
        executing the command.
      - C(scan) is not executed in check mode.
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the Dr.Web operation for identification.
    type: str
    required: true
  command:
    description:
      - Dr.Web operation to perform.
    type: str
    required: true
    choices:
      license:
        - Show the current license information.
      appinfo:
        - Show information about the installed Dr.Web application.
      baseinfo:
        - Show information about the virus databases and scan engine.
      update:
        - Update Dr.Web virus databases.
      scan:
        - Scan a file or directory.
        - Requires O(path).
      threats:
        - List detected threats.
      quarantine:
        - List quarantined objects.
      reload:
        - Reload the Dr.Web configuration.
      cfshow:
        - Show one configuration key when O(key) is set,
          or all configuration values otherwise.
      cfset:
        - Set a configuration key to a value.
        - Requires O(key) and O(value).
      log:
        - Show the last O(lines) lines of the Dr.Web log.
  path:
    description:
      - Path to scan.
      - Required when O(command=scan).
    type: path
  parameter:
    description:
      - Configuration key.
      - Required for O(command=cfset).
      - Optional for O(command=cfshow).
    type: str
  value:
    description:
      - Value to assign to O(parameter).
      - Required for O(command=cfset).
    type: str
  lines:
    description:
      - Number of last log lines to return for O(command=log).
    type: int
    default: 20
"""

EXAMPLES = r"""
- name: Get Dr.Web license information
  community.general.drweb_ctl:
    name: license
    command: license
  register: drweb_license

- name: Update Dr.Web virus databases
  community.general.drweb_ctl:
    name: update-bases
    command: update

- name: Scan a mounted directory
  community.general.drweb_ctl:
    name: scan-admin
    command: scan
    path: /opt/drweb_work/admin
  register: scan_result

- name: Show detected threats
  community.general.drweb_ctl:
    name: threats
    command: threats
  register: threats

- name: Show quarantine
  community.general.drweb_ctl:
    name: quarantine
    command: quarantine

- name: Show one configuration value
  community.general.drweb_ctl:
    name: update-log-level
    command: cfshow
    parameter: Update.LogLevel
  register: cf

- name: Set Update.LogLevel to debug
  community.general.drweb_ctl:
    name: update-log-level
    command: cfset
    parameter: Update.LogLevel
    value: debug

- name: Reload Dr.Web configuration
  community.general.drweb_ctl:
    name: reload
    command: reload

- name: Show the last 50 log lines
  community.general.drweb_ctl:
    name: log
    command: log
    lines: 50
  register: drweb_log
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
scan_result:
  description:
    - Best-effort parsed scan summary.
  returned: when O(command=scan)
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

import os
import re

from ansible.module_utils.basic import AnsibleModule

VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+){0,2})")
KV_RE = re.compile(r"^\s*([^:=]+?)\s*[:=]\s*(.*?)\s*$")


class DrwebCtlModule:
    """Dr.Web controller using drweb-ctl."""

    READ_ONLY_COMMANDS = {
        "license",
        "appinfo",
        "baseinfo",
        "threats",
        "quarantine",
        "cfshow",
        "log",
    }

    SIDE_EFFECT_COMMANDS = {
        "update",
        "reload",
    }

    def __init__(self, module: AnsibleModule, drweb_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.drweb_bin = drweb_bin
        self.command = self.params["command"]
        self.path = self.params["path"]
        self.parameter = self.params["parameter"]
        self.value = self.params["value"]
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

        if self.command == "cfshow":
            if self.parameter is not None and not self.parameter:
                self.module.fail_json(msg="'parameter' must not be empty when command=cfshow")

        if self.command == "log" and self.lines < 1:
            self.module.fail_json(msg="'lines' must be greater than zero when command=log")

    def build_command(self, command: str | None = None) -> list[str]:
        command = command or self.command

        if command in {
            "license",
            "appinfo",
            "baseinfo",
            "update",
            "threats",
            "quarantine",
            "reload",
        }:
            return [self.drweb_bin, command]

        if command == "scan":
            return [self.drweb_bin, "scan", self.path]

        if command == "cfshow":
            cmd = [self.drweb_bin, "cfshow"]
            if self.parameter:
                cmd.append(self.parameter)
            return cmd

        if command == "cfset":
            return [
                self.drweb_bin,
                "cfset",
                self.parameter,
                str(self.value),
            ]

        if command == "log":
            return [
                self.drweb_bin,
                "log",
                "-s",
                str(self.lines),
            ]

        self.module.fail_json(msg=f"Unsupported command: {command}")

    @staticmethod
    def parse_kv(stdout: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in stdout.splitlines():
            match = KV_RE.match(line)
            if match:
                result[match.group(1).strip()] = match.group(2).strip()
        return result

    def parse_license(self, stdout: str) -> dict[str, str]:
        return self.parse_kv(stdout)

    def parse_appinfo(self, stdout: str) -> dict[str, str]:
        return self.parse_kv(stdout)

    def parse_baseinfo(self, stdout: str) -> dict[str, object]:
        result: dict[str, object] = self.parse_kv(stdout)
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

            match = re.search(
                r"(?:scanned|total)[^\d]*(\d+)",
                stripped,
                re.IGNORECASE,
            )
            if match:
                result["scanned"] = int(match.group(1))

            match = re.search(
                r"infected[^\d]*(\d+)",
                stripped,
                re.IGNORECASE,
            )
            if match:
                result["infected"] = int(match.group(1))

            match = re.search(
                r"suspicious[^\d]*(\d+)",
                stripped,
                re.IGNORECASE,
            )
            if match:
                result["suspicious"] = int(match.group(1))

            lowered = stripped.lower()
            if "infected" in lowered or "suspicious" in lowered:
                result["raw_summary"] = stripped

        return result

    @staticmethod
    def parse_cfvalue(stdout: str, key: str) -> str | None:
        expected_key = key.strip()

        for line in stdout.splitlines():
            match = KV_RE.match(line)
            if not match:
                continue

            current_key = match.group(1).strip()
            if current_key == expected_key:
                return match.group(2).strip()

        return None

    def get_current_cfvalue(self) -> str | None:
        rc, stdout, stderr = self.module.run_command(
            [self.drweb_bin, "cfshow", self.parameter],
            check_rc=True,
        )

        if rc != 0:
            self.module.fail_json(msg=f"Failed to read configuration key '{self.parameter}': {stderr}")

        return self.parse_cfvalue(stdout, self.parameter)

    def execute_command(self) -> dict[str, object]:
        cmd = self.build_command()

        rc, stdout, stderr = self.module.run_command(
            cmd,
            check_rc=True,
        )

        result: dict[str, object] = {
            "changed": self.command in self.SIDE_EFFECT_COMMANDS,
            "rc": rc,
            "stdout": stdout,
            "stderr": stderr,
            "cmd": cmd,
            "drweb_version": self.get_drweb_version(),
        }

        if self.command == "license":
            result["license"] = self.parse_license(stdout)
        elif self.command == "appinfo":
            result["appinfo"] = self.parse_appinfo(stdout)
        elif self.command == "baseinfo":
            result["baseinfo"] = self.parse_baseinfo(stdout)
        elif self.command == "threats":
            result["threats"] = self.parse_threats(stdout)
        elif self.command == "quarantine":
            result["quarantine"] = self.parse_quarantine(stdout)
        elif self.command == "scan":
            result["scan_result"] = self.parse_scan(stdout)
        elif self.command == "cfshow":
            result["cfvalue"] = stdout.strip()
        elif self.command == "log":
            result["log_lines"] = stdout.splitlines()

        return result

    def execute_cfset(self) -> dict[str, object]:
        current_value = self.get_current_cfvalue()
        desired_value = str(self.value)
        cmd = self.build_command("cfset")

        if current_value == desired_value:
            return {
                "changed": False,
                "cmd": cmd,
                "current_value": current_value,
                "drweb_version": self.get_drweb_version(),
            }

        if self.module.check_mode:
            return {
                "changed": True,
                "cmd": cmd,
                "current_value": current_value,
                "desired_value": desired_value,
            }

        rc, stdout, stderr = self.module.run_command(
            cmd,
            check_rc=True,
        )

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
            if self.command in self.READ_ONLY_COMMANDS:
                return {
                    "changed": False,
                    "cmd": cmd,
                    "msg": (f"Check mode: read-only command '{self.command}' skipped."),
                }

            if self.command == "scan":
                return {
                    "changed": False,
                    "cmd": cmd,
                    "msg": ("Check mode: scan was not executed because scanning is an inspection operation."),
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
            name=dict(type="str", required=True),
            command=dict(
                type="str",
                required=True,
                choices=[
                    "license",
                    "appinfo",
                    "baseinfo",
                    "update",
                    "scan",
                    "threats",
                    "quarantine",
                    "reload",
                    "cfshow",
                    "cfset",
                    "log",
                ],
            ),
            path=dict(type="path"),
            parameter=dict(type="str"),
            value=dict(type="str"),
            lines=dict(type="int", default=20),
        ),
        supports_check_mode=True,
    )

    drweb_bin = module.get_bin_path(
        "drweb-ctl",
        required=True,
    )

    drweb_module = DrwebCtlModule(
        module,
        drweb_bin,
    )

    result = drweb_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

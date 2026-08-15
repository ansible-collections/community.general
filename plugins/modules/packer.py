#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: packer
version_added: 13.4.0
short_description: Manage HashiCorp Packer builds
description:
  - Manage Packer builds and templates.
  - Supports building and initializing Packer templates.
  - In check_mode, runs C(packer validate) instead of building.
author: "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - packer >= 1.7.0
attributes:
  check_mode:
    description: In check_mode, validates the template instead of building.
    support: full
options:
  name:
    description:
      - Name of the Packer build configuration (for identification).
    type: str
    required: true
  state:
    description:
      - Desired operation to perform.
      - "build: builds the image from template (or validates in check_mode)."
      - "init: initializes the template (installs required plugins)."
    type: str
    required: true
    choices: [build, init]
  template:
    description:
      - Path to the Packer template file or directory.
      - Required for all states.
    type: path
    required: false
  variables:
    description:
      - Dictionary of variables to pass to Packer (C(-var)).
    type: dict
    required: false
    default: {}
  var_files:
    description:
      - List of variable files to load (C(-var-file)).
    type: list
    elements: path
    required: false
    default: []
  only:
    description:
      - Build only the specified builders (C(-only)).
    type: list
    elements: str
    required: false
  except_builders:
    description:
      - Build all builders except the specified ones (C(-except)).
    type: list
    elements: str
    required: false
    aliases: [except]
  force:
    description:
      - Force rebuilding (passes C(-force) flag).
    type: bool
    default: false
  parallel:
    description:
      - Enable parallel building (C(-parallel=false) if V(false)).
    type: bool
    default: true
  color:
    description:
      - Disable colored output (C(-no-color) if V(false)).
    type: bool
    default: true
  machine_readable:
    description:
      - Output in machine-readable format (C(-machine-readable) if V(true)).
      - Recommended for parsing artifacts reliably.
    type: bool
    default: false
  chdir:
    description:
      - Change to this directory before running Packer.
    type: path
    required: false
  cleanup:
    description:
      - Clean up temporary files after build (C(-cleanup)).
    type: bool
    default: false
  log_level:
    description:
      - Set the log level (C(--log-level)).
    type: str
    choices: [trace, debug, info, warn, error]
    default: info
"""

EXAMPLES = r"""
- name: Initialize Packer template (install plugins)
  community.general.packer:
    name: init-template
    state: init
    template: aws-ubuntu.pkr.hcl

- name: Build AWS AMI with Packer (or validate in check_mode)
  community.general.packer:
    name: my-ami
    state: build
    template: aws-ubuntu.pkr.hcl
    variables:
      aws_region: us-west-2
      instance_type: t2.micro
    force: false

- name: Validate template using check_mode
  community.general.packer:
    name: validate-check
    state: build
    template: template.pkr.hcl
    var_files:
      - dev.pkrvars.hcl
      - common.pkrvars.hcl
  check_mode: true

- name: Build with force rebuild
  community.general.packer:
    name: force-build
    state: build
    template: template.pkr.hcl
    force: true
    parallel: false
    machine_readable: true

- name: Build only specific builders
  community.general.packer:
    name: selective-build
    state: build
    template: template.pkr.hcl
    only:
      - amazon-ebs.builder1
      - virtualbox-iso.builder2

- name: Build local artifact (VirtualBox)
  community.general.packer:
    name: local-build
    state: build
    template: virtualbox.pkr.hcl
    force: true
"""

RETURN = r"""
cmd:
  description: Full command line executed
  returned: always
  type: str
  sample: "packer build -force template.pkr.hcl"
packer_version:
  description: Packer version used
  returned: always
  type: str
  sample: "1.9.4"
artifacts:
  description: List of created artifacts
  returned: when state is build and build successful (not in check_mode)
  type: list
  elements: dict
  sample:
    - type: amazon-ebs
      name: ami-12345678
      build_index: 0
artifacts_count:
  description: Number of artifacts created
  returned: when state is build and build successful
  type: int
  sample: 1
started:
  description: Timestamp when the build started (UTC)
  returned: when state is build
  type: str
  sample: "2024-01-15T10:30:00Z"
"""

import os
import re
from datetime import datetime, timezone

from ansible.module_utils.basic import AnsibleModule


class PackerModule:
    """Packer configuration and build manager."""

    def __init__(self, module: AnsibleModule, packer_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.packer_bin = packer_bin
        self.result: dict[str, object] = {
            "changed": False,
            "stdout": "",
            "stderr": "",
            "rc": 0,
            "cmd": "",
            "packer_version": "",
        }

        self.state = self.params["state"]
        self.template = self.params.get("template")
        self.variables = self.params.get("variables") or {}
        self.var_files = self.params.get("var_files") or []
        self.only = self.params.get("only")
        self.except_builders = self.params.get("except_builders")
        self.force = self.params.get("force")
        self.parallel = self.params.get("parallel")
        self.color = self.params.get("color")
        self.machine_readable = self.params.get("machine_readable")
        self.chdir = self.params.get("chdir")
        self.cleanup = self.params.get("cleanup")
        self.log_level = self.params.get("log_level", "info")

    def _check_packer_version(self) -> str:
        """Get Packer version using module.run_command."""
        try:
            rc, stdout, _stderr = self.module.run_command(
                [self.packer_bin, "version"],
                check_rc=False,
            )
            if rc == 0 and stdout:
                version_line = stdout.splitlines()[0]
                match = re.search(r"(\d+\.\d+\.\d+)", version_line)
                if match:
                    return match.group(1)
                return version_line.strip()
            return "unknown"
        except Exception:
            return "unknown"

    def _validate_parameters(self) -> None:
        """Validate module parameters."""
        if self.chdir and not os.path.exists(self.chdir):
            self.module.fail_json(msg=f"Working directory does not exist: {self.chdir}")

        def path_exists(path):
            if self.chdir:
                full_path = os.path.join(self.chdir, path)
                return os.path.exists(full_path)
            return os.path.exists(path)

        if self.template and not path_exists(self.template):
            self.module.fail_json(
                msg=f"Template file/directory does not exist: {self.template} "
                f"(relative to chdir: {self.chdir if self.chdir else '.'})"
            )

        for var_file in self.var_files:
            if not path_exists(var_file):
                self.module.fail_json(
                    msg=f"Variable file does not exist: {var_file} "
                    f"(relative to chdir: {self.chdir if self.chdir else '.'})"
                )

    def _build_command(self, command: str) -> list[str]:
        """Build the Packer command line."""
        cmd = [self.packer_bin]

        if self.log_level != "info":
            cmd.extend(["--log-level", self.log_level])

        cmd.append(command)

        if command in ["build", "init"] and self.template:
            cmd.append(self.template)

        if command == "build":
            if self.force:
                cmd.append("-force")
            if not self.parallel:
                cmd.append("-parallel=false")
            if self.cleanup:
                cmd.append("-cleanup")

        if command != "init":
            if not self.color:
                cmd.append("-no-color")
            if self.machine_readable:
                cmd.append("-machine-readable")

        if command in ["build", "validate"]:
            for key, value in self.variables.items():
                if isinstance(value, str) and (" " in value or '"' in value):
                    cmd.extend(["-var", f'{key}="{value}"'])
                else:
                    cmd.extend(["-var", f"{key}={value}"])

            for var_file in self.var_files:
                cmd.extend(["-var-file", var_file])

        if self.only and command == "build":
            cmd.extend(["-only", ",".join(self.only)])
        if self.except_builders and command == "build":
            cmd.extend(["-except", ",".join(self.except_builders)])

        return cmd

    def _parse_machine_readable_output(self, output: str) -> list[dict[str, str]]:
        """
        Parse machine-readable output for artifacts.
        Real format: artifact,<build_index>,<artifact_type>,<artifact_id>
        Example: artifact,0,amazon-ebs,ami-12345678
        """
        artifacts = []
        for line in output.splitlines():
            if not line.startswith("artifact,"):
                continue

            parts = line.split(",")
            if len(parts) >= 4:
                artifact = {
                    "type": parts[2],
                    "name": parts[3],
                    "build_index": parts[1],
                }
                if artifact["name"]:
                    artifacts.append(artifact)
        return artifacts

    def _parse_build_output(self, output: str) -> list[dict[str, str]]:
        """Parse build output to extract artifacts."""
        artifacts = []

        if self.machine_readable:
            return self._parse_machine_readable_output(output)

        pattern = re.compile(r"^-->\s+(.+?):\s+(.+)$")
        lines = output.splitlines()
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                builder = match.group(1).strip()
                artifact_desc = match.group(2).strip()
                artifacts.append(
                    {
                        "type": builder,
                        "name": artifact_desc,
                    }
                )
            elif "ami-" in line and ("created" in line or "AMIs" in line):
                ami_match = re.search(r"(ami-[a-zA-Z0-9]+)", line)
                if ami_match:
                    artifacts.append(
                        {
                            "type": "amazon-ebs",
                            "name": ami_match.group(1),
                        }
                    )

        return artifacts

    def _execute_packer(self, command: str) -> dict[str, object]:
        """Execute Packer command."""
        cmd = self._build_command(command)
        self.result["cmd"] = " ".join(cmd)

        cwd = self.chdir or os.getcwd()

        try:
            start_time = datetime.now(timezone.utc).isoformat() + "Z"

            rc, stdout, stderr = self.module.run_command(
                cmd,
                cwd=cwd,
                check_rc=False,
            )

            artifacts = []
            artifacts_count = 0
            if command == "build" and rc == 0:
                artifacts = self._parse_build_output(stdout)
                artifacts_count = len(artifacts)

            changed = False
            if command == "build":
                changed = True
            elif command in ["init", "validate"]:
                changed = False

            result_dict = {
                "changed": changed,
                "stdout": stdout,
                "stderr": stderr,
                "rc": rc,
                "cmd": " ".join(cmd),
                "packer_version": self._check_packer_version(),
            }

            if command == "build":
                result_dict["started"] = start_time
                result_dict["artifacts"] = artifacts
                result_dict["artifacts_count"] = artifacts_count

            if rc != 0:
                result_dict["failed"] = True
                self.module.fail_json(msg="Packer command failed", **result_dict)

            return result_dict

        except Exception as e:
            self.module.fail_json(
                msg=f"Error executing Packer: {e}",
                cmd=" ".join(cmd),
            )

    def apply(self) -> dict[str, object]:
        """Apply Packer configuration and build if needed."""
        self._validate_parameters()

        if self.state == "init":
            return self._execute_packer("init")

        if self.state == "build":
            if self.module.check_mode:
                result = self._execute_packer("validate")
                result["changed"] = False
                result["msg"] = "Check mode: template validation completed, no build performed."
                return result
            else:
                result = self._execute_packer("build")
                self.result.update(result)
                return self.result

        self.module.fail_json(msg=f"Unsupported state: {self.state}")


def main() -> None:
    """Main function."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str",
                required=True,
                choices=["build", "init"],
            ),
            template=dict(type="path", required=False),
            variables=dict(type="dict", required=False, default={}),
            var_files=dict(type="list", elements="path", required=False, default=[]),
            only=dict(type="list", elements="str", required=False),
            except_builders=dict(
                type="list",
                elements="str",
                required=False,
                aliases=["except"],
            ),
            force=dict(type="bool", required=False, default=False),
            parallel=dict(type="bool", required=False, default=True),
            color=dict(type="bool", required=False, default=True),
            machine_readable=dict(type="bool", required=False, default=False),
            chdir=dict(type="path", required=False),
            cleanup=dict(type="bool", required=False, default=False),
            log_level=dict(
                type="str",
                required=False,
                choices=["trace", "debug", "info", "warn", "error"],
                default="info",
            ),
        ),
        mutually_exclusive=[
            ("only", "except_builders"),
        ],
        required_if=[
            ["state", "build", ["template"]],
            ["state", "init", ["template"]],
        ],
        supports_check_mode=True,
    )

    packer_bin = module.get_bin_path("packer", required=True)

    packer_module = PackerModule(module, packer_bin)
    result = packer_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

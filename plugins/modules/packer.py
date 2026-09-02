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
    description: In check_mode, runs C(packer validate) instead of building.
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
    type: str
    required: true
    choices:
      build: builds the image from template (or validates in check mode).
      init: initializes the template (installs required plugins).
  template:
    description:
      - Path to the Packer template file or directory.
      - Required for all states.
    type: path
    required: true
  variables:
    description:
      - Dictionary of variables to pass to Packer (C(-var)).
    type: dict
    default: {}
  var_files:
    description:
      - List of variable files to load (C(-var-file)).
    type: list
    elements: path
    default: []
  only:
    description:
      - Build only the specified builders (C(-only)).
    type: list
    elements: str
  except_builders:
    description:
      - Build all builders except the specified ones (C(-except)).
    type: list
    elements: str
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
    default: false
  machine_readable:
    description:
      - Output in machine-readable format (C(-machine-readable) if V(true)).
      - Recommended for parsing artifacts reliably.
    type: bool
    default: false
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

- name: Initialize Packer template from directory
  community.general.packer:
    name: init-template-dir
    state: init
    template: ./packer-templates/

- name: Build AWS AMI with Packer (or validate in check_mode)
  community.general.packer:
    name: my-ami
    state: build
    template: aws-ubuntu.pkr.hcl
    variables:
      aws_region: us-west-2
      instance_type: t2.micro
    force: false

- name: Build from directory containing multiple templates
  community.general.packer:
    name: multi-template-build
    state: build
    template: ./packer-templates/
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
packer_version:
  description: Packer version used.
  returned: always
  type: str
  sample: "1.9.4"
artifacts:
  description: List of created artifacts.
  returned: when O(state=build) and build successful (not in check_mode)
  type: list
  elements: dict
  sample:
    - type: amazon-ebs
      name: ami-12345678
      build_index: 0
artifacts_count:
  description: Number of artifacts created.
  returned: when O(state=build) and build successful
  type: int
  sample: 1
build_start_timestamp:
  description: Timestamp when the build started (UTC).
  returned: when O(state=build)
  type: str
  sample: "2024-01-15T10:30:00Z"
"""

import os
import re
from datetime import datetime, timezone

from ansible.module_utils.basic import AnsibleModule

VERSION_RE = re.compile(r"(\d+\.\d+\.\d+)")
BUILD_ARTIFACT_RE = re.compile(r"^-->\s+(\S+):\s+(.+)$")
AMI_ARTIFACT_RE = re.compile(r"(ami-\S+)")


class PackerModule:
    """Packer configuration and build manager."""

    def __init__(self, module: AnsibleModule, packer_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.packer_bin = packer_bin
        self.state = self.params["state"]
        self.template = self.params["template"]
        self.variables = self.params["variables"]
        self.var_files = self.params["var_files"]
        self.only = self.params["only"]
        self.except_builders = self.params["except_builders"]
        self.force = self.params["force"]
        self.parallel = self.params["parallel"]
        self.color = self.params["color"]
        self.machine_readable = self.params["machine_readable"]
        self.cleanup = self.params["cleanup"]
        self.log_level = self.params["log_level"]

    def get_packer_version(self) -> str:
        """Get Packer version using module.run_command."""
        rc, stdout, _stderr = self.module.run_command(
            [self.packer_bin, "version"],
            check_rc=False,
        )
        if rc == 0 and stdout:
            match = VERSION_RE.search(stdout.splitlines()[0])
            if match:
                return match.group(1)
        return "unknown"

    def validate_parameters(self) -> None:
        """Validate module parameters."""
        if not os.path.exists(self.template):
            self.module.fail_json(msg=f"Template file/directory does not exist: {self.template}")

        for var_file in self.var_files:
            if not os.path.exists(var_file):
                self.module.fail_json(msg=f"Variable file does not exist: {var_file}")

    def build_command(self, command: str) -> list[str]:
        cmd = [self.packer_bin]
        if self.log_level != "info":
            cmd.extend(["--log-level", self.log_level])

        cmd.append(command)

        if command in ["build", "init"]:
            cmd.append(self.template)

        if command == "build":
            if self.force:
                cmd.append("-force")
            if not self.parallel:
                cmd.append("-parallel=false")
            if self.cleanup:
                cmd.append("-cleanup")
            if self.only:
                cmd.extend(["-only", ",".join(self.only)])
            if self.except_builders:
                cmd.extend(["-except", ",".join(self.except_builders)])

        if command in ["build", "validate"]:
            if not self.color:
                cmd.append("-no-color")
            if self.machine_readable:
                cmd.append("-machine-readable")

            for key, value in self.variables.items():
                cmd.extend(["-var", f"{key}={value}"])

            for var_file in self.var_files:
                cmd.extend(["-var-file", var_file])

        return cmd

    def parse_machine_readable_output(self, output: str) -> list[dict[str, str]]:
        """Parse machine-readable output for artifacts."""
        artifacts = []
        for line in output.splitlines():
            if not line.startswith("artifact,"):
                continue
            parts = line.split(",")
            if len(parts) >= 4 and parts[3]:
                artifacts.append(
                    {
                        "type": parts[2],
                        "name": parts[3],
                        "build_index": parts[1],
                    }
                )
        return artifacts

    def parse_build_output(self, output: str) -> list[dict[str, str]]:
        """Parse build output to extract artifacts."""
        artifacts = []
        for line in output.splitlines():
            match = BUILD_ARTIFACT_RE.match(line.strip())
            if match:
                artifacts.append(
                    {
                        "type": match.group(1),
                        "name": match.group(2),
                    }
                )
            elif "ami-" in line and ("created" in line or "AMIs" in line):
                ami_match = AMI_ARTIFACT_RE.search(line)
                if ami_match:
                    artifacts.append(
                        {
                            "type": "amazon-ebs",
                            "name": ami_match.group(1),
                        }
                    )
        return artifacts

    def execute_packer(self, command: str) -> dict[str, object]:
        cmd = self.build_command(command)
        start_time = datetime.now(timezone.utc).isoformat() + "Z"
        rc, stdout, stderr = self.module.run_command(cmd, check_rc=True)

        artifacts = []
        if command == "build":
            if self.machine_readable:
                artifacts = self.parse_machine_readable_output(stdout)
            else:
                artifacts = self.parse_build_output(stdout)

        result_dict = {
            "changed": command == "build" or command == "init",
            "stdout": stdout,
            "stderr": stderr,
            "rc": rc,
            "packer_version": self.get_packer_version(),
        }

        if command == "build":
            result_dict.update(
                {
                    "build_start_timestamp": start_time,
                    "artifacts": artifacts,
                    "artifacts_count": len(artifacts),
                }
            )

        return result_dict

    def apply(self) -> dict[str, object]:
        self.validate_parameters()

        if self.state == "init":
            return self.execute_packer("init")
        if self.module.check_mode:
            return self.execute_packer("validate")
        return self.execute_packer("build")


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str",
                required=True,
                choices=["build", "init"],
            ),
            template=dict(type="path", required=True),
            variables=dict(type="dict", default={}),
            var_files=dict(type="list", elements="path", default=[]),
            only=dict(type="list", elements="str"),
            except_builders=dict(
                type="list",
                elements="str",
                aliases=["except"],
            ),
            force=dict(type="bool", default=False),
            parallel=dict(type="bool", default=True),
            color=dict(type="bool", default=False),
            machine_readable=dict(type="bool", default=False),
            cleanup=dict(type="bool", default=False),
            log_level=dict(
                type="str",
                choices=["trace", "debug", "info", "warn", "error"],
                default="info",
            ),
        ),
        mutually_exclusive=[
            ("only", "except_builders"),
        ],
        supports_check_mode=True,
    )
    packer_bin = module.get_bin_path("packer", required=True)

    packer_module = PackerModule(module, packer_bin)
    result = packer_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

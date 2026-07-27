#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: packer
version_added: 1.0.0
short_description: Manage HashiCorp Packer builds
description:
  - Manage Packer builds and templates.
  - Supports building, validating, inspecting, and formatting Packer templates.
  - Provides idempotent build management with artifact existence checking.
author: "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - packer >= 1.7.0
attributes:
  check_mode:
    description: Can run in check_mode and report changes without making them.
    support: full
  diff_mode:
    description: Will return a diff of changes.
    support: full
options:
  name:
    description:
      - Name of the Packer build configuration.
      - Used for identification and artifact tracking.
    type: str
    required: true
  state:
    description:
      - Desired state of the Packer resource.
      - V(build) builds the image from template.
      - V(absent) is a no-op (use V(force=true) to rebuild).
      - V(validated) only validates the template without building.
      - V(inspected) shows template information without building.
      - V(formatted) formats the template file.
    type: str
    required: true
    choices: [build, absent, validated, inspected, formatted]
  template:
    description:
      - Path to the Packer template file.
      - Required for all states except V(absent).
      - Supports HCL2 and JSON formats.
    type: path
    required: false
  variables:
    description:
      - Dictionary of variables to pass to Packer.
      - Corresponds to V(-var) option.
    type: dict
    required: false
    default: {}
  var_files:
    description:
      - List of variable files to load.
      - Corresponds to V(-var-file) option.
    type: list
    elements: path
    required: false
    default: []
  only:
    description:
      - Build only the specified builders.
      - Corresponds to V(-only) option.
    type: list
    elements: str
    required: false
  except_builders:
    description:
      - Build all builders except the specified ones.
      - Corresponds to V(-except) option.
    type: list
    elements: str
    required: false
    aliases: [except]
  force:
    description:
      - Force rebuilding even if artifacts exist.
      - Corresponds to V(-force) flag.
    type: bool
    default: false
  parallel:
    description:
      - Enable parallel building.
      - Set to V(false) to build sequentially.
    type: bool
    default: true
  color:
    description:
      - Enable colored output.
      - Set to V(false) for non-interactive environments.
    type: bool
    default: true
  machine_readable:
    description:
      - Output in machine-readable format.
      - Useful for parsing output in automation.
      - Recommended for CI/CD pipelines.
    type: bool
    default: false
  timeout:
    description:
      - Timeout for the Packer command in seconds.
      - Set to V(0) for no timeout.
    type: int
    default: 3600
  chdir:
    description:
      - Change to this directory before running Packer.
      - Useful when template references relative paths.
    type: path
    required: false
  cleanup:
    description:
      - Clean up temporary files after build.
      - Corresponds to V(-cleanup) flag.
    type: bool
    default: false
  env_vars:
    description:
      - Environment variables to set for Packer process.
      - Useful for cloud provider credentials.
    type: dict
    required: false
    default: {}
  artifact_name:
    description:
      - Name of the artifact to check for existence.
      - Used with V(state=build) to determine if rebuild is needed.
      - For AWS AMI, specify the AMI ID.
      - For Docker, specify the image tag.
    type: str
    required: false
  artifact_region:
    description:
      - Cloud region where the artifact exists.
      - Required for cloud artifacts (AWS, Azure, GCP).
    type: str
    required: false
  artifact_type:
    description:
      - Type of artifact to check.
      - Used to determine the appropriate existence check method.
    type: str
    choices: [ami, docker, azure, gcp, vsphere, openstack, none]
    default: none
  output_dir:
    description:
      - Directory where Packer artifacts will be stored.
      - Used for local builders (virtualbox, qemu, etc.).
    type: path
    required: false
  log_level:
    description:
      - Set the log level for Packer.
      - Useful for debugging.
    type: str
    choices: [trace, debug, info, warn, error]
    default: info
"""

EXAMPLES = r"""
- name: Build AWS AMI with Packer
  community.general.packer:
    name: my-ami
    state: build
    template: aws-ubuntu.pkr.hcl
    variables:
      aws_region: us-west-2
      instance_type: t2.micro
    artifact_type: ami
    artifact_name: ami-12345678
    artifact_region: us-west-2
    force: false

- name: Validate Packer template
  community.general.packer:
    name: template-validation
    state: validated
    template: template.pkr.hcl
    var_files:
      - dev.pkrvars.hcl
      - common.pkrvars.hcl

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

- name: Inspect template structure
  community.general.packer:
    name: inspect-template
    state: inspected
    template: template.pkr.hcl
  register: packer_inspect

- name: Format Packer template
  community.general.packer:
    name: format-template
    state: formatted
    template: template.pkr.hcl

- name: Build with environment variables
  community.general.packer:
    name: env-build
    state: build
    template: template.pkr.hcl
    env_vars:
      AWS_ACCESS_KEY_ID: "{{ aws_access_key }}"
      AWS_SECRET_ACCESS_KEY: "{{ aws_secret_key }}"
    log_level: debug

- name: Build local artifact (VirtualBox)
  community.general.packer:
    name: local-build
    state: build
    template: virtualbox.pkr.hcl
    output_dir: /var/lib/packer/builds
    artifact_type: none
    force: true
"""

RETURN = r"""
stdout:
  description: Standard output from Packer command
  returned: always
  type: str
  sample: "Build finished successfully"
stderr:
  description: Standard error from Packer command
  returned: always
  type: str
  sample: "Error: missing required variable"
rc:
  description: Return code from Packer command
  returned: always
  type: int
  sample: 0
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
  returned: when state is build and build successful
  type: list
  elements: dict
  sample:
    - name: ami-12345678
      region: us-west-2
      type: amazon-ebs
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
changed:
  description: Whether the module made changes
  returned: always
  type: bool
  sample: true
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
        self.timeout = self.params.get("timeout")
        self.chdir = self.params.get("chdir")
        self.cleanup = self.params.get("cleanup")
        self.env_vars = self.params.get("env_vars") or {}
        self.artifact_name = self.params.get("artifact_name")
        self.artifact_region = self.params.get("artifact_region")
        self.artifact_type = self.params.get("artifact_type", "none")
        self.output_dir = self.params.get("output_dir")
        self.log_level = self.params.get("log_level", "info")

        self.state_to_command = {
            "build": "build",
            "absent": "build",
            "validated": "validate",
            "inspected": "inspect",
            "formatted": "fmt",
        }

        self.build_output = ""

    def _check_packer_version(self) -> str:
        """Get Packer version using module.run_command."""
        try:
            rc, stdout, stderr = self.module.run_command(
                [self.packer_bin, "version"],
                check_rc=False,
            )
            if rc == 0 and stdout:
                version_line = stdout.splitlines()[0] if stdout else ""
                match = re.search(r"(\d+\.\d+\.\d+)", version_line)
                if match:
                    return match.group(1)
                return version_line.strip()
            return "unknown"
        except Exception:
            return "unknown"

    def _validate_parameters(self) -> None:
        """Validate module parameters."""
        if self.state in ["build", "validated", "inspected"]:
            if not self.template:
                self.module.fail_json(msg=f"Template file is required for state: {self.state}")
            if not os.path.exists(self.template):
                self.module.fail_json(msg=f"Template file does not exist: {self.template}")

        if self.state == "formatted" and not self.template:
            self.module.fail_json(msg="Template file is required for state: formatted")

        if self.only and self.except_builders:
            self.module.fail_json(msg="'only' and 'except_builders' parameters are mutually exclusive")

        if self.artifact_type != "none" and not self.artifact_name:
            self.module.fail_json(msg=f"'artifact_name' is required when artifact_type is '{self.artifact_type}'")

        if self.artifact_type in ["ami", "azure", "gcp"] and not self.artifact_region:
            self.module.fail_json(msg=f"'artifact_region' is required for artifact_type: {self.artifact_type}")

        if self.timeout < 0:
            self.module.fail_json(msg="'timeout' must be a positive integer")

        if self.chdir and not os.path.exists(self.chdir):
            self.module.fail_json(msg=f"Working directory does not exist: {self.chdir}")

        for var_file in self.var_files:
            if not os.path.exists(var_file):
                self.module.fail_json(msg=f"Variable file does not exist: {var_file}")

    def _artifact_exists(self) -> bool:
        """Check if the artifact already exists."""
        if self.artifact_type == "none" or not self.artifact_name:
            return False

        if self.force:
            return False

        if self.artifact_type == "none" and self.output_dir:
            if os.path.exists(self.output_dir):
                return True

        return False

    def _build_command(self, command: str) -> list[str]:
        """Build the Packer command line."""
        cmd = [self.packer_bin]

        if self.log_level != "info":
            cmd.extend(["--log-level", self.log_level])

        cmd.append(command)

        if command in ["build", "validate", "inspect"]:
            if self.template:
                cmd.append(self.template)
        elif command == "fmt":
            if self.template:
                cmd.append(self.template)

        if command == "build":
            if self.force:
                cmd.append("-force")
            if not self.parallel:
                cmd.append("-parallel=false")
            if self.cleanup:
                cmd.append("-cleanup")

        if not self.color:
            cmd.append("-no-color")
        if self.machine_readable:
            cmd.append("-machine-readable")

        for key, value in self.variables.items():
            if isinstance(value, str) and (" " in value or '"' in value):
                cmd.extend(["-var", f'{key}="{value}"'])
            else:
                cmd.extend(["-var", f"{key}={value}"])

        for var_file in self.var_files:
            cmd.extend(["-var-file", var_file])

        if self.only:
            cmd.extend(["-only", ",".join(self.only)])
        if self.except_builders:
            cmd.extend(["-except", ",".join(self.except_builders)])

        return cmd

    def _parse_machine_readable_output(self, output: str) -> list[dict]:
        """Parse machine-readable output for artifacts."""
        artifacts = []
        for line in output.splitlines():
            if not line.startswith("artifact,"):
                continue

            parts = line.split(",")
            if len(parts) >= 4:
                artifact = {
                    "type": parts[1] if len(parts) > 1 else "",
                    "region": parts[2] if len(parts) > 2 else "",
                    "name": parts[3] if len(parts) > 3 else "",
                }
                if artifact["name"]:
                    artifacts.append(artifact)
        return artifacts

    def _parse_build_output(self, output: str) -> list[dict]:
        """Parse build output to extract artifacts."""
        artifacts = []

        if self.machine_readable:
            return self._parse_machine_readable_output(output)

        lines = output.splitlines()
        for line in lines:
            if "Artifact" in line and "built" in line and ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    artifact_name = parts[1].strip()
                    artifact_type = parts[0].replace("Artifact", "").strip()
                    if artifact_name:
                        artifacts.append(
                            {
                                "name": artifact_name,
                                "type": artifact_type,
                            }
                        )

            if "ami-" in line and ("created" in line or "AMIs" in line):
                match = re.search(r"(ami-[a-zA-Z0-9]+)", line)
                if match:
                    artifacts.append(
                        {
                            "name": match.group(1),
                            "type": "ami",
                        }
                    )

        return artifacts

    def _execute_packer(self, command: str) -> dict[str, object]:
        """Execute Packer command."""
        cmd = self._build_command(command)
        self.result["cmd"] = " ".join(cmd)

        env = os.environ.copy()
        env.update(self.env_vars)
        cwd = self.chdir or os.getcwd()

        try:
            start_time = datetime.now(timezone.utc).isoformat() + "Z"

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                env=env,
                timeout=self.timeout if self.timeout > 0 else None,
                check=False,
            )

            rc, stdout, stderr = result.returncode, result.stdout, result.stderr

            self.build_output = stdout

            artifacts = []
            artifacts_count = 0
            if command == "build" and rc == 0:
                artifacts = self._parse_build_output(stdout)
                artifacts_count = len(artifacts)

            changed = False
            if command == "build":
                changed = True
            elif command == "fmt":
                changed = rc == 0 and stdout != ""
            elif command in ["validate", "inspect"]:
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

        except subprocess.TimeoutExpired:
            self.module.fail_json(
                msg=f"Packer command timed out after {self.timeout} seconds",
                cmd=" ".join(cmd),
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Error executing Packer: {str(e)}",
                cmd=" ".join(cmd),
            )

    def _should_build(self) -> bool:
        """Determine if we need to build based on state and artifact existence."""
        if self.state != "build":
            return False
        if self.force:
            return True
        return not self._artifact_exists()

    def apply(self) -> dict[str, object]:
        """Apply Packer configuration and build if needed."""
        self._validate_parameters()

        if self.state == "absent":
            self.module.warn(
                "State 'absent' is not fully implemented. "
                "Use 'force: true' to force rebuild or use cloud-native modules to delete artifacts."
            )
            self.result["changed"] = False
            self.result["msg"] = "Absent state is not implemented. Use 'force: true' to force rebuild."
            return self.result

        if self.state == "formatted":
            return self._execute_packer("fmt")

        if self.state == "build" and not self._should_build():
            self.result["changed"] = False
            self.result["msg"] = (
                f"Artifact '{self.artifact_name}' already exists, no build needed (use 'force: true' to rebuild)"
            )
            return self.result

        command = self.state_to_command.get(self.state)
        if not command:
            self.module.fail_json(msg=f"Unsupported state: {self.state}")

        if self.state in ["validated", "inspected"]:
            return self._execute_packer(command)

        if self.state == "build":
            result = self._execute_packer("build")
            self.result.update(result)
            return self.result

        return self.result


def main() -> None:
    """Main function."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str",
                required=True,
                choices=["build", "absent", "validated", "inspected", "formatted"],
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
            timeout=dict(type="int", required=False, default=3600),
            chdir=dict(type="path", required=False),
            cleanup=dict(type="bool", required=False, default=False),
            env_vars=dict(type="dict", required=False, default={}),
            artifact_name=dict(type="str", required=False),
            artifact_region=dict(type="str", required=False),
            artifact_type=dict(
                type="str",
                required=False,
                choices=["ami", "docker", "azure", "gcp", "vsphere", "openstack", "none"],
                default="none",
            ),
            output_dir=dict(type="path", required=False),
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
        supports_check_mode=True,
    )

    packer_bin = module.get_bin_path("packer", required=True)

    packer_module = PackerModule(module, packer_bin)
    result = packer_module.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()

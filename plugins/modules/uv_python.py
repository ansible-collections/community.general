#!/usr/bin/python
# Copyright (c) 2026 Mariam Ahhttouche <mariam.ahhttouche@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: uv_python
short_description: Manage Python versions and installations using the C(uv) Python package manager
description:
  - Install, uninstall or upgrade Python versions managed by C(uv).
version_added: "13.0.0"
requirements:
  - C(uv) must be installed and available in E(PATH) and must be at least 0.8.0.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  version:
    description:
      - Python version to manage.
      - "Not all canonical Python versions are supported in this release. Valid version numbers consist of two or three dot-separated
        numeric components, with an optional 'pre-release' tag at the end such as V(3.12), V(3.12.3), V(3.15.0a5)."
      - Advanced uv selectors such as V(>=3.12,<3.13) or V(cpython@3.12) are not supported in this release.
      - When you specify only a major.minor version, make sure the number is enclosed in quotes so that it gets parsed correctly.
        Note that in case only a major.minor version are specified behavior depends on the O(state) parameter.
    type: str
    required: true
  state:
    description:
      - Desired state of the specified Python version.
      - "V(present) ensures the specified version is installed. If you specify a full patch version (for example O(version=3.12.3)),
        that exact version is be installed if not already present. If you only specify a minor version (for example V(3.12)),
        the latest available patch version for that minor release is installed only if no patch version for that minor release
        is currently installed (including patch versions not managed by C(uv)). RV(python_versions) and RV(python_paths)
        lengths are always equal to one for this state."
      - "V(absent) ensures the specified version is removed. If you specify a full patch version, only that exact patch version
        is removed. If you only specify a minor version (for example V(3.12)), all installed patch versions for that minor
        release are removed. If you specify a version that is not installed, no changes are made. RV(python_versions) and
        RV(python_paths) lengths can be higher or equal to one in this state."
      - V(latest) ensures the latest available patch version for the specified version is installed. If you only specify
        a minor version (for example V(3.12)), the latest available patch version for that minor release is always installed.
        If another patch version is already installed but is not the latest, the latest patch version is installed. The latest
        patch version installed depends on the C(uv) version, since available Python versions are frozen per C(uv) release.
        RV(python_versions) and RV(python_paths) lengths are always equal to one in this state. This state does not use C(uv python upgrade).
    type: str
    choices: [present, absent, latest]
    default: present
seealso:
  - name: C(uv) documentation
    description: Python versions management with C(uv).
    link: https://docs.astral.sh/uv/concepts/python-versions/
  - name: C(uv) CLI documentation
    description: C(uv) CLI reference guide.
    link: https://docs.astral.sh/uv/reference/cli/#uv-python
author: Mariam Ahhttouche (@mriamah)
"""

EXAMPLES = r"""
- name: Install Python 3.14
  community.general.uv_python:
    version: "3.14"

- name: Upgrade Python 3.14
  community.general.uv_python:
    version: "3.14"
    state: latest

- name: Remove Python 3.13.5
  community.general.uv_python:
    version: 3.13.5
    state: absent
"""

RETURN = r"""
python_versions:
  description: List of Python versions changed.
  returned: success
  type: list
  elements: str
  sample:
    - "3.13.5"
python_paths:
  description: List of installation paths of Python versions changed.
  returned: success
  type: list
  elements: str
  sample:
    - "/root/.local/share/uv/python/cpython-3.13.5-linux-x86_64-gnu/bin/python3.13"
stdout:
  description: Stdout of the executed command.
  returned: success
  type: str
  sample: ""
stderr:
  description: Stderr of the executed command.
  returned: success
  type: str
  sample: ""
rc:
  description: Return code of the executed command.
  returned: success
  type: int
  sample: 0
"""

import json
import re
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion, StrictVersion

MINIMUM_UV_VERSION = "0.8.0"


class UV:
    """
    Module for managing Python versions and installations using "uv python" command
    """

    def __init__(self, module: AnsibleModule) -> None:
        self.module = module
        self.bin_path = self.module.get_bin_path("uv", required=True)
        self._ensure_min_uv_version()
        try:
            self.python_version = StrictVersion(module.params["version"])
            self.python_version_str = str(self.python_version)
        except (ValueError, AttributeError):
            self.module.fail_json(
                msg=(
                    "Unsupported version format. Valid version numbers consist of two or three dot-separated numeric components"
                    " with an optional 'pre-release' tag on the end (for example 3.12, 3.12.3, 3.15.0a5) are supported in this release."
                )
            )

    def _ensure_min_uv_version(self) -> None:
        cmd = [self.bin_path, "--version", "--color", "never"]
        dummy_rc, out, dummy_err = self.module.run_command(cmd, check_rc=True)
        try:
            detected = re.search(r"\b\d+(?:\.\d+)+\b", out).group()  # type: ignore[union-attr]
            if LooseVersion(detected) < LooseVersion(MINIMUM_UV_VERSION):
                self.module.fail_json(
                    msg=f"uv_python module requires uv >= {MINIMUM_UV_VERSION}",
                    detected_version=detected,
                    required_version=MINIMUM_UV_VERSION,
                )
        except AttributeError:
            self.module.warn("Could not get installed uv version, skipping uv version check")

    def install_python(self) -> tuple[bool, str, str, int, list[str], list[str]]:
        """
        Runs command 'uv python install X.Y.Z' which installs specified python version.
        If patch version is not specified uv installs latest available patch version.
        Returns:
          - boolean to indicate if method changed state
          - command's stdout
          - command's stderr
          - command's return code
          - list of installed versions
          - list of installation paths for each installed version
        """
        find_rc, existing_version, dummy_err = self._find_python("--show-version")
        if find_rc == 0:
            dummy_rc, version_path, dummy_err = self._find_python()
            return False, "", "", 0, [existing_version], [version_path]
        if self.module.check_mode:
            latest_version, dummy_path = self._get_latest_patch_release("--managed-python")
            # when uv does not find any available patch version the install command will fail
            if not latest_version:
                self.module.fail_json(msg=(f"Version {self.python_version_str} is not available."))
            return True, "", "", 0, [latest_version], [""]
        rc, out, err = self._exec(self.python_version_str, "install", check_rc=True)
        latest_version, path = self._get_latest_patch_release("--only-installed", "--managed-python")
        return True, out, err, rc, [latest_version], [path]

    def uninstall_python(self) -> tuple[bool, str, str, int, list, list]:
        """
        Runs command 'uv python uninstall X.Y.Z' which removes specified python version from environment.
        If patch version is not specified all correspending installed patch versions are removed.
        Returns:
          tuple [bool, str, str, int, list, list]
          - boolean to indicate if method changed state
          - command's stdout
          - command's stderr
          - command's return code
          - list of uninstalled versions
          - list of previous installation paths for each uninstalled version
        """
        installed_versions, install_paths = self._get_installed_versions("--managed-python")
        if not installed_versions:
            return False, "", "", 0, [], []
        if self.module.check_mode:
            return True, "", "", 0, installed_versions, install_paths
        rc, out, err = self._exec(self.python_version_str, "uninstall", check_rc=True)
        return True, out, err, rc, installed_versions, install_paths

    def upgrade_python(self) -> tuple[bool, str, str, int, list, list]:
        """
        Runs command 'uv python install X.Y.Z' with latest patch version available.
        Returns:
          - boolean to indicate if method changed state
          - command's stdout
          - command's stderr
          - command's return code
          - list of installed versions
          - list of installation paths for each installed version
        """
        rc, installed_version_str, dummy_err = self._find_python("--show-version")
        installed_version = self._parse_version(installed_version_str)
        latest_version_str, dummy_path = self._get_latest_patch_release("--managed-python")
        if not latest_version_str:
            self.module.fail_json(msg=f"Version {self.python_version_str} is not available.")
        if rc == 0 and installed_version >= StrictVersion(latest_version_str):
            dummy_rc, install_path, dummy_err = self._find_python()
            return False, "", "", rc, [installed_version_str], [install_path]
        if self.module.check_mode:
            return True, "", "", 0, [latest_version_str], []
        # it's possible to have latest version already installed but not used as default
        # so in this case 'uv python install' will set latest version as default
        rc, out, err = self._exec(latest_version_str, "install", check_rc=True)
        latest_version_str, latest_path = self._get_latest_patch_release("--only-installed", "--managed-python")
        return True, out, err, rc, [latest_version_str], [latest_path]

    def _exec(self, python_version: str, command: str, *args, check_rc: bool = False) -> tuple[int, str, str]:
        """
        Execute a uv python subcommand.
        Args:
          python_version: Python version specifier (e.g. "3.12", "3.12.3").
          command (str): uv python subcommand (e.g. "install", "uninstall", "find").
          *args: Additional positional arguments passed to the command.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        """
        cmd = [
            self.bin_path,
            "python",
            command,
            python_version,
            "--color",
            "never",
            *args,
        ]
        rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
        return rc, out, err

    def _find_python(self, *args, check_rc: bool = False) -> tuple[int, str, str]:
        """
        Runs command 'uv python find' which returns path of installed patch releases for a given python version.
        If multiple patch versions are installed, "uv python find" returns the one used by default
        if inside a virtualenv otherwise it returns latest installed patch version.
        Args:
          *args: Additional positional arguments passed to _exec.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        """
        rc, out, err = self._exec(self.python_version_str, "find", *args, check_rc=check_rc)
        if rc == 0:
            out = out.strip()
        return rc, out, err

    def _list_python(self, *args, check_rc: bool = False) -> tuple[int, list, str]:
        """
        Runs command 'uv python list' (which returns list of installed patch releases for a given python version).
        Official documentation https://docs.astral.sh/uv/reference/cli/#uv-python-list
        Args:
          *args: Additional positional arguments passed to _exec.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        """
        rc, out, err = self._exec(
            self.python_version_str,
            "list",
            "--output-format",
            "json",
            *args,
            check_rc=check_rc,
        )
        pythons_installed = []
        try:
            pythons_installed = json.loads(out)
            # convert path to absolute path since in some recent uv releases "uv python list" returns relative install paths instead of absolute paths
            for result in pythons_installed:
                path = result.get("path", "")
                if path and not Path(path).is_absolute():
                    result["path"] = str(Path(path).resolve())
        except json.decoder.JSONDecodeError:
            self.module.debug("No Python installation found.")
        return rc, pythons_installed, err

    def _get_latest_patch_release(self, *args) -> tuple[str, str]:
        """
        Returns latest available patch release for a given python version.
        Args:
          *args: Additional positional arguments passed to _list_python.
        Returns:
            - latest found patch version in format X.Y.Z
            - installation path of latest patch version if version exists
        """
        latest_version = path = ""
        # 'uv python list' returns versions in descending order but we sort them just in case future uv behavior changes
        dummy_rc, results, dummy_err = self._list_python(*args)
        valid_results = self._filter_valid_versions(results)
        if valid_results:
            version = max(valid_results, key=lambda result: result["parsed_version"])
            latest_version = version.get("version", "")
            path = version.get("path", "")
        return latest_version, path

    def _get_installed_versions(self, *args) -> tuple[list, list]:
        """
        Returns installed patch releases for a given python version.
        Args:
          *args: Additional positional arguments passed to _list_python.
        Returns:
            - list of latest found patch versions
            - list of installation paths of installed versions
        """
        dummy_rc, results, dummy_err = self._list_python("--only-installed", *args)
        if results:
            return [result.get("version") for result in results], [result.get("path") for result in results]
        return [], []

    def _filter_valid_versions(self, results: list):
        valid_results = []
        for result in results:
            version = result.get("version", "")
            try:
                result["parsed_version"] = StrictVersion(version)
                valid_results.append(result)
            except ValueError:
                self.module.debug(f"Filtering out version {version!r} since it's not supported by uv_python module.")
        return valid_results

    @staticmethod
    def _parse_version(version_str: str):
        try:
            return StrictVersion(version_str)
        except ValueError:
            return StrictVersion("0")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            version=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent", "latest"]),
        ),
        supports_check_mode=True,
    )

    result = dict(
        changed=False,
        stdout="",
        stderr="",
        rc=0,
        python_versions=[],
        python_paths=[],
        failed=False,
    )
    state = module.params["state"]
    exec_result = {}
    uv = UV(module)

    if state == "present":
        exec_result = dict(
            zip(
                [
                    "changed",
                    "stdout",
                    "stderr",
                    "rc",
                    "python_versions",
                    "python_paths",
                ],
                uv.install_python(),
            )
        )
    elif state == "absent":
        exec_result = dict(
            zip(
                [
                    "changed",
                    "stdout",
                    "stderr",
                    "rc",
                    "python_versions",
                    "python_paths",
                ],
                uv.uninstall_python(),
            )
        )
    elif state == "latest":
        exec_result = dict(
            zip(
                [
                    "changed",
                    "stdout",
                    "stderr",
                    "rc",
                    "python_versions",
                    "python_paths",
                ],
                uv.upgrade_python(),
            )
        )

    result.update(exec_result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()

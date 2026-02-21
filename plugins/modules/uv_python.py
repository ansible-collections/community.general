#!/usr/bin/python
# Copyright (c) 2026 Mariam Ahhttouche <mariam.ahhttouche@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r'''
---
module: uv_python
short_description: Manage Python installations using uv.
description:
  - Install, remove or upgrade Python versions managed by uv.
version_added: "X.Y"
requirements:
  - uv must be installed and available on PATH
  - uv >= 0.8.0
options:
  version:
    description: 
      - Python version to manage. 
      - Expected formats are "X.Y" or "X.Y.Z".
    type: str
    required: true
  state:
    description: Desired state of the specified Python version.
    type: str
    choices: [present, absent, latest]
    default: present
author:
  - Mariam Ahhttouche (@mriamah)
deprecated:
'''

EXAMPLES = r'''
- name: Install Python 3.12
  uv_python:
    version: "3.12"

- name: Remove Python 3.11
  uv_python:
    version: "3.11"
    state: absent
'''

RETURN = r'''
python:
  description: Installed Python info
  returned: when state=present
  type: dict
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import StrictVersion


class UV:
    """
      Module for "uv python" command
      Official documentation for uv python https://docs.astral.sh/uv/concepts/python-versions/#installing-a-python-version
    """

    def __init__(self, module):
        self.module = module
        python_version = module.params["version"]
        try:
          self.python_version = StrictVersion(python_version)
          self.python_version_str = self.python_version.__str__()
        except ValueError:
          self.module.fail_json(
            msg=(
                f"Invalid version {python_version}. "
                "Expected formats are X.Y or X.Y.Z"
            )
          )


    def install_python(self):
      """
        Runs command 'uv python install X.Y.Z' which installs specified python version.
        If patch version is not specified uv installs latest available patch version.
        Returns: 
          tuple [bool, str, str, int, list, list] 
          - boolean to indicate if method changed state
          - command's stdout
          - command's stderr
          - command's return code
          - list of installed versions
          - list of installation paths for each installed version
        Raises:
          AnsibleModuleFailJson:
              If the install command exits with a non-zero return code.
              If specified version is not available for download.
      """
      find_rc, existing_version, _ = self._find_python(self.python_version_str, "--show-version")
      if find_rc == 0:
        _, version_path, _ = self._find_python(self.python_version_str)
        return False, "", "", 0, [existing_version], [version_path]
      if self.module.check_mode:
        latest_version, _ = self._get_latest_patch_release("--managed-python")
        # when uv does not find any available patch version the install command will fail
        if not latest_version:
          self.module.fail_json(msg=(f"Version {self.python_version_str} is not available."))
        return True, "", "", 0, [latest_version], [""]

      rc, out, err = self._exec(self.python_version_str, "install", check_rc=True)
      latest_version, path = self._get_latest_patch_release("--only-installed", "--managed-python")
      return True, out, err, rc, [latest_version], [path]


    def uninstall_python(self):
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
        Raises:
          AnsibleModuleFailJson:
              If the uninstall command exits with a non-zero return code.
      """
      installed_versions, install_paths = self._get_installed_versions("--managed-python")
      if not installed_versions:
        return False, "", "", 0, [], []
      if self.module.check_mode:
        return True, "", "", 0, installed_versions, install_paths
      
      rc, out, err = self._exec(self.python_version_str, "uninstall", check_rc=True)
      return True, out, err, rc, installed_versions, install_paths
    

    def upgrade_python(self):
      """
        Runs command 'uv python install X.Y.Z' with latest patch version available.
        Returns: 
          tuple [bool, str, str, int, list, list] 
          - boolean to indicate if method changed state
          - command's stdout
          - command's stderr
          - command's return code
          - list of installed versions
          - list of installation paths for each installed version
        Raises:
          AnsibleModuleFailJson:
              If the install command exits with a non-zero return code.
              If resolved patch version is not available for download.
      """
      rc, installed_version, _ = self._find_python(self.python_version_str, "--show-version")
      latest_version, _ = self._get_latest_patch_release("--managed-python")
      if not latest_version:
         self.module.fail_json(msg=f"Version {self.python_version_str} is not available.")
      if rc == 0 and StrictVersion(installed_version) >= StrictVersion(latest_version):
          _, install_path, _ = self._find_python(self.python_version_str)
          return False, "", "", rc, [installed_version], [install_path]
      if self.module.check_mode:
          return True, "", "", 0, [latest_version], []
      # it's possible to have latest version already installed but not used as default so in this case 'uv python install' will set latest version as default
      rc, out, err = self._exec(latest_version, "install", check_rc=True)
      latest_version, latest_path = self._get_latest_patch_release("--only-installed", "--managed-python")
      return True, out, err, rc, [latest_version], [latest_path]


    def _exec(self, python_version, command, *args, check_rc=False):
      """
        Execute a uv python subcommand.
        Args:
          python_version (str): Python version specifier (e.g. "3.12", "3.12.3").
          command (str): uv python subcommand (e.g. "install", "uninstall", "find").
          *args: Additional positional arguments passed to the command.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        Returns:
          tuple[int, str, str]:
            A tuple containing (rc, stdout, stderr).
        Raises:
          AnsibleModuleFailJson:
              If check_rc is True and the command exits with a non-zero return code.
      """
      cmd = [self.module.get_bin_path("uv", required=True), "python", command, python_version, *args]
      rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
      return rc, out, err


    def _find_python(self, python_version, *args, check_rc=False):
      """
        Runs command 'uv python find' which returns path of installed patch releases for a given python version.
        If multiple patch versions are installed, "uv python find" returns the one used by default if inside a virtualenv otherwise it returns latest installed patch version.
        Args:
          python_version (str): Python version specifier (e.g. "3.12", "3.12.3").
          *args: Additional positional arguments passed to _exec.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        Returns:
          tuple[int, str, str]:
            A tuple containing (rc, stdout, stderr).
        Raises:
          AnsibleModuleFailJson:
            If check_rc is True and the command exits with a non-zero return code.
      """
      rc, out, err = self._exec(python_version, "find", *args, check_rc=check_rc)
      if rc == 0:
        out = out.strip()
      return rc, out, err


    def _list_python(self, python_version, *args, check_rc=False):
      """
        Runs command 'uv python list' (which returns list of installed patch releases for a given python version).
        Official documentation https://docs.astral.sh/uv/reference/cli/#uv-python-list
        Args:
          python_version (str): Python version specifier (e.g. "3.12", "3.12.3").
          *args: Additional positional arguments passed to _exec.
          check_rc (bool): Whether to fail if the command exits with non-zero return code.
        Returns:
          tuple[int, str, str]:
            A tuple containing (rc, stdout, stderr).
        Raises:
          AnsibleModuleFailJson:
            If check_rc is True and the command exits with a non-zero return code.
      """
      rc, out, err = self._exec(python_version, "list", "--output-format", "json", *args, check_rc=check_rc)
      try:
        out = json.loads(out)
      except json.decoder.JSONDecodeError:
        # This happens when no version is found
        pass
      return rc, out, err


    def _get_latest_patch_release(self, *args):
      """
        Returns latest available patch release for a given python version.
        Args:
          *args: Additional positional arguments passed to _list_python.
        Returns:
          tuple[str, str]:
            - latest found patch version in format X.Y.Z
            - installation path of latest patch version if version exists
      """
      latest_version = path = ""
      _, results, _ = self._list_python(self.python_version_str, *args) # uv returns versions in descending order but we sort them just in case future uv behavior changes
      if results:
        version = max(results, key=lambda item: (item["version_parts"]["major"], item["version_parts"]["minor"], item["version_parts"]["patch"]))
        latest_version = version["version"]
        path = version["path"] if version["path"] else ""
      return latest_version, path


    def _get_installed_versions(self, *args):
      """
        Returns installed patch releases for a given python version.
        Args:
          *args: Additional positional arguments passed to _list_python.
        Returns:
          tuple[list, list]:
            - list of latest found patch versions
            - list of installation paths of installed versions
      """
      _, results, _ = self._list_python(self.python_version_str, "--only-installed", *args)
      if results:
        return [result["version"] for result in results], [result["path"] for result in results]
      return [], []



def main():
    module = AnsibleModule(
        argument_spec=dict(
            version=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
        ),
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        stdout="",
        stderr="",
        rc=0,
        python_versions=[],
        python_paths=[],
        failed=False
    )
    state = module.params["state"]

    uv = UV(module)
    if state == "present":
      result["changed"], result["stdout"], result["stderr"], result["rc"], result["python_versions"], result["python_paths"] = uv.install_python()
    elif state == "absent":
      result["changed"], result["stdout"], result["stderr"], result["rc"], result["python_versions"], result["python_paths"] = uv.uninstall_python()
    elif state == "latest":
      result["changed"], result["stdout"], result["stderr"], result["rc"], result["python_versions"], result["python_paths"] = uv.upgrade_python()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
#!/usr/bin/python
# Copyright (c) 2026 Mariam Ahhttouche <mariam.ahhttouche@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r'''
---
module: uv_python
short_description: Manage Python installations using uv
description:
  - Install or remove Python versions managed by uv.
# requirements:
#   - uv must be installed and available on PATH
options:
  version:
    description: Python version to manage
    type: str
    required: true
  state:
    description: Desired state
    type: str
    choices: [present, absent]
    default: present
  force:
    description: Force reinstall
    type: bool
    default: false
  uv_path:
    description: Path to uv binary
    type: str
    default: uv
author:
  - Your Name
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
    subcommand = "python"

    def __init__(self, module, **kwargs):
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
        Returns: tuple with following elements 
          - boolean to indicate if method changed state
          - installed version
      """
      rc, out, _ = self._find_python("--show-version") 
      if rc == 0:
        return False, out.split()[0]
      if self.module.check_mode:
        _, versions_available, _ = self._list_python()
        # when uv does not find any available patch version the install command will fail
        try:
          if not json.loads(versions_available):
            self.module.fail_json(msg=(f"Version {self.python_version_str} is not available."))
        except json.decoder.JSONDecodeError as e:
          self.module.fail_json(msg=f"Failed to parse 'uv python list' output with error {str(e)}")
        return True, self.python_version_str

      cmd = [self.module.get_bin_path("uv", required=True), self.subcommand, "install", self.python_version_str]
      self.module.run_command(cmd, check_rc=True)
      return True, self.python_version_str
    
    def uninstall_python(self):
      """
        Runs command 'uv python uninstall X.Y.Z' which removes specified python version from environment.
        If patch version is not specified all correspending installed patch versions are removed.
        Returns: tuple with following elements 
          - boolean to indicate if method changed state
          - removed version
      """
      rc, _, _ = self._find_python("--show-version")
      # if "uv python find" fails, it means specified version does not exist
      if rc != 0:
          return False, ""
      if self.module.check_mode:
        return True, self.python_version_str
      
      cmd = [self.module.get_bin_path("uv", required=True), self.subcommand, "uninstall", self.python_version_str]
      self.module.run_command(cmd, check_rc=True)
      return True, self.python_version_str
    
    def upgrade_python(self):
      """
        Runs command 'uv python install X.Y.Z' which installs specified python version.
        Returns: tuple with following elements 
          - boolean to indicate if method changed state
          - installed version
      """
      rc, out, _ = self._find_python("--show-version")
      latest_version = self._get_latest_patch_release()
      if not latest_version:
         self.module.fail_json(msg=(f"Version {self.python_version_str} is not available."))
      if rc == 0 and out.split()[0] == latest_version:
          return False, latest_version
      if self.module.check_mode:
          return True, latest_version
      
      cmd = [self.module.get_bin_path("uv", required=True), self.subcommand, "install", latest_version]
      self.module.run_command(cmd, check_rc=True)
      return True, latest_version

    def _find_python(self, *args):
      """
        Runs command 'uv python find' which returns path of installed patch releases for a given python version.
        If multiple patch versions are installed, "uv python find" returns the one used by default if inside a virtualenv otherwise it returns latest installed patch version.
        Returns: tuple with following elements 
          - return code of executed command
          - stdout of command
          - stderr of command
      """
      cmd = [self.module.get_bin_path("uv", required=True), self.subcommand, "find", self.python_version_str, *args]
      rc, out, err = self.module.run_command(cmd)
      return rc, out, err
    
    def _list_python(self):
      """
        Runs command 'uv python list' which returns list of installed patch releases for a given python version.
        Returns: tuple with following elements 
          - return code of executed command
          - stdout of command
          - stderr of command
      """
      # https://docs.astral.sh/uv/reference/cli/#uv-python-list
      cmd = [self.module.get_bin_path("uv", required=True), self.subcommand, "list", self.python_version_str, "--output-format", "json"]
      rc, out, err = self.module.run_command(cmd)
      return rc, out, err

    def _get_latest_patch_release(self):
      """
        Returns latest available patch release for a given python version.
        Fails when no available release exists for the specified version.
      """
      _, out, _ = self._list_python() # uv returns versions in descending order but we sort them just in case future uv behavior changes
      latest_version = ""
      try:
        results = json.loads(out)
        versions = [StrictVersion(result["version"]) for result in results]
        latest_version = max(versions).__str__()
      except ValueError:
        pass
      return latest_version


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
        msg="",
        failed=False
    )
    state = module.params["state"]

    try:
      uv = UV(module)
      if state == "present":
        result["changed"], result["msg"] = uv.install_python()
      elif state == "absent":
        result["changed"], result["msg"] = uv.uninstall_python()
      elif state == "latest":
        result["changed"], result["msg"] = uv.upgrade_python()

      module.exit_json(**result)
    except Exception as e:
      module.fail_json(msg=str(e))

if __name__ == "__main__":
    main()
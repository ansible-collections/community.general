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

import re
import json
from enum import Enum
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import StrictVersion


class UV:
    """
      Documentation for uv python https://docs.astral.sh/uv/concepts/python-versions/#installing-a-python-version
    """
    def __init__(self, module, **kwargs):
        self.module = module
        python_version = module.params["version"]
        try:
          self.python_version = StrictVersion(python_version)
          self.python_version_str = self.python_version.__str__()
        except ValueError:
          module.fail_json(
            msg=(
                f"Invalid version '{python_version}'. "
                "Expected formats are X.Y or X.Y.Z"
            )
          )

    def install_python(self):
        rc, out, _ = self._find_python("--show-version") 
        if rc == 0:
          return False, out.split()[0]
        if self.module.check_mode:
          return True, self.python_version_str

        cmd = [self.module.get_bin_path("uv", required=True), "python", "install", self.python_version_str]
        self.module.run_command(cmd, check_rc=True)
        return True, self.python_version_str
    
    def uninstall_python(self):
      rc, out, _ = self._find_python()
      if rc != 0:
          return False, out
      if self.module.check_mode:
          return True, ""
      
      cmd = [self.module.get_bin_path("uv", required=True), "python", "uninstall", self.python_version_str]
      self.module.run_command(cmd, check_rc=True)
      return True, ""
    
    def upgrade_python(self):
      rc, out, _ = self._find_python("--show-version")
      latest_version = self._get_latest_patch_release()
      if rc == 0:
        detected_version = out.split()[0]
        if detected_version == latest_version:
          return False, latest_version
      if self.module.check_mode:
          return True, latest_version
      
      cmd = [self.module.get_bin_path("uv", required=True), "python", "install", latest_version]
      self.module.run_command(cmd, check_rc=True)
      return True, latest_version

    def _find_python(self, *args):
      # if multiple similar minor versions exist, find returns the one used by default if inside a virtualenv otherwise it returns latest installed patch version
      cmd = [self.module.get_bin_path("uv", required=True), "python", "find", self.python_version_str, *args]
      rc, out, err = self.module.run_command(cmd)
      return rc, out, err
    
    def _list_python(self):
      # https://docs.astral.sh/uv/reference/cli/#uv-python-list
      cmd = [self.module.get_bin_path("uv", required=True), "python", "list", self.python_version_str, "--output-format", "json"]
      rc, out, err = self.module.run_command(cmd)
      return rc, out, err

    def _get_latest_patch_release(self):
      _, out, _ = self._list_python() # uv returns versions in descending order but we sort them just in case future uv behavior changes
      results = json.loads(out)
      versions = [StrictVersion(result["version"]) for result in results]
      return max(versions).__str__()
    

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
    )
    state = module.params["state"]
    uv = UV(module)

    if state == "present":
      result["changed"], result["msg"] = uv.install_python()
    elif state == "absent":
      result["changed"], result["msg"] = uv.uninstall_python()
    elif state == "latest":
      result["changed"], result["msg"] = uv.upgrade_python()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
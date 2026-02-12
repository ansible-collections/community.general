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
from enum import Enum
from ansible.module_utils.basic import AnsibleModule


MINOR_RELEASE = re.compile(r"^\d+\.\d+$")
PATCH_RELEASE = re.compile(r"^\d+\.\d+\.\d+$")

class Release(Enum):
  PATCH = 1
  MINOR = 2

def extract_python_version(version: str, module):
  if PATCH_RELEASE.match(version):
      return Release.PATCH, version
  elif MINOR_RELEASE.match(version):
      return Release.MINOR, version
  else:
      module.fail_json(
          msg=(
              f"Invalid version '{version}'. "
              "Expected X.Y or X.Y.Z."
          )
      )
  return None, None

class UV:
    """
      Documentation for uv python https://docs.astral.sh/uv/concepts/python-versions/#installing-a-python-version
    """
    def __init__(self, module, **kwargs):
        self.module = module
        self.python_version_type, self.python_version = extract_python_version(module.params["version"], module)

    def install_python(self):
        rc, out, _ = self._find_python() 
        if rc == 0:
          return False, out
        if self.module.check_mode:
          return True, ""

        cmd = [self.module.get_bin_path("uv", required=True), "python", "install", self.python_version]
        _, out, _ = self.module.run_command(cmd, check_rc=True)
        return True, out
    
    def uninstall_python(self):
      rc, out, _ = self._find_python()
      if rc != 0:
          return False, out
      if self.module.check_mode:
          return True, ""
      
      cmd = [self.module.get_bin_path("uv", required=True), "python", "uninstall", self.python_version]
      _, out, _ = self.module.run_command(cmd, check_rc=True)
      return True, out

    def _find_python(self):
      cmd = [self.module.get_bin_path("uv", required=True), "python", "find", self.python_version]
      rc, out, err = self.module.run_command(cmd)
      return rc, out, err


def main():
    module = AnsibleModule(
        argument_spec=dict(
            version=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
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

    module.exit_json(**result)


if __name__ == "__main__":
    main()
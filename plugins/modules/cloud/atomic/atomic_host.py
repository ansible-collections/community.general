#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: atomic_host
short_description: Manage the atomic host platform
description:
    - Manage the atomic host platform.
    - Rebooting of Atomic host platform should be done outside this module.
author:
- Saravanan KR (@krsacme)
notes:
    - Host should be an atomic platform (verified by existence of '/run/ostree-booted' file).
requirements:
  - atomic
  - python >= 2.6
options:
    revision:
        description:
          - The version number of the atomic host to be deployed.
          - Providing C(latest) will upgrade to the latest available version.
        default: 'latest'
        aliases: [ version ]
        type: str
'''

EXAMPLES = r'''
- name: Upgrade the atomic host platform to the latest version (atomic host upgrade)
  community.general.atomic_host:
    revision: latest

- name: Deploy a specific revision as the atomic host (atomic host deploy 23.130)
  community.general.atomic_host:
    revision: 23.130
'''

RETURN = r'''
msg:
    description: The command standard output
    returned: always
    type: str
    sample: 'Already on latest'
'''
import os
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def core(module):
    revision = module.params['revision']
    atomic_bin = module.get_bin_path('atomic', required=True)

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')

    if revision == 'latest':
        args = [atomic_bin, 'host', 'upgrade']
    else:
        args = [atomic_bin, 'host', 'deploy', revision]

    rc, out, err = module.run_command(args, check_rc=False)

    if rc == 77 and revision == 'latest':
        module.exit_json(msg="Already on latest", changed=False)
    elif rc != 0:
        module.fail_json(rc=rc, msg=err)
    else:
        module.exit_json(msg=out, changed=True)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            revision=dict(type='str', default='latest', aliases=["version"]),
        ),
    )

    # Verify that the platform is atomic host
    if not os.path.exists("/run/ostree-booted"):
        module.fail_json(msg="Module atomic_host is applicable for Atomic Host Platforms only")

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

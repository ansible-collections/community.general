#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Kaarle Ritvanen <kaarle.ritvanen@datakunkku.fi>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: lbu

short_description: Local Backup Utility for Alpine Linux

version_added: '0.2.0'

description:
  - Manage Local Backup Utility of Alpine Linux in run-from-RAM mode.
extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  commit:
    description:
      - Control whether to commit changed files.
    type: bool
  exclude:
    description:
      - List of paths to exclude.
    type: list
    elements: str
  include:
    description:
      - List of paths to include.
    type: list
    elements: str

author:
  - Kaarle Ritvanen (@kunkku)
"""

EXAMPLES = r"""
# Commit changed files (if any)
- name: Commit
  community.general.lbu:
    commit: true

# Exclude path and commit
- name: Exclude directory
  community.general.lbu:
    commit: true
    exclude:
      - /etc/opt

# Include paths without committing
- name: Include file and directory
  community.general.lbu:
    include:
      - /root/.ssh/authorized_keys
      - /var/lib/misc
"""

RETURN = r"""
msg:
  description: Error message.
  type: str
  returned: on failure
"""

from ansible.module_utils.basic import AnsibleModule

import os.path


def run_module():
    module = AnsibleModule(
        argument_spec={
            'commit': {'type': 'bool'},
            'exclude': {'type': 'list', 'elements': 'str'},
            'include': {'type': 'list', 'elements': 'str'}
        },
        supports_check_mode=True
    )

    changed = False

    def run_lbu(*args):
        code, stdout, stderr = module.run_command(
            [module.get_bin_path('lbu', required=True)] + list(args)
        )
        if code:
            module.fail_json(changed=changed, msg=stderr)
        return stdout

    update = False
    commit = False

    for param in ('include', 'exclude'):
        if module.params[param]:
            paths = run_lbu(param, '-l').split('\n')
            for path in module.params[param]:
                if os.path.normpath('/' + path)[1:] not in paths:
                    update = True

    if module.params['commit']:
        commit = update or run_lbu('status') > ''

    if module.check_mode:
        module.exit_json(changed=update or commit)

    if update:
        for param in ('include', 'exclude'):
            if module.params[param]:
                run_lbu(param, *module.params[param])
                changed = True

    if commit:
        run_lbu('commit')
        changed = True

    module.exit_json(changed=changed)


def main():
    run_module()


if __name__ == '__main__':
    main()

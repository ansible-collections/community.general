#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019-2020, Andrew Klaus <andrewklaus@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: syspatch

short_description: Manage OpenBSD system patches


description:
    - "Manage OpenBSD system patches using syspatch."

extends_documentation_fragment:
    - community.general.attributes

attributes:
    check_mode:
        support: full
    diff_mode:
        support: none

options:
    revert:
        description:
            - Revert system patches.
        type: str
        choices: [ all, one ]

author:
    - Andrew Klaus (@precurse)
'''

EXAMPLES = '''
- name: Apply all available system patches
  community.general.syspatch:

- name: Revert last patch
  community.general.syspatch:
    revert: one

- name: Revert all patches
  community.general.syspatch:
    revert: all

# NOTE: You can reboot automatically if a patch requires it:
- name: Apply all patches and store result
  community.general.syspatch:
  register: syspatch

- name: Reboot if patch requires it
  ansible.builtin.reboot:
  when: syspatch.reboot_needed
'''

RETURN = r'''
rc:
  description: The command return code (0 means success)
  returned: always
  type: int
stdout:
  description: syspatch standard output.
  returned: always
  type: str
  sample: "001_rip6cksum"
stderr:
  description: syspatch standard error.
  returned: always
  type: str
  sample: "syspatch: need root privileges"
reboot_needed:
  description: Whether or not a reboot is required after an update.
  returned: always
  type: bool
  sample: true
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        revert=dict(type='str', choices=['all', 'one'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result = syspatch_run(module)

    module.exit_json(**result)


def syspatch_run(module):
    cmd = module.get_bin_path('syspatch', True)
    changed = False
    reboot_needed = False
    warnings = []

    # Set safe defaults for run_flag and check_flag
    run_flag = ['-c']
    check_flag = ['-c']
    if module.params['revert']:
        check_flag = ['-l']

        if module.params['revert'] == 'all':
            run_flag = ['-R']
        else:
            run_flag = ['-r']
    else:
        check_flag = ['-c']
        run_flag = []

    # Run check command
    rc, out, err = module.run_command([cmd] + check_flag)

    if rc != 0:
        module.fail_json(msg="Command %s failed rc=%d, out=%s, err=%s" % (cmd, rc, out, err))

    if len(out) > 0:
        # Changes pending
        change_pending = True
    else:
        # No changes pending
        change_pending = False

    if module.check_mode:
        changed = change_pending
    elif change_pending:
        rc, out, err = module.run_command([cmd] + run_flag)

        # Workaround syspatch ln bug:
        # http://openbsd-archive.7691.n7.nabble.com/Warning-applying-latest-syspatch-td354250.html
        if rc != 0 and err != 'ln: /usr/X11R6/bin/X: No such file or directory\n':
            module.fail_json(msg="Command %s failed rc=%d, out=%s, err=%s" % (cmd, rc, out, err))
        elif out.lower().find('create unique kernel') >= 0:
            # Kernel update applied
            reboot_needed = True
        elif out.lower().find('syspatch updated itself') >= 0:
            warnings.append('Syspatch was updated. Please run syspatch again.')

        # If no stdout, then warn user
        if len(out) == 0:
            warnings.append('syspatch had suggested changes, but stdout was empty.')

        changed = True
    else:
        changed = False

    return dict(
        changed=changed,
        reboot_needed=reboot_needed,
        rc=rc,
        stderr=err,
        stdout=out,
        warnings=warnings
    )


def main():
    run_module()


if __name__ == '__main__':
    main()

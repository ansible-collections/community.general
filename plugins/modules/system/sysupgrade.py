#!/usr/bin/python

# Copyright: (c) 2020, Andrew Klaus <andrewklaus@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sysupgrade
short_description: Manage OpenBSD system upgrades
version_added: 1.1.0
description:
    - Manage OpenBSD system upgrades using sysupgrade.
options:
    snapshot:
        description:
        - Apply the latest snapshot.
        - Otherwise release will be applied.
        default: no
        type: bool
    force:
        description:
        - Force upgrade (for snapshots only).
        default: no
        type: bool
    keep_files:
        description:
        - Keep the files under /home/_sysupgrade.
        - By default, the files will be deleted after the upgrade.
        default: no
        type: bool
    fetch_only:
        description:
        - Fetch and verify files and create /bsd.upgrade but do not reboot.
        - Set to C(false) if you want sysupgrade to reboot. This will cause Ansible to error, as it expects the module to exit gracefully. See the examples.
        default: yes
        type: bool
    installurl:
        description:
        - OpenBSD mirror top-level URL for fetching an upgrade.
        - By default, the mirror URL is pulled from /etc/installurl.
        type: str
author:
    - Andrew Klaus (@precurse)
'''

EXAMPLES = r'''
- name: Upgrade to latest release
  community.general.sysupgrade:
  register: sysupgrade

- name: Upgrade to latest snapshot
  community.general.sysupgrade:
    snapshot: yes
    installurl: https://cloudflare.cdn.openbsd.org/pub/OpenBSD
  register: sysupgrade

- name: Reboot to apply upgrade if needed
  ansible.builtin.reboot:
  when: sysupgrade.changed

# Note: Ansible will error when running this way due to how
#   the reboot is forcefully handled by sysupgrade:

- name: Have sysupgrade automatically reboot
  community.general.sysupgrade:
    fetch_only: no
  ignore_errors: yes
'''

RETURN = r'''
rc:
  description: The command return code (0 means success).
  returned: always
  type: int
stdout:
  description: Sysupgrade standard output.
  returned: always
  type: str
stderr:
  description: Sysupgrade standard error.
  returned: always
  type: str
  sample: "sysupgrade: need root privileges"
'''

from ansible.module_utils.basic import AnsibleModule


def sysupgrade_run(module):
    sysupgrade_bin = module.get_bin_path('/usr/sbin/sysupgrade', required=True)
    cmd = [sysupgrade_bin]
    changed = False
    warnings = []

    # Setup command flags
    if module.params['snapshot']:
        run_flag = ['-s']
        if module.params['force']:
            # Force only applies to snapshots
            run_flag.append('-f')
    else:
        # release flag
        run_flag = ['-r']

    if module.params['keep_files']:
        run_flag.append('-k')

    if module.params['fetch_only']:
        run_flag.append('-n')

    # installurl must be the last argument
    if module.params['installurl']:
        run_flag.append(module.params['installurl'])

    rc, out, err = module.run_command(cmd + run_flag)

    if rc != 0:
        module.fail_json(msg="Command %s failed rc=%d, out=%s, err=%s" % (cmd, rc, out, err))
    elif out.lower().find('already on latest snapshot') >= 0:
        changed = False
    elif out.lower().find('upgrade on next reboot') >= 0:
        changed = True

    return dict(
        changed=changed,
        rc=rc,
        stderr=err,
        stdout=out,
        warnings=warnings
    )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            snapshot=dict(type='bool', default=False),
            fetch_only=dict(type='bool', default=True),
            force=dict(type='bool', default=False),
            keep_files=dict(type='bool', default=False),
            installurl=dict(type='str'),
        ),
        supports_check_mode=False,
    )
    return_dict = sysupgrade_run(module)
    module.exit_json(**return_dict)


if __name__ == '__main__':
    main()

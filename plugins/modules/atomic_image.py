#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: atomic_image
short_description: Manage the container images on the atomic host platform
description:
  - Manage the container images on the atomic host platform.
  - Allows to execute the commands specified by the RUN label in the container image when present.
deprecated:
  removed_in: 13.0.0
  why: Project Atomic was sunset by the end of 2019.
  alternative: There is none.
author:
  - Saravanan KR (@krsacme)
notes:
  - According to U(https://projectatomic.io/) the project has been sunset around 2019/2020, in favor of C(podman) and Fedora CoreOS.
requirements:
  - atomic
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  backend:
    description:
      - Define the backend where the image is pulled.
    choices: ['docker', 'ostree']
    type: str
  name:
    description:
      - Name of the container image.
    required: true
    type: str
  state:
    description:
      - The state of the container image.
      - The state V(latest) will ensure container image is upgraded to the latest version and forcefully restart container,
        if running.
    choices: ['absent', 'latest', 'present']
    default: 'latest'
    type: str
  started:
    description:
      - Start or stop the container.
    type: bool
    default: true
"""

EXAMPLES = r"""
- name: Execute the run command on rsyslog container image (atomic run rhel7/rsyslog)
  community.general.atomic_image:
    name: rhel7/rsyslog
    state: latest

- name: Pull busybox to the OSTree backend
  community.general.atomic_image:
    name: busybox
    state: latest
    backend: ostree
"""

RETURN = r"""
msg:
  description: The command standard output.
  returned: always
  type: str
  sample: 'Using default tag: latest ...'
"""
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def do_upgrade(module, image):
    atomic_bin = module.get_bin_path('atomic')
    args = [atomic_bin, 'update', '--force', image]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:  # something went wrong emit the msg
        module.fail_json(rc=rc, msg=err)
    elif 'Image is up to date' in out:
        return False

    return True


def core(module):
    image = module.params['name']
    state = module.params['state']
    started = module.params['started']
    backend = module.params['backend']
    is_upgraded = False

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')
    atomic_bin = module.get_bin_path('atomic')
    out = {}
    err = {}
    rc = 0

    if backend:
        if state == 'present' or state == 'latest':
            args = [atomic_bin, 'pull', "--storage=%s" % backend, image]
            rc, out, err = module.run_command(args, check_rc=False)
            if rc < 0:
                module.fail_json(rc=rc, msg=err)
            else:
                out_run = ""
                if started:
                    args = [atomic_bin, 'run', "--storage=%s" % backend, image]
                    rc, out_run, err = module.run_command(args, check_rc=False)
                    if rc < 0:
                        module.fail_json(rc=rc, msg=err)

                changed = "Extracting" in out or "Copying blob" in out
                module.exit_json(msg=(out + out_run), changed=changed)
        elif state == 'absent':
            args = [atomic_bin, 'images', 'delete', "--storage=%s" % backend, image]
            rc, out, err = module.run_command(args, check_rc=False)
            if rc < 0:
                module.fail_json(rc=rc, msg=err)
            else:
                changed = "Unable to find" not in out
                module.exit_json(msg=out, changed=changed)
        return

    if state == 'present' or state == 'latest':
        if state == 'latest':
            is_upgraded = do_upgrade(module, image)

        if started:
            args = [atomic_bin, 'run', image]
        else:
            args = [atomic_bin, 'install', image]
    elif state == 'absent':
        args = [atomic_bin, 'uninstall', image]

    rc, out, err = module.run_command(args, check_rc=False)

    if rc < 0:
        module.fail_json(rc=rc, msg=err)
    elif rc == 1 and 'already present' in err:
        module.exit_json(restult=err, changed=is_upgraded)
    elif started and 'Container is running' in out:
        module.exit_json(result=out, changed=is_upgraded)
    else:
        module.exit_json(msg=out, changed=True)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            backend=dict(type='str', choices=['docker', 'ostree']),
            name=dict(type='str', required=True),
            state=dict(type='str', default='latest', choices=['absent', 'latest', 'present']),
            started=dict(type='bool', default=True),
        ),
    )

    # Verify that the platform supports atomic command
    dummy = module.get_bin_path('atomic', required=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

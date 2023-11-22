#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: atomic_container
short_description: Manage the containers on the atomic host platform
description:
    - Manage the containers on the atomic host platform.
    - Allows to manage the lifecycle of a container on the atomic host platform.
author: "Giuseppe Scrivano (@giuseppe)"
notes:
    - Host should support C(atomic) command
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
          - Define the backend to use for the container.
        required: true
        choices: ["docker", "ostree"]
        type: str
    name:
        description:
          - Name of the container.
        required: true
        type: str
    image:
        description:
          - The image to use to install the container.
        required: true
        type: str
    rootfs:
        description:
          - Define the rootfs of the image.
        type: str
    state:
        description:
          - State of the container.
        choices: ["absent", "latest", "present", "rollback"]
        default: "latest"
        type: str
    mode:
        description:
          - Define if it is an user or a system container.
        choices: ["user", "system"]
        type: str
    values:
        description:
            - Values for the installation of the container.
            - This option is permitted only with mode 'user' or 'system'.
            - The values specified here will be used at installation time as --set arguments for atomic install.
        type: list
        elements: str
        default: []
'''

EXAMPLES = r'''

- name: Install the etcd system container
  community.general.atomic_container:
    name: etcd
    image: rhel/etcd
    backend: ostree
    state: latest
    mode: system
    values:
        - ETCD_NAME=etcd.server

- name: Uninstall the etcd system container
  community.general.atomic_container:
    name: etcd
    image: rhel/etcd
    backend: ostree
    state: absent
    mode: system
'''

RETURN = r'''
msg:
    description: The command standard output
    returned: always
    type: str
    sample: 'Using default tag: latest ...'
'''

# import module snippets
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def do_install(module, mode, rootfs, container, image, values_list, backend):
    system_list = ["--system"] if mode == 'system' else []
    user_list = ["--user"] if mode == 'user' else []
    rootfs_list = ["--rootfs=%s" % rootfs] if rootfs else []
    atomic_bin = module.get_bin_path('atomic')
    args = [atomic_bin, 'install', "--storage=%s" % backend, '--name=%s' % container] + system_list + user_list + rootfs_list + values_list + [image]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:
        module.fail_json(rc=rc, msg=err)
    else:
        changed = "Extracting" in out or "Copying blob" in out
        module.exit_json(msg=out, changed=changed)


def do_update(module, container, image, values_list):
    atomic_bin = module.get_bin_path('atomic')
    args = [atomic_bin, 'containers', 'update', "--rebase=%s" % image] + values_list + [container]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:
        module.fail_json(rc=rc, msg=err)
    else:
        changed = "Extracting" in out or "Copying blob" in out
        module.exit_json(msg=out, changed=changed)


def do_uninstall(module, name, backend):
    atomic_bin = module.get_bin_path('atomic')
    args = [atomic_bin, 'uninstall', "--storage=%s" % backend, name]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:
        module.fail_json(rc=rc, msg=err)
    module.exit_json(msg=out, changed=True)


def do_rollback(module, name):
    atomic_bin = module.get_bin_path('atomic')
    args = [atomic_bin, 'containers', 'rollback', name]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:
        module.fail_json(rc=rc, msg=err)
    else:
        changed = "Rolling back" in out
        module.exit_json(msg=out, changed=changed)


def core(module):
    mode = module.params['mode']
    name = module.params['name']
    image = module.params['image']
    rootfs = module.params['rootfs']
    values = module.params['values']
    backend = module.params['backend']
    state = module.params['state']

    atomic_bin = module.get_bin_path('atomic')
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')

    values_list = ["--set=%s" % x for x in values] if values else []

    args = [atomic_bin, 'containers', 'list', '--no-trunc', '-n', '--all', '-f', 'backend=%s' % backend, '-f', 'container=%s' % name]
    rc, out, err = module.run_command(args, check_rc=False)
    if rc != 0:
        module.fail_json(rc=rc, msg=err)
        return
    present = name in out

    if state == 'present' and present:
        module.exit_json(msg=out, changed=False)
    elif (state in ['latest', 'present']) and not present:
        do_install(module, mode, rootfs, name, image, values_list, backend)
    elif state == 'latest':
        do_update(module, name, image, values_list)
    elif state == 'absent':
        if not present:
            module.exit_json(msg="The container is not present", changed=False)
        else:
            do_uninstall(module, name, backend)
    elif state == 'rollback':
        do_rollback(module, name)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mode=dict(choices=['user', 'system']),
            name=dict(required=True),
            image=dict(required=True),
            rootfs=dict(),
            state=dict(default='latest', choices=['present', 'absent', 'latest', 'rollback']),
            backend=dict(required=True, choices=['docker', 'ostree']),
            values=dict(type='list', default=[], elements='str'),
        ),
    )

    if module.params['values'] is not None and module.params['mode'] == 'default':
        module.fail_json(msg="values is supported only with user or system mode")

    # Verify that the platform supports atomic command
    dummy = module.get_bin_path('atomic', required=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg='Unanticipated error running atomic: %s' % to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

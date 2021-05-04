#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sa_pool
short_description: Handles pools on IBM Spectrum Accelerate Family storage systems.

description:
    - "This module creates or deletes pools to be used on IBM Spectrum Accelerate Family storage systems"

options:
    pool:
        description:
            - Pool name.
        required: true
        type: str
    state:
        description:
            - Pool state.
        default: "present"
        choices: [ "present", "absent" ]
        type: str
    size:
        description:
            - Pool size in GB
        required: false
        type: str
    snapshot_size:
        description:
            - Pool snapshot size in GB
        required: false
        type: str
    domain:
        description:
            - Adds the pool to the specified domain.
        required: false
        type: str
    perf_class:
        description:
            - Assigns a perf_class to the pool.
        required: false
        type: str

extends_documentation_fragment:
- community.general.ibm_storage


author:
    - Tzur Eliyahu (@tzure)
'''

EXAMPLES = '''
- name: Create new pool.
  community.general.ibm_sa_pool:
    name: pool_name
    size: 300
    state: present
    username: admin
    password: secret
    endpoints: hostdev-system

- name: Delete pool.
  community.general.ibm_sa_pool:
    name: pool_name
    state: absent
    username: admin
    password: secret
    endpoints: hostdev-system
'''
RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ibm_sa_utils import execute_pyxcli_command, \
    connect_ssl, spectrum_accelerate_spec, is_pyxcli_installed


def main():
    argument_spec = spectrum_accelerate_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent']),
            pool=dict(required=True),
            size=dict(),
            snapshot_size=dict(),
            domain=dict(),
            perf_class=dict()
        )
    )

    module = AnsibleModule(argument_spec)

    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    pool = xcli_client.cmd.pool_list(
        pool=module.params['pool']).as_single_element
    state = module.params['state']

    state_changed = False
    if state == 'present' and not pool:
        state_changed = execute_pyxcli_command(
            module, 'pool_create', xcli_client)
    if state == 'absent' and pool:
        state_changed = execute_pyxcli_command(
            module, 'pool_delete', xcli_client)

    module.exit_json(changed=state_changed)


if __name__ == '__main__':
    main()

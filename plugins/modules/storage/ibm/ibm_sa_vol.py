#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sa_vol
short_description: Handle volumes on IBM Spectrum Accelerate Family storage systems.

description:
    - "This module creates or deletes volumes to be used on IBM Spectrum Accelerate Family storage systems."

options:
    vol:
        description:
            - Volume name.
        required: true
        type: str
    pool:
        description:
            - Volume pool.
        required: false
        type: str
    state:
        description:
            - Volume state.
        default: "present"
        choices: [ "present", "absent" ]
        type: str
    size:
        description:
            - Volume size.
        required: false
        type: str

extends_documentation_fragment:
- community.general.ibm_storage


author:
    - Tzur Eliyahu (@tzure)
'''

EXAMPLES = '''
- name: Create a new volume.
  community.general.ibm_sa_vol:
    vol: volume_name
    pool: pool_name
    size: 17
    state: present
    username: admin
    password: secret
    endpoints: hostdev-system

- name: Delete an existing volume.
  community.general.ibm_sa_vol:
    vol: volume_name
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
            vol=dict(required=True),
            pool=dict(),
            size=dict()
        )
    )

    module = AnsibleModule(argument_spec)

    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    # required args
    volume = xcli_client.cmd.vol_list(
        vol=module.params.get('vol')).as_single_element
    state = module.params['state']

    state_changed = False
    if state == 'present' and not volume:
        state_changed = execute_pyxcli_command(
            module, 'vol_create', xcli_client)
    elif state == 'absent' and volume:
        state_changed = execute_pyxcli_command(
            module, 'vol_delete', xcli_client)

    module.exit_json(changed=state_changed)


if __name__ == '__main__':
    main()

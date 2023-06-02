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
module: ibm_sa_host_ports
short_description: Add host ports on IBM Spectrum Accelerate Family storage systems

description:
    - "This module adds ports to or removes them from the hosts
        on IBM Spectrum Accelerate Family storage systems."

options:
    host:
        description:
            - Host name.
        required: true
        type: str
    state:
        description:
            - Host ports state.
        default: "present"
        choices: [ "present", "absent" ]
        type: str
    iscsi_name:
        description:
            - iSCSI initiator name.
        required: false
        type: str
    fcaddress:
        description:
            - Fiber channel address.
        required: false
        type: str
    num_of_visible_targets:
        description:
            - Number of visible targets.
        required: false
        type: str

extends_documentation_fragment:
- community.general.ibm_storage

author:
    - Tzur Eliyahu (@tzure)
'''

EXAMPLES = '''
- name: Add ports for host.
  community.general.ibm_sa_host_ports:
    host: test_host
    iscsi_name: iqn.1994-05.com***
    username: admin
    password: secret
    endpoints: hostdev-system
    state: present

- name: Remove ports for host.
  community.general.ibm_sa_host_ports:
    host: test_host
    iscsi_name: iqn.1994-05.com***
    username: admin
    password: secret
    endpoints: hostdev-system
    state: absent

'''
RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ibm_sa_utils import (execute_pyxcli_command, connect_ssl,
                                                                                     spectrum_accelerate_spec, is_pyxcli_installed)


def main():
    argument_spec = spectrum_accelerate_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent']),
            host=dict(required=True),
            iscsi_name=dict(),
            fcaddress=dict(),
            num_of_visible_targets=dict()
        )
    )

    module = AnsibleModule(argument_spec)
    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    # required args
    ports = []
    try:
        ports = xcli_client.cmd.host_list_ports(
            host=module.params.get('host')).as_list
    except Exception:
        pass
    state = module.params['state']
    port_exists = False
    ports = [port.get('port_name') for port in ports]

    fc_ports = (module.params.get('fcaddress')
                if module.params.get('fcaddress') else [])
    iscsi_ports = (module.params.get('iscsi_name')
                   if module.params.get('iscsi_name') else [])
    for port in ports:
        if port in iscsi_ports or port in fc_ports:
            port_exists = True
            break
    state_changed = False
    if state == 'present' and not port_exists:
        state_changed = execute_pyxcli_command(
            module, 'host_add_port', xcli_client)
    if state == 'absent' and port_exists:
        state_changed = execute_pyxcli_command(
            module, 'host_remove_port', xcli_client)

    module.exit_json(changed=state_changed)


if __name__ == '__main__':
    main()

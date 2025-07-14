#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ibm_sa_host
short_description: Adds hosts to or removes them from IBM Spectrum Accelerate Family storage systems

description:
  - This module adds hosts to or removes them from IBM Spectrum Accelerate Family storage systems.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  host:
    description:
      - Host name.
    required: true
    type: str
  state:
    description:
      - Host state.
    default: "present"
    choices: ["present", "absent"]
    type: str
  cluster:
    description:
      - The name of the cluster to include the host.
    required: false
    type: str
  domain:
    description:
      - The domains the cluster is attached to. To include more than one domain, separate domain names with commas. To include
        all existing domains, use an asterisk (V(*)).
    required: false
    type: str
  iscsi_chap_name:
    description:
      - The host's CHAP name identifier.
    required: false
    type: str
  iscsi_chap_secret:
    description:
      - The password of the initiator used to authenticate to the system when CHAP is enable.
    required: false
    type: str

extends_documentation_fragment:
  - community.general.ibm_storage
  - community.general.attributes

author:
  - Tzur Eliyahu (@tzure)
"""

EXAMPLES = r"""
- name: Define new host.
  community.general.ibm_sa_host:
    host: host_name
    state: present
    username: admin
    password: secret
    endpoints: hostdev-system

- name: Delete host.
  community.general.ibm_sa_host:
    host: host_name
    state: absent
    username: admin
    password: secret
    endpoints: hostdev-system
"""
RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ibm_sa_utils import execute_pyxcli_command, \
    connect_ssl, spectrum_accelerate_spec, is_pyxcli_installed


def main():
    argument_spec = spectrum_accelerate_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent']),
            host=dict(required=True),
            cluster=dict(),
            domain=dict(),
            iscsi_chap_name=dict(),
            iscsi_chap_secret=dict(no_log=True),
        )
    )

    module = AnsibleModule(argument_spec)

    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    host = xcli_client.cmd.host_list(
        host=module.params['host']).as_single_element
    state = module.params['state']

    state_changed = False
    if state == 'present' and not host:
        state_changed = execute_pyxcli_command(
            module, 'host_define', xcli_client)
    elif state == 'absent' and host:
        state_changed = execute_pyxcli_command(
            module, 'host_delete', xcli_client)

    module.exit_json(changed=state_changed)


if __name__ == '__main__':
    main()

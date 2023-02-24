#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sa_domain
short_description: Manages domains on IBM Spectrum Accelerate Family storage systems

description:
    - "This module can be used to add domains to or removes them from IBM Spectrum Accelerate Family storage systems."

attributes:
    check_mode:
        support: none
    diff_mode:
        support: none

options:
    domain:
        description:
            - Name of the domain to be managed.
        required: true
        type: str
    state:
        description:
            - The desired state of the domain.
        default: "present"
        choices: [ "present", "absent" ]
        type: str
    ldap_id:
        description:
            - ldap id to add to the domain.
        required: false
        type: str
    size:
        description:
            - Size of the domain.
        required: false
        type: str
    hard_capacity:
        description:
            - Hard capacity of the domain.
        required: false
        type: str
    soft_capacity:
        description:
            - Soft capacity of the domain.
        required: false
        type: str
    max_cgs:
        description:
            - Number of max cgs.
        required: false
        type: str
    max_dms:
        description:
            - Number of max dms.
        required: false
        type: str
    max_mirrors:
        description:
            - Number of max_mirrors.
        required: false
        type: str
    max_pools:
        description:
            - Number of max_pools.
        required: false
        type: str
    max_volumes:
        description:
            - Number of max_volumes.
        required: false
        type: str
    perf_class:
        description:
            - Add the domain to a performance class.
        required: false
        type: str

extends_documentation_fragment:
  - community.general.ibm_storage
  - community.general.attributes

author:
    - Tzur Eliyahu (@tzure)
'''

EXAMPLES = '''
- name: Define new domain.
  community.general.ibm_sa_domain:
    domain: domain_name
    size: domain_size
    state: present
    username: admin
    password: secret
    endpoints: hostdev-system

- name: Delete domain.
  community.general.ibm_sa_domain:
    domain: domain_name
    state: absent
    username: admin
    password: secret
    endpoints: hostdev-system
'''
RETURN = '''
msg:
    description: module return status.
    returned: as needed
    type: str
    sample: "domain 'domain_name' created successfully."
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ibm_sa_utils import execute_pyxcli_command, \
    connect_ssl, spectrum_accelerate_spec, is_pyxcli_installed


def main():
    argument_spec = spectrum_accelerate_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present', 'absent']),
            domain=dict(required=True),
            size=dict(),
            max_dms=dict(),
            max_cgs=dict(),
            ldap_id=dict(),
            max_mirrors=dict(),
            max_pools=dict(),
            max_volumes=dict(),
            perf_class=dict(),
            hard_capacity=dict(),
            soft_capacity=dict()
        )
    )

    module = AnsibleModule(argument_spec)

    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    domain = xcli_client.cmd.domain_list(
        domain=module.params['domain']).as_single_element
    state = module.params['state']

    state_changed = False
    msg = 'Domain \'{0}\''.format(module.params['domain'])
    if state == 'present' and not domain:
        state_changed = execute_pyxcli_command(
            module, 'domain_create', xcli_client)
        msg += " created successfully."
    elif state == 'absent' and domain:
        state_changed = execute_pyxcli_command(
            module, 'domain_delete', xcli_client)
        msg += " deleted successfully."
    else:
        msg += " state unchanged."

    module.exit_json(changed=state_changed, msg=msg)


if __name__ == '__main__':
    main()

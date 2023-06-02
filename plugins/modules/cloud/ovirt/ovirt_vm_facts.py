#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat, Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ovirt_vm_facts
short_description: Retrieve information about one or more oVirt/RHV virtual machines
author: "Ondra Machacek (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_vm_info) instead.
description:
    - "Retrieve information about one or more oVirt/RHV virtual machines."
notes:
    - "This module returns a variable C(ovirt_vms), which
       contains a list of virtual machines. You need to register the result with
       the I(register) keyword to use it."
options:
    pattern:
      description:
        - "Search term which is accepted by oVirt/RHV search backend."
        - "For example to search VM X from cluster Y use following pattern:
           name=X and cluster=Y"
    all_content:
      description:
        - "If I(true) all the attributes of the virtual machines should be
           included in the response."
      type: bool
    case_sensitive:
      description:
        - "If I(true) performed search will take case into account."
      type: bool
      default: true
    max:
      description:
        - "The maximum number of results to return."
    next_run:
      description:
        - "Indicates if the returned result describes the virtual machine as it is currently running or if describes
           the virtual machine with the modifications that have already been performed but that will only come into
           effect when the virtual machine is restarted. By default the value is set by engine."
      type: bool
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all VMs which names start with centos and belong to cluster west
  ovirt_vm_info:
    pattern: name=centos* and cluster=west
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_vms }}"

- name: Gather info about next run configuration of virtual machine named myvm
  ovirt_vm_info:
    pattern: name=myvm
    next_run: true
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_vms[0] }}"
'''

RETURN = '''
ovirt_vms:
    description: "List of dictionaries describing the VMs. VM attributes are mapped to dictionary keys,
                  all VMs attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/vm."
    returned: On success.
    type: list
'''

import traceback

from ansible.module_utils.common.removed import removed_module
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils._ovirt import (
    check_sdk,
    create_connection,
    get_dict_of_struct,
    ovirt_info_full_argument_spec,
)


def main():
    argument_spec = ovirt_info_full_argument_spec(
        pattern=dict(default='', required=False),
        all_content=dict(default=False, type='bool'),
        next_run=dict(default=None, type='bool'),
        case_sensitive=dict(default=True, type='bool'),
        max=dict(default=None, type='int'),
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_vm_facts', 'community.general.ovirt_vm_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_vm_facts' module has been renamed to 'ovirt_vm_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        vms_service = connection.system_service().vms_service()
        vms = vms_service.list(
            search=module.params['pattern'],
            all_content=module.params['all_content'],
            case_sensitive=module.params['case_sensitive'],
            max=module.params['max'],
        )
        if module.params['next_run']:
            vms = [vms_service.vm_service(vm.id).get(next_run=True) for vm in vms]

        result = dict(
            ovirt_vms=[
                get_dict_of_struct(
                    struct=c,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for c in vms
            ],
        )
        if is_old_facts:
            module.exit_json(changed=False, ansible_facts=result)
        else:
            module.exit_json(changed=False, **result)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == '__main__':
    main()

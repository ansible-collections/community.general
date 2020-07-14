#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat, Inc.
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
module: ovirt_disk_facts
short_description: Retrieve information about one or more oVirt/RHV disks
author: "Katerina Koukiou (@KKoukiou)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_disk_info) instead
description:
    - "Retrieve information about one or more oVirt/RHV disks."
notes:
    - "This module returns a variable C(ovirt_disks), which
       contains a list of disks. You need to register the result with
       the I(register) keyword to use it."
options:
    pattern:
      description:
        - "Search term which is accepted by oVirt/RHV search backend."
        - "For example to search Disk X from storage Y use following pattern:
           name=X and storage.name=Y"
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all Disks which names start with centos
  ovirt_disk_info:
    pattern: name=centos*
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_disks }}"
'''

RETURN = '''
ovirt_disks:
    description: "List of dictionaries describing the Disks. Disk attributes are mapped to dictionary keys,
                  all Disks attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/disk."
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
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_disk_facts', 'community.general.ovirt_disk_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_disk_facts' module has been renamed to 'ovirt_disk_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13
    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        disks_service = connection.system_service().disks_service()
        disks = disks_service.list(
            search=module.params['pattern'],
        )
        result = dict(
            ovirt_disks=[
                get_dict_of_struct(
                    struct=c,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for c in disks
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

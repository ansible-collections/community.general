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
module: ovirt_network_facts
short_description: Retrieve information about one or more oVirt/RHV networks
author: "Ondra Machacek (@machacekondra)"
deprecated:
    removed_in: "2.14"
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use C(ovirt_network_info) from the C(ovirt.ovirt) collection instead
description:
    - "Retrieve information about one or more oVirt/RHV networks."
    - This module was called C(ovirt_network_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(ovirt_network_info) module no longer returns C(ansible_facts)!
notes:
    - "This module returns a variable C(ovirt_networks), which
       contains a list of networks. You need to register the result with
       the I(register) keyword to use it."
options:
    pattern:
      description:
        - "Search term which is accepted by oVirt/RHV search backend."
        - "For example to search network starting with string vlan1 use: name=vlan1*"
extends_documentation_fragment:
- community.general.ovirt_facts

'''


EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all networks which names start with vlan1
  ovirt_network_info:
    pattern: name=vlan1*
  register: result

- name: Print gathered information
  debug:
    msg: "{{ result.ovirt_networks }}"
'''


RETURN = '''
ovirt_networks:
    description: "List of dictionaries describing the networks. Network attributes are mapped to dictionary keys,
                  all networks attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/network."
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
    is_old_facts = module._name in ('ovirt_network_facts', 'community.general.ovirt_network_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_network_facts' module has been renamed to 'ovirt_network_info', "
                         "and the renamed one no longer returns ansible_facts", version='2.13')

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        networks_service = connection.system_service().networks_service()
        networks = networks_service.list(search=module.params['pattern'])
        result = dict(
            ovirt_networks=[
                get_dict_of_struct(
                    struct=c,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for c in networks
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

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
module: ovirt_quota_facts
short_description: Retrieve information about one or more oVirt/RHV quotas
author: "Maor Lipchuk (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_quota_info) instead.
description:
    - "Retrieve information about one or more oVirt/RHV quotas."
notes:
    - "This module returns a variable C(ovirt_quotas), which
       contains a list of quotas. You need to register the result with
       the I(register) keyword to use it."
options:
    data_center:
        description:
            - "Name of the datacenter where quota resides."
        required: true
    name:
        description:
            - "Name of the quota, can be used as glob expression."
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about quota named C<myquota> in Default datacenter
  ovirt_quota_info:
    data_center: Default
    name: myquota
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_quotas }}"
'''

RETURN = '''
ovirt_quotas:
    description: "List of dictionaries describing the quotas. Quota attributes are mapped to dictionary keys,
                  all quotas attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/quota."
    returned: On success.
    type: list
'''

import fnmatch
import traceback

from ansible.module_utils.common.removed import removed_module
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils._ovirt import (
    check_sdk,
    create_connection,
    get_dict_of_struct,
    ovirt_info_full_argument_spec,
    search_by_name,
)


def main():
    argument_spec = ovirt_info_full_argument_spec(
        data_center=dict(required=True),
        name=dict(default=None),
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_quota_facts', 'community.general.ovirt_quota_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_quota_facts' module has been renamed to 'ovirt_quota_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        datacenters_service = connection.system_service().data_centers_service()
        dc_name = module.params['data_center']
        dc = search_by_name(datacenters_service, dc_name)
        if dc is None:
            raise Exception("Datacenter '%s' was not found." % dc_name)

        quotas_service = datacenters_service.service(dc.id).quotas_service()
        if module.params['name']:
            quotas = [
                e for e in quotas_service.list()
                if fnmatch.fnmatch(e.name, module.params['name'])
            ]
        else:
            quotas = quotas_service.list()

        result = dict(
            ovirt_quotas=[
                get_dict_of_struct(
                    struct=c,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for c in quotas
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

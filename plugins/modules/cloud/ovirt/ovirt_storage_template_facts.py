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
module: ovirt_storage_template_facts
short_description: Retrieve information about one or more oVirt/RHV templates relate to a storage domain.
author: "Maor Lipchuk (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_storage_template_info) instead.
description:
    - "Retrieve information about one or more oVirt/RHV templates relate to a storage domain."
notes:
    - "This module returns a variable C(ovirt_storage_templates), which
       contains a list of templates. You need to register the result with
       the I(register) keyword to use it."
options:
    unregistered:
        description:
            - "Flag which indicates whether to get unregistered templates which contain one or more
               disks which reside on a storage domain or diskless templates."
        type: bool
        default: false
    max:
        description:
            - "Sets the maximum number of templates to return. If not specified all the templates are returned."
    storage_domain:
        description:
            - "The storage domain name where the templates should be listed."
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all templates which relate to a storage domain and are unregistered
  ovirt_storage_template_info:
    unregistered: yes
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_storage_templates }}"
'''

RETURN = '''
ovirt_storage_templates:
    description: "List of dictionaries describing the Templates. Template attributes are mapped to dictionary keys,
                  all Templates attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/template."
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
    get_id_by_name
)


def main():
    argument_spec = ovirt_info_full_argument_spec(
        storage_domain=dict(default=None),
        max=dict(default=None, type='int'),
        unregistered=dict(default=False, type='bool'),
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_storage_template_facts', 'community.general.ovirt_storage_template_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_storage_template_facts' module has been renamed to 'ovirt_storage_template_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        storage_domains_service = connection.system_service().storage_domains_service()
        sd_id = get_id_by_name(storage_domains_service, module.params['storage_domain'])
        storage_domain_service = storage_domains_service.storage_domain_service(sd_id)
        templates_service = storage_domain_service.templates_service()

        # Find the unregistered Template we want to register:
        if module.params.get('unregistered'):
            templates = templates_service.list(unregistered=True)
        else:
            templates = templates_service.list(max=module.params['max'])
        result = dict(
            ovirt_storage_templates=[
                get_dict_of_struct(
                    struct=c,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for c in templates
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

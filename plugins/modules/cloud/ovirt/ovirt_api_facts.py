#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ovirt_api_facts
short_description: Retrieve information about the oVirt/RHV API
author: "Ondra Machacek (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_api_info) instead.
description:
    - "Retrieve information about the oVirt/RHV API."
notes:
    - "This module returns a variable C(ovirt_api),
       which contains a information about oVirt/RHV API. You need to register the result with
       the I(register) keyword to use it."
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information oVirt API
  ovirt_api_info:
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_api }}"
'''

RETURN = '''
ovirt_api:
    description: "Dictionary describing the oVirt API information.
                  Api attributes are mapped to dictionary keys,
                  all API attributes can be found at following
                  url: https://ovirt.example.com/ovirt-engine/api/model#types/api."
    returned: On success.
    type: dict
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
    argument_spec = ovirt_info_full_argument_spec()
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_api_facts', 'community.general.ovirt_api_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_api_facts' module has been renamed to 'ovirt_api_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13
    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        api = connection.system_service().get()
        result = dict(
            ovirt_api=get_dict_of_struct(
                struct=api,
                connection=connection,
                fetch_nested=module.params.get('fetch_nested'),
                attributes=module.params.get('nested_attributes'),
            )
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

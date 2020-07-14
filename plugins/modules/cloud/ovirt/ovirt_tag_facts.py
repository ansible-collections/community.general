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
module: ovirt_tag_facts
short_description: Retrieve information about one or more oVirt/RHV tags
author: "Ondra Machacek (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_tag_info) instead.
description:
    - "Retrieve information about one or more oVirt/RHV tags."
notes:
    - "This module returns a variable C(ovirt_tags), which
       contains a list of tags. You need to register the result with
       the I(register) keyword to use it."
options:
    name:
      description:
        - "Name of the tag which should be listed."
    vm:
      description:
        - "Name of the VM, which tags should be listed."
    host:
      description:
        - "Name of the host, which tags should be listed."
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all tags, which names start with tag
  ovirt_tag_info:
    name: tag*
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_tags }}"

- name: Gather information about all tags, which are assigned to VM postgres
  ovirt_tag_info:
    vm: postgres
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_tags }}"

- name: Gather information about all tags, which are assigned to host west
  ovirt_tag_info:
    host: west
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_tags }}"
'''

RETURN = '''
ovirt_tags:
    description: "List of dictionaries describing the tags. Tags attributes are mapped to dictionary keys,
                  all tags attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/tag."
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
        name=dict(default=None),
        host=dict(default=None),
        vm=dict(default=None),
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_tag_facts', 'community.general.ovirt_tag_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_tag_facts' module has been renamed to 'ovirt_tag_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        tags_service = connection.system_service().tags_service()
        tags = []
        all_tags = tags_service.list()
        if module.params['name']:
            tags.extend([
                t for t in all_tags
                if fnmatch.fnmatch(t.name, module.params['name'])
            ])
        if module.params['host']:
            hosts_service = connection.system_service().hosts_service()
            host = search_by_name(hosts_service, module.params['host'])
            if host is None:
                raise Exception("Host '%s' was not found." % module.params['host'])
            tags.extend([
                tag for tag in hosts_service.host_service(host.id).tags_service().list()
            ])
        if module.params['vm']:
            vms_service = connection.system_service().vms_service()
            vm = search_by_name(vms_service, module.params['vm'])
            if vm is None:
                raise Exception("Vm '%s' was not found." % module.params['vm'])
            tags.extend([
                tag for tag in vms_service.vm_service(vm.id).tags_service().list()
            ])

        if not (module.params['vm'] or module.params['host'] or module.params['name']):
            tags = all_tags

        result = dict(
            ovirt_tags=[
                get_dict_of_struct(
                    struct=t,
                    connection=connection,
                    fetch_nested=module.params['fetch_nested'],
                    attributes=module.params['nested_attributes'],
                ) for t in tags
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

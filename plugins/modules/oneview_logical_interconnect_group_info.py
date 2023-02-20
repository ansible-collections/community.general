#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: oneview_logical_interconnect_group_info
short_description: Retrieve information about one or more of the OneView Logical Interconnect Groups
description:
    - Retrieve information about one or more of the Logical Interconnect Groups from OneView
    - This module was called C(oneview_logical_interconnect_group_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(community.general.oneview_logical_interconnect_group_info) module no longer returns C(ansible_facts)!
requirements:
    - hpOneView >= 2.0.1
author:
    - Felipe Bulsoni (@fgbulsoni)
    - Thiago Miotto (@tmiotto)
    - Adriane Cardozo (@adriane-cardozo)
attributes:
    check_mode:
        version_added: 3.3.0
        # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
    name:
      description:
        - Logical Interconnect Group name.
      type: str
extends_documentation_fragment:
  - community.general.oneview
  - community.general.oneview.factsparams
  - community.general.attributes
  - community.general.attributes.info_module

'''

EXAMPLES = '''
- name: Gather information about all Logical Interconnect Groups
  community.general.oneview_logical_interconnect_group_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Logical Interconnect Groups
  ansible.builtin.debug:
    msg: "{{ result.logical_interconnect_groups }}"

- name: Gather paginated, filtered and sorted information about Logical Interconnect Groups
  community.general.oneview_logical_interconnect_group_info:
    params:
      start: 0
      count: 3
      sort: name:descending
      filter: name=LIGName
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about paginated, filtered and sorted list of Logical Interconnect Groups
  ansible.builtin.debug:
    msg: "{{ result.logical_interconnect_groups }}"

- name: Gather information about a Logical Interconnect Group by name
  community.general.oneview_logical_interconnect_group_info:
    name: logical interconnect group name
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- name: Print fetched information about Logical Interconnect Group found by name
  ansible.builtin.debug:
    msg: "{{ result.logical_interconnect_groups }}"
'''

RETURN = '''
logical_interconnect_groups:
    description: Has all the OneView information about the Logical Interconnect Groups.
    returned: Always, but can be null.
    type: dict
'''

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class LogicalInterconnectGroupInfoModule(OneViewModuleBase):
    def __init__(self):

        argument_spec = dict(
            name=dict(type='str'),
            params=dict(type='dict'),
        )

        super(LogicalInterconnectGroupInfoModule, self).__init__(
            additional_arg_spec=argument_spec,
            supports_check_mode=True,
        )

    def execute_module(self):
        if self.module.params.get('name'):
            ligs = self.oneview_client.logical_interconnect_groups.get_by('name', self.module.params['name'])
        else:
            ligs = self.oneview_client.logical_interconnect_groups.get_all(**self.facts_params)

        return dict(changed=False, logical_interconnect_groups=ligs)


def main():
    LogicalInterconnectGroupInfoModule().run()


if __name__ == '__main__':
    main()

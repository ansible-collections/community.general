#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: oneview_datacenter_info
short_description: Retrieve information about the OneView Data Centers
description:
    - Retrieve information about the OneView Data Centers.
    - This module was called C(oneview_datacenter_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(community.general.oneview_datacenter_info) module no longer returns C(ansible_facts)!
requirements:
    - "hpOneView >= 2.0.1"
author:
    - Alex Monteiro (@aalexmonteiro)
    - Madhav Bharadwaj (@madhav-bharadwaj)
    - Priyanka Sood (@soodpr)
    - Ricardo Galeno (@ricardogpsf)
options:
    name:
      description:
        - Data Center name.
      type: str
    options:
      description:
        - "Retrieve additional information. Options available: 'visualContent'."
      type: list
      elements: str

extends_documentation_fragment:
- community.general.oneview
- community.general.oneview.factsparams

'''

EXAMPLES = '''
- name: Gather information about all Data Centers
  community.general.oneview_datacenter_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  delegate_to: localhost
  register: result

- name: Print fetched information about Data Centers
  ansible.builtin.debug:
    msg: "{{ result.datacenters }}"

- name: Gather paginated, filtered and sorted information about Data Centers
  community.general.oneview_datacenter_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    params:
      start: 0
      count: 3
      sort: 'name:descending'
      filter: 'state=Unmanaged'
  register: result

- name: Print fetched information about paginated, filtered and sorted list of Data Centers
  ansible.builtin.debug:
    msg: "{{ result.datacenters }}"

- name: Gather information about a Data Center by name
  community.general.oneview_datacenter_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    name: "My Data Center"
  delegate_to: localhost
  register: result

- name: Print fetched information about Data Center found by name
  ansible.builtin.debug:
    msg: "{{ result.datacenters }}"

- name: Gather information about the Data Center Visual Content
  community.general.oneview_datacenter_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    name: "My Data Center"
    options:
      - visualContent
  delegate_to: localhost
  register: result

- name: Print fetched information about Data Center found by name
  ansible.builtin.debug:
    msg: "{{ result.datacenters }}"

- name: Print fetched information about Data Center Visual Content
  ansible.builtin.debug:
    msg: "{{ result.datacenter_visual_content }}"
'''

RETURN = '''
datacenters:
    description: Has all the OneView information about the Data Centers.
    returned: Always, but can be null.
    type: dict

datacenter_visual_content:
    description: Has information about the Data Center Visual Content.
    returned: When requested, but can be null.
    type: dict
'''

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class DatacenterInfoModule(OneViewModuleBase):
    argument_spec = dict(
        name=dict(type='str'),
        options=dict(type='list', elements='str'),
        params=dict(type='dict')
    )

    def __init__(self):
        super(DatacenterInfoModule, self).__init__(
            additional_arg_spec=self.argument_spec,
            supports_check_mode=True,
        )

    def execute_module(self):

        client = self.oneview_client.datacenters
        info = {}

        if self.module.params.get('name'):
            datacenters = client.get_by('name', self.module.params['name'])

            if self.options and 'visualContent' in self.options:
                if datacenters:
                    info['datacenter_visual_content'] = client.get_visual_content(datacenters[0]['uri'])
                else:
                    info['datacenter_visual_content'] = None

            info['datacenters'] = datacenters
        else:
            info['datacenters'] = client.get_all(**self.facts_params)

        return dict(changed=False, **info)


def main():
    DatacenterInfoModule().run()


if __name__ == '__main__':
    main()

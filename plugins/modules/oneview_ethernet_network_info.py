#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: oneview_ethernet_network_info
short_description: Retrieve the information about one or more of the OneView Ethernet Networks
description:
    - Retrieve the information about one or more of the Ethernet Networks from OneView.
    - This module was called C(oneview_ethernet_network_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(community.general.oneview_ethernet_network_info) module no longer returns C(ansible_facts)!
requirements:
    - hpOneView >= 2.0.1
author:
    - Felipe Bulsoni (@fgbulsoni)
    - Thiago Miotto (@tmiotto)
    - Adriane Cardozo (@adriane-cardozo)
options:
    name:
      description:
        - Ethernet Network name.
      type: str
    options:
      description:
        - "List with options to gather additional information about an Ethernet Network and related resources.
          Options allowed: C(associatedProfiles) and C(associatedUplinkGroups)."
      type: list
      elements: str
extends_documentation_fragment:
  - community.general.oneview
  - community.general.oneview.factsparams
  - community.general.attributes
  - community.general.attributes.info_module

'''

EXAMPLES = '''
- name: Gather information about all Ethernet Networks
  community.general.oneview_ethernet_network_info:
    config: /etc/oneview/oneview_config.json
  delegate_to: localhost
  register: result

- name: Print fetched information about Ethernet Networks
  ansible.builtin.debug:
    msg: "{{ result.ethernet_networks }}"

- name: Gather paginated and filtered information about Ethernet Networks
  community.general.oneview_ethernet_network_info:
    config: /etc/oneview/oneview_config.json
    params:
      start: 1
      count: 3
      sort: 'name:descending'
      filter: 'purpose=General'
  delegate_to: localhost
  register: result

- name: Print fetched information about paginated and filtered list of Ethernet Networks
  ansible.builtin.debug:
    msg: "{{ result.ethernet_networks }}"

- name: Gather information about an Ethernet Network by name
  community.general.oneview_ethernet_network_info:
    config: /etc/oneview/oneview_config.json
    name: Ethernet network name
  delegate_to: localhost
  register: result

- name: Print fetched information about Ethernet Network found by name
  ansible.builtin.debug:
    msg: "{{ result.ethernet_networks }}"

- name: Gather information about an Ethernet Network by name with options
  community.general.oneview_ethernet_network_info:
    config: /etc/oneview/oneview_config.json
    name: eth1
    options:
      - associatedProfiles
      - associatedUplinkGroups
  delegate_to: localhost
  register: result

- name: Print fetched information about Ethernet Network Associated Profiles
  ansible.builtin.debug:
    msg: "{{ result.enet_associated_profiles }}"

- name: Print fetched information about Ethernet Network Associated Uplink Groups
  ansible.builtin.debug:
    msg: "{{ result.enet_associated_uplink_groups }}"
'''

RETURN = '''
ethernet_networks:
    description: Has all the OneView information about the Ethernet Networks.
    returned: Always, but can be null.
    type: dict

enet_associated_profiles:
    description: Has all the OneView information about the profiles which are using the Ethernet network.
    returned: When requested, but can be null.
    type: dict

enet_associated_uplink_groups:
    description: Has all the OneView information about the uplink sets which are using the Ethernet network.
    returned: When requested, but can be null.
    type: dict
'''

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class EthernetNetworkInfoModule(OneViewModuleBase):
    argument_spec = dict(
        name=dict(type='str'),
        options=dict(type='list', elements='str'),
        params=dict(type='dict')
    )

    def __init__(self):
        super(EthernetNetworkInfoModule, self).__init__(
            additional_arg_spec=self.argument_spec,
            supports_check_mode=True,
        )

        self.resource_client = self.oneview_client.ethernet_networks

    def execute_module(self):
        info = {}
        if self.module.params['name']:
            ethernet_networks = self.resource_client.get_by('name', self.module.params['name'])

            if self.module.params.get('options') and ethernet_networks:
                info = self.__gather_optional_info(ethernet_networks[0])
        else:
            ethernet_networks = self.resource_client.get_all(**self.facts_params)

        info['ethernet_networks'] = ethernet_networks

        return dict(changed=False, **info)

    def __gather_optional_info(self, ethernet_network):

        info = {}

        if self.options.get('associatedProfiles'):
            info['enet_associated_profiles'] = self.__get_associated_profiles(ethernet_network)
        if self.options.get('associatedUplinkGroups'):
            info['enet_associated_uplink_groups'] = self.__get_associated_uplink_groups(ethernet_network)

        return info

    def __get_associated_profiles(self, ethernet_network):
        associated_profiles = self.resource_client.get_associated_profiles(ethernet_network['uri'])
        return [self.oneview_client.server_profiles.get(x) for x in associated_profiles]

    def __get_associated_uplink_groups(self, ethernet_network):
        uplink_groups = self.resource_client.get_associated_uplink_groups(ethernet_network['uri'])
        return [self.oneview_client.uplink_sets.get(x) for x in uplink_groups]


def main():
    EthernetNetworkInfoModule().run()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: oneview_network_set_info
short_description: Retrieve information about the OneView Network Sets
description:
    - Retrieve information about the Network Sets from OneView.
    - This module was called C(oneview_network_set_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(community.general.oneview_network_set_info) module no longer returns C(ansible_facts)!
requirements:
    - hpOneView >= 2.0.1
author:
    - Felipe Bulsoni (@fgbulsoni)
    - Thiago Miotto (@tmiotto)
    - Adriane Cardozo (@adriane-cardozo)
options:
    name:
      description:
        - Network Set name.

    options:
      description:
        - "List with options to gather information about Network Set.
          Option allowed: C(withoutEthernet).
          The option C(withoutEthernet) retrieves the list of network_sets excluding Ethernet networks."

extends_documentation_fragment:
- community.general.oneview
- community.general.oneview.factsparams

'''

EXAMPLES = '''
- name: Gather information about all Network Sets
  community.general.oneview_network_set_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
  no_log: true
  delegate_to: localhost
  register: result

- ansible.builtin.debug:
    msg: "{{ result.network_sets }}"

- name: Gather paginated, filtered, and sorted information about Network Sets
  community.general.oneview_network_set_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    params:
      start: 0
      count: 3
      sort: 'name:descending'
      filter: name='netset001'
  no_log: true
  delegate_to: localhost
  register: result

- ansible.builtin.debug:
    msg: "{{ result.network_sets }}"

- name: Gather information about all Network Sets, excluding Ethernet networks
  community.general.oneview_network_set_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    options:
        - withoutEthernet
  no_log: true
  delegate_to: localhost
  register: result

- ansible.builtin.debug:
    msg: "{{ result.network_sets }}"

- name: Gather information about a Network Set by name
  community.general.oneview_network_set_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    name: Name of the Network Set
  no_log: true
  delegate_to: localhost
  register: result

- ansible.builtin.debug:
    msg: "{{ result.network_sets }}"

- name: Gather information about a Network Set by name, excluding Ethernet networks
  community.general.oneview_network_set_info:
    hostname: 172.16.101.48
    username: administrator
    password: my_password
    api_version: 500
    name: Name of the Network Set
    options:
        - withoutEthernet
  no_log: true
  delegate_to: localhost
  register: result

- ansible.builtin.debug:
    msg: "{{ result.network_sets }}"
'''

RETURN = '''
network_sets:
    description: Has all the OneView information about the Network Sets.
    returned: Always, but can be empty.
    type: dict
'''

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class NetworkSetInfoModule(OneViewModuleBase):
    argument_spec = dict(
        name=dict(type='str'),
        options=dict(type='list'),
        params=dict(type='dict'),
    )

    def __init__(self):
        super(NetworkSetInfoModule, self).__init__(additional_arg_spec=self.argument_spec)
        self.is_old_facts = self.module._name in ('oneview_network_set_facts', 'community.general.oneview_network_set_facts')
        if self.is_old_facts:
            self.module.deprecate("The 'oneview_network_set_facts' module has been renamed to 'oneview_network_set_info', "
                                  "and the renamed one no longer returns ansible_facts",
                                  version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    def execute_module(self):

        name = self.module.params.get('name')

        if 'withoutEthernet' in self.options:
            filter_by_name = ("\"'name'='%s'\"" % name) if name else ''
            network_sets = self.oneview_client.network_sets.get_all_without_ethernet(filter=filter_by_name)
        elif name:
            network_sets = self.oneview_client.network_sets.get_by('name', name)
        else:
            network_sets = self.oneview_client.network_sets.get_all(**self.facts_params)

        if self.is_old_facts:
            return dict(changed=False,
                        ansible_facts=dict(network_sets=network_sets))
        else:
            return dict(changed=False, network_sets=network_sets)


def main():
    NetworkSetInfoModule().run()


if __name__ == '__main__':
    main()

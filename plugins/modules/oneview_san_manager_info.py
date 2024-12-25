#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: oneview_san_manager_info
short_description: Retrieve information about one or more of the OneView SAN Managers
description:
  - Retrieve information about one or more of the SAN Managers from OneView.
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
  provider_display_name:
    description:
      - Provider Display Name.
    type: str
  params:
    description:
      - List of params to delimit, filter and sort the list of resources.
      - 'Params allowed:'
      - 'V(start): The first item to return, using 0-based indexing.'
      - 'V(count): The number of resources to return.'
      - 'V(query): A general query string to narrow the list of resources returned.'
      - 'V(sort): The sort order of the returned data set.'
    type: dict
extends_documentation_fragment:
  - community.general.oneview
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: Gather information about all SAN Managers
  community.general.oneview_san_manager_info:
    config: /etc/oneview/oneview_config.json
  delegate_to: localhost
  register: result

- name: Print fetched information about SAN Managers
  ansible.builtin.debug:
    msg: "{{ result.san_managers }}"

- name: Gather paginated, filtered and sorted information about SAN Managers
  community.general.oneview_san_manager_info:
    config: /etc/oneview/oneview_config.json
    params:
      start: 0
      count: 3
      sort: name:ascending
      query: isInternal eq false
  delegate_to: localhost
  register: result

- name: Print fetched information about paginated, filtered and sorted list of SAN Managers
  ansible.builtin.debug:
    msg: "{{ result.san_managers }}"

- name: Gather information about a SAN Manager by provider display name
  community.general.oneview_san_manager_info:
    config: /etc/oneview/oneview_config.json
    provider_display_name: Brocade Network Advisor
  delegate_to: localhost
  register: result

- name: Print fetched information about SAN Manager found by provider display name
  ansible.builtin.debug:
    msg: "{{ result.san_managers }}"
"""

RETURN = r"""
san_managers:
  description: Has all the OneView information about the SAN Managers.
  returned: Always, but can be null.
  type: dict
"""

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class SanManagerInfoModule(OneViewModuleBase):
    argument_spec = dict(
        provider_display_name=dict(type='str'),
        params=dict(type='dict')
    )

    def __init__(self):
        super(SanManagerInfoModule, self).__init__(
            additional_arg_spec=self.argument_spec,
            supports_check_mode=True,
        )
        self.resource_client = self.oneview_client.san_managers

    def execute_module(self):
        if self.module.params.get('provider_display_name'):
            provider_display_name = self.module.params['provider_display_name']
            san_manager = self.oneview_client.san_managers.get_by_provider_display_name(provider_display_name)
            if san_manager:
                resources = [san_manager]
            else:
                resources = []
        else:
            resources = self.oneview_client.san_managers.get_all(**self.facts_params)

        return dict(changed=False, san_managers=resources)


def main():
    SanManagerInfoModule().run()


if __name__ == '__main__':
    main()

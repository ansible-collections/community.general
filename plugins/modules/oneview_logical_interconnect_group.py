#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: oneview_logical_interconnect_group
short_description: Manage OneView Logical Interconnect Group resources
description:
  - Provides an interface to manage Logical Interconnect Group resources. Can create, update, or delete.
requirements:
  - hpOneView >= 4.0.0
author:
  - Felipe Bulsoni (@fgbulsoni)
  - Thiago Miotto (@tmiotto)
  - Adriane Cardozo (@adriane-cardozo)
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicates the desired state for the Logical Interconnect Group resource.
      - V(absent) will remove the resource from OneView, if it exists.
      - V(present) will ensure data properties are compliant with OneView.
    type: str
    choices: [absent, present]
    default: present
  data:
    description:
      - List with the Logical Interconnect Group properties.
    type: dict
    required: true
extends_documentation_fragment:
  - community.general.oneview
  - community.general.oneview.validateetag
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Ensure that the Logical Interconnect Group is present
  community.general.oneview_logical_interconnect_group:
    config: /etc/oneview/oneview_config.json
    state: present
    data:
      name: Test Logical Interconnect Group
      uplinkSets: []
      enclosureType: C7000
      interconnectMapTemplate:
        interconnectMapEntryTemplates:
          - logicalDownlinkUri:
            logicalLocation:
              locationEntries:
                - relativeValue: 1
                  type: Bay
                - relativeValue: 1
                  type: Enclosure
            permittedInterconnectTypeName: HP VC Flex-10/10D Module
            # Alternatively you can inform permittedInterconnectTypeUri
  delegate_to: localhost

- name: Ensure that the Logical Interconnect Group has the specified scopes
  community.general.oneview_logical_interconnect_group:
    config: /etc/oneview/oneview_config.json
    state: present
    data:
      name: Test Logical Interconnect Group
      scopeUris:
        - /rest/scopes/00SC123456
        - /rest/scopes/01SC123456
  delegate_to: localhost

- name: Ensure that the Logical Interconnect Group is present with name 'Test'
  community.general.oneview_logical_interconnect_group:
    config: /etc/oneview/oneview_config.json
    state: present
    data:
      name: New Logical Interconnect Group
      newName: Test
  delegate_to: localhost

- name: Ensure that the Logical Interconnect Group is absent
  community.general.oneview_logical_interconnect_group:
    config: /etc/oneview/oneview_config.json
    state: absent
    data:
      name: New Logical Interconnect Group
  delegate_to: localhost
"""

RETURN = r"""
logical_interconnect_group:
  description: Has the facts about the OneView Logical Interconnect Group.
  returned: On O(state=present). Can be null.
  type: dict
"""

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase, OneViewModuleResourceNotFound


class LogicalInterconnectGroupModule(OneViewModuleBase):
    MSG_CREATED = 'Logical Interconnect Group created successfully.'
    MSG_UPDATED = 'Logical Interconnect Group updated successfully.'
    MSG_DELETED = 'Logical Interconnect Group deleted successfully.'
    MSG_ALREADY_PRESENT = 'Logical Interconnect Group is already present.'
    MSG_ALREADY_ABSENT = 'Logical Interconnect Group is already absent.'
    MSG_INTERCONNECT_TYPE_NOT_FOUND = 'Interconnect Type was not found.'

    RESOURCE_FACT_NAME = 'logical_interconnect_group'

    def __init__(self):
        argument_spec = dict(
            state=dict(default='present', choices=['present', 'absent']),
            data=dict(required=True, type='dict')
        )

        super(LogicalInterconnectGroupModule, self).__init__(additional_arg_spec=argument_spec,
                                                             validate_etag_support=True)
        self.resource_client = self.oneview_client.logical_interconnect_groups

    def execute_module(self):
        resource = self.get_by_name(self.data['name'])

        if self.state == 'present':
            return self.__present(resource)
        elif self.state == 'absent':
            return self.resource_absent(resource)

    def __present(self, resource):
        scope_uris = self.data.pop('scopeUris', None)

        self.__replace_name_by_uris(self.data)
        result = self.resource_present(resource, self.RESOURCE_FACT_NAME)

        if scope_uris is not None:
            result = self.resource_scopes_set(result, 'logical_interconnect_group', scope_uris)

        return result

    def __replace_name_by_uris(self, data):
        map_template = data.get('interconnectMapTemplate')

        if map_template:
            map_entry_templates = map_template.get('interconnectMapEntryTemplates')
            if map_entry_templates:
                for value in map_entry_templates:
                    permitted_interconnect_type_name = value.pop('permittedInterconnectTypeName', None)
                    if permitted_interconnect_type_name:
                        value['permittedInterconnectTypeUri'] = self.__get_interconnect_type_by_name(
                            permitted_interconnect_type_name).get('uri')

    def __get_interconnect_type_by_name(self, name):
        i_type = self.oneview_client.interconnect_types.get_by('name', name)
        if i_type:
            return i_type[0]
        else:
            raise OneViewModuleResourceNotFound(self.MSG_INTERCONNECT_TYPE_NOT_FOUND)


def main():
    LogicalInterconnectGroupModule().run()


if __name__ == '__main__':
    main()

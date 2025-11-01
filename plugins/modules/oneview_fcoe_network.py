#!/usr/bin/python
# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: oneview_fcoe_network
short_description: Manage OneView FCoE Network resources
description:
  - Provides an interface to manage FCoE Network resources. Can create, update, or delete.
requirements:
  - "Python >= 2.7.9"
  - "hpOneView >= 4.0.0"
author: "Felipe Bulsoni (@fgbulsoni)"
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicates the desired state for the FCoE Network resource.
      - V(present) ensures data properties are compliant with OneView.
      - V(absent) removes the resource from OneView, if it exists.
    type: str
    default: present
    choices: ['present', 'absent']
  data:
    description:
      - List with FCoE Network properties.
    type: dict
    required: true

extends_documentation_fragment:
  - community.general.oneview
  - community.general.oneview.validateetag
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Ensure that FCoE Network is present using the default configuration
  community.general.oneview_fcoe_network:
    config: '/etc/oneview/oneview_config.json'
    state: present
    data:
      name: Test FCoE Network
      vlanId: 201
  delegate_to: localhost

- name: Update the FCOE network scopes
  community.general.oneview_fcoe_network:
    config: '/etc/oneview/oneview_config.json'
    state: present
    data:
      name: New FCoE Network
      scopeUris:
        - '/rest/scopes/00SC123456'
        - '/rest/scopes/01SC123456'
  delegate_to: localhost

- name: Ensure that FCoE Network is absent
  community.general.oneview_fcoe_network:
    config: '/etc/oneview/oneview_config.json'
    state: absent
    data:
      name: New FCoE Network
  delegate_to: localhost
"""

RETURN = r"""
fcoe_network:
  description: Has the facts about the OneView FCoE Networks.
  returned: On O(state=present). Can be null.
  type: dict
"""

from ansible_collections.community.general.plugins.module_utils.oneview import OneViewModuleBase


class FcoeNetworkModule(OneViewModuleBase):
    MSG_CREATED = "FCoE Network created successfully."
    MSG_UPDATED = "FCoE Network updated successfully."
    MSG_DELETED = "FCoE Network deleted successfully."
    MSG_ALREADY_PRESENT = "FCoE Network is already present."
    MSG_ALREADY_ABSENT = "FCoE Network is already absent."
    RESOURCE_FACT_NAME = "fcoe_network"

    def __init__(self):
        additional_arg_spec = dict(
            data=dict(required=True, type="dict"), state=dict(default="present", choices=["present", "absent"])
        )

        super().__init__(additional_arg_spec=additional_arg_spec, validate_etag_support=True)

        self.resource_client = self.oneview_client.fcoe_networks

    def execute_module(self):
        resource = self.get_by_name(self.data.get("name"))

        if self.state == "present":
            return self.__present(resource)
        elif self.state == "absent":
            return self.resource_absent(resource)

    def __present(self, resource):
        scope_uris = self.data.pop("scopeUris", None)
        result = self.resource_present(resource, self.RESOURCE_FACT_NAME)
        if scope_uris is not None:
            result = self.resource_scopes_set(result, "fcoe_network", scope_uris)
        return result


def main():
    FcoeNetworkModule().run()


if __name__ == "__main__":
    main()

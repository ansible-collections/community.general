#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_network_view
author: "Peter Sprygada (@privateip)"
short_description: Configure Infoblox NIOS network views
deprecated:
    why: Please install the infoblox.nios_modules collection and use the corresponding module from it.
    alternative: infoblox.nios_modules.nios_network_view
    removed_in: 5.0.0
description:
  - Adds and/or removes instances of network view objects from
    Infoblox NIOS servers.  This module manages NIOS C(networkview) objects
    using the Infoblox WAPI interface over REST.
  - Updates instances of network view object from Infoblox NIOS servers.
requirements:
  - infoblox-client
extends_documentation_fragment:
- community.general.nios

options:
  name:
    description:
      - Specifies the fully qualified hostname to add or remove from
        the system. User can also update the hostname as it is possible
        to pass a dict containing I(new_name), I(old_name). See examples.
    required: true
    aliases:
      - network_view
    type: str
  extattrs:
    description:
      - Allows for the configuration of Extensible Attributes on the
        instance of the object.  This argument accepts a set of key / value
        pairs for configuration.
    type: dict
  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
    type: str
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    default: present
    choices:
      - present
      - absent
    type: str
'''

EXAMPLES = '''
- name: Configure a new network view
  community.general.nios_network_view:
    name: ansible
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Update the comment for network view
  community.general.nios_network_view:
    name: ansible
    comment: this is an example comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Remove the network view
  community.general.nios_network_view:
    name: ansible
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Update a existing network view
  community.general.nios_network_view:
    name: {new_name: ansible-new, old_name: ansible}
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import NIOS_NETWORK_VIEW
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''
    ib_spec = dict(
        name=dict(required=True, aliases=['network_view'], ib_req=True),
        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_NETWORK_VIEW, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

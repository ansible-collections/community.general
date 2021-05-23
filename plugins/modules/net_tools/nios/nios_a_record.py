#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_a_record
author: "Blair Rampling (@brampling)"
short_description: Configure Infoblox NIOS A records
deprecated:
    why: Please install the infoblox.nios_modules collection and use the corresponding module from it.
    alternative: infoblox.nios_modules.nios_a_record
    removed_in: 5.0.0
description:
  - Adds and/or removes instances of A record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:a) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment:
- community.general.nios

options:
  name:
    description:
      - Specifies the fully qualified hostname to add or remove from
        the system
    required: true
    type: str
  view:
    description:
      - Sets the DNS view to associate this A record with.  The DNS
        view must already be configured on the system
    default: default
    aliases:
      - dns_view
    type: str
  ipv4addr:
    description:
      - Configures the IPv4 address for this A record. Users can dynamically
        allocate ipv4 address to A record by passing dictionary containing,
        I(nios_next_ip) and I(CIDR network range). See example
    aliases:
      - ipv4
    type: str
  ttl:
    description:
      - Configures the TTL to be associated with this A record
    type: int
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
- name: Configure an A record
  community.general.nios_a_record:
    name: a.ansible.com
    ipv4: 192.168.10.1
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add a comment to an existing A record
  community.general.nios_a_record:
    name: a.ansible.com
    ipv4: 192.168.10.1
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove an A record from the system
  community.general.nios_a_record:
    name: a.ansible.com
    ipv4: 192.168.10.1
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update an A record name
  community.general.nios_a_record:
    name: {new_name: a_new.ansible.com, old_name: a.ansible.com}
    ipv4: 192.168.10.1
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Dynamically add a record to next available ip
  community.general.nios_a_record:
    name: a.ansible.com
    ipv4: {nios_next_ip: 192.168.10.0/24}
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
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import NIOS_A_RECORD
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),

        ipv4addr=dict(aliases=['ipv4'], ib_req=True),

        ttl=dict(type='int'),

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
    result = wapi.run(NIOS_A_RECORD, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

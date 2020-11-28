#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_aaaa_record
author: "Blair Rampling (@brampling)"
short_description: Configure Infoblox NIOS AAAA records
description:
  - Adds and/or removes instances of AAAA record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:aaaa) objects
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
  view:
    description:
      - Sets the DNS view to associate this AAAA record with.  The DNS
        view must already be configured on the system
    default: default
    aliases:
      - dns_view
  ipv6addr:
    description:
      - Configures the IPv6 address for this AAAA record.
    aliases:
      - ipv6
  ttl:
    description:
      - Configures the TTL to be associated with this AAAA record
  extattrs:
    description:
      - Allows for the configuration of Extensible Attributes on the
        instance of the object.  This argument accepts a set of key / value
        pairs for configuration.
  comment:
    description:
      - Configures a text string comment to be associated with the instance
        of this object.  The provided text string will be configured on the
        object instance.
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
'''

EXAMPLES = '''
- name: Configure an AAAA record
  community.general.nios_aaaa_record:
    name: aaaa.ansible.com
    ipv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add a comment to an existing AAAA record
  community.general.nios_aaaa_record:
    name: aaaa.ansible.com
    ipv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove an AAAA record from the system
  community.general.nios_aaaa_record:
    name: aaaa.ansible.com
    ipv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Update an AAAA record name
  community.general.nios_aaaa_record:
    name: {new_name: aaaa_new.ansible.com, old_name: aaaa.ansible.com}
    ipv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import NIOS_AAAA_RECORD


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),

        ipv6addr=dict(aliases=['ipv6'], ib_req=True),

        ttl=dict(type='int'),

        extattrs=dict(type='dict'),
        comment=dict(),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(ib_spec)
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_AAAA_RECORD, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

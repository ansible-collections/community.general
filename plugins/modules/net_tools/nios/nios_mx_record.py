#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_mx_record
author: "Blair Rampling (@brampling)"
short_description: Configure Infoblox NIOS MX records
description:
  - Adds and/or removes instances of MX record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:mx) objects
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
      - Sets the DNS view to associate this a record with.  The DNS
        view must already be configured on the system
    default: default
    aliases:
      - dns_view
    type: str
  mail_exchanger:
    description:
      - Configures the mail exchanger FQDN for this MX record.
    aliases:
      - mx
    type: str
  preference:
    description:
      - Configures the preference (0-65535) for this MX record.
    type: int
  ttl:
    description:
      - Configures the TTL to be associated with this host record
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
- name: Configure an MX record
  community.general.nios_mx_record:
    name: ansible.com
    mx: mailhost.ansible.com
    preference: 0
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Add a comment to an existing MX record
  community.general.nios_mx_record:
    name: ansible.com
    mx: mailhost.ansible.com
    preference: 0
    comment: this is a test comment
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local

- name: Remove an MX record from the system
  community.general.nios_mx_record:
    name: ansible.com
    mx: mailhost.ansible.com
    preference: 0
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import NIOS_MX_RECORD
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),

        mail_exchanger=dict(aliases=['mx'], ib_req=True),
        preference=dict(type='int', ib_req=True),

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
    result = wapi.run(NIOS_MX_RECORD, ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_txt_record
author: "Corey Wanless (@coreywan)"
short_description: Configure Infoblox NIOS txt records
deprecated:
    why: Please install the infoblox.nios_modules collection and use the corresponding module from it.
    alternative: infoblox.nios_modules.nios_txt_record
    removed_in: 5.0.0
description:
  - Adds and/or removes instances of txt record objects from
    Infoblox NIOS servers.  This module manages NIOS C(record:txt) objects
    using the Infoblox WAPI interface over REST.
requirements:
  - infoblox_client
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
      - Sets the DNS view to associate this tst record with.  The DNS
        view must already be configured on the system
    default: default
    aliases:
      - dns_view
    type: str
  text:
    description:
      - Text associated with the record. It can contain up to 255 bytes
        per substring, up to a total of 512 bytes. To enter leading,
        trailing, or embedded spaces in the text, add quotes around the
        text to preserve the spaces.
    type: str
  ttl:
    description:
      - Configures the TTL to be associated with this tst record
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
    - name: Ensure a text Record Exists
      community.general.nios_txt_record:
        name: fqdn.txt.record.com
        text: mytext
        state: present
        view: External
        provider:
          host: "{{ inventory_hostname_short }}"
          username: admin
          password: admin

    - name: Ensure a text Record does not exist
      community.general.nios_txt_record:
        name: fqdn.txt.record.com
        text: mytext
        state: absent
        view: External
        provider:
          host: "{{ inventory_hostname_short }}"
          username: admin
          password: admin
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''

    ib_spec = dict(
        name=dict(required=True, ib_req=True),
        view=dict(default='default', aliases=['dns_view'], ib_req=True),
        text=dict(ib_req=True),
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
    result = wapi.run('record:txt', ib_spec)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

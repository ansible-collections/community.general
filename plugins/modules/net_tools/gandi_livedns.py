#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Gregory Thiemonge <gregory.thiemonge@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gandi_livedns
author:
- Gregory Thiemonge (@gthiemonge)
version_added: "2.3.0"
short_description: Manage Gandi LiveDNS records
description:
- "Manages DNS records by the Gandi LiveDNS API, see the docs: U(https://doc.livedns.gandi.net/)."
options:
  api_key:
    description:
    - Account API token.
    type: str
    required: true
  record:
    description:
    - Record to add.
    type: str
    required: true
  state:
    description:
    - Whether the record(s) should exist or not.
    type: str
    choices: [ absent, present ]
    default: present
  ttl:
    description:
    - The TTL to give the new record.
    - Required when I(state=present).
    type: int
  type:
    description:
      - The type of DNS record to create.
    type: str
    required: true
  values:
    description:
    - The record values.
    - Required when I(state=present).
    type: list
    elements: str
  domain:
    description:
    - The name of the Domain to work with (for example, "example.com").
    required: true
    type: str
notes:
- Supports C(check_mode).
'''

EXAMPLES = r'''
- name: Create a test A record to point to 127.0.0.1 in the my.com domain
  community.general.gandi_livedns:
    domain: my.com
    record: test
    type: A
    values:
    - 127.0.0.1
    ttl: 7200
    api_key: dummyapitoken
  register: record

- name: Create a mail CNAME record to www.my.com domain
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    values:
    - www
    ttl: 7200
    api_key: dummyapitoken
    state: present

- name: Change its TTL
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    values:
    - www
    ttl: 10800
    api_key: dummyapitoken
    state: present

- name: Delete the record
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    api_key: dummyapitoken
    state: absent
'''

RETURN = r'''
record:
    description: A dictionary containing the record data.
    returned: success, except on record deletion
    type: dict
    contains:
        values:
            description: The record content (details depend on record type).
            returned: success
            type: list
            elements: str
            sample:
            - 192.0.2.91
            - 192.0.2.92
        record:
            description: The record name.
            returned: success
            type: str
            sample: www
        ttl:
            description: The time-to-live for the record.
            returned: success
            type: int
            sample: 300
        type:
            description: The record type.
            returned: success
            type: str
            sample: A
        domain:
            description: The domain associated with the record.
            returned: success
            type: str
            sample: my.com
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.gandi_livedns_api import GandiLiveDNSAPI


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(type='str', required=True, no_log=True),
            record=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            ttl=dict(type='int'),
            type=dict(type='str', required=True),
            values=dict(type='list', elements='str'),
            domain=dict(type='str', required=True),
        ),
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['values', 'ttl']),
        ],
    )

    gandi_api = GandiLiveDNSAPI(module)

    if module.params['state'] == 'present':
        ret, changed = gandi_api.ensure_dns_record(module.params['record'],
                                                   module.params['type'],
                                                   module.params['ttl'],
                                                   module.params['values'],
                                                   module.params['domain'])
    else:
        ret, changed = gandi_api.delete_dns_record(module.params['record'],
                                                   module.params['type'],
                                                   module.params['values'],
                                                   module.params['domain'])

    result = dict(
        changed=changed,
    )
    if ret:
        result['record'] = gandi_api.build_result(ret,
                                                  module.params['domain'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Gregory Thiemonge <gregory.thiemonge@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gandi_livedns
author:
  - Gregory Thiemonge (@gthiemonge)
version_added: "2.3.0"
short_description: Manage Gandi LiveDNS records
description:
  - 'Manages DNS records by the Gandi LiveDNS API, see the docs: U(https://doc.livedns.gandi.net/).'
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  personal_access_token:
    description:
      - Scoped API token.
      - One of O(personal_access_token) and O(api_key) must be specified.
    type: str
    version_added: 9.0.0
  api_key:
    description:
      - Account API token.
      - Note that these type of keys are deprecated and might stop working at some point. Use personal access tokens instead.
      - One of O(personal_access_token) and O(api_key) must be specified.
    type: str
  record:
    description:
      - Record to add.
    type: str
    required: true
  state:
    description:
      - Whether the record(s) should exist or not.
    type: str
    choices: [absent, present]
    default: present
  ttl:
    description:
      - The TTL to give the new record.
      - Required when O(state=present).
    type: int
  type:
    description:
      - The type of DNS record to create.
    type: str
    required: true
  values:
    description:
      - The record values.
      - Required when O(state=present).
    type: list
    elements: str
  domain:
    description:
      - The name of the Domain to work with (for example, V(example.com)).
    required: true
    type: str
"""

EXAMPLES = r"""
- name: Create a test A record to point to 127.0.0.1 in the my.com domain
  community.general.gandi_livedns:
    domain: my.com
    record: test
    type: A
    values:
      - 127.0.0.1
    ttl: 7200
    personal_access_token: dummytoken
  register: record

- name: Create a mail CNAME record to www.my.com domain
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    values:
      - www
    ttl: 7200
    personal_access_token: dummytoken
    state: present

- name: Change its TTL
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    values:
      - www
    ttl: 10800
    personal_access_token: dummytoken
    state: present

- name: Delete the record
  community.general.gandi_livedns:
    domain: my.com
    type: CNAME
    record: mail
    personal_access_token: dummytoken
    state: absent

- name: Use a (deprecated) API Key
  community.general.gandi_livedns:
    domain: my.com
    record: test
    type: A
    values:
      - 127.0.0.1
    ttl: 7200
    api_key: dummyapikey
"""

RETURN = r"""
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
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.gandi_livedns_api import GandiLiveDNSAPI


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(type='str', no_log=True),
            personal_access_token=dict(type='str', no_log=True),
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
        mutually_exclusive=[
            ('api_key', 'personal_access_token'),
        ],
        required_one_of=[
            ('api_key', 'personal_access_token'),
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

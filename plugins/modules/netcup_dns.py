#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Nicolai Buchwitz <nb@tipi-net.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: netcup_dns
notes: []
short_description: Manage Netcup DNS records
description:
  - "Manages DNS records via the Netcup API, see the docs U(https://ccp.netcup.net/run/webservice/servers/endpoint.php)."
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  api_key:
    description:
      - "API key for authentication, must be obtained via the netcup CCP (U(https://ccp.netcup.net))."
    required: true
    type: str
  api_password:
    description:
      - "API password for authentication, must be obtained via the netcup CCP (U(https://ccp.netcup.net))."
    required: true
    type: str
  customer_id:
    description:
      - Netcup customer id.
    required: true
    type: int
  domain:
    description:
      - Domainname the records should be added / removed.
    required: true
    type: str
  record:
    description:
      - Record to add or delete, supports wildcard (*). Default is C(@) (e.g. the zone name).
    default: "@"
    aliases: [ name ]
    type: str
  type:
    description:
      - Record type.
    choices: ['A', 'AAAA', 'MX', 'CNAME', 'CAA', 'SRV', 'TXT', 'TLSA', 'NS', 'DS']
    required: true
    type: str
  value:
    description:
      - Record value.
    required: true
    type: str
  solo:
    type: bool
    default: false
    description:
      - Whether the record should be the only one for that record type and record name. Only use with I(state=present).
      - This will delete all other records with the same record name and type.
  priority:
    description:
      - Record priority. Required for I(type=MX).
    required: false
    type: int
  state:
    description:
      - Whether the record should exist or not.
    required: false
    default: present
    choices: [ 'present', 'absent' ]
    type: str
  timeout:
    description:
      - HTTP(S) connection timeout in seconds.
    default: 5
    type: int
    version_added: 5.7.0
requirements:
  - "nc-dnsapi >= 0.1.3"
author: "Nicolai Buchwitz (@nbuchwitz)"

'''

EXAMPLES = '''
- name: Create a record of type A
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    domain: "example.com"
    name: "mail"
    type: "A"
    value: "127.0.0.1"

- name: Delete that record
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    domain: "example.com"
    name: "mail"
    type: "A"
    value: "127.0.0.1"
    state: absent

- name: Create a wildcard record
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    domain: "example.com"
    name: "*"
    type: "A"
    value: "127.0.1.1"

- name: Set the MX record for example.com
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    domain: "example.com"
    type: "MX"
    value: "mail.example.com"

- name: Set a record and ensure that this is the only one
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    name: "demo"
    domain: "example.com"
    type: "AAAA"
    value: "::1"
    solo: true

- name: Increase the connection timeout to avoid problems with an unstable connection
  community.general.netcup_dns:
    api_key: "..."
    api_password: "..."
    customer_id: "..."
    domain: "example.com"
    name: "mail"
    type: "A"
    value: "127.0.0.1"
    timeout: 30

'''

RETURN = '''
records:
    description: list containing all records
    returned: success
    type: complex
    contains:
        name:
            description: the record name
            returned: success
            type: str
            sample: fancy-hostname
        type:
            description: the record type
            returned: succcess
            type: str
            sample: A
        value:
            description: the record destination
            returned: success
            type: str
            sample: 127.0.0.1
        priority:
            description: the record priority (only relevant if type=MX)
            returned: success
            type: int
            sample: 0
        id:
            description: internal id of the record
            returned: success
            type: int
            sample: 12345
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

NCDNSAPI_IMP_ERR = None
try:
    import nc_dnsapi
    from nc_dnsapi import DNSRecord

    HAS_NCDNSAPI = True
except ImportError:
    NCDNSAPI_IMP_ERR = traceback.format_exc()
    HAS_NCDNSAPI = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True, no_log=True),
            api_password=dict(required=True, no_log=True),
            customer_id=dict(required=True, type='int'),

            domain=dict(required=True),
            record=dict(required=False, default='@', aliases=['name']),
            type=dict(required=True, choices=['A', 'AAAA', 'MX', 'CNAME', 'CAA', 'SRV', 'TXT', 'TLSA', 'NS', 'DS']),
            value=dict(required=True),
            priority=dict(required=False, type='int'),
            solo=dict(required=False, type='bool', default=False),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            timeout=dict(required=False, type='int', default=5),

        ),
        supports_check_mode=True
    )

    if not HAS_NCDNSAPI:
        module.fail_json(msg=missing_required_lib('nc-dnsapi'), exception=NCDNSAPI_IMP_ERR)

    api_key = module.params.get('api_key')
    api_password = module.params.get('api_password')
    customer_id = module.params.get('customer_id')
    domain = module.params.get('domain')
    record_type = module.params.get('type')
    record = module.params.get('record')
    value = module.params.get('value')
    priority = module.params.get('priority')
    solo = module.params.get('solo')
    state = module.params.get('state')
    timeout = module.params.get('timeout')

    if record_type == 'MX' and not priority:
        module.fail_json(msg="record type MX required the 'priority' argument")

    has_changed = False
    all_records = []
    try:
        with nc_dnsapi.Client(customer_id, api_key, api_password, timeout) as api:
            all_records = api.dns_records(domain)
            record = DNSRecord(record, record_type, value, priority=priority)

            # try to get existing record
            record_exists = False
            for r in all_records:
                if r == record:
                    record_exists = True
                    record = r

                    break

            if state == 'present':
                if solo:
                    obsolete_records = [r for r in all_records if
                                        r.hostname == record.hostname
                                        and r.type == record.type
                                        and not r.destination == record.destination]

                    if obsolete_records:
                        if not module.check_mode:
                            all_records = api.delete_dns_records(domain, obsolete_records)

                        has_changed = True

                if not record_exists:
                    if not module.check_mode:
                        all_records = api.add_dns_record(domain, record)

                    has_changed = True
            elif state == 'absent' and record_exists:
                if not module.check_mode:
                    all_records = api.delete_dns_record(domain, record)

                has_changed = True

    except Exception as ex:
        module.fail_json(msg=str(ex))

    module.exit_json(changed=has_changed, result={"records": [record_data(r) for r in all_records]})


def record_data(r):
    return {"name": r.hostname, "type": r.type, "value": r.destination, "priority": r.priority, "id": r.id}


if __name__ == '__main__':
    main()

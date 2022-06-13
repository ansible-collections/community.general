#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright: Edward Hilgendorf, <edward@hilgendorf.me>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: dnsimple_info

short_description: Pull basic info from DNSimple API

version_added: "4.2.0"

description: Retrieve existing records and domains from DNSimple API.

options:
    name:
        description:
          - The domain name to retrieve info from.
          - Will return all associated records for this domain if specified.
          - If not specified, will return all domains associated with the account ID.
        type: str

    account_id:
        description: The account ID to query.
        required: true
        type: str

    api_key:
        description: The API key to use.
        required: true
        type: str

    record:
        description:
          - The record to find.
          - If specified, only this record will be returned instead of all records.
        required: false
        type: str

    sandbox:
        description: Whether or not to use sandbox environment.
        required: false
        default: false
        type: bool

author:
    -  Edward Hilgendorf (@edhilgendorf)
'''

EXAMPLES = r'''
- name: Get all domains from an account
  community.general.dnsimple_info:
    account_id: "1234"
    api_key: "1234"

- name: Get all records from a domain
  community.general.dnsimple_info:
    name: "example.com"
    account_id: "1234"
    api_key: "1234"

- name: Get all info from a matching record
  community.general.dnsimple_info:
    name: "example.com"
    record: "subdomain"
    account_id: "1234"
    api_key: "1234"
'''

RETURN = r'''
dnsimple_domain_info:
    description: Returns a list of dictionaries of all domains associated with the supplied account ID.
    type: list
    elements: dict
    returned: success when I(name) is not specified
    sample:
    - account_id: 1234
      created_at: '2021-10-16T21:25:42Z'
      id: 123456
      last_transferred_at:
      name: example.com
      reverse: false
      secondary: false
      updated_at: '2021-11-10T20:22:50Z'
    contains:
      account_id:
        description: The account ID.
        type: int
      created_at:
        description: When the domain entry was created.
        type: str
      id:
        description: ID of the entry.
        type: int
      last_transferred_at:
        description: Date the domain was transferred, or empty if not.
        type: str
      name:
        description: Name of the record.
        type: str
      reverse:
        description: Whether or not it is a reverse zone record.
        type: bool
      updated_at:
        description: When the domain entry was updated.
        type: str

dnsimple_records_info:
    description: Returns a list of dictionaries with all records for the domain supplied.
    type: list
    elements: dict
    returned: success when I(name) is specified, but I(record) is not
    sample:
    - content: ns1.dnsimple.com admin.dnsimple.com
      created_at: '2021-10-16T19:07:34Z'
      id: 12345
      name: 'catheadbiscuit'
      parent_id: null
      priority: null
      regions:
        - global
      system_record: true
      ttl: 3600
      type: SOA
      updated_at: '2021-11-15T23:55:51Z'
      zone_id: example.com
    contains:
      content:
        description:  Content of the returned record.
        type: str
      created_at:
        description: When the domain entry was created.
        type: str
      id:
        description: ID of the entry.
        type: int
      name:
        description: Name of the record.
        type: str
      parent_id:
        description: Parent record or null.
        type: int
      priority:
        description: Priority setting of the record.
        type: str
      regions:
        description: List of regions where the record is available.
        type: list
      system_record:
        description: Whether or not it is a system record.
        type: bool
      ttl:
        description: Record TTL.
        type: int
      type:
        description: Record type.
        type: str
      updated_at:
        description: When the domain entry was updated.
        type: str
      zone_id:
        description: ID of the zone that the record is associated with.
        type: str
dnsimple_record_info:
    description: Returns a list of dictionaries that match the record supplied.
    returned: success when I(name) and I(record) are specified
    type: list
    elements: dict
    sample:
    - content: 1.2.3.4
      created_at: '2021-11-15T23:55:51Z'
      id: 123456
      name: catheadbiscuit
      parent_id: null
      priority: null
      regions:
        - global
      system_record: false
      ttl: 3600
      type: A
      updated_at: '2021-11-15T23:55:51Z'
      zone_id: example.com
    contains:
      content:
        description:  Content of the returned record.
        type: str
      created_at:
        description: When the domain entry was created.
        type: str
      id:
        description: ID of the entry.
        type: int
      name:
        description: Name of the record.
        type: str
      parent_id:
        description: Parent record or null.
        type: int
      priority:
        description: Priority setting of the record.
        type: str
      regions:
        description: List of regions where the record is available.
        type: list
      system_record:
        description: Whether or not it is a system record.
        type: bool
      ttl:
        description: Record TTL.
        type: int
      type:
        description: Record type.
        type: str
      updated_at:
        description: When the domain entry was updated.
        type: str
      zone_id:
        description: ID of the zone that the record is associated with.
        type: str
'''

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

try:
    from requests import Request, Session
    HAS_REQUESTS_LIBRARY = True
except ImportError:
    HAS_REQUESTS_LIBRARY = False
    REQUESTS_LIBRARY_IMPORT_ERROR = traceback.format_exc()


def build_url(account, key, is_sandbox):
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer {0}'.format(key)}
    sandbox = '.sandbox' if is_sandbox else ''
    url = 'https://api{sandbox}.dnsimple.com/v2/{account}'.format(sandbox=sandbox, account=account)
    req = Request(url=url, headers=headers)
    prepped_request = req.prepare()
    return prepped_request


def iterate_data(module, request_object):
    base_url = request_object.url
    response = Session().send(request_object)
    if 'pagination' not in response.json():
        module.fail_json('API Call failed, check ID, key and sandbox values')

    data = response.json()['data']
    total_pages = int(response.json()['pagination']['total_pages'])
    page = 1
    while page < total_pages:
        page = page + 1
        request_object.url = '{url}&page={page}'.format(url=base_url, page=page)
        new_results = Session().send(request_object)
        data = data + new_results.json()['data']

    return data


def record_info(dnsimple_mod, req_obj):
    req_obj.url, req_obj.method = '{url}/zones/{name}/records/?name={record}'.format(
        url=req_obj.url,
        name=dnsimple_mod.params['name'],
        record=dnsimple_mod.params['record']), 'GET'
    return iterate_data(dnsimple_mod, req_obj)


def domain_info(dnsimple_mod, req_obj):
    req_obj.url, req_obj.method = '{url}/zones/{name}/records?per_page=100'.format(url=req_obj.url, name=dnsimple_mod.params['name']), 'GET'
    return iterate_data(dnsimple_mod, req_obj)


def account_info(dnsimple_mod, req_obj):
    req_obj.url, req_obj.method = '{url}/zones/?per_page=100'.format(url=req_obj.url), 'GET'
    return iterate_data(dnsimple_mod, req_obj)


def main():
    result = {
        'changed': False
    }

    module = AnsibleModule(
        argument_spec={
            'account_id': {'required': True, 'type': 'str'},
            'api_key': {'required': True, 'type': 'str', 'no_log': True},
            'name': {'type': 'str'},
            'record': {'type': 'str'},
            'sandbox': {'type': 'bool', 'default': False}
        },
        supports_check_mode=True,
        required_by={
            'record': 'name',
        }
        required_one_of=[
            ('api_key', 'account_id'),
        ],
    )

    params = module.params
    req = build_url(params['account_id'], params['api_key'], params['sandbox'])

    if not HAS_REQUESTS_LIBRARY:
        # Needs: from ansible.module_utils.basic import missing_required_lib
        module.exit_json(
            msg=missing_required_lib('requests'),
            exception=REQUESTS_LIBRARY_IMPORT_ERROR)

    if not(params['account_id'] and params['api_key']):
        module.fail_json(msg="Need at least account_id and api_key")

    # If we have a record return info on that record
    if params['record']:
        result['dnsimple_record_info'] = record_info(module, req)
        module.exit_json(**result)

        # If we have the account only and domain, return records for the domain
    elif params['name']:
        result['dnsimple_records_info'] = domain_info(module, req)
        module.exit_json(**result)

        # If we have the account only, return domains
    else:
        result['dnsimple_domain_info'] = account_info(module, req)
        module.exit_json(**result)


if __name__ == '__main__':
    main()

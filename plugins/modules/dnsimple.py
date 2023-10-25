#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: dnsimple
short_description: Interface with dnsimple.com (a DNS hosting service)
description:
   - "Manages domains and records via the DNSimple API, see the docs: U(http://developer.dnsimple.com/)."
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  account_email:
    description:
      - Account email. If omitted, the environment variables E(DNSIMPLE_EMAIL) and E(DNSIMPLE_API_TOKEN) will be looked for.
      - "If those aren't found, a C(.dnsimple) file will be looked for, see: U(https://github.com/mikemaccana/dnsimple-python#getting-started)."
      - "C(.dnsimple) config files are only supported in dnsimple-python<2.0.0"
    type: str
  account_api_token:
    description:
      - Account API token. See O(account_email) for more information.
    type: str
  domain:
    description:
      - Domain to work with. Can be the domain name (e.g. "mydomain.com") or the numeric ID of the domain in DNSimple.
      - If omitted, a list of domains will be returned.
      - If domain is present but the domain doesn't exist, it will be created.
    type: str
  record:
    description:
      - Record to add, if blank a record for the domain will be created, supports the wildcard (*).
    type: str
  record_ids:
    description:
      - List of records to ensure they either exist or do not exist.
    type: list
    elements: str
  type:
    description:
      - The type of DNS record to create.
    choices: [ 'A', 'ALIAS', 'CNAME', 'MX', 'SPF', 'URL', 'TXT', 'NS', 'SRV', 'NAPTR', 'PTR', 'AAAA', 'SSHFP', 'HINFO', 'POOL', 'CAA' ]
    type: str
  ttl:
    description:
      - The TTL to give the new record in seconds.
    default: 3600
    type: int
  value:
    description:
      - Record value.
      - Must be specified when trying to ensure a record exists.
    type: str
  priority:
    description:
      - Record priority.
    type: int
  state:
    description:
      - whether the record should exist or not.
    choices: [ 'present', 'absent' ]
    default: present
    type: str
  solo:
    description:
      - Whether the record should be the only one for that record type and record name.
      - Only use with O(state) is set to V(present) on a record.
    type: 'bool'
    default: false
  sandbox:
    description:
      - Use the DNSimple sandbox environment.
      - Requires a dedicated account in the dnsimple sandbox environment.
      - Check U(https://developer.dnsimple.com/sandbox/) for more information.
    type: 'bool'
    default: false
    version_added: 3.5.0
requirements:
  - "dnsimple >= 2.0.0"
author: "Alex Coomans (@drcapulet)"
'''

EXAMPLES = '''
- name: Authenticate using email and API token and fetch all domains
  community.general.dnsimple:
    account_email: test@example.com
    account_api_token: dummyapitoken
  delegate_to: localhost

- name: Delete a domain
  community.general.dnsimple:
    domain: my.com
    state: absent
  delegate_to: localhost

- name: Create a test.my.com A record to point to 127.0.0.1
  community.general.dnsimple:
    domain: my.com
    record: test
    type: A
    value: 127.0.0.1
  delegate_to: localhost
  register: record

- name: Delete record using record_ids
  community.general.dnsimple:
    domain: my.com
    record_ids: '{{ record["id"] }}'
    state: absent
  delegate_to: localhost

- name: Create a my.com CNAME record to example.com
  community.general.dnsimple:
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    state: present
  delegate_to: localhost

- name: Change TTL value for a record
  community.general.dnsimple:
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    ttl: 600
    state: present
  delegate_to: localhost

- name: Delete the record
  community.general.dnsimple:
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    state: absent
  delegate_to: localhost
'''

RETURN = r"""# """

import traceback
import re

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


class DNSimpleV2():
    """class which uses dnsimple-python >= 2"""

    def __init__(self, account_email, account_api_token, sandbox, module):
        """init"""
        self.module = module
        self.account_email = account_email
        self.account_api_token = account_api_token
        self.sandbox = sandbox
        self.pagination_per_page = 30
        self.dnsimple_client()
        self.dnsimple_account()

    def dnsimple_client(self):
        """creates a dnsimple client object"""
        if self.account_email and self.account_api_token:
            client = Client(sandbox=self.sandbox, email=self.account_email, access_token=self.account_api_token, user_agent="ansible/community.general")
        else:
            msg = "Option account_email or account_api_token not provided. " \
                  "Dnsimple authentication with a .dnsimple config file is not " \
                  "supported with dnsimple-python>=2.0.0"
            raise DNSimpleException(msg)
        client.identity.whoami()
        self.client = client

    def dnsimple_account(self):
        """select a dnsimple account. If a user token is used for authentication,
        this user must only have access to a single account"""
        account = self.client.identity.whoami().data.account
        # user supplied a user token instead of account api token
        if not account:
            accounts = Accounts(self.client).list_accounts().data
            if len(accounts) != 1:
                msg = "The provided dnsimple token is a user token with multiple accounts." \
                    "Use an account token or a user token with access to a single account." \
                    "See https://support.dnsimple.com/articles/api-access-token/"
                raise DNSimpleException(msg)
            account = accounts[0]
        self.account = account

    def get_all_domains(self):
        """returns a list of all domains"""
        domain_list = self._get_paginated_result(self.client.domains.list_domains, account_id=self.account.id)
        return [d.__dict__ for d in domain_list]

    def get_domain(self, domain):
        """returns a single domain by name or id"""
        try:
            dr = self.client.domains.get_domain(self.account.id, domain).data.__dict__
        except DNSimpleException as e:
            exception_string = str(e.message)
            if re.match(r"^Domain .+ not found$", exception_string):
                dr = None
            else:
                raise
        return dr

    def create_domain(self, domain):
        """create a single domain"""
        return self.client.domains.create_domain(self.account.id, domain).data.__dict__

    def delete_domain(self, domain):
        """delete a single domain"""
        self.client.domains.delete_domain(self.account.id, domain)

    def get_records(self, zone, dnsimple_filter=None):
        """return dns resource records which match a specified filter"""
        records_list = self._get_paginated_result(self.client.zones.list_records,
                                                  account_id=self.account.id,
                                                  zone=zone, filter=dnsimple_filter)
        return [d.__dict__ for d in records_list]

    def delete_record(self, domain, rid):
        """delete a single dns resource record"""
        self.client.zones.delete_record(self.account.id, domain, rid)

    def update_record(self, domain, rid, ttl=None, priority=None):
        """update a single dns resource record"""
        zr = ZoneRecordUpdateInput(ttl=ttl, priority=priority)
        result = self.client.zones.update_record(self.account.id, str(domain), str(rid), zr).data.__dict__
        return result

    def create_record(self, domain, name, record_type, content, ttl=None, priority=None):
        """create a single dns resource record"""
        zr = ZoneRecordInput(name=name, type=record_type, content=content, ttl=ttl, priority=priority)
        return self.client.zones.create_record(self.account.id, str(domain), zr).data.__dict__

    def _get_paginated_result(self, operation, **options):
        """return all results of a paginated api response"""
        records_pagination = operation(per_page=self.pagination_per_page, **options).pagination
        result_list = []
        for page in range(1, records_pagination.total_pages + 1):
            page_data = operation(per_page=self.pagination_per_page, page=page, **options).data
            result_list.extend(page_data)
        return result_list


DNSIMPLE_IMP_ERR = []
HAS_DNSIMPLE = False
try:
    # try to import dnsimple >= 2.0.0
    from dnsimple import Client, DNSimpleException
    from dnsimple.service import Accounts
    from dnsimple.version import version as dnsimple_version
    from dnsimple.struct.zone_record import ZoneRecordUpdateInput, ZoneRecordInput
    HAS_DNSIMPLE = True
except ImportError:
    DNSIMPLE_IMP_ERR.append(traceback.format_exc())

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback


def main():
    module = AnsibleModule(
        argument_spec=dict(
            account_email=dict(type='str', fallback=(env_fallback, ['DNSIMPLE_EMAIL'])),
            account_api_token=dict(type='str',
                                   no_log=True,
                                   fallback=(env_fallback, ['DNSIMPLE_API_TOKEN'])),
            domain=dict(type='str'),
            record=dict(type='str'),
            record_ids=dict(type='list', elements='str'),
            type=dict(type='str', choices=['A', 'ALIAS', 'CNAME', 'MX', 'SPF',
                                           'URL', 'TXT', 'NS', 'SRV', 'NAPTR',
                                           'PTR', 'AAAA', 'SSHFP', 'HINFO',
                                           'POOL', 'CAA']),
            ttl=dict(type='int', default=3600),
            value=dict(type='str'),
            priority=dict(type='int'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            solo=dict(type='bool', default=False),
            sandbox=dict(type='bool', default=False),
        ),
        required_together=[
            ['record', 'value']
        ],
        supports_check_mode=True,
    )

    if not HAS_DNSIMPLE:
        module.fail_json(msg=missing_required_lib('dnsimple'), exception=DNSIMPLE_IMP_ERR[0])

    account_email = module.params.get('account_email')
    account_api_token = module.params.get('account_api_token')
    domain = module.params.get('domain')
    record = module.params.get('record')
    record_ids = module.params.get('record_ids')
    record_type = module.params.get('type')
    ttl = module.params.get('ttl')
    value = module.params.get('value')
    priority = module.params.get('priority')
    state = module.params.get('state')
    is_solo = module.params.get('solo')
    sandbox = module.params.get('sandbox')

    DNSIMPLE_MAJOR_VERSION = LooseVersion(dnsimple_version).version[0]

    try:
        if DNSIMPLE_MAJOR_VERSION < 2:
            module.fail_json(
                msg='Support for python-dnsimple < 2 has been removed in community.general 5.0.0. Update python-dnsimple to version >= 2.0.0.')
        ds = DNSimpleV2(account_email, account_api_token, sandbox, module)
        # Let's figure out what operation we want to do
        # No domain, return a list
        if not domain:
            all_domains = ds.get_all_domains()
            module.exit_json(changed=False, result=all_domains)

        # Domain & No record
        if record is None and not record_ids:
            if domain.isdigit():
                typed_domain = int(domain)
            else:
                typed_domain = str(domain)
            dr = ds.get_domain(typed_domain)
            # domain does not exist
            if state == 'present':
                if dr:
                    module.exit_json(changed=False, result=dr)
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = ds.create_domain(domain)
                        module.exit_json(changed=True, result=response)
            # state is absent
            else:
                if dr:
                    if not module.check_mode:
                        ds.delete_domain(domain)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # need the not none check since record could be an empty string
        if record is not None:
            if not record_type:
                module.fail_json(msg="Missing the record type")
            if not value:
                module.fail_json(msg="Missing the record value")

            records_list = ds.get_records(domain, dnsimple_filter={'name': record})
            rr = next((r for r in records_list if r['name'] == record and r['type'] == record_type and r['content'] == value), None)
            if state == 'present':
                changed = False
                if is_solo:
                    # delete any records that have the same name and record type
                    same_type = [r['id'] for r in records_list if r['name'] == record and r['type'] == record_type]
                    if rr:
                        same_type = [rid for rid in same_type if rid != rr['id']]
                    if same_type:
                        if not module.check_mode:
                            for rid in same_type:
                                ds.delete_record(domain, rid)
                        changed = True
                if rr:
                    # check if we need to update
                    if rr['ttl'] != ttl or rr['priority'] != priority:
                        if module.check_mode:
                            module.exit_json(changed=True)
                        else:
                            response = ds.update_record(domain, rr['id'], ttl, priority)
                            module.exit_json(changed=True, result=response)
                    else:
                        module.exit_json(changed=changed, result=rr)
                else:
                    # create it
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = ds.create_record(domain, record, record_type, value, ttl, priority)
                        module.exit_json(changed=True, result=response)
            # state is absent
            else:
                if rr:
                    if not module.check_mode:
                        ds.delete_record(domain, rr['id'])
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # Make sure these record_ids either all exist or none
        if record_ids:
            current_records = ds.get_records(domain, dnsimple_filter=None)
            current_record_ids = [str(d['id']) for d in current_records]
            wanted_record_ids = [str(r) for r in record_ids]
            if state == 'present':
                difference = list(set(wanted_record_ids) - set(current_record_ids))
                if difference:
                    module.fail_json(msg="Missing the following records: %s" % difference)
                else:
                    module.exit_json(changed=False)
            # state is absent
            else:
                difference = list(set(wanted_record_ids) & set(current_record_ids))
                if difference:
                    if not module.check_mode:
                        for rid in difference:
                            ds.delete_record(domain, rid)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

    except DNSimpleException as e:
        if DNSIMPLE_MAJOR_VERSION > 1:
            module.fail_json(msg="DNSimple exception: %s" % e.message)
        else:
            module.fail_json(msg="DNSimple exception: %s" % str(e.args[0]['message']))
    module.fail_json(msg="Unknown what you wanted me to do")


if __name__ == '__main__':
    main()

#!/usr/bin/python
#
# Copyright: Ansible Project
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: dnsimple
short_description: Interface with dnsimple.com (a DNS hosting service)
description:
   - "Manages domains and records via the DNSimple API, see the docs: U(http://developer.dnsimple.com/)."
options:
  account_email:
    description:
      - Account email. If omitted, the environment variables C(DNSIMPLE_EMAIL) and C(DNSIMPLE_API_TOKEN) will be looked for.
      - "If those aren't found, a C(.dnsimple) file will be looked for, see: U(https://github.com/mikemaccana/dnsimple-python#getting-started)."
    type: str
  account_api_token:
    description:
      - Account API token. See I(account_email) for more information.
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
      - Only use with C(state) is set to C(present) on a record.
    type: 'bool'
    default: no
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

- name: Fetch my.com domain records
  community.general.dnsimple:
    domain: my.com
    state: present
  delegate_to: localhost
  register: records

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

import os
import traceback
from distutils.version import LooseVersion

DNSIMPLE_IMP_ERR = None
try:
    from dnsimple import Client, DNSimpleException
    from dnsimple.service import Accounts
    from dnsimple.version import version as dnsimple_version
    from dnsimple.struct.zone_record import ZoneRecordUpdateInput, ZoneRecordInput
    HAS_DNSIMPLE = True
except ImportError:
    DNSIMPLE_IMP_ERR = traceback.format_exc()
    HAS_DNSIMPLE = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def main():
    module = AnsibleModule(
        argument_spec=dict(
            account_email=dict(type='str'),
            account_api_token=dict(type='str', no_log=True),
            domain=dict(type='str'),
            record=dict(type='str'),
            record_ids=dict(type='list', elements='str'),
            type=dict(type='str', choices=['A', 'ALIAS', 'CNAME', 'MX', 'SPF', 'URL', 'TXT', 'NS', 'SRV', 'NAPTR', 'PTR', 'AAAA', 'SSHFP', 'HINFO',
                                           'POOL', 'CAA']),
            ttl=dict(type='int', default=3600),
            value=dict(type='str'),
            priority=dict(type='int'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            solo=dict(type='bool', default=False),
        ),
        required_together=[
            ['record', 'value']
        ],
        supports_check_mode=True,
    )

    if not HAS_DNSIMPLE:
        module.fail_json(msg=missing_required_lib('dnsimple'), exception=DNSIMPLE_IMP_ERR)

    if LooseVersion(dnsimple_version) < LooseVersion('2.0.0'):
        module.fail_json(msg="community.general.dnsimple requires dnsimple Python module >= 2.0.0 (installed version: [%s])."
                             " Please upgrade dnsimple to version 2.0.0 or above." % dnsimple_version)

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
    pagination_per_page = 30

    try:
        if account_email and account_api_token:
            client = Client(email=account_email, access_token=account_api_token)
        elif os.environ.get('DNSIMPLE_EMAIL') and os.environ.get('DNSIMPLE_API_TOKEN'):
            client = Client(email=os.environ.get('DNSIMPLE_EMAIL'), access_token=os.environ.get('DNSIMPLE_API_TOKEN'))
        else:
            client = Client()
        account = client.identity.whoami().data.account

        # user supplied a user token instead of account api token
        if not account:
            accounts = Accounts(client).list_accounts().data
            if len(accounts) != 1:
                module.fail_json(msg="Provided dnsimple token is a user token with multiple accounts. Use an account token or a user token with access to a single account. See https://support.dnsimple.com/articles/api-access-token/")
            else:
                account = accounts[0]

    except DNSimpleException as e:
        module.fail_json(msg="Unable to contact DNSimple: %s" % e.message)

    try:
        # Let's figure out what operation we want to do

        # No domain, return a list
        if not domain:
            domain_list = []
            domains_pagination = client.domains.list_domains(account.id, per_page=pagination_per_page).pagination
            for page in range(1, domains_pagination.total_pages + 1):
                page_data = client.domains.list_domains(account.id, page=page, per_page=pagination_per_page).data
                domain_list.extend(page_data)
            module.exit_json(changed=False, result=[d.__dict__ for d in domain_list])

        # Domain & No record
        if domain and record is None and not record_ids:
            try:
                if domain.isdigit():
                    dr = client.domains.get_domain(account.id, int(domain)).data
                else:
                    dr = client.domains.get_domain(account.id, str(domain)).data
            # domain does not exist
            except DNSimpleException:
                dr = None
            if state == 'present':
                if dr:
                    module.exit_json(changed=False, result=dr.__dict__)
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = client.domains.create_domain(account.id, domain)
                        module.exit_json(changed=True, result=response.data.__dict__)
            # state is absent
            else:
                if dr:
                    if not module.check_mode:
                        client.domains.delete_domain(account.id, domain)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # need the not none check since record could be an empty string
        if domain and record is not None:
            dr = client.domains.get_domain(account.id, domain).data

            records_list = []
            records_pagination = client.zones.list_records(account.id, dr.name, filter={'name': record}, per_page=pagination_per_page).pagination
            for page in range(1, records_pagination.total_pages + 1):
                page_data = client.zones.list_records(account.id, dr.name, filter={'name': record}, page=page, per_page=pagination_per_page).data
                records_list.extend(page_data)

            if not record_type:
                module.fail_json(msg="Missing the record type")

            if not value:
                module.fail_json(msg="Missing the record value")

            rr = next((r for r in records_list if r.name == record and r.type == record_type and r.content == value), None)

            if state == 'present':
                changed = False
                if is_solo:
                    # delete any records that have the same name and record type
                    same_type = [r.id for r in records_list if r.name == record and r.type == record_type]
                    if rr:
                        same_type = [rid for rid in same_type if rid != rr.id]
                    if same_type:
                        if not module.check_mode:
                            for rid in same_type:
                                client.zones.delete_record(account.id, dr.name, rid)
                        changed = True
                if rr:
                    # check if we need to update
                    if rr.ttl != ttl or rr.priority != priority:
                        zr = ZoneRecordUpdateInput(ttl=ttl, priority=priority)
                        if module.check_mode:
                            module.exit_json(changed=True)
                        else:
                            response = client.zones.update_record(account.id, str(dr.name), str(rr.id), zr)
                            module.exit_json(changed=True, result=response.data.__dict__)
                    else:
                        module.exit_json(changed=changed, result=rr.__dict__)
                else:
                    # create it
                    zr = ZoneRecordInput(name=record, type=record_type, content=value, ttl=ttl, priority=priority)
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = client.zones.create_record(account.id, str(dr.name), zr)
                        module.exit_json(changed=True, result=response.data.__dict__)
            # state is absent
            else:
                if rr:
                    if not module.check_mode:
                        client.zones.delete_record(account.id, str(dr.name), rr.id)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # Make sure these record_ids either all exist or none
        if domain and record_ids:
            dr = client.domains.get_domain(account.id, domain).data
            current_records = []
            current_records_pagination = client.zones.list_records(account.id, dr.name, per_page=pagination_per_page).pagination
            for page in range(1, current_records_pagination.total_pages + 1):
                page_data = client.zones.list_records(account.id, dr.name, page=page, per_page=pagination_per_page).data
                records = [str(r.id) for r in page_data]
                current_records.extend(records)
            wanted_records = [str(r) for r in record_ids]
            if state == 'present':
                difference = list(set(wanted_records) - set(current_records))
                if difference:
                    module.fail_json(msg="Missing the following records: %s" % difference)
                else:
                    module.exit_json(changed=False)

            # state is absent
            else:
                difference = list(set(wanted_records) & set(current_records))
                if difference:
                    if not module.check_mode:
                        for rid in difference:
                            client.zones.delete_record(account.id, str(dr.name), rid)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

    except DNSimpleException as e:
        module.fail_json(msg="Unable to contact DNSimple: %s" % e.message)

    module.fail_json(msg="Unknown what you wanted me to do")


if __name__ == '__main__':
    main()

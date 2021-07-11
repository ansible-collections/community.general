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
      - "C(.dnsimple) config files are only supported in dnsimple-python<2.0.0"
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
  sandbox:
    description:
      - Use the DNSimple sandbox environment.
      - Requires a dedicated account in the dnsimple sandbox environment.
      - Check U(https://developer.dnsimple.com/sandbox/) for more information.
    type: 'bool'
    default: no
requirements:
  - "dnsimple >= 1.0.0"
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

import traceback
from distutils.version import LooseVersion
import re

DNSIMPLE_PAGINATION_PER_PAGE = 30
DNSIMPLE_MAJOR_VERSION = ""
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

if not HAS_DNSIMPLE:
    # try to import dnsimple < 2.0.0
    try:
        from dnsimple.dnsimple import __version__ as dnsimple_version
        from dnsimple import DNSimple
        from dnsimple.dnsimple import __version__ as dnsimple_version
        from dnsimple.dnsimple import DNSimpleException
        HAS_DNSIMPLE = True
    except ImportError:
        DNSIMPLE_IMP_ERR.append(traceback.format_exc())

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback


def dnsimple_client(sandbox=False, account_email=None, account_api_token=None):
    if DNSIMPLE_MAJOR_VERSION > 1:
        if account_email and account_api_token:
            client = Client(sandbox=sandbox, email=account_email, access_token=account_api_token)
        else:
            msg = "Option account_email or account_api_token not provided. " \
                  "Dnsimple authentiction with a .dnsimple config file is not " \
                  "supported with dnsimple-python>=2.0.0"
            raise DNSimpleException(msg)
    else:
        if account_email and account_api_token:
            client = DNSimple(sandbox=sandbox, email=account_email, api_token=account_api_token)
        else:
            client = DNSimple(sandbox=sandbox)
    return client


def dnsimple_account(client):
    if DNSIMPLE_MAJOR_VERSION > 1:
        account = client.identity.whoami().data.account
        # user supplied a user token instead of account api token
        if not account:
            accounts = Accounts(client).list_accounts().data
            if len(accounts) != 1:
                msg = "The provided dnsimple token is a user token with multiple accounts." \
                      "Use an account token or a user token with access to a single account." \
                      "See https://support.dnsimple.com/articles/api-access-token/"
                raise DNSimpleException(msg)
            account = accounts[0]
    else:
        account = None
    return account


def get_all_domains(client, account):
    if DNSIMPLE_MAJOR_VERSION > 1:
        domain_list = get_paginated_result(client.domains.list_domains, account_id=account.id)
        domains = [d.__dict__ for d in domain_list]
    else:
        domain_list = client.domains()
        domains = [d['domain'] for d in domain_list]
    return domains


def get_domain(client, account, domain):
    if domain.isdigit():
        typed_domain = int(domain)
    else:
        typed_domain = str(domain)

    try:
        if DNSIMPLE_MAJOR_VERSION > 1:
            dr = client.domains.get_domain(account.id, typed_domain).data.__dict__
        else:
            dr = client.domain(typed_domain)['domain']
    except DNSimpleException as e:
        if DNSIMPLE_MAJOR_VERSION > 1:
            exception_string = str(e.message)
        else:
            exception_string = str(e.args[0]['message'])
        if re.match(r"^Domain .+ not found$", exception_string):
            dr = None
        else:
            raise
    return dr


def create_domain(client, account, domain):
    if DNSIMPLE_MAJOR_VERSION > 1:
        result = client.domains.create_domain(account.id, domain).data.__dict__
    else:
        result = client.add_domain(domain)['domain']
    return result


def delete_domain(client, account, domain):
    if DNSIMPLE_MAJOR_VERSION > 1:
        client.domains.delete_domain(account.id, domain)
    else:
        client.delete(domain)


def get_records(client, account, zone, dnsimple_filter=None):
    if DNSIMPLE_MAJOR_VERSION > 1:
        records_list = get_paginated_result(client.zones.list_records,
                                            account_id=account.id,
                                            zone=zone,
                                            filter=dnsimple_filter)
        records = [d.__dict__ for d in records_list]
    else:
        records = [r['record'] for r in client.records(str(zone), params=dnsimple_filter)]
    return records


def delete_record(client, account, domain, rid):
    if DNSIMPLE_MAJOR_VERSION > 1:
        client.zones.delete_record(account.id, domain, rid)
    else:
        client.delete_record(str(domain), rid)


def update_record(client, account, domain, rid, ttl=None, priority=None):
    if DNSIMPLE_MAJOR_VERSION > 1:
        zr = ZoneRecordUpdateInput(ttl=ttl, priority=priority)
        result = client.zones.update_record(account.id, str(domain), str(rid), zr).data.__dict__
    else:
        data = {}
        if ttl:
            data['ttl'] = ttl
        if priority:
            data['priority'] = priority
        result = client.update_record(str(domain), str(rid), data)['record']
    return result


def create_record(client, account, domain, name, record_type, content, ttl=None, priority=None):
    if DNSIMPLE_MAJOR_VERSION > 1:
        zr = ZoneRecordInput(name=name, type=record_type, content=content, ttl=ttl, priority=priority)
        result = client.zones.create_record(account.id, str(domain), zr).data.__dict__
    else:
        data = {
            'name': name,
            'type': record_type,
            'content': content,
        }
        if ttl:
            data['ttl'] = ttl
        if priority:
            data['priority'] = priority
        result = client.add_record(str(domain), data)['record']
    return result


def get_paginated_result(operation, **options):
    global DNSIMPLE_PAGINATION_PER_PAGE
    records_pagination = operation(per_page=DNSIMPLE_PAGINATION_PER_PAGE, **options).pagination
    result_list = []
    for page in range(1, records_pagination.total_pages + 1):
        page_data = operation(per_page=DNSIMPLE_PAGINATION_PER_PAGE, page=page, **options).data
        result_list.extend(page_data)
    return result_list


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
        module.fail_json(msg=missing_required_lib('dnsimple'), exception=str(DNSIMPLE_IMP_ERR))

    global DNSIMPLE_MAJOR_VERSION
    DNSIMPLE_MAJOR_VERSION = LooseVersion(dnsimple_version).version[0]
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

    try:
        client = dnsimple_client(sandbox, account_email, account_api_token)
        account = dnsimple_account(client)
        # Let's figure out what operation we want to do
        # No domain, return a list
        if not domain:
            all_domains = get_all_domains(client, account)
            module.exit_json(changed=False, result=all_domains)

        # Domain & No record
        if domain and record is None and not record_ids:
            dr = get_domain(client, account, domain)
            # domain does not exist
            if state == 'present':
                if dr:
                    module.exit_json(changed=False, result=dr)
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = create_domain(client, account, domain)
                        module.exit_json(changed=True, result=response)
            # state is absent
            else:
                if dr:
                    if not module.check_mode:
                        delete_domain(client, account, domain)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # need the not none check since record could be an empty string
        if domain and record is not None:
            if not record_type:
                module.fail_json(msg="Missing the record type")
            if not value:
                module.fail_json(msg="Missing the record value")

            records_list = get_records(client,
                                       account, domain,
                                       dnsimple_filter={'name': record})
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
                                delete_record(client, account, domain, rid)
                        changed = True
                if rr:
                    # check if we need to update
                    if rr['ttl'] != ttl or rr['priority'] != priority:
                        if module.check_mode:
                            module.exit_json(changed=True)
                        else:
                            response = update_record(client, account, domain, rr['id'], ttl, priority)
                            module.exit_json(changed=True, result=response)
                    else:
                        module.exit_json(changed=changed, result=rr)
                else:
                    # create it
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        response = create_record(client, account, domain, record,
                                                 record_type, value, ttl, priority)
                        module.exit_json(changed=True, result=response)
            # state is absent
            else:
                if rr:
                    if not module.check_mode:
                        delete_record(client, account, domain, rr['id'])
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # Make sure these record_ids either all exist or none
        if domain and record_ids:
            current_records = get_records(client, account, domain, dnsimple_filter=None)
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
                            delete_record(client, account, domain, rid)
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

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
notes:
  - DNSimple API v1 is deprecated. Please install dnsimple-python>=1.0.0 which uses v2 API.
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
  type:
    description:
      - The type of DNS record to create.
    choices: [ 'A', 'ALIAS', 'CNAME', 'MX', 'SPF', 'URL', 'TXT', 'NS', 'SRV', 'NAPTR', 'PTR', 'AAAA', 'SSHFP', 'HINFO', 'POOL' ]
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

import os
import traceback
from distutils.version import LooseVersion

DNSIMPLE_IMP_ERR = None
try:
    from dnsimple import DNSimple
    from dnsimple.dnsimple import __version__ as dnsimple_version
    from dnsimple.dnsimple import DNSimpleException
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
            record_ids=dict(type='list'),
            type=dict(type='str', choices=['A', 'ALIAS', 'CNAME', 'MX', 'SPF', 'URL', 'TXT', 'NS', 'SRV', 'NAPTR', 'PTR', 'AAAA', 'SSHFP', 'HINFO',
                                           'POOL']),
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

    if LooseVersion(dnsimple_version) < LooseVersion('1.0.0'):
        module.fail_json(msg="Current version of dnsimple Python module [%s] uses 'v1' API which is deprecated."
                             " Please upgrade to version 1.0.0 and above to use dnsimple 'v2' API." % dnsimple_version)

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

    if account_email and account_api_token:
        client = DNSimple(email=account_email, api_token=account_api_token)
    elif os.environ.get('DNSIMPLE_EMAIL') and os.environ.get('DNSIMPLE_API_TOKEN'):
        client = DNSimple(email=os.environ.get('DNSIMPLE_EMAIL'), api_token=os.environ.get('DNSIMPLE_API_TOKEN'))
    else:
        client = DNSimple()

    try:
        # Let's figure out what operation we want to do

        # No domain, return a list
        if not domain:
            domains = client.domains()
            module.exit_json(changed=False, result=[d['domain'] for d in domains])

        # Domain & No record
        if domain and record is None and not record_ids:
            domains = [d['domain'] for d in client.domains()]
            if domain.isdigit():
                dr = next((d for d in domains if d['id'] == int(domain)), None)
            else:
                dr = next((d for d in domains if d['name'] == domain), None)
            if state == 'present':
                if dr:
                    module.exit_json(changed=False, result=dr)
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        module.exit_json(changed=True, result=client.add_domain(domain)['domain'])

            # state is absent
            else:
                if dr:
                    if not module.check_mode:
                        client.delete(domain)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # need the not none check since record could be an empty string
        if domain and record is not None:
            records = [r['record'] for r in client.records(str(domain), params={'name': record})]

            if not record_type:
                module.fail_json(msg="Missing the record type")

            if not value:
                module.fail_json(msg="Missing the record value")

            rr = next((r for r in records if r['name'] == record and r['type'] == record_type and r['content'] == value), None)

            if state == 'present':
                changed = False
                if is_solo:
                    # delete any records that have the same name and record type
                    same_type = [r['id'] for r in records if r['name'] == record and r['type'] == record_type]
                    if rr:
                        same_type = [rid for rid in same_type if rid != rr['id']]
                    if same_type:
                        if not module.check_mode:
                            for rid in same_type:
                                client.delete_record(str(domain), rid)
                        changed = True
                if rr:
                    # check if we need to update
                    if rr['ttl'] != ttl or rr['priority'] != priority:
                        data = {}
                        if ttl:
                            data['ttl'] = ttl
                        if priority:
                            data['priority'] = priority
                        if module.check_mode:
                            module.exit_json(changed=True)
                        else:
                            module.exit_json(changed=True, result=client.update_record(str(domain), str(rr['id']), data)['record'])
                    else:
                        module.exit_json(changed=changed, result=rr)
                else:
                    # create it
                    data = {
                        'name': record,
                        'type': record_type,
                        'content': value,
                    }
                    if ttl:
                        data['ttl'] = ttl
                    if priority:
                        data['priority'] = priority
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        module.exit_json(changed=True, result=client.add_record(str(domain), data)['record'])

            # state is absent
            else:
                if rr:
                    if not module.check_mode:
                        client.delete_record(str(domain), rr['id'])
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

        # Make sure these record_ids either all exist or none
        if domain and record_ids:
            current_records = [str(r['record']['id']) for r in client.records(str(domain))]
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
                            client.delete_record(str(domain), rid)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)

    except DNSimpleException as e:
        module.fail_json(msg="Unable to contact DNSimple: %s" % e.message)

    module.fail_json(msg="Unknown what you wanted me to do")


if __name__ == '__main__':
    main()

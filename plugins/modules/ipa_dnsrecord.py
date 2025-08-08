#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Abhijeet Kasurde (akasurde@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ipa_dnsrecord
author: Abhijeet Kasurde (@Akasurde)
short_description: Manage FreeIPA DNS records
description:
  - Add, modify and delete an IPA DNS Record using IPA API.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  zone_name:
    description:
      - The DNS zone name to which DNS record needs to be managed.
    required: true
    type: str
  record_name:
    description:
      - The DNS record name to manage.
    required: true
    aliases: ["name"]
    type: str
  record_type:
    description:
      - The type of DNS record name.
      - Support for V(NS) was added in comunity.general 8.2.0.
      - Support for V(SSHFP) was added in community.general 9.1.0.
    required: false
    default: 'A'
    choices: ['A', 'AAAA', 'A6', 'CNAME', 'DNAME', 'MX', 'NS', 'PTR', 'SRV', 'TXT', 'SSHFP']
    type: str
  record_value:
    description:
      - Manage DNS record name with this value.
      - Mutually exclusive with O(record_values), and exactly one of O(record_value) and O(record_values) has to be specified.
      - Use O(record_values) if you need to specify multiple values.
      - In the case of V(A) or V(AAAA) record types, this is the IP address.
      - In the case of V(A6) record type, this is the A6 Record data.
      - In the case of V(CNAME) record type, this is the hostname.
      - In the case of V(DNAME) record type, this is the DNAME target.
      - In the case of V(NS) record type, this is the name server hostname. Hostname must already have a valid A or AAAA record.
      - In the case of V(PTR) record type, this is the hostname.
      - In the case of V(TXT) record type, this is a text.
      - In the case of V(SRV) record type, this is a service record.
      - In the case of V(MX) record type, this is a mail exchanger record.
      - In the case of V(SSHFP) record type, this is an SSH fingerprint record.
    type: str
  record_values:
    description:
      - Manage DNS record name with this value.
      - Mutually exclusive with O(record_value), and exactly one of O(record_value) and O(record_values) has to be specified.
      - In the case of V(A) or V(AAAA) record types, this is the IP address.
      - In the case of V(A6) record type, this is the A6 Record data.
      - In the case of V(CNAME) record type, this is the hostname.
      - In the case of V(DNAME) record type, this is the DNAME target.
      - In the case of V(NS) record type, this is the name server hostname. Hostname must already have a valid A or AAAA record.
      - In the case of V(PTR) record type, this is the hostname.
      - In the case of V(TXT) record type, this is a text.
      - In the case of V(SRV) record type, this is a service record.
      - In the case of V(MX) record type, this is a mail exchanger record.
      - In the case of V(SSHFP) record type, this is an SSH fingerprint record.
    type: list
    elements: str
  record_ttl:
    description:
      - Set the TTL for the record.
      - Applies only when adding a new or changing the value of O(record_value) or O(record_values).
    required: false
    type: int
  state:
    description: State to ensure.
    required: false
    default: present
    choices: ["absent", "present"]
    type: str
extends_documentation_fragment:
  - community.general.ipa.documentation
  - community.general.ipa.connection_notes
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Ensure dns record is present
  community.general.ipa_dnsrecord:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    record_name: vm-001
    record_type: 'AAAA'
    record_value: '::1'

- name: Ensure that dns records exists with a TTL
  community.general.ipa_dnsrecord:
    name: host02
    zone_name: example.com
    record_type: 'AAAA'
    record_values: '::1,fe80::1'
    record_ttl: 300
    ipa_host: ipa.example.com
    ipa_pass: topsecret
    state: present

- name: Ensure a PTR record is present
  community.general.ipa_dnsrecord:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: 2.168.192.in-addr.arpa
    record_name: 5
    record_type: 'PTR'
    record_value: 'internal.ipa.example.com'

- name: Ensure a TXT record is present
  community.general.ipa_dnsrecord:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    record_name: _kerberos
    record_type: 'TXT'
    record_value: 'EXAMPLE.COM'

- name: Ensure an SRV record is present
  community.general.ipa_dnsrecord:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    record_name: _kerberos._udp.example.com
    record_type: 'SRV'
    record_value: '10 50 88 ipa.example.com'

- name: Ensure an MX records are present
  community.general.ipa_dnsrecord:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    record_name: '@'
    record_type: 'MX'
    record_values:
      - '1 mailserver-01.example.com'
      - '2 mailserver-02.example.com'

- name: Ensure that dns record is removed
  community.general.ipa_dnsrecord:
    name: host01
    zone_name: example.com
    record_type: 'AAAA'
    record_value: '::1'
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
    state: absent

- name: Ensure an NS record for a subdomain is present
  community.general.ipa_dnsrecord:
    name: subdomain
    zone_name: example.com
    record_type: 'NS'
    record_value: 'ns1.subdomain.exmaple.com'
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: ChangeMe!

- name: Retrieve the current sshfp fingerprints
  ansible.builtin.command: ssh-keyscan -D localhost
  register: ssh_hostkeys

- name: Update the SSHFP records in DNS
  community.general.ipa_dnsrecord:
    name: "{{ inventory_hostname}}"
    zone_name: example.com
    record_type: 'SSHFP'
    record_values: "{{ ssh_hostkeys.stdout.split('\n') | map('split', 'SSHFP ') | map('last') | list }}"
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: ChangeMe!
"""

RETURN = r"""
dnsrecord:
  description: DNS record as returned by IPA API.
  returned: always
  type: dict
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class DNSRecordIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(DNSRecordIPAClient, self).__init__(module, host, port, protocol)

    def dnsrecord_find(self, zone_name, record_name):
        if record_name == '@':
            return self._post_json(method='dnsrecord_show', name=zone_name, item={'idnsname': record_name, 'all': True})
        else:
            return self._post_json(method='dnsrecord_find', name=zone_name, item={'idnsname': record_name, 'all': True})

    def dnsrecord_add(self, zone_name=None, record_name=None, details=None):
        item = dict(idnsname=record_name)

        if details.get('record_ttl'):
            item.update(dnsttl=details['record_ttl'])

        for value in details['record_values']:
            if details['record_type'] == 'A':
                item.update(a_part_ip_address=value)
            elif details['record_type'] == 'AAAA':
                item.update(aaaa_part_ip_address=value)
            elif details['record_type'] == 'A6':
                item.update(a6_part_data=value)
            elif details['record_type'] == 'CNAME':
                item.update(cname_part_hostname=value)
            elif details['record_type'] == 'DNAME':
                item.update(dname_part_target=value)
            elif details['record_type'] == 'NS':
                item.update(ns_part_hostname=value)
            elif details['record_type'] == 'PTR':
                item.update(ptr_part_hostname=value)
            elif details['record_type'] == 'TXT':
                item.update(txtrecord=value)
            elif details['record_type'] == 'SRV':
                item.update(srvrecord=value)
            elif details['record_type'] == 'MX':
                item.update(mxrecord=value)
            elif details['record_type'] == 'SSHFP':
                item.update(sshfprecord=value)

            self._post_json(method='dnsrecord_add', name=zone_name, item=item)

    def dnsrecord_mod(self, zone_name=None, record_name=None, details=None):
        item = get_dnsrecord_dict(details)
        item.update(idnsname=record_name)
        if details.get('record_ttl'):
            item.update(dnsttl=details['record_ttl'])
        return self._post_json(method='dnsrecord_mod', name=zone_name, item=item)

    def dnsrecord_del(self, zone_name=None, record_name=None, details=None):
        item = get_dnsrecord_dict(details)
        item.update(idnsname=record_name)
        return self._post_json(method='dnsrecord_del', name=zone_name, item=item)


def get_dnsrecord_dict(details=None):
    module_dnsrecord = dict()
    if details['record_type'] == 'A' and details['record_values']:
        module_dnsrecord.update(arecord=details['record_values'])
    elif details['record_type'] == 'AAAA' and details['record_values']:
        module_dnsrecord.update(aaaarecord=details['record_values'])
    elif details['record_type'] == 'A6' and details['record_values']:
        module_dnsrecord.update(a6record=details['record_values'])
    elif details['record_type'] == 'CNAME' and details['record_values']:
        module_dnsrecord.update(cnamerecord=details['record_values'])
    elif details['record_type'] == 'DNAME' and details['record_values']:
        module_dnsrecord.update(dnamerecord=details['record_values'])
    elif details['record_type'] == 'NS' and details['record_values']:
        module_dnsrecord.update(nsrecord=details['record_values'])
    elif details['record_type'] == 'PTR' and details['record_values']:
        module_dnsrecord.update(ptrrecord=details['record_values'])
    elif details['record_type'] == 'TXT' and details['record_values']:
        module_dnsrecord.update(txtrecord=details['record_values'])
    elif details['record_type'] == 'SRV' and details['record_values']:
        module_dnsrecord.update(srvrecord=details['record_values'])
    elif details['record_type'] == 'MX' and details['record_values']:
        module_dnsrecord.update(mxrecord=details['record_values'])
    elif details['record_type'] == 'SSHFP' and details['record_values']:
        module_dnsrecord.update(sshfprecord=details['record_values'])

    if details.get('record_ttl'):
        module_dnsrecord.update(dnsttl=details['record_ttl'])

    return module_dnsrecord


def get_dnsrecord_diff(client, ipa_dnsrecord, module_dnsrecord):
    details = get_dnsrecord_dict(module_dnsrecord)
    return client.get_diff(ipa_data=ipa_dnsrecord, module_data=details)


def ensure(module, client):
    zone_name = module.params['zone_name']
    record_name = module.params['record_name']
    record_ttl = module.params.get('record_ttl')
    state = module.params['state']

    ipa_dnsrecord = client.dnsrecord_find(zone_name, record_name)

    record_values = module.params['record_values']
    if module.params['record_value'] is not None:
        record_values = [module.params['record_value']]

    module_dnsrecord = dict(
        record_type=module.params['record_type'],
        record_values=record_values,
        record_ttl=to_native(record_ttl, nonstring='passthru'),
    )

    # ttl is not required to change records
    if module_dnsrecord['record_ttl'] is None:
        module_dnsrecord.pop('record_ttl')

    changed = False
    if state == 'present':
        if not ipa_dnsrecord:
            changed = True
            if not module.check_mode:
                client.dnsrecord_add(zone_name=zone_name,
                                     record_name=record_name,
                                     details=module_dnsrecord)
        else:
            diff = get_dnsrecord_diff(client, ipa_dnsrecord, module_dnsrecord)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:
                    client.dnsrecord_mod(zone_name=zone_name,
                                         record_name=record_name,
                                         details=module_dnsrecord)
    else:
        if ipa_dnsrecord:
            changed = True
            if not module.check_mode:
                client.dnsrecord_del(zone_name=zone_name,
                                     record_name=record_name,
                                     details=module_dnsrecord)

    return changed, client.dnsrecord_find(zone_name, record_name)


def main():
    record_types = ['A', 'AAAA', 'A6', 'CNAME', 'DNAME', 'NS', 'PTR', 'TXT', 'SRV', 'MX', 'SSHFP']
    argument_spec = ipa_argument_spec()
    argument_spec.update(
        zone_name=dict(type='str', required=True),
        record_name=dict(type='str', aliases=['name'], required=True),
        record_type=dict(type='str', default='A', choices=record_types),
        record_value=dict(type='str'),
        record_values=dict(type='list', elements='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        record_ttl=dict(type='int'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[['record_value', 'record_values']],
        required_one_of=[['record_value', 'record_values']],
        supports_check_mode=True
    )

    client = DNSRecordIPAClient(
        module=module,
        host=module.params['ipa_host'],
        port=module.params['ipa_port'],
        protocol=module.params['ipa_prot']
    )

    try:
        client.login(
            username=module.params['ipa_user'],
            password=module.params['ipa_pass']
        )
        changed, record = ensure(module, client)
        module.exit_json(changed=changed, record=record)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

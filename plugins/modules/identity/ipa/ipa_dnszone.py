#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Fran Fitzpatrick (francis.x.fitzpatrick@gmail.com)
# Borrowed heavily from other work by Abhijeet Kasurde (akasurde@redhat.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_dnszone
author: Fran Fitzpatrick (@fxfitz)
short_description: Manage FreeIPA DNS Zones
description:
- Add and delete an IPA DNS Zones using IPA API
options:
  zone_name:
    description:
    - The DNS zone name to which needs to be managed.
    required: true
    type: str
  state:
    description: State to ensure
    required: false
    default: present
    choices: ["absent", "present"]
    type: str
  dynamicupdate:
    description: Apply dynamic update to zone.
    default: false
    type: bool
  allowsyncptr:
    description: Allow synchronization of forward and reverse records in the zone.
    default: false
    type: bool
    version_added: 4.3.0
extends_documentation_fragment:
- community.general.ipa.documentation

'''

EXAMPLES = r'''
- name: Ensure dns zone is present
  community.general.ipa_dnszone:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com

- name: Ensure dns zone is present and is dynamic update
  community.general.ipa_dnszone:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    dynamicupdate: true

- name: Ensure that dns zone is removed
  community.general.ipa_dnszone:
    zone_name: example.com
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: topsecret
    state: absent

- name: Ensure dns zone is present and is allowing sync
  community.general.ipa_dnszone:
    ipa_host: spider.example.com
    ipa_pass: Passw0rd!
    state: present
    zone_name: example.com
    allowsyncptr: true
'''

RETURN = r'''
zone:
  description: DNS zone as returned by IPA API.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class DNSZoneIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(DNSZoneIPAClient, self).__init__(module, host, port, protocol)

    def dnszone_find(self, zone_name, details=None):
        items = {'all': 'true',
                 'idnsname': zone_name, }
        if details is not None:
            items.update(details)

        return self._post_json(
            method='dnszone_find',
            name=zone_name,
            item=items
        )

    def dnszone_add(self, zone_name=None, details=None):
        items = {}
        if details is not None:
            items.update(details)

        return self._post_json(
            method='dnszone_add',
            name=zone_name,
            item=items
        )

    def dnszone_mod(self, zone_name=None, details=None):
        items = {}
        if details is not None:
            items.update(details)

        return self._post_json(
            method='dnszone_mod',
            name=zone_name,
            item=items
        )

    def dnszone_del(self, zone_name=None, record_name=None, details=None):
        return self._post_json(
            method='dnszone_del', name=zone_name, item={})


def ensure(module, client):
    zone_name = module.params['zone_name']
    state = module.params['state']
    dynamicupdate = module.params['dynamicupdate']
    allowsyncptr = module.params['allowsyncptr']

    changed = False

    # does zone exist
    ipa_dnszone = client.dnszone_find(zone_name)

    if state == 'present':
        if not ipa_dnszone:

            changed = True
            if not module.check_mode:
                client.dnszone_add(zone_name=zone_name, details={'idnsallowdynupdate': dynamicupdate, 'idnsallowsyncptr': allowsyncptr})
        elif ipa_dnszone['idnsallowdynupdate'][0] != str(dynamicupdate).upper() or ipa_dnszone['idnsallowsyncptr'][0] != str(allowsyncptr).upper():
            changed = True
            if not module.check_mode:
                client.dnszone_mod(zone_name=zone_name, details={'idnsallowdynupdate': dynamicupdate, 'idnsallowsyncptr': allowsyncptr})
        else:
            changed = False

    # state is absent
    else:
        # check for generic zone existence
        if ipa_dnszone:
            changed = True
            if not module.check_mode:
                client.dnszone_del(zone_name=zone_name)

    return changed, client.dnszone_find(zone_name)


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(zone_name=dict(type='str', required=True),
                         state=dict(type='str', default='present', choices=['present', 'absent']),
                         dynamicupdate=dict(type='bool', required=False, default=False),
                         allowsyncptr=dict(type='bool', required=False, default=False),
                         )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )

    client = DNSZoneIPAClient(
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
        changed, zone = ensure(module, client)
        module.exit_json(changed=changed, zone=zone)
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()

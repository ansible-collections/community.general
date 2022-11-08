#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright: (c) 2016, Adfinis SyGroup AG
# Tobias Rueetschi <tobias.ruetschi@adfinis-sygroup.ch>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: udm_dns_record
author:
- Tobias Rüetschi (@keachi)
short_description: Manage dns entries on a univention corporate server
description:
    - "This module allows to manage dns records on a univention corporate server (UCS).
       It uses the python API of the UCS to create a new object or edit it."
requirements:
    - Python >= 2.6
    - Univention
options:
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the dns record is present or not.
    name:
        required: true
        description:
            - "Name of the record, this is also the DNS record. E.g. www for
               www.example.com."
    zone:
        required: true
        description:
            - Corresponding DNS zone for this record, e.g. example.com.
    type:
        required: true
        choices: [ host_record, alias, ptr_record, srv_record, txt_record ]
        description:
            - "Define the record type. C(host_record) is a A or AAAA record,
               C(alias) is a CNAME, C(ptr_record) is a PTR record, C(srv_record)
               is a SRV record and C(txt_record) is a TXT record."
    data:
        required: false
        default: []
        description:
            - "Additional data for this record, e.g. ['a': '192.0.2.1'].
               Required if C(state=present)."
'''


EXAMPLES = '''
- name: Create a DNS record on a UCS
  community.general.udm_dns_record:
    name: www
    zone: example.com
    type: host_record
    data:
      a:
         - 192.0.2.1
         - 2001:0db8::42
'''


RETURN = '''#'''

HAVE_UNIVENTION = False
try:
    from univention.admin.handlers.dns import (
        forward_zone,
        reverse_zone,
    )
    HAVE_UNIVENTION = True
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.univention_umc import (
    umc_module_for_add,
    umc_module_for_edit,
    ldap_search,
    base_dn,
    config,
    uldap,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            type=dict(required=True,
                      type='str'),
            zone=dict(required=True,
                      type='str'),
            name=dict(required=True,
                      type='str'),
            data=dict(default=[],
                      type='dict'),
            state=dict(default='present',
                       choices=['present', 'absent'],
                       type='str')
        ),
        supports_check_mode=True,
        required_if=([
            ('state', 'present', ['data'])
        ])
    )

    if not HAVE_UNIVENTION:
        module.fail_json(msg="This module requires univention python bindings")

    type = module.params['type']
    zone = module.params['zone']
    name = module.params['name']
    data = module.params['data']
    state = module.params['state']
    changed = False
    diff = None

    obj = list(ldap_search(
        '(&(objectClass=dNSZone)(zoneName={0})(relativeDomainName={1}))'.format(zone, name),
        attr=['dNSZone']
    ))

    exists = bool(len(obj))
    container = 'zoneName={0},cn=dns,{1}'.format(zone, base_dn())
    dn = 'relativeDomainName={0},{1}'.format(name, container)

    if state == 'present':
        try:
            if not exists:
                so = forward_zone.lookup(
                    config(),
                    uldap(),
                    '(zone={0})'.format(zone),
                    scope='domain',
                ) or reverse_zone.lookup(
                    config(),
                    uldap(),
                    '(zone={0})'.format(zone),
                    scope='domain',
                )
                obj = umc_module_for_add('dns/{0}'.format(type), container, superordinate=so[0])
            else:
                obj = umc_module_for_edit('dns/{0}'.format(type), dn)
            obj['name'] = name
            for k, v in data.items():
                obj[k] = v
            diff = obj.diff()
            changed = obj.diff() != []
            if not module.check_mode:
                if not exists:
                    obj.create()
                else:
                    obj.modify()
        except Exception as e:
            module.fail_json(
                msg='Creating/editing dns entry {0} in {1} failed: {2}'.format(name, container, e)
            )

    if state == 'absent' and exists:
        try:
            obj = umc_module_for_edit('dns/{0}'.format(type), dn)
            if not module.check_mode:
                obj.remove()
            changed = True
        except Exception as e:
            module.fail_json(
                msg='Removing dns entry {0} in {1} failed: {2}'.format(name, container, e)
            )

    module.exit_json(
        changed=changed,
        name=name,
        diff=diff,
        container=container
    )


if __name__ == '__main__':
    main()

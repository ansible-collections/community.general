#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: xenserver_facts
short_description: Get facts reported on xenserver
description:
  - Reads data out of XenAPI, can be used instead of multiple xe commands.
author:
  - Andy Hill (@andyhky)
  - Tim Rupp (@caphrim007)
  - Robin Lee (@cheese)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.facts
  - community.general.attributes.facts_module
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options: {}
'''

EXAMPLES = '''
- name: Gather facts from xenserver
  community.general.xenserver_facts:

- name: Print running VMs
  ansible.builtin.debug:
    msg: "{{ item }}"
  with_items: "{{ xs_vms.keys() }}"
  when: xs_vms[item]['power_state'] == "Running"

# Which will print:
#
# TASK: [Print running VMs] ***********************************************************
# skipping: [10.13.0.22] => (item=CentOS 4.7 (32-bit))
# ok: [10.13.0.22] => (item=Control domain on host: 10.0.13.22) => {
#     "item": "Control domain on host: 10.0.13.22",
#     "msg": "Control domain on host: 10.0.13.22"
# }
'''


HAVE_XENAPI = False
try:
    import XenAPI
    HAVE_XENAPI = True
except ImportError:
    pass

from ansible.module_utils import distro
from ansible.module_utils.basic import AnsibleModule


class XenServerFacts:
    def __init__(self):
        self.codes = {
            '5.5.0': 'george',
            '5.6.100': 'oxford',
            '6.0.0': 'boston',
            '6.1.0': 'tampa',
            '6.2.0': 'clearwater'
        }

    @property
    def version(self):
        result = distro.linux_distribution()[1]
        return result

    @property
    def codename(self):
        if self.version in self.codes:
            result = self.codes[self.version]
        else:
            result = None

        return result


def get_xenapi_session():
    session = XenAPI.xapi_local()
    session.xenapi.login_with_password('', '')
    return session


def get_networks(session):
    recs = session.xenapi.network.get_all_records()
    networks = change_keys(recs, key='name_label')
    return networks


def get_pifs(session):
    recs = session.xenapi.PIF.get_all_records()
    pifs = change_keys(recs, key='uuid')
    xs_pifs = {}
    devicenums = range(0, 7)
    for pif in pifs.values():
        for eth in devicenums:
            interface_name = "eth%s" % (eth)
            bond_name = interface_name.replace('eth', 'bond')
            if pif['device'] == interface_name:
                xs_pifs[interface_name] = pif
            elif pif['device'] == bond_name:
                xs_pifs[bond_name] = pif
    return xs_pifs


def get_vlans(session):
    recs = session.xenapi.VLAN.get_all_records()
    return change_keys(recs, key='tag')


def change_keys(recs, key='uuid', filter_func=None):
    """
    Take a xapi dict, and make the keys the value of recs[ref][key].

    Preserves the ref in rec['ref']

    """
    new_recs = {}

    for ref, rec in recs.items():
        if filter_func is not None and not filter_func(rec):
            continue

        for param_name, param_value in rec.items():
            # param_value may be of type xmlrpc.client.DateTime,
            # which is not simply convertable to str.
            # Use 'value' attr to get the str value,
            # following an example in xmlrpc.client.DateTime document
            if hasattr(param_value, "value"):
                rec[param_name] = param_value.value
        new_recs[rec[key]] = rec
        new_recs[rec[key]]['ref'] = ref

    return new_recs


def get_host(session):
    """Get the host"""
    host_recs = session.xenapi.host.get_all()
    # We only have one host, so just return its entry
    return session.xenapi.host.get_record(host_recs[0])


def get_vms(session):
    recs = session.xenapi.VM.get_all_records()
    if not recs:
        return None
    vms = change_keys(recs, key='name_label')
    return vms


def get_srs(session):
    recs = session.xenapi.SR.get_all_records()
    if not recs:
        return None
    srs = change_keys(recs, key='name_label')
    return srs


def main():
    module = AnsibleModule({}, supports_check_mode=True)

    if not HAVE_XENAPI:
        module.fail_json(changed=False, msg="python xen api required for this module")

    obj = XenServerFacts()
    try:
        session = get_xenapi_session()
    except XenAPI.Failure as e:
        module.fail_json(msg='%s' % e)

    data = {
        'xenserver_version': obj.version,
        'xenserver_codename': obj.codename
    }

    xs_networks = get_networks(session)
    xs_pifs = get_pifs(session)
    xs_vlans = get_vlans(session)
    xs_vms = get_vms(session)
    xs_srs = get_srs(session)

    if xs_vlans:
        data['xs_vlans'] = xs_vlans
    if xs_pifs:
        data['xs_pifs'] = xs_pifs
    if xs_networks:
        data['xs_networks'] = xs_networks

    if xs_vms:
        data['xs_vms'] = xs_vms

    if xs_srs:
        data['xs_srs'] = xs_srs

    module.exit_json(ansible_facts=data)


if __name__ == '__main__':
    main()

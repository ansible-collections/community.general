#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Alexander Bakanovskii <skottttt228@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: kutils
short_description: Kerberos utils for managing tickets
description:
  - Manage Kerberos tickets with C(kinit), C(klist) and C(kdestroy) base utilities.
author: "Alexander Bakanovskii (@abakanovskii)"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  password:
    description:
      - Principal password.
      - It is required to specify O(password) or O(keytab_path).
    type: str
  principal:
    description:
      - The principal name.
      - If not set, the user running this module will be used.
    type: str
  state:
    description:
      - The state of the Kerberos ticket.
      - V(present) is equivalent of C(kinit) command.
      - V(absent) is equivalent of C(kdestroy) command.
    type: str
    default: present
    choices: ["present", "absent"]
  kdestroy_all:
    description:
      - When O(state=absent) destroys all credential caches in collection.
      - Equivalent of running C(kdestroy -A).
    type: bool
  cache_name:
    description:
      - Use V(cache_name) as the ticket cache name and location.
      - If this option is not used, the default cache name and location are used.
      - The default credentials cache may vary between systems.
      - If not set the the value of E(KRB5CCNAME) environment variable will be used instead, its value is used to name the default ticket cache.
    type: str
  lifetime:
    description:
      - Requests a ticket with the lifetime, if the O(lifetime) is not specified, the default ticket lifetime is used.
      - Specifying a ticket lifetime longer than the maximum ticket lifetime (configured by each site) will not override the configured maximum ticket lifetime.
    type: str
  start_time:
    description:
      - Requests a postdated ticket.
      - Postdated tickets are issued with the invalid flag set, and need to be resubmitted to the KDC for validation before use.
      - O(start_time) specifies the duration of the delay before the ticket can become valid.
    type: str
  renewable:
    description:
      - Requests renewable tickets, with a total lifetime equal to O(renewable).
    type: str
  forwardable:
    description:
      - Request forwardable or non-forwardable tickets.
    type: bool
  proxiable:
    description:
      - Request proxiable or non-proxiable tickets.
    type: bool
  address_restricted:
    description:
      - Request tickets restricted to the host's local address or non-restricted.
    type: bool
  anonymous:
    description:
      - Requests anonymous processing.
    type: bool
  canonicalization:
    description:
      - Requests canonicalization of the principal name, and allows the KDC to reply with a different client principal from the one requested.
    type: bool
  enterprise:
    description:
      - Treats the principal name as an enterprise name (implies the O(canonicalization) option).
    type: bool
  renewal:
    description:
      - Requests renewal of the ticket-granting ticket.
      - Note that an expired ticket cannot be renewed, even if the ticket is still within its renewable life.
    type: bool
  validate:
    description:
      - Requests that the ticket-granting ticket in the cache (with the invalid flag set) be passed to the KDC for validation.
      - If the ticket is within its requested time range, the cache is replaced with the validated ticket.
    type: bool
  keytab:
    description:
      - Requests a ticket, obtained from a key in the local host's keytab.
      - If O(keytab_path) is not specified will try to use default client keytab path (C(-i) option).
    type: bool
  keytab_path:
    description:
      - Use when O(keytab=true) to specify path to a keytab file.
      - It is required to specify O(password) or O(keytab_path).
    type: path
requirements:
  - krb5-user and krb5-config packages
extends_documentation_fragment:
  - community.general.attributes
'''

EXAMPLES = r'''
- name: Get Kerberos ticket using default principal
  community.general.kutils:
    password: some_password

- name: Get Kerberos ticket using keytab
  community.general.kutils:
    keytab: true
    keytab_path: /etc/ipa/file.keytab

- name: Get Kerberos ticket using principal name
  community.general.kutils:
    password: some_password
    principal: admin

- name: Get Kerberos ticket using principal with realm
  community.general.kutils:
    password: some_password
    principal: admin@IPA.TEST

- name: Check for existence by ticket cache
  community.general.kutils:
    cache_name: KEYRING:persistent:0:0

- name: Make sure default ticket is destroyed
  community.general.kutils:
    state: absent

- name: Make sure specific ticket destroyed by principal
  community.general.kutils:
    state: absent
    principal: admin@IPA.TEST

- name: Make sure specific ticket destroyed by cache_name
  community.general.kutils:
    state: absent
    cache_name: KEYRING:persistent:0:0

- name: Make sure all tickets are destroyed
  community.general.kutils:
    state: absent
    kdestroy_all: true
'''

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


class IPAKeytab(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.password = kwargs['password']
        self.principal = kwargs['principal']
        self.state = kwargs['state']
        self.kdestroy_all = kwargs['kdestroy_all']
        self.cache_name = kwargs['cache_name']
        self.start_time = kwargs['start_time']
        self.renewable = kwargs['renewable']
        self.forwardable = kwargs['forwardable']
        self.proxiable = kwargs['proxiable']
        self.address_restricted = kwargs['address_restricted']
        self.canonicalization = kwargs['canonicalization']
        self.enterprise = kwargs['enterprise']
        self.renewal = kwargs['renewal']
        self.validate = kwargs['validate']
        self.keytab = kwargs['keytab']
        self.keytab_path = kwargs['keytab_path']

        self.kinit = CmdRunner(
            module,
            command='kinit',
            arg_formats=dict(
                lifetime=cmd_runner_fmt.as_opt_val('-l'),
                start_time=cmd_runner_fmt.as_opt_val('-s'),
                renewable=cmd_runner_fmt.as_opt_val('-r'),
                forwardable=cmd_runner_fmt.as_bool('-f', '-F'),
                proxiable=cmd_runner_fmt.as_bool('-p', '-P'),
                address_restricted=cmd_runner_fmt.as_bool('-a', '-A'),
                anonymous=cmd_runner_fmt.as_bool('-n'),
                canonicalization=cmd_runner_fmt.as_bool('-C'),
                enterprise=cmd_runner_fmt.as_bool('-E'),
                renewal=cmd_runner_fmt.as_bool('-R'),
                validate=cmd_runner_fmt.as_bool('-v'),
                keytab=cmd_runner_fmt.as_bool('-k'),
                keytab_path=cmd_runner_fmt.as_func(lambda v: ['-t', v] if v else ['-i']),
                cache_name=cmd_runner_fmt.as_opt_val('-c'),
            )
        )

        self.kdestroy = CmdRunner(
            module,
            command='kdestroy',
            arg_formats=dict(
                kdestroy_all=cmd_runner_fmt.as_bool('-A'),
                cache_name=cmd_runner_fmt.as_opt_val('-c'),
                principal=cmd_runner_fmt.as_opt_val('-p'),
            )
        )

        self.klist = CmdRunner(
            module,
            command='klist',
            arg_formats=dict(
                list=cmd_runner_fmt.as_bool('-l'),
            )
        )

    def exec_kinit(self):
        params = dict(self.module.params)
        with self.kinit(
            "lifetime start_time renewable forwardable proxiable address_restricted anonymous canonicalization enterprise renewal validate keytab keytab_path",
            check_rc=True,
            data=self.password,
        ) as ctx:
            rc, out, err = ctx.run(**params)
        return out

    def exec_kdestroy(self):
        params = dict(self.module.params)
        with self.kdestroy(
            "kdestroy_all cache_name principal",
            check_rc=True
        ) as ctx:
            rc, out, err = ctx.run(**params)
        return out

    def exec_klist(self, list):
        # Use chech_rc = False because
        # If no tickets present, klist command will always return rc = 1
        with self.klist(
            "list",
            check_rc=False
        ) as ctx:
            rc, out, err = ctx.run(list)
        return rc, out, err

    def check_ticket_present(self):
        ticket_present = True
        list = False

        if not self.principal and not self.cache_name:
            rc, out, err = self.exec_klist(list)
            if rc != 0:
                ticket_present = False
        else:
            list = True
            rc, out, err = self.exec_klist(list)
            if self.principal and self.principal not in str(out):
                ticket_present = False
            if self.cache_name and self.cache_name not in str(out):
                ticket_present = False

        return ticket_present


def main():
    arg_spec = dict(
        principal=dict(type='str'),
        password=dict(type='str', no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        kdestroy_all=dict(type='bool'),
        cache_name=dict(type='str', fallback=(env_fallback, ['KRB5CCNAME'])),
        lifetime=dict(type='str'),
        start_time=dict(type='str'),
        renewable=dict(type='str'),
        forwardable=dict(type='bool'),
        proxiable=dict(type='bool'),
        address_restricted=dict(type='bool'),
        anonymous=dict(type='bool'),
        canonicalization=dict(type='bool'),
        enterprise=dict(type='bool'),
        renewal=dict(type='bool'),
        validate=dict(type='bool'),
        keytab=dict(type='bool'),
        keytab_path=dict(type='path'),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True,
        required_by={
            'keytab_path': 'keytab'
        },
        required_if=[
            ('state', 'present', ('password', 'keytab_path'), True),
        ],
    )

    state = module.params['state']
    kdestroy_all = module.params['kdestroy_all']

    keytab = IPAKeytab(module,
                       state=state,
                       kdestroy_all=kdestroy_all,
                       principal=module.params['principal'],
                       password=module.params['password'],
                       cache_name=module.params['cache_name'],
                       lifetime=module.params['lifetime'],
                       start_time=module.params['start_time'],
                       renewable=module.params['renewable'],
                       forwardable=module.params['forwardable'],
                       proxiable=module.params['proxiable'],
                       address_restricted=module.params['address_restricted'],
                       anonymous=module.params['anonymous'],
                       canonicalization=module.params['canonicalization'],
                       enterprise=module.params['enterprise'],
                       renewal=module.params['renewal'],
                       validate=module.params['validate'],
                       keytab=module.params['keytab'],
                       keytab_path=module.params['keytab_path'],
                       )

    changed = False
    if state == 'present':
        if not keytab.check_ticket_present():
            changed = True
            if not module.check_mode:
                keytab.exec_kinit()

    if state == 'absent':
        if kdestroy_all:
            changed = True
            if not module.check_mode:
                keytab.exec_kdestroy()
        if keytab.check_ticket_present():
            changed = True
            if not module.check_mode:
                keytab.exec_kdestroy()

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

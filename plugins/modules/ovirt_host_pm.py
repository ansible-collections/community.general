#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: ovirt_host_pm
short_description: Module to manage power management of hosts in oVirt/RHV
author: "Ondra Machacek (@machacekondra)"
description:
    - "Module to manage power management of hosts in oVirt/RHV."
options:
    name:
        description:
            - "Name of the host to manage."
        required: true
        aliases: ['host']
    state:
        description:
            - "Should the host be present/absent."
        choices: ['present', 'absent']
        default: present
    address:
        description:
            - "Address of the power management interface."
    username:
        description:
            - "Username to be used to connect to power management interface."
    password:
        description:
            - "Password of the user specified in C(username) parameter."
    type:
        description:
            - "Type of the power management. oVirt/RHV predefined values are I(drac5), I(ipmilan), I(rsa),
               I(bladecenter), I(alom), I(apc), I(apc_snmp), I(eps), I(wti), I(rsb), I(cisco_ucs),
               I(drac7), I(hpblade), I(ilo), I(ilo2), I(ilo3), I(ilo4), I(ilo_ssh),
               but user can have defined custom type."
    port:
        description:
            - "Power management interface port."
    options:
        description:
            - "Dictionary of additional fence agent options (including Power Management slot)."
            - "Additional information about options can be found at U(https://github.com/ClusterLabs/fence-agents/blob/master/doc/FenceAgentAPI.md)."
    encrypt_options:
        description:
            - "If I(true) options will be encrypted when send to agent."
        aliases: ['encrypt']
        type: bool
    order:
        description:
            - "Integer value specifying, by default it's added at the end."

extends_documentation_fragment:
- community.general.ovirt
'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

# Add fence agent to host 'myhost'
- ovirt_host_pm:
    name: myhost
    address: 1.2.3.4
    options:
      myoption1: x
      myoption2: y
    username: admin
    password: admin
    port: 3333
    type: ipmilan

# Add fence agent to host 'myhost' using 'slot' option
- ovirt_host_pm:
    name: myhost
    address: 1.2.3.4
    options:
      myoption1: x
      myoption2: y
      slot: myslot
    username: admin
    password: admin
    port: 3333
    type: ipmilan


# Remove ipmilan fence agent with address 1.2.3.4 on host 'myhost'
- ovirt_host_pm:
    state: absent
    name: myhost
    address: 1.2.3.4
    type: ipmilan
'''

RETURN = '''
id:
    description: ID of the agent which is managed
    returned: On success if agent is found.
    type: str
    sample: 7de90f31-222c-436c-a1ca-7e655bd5b60c
agent:
    description: "Dictionary of all the agent attributes. Agent attributes can be found on your oVirt/RHV instance
                  at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/agent."
    returned: On success if agent is found.
    type: dict
'''

import traceback

try:
    import ovirtsdk4.types as otypes
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ovirt import (
    BaseModule,
    check_sdk,
    create_connection,
    equal,
    ovirt_full_argument_spec,
    search_by_name,
)


class HostModule(BaseModule):
    def build_entity(self):
        return otypes.Host(
            power_management=otypes.PowerManagement(
                enabled=True,
            ),
        )

    def update_check(self, entity):
        return equal(True, entity.power_management.enabled)


class HostPmModule(BaseModule):

    def pre_create(self, entity):
        # Save the entity, so we know if Agent already existed
        self.entity = entity

    def build_entity(self):
        last = next((s for s in sorted([a.order for a in self._service.list()])), 0)
        order = self.param('order') if self.param('order') is not None else self.entity.order if self.entity else last + 1
        return otypes.Agent(
            address=self._module.params['address'],
            encrypt_options=self._module.params['encrypt_options'],
            options=[
                otypes.Option(
                    name=name,
                    value=value,
                ) for name, value in self._module.params['options'].items()
            ] if self._module.params['options'] else None,
            password=self._module.params['password'],
            port=self._module.params['port'],
            type=self._module.params['type'],
            username=self._module.params['username'],
            order=order,
        )

    def update_check(self, entity):
        def check_options():
            if self.param('options'):
                current = []
                if entity.options:
                    current = [(opt.name, str(opt.value)) for opt in entity.options]
                passed = [(k, str(v)) for k, v in self.param('options').items()]
                return sorted(current) == sorted(passed)
            return True

        return (
            check_options() and
            equal(self._module.params.get('address'), entity.address) and
            equal(self._module.params.get('encrypt_options'), entity.encrypt_options) and
            equal(self._module.params.get('username'), entity.username) and
            equal(self._module.params.get('port'), entity.port) and
            equal(self._module.params.get('type'), entity.type) and
            equal(self._module.params.get('order'), entity.order)
        )


def main():
    argument_spec = ovirt_full_argument_spec(
        state=dict(
            choices=['present', 'absent'],
            default='present',
        ),
        name=dict(default=None, required=True, aliases=['host']),
        address=dict(default=None),
        username=dict(default=None),
        password=dict(default=None, no_log=True),
        type=dict(default=None),
        port=dict(default=None, type='int'),
        order=dict(default=None, type='int'),
        options=dict(default=None, type='dict'),
        encrypt_options=dict(default=None, type='bool', aliases=['encrypt']),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        hosts_service = connection.system_service().hosts_service()
        host = search_by_name(hosts_service, module.params['name'])
        fence_agents_service = hosts_service.host_service(host.id).fence_agents_service()

        host_pm_module = HostPmModule(
            connection=connection,
            module=module,
            service=fence_agents_service,
        )
        host_module = HostModule(
            connection=connection,
            module=module,
            service=hosts_service,
        )

        state = module.params['state']
        if state == 'present':
            agent = host_pm_module.search_entity(
                search_params={
                    'address': module.params['address'],
                    'type': module.params['type'],
                }
            )
            ret = host_pm_module.create(entity=agent)

            # Enable Power Management, if it's not enabled:
            host_module.create(entity=host)
        elif state == 'absent':
            agent = host_pm_module.search_entity(
                search_params={
                    'address': module.params['address'],
                    'type': module.params['type'],
                }
            )
            ret = host_pm_module.remove(entity=agent)

        module.exit_json(**ret)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == "__main__":
    main()

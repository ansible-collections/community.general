#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, 2018 Red Hat, Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: ovirt_host_network
short_description: Module to manage host networks in oVirt/RHV
author: "Ondra Machacek (@machacekondra)"
description:
    - "Module to manage host networks in oVirt/RHV."
options:
    name:
        description:
            - "Name of the host to manage networks for."
        required: true
        aliases:
            - 'host'
    state:
        description:
            - "Should the host be present/absent."
        choices: ['present', 'absent']
        default: present
    bond:
        description:
            - "Dictionary describing network bond:"
        suboptions:
            name:
                description:
                    - Bond name.
            mode:
                description:
                    - Bonding mode.
            options:
                description:
                    - Bonding options.
            interfaces:
                description:
                    - List of interfaces to create a bond.
    interface:
        description:
            - "Name of the network interface where logical network should be attached."
    networks:
        description:
            - "List of dictionary describing networks to be attached to interface or bond:"
        suboptions:
            name:
                description:
                    - Name of the logical network to be assigned to bond or interface.
            boot_protocol:
                description:
                    - Boot protocol.
                choices: ['none', 'static', 'dhcp']
            address:
                description:
                    - IP address in case of I(static) boot protocol is used.
            netmask:
                description:
                    - Subnet mask in case of I(static) boot protocol is used.
            gateway:
                description:
                    - Gateway in case of I(static) boot protocol is used.
            version:
                description:
                    - IP version. Either v4 or v6. Default is v4.
            custom_properties:
                description:
                    - "Custom properties applied to the host network."
                    - "Custom properties is a list of dictionary which can have following values."
                suboptions:
                    name:
                        description:
                            - Name of custom property.
                    value:
                        description:
                            - Value of custom property.
    labels:
        description:
            - "List of names of the network label to be assigned to bond or interface."
    check:
        description:
            - "If I(true) verify connectivity between host and engine."
            - "Network configuration changes will be rolled back if connectivity between
               engine and the host is lost after changing network configuration."
        type: bool
    save:
        description:
            - "If I(true) network configuration will be persistent, otherwise it is temporary. Default I(true) since Ansible 2.8."
        type: bool
        default: True
    sync_networks:
        description:
            - "If I(true) all networks will be synchronized before modification"
        type: bool
        default: false

extends_documentation_fragment:
- community.general.ovirt
'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

# In all examples the durability of the configuration created is dependent on the 'save' option value:

# Create bond on eth0 and eth1 interface, and put 'myvlan' network on top of it and persist the new configuration:
- name: Bonds
  ovirt_host_network:
    name: myhost
    save: yes
    bond:
      name: bond0
      mode: 2
      interfaces:
        - eth1
        - eth2
    networks:
      - name: myvlan
        boot_protocol: static
        address: 1.2.3.4
        netmask: 255.255.255.0
        gateway: 1.2.3.4
        version: v4

# Create bond on eth1 and eth2 interface, specifying both mode and miimon:
- name: Bonds
  ovirt_host_network:
    name: myhost
    bond:
      name: bond0
      mode: 1
      options:
        miimon: 200
      interfaces:
        - eth1
        - eth2

# Remove bond0 bond from host interfaces:
- ovirt_host_network:
    state: absent
    name: myhost
    bond:
      name: bond0

# Assign myvlan1 and myvlan2 vlans to host eth0 interface:
- ovirt_host_network:
    name: myhost
    interface: eth0
    networks:
      - name: myvlan1
      - name: myvlan2

# Remove myvlan2 vlan from host eth0 interface:
- ovirt_host_network:
    state: absent
    name: myhost
    interface: eth0
    networks:
      - name: myvlan2

# Remove all networks/vlans from host eth0 interface:
- ovirt_host_network:
    state: absent
    name: myhost
    interface: eth0

# Add custom_properties to network:
- ovirt_host_network:
    name: myhost
    interface: eth0
    networks:
      - name: myvlan1
        custom_properties:
          - name: bridge_opts
            value: gc_timer=10
'''

RETURN = '''
id:
    description: ID of the host NIC which is managed
    returned: On success if host NIC is found.
    type: str
    sample: 7de90f31-222c-436c-a1ca-7e655bd5b60c
host_nic:
    description: "Dictionary of all the host NIC attributes. Host NIC attributes can be found on your oVirt/RHV instance
                  at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/host_nic."
    returned: On success if host NIC is found.
    type: dict
'''

import traceback

try:
    import ovirtsdk4.types as otypes
except ImportError:
    pass

from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ovirt import (
    BaseModule,
    check_sdk,
    create_connection,
    equal,
    get_dict_of_struct,
    get_entity,
    get_link_name,
    ovirt_full_argument_spec,
    search_by_name,
    engine_supported
)


def get_bond_options(mode, usr_opts):
    MIIMON_100 = dict(miimon='100')
    DEFAULT_MODE_OPTS = {
        '1': MIIMON_100,
        '2': MIIMON_100,
        '3': MIIMON_100,
        '4': dict(xmit_hash_policy='2', **MIIMON_100)
    }

    options = []
    if mode is None:
        return options

    def get_type_name(mode_number):
        """
        We need to maintain this type strings, for the __compare_options method,
        for easier comparision.
        """
        modes = [
            'Active-Backup',
            'Load balance (balance-xor)',
            None,
            'Dynamic link aggregation (802.3ad)',
        ]
        if (not 0 < mode_number <= len(modes)):
            return None
        return modes[mode_number - 1]

    try:
        mode_number = int(mode)
    except ValueError:
        raise Exception('Bond mode must be a number.')

    options.append(
        otypes.Option(
            name='mode',
            type=get_type_name(mode_number),
            value=str(mode_number)
        )
    )

    opts_dict = DEFAULT_MODE_OPTS.get(str(mode), {})
    if usr_opts is not None:
        opts_dict.update(**usr_opts)

    options.extend(
        [otypes.Option(name=opt, value=str(value))
         for opt, value in six.iteritems(opts_dict)]
    )
    return options


class HostNetworksModule(BaseModule):

    def __compare_options(self, new_options, old_options):
        return sorted((get_dict_of_struct(opt) for opt in new_options),
                      key=lambda x: x["name"]) != sorted((get_dict_of_struct(opt) for opt in old_options),
                                                         key=lambda x: x["name"])

    def build_entity(self):
        return otypes.Host()

    def update_custom_properties(self, attachments_service, attachment, network):
        if network.get('custom_properties'):
            current = []
            if attachment.properties:
                current = [(cp.name, str(cp.value)) for cp in attachment.properties]
            passed = [(cp.get('name'), str(cp.get('value'))) for cp in network.get('custom_properties') if cp]
            if sorted(current) != sorted(passed):
                attachment.properties = [
                    otypes.Property(
                        name=prop.get('name'),
                        value=prop.get('value')
                    ) for prop in network.get('custom_properties')
                ]
                if not self._module.check_mode:
                    attachments_service.service(attachment.id).update(attachment)
                self.changed = True

    def update_address(self, attachments_service, attachment, network):
        # Check if there is any change in address assignments and
        # update it if needed:
        for ip in attachment.ip_address_assignments:
            if str(ip.ip.version) == network.get('version', 'v4'):
                changed = False
                if not equal(network.get('boot_protocol'), str(ip.assignment_method)):
                    ip.assignment_method = otypes.BootProtocol(network.get('boot_protocol'))
                    changed = True
                if not equal(network.get('address'), ip.ip.address):
                    ip.ip.address = network.get('address')
                    changed = True
                if not equal(network.get('gateway'), ip.ip.gateway):
                    ip.ip.gateway = network.get('gateway')
                    changed = True
                if not equal(network.get('netmask'), ip.ip.netmask):
                    ip.ip.netmask = network.get('netmask')
                    changed = True

                if changed:
                    if not self._module.check_mode:
                        attachments_service.service(attachment.id).update(attachment)
                    self.changed = True
                    break

    def has_update(self, nic_service):
        update = False
        bond = self._module.params['bond']
        networks = self._module.params['networks']
        labels = self._module.params['labels']
        nic = get_entity(nic_service)

        if nic is None:
            return update

        # Check if bond configuration should be updated:
        if bond:
            update = self.__compare_options(get_bond_options(bond.get('mode'), bond.get('options')), getattr(nic.bonding, 'options', []))
            update = update or not equal(
                sorted(bond.get('interfaces')) if bond.get('interfaces') else None,
                sorted(get_link_name(self._connection, s) for s in nic.bonding.slaves)
            )

        # Check if labels need to be updated on interface/bond:
        if labels:
            net_labels = nic_service.network_labels_service().list()
            # If any labels which user passed aren't assigned, relabel the interface:
            if sorted(labels) != sorted([lbl.id for lbl in net_labels]):
                return True

        if not networks:
            return update

        # Check if networks attachments configuration should be updated:
        attachments_service = nic_service.network_attachments_service()
        network_names = [network.get('name') for network in networks]

        attachments = {}
        for attachment in attachments_service.list():
            name = get_link_name(self._connection, attachment.network)
            if name in network_names:
                attachments[name] = attachment

        for network in networks:
            attachment = attachments.get(network.get('name'))
            # If attachment don't exists, we need to create it:
            if attachment is None:
                return True
            self.update_custom_properties(attachments_service, attachment, network)
            self.update_address(attachments_service, attachment, network)

        return update

    def _action_save_configuration(self, entity):
        if not self._module.check_mode:
            self._service.service(entity.id).commit_net_config()
        self.changed = True


def needs_sync(nics_service):
    nics = nics_service.list()
    for nic in nics:
        nic_service = nics_service.nic_service(nic.id)
        for network_attachment_service in nic_service.network_attachments_service().list():
            if not network_attachment_service.in_sync:
                return True
    return False


def main():
    argument_spec = ovirt_full_argument_spec(
        state=dict(
            choices=['present', 'absent'],
            default='present',
        ),
        name=dict(aliases=['host'], required=True),
        bond=dict(default=None, type='dict'),
        interface=dict(default=None),
        networks=dict(default=None, type='list'),
        labels=dict(default=None, type='list'),
        check=dict(default=None, type='bool'),
        save=dict(default=True, type='bool'),
        sync_networks=dict(default=False, type='bool'),
    )
    module = AnsibleModule(argument_spec=argument_spec)

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        hosts_service = connection.system_service().hosts_service()
        host_networks_module = HostNetworksModule(
            connection=connection,
            module=module,
            service=hosts_service,
        )

        host = host_networks_module.search_entity()
        if host is None:
            raise Exception("Host '%s' was not found." % module.params['name'])

        bond = module.params['bond']
        interface = module.params['interface']
        networks = module.params['networks']
        labels = module.params['labels']
        nic_name = bond.get('name') if bond else module.params['interface']

        host_service = hosts_service.host_service(host.id)
        nics_service = host_service.nics_service()
        nic = search_by_name(nics_service, nic_name)

        if module.params["sync_networks"]:
            if needs_sync(nics_service):
                if not module.check_mode:
                    host_service.sync_all_networks()
                host_networks_module.changed = True

        network_names = [network['name'] for network in networks or []]
        state = module.params['state']

        if (
            state == 'present' and
            (nic is None or host_networks_module.has_update(nics_service.service(nic.id)))
        ):
            # Remove networks which are attached to different interface then user want:
            attachments_service = host_service.network_attachments_service()

            # Append attachment ID to network if needs update:
            for a in attachments_service.list():
                current_network_name = get_link_name(connection, a.network)
                if current_network_name in network_names:
                    for n in networks:
                        if n['name'] == current_network_name:
                            n['id'] = a.id

            # Check if we have to break some bonds:
            removed_bonds = []
            if nic is not None:
                for host_nic in nics_service.list():
                    if host_nic.bonding and nic.id in [slave.id for slave in host_nic.bonding.slaves]:
                        removed_bonds.append(otypes.HostNic(id=host_nic.id))

            # Assign the networks:
            setup_params = dict(
                entity=host,
                action='setup_networks',
                check_connectivity=module.params['check'],
                removed_bonds=removed_bonds if removed_bonds else None,
                modified_bonds=[
                    otypes.HostNic(
                        name=bond.get('name'),
                        bonding=otypes.Bonding(
                            options=get_bond_options(bond.get('mode'), bond.get('options')),
                            slaves=[
                                otypes.HostNic(name=i) for i in bond.get('interfaces', [])
                            ],
                        ),
                    ),
                ] if bond else None,
                modified_labels=[
                    otypes.NetworkLabel(
                        id=str(name),
                        host_nic=otypes.HostNic(
                            name=bond.get('name') if bond else interface
                        ),
                    ) for name in labels
                ] if labels else None,
                modified_network_attachments=[
                    otypes.NetworkAttachment(
                        id=network.get('id'),
                        network=otypes.Network(
                            name=network['name']
                        ) if network['name'] else None,
                        host_nic=otypes.HostNic(
                            name=bond.get('name') if bond else interface
                        ),
                        ip_address_assignments=[
                            otypes.IpAddressAssignment(
                                assignment_method=otypes.BootProtocol(
                                    network.get('boot_protocol', 'none')
                                ),
                                ip=otypes.Ip(
                                    address=network.get('address'),
                                    gateway=network.get('gateway'),
                                    netmask=network.get('netmask'),
                                    version=otypes.IpVersion(
                                        network.get('version')
                                    ) if network.get('version') else None,
                                ),
                            ),
                        ],
                        properties=[
                            otypes.Property(
                                name=prop.get('name'),
                                value=prop.get('value')
                            ) for prop in network.get('custom_properties')
                        ]
                    ) for network in networks
                ] if networks else None,
            )
            if engine_supported(connection, '4.3'):
                setup_params['commit_on_success'] = module.params['save']
            elif module.params['save']:
                setup_params['post_action'] = host_networks_module._action_save_configuration
            host_networks_module.action(**setup_params)
        elif state == 'absent' and nic:
            attachments = []
            nic_service = nics_service.nic_service(nic.id)

            attached_labels = set([str(lbl.id) for lbl in nic_service.network_labels_service().list()])
            if networks:
                attachments_service = nic_service.network_attachments_service()
                attachments = attachments_service.list()
                attachments = [
                    attachment for attachment in attachments
                    if get_link_name(connection, attachment.network) in network_names
                ]

            # Remove unmanaged networks:
            unmanaged_networks_service = host_service.unmanaged_networks_service()
            unmanaged_networks = [(u.id, u.name) for u in unmanaged_networks_service.list()]
            for net_id, net_name in unmanaged_networks:
                if net_name in network_names:
                    if not module.check_mode:
                        unmanaged_networks_service.unmanaged_network_service(net_id).remove()
                    host_networks_module.changed = True

            # Need to check if there are any labels to be removed, as backend fail
            # if we try to send remove non existing label, for bond and attachments it's OK:
            if (labels and set(labels).intersection(attached_labels)) or bond or attachments:
                setup_params = dict(
                    entity=host,
                    action='setup_networks',
                    check_connectivity=module.params['check'],
                    removed_bonds=[
                        otypes.HostNic(
                            name=bond.get('name'),
                        ),
                    ] if bond else None,
                    removed_labels=[
                        otypes.NetworkLabel(id=str(name)) for name in labels
                    ] if labels else None,
                    removed_network_attachments=attachments if attachments else None,
                )
                if engine_supported(connection, '4.3'):
                    setup_params['commit_on_success'] = module.params['save']
                elif module.params['save']:
                    setup_params['post_action'] = host_networks_module._action_save_configuration
                host_networks_module.action(**setup_params)

        nic = search_by_name(nics_service, nic_name)
        module.exit_json(**{
            'changed': host_networks_module.changed,
            'id': nic.id if nic else None,
            'host_nic': get_dict_of_struct(nic),
        })
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == "__main__":
    main()

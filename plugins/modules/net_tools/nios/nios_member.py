#!/usr/bin/python
# Copyright (c) 2018 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nios_member
author: "Krishna Vasudevan (@krisvasudevan)"
short_description: Configure Infoblox NIOS members
description:
  - Adds and/or removes Infoblox NIOS servers.  This module manages NIOS C(member) objects using the Infoblox WAPI interface over REST.
requirements:
  - infoblox-client
extends_documentation_fragment:
- community.general.nios

options:
  host_name:
    description:
      - Specifies the host name of the member to either add or remove from
        the NIOS instance.
    required: true
    aliases:
      - name
    type: str
  vip_setting:
    description:
      - Configures the network settings for the grid member.
    type: list
    elements: dict
    suboptions:
      address:
        description:
          - The IPv4 Address of the Grid Member
        type: str
      subnet_mask:
        description:
          - The subnet mask for the Grid Member
        type: str
      gateway:
        description:
          - The default gateway for the Grid Member
        type: str
  ipv6_setting:
    description:
      - Configures the IPv6 settings for the grid member.
    type: list
    elements: dict
    suboptions:
      virtual_ip:
        description:
          - The IPv6 Address of the Grid Member
        type: str
      cidr_prefix:
        description:
          - The IPv6 CIDR prefix for the Grid Member
        type: int
      gateway:
        description:
          - The gateway address for the Grid Member
        type: str
  config_addr_type:
    description:
      - Address configuration type (IPV4/IPV6/BOTH)
    default: IPV4
    type: str
  comment:
    description:
      - A descriptive comment of the Grid member.
    type: str
  extattrs:
    description:
      - Extensible attributes associated with the object.
    type: dict
  enable_ha:
    description:
      - If set to True, the member has two physical nodes (HA pair).
    type: bool
    default: false
  router_id:
    description:
      - Virtual router identifier. Provide this ID if "ha_enabled" is set to "true". This is a unique VRID number (from 1 to 255) for the local subnet.
    type: int
  lan2_enabled:
    description:
      - When set to "true", the LAN2 port is enabled as an independent port or as a port for failover purposes.
    type: bool
    default: false
  lan2_port_setting:
    description:
      - Settings for the Grid member LAN2 port if 'lan2_enabled' is set to "true".
    type: list
    elements: dict
    suboptions:
      enabled:
        description:
          - If set to True, then it has its own IP settings.
        type: bool
      network_setting:
        description:
          - If the 'enable' field is set to True, this defines IPv4 network settings for LAN2.
        type: list
        elements: dict
        suboptions:
          address:
            description:
              - The IPv4 Address of LAN2
            type: str
          subnet_mask:
            description:
              - The subnet mask of LAN2
            type: str
          gateway:
            description:
              - The default gateway of LAN2
            type: str
      v6_network_setting:
        description:
          - If the 'enable' field is set to True, this defines IPv6 network settings for LAN2.
        type: list
        elements: dict
        suboptions:
          virtual_ip:
            description:
              - The IPv6 Address of LAN2
            type: str
          cidr_prefix:
            description:
              - The IPv6 CIDR prefix of LAN2
            type: int
          gateway:
            description:
              - The gateway address of LAN2
            type: str
  platform:
    description:
      - Configures the Hardware Platform.
    default: INFOBLOX
    type: str
  node_info:
    description:
      - Configures the node information list with detailed status report on the operations of the Grid Member.
    type: list
    elements: dict
    suboptions:
      lan2_physical_setting:
        description:
          - Physical port settings for the LAN2 interface.
        type: list
        elements: dict
        suboptions:
          auto_port_setting_enabled:
            description:
              - Enable or disalbe the auto port setting.
            type: bool
          duplex:
            description:
              - The port duplex; if speed is 1000, duplex must be FULL.
            type: str
          speed:
            description:
              - The port speed; if speed is 1000, duplex is FULL.
            type: str
      lan_ha_port_setting:
        description:
          - LAN/HA port settings for the node.
        type: list
        elements: dict
        suboptions:
          ha_ip_address:
            description:
              - HA IP address.
            type: str
          ha_port_setting:
            description:
              - Physical port settings for the HA interface.
            type: list
            elements: dict
            suboptions:
              auto_port_setting_enabled:
                description:
                  - Enable or disalbe the auto port setting.
                type: bool
              duplex:
                description:
                  - The port duplex; if speed is 1000, duplex must be FULL.
                type: str
              speed:
                description:
                  - The port speed; if speed is 1000, duplex is FULL.
                type: str
          lan_port_setting:
            description:
              - Physical port settings for the LAN interface.
            type: list
            elements: dict
            suboptions:
              auto_port_setting_enabled:
                description:
                  - Enable or disalbe the auto port setting.
                type: bool
              duplex:
                description:
                  - The port duplex; if speed is 1000, duplex must be FULL.
                type: str
              speed:
                description:
                  - The port speed; if speed is 1000, duplex is FULL.
                type: str
          mgmt_ipv6addr:
            description:
              - Public IPv6 address for the LAN1 interface.
            type: str
          mgmt_lan:
            description:
              - Public IPv4 address for the LAN1 interface.
            type: str
      mgmt_network_setting:
        description:
          - Network settings for the MGMT port of the node.
        type: list
        elements: dict
        suboptions:
          address:
            description:
              - The IPv4 Address of MGMT
            type: str
          subnet_mask:
            description:
              - The subnet mask of MGMT
            type: str
          gateway:
            description:
              - The default gateway of MGMT
            type: str
      v6_mgmt_network_setting:
        description:
          - The network settings for the IPv6 MGMT port of the node.
        type: list
        elements: dict
        suboptions:
          virtual_ip:
            description:
              - The IPv6 Address of MGMT
            type: str
          cidr_prefix:
            description:
              - The IPv6 CIDR prefix of MGMT
            type: int
          gateway:
            description:
              - The gateway address of MGMT
            type: str
  mgmt_port_setting:
    description:
      - Settings for the member MGMT port.
    type: list
    elements: dict
    suboptions:
      enabled:
        description:
          - Determines if MGMT port settings should be enabled.
        type: bool
      security_access_enabled:
        description:
          - Determines if security access on the MGMT port is enabled or not.
        type: bool
      vpn_enabled:
        description:
          - Determines if VPN on the MGMT port is enabled or not.
        type: bool
  upgrade_group:
    description:
      - The name of the upgrade group to which this Grid member belongs.
    default: Default
    type: str
  use_syslog_proxy_setting:
    description:
      - Use flag for external_syslog_server_enable , syslog_servers, syslog_proxy_setting, syslog_size
    type: bool
  external_syslog_server_enable:
    description:
      - Determines if external syslog servers should be enabled
    type: bool
  syslog_servers:
    description:
      - The list of external syslog servers.
    type: list
    elements: dict
    suboptions:
      address:
        description:
          - The server address.
        type: str
      category_list:
        description:
          - The list of all syslog logging categories.
        type: list
        elements: str
      connection_type:
        description:
          - The connection type for communicating with this server.(STCP/TCP?UDP)
        default: UDP
        type: str
      local_interface:
        description:
          - The local interface through which the appliance sends syslog messages to the syslog server.(ANY/LAN/MGMT)
        default: ANY
        type: str
      message_node_id:
        description:
          - Identify the node in the syslog message. (HOSTNAME/IP_HOSTNAME/LAN/MGMT)
        default: LAN
        type: str
      message_source:
        description:
          - The source of syslog messages to be sent to the external syslog server.
        default: ANY
        type: str
      only_category_list:
        description:
          - The list of selected syslog logging categories. The appliance forwards syslog messages that belong to the selected categories.
        type: bool
      port:
        description:
          - The port this server listens on.
        default: 514
        type: int
      severity:
        description:
          - The severity filter. The appliance sends log messages of the specified severity and above to the external syslog server.
        default: DEBUG
        type: str
  pre_provisioning:
    description:
      - Pre-provisioning information.
    type: list
    elements: dict
    suboptions:
      hardware_info:
        description:
          - An array of structures that describe the hardware being pre-provisioned.
        type: list
        elements: dict
        suboptions:
          hwmodel:
            description:
              - Hardware model
            type: str
          hwtype:
            description:
              - Hardware type.
            type: str
      licenses:
        description:
          - An array of license types.
        type: list
        elements: str
  create_token:
    description:
      - Flag for initiating a create token request for pre-provisioned members.
    type: bool
    default: False
  state:
    description:
      - Configures the intended state of the instance of the object on
        the NIOS server.  When this value is set to C(present), the object
        is configured on the device and when this value is set to C(absent)
        the value is removed (if necessary) from the device.
    default: present
    choices:
      - present
      - absent
    type: str
'''

EXAMPLES = '''
- name: Add a member to the grid with IPv4 address
  community.general.nios_member:
    host_name: member01.localdomain
    vip_setting:
      - address: 192.168.1.100
        subnet_mask: 255.255.255.0
        gateway: 192.168.1.1
    config_addr_type: IPV4
    platform: VNIOS
    comment: "Created by Ansible"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Add a HA member to the grid
  community.general.nios_member:
    host_name: memberha.localdomain
    vip_setting:
      - address: 192.168.1.100
        subnet_mask: 255.255.255.0
        gateway: 192.168.1.1
    config_addr_type: IPV4
    platform: VNIOS
    enable_ha: true
    router_id: 150
    node_info:
      - lan_ha_port_setting:
         - ha_ip_address: 192.168.1.70
           mgmt_lan: 192.168.1.80
      - lan_ha_port_setting:
         - ha_ip_address: 192.168.1.71
           mgmt_lan: 192.168.1.81
    comment: "Created by Ansible"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Update the member with pre-provisioning details specified
  community.general.nios_member:
    name: member01.localdomain
    pre_provisioning:
      - hardware_info:
         - hwmodel: IB-VM-820
           hwtype: IB-VNIOS
        licenses:
         - dns
         - dhcp
         - enterprise
         - vnios
    comment: "Updated by Ansible"
    state: present
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
- name: Remove the member
  community.general.nios_member:
    name: member01.localdomain
    state: absent
    provider:
      host: "{{ inventory_hostname_short }}"
      username: admin
      password: admin
  connection: local
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import WapiModule
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import NIOS_MEMBER
from ansible_collections.community.general.plugins.module_utils.net_tools.nios.api import normalize_ib_spec


def main():
    ''' Main entry point for module execution
    '''
    ipv4_spec = dict(
        address=dict(),
        subnet_mask=dict(),
        gateway=dict(),
    )

    ipv6_spec = dict(
        virtual_ip=dict(),
        cidr_prefix=dict(type='int'),
        gateway=dict(),
    )

    port_spec = dict(
        auto_port_setting_enabled=dict(type='bool'),
        duplex=dict(),
        speed=dict(),
    )

    lan2_port_spec = dict(
        enabled=dict(type='bool'),
        network_setting=dict(type='list', elements='dict', options=ipv4_spec),
        v6_network_setting=dict(type='list', elements='dict', options=ipv6_spec),
    )

    ha_port_spec = dict(
        ha_ip_address=dict(),
        ha_port_setting=dict(type='list', elements='dict', options=port_spec),
        lan_port_setting=dict(type='list', elements='dict', options=port_spec),
        mgmt_lan=dict(),
        mgmt_ipv6addr=dict(),
    )

    node_spec = dict(
        lan2_physical_setting=dict(type='list', elements='dict', options=port_spec),
        lan_ha_port_setting=dict(type='list', elements='dict', options=ha_port_spec),
        mgmt_network_setting=dict(type='list', elements='dict', options=ipv4_spec),
        v6_mgmt_network_setting=dict(type='list', elements='dict', options=ipv6_spec),
    )

    mgmt_port_spec = dict(
        enabled=dict(type='bool'),
        security_access_enabled=dict(type='bool'),
        vpn_enabled=dict(type='bool'),
    )

    syslog_spec = dict(
        address=dict(),
        category_list=dict(type='list', elements='str'),
        connection_type=dict(default='UDP'),
        local_interface=dict(default='ANY'),
        message_node_id=dict(default='LAN'),
        message_source=dict(default='ANY'),
        only_category_list=dict(type='bool'),
        port=dict(type='int', default=514),
        severity=dict(default='DEBUG'),
    )

    hw_spec = dict(
        hwmodel=dict(),
        hwtype=dict(),
    )

    pre_prov_spec = dict(
        hardware_info=dict(type='list', elements='dict', options=hw_spec),
        licenses=dict(type='list', elements='str'),
    )

    ib_spec = dict(
        host_name=dict(required=True, aliases=['name'], ib_req=True),
        vip_setting=dict(type='list', elements='dict', options=ipv4_spec),
        ipv6_setting=dict(type='list', elements='dict', options=ipv6_spec),
        config_addr_type=dict(default='IPV4'),
        comment=dict(),
        enable_ha=dict(type='bool', default=False),
        router_id=dict(type='int'),
        lan2_enabled=dict(type='bool', default=False),
        lan2_port_setting=dict(type='list', elements='dict', options=lan2_port_spec),
        platform=dict(default='INFOBLOX'),
        node_info=dict(type='list', elements='dict', options=node_spec),
        mgmt_port_setting=dict(type='list', elements='dict', options=mgmt_port_spec),
        upgrade_group=dict(default='Default'),
        use_syslog_proxy_setting=dict(type='bool'),
        external_syslog_server_enable=dict(type='bool'),
        syslog_servers=dict(type='list', elements='dict', options=syslog_spec),
        pre_provisioning=dict(type='list', elements='dict', options=pre_prov_spec),
        extattrs=dict(type='dict'),
        create_token=dict(type='bool', default=False),
    )

    argument_spec = dict(
        provider=dict(required=True),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(normalize_ib_spec(ib_spec))
    argument_spec.update(WapiModule.provider_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    wapi = WapiModule(module)
    result = wapi.run(NIOS_MEMBER, ib_spec)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

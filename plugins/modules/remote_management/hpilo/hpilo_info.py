#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2012 Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: hpilo_info
author: Dag Wieers (@dagwieers)
short_description: Gather information through an HP iLO interface
description:
- This module gathers information on a specific system using its HP iLO interface.
  These information includes hardware and network related information useful
  for provisioning (e.g. macaddress, uuid).
- This module requires the C(hpilo) python module.
- This module was called C(hpilo_facts) before Ansible 2.9, returning C(ansible_facts).
  Note that the M(community.general.hpilo_info) module no longer returns C(ansible_facts)!
options:
  host:
    description:
    - The HP iLO hostname/address that is linked to the physical system.
    required: true
  login:
    description:
    - The login name to authenticate to the HP iLO interface.
    default: Administrator
  password:
    description:
    - The password to authenticate to the HP iLO interface.
    default: admin
  ssl_version:
    description:
      - Change the ssl_version used.
    default: TLSv1
    choices: [ "SSLv3", "SSLv23", "TLSv1", "TLSv1_1", "TLSv1_2" ]
requirements:
- hpilo
notes:
- This module ought to be run from a system that can access the HP iLO
  interface directly, either by using C(local_action) or using C(delegate_to).
'''

EXAMPLES = r'''
- name: Gather facts from a HP iLO interface only if the system is an HP server
  community.general.hpilo_info:
    host: YOUR_ILO_ADDRESS
    login: YOUR_ILO_LOGIN
    password: YOUR_ILO_PASSWORD
  when: cmdb_hwmodel.startswith('HP ')
  delegate_to: localhost
  register: results

- ansible.builtin.fail:
    msg: 'CMDB serial ({{ cmdb_serialno }}) does not match hardware serial ({{ results.hw_system_serial }}) !'
  when: cmdb_serialno != results.hw_system_serial
'''

RETURN = r'''
# Typical output of HP iLO_info for a physical system
hw_bios_date:
    description: BIOS date
    returned: always
    type: str
    sample: 05/05/2011

hw_bios_version:
    description: BIOS version
    returned: always
    type: str
    sample: P68

hw_ethX:
    description: Interface information (for each interface)
    returned: always
    type: dict
    sample:
      - macaddress: 00:11:22:33:44:55
        macaddress_dash: 00-11-22-33-44-55

hw_eth_ilo:
    description: Interface information (for the iLO network interface)
    returned: always
    type: dict
    sample:
      - macaddress: 00:11:22:33:44:BA
        macaddress_dash: 00-11-22-33-44-BA

hw_product_name:
    description: Product name
    returned: always
    type: str
    sample: ProLiant DL360 G7

hw_product_uuid:
    description: Product UUID
    returned: always
    type: str
    sample: ef50bac8-2845-40ff-81d9-675315501dac

hw_system_serial:
    description: System serial number
    returned: always
    type: str
    sample: ABC12345D6

hw_uuid:
    description: Hardware UUID
    returned: always
    type: str
    sample: 123456ABC78901D2

host_power_status:
    description:
      - Power status of host.
      - Will be one of C(ON), C(OFF) and C(UNKNOWN).
    returned: always
    type: str
    sample: ON
    version_added: 3.5.0

server_name:
    description: The server name
    returned: always
    type: str
    sample: milo.company.com
    version_added: 4.1.0

snmp_im_settings:
    description: The system serial number
    returned: always
    type: dict
    sample: 
      snmp_im_settings:
        agentless_management_enable: true
        cim_security_mask: 3
        cold_start_trap_broadcast: true
        os_traps: true
        rib_traps: true
        snmp_access: Enable
        snmp_address_1: ''
        snmp_address_1_rocommunity: ''
        snmp_address_1_trapcommunity: ''
        snmp_address_2: ''
        snmp_address_2_rocommunity: ''
        snmp_address_2_trapcommunity: ''
        snmp_address_3: ''
        snmp_address_3_rocommunity: ''
        snmp_address_3_trapcommunity: ''
        snmp_passthrough_status: false
        snmp_port: 161
        snmp_sys_contact: ''
        snmp_sys_location: ''
        snmp_system_role: ''
        snmp_system_role_detail: ''
        snmp_trap_port: 162
        snmp_v1_traps: true
        snmp_v3_engine_id: '0x800000E804435A3137323030314139'
        trap_source_identifier: iLO Hostname
        web_agent_ip_address: milo.company.com
    version_added: 4.1.0

network_settings:
    description: Retrieve information about ilo network
    returned: always
    type: dict
    sample: 
      network_settings:
        dhcp_dns_server: false
        dhcp_domain_name: false
        dhcp_enable: false
        dhcp_gateway: false
        dhcp_sntp_settings: false
        dhcp_static_route: false
        dhcp_wins_server: false
        dns_name: ilo
        domain_name: ''
        enable_nic: true
        full_duplex: Automatic
        gateway_ip_address: 10.1.2.254
        ilo_nic_auto_delay: 90
        ilo_nic_auto_select: DISABLED
        ilo_nic_auto_snp_scan: 0
        ilo_nic_fail_over: DISABLED
        ilo_nic_fail_over_delay: 300
        ip_address: 10.1.2.3
        mac_address: f4:03:43:ff:1d:63
        nic_speed: Automatic
        ping_gateway: true
        prim_dns_server: 8.8.8.8
        prim_wins_server: 0.0.0.0
        reg_ddns_server: true
        reg_wins_server: true
        sec_dns_server: 9.9.9.9
        sec_wins_server: 0.0.0.0
        shared_network_port: LOM
        snp_port: 1
        sntp_server1: fr.pool.ntp.org
        sntp_server2: ''
        speed_autoselect: true
        static_route_1:
            dest: 0.0.0.0
            gateway: 0.0.0.0
            mask: 0.0.0.0
        static_route_2:
            dest: 0.0.0.0
            gateway: 0.0.0.0
            mask: 0.0.0.0
        static_route_3:
            dest: 0.0.0.0
            gateway: 0.0.0.0
            mask: 0.0.0.0
        subnet_mask: 255.255.255.0
        ter_dns_server: 0.0.0.0
        timezone: Europe/Madrid
        vlan_enabled: false
        vlan_id: 0
    version_added: 4.1.0


global_settings:
    description: Global settings about ilo
    returned: always
    type: dict
    sample: 
      global_settings:
        alertmail_email_address: ''
        alertmail_enable: false
        alertmail_sender_domain: ''
        alertmail_smtp_port: 25
        alertmail_smtp_server: ''
        authentication_failure_delay_secs: 10
        authentication_failure_logging: Enabled-every 3rd failure
        authentication_failures_before_delay: 1
        enforce_aes: false
        f8_login_required: false
        f8_prompt_enabled: true
        http_port: 80
        https_port: 443
        ilo_funct_enabled: true
        ipmi_dcmi_over_lan_enabled: true
        ipmi_dcmi_over_lan_port: 623
        lock_configuration: false
        min_password: 8
        propagate_time_to_host: true
        rbsu_post_ip: true
        remote_console_port: 17990
        remote_syslog_enable: false
        remote_syslog_port: 514
        remote_syslog_server_address: ''
        session_timeout: 120
        snmp_access_enabled: true
        snmp_port: 161
        snmp_trap_port: 162
        ssh_port: 22
        ssh_status: true
        virtual_media_port: 17988
        vsp_log_enable: false
    version_added: 4.1.0


supported_boot_mode:
    description: Boot mode supported
    returned: always
    type: str
    sample: LEGACY_UEFI
    version_added: 4.1.0
    
one_time_boot:
    description: The one time boot
    returned: always
    type: str
    sample: normal
    version_added: 4.1.0

pending_boot_mode:
    description: The pending boot mode
    returned: always
    type: str
    sample: UEFI
    version_added: 4.1.0

persistent_boot:
    description: The persistant boot
    returned: always
    type: list
    elements: ... (fill type in here) ...
    sample: 
      persistent_boot:
        -   - Boot0013
            - VMware ESXi
        -   - Boot000E
            - Windows Boot Manager
        -   - Boot000D
            - Assisted_Installation
        -   - Boot0008
            - Generic USB Boot
        -   - Boot0009
            - 'Internal SD Card 1 : Generic Ultra Fast Media Reader'
        -   - Boot000B
            - 'Rear USB 1 : Kingston DataTraveler 3.0'
    version_added: 4.1.0

current_boot_mode:
    description: The current boot mode
    returned: always
    type: str
    sample: UEFI
    version_added: 4.1.0

security_msg:
    description: Security msg if enabled
    returned: always
    type: dict
    sample: 
      security_msg:
        security_msg: Disabled
        security_msg_text: ''
    version_added: 4.1.0

all_licenses:
    description: Display list of dict about the licences (expired or not)
    returned: always
    type: list
    elements: dict
    sample: 
    -   license_class: FQL
        license_install_date: Sun Mar 12 16:44:03 1988
        license_key: XXXX-XXXX-XXXX-XXXX-XXXX
        license_type: iLO Advanced
    version_added: 4.1.0

all_user_info:
    description: Return detail actual connected user
    returned: always
    type: dict
    sample: 
      Administrator:
        admin_priv: true
        config_ilo_priv: true
        remote_cons_priv: true
        reset_server_priv: true
        user_login: Administrator
        user_name: Administrator
        virtual_media_priv: true
    version_added: 4.1.0

all_users:
    description: Display all user in ILO
    returned: always
    type: list
    sample: 
    - Administrator
    version_added: 4.1.0
    
'''

import re
import traceback
import warnings

HPILO_IMP_ERR = None
try:
    import hpilo
    HAS_HPILO = True
except ImportError:
    HPILO_IMP_ERR = traceback.format_exc()
    HAS_HPILO = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


# Suppress warnings from hpilo
warnings.simplefilter('ignore')


def parse_flat_interface(entry, non_numeric='hw_eth_ilo'):
    try:
        infoname = 'hw_eth' + str(int(entry['Port']) - 1)
    except Exception:
        infoname = non_numeric

    info = {
        'macaddress': entry['MAC'].replace('-', ':'),
        'macaddress_dash': entry['MAC']
    }
    return (infoname, info)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            login=dict(type='str', default='Administrator'),
            password=dict(type='str', default='admin', no_log=True),
            ssl_version=dict(type='str', default='TLSv1', choices=['SSLv3', 'SSLv23', 'TLSv1', 'TLSv1_1', 'TLSv1_2']),
        ),
        supports_check_mode=True,
    )

    if not HAS_HPILO:
        module.fail_json(msg=missing_required_lib('python-hpilo'), exception=HPILO_IMP_ERR)

    host = module.params['host']
    login = module.params['login']
    password = module.params['password']
    ssl_version = getattr(hpilo.ssl, 'PROTOCOL_' + module.params.get('ssl_version').upper().replace('V', 'v'))

    ilo = hpilo.Ilo(host, login=login, password=password, ssl_version=ssl_version)

    info = {
        'module_hw': True,
    }

    # TODO: Count number of CPUs, DIMMs and total memory
    try:
        data = ilo.get_host_data()
        power_state = ilo.get_host_power_status()
    except hpilo.IloCommunicationError as e:
        module.fail_json(msg=to_native(e))

    for entry in data:
        if 'type' not in entry:
            continue
        elif entry['type'] == 0:  # BIOS Information
            info['hw_bios_version'] = entry['Family']
            info['hw_bios_date'] = entry['Date']
        elif entry['type'] == 1:  # System Information
            info['hw_uuid'] = entry['UUID']
            info['hw_system_serial'] = entry['Serial Number'].rstrip()
            info['hw_product_name'] = entry['Product Name']
            info['hw_product_uuid'] = entry['cUUID']
        elif entry['type'] == 209:  # Embedded NIC MAC Assignment
            if 'fields' in entry:
                for (name, value) in [(e['name'], e['value']) for e in entry['fields']]:
                    if name.startswith('Port'):
                        try:
                            infoname = 'hw_eth' + str(int(value) - 1)
                        except Exception:
                            infoname = 'hw_eth_ilo'
                    elif name.startswith('MAC'):
                        info[infoname] = {
                            'macaddress': value.replace('-', ':'),
                            'macaddress_dash': value
                        }
            else:
                (infoname, entry_info) = parse_flat_interface(entry, 'hw_eth_ilo')
                info[infoname] = entry_info
        elif entry['type'] == 209:  # HPQ NIC iSCSI MAC Info
            for (name, value) in [(e['name'], e['value']) for e in entry['fields']]:
                if name.startswith('Port'):
                    try:
                        infoname = 'hw_iscsi' + str(int(value) - 1)
                    except Exception:
                        infoname = 'hw_iscsi_ilo'
                elif name.startswith('MAC'):
                    info[infoname] = {
                        'macaddress': value.replace('-', ':'),
                        'macaddress_dash': value
                    }
        elif entry['type'] == 233:  # Embedded NIC MAC Assignment (Alternate data format)
            (infoname, entry_info) = parse_flat_interface(entry, 'hw_eth_ilo')
            info[infoname] = entry_info

    # Collect health (RAM/CPU data)
    health = ilo.get_embedded_health()
    info['hw_health'] = health

    memory_details_summary = health.get('memory', {}).get('memory_details_summary')
    # RAM as reported by iLO 2.10 on ProLiant BL460c Gen8
    if memory_details_summary:
        info['hw_memory_details_summary'] = memory_details_summary
        info['hw_memory_total'] = 0
        for cpu, details in memory_details_summary.items():
            cpu_total_memory_size = details.get('total_memory_size')
            if cpu_total_memory_size:
                ram = re.search(r'(\d+)\s+(\w+)', cpu_total_memory_size)
                if ram:
                    if ram.group(2) == 'GB':
                        info['hw_memory_total'] = info['hw_memory_total'] + int(ram.group(1))

        # reformat into a text friendly format
        info['hw_memory_total'] = "{0} GB".format(info['hw_memory_total'])

    # Report host state
    info['host_power_status'] = power_state or 'UNKNOWN'

    # Rerieve server name
    server_name = ilo.get_server_name()
    info['server_name'] = server_name

    # Rerieve snmp setting
    snmp_im_settings = ilo.get_snmp_im_settings()
    info['snmp_im_settings'] = snmp_im_settings

    # Rerieve network setting
    network_settings = ilo.get_network_settings()
    info['network_settings'] = network_settings

    # Rerieve global settings
    global_settings = ilo.get_global_settings()
    info['global_settings'] = global_settings

    # Rerieve Supported boot mode
    supported_boot_mode = ilo.get_supported_boot_mode()
    info['supported_boot_mode'] = supported_boot_mode

    # Rerieve one time boot
    one_time_boot = ilo.get_one_time_boot()
    info['one_time_boot'] = one_time_boot

    # Rerieve if is pending boot
    pending_boot_mode = ilo.get_pending_boot_mode()
    info['pending_boot_mode'] = pending_boot_mode

    # Rerieve if is persistent boot
    persistent_boot = ilo.get_persistent_boot()
    info['persistent_boot'] = persistent_boot

    # Rerieve current boot mode
    current_boot_mode = ilo.get_current_boot_mode()
    info['current_boot_mode'] = current_boot_mode

    # Retrieve Security msg
    security_msg = ilo.get_security_msg()
    info['security_msg'] = security_msg

    # Retrieve list of licenses
    all_licenses = ilo.get_all_licenses()
    info['all_licenses'] = all_licenses

    # Retrieve user data
    all_user_info = ilo.get_all_user_info()
    info['all_user_info'] = all_user_info

    # Rerieve list of users
    all_users = ilo.get_all_users()
    info['all_users'] = all_users

    module.exit_json(**info)


if __name__ == '__main__':
    main()

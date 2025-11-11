#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: sssd_info
short_description: Check SSSD domain status using D-Bus
description:
    - Check the online status of SSSD domains, list domains, and retrieve active servers using D-Bus.
author: 
    - Aleksandr Gabidullin (@MikeyTide)
requirements:
    - dbus-python
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
    platform:
        platforms: posix
options:
    action:
        description:
            - The action to perform.
            - V(domain_status) - Check if domain is online.
            - V(domain_list) - List all configured domains.
            - V(active_servers) - Get active servers for domain.
            - V(list_servers) - List all servers for domain.
        type: str
        required: true
        choices: ['domain_status', 'domain_list', 'active_servers', 'list_servers']
    domain:
        description:
            - Domain name to check.
            - Required for O(action=domain_status), O(action=active_servers) and O(action=list_servers).
        type: str
    server_type:
        description:
            - The type of server to retrieve for the O(action=active_servers) and O(action=list_servers).
        type: str
        choices: ['IPA', 'AD']
extends_documentation_fragment:
    - community.general.attributes
'''

EXAMPLES = r'''
- name: Check SSSD domain status
  community.general.sssd_info:
    action: domain_status
    domain: example.com
  register: sssd_status_result

- name: Get domain list
  community.general.sssd_info:
    action: domain_list
  register: domain_list_result

- name: Get active IPA servers for a domain
  community.general.sssd_info:
    action: active_servers
    domain: example.com
    server_type: IPA
  register: active_servers_result

- name: List servers for a domain
  community.general.sssd_info:
    action: list_servers
    domain: example.com
    server_type: AD
  register: list_servers_result
'''

RETURN = r'''
online:
    description: The online status of the SSSD domain.
    type: str
    returned: when O(action=domain_status)
    sample: online
domain_list:
    description: List of SSSD domains.
    type: list
    returned: when O(action=domain_list)
    sample: ["ipa.domain", "winad.test"]
servers:
    description: Active servers for the specified domain and type.
    type: dict
    returned: when O(action=active_servers)
    sample: {
        "Global Catalog": "server1.winad.test",
        "Domain Server": "server2.winad.test"
    }
list_servers:
    description: List of servers for the specified domain.
    type: list
    returned: when O(action=list_servers)
    sample: ["server1.winad.test", "server2.winad.test"]
error:
    description: Error message if operation failed.
    type: str
    returned: on error
    sample: "Domain not found: winad.test"
'''


from ansible.module_utils.basic import AnsibleModule
import dbus


class SSSDHandler:
    """SSSD D-Bus handler"""
    
    BUS_NAME = 'org.freedesktop.sssd.infopipe'
    DOMAIN_INTERFACE = 'org.freedesktop.sssd.infopipe.Domains.Domain'
    INFOPIPE_INTERFACE = 'org.freedesktop.sssd.infopipe'
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.sssd_obj = self.bus.get_object(self.BUS_NAME, '/org/freedesktop/sssd/infopipe')
        self.infopipe_iface = dbus.Interface(self.sssd_obj, dbus_interface=self.INFOPIPE_INTERFACE)
    
    def _get_domain_path(self, domain):
        """Convert domain name to D-Bus path format"""
        return "/org/freedesktop/sssd/infopipe/Domains/%s" % domain.replace('.', '_2e')
    
    def _get_domain_object(self, domain):
        """Get D-Bus object for domain"""
        domain_path = self._get_domain_path(domain)
        try:
            return self.bus.get_object(self.BUS_NAME, domain_path)
        except dbus.exceptions.DBusException as e:
            raise Exception("Domain not found: %s. Error: %s" % (domain, str(e)))
    
    def check_domain_status(self, domain):
        """Check if domain is online"""
        domain_obj = self._get_domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)
        return 'online' if iface.IsOnline() else 'offline'
    
    def get_active_servers(self, domain, server_type):
        """Get active servers for domain"""
        domain_obj = self._get_domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)
        
        if server_type == 'IPA':
            server_name = "%s Server" % server_type
            return {server_name: iface.ActiveServer(server_type)}
        elif server_type == 'AD':
            return {
                "AD Global Catalog": iface.ActiveServer("sd_gc_%s" % domain),
                "AD Domain Controller": iface.ActiveServer("sd_%s" % domain)
            }
    
    def list_servers(self, domain, server_type):
        """List all servers for domain"""
        domain_obj = self._get_domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)
        if server_type == 'IPA':
            return iface.ListServers(server_type)
        elif server_type == 'AD':
            return iface.ListServers("sd_%s" % domain)
    
    def get_domain_list(self):
        """Get list of all domains"""
        response = self.infopipe_iface.ListDomains()
        return [str(domain).split('/')[-1].replace('_2e', '.') for domain in response]


def main():
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(
                type='str', 
                required=True, 
                choices=['domain_status', 'domain_list', 'active_servers', 'list_servers']
            ),
            domain=dict(type='str'),
            server_type=dict(type='str', choices=['IPA', 'AD'])
        ),
        supports_check_mode=True,
        required_if=[
            ('action', 'domain_status', ['domain']),
            ('action', 'list_servers', ['domain', 'server_type']),
            ('action', 'active_servers', ['domain', 'server_type'])
        ]
    )
    
    action = module.params['action']
    domain = module.params.get('domain')
    server_type = module.params.get('server_type')
    
    sssd = SSSDHandler()
    result = {}
    
    try:
        if action == 'domain_status':
            result['online'] = sssd.check_domain_status(domain)
        elif action == 'domain_list':
            result['domain_list'] = sssd.get_domain_list()
        elif action == 'active_servers':
            result['servers'] = sssd.get_active_servers(domain, server_type)
        elif action == 'list_servers':
            result['list_servers'] = sssd.list_servers(domain, server_type)
            
    except dbus.exceptions.DBusException as e:
        dbus_error_name = e.get_dbus_name()
        if dbus_error_name == 'org.freedesktop.DBus.Error.UnknownObject':
            module.fail_json(msg="Domain not found: %s" % domain, **result)
        elif dbus_error_name == 'org.freedesktop.DBus.Error.UnknownInterface':
            module.fail_json(msg="Interface not found for domain: %s" % domain, **result)
        elif dbus_error_name == 'org.freedesktop.DBus.Error.UnknownMethod':
            module.fail_json(msg="Method not supported for domain: %s" % domain, **result)
        elif 'org.freedesktop.DBus.Error.InvalidArgs' in dbus_error_name:
            module.fail_json(msg="Invalid arguments for method: %s" % str(e), **result)
        else:
            module.fail_json(msg="D-Bus error (name: %s): %s" % (dbus_error_name, str(e)), **result)
    except Exception as e:
        module.fail_json(msg="Unexpected error: %s" % str(e), **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
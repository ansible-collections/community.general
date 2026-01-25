#!/usr/bin/python
# Copyright (c) 2025 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: sssd_info
version_added: 12.2.0
short_description: Check SSSD domain status using D-Bus
description:
  - Check the online status of SSSD domains, list domains, and retrieve active servers using D-Bus.
author: "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - dbus
  - SSSD needs to be running
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  action:
    description:
      - The action to perform.
    type: str
    required: true
    choices:
      domain_status: Check if domain is online.
      domain_list: List all configured domains.
      active_servers: Get active servers for domain.
      list_servers: List all servers for domain.
  domain:
    description:
      - Domain name to check.
      - Required unless O(action=domain_list).
      - When O(action=domain_list), this parameter is ignored and the module returns a list of all configured domains.
    type: str
  server_type:
    description:
      - Required parameter when O(action=active_servers) and O(action=list_servers).
      - Optional and ignored for all other actions.
      - At this point, the module supports ONLY the types C(IPA) for FreeIPA servers and C(AD).
    type: str
    choices: ['IPA', 'AD']
extends_documentation_fragment:
  - community.general.attributes
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
online:
  description: The online status of the SSSD domain.
  type: str
  returned: when O(action=domain_status)
  sample: online
domain_list:
  description: List of SSSD domains.
  type: list
  elements: str
  returned: when O(action=domain_list)
  sample: ["ipa.domain", "winad.test"]
servers:
  description: Active servers for the specified domain and type.
  type: dict
  returned: when O(action=active_servers)
  sample: {"Global Catalog": "server1.winad.test", "Domain Server": "server2.winad.test"}
list_servers:
  description: List of servers for the specified domain.
  type: list
  elements: str
  returned: when O(action=list_servers)
  sample: ["server1.winad.test", "server2.winad.test"]
"""


import typing as t

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("dbus"):
    import dbus


class SSSDHandler:
    """SSSD D-Bus handler"""

    BUS_NAME = "org.freedesktop.sssd.infopipe"
    DOMAIN_INTERFACE = "org.freedesktop.sssd.infopipe.Domains.Domain"
    INFOPIPE_INTERFACE = "org.freedesktop.sssd.infopipe"

    def __init__(self) -> None:
        """Initialize SSSD D-Bus connection."""
        self.bus = dbus.SystemBus()
        self.sssd_obj = self.bus.get_object(self.BUS_NAME, "/org/freedesktop/sssd/infopipe")
        self.infopipe_iface = dbus.Interface(self.sssd_obj, dbus_interface=self.INFOPIPE_INTERFACE)

    def domain_path(self, domain: str) -> str:
        return f"/org/freedesktop/sssd/infopipe/Domains/{domain.replace('.', '_2e')}"

    def domain_object(self, domain: str) -> dbus.proxies.ProxyObject:
        domain_path = self.domain_path(domain)
        try:
            return self.bus.get_object(self.BUS_NAME, domain_path)
        except dbus.exceptions.DBusException as e:
            raise Exception(f"Domain not found: {domain}. Error: {e}") from e

    def check_domain_status(self, domain: str) -> str:
        domain_obj = self.domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)
        return "online" if iface.IsOnline() else "offline"

    def active_servers(self, domain: str, server_type: str) -> dict[str, str]:
        """Get active servers for domain.

        Args:
            domain: Domain name to get servers for.
            server_type: Type of servers ('IPA' or 'AD').

        Returns:
            Dictionary with server types as keys and server names as values.
        """
        domain_obj = self.domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)

        if server_type == "IPA":
            server_name = f"{server_type} Server"
            return {server_name: iface.ActiveServer(server_type)}
        else:
            return {
                "AD Global Catalog": iface.ActiveServer(f"sd_gc_{domain}"),
                "AD Domain Controller": iface.ActiveServer(f"sd_{domain}"),
            }

    def list_servers(self, domain: str, server_type: str) -> list[str]:
        """List all servers for domain.

        Args:
            domain: Domain name to list servers for.
            server_type: Type of servers ('IPA' or 'AD').

        Returns:
            List of server names.
        """
        domain_obj = self.domain_object(domain)
        iface = dbus.Interface(domain_obj, dbus_interface=self.DOMAIN_INTERFACE)
        if server_type == "IPA":
            return iface.ListServers(server_type)
        else:
            return iface.ListServers(f"sd_{domain}")

    def domain_list(self) -> list[str]:
        """Get list of all domains.

        Returns:
            List of domain names.
        """
        response = self.infopipe_iface.ListDomains()
        return [domain.rsplit("/", maxsplit=1)[-1].replace("_2e", ".") for domain in response]


def main() -> None:
    """Main function for the Ansible module."""
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(
                type="str",
                required=True,
                choices=["domain_status", "domain_list", "active_servers", "list_servers"],
            ),
            domain=dict(type="str"),
            server_type=dict(type="str", choices=["IPA", "AD"]),
        ),
        supports_check_mode=True,
        required_if=[
            ("action", "domain_status", ["domain"]),
            ("action", "list_servers", ["domain", "server_type"]),
            ("action", "active_servers", ["domain", "server_type"]),
        ],
    )

    deps.validate(module)

    action = module.params["action"]
    domain = module.params.get("domain")
    server_type = module.params.get("server_type")

    sssd = SSSDHandler()
    result: dict[str, t.Any] = {}

    try:
        if action == "domain_status":
            result["online"] = sssd.check_domain_status(domain)
        elif action == "domain_list":
            result["domain_list"] = sssd.domain_list()
        elif action == "active_servers":
            result["servers"] = sssd.active_servers(domain, server_type)
        elif action == "list_servers":
            result["list_servers"] = sssd.list_servers(domain, server_type)

    except Exception as e:
        module.fail_json(msg=f"Error: {e}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()

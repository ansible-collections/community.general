# Copyright (C) 2020 Orion Poplawski <orion@nwra.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
author: Orion Poplawski (@opoplawski)
name: cobbler
short_description: Cobbler inventory source
version_added: 1.0.0
description:
  - Get inventory hosts from the cobbler service.
  - 'Uses a configuration file as an inventory source, it must end in C(.cobbler.yml) or C(.cobbler.yaml) and have a C(plugin:
    cobbler) entry.'
  - Adds the primary IP addresses to C(cobbler_ipv4_address) and C(cobbler_ipv6_address) host variables if defined in Cobbler.
    The primary IP address is defined as the management interface if defined, or the interface who's DNS name matches the
    hostname of the system, or else the first interface found.
extends_documentation_fragment:
  - inventory_cache
options:
  plugin:
    description: The name of this plugin, it should always be set to V(community.general.cobbler) for this plugin to recognize
      it as its own.
    type: string
    required: true
    choices: ['cobbler', 'community.general.cobbler']
  url:
    description: URL to cobbler.
    type: string
    default: 'http://cobbler/cobbler_api'
    env:
      - name: COBBLER_SERVER
  user:
    description: Cobbler authentication user.
    type: string
    required: false
    env:
      - name: COBBLER_USER
  password:
    description: Cobbler authentication password.
    type: string
    required: false
    env:
      - name: COBBLER_PASSWORD
  cache_fallback:
    description: Fallback to cached results if connection to cobbler fails.
    type: boolean
    default: false
  connection_timeout:
    description: Timeout to connect to cobbler server.
    type: int
    required: false
    version_added: 10.7.0
  exclude_mgmt_classes:
    description: Management classes to exclude from inventory.
    type: list
    default: []
    elements: str
    version_added: 7.4.0
  exclude_profiles:
    description:
      - Profiles to exclude from inventory.
      - Ignored if O(include_profiles) is specified.
    type: list
    default: []
    elements: str
  include_mgmt_classes:
    description: Management classes to include from inventory.
    type: list
    default: []
    elements: str
    version_added: 7.4.0
  include_profiles:
    description:
      - Profiles to include from inventory.
      - If specified, all other profiles are excluded.
      - O(exclude_profiles) is ignored if O(include_profiles) is specified.
    type: list
    default: []
    elements: str
    version_added: 4.4.0
  inventory_hostname:
    description:
      - What to use for the ansible inventory hostname.
      - By default the networking hostname is used if defined, otherwise the DNS name of the management or first non-static
        interface.
      - If set to V(system), the cobbler system name is used.
    type: str
    choices: ['hostname', 'system']
    default: hostname
    version_added: 7.1.0
  group_by:
    description: Keys to group hosts by.
    type: list
    elements: string
    default: ['mgmt_classes', 'owners', 'status']
  group:
    description: Group to place all hosts into.
    default: cobbler
  group_prefix:
    description: Prefix to apply to cobbler groups.
    default: cobbler_
  want_facts:
    description: Toggle, if V(true) the plugin retrieves all host facts from the server.
    type: boolean
    default: true
  want_ip_addresses:
    description:
      - Toggle, if V(true) the plugin adds a C(cobbler_ipv4_addresses) and C(cobbler_ipv6_addresses) dictionary to the
        defined O(group) mapping interface DNS names to IP addresses.
    type: boolean
    default: true
    version_added: 7.1.0
  facts_level:
    description:
      - Set to V(normal) to gather only system-level variables.
      - Set to V(as_rendered) to gather all variables as rolled up by Cobbler.
    type: string
    choices: ['normal', 'as_rendered']
    default: normal
    version_added: 10.7.0
"""

EXAMPLES = r"""
# my.cobbler.yml
plugin: community.general.cobbler
url: http://cobbler/cobbler_api
user: ansible-tester
password: secure
"""

import socket

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name

from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe

# xmlrpc
try:
    import xmlrpc.client as xmlrpc_client

    HAS_XMLRPC_CLIENT = True
except ImportError:
    HAS_XMLRPC_CLIENT = False


class TimeoutTransport(xmlrpc_client.SafeTransport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super().__init__()
        self._timeout = timeout
        self.context = None

    def make_connection(self, host):
        conn = xmlrpc_client.SafeTransport.make_connection(self, host)
        conn.timeout = self._timeout
        return conn


class InventoryModule(BaseInventoryPlugin, Cacheable):
    """Host inventory parser for ansible using cobbler as source."""

    NAME = "community.general.cobbler"

    def __init__(self):
        super().__init__()
        self.cache_key = None

        if not HAS_XMLRPC_CLIENT:
            raise AnsibleError("Could not import xmlrpc client library")

    def verify_file(self, path):
        valid = False
        if super().verify_file(path):
            if path.endswith(("cobbler.yaml", "cobbler.yml")):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "cobbler.yaml" nor "cobbler.yml"')
        return valid

    def _init_cache(self):
        if self.cache_key not in self._cache:
            self._cache[self.cache_key] = {}

    def _reload_cache(self):
        if self.get_option("cache_fallback"):
            self.display.vvv("Cannot connect to server, loading cache\n")
            self._options["cache_timeout"] = 0
            self.load_cache_plugin()
            self._cache.get(self.cache_key, {})

    def _get_profiles(self):
        if not self.use_cache or "profiles" not in self._cache.get(self.cache_key, {}):
            try:
                if self.token is not None:
                    data = self.cobbler.get_profiles(self.token)
                else:
                    data = self.cobbler.get_profiles()
            except (socket.gaierror, socket.error, xmlrpc_client.ProtocolError):
                self._reload_cache()
            else:
                self._init_cache()
                self._cache[self.cache_key]["profiles"] = data

        return self._cache[self.cache_key]["profiles"]

    def _get_systems(self):
        if not self.use_cache or "systems" not in self._cache.get(self.cache_key, {}):
            try:
                if self.token is not None:
                    data = self.cobbler.get_systems(self.token)
                else:
                    data = self.cobbler.get_systems()

                # If more facts are requested, gather them all from Cobbler
                if self.facts_level == "as_rendered":
                    for i, host in enumerate(data):
                        self.display.vvvv(f"Gathering all facts for {host['name']}\n")
                        if self.token is not None:
                            data[i] = self.cobbler.get_system_as_rendered(host["name"], self.token)
                        else:
                            data[i] = self.cobbler.get_system_as_rendered(host["name"])
            except (socket.gaierror, socket.error, xmlrpc_client.ProtocolError):
                self._reload_cache()
            else:
                self._init_cache()
                self._cache[self.cache_key]["systems"] = data

        return self._cache[self.cache_key]["systems"]

    def _add_safe_group_name(self, group, child=None):
        group_name = self.inventory.add_group(
            to_safe_group_name(f"{self.get_option('group_prefix')}{group.lower().replace(' ', '')}")
        )
        if child is not None:
            self.inventory.add_child(group_name, child)
        return group_name

    def _exclude_profile(self, profile):
        if self.include_profiles:
            return profile not in self.include_profiles
        else:
            return profile in self.exclude_profiles

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # get connection host
        self.cobbler_url = self.get_option("url")
        self.display.vvvv(f"Connecting to {self.cobbler_url}\n")

        if "connection_timeout" in self._options:
            self.cobbler = xmlrpc_client.Server(
                self.cobbler_url,
                allow_none=True,
                transport=TimeoutTransport(timeout=self.get_option("connection_timeout")),
            )
        else:
            self.cobbler = xmlrpc_client.Server(self.cobbler_url, allow_none=True)
        self.token = None
        if self.get_option("user") is not None:
            self.token = self.cobbler.login(str(self.get_option("user")), str(self.get_option("password")))

        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option("cache")

        self.exclude_mgmt_classes = self.get_option("exclude_mgmt_classes")
        self.include_mgmt_classes = self.get_option("include_mgmt_classes")
        self.exclude_profiles = self.get_option("exclude_profiles")
        self.include_profiles = self.get_option("include_profiles")
        self.group_by = self.get_option("group_by")
        self.inventory_hostname = self.get_option("inventory_hostname")
        self.facts_level = self.get_option("facts_level")

        for profile in self._get_profiles():
            if profile["parent"]:
                self.display.vvvv(f"Processing profile {profile['name']} with parent {profile['parent']}\n")
                if not self._exclude_profile(profile["parent"]):
                    parent_group_name = self._add_safe_group_name(profile["parent"])
                    self.display.vvvv(f"Added profile parent group {parent_group_name}\n")
                    if not self._exclude_profile(profile["name"]):
                        group_name = self._add_safe_group_name(profile["name"])
                        self.display.vvvv(f"Added profile group {group_name}\n")
                        self.inventory.add_child(parent_group_name, group_name)
            else:
                self.display.vvvv(f"Processing profile {profile['name']} without parent\n")
                # Create a hierarchy of profile names
                profile_elements = profile["name"].split("-")
                i = 0
                while i < len(profile_elements) - 1:
                    profile_group = "-".join(profile_elements[0 : i + 1])
                    profile_group_child = "-".join(profile_elements[0 : i + 2])
                    if self._exclude_profile(profile_group):
                        self.display.vvvv(f"Excluding profile {profile_group}\n")
                        break
                    group_name = self._add_safe_group_name(profile_group)
                    self.display.vvvv(f"Added profile group {group_name}\n")
                    child_group_name = self._add_safe_group_name(profile_group_child)
                    self.display.vvvv(f"Added profile child group {child_group_name} to {group_name}\n")
                    self.inventory.add_child(group_name, child_group_name)
                    i = i + 1

        # Add default group for this inventory if specified
        self.group = to_safe_group_name(self.get_option("group"))
        if self.group is not None and self.group != "":
            self.inventory.add_group(self.group)
            self.display.vvvv(f"Added site group {self.group}\n")

        ip_addresses = {}
        ipv6_addresses = {}
        for host in self._get_systems():
            # Get the FQDN for the host and add it to the right groups
            if self.inventory_hostname == "system":
                hostname = make_unsafe(host["name"])  # None
            else:
                hostname = make_unsafe(host["hostname"])  # None
            interfaces = host["interfaces"]

            if set(host["mgmt_classes"]) & set(self.include_mgmt_classes):
                self.display.vvvv(f"Including host {host['name']} in mgmt_classes {host['mgmt_classes']}\n")
            else:
                if self._exclude_profile(host["profile"]):
                    self.display.vvvv(f"Excluding host {host['name']} in profile {host['profile']}\n")
                    continue

                if set(host["mgmt_classes"]) & set(self.exclude_mgmt_classes):
                    self.display.vvvv(f"Excluding host {host['name']} in mgmt_classes {host['mgmt_classes']}\n")
                    continue

            # hostname is often empty for non-static IP hosts
            if hostname == "":
                for iname, ivalue in interfaces.items():
                    if ivalue["management"] or not ivalue["static"]:
                        this_dns_name = ivalue.get("dns_name", None)
                        if this_dns_name is not None and this_dns_name != "":
                            hostname = make_unsafe(this_dns_name)
                            self.display.vvvv(f"Set hostname to {hostname} from {iname}\n")

            if hostname == "":
                self.display.vvvv(f"Cannot determine hostname for host {host['name']}, skipping\n")
                continue

            self.inventory.add_host(hostname)
            self.display.vvvv(f"Added host {host['name']} hostname {hostname}\n")

            # Add host to profile group
            if host["profile"] != "":
                group_name = self._add_safe_group_name(host["profile"], child=hostname)
                self.display.vvvv(f"Added host {hostname} to profile group {group_name}\n")
            else:
                self.display.warning(f"Host {hostname} has an empty profile\n")

            # Add host to groups specified by group_by fields
            for group_by in self.group_by:
                if host[group_by] == "<<inherit>>" or host[group_by] == "":
                    groups = []
                else:
                    groups = [host[group_by]] if isinstance(host[group_by], str) else host[group_by]
                for group in groups:
                    group_name = self._add_safe_group_name(group, child=hostname)
                    self.display.vvvv(f"Added host {hostname} to group_by {group_by} group {group_name}\n")

            # Add to group for this inventory
            if self.group is not None:
                self.inventory.add_child(self.group, hostname)

            # Add host variables
            ip_address = None
            ip_address_first = None
            ipv6_address = None
            ipv6_address_first = None
            for iname, ivalue in interfaces.items():
                # Set to first interface or management interface if defined or hostname matches dns_name
                if ivalue["ip_address"] != "":
                    if ip_address_first is None:
                        ip_address_first = ivalue["ip_address"]
                    if ivalue["management"]:
                        ip_address = ivalue["ip_address"]
                    elif ivalue["dns_name"] == hostname and ip_address is None:
                        ip_address = ivalue["ip_address"]
                if ivalue["ipv6_address"] != "":
                    if ipv6_address_first is None:
                        ipv6_address_first = ivalue["ipv6_address"]
                    if ivalue["management"]:
                        ipv6_address = ivalue["ipv6_address"]
                    elif ivalue["dns_name"] == hostname and ipv6_address is None:
                        ipv6_address = ivalue["ipv6_address"]

                # Collect all interface name mappings for adding to group vars
                if self.get_option("want_ip_addresses"):
                    if ivalue["dns_name"] != "":
                        if ivalue["ip_address"] != "":
                            ip_addresses[ivalue["dns_name"]] = ivalue["ip_address"]
                        if ivalue["ipv6_address"] != "":
                            ip_addresses[ivalue["dns_name"]] = ivalue["ipv6_address"]

            # Add ip_address to host if defined, use first if no management or matched dns_name
            if ip_address is None and ip_address_first is not None:
                ip_address = ip_address_first
            if ip_address is not None:
                self.inventory.set_variable(hostname, "cobbler_ipv4_address", make_unsafe(ip_address))
            if ipv6_address is None and ipv6_address_first is not None:
                ipv6_address = ipv6_address_first
            if ipv6_address is not None:
                self.inventory.set_variable(hostname, "cobbler_ipv6_address", make_unsafe(ipv6_address))

            if self.get_option("want_facts"):
                try:
                    self.inventory.set_variable(hostname, "cobbler", make_unsafe(host))
                except ValueError as e:
                    self.display.warning(f"Could not set host info for {hostname}: {e}")

        if self.get_option("want_ip_addresses"):
            self.inventory.set_variable(self.group, "cobbler_ipv4_addresses", make_unsafe(ip_addresses))
            self.inventory.set_variable(self.group, "cobbler_ipv6_addresses", make_unsafe(ipv6_addresses))

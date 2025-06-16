# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: nmap
short_description: Uses nmap to find hosts to target
description:
  - Uses a YAML configuration file with a valid YAML extension.
extends_documentation_fragment:
  - constructed
  - inventory_cache
requirements:
  - nmap CLI installed
options:
  plugin:
    description: token that ensures this is a source file for the 'nmap' plugin.
    type: string
    required: true
    choices: ['nmap', 'community.general.nmap']
  sudo:
    description: Set to V(true) to execute a C(sudo nmap) plugin scan.
    version_added: 4.8.0
    default: false
    type: boolean
  address:
    description: Network IP or range of IPs to scan, you can use a simple range (10.2.2.15-25) or CIDR notation.
    type: string
    required: true
    env:
      - name: ANSIBLE_NMAP_ADDRESS
        version_added: 6.6.0
  exclude:
    description:
      - List of addresses to exclude.
      - For example V(10.2.2.15-25) or V(10.2.2.15,10.2.2.16).
    type: list
    elements: string
    env:
      - name: ANSIBLE_NMAP_EXCLUDE
        version_added: 6.6.0
  port:
    description:
      - Only scan specific port or port range (C(-p)).
      - For example, you could pass V(22) for a single port, V(1-65535) for a range of ports,
        or V(U:53,137,T:21-25,139,8080,S:9) to check port 53 with UDP, ports 21-25 with TCP, port 9 with SCTP, and ports 137, 139, and 8080 with all.
    type: string
    version_added: 6.5.0
  ports:
    description: Enable/disable scanning ports.
    type: boolean
    default: true
  ipv4:
    description: use IPv4 type addresses
    type: boolean
    default: true
  ipv6:
    description: use IPv6 type addresses
    type: boolean
    default: true
  udp_scan:
    description:
      - Scan via UDP.
      - Depending on your system you might need O(sudo=true) for this to work.
    type: boolean
    default: false
    version_added: 6.1.0
  icmp_timestamp:
    description:
      - Scan via ICMP Timestamp (C(-PP)).
      - Depending on your system you might need O(sudo=true) for this to work.
    type: boolean
    default: false
    version_added: 6.1.0
  open:
    description: Only scan for open (or possibly open) ports.
    type: boolean
    default: false
    version_added: 6.5.0
  dns_resolve:
    description: Whether to always (V(true)) or never (V(false)) do DNS resolution.
    type: boolean
    default: false
    version_added: 6.1.0
  dns_servers:
    description: Specify which DNS servers to use for name resolution.
    type: list
    elements: string
    version_added: 10.5.0
  use_arp_ping:
    description: Whether to always (V(true)) use the quick ARP ping or (V(false)) a slower but more reliable method.
    type: boolean
    default: true
    version_added: 7.4.0
notes:
  - At least one of O(ipv4) or O(ipv6) is required to be V(true); both can be V(true), but they cannot both be V(false).
  - 'TODO: add OS fingerprinting'
"""
EXAMPLES = r"""
---
# inventory.config file in YAML format
plugin: community.general.nmap
strict: false
address: 192.168.0.0/24

---
# a sudo nmap scan to fully use nmap scan power.
plugin: community.general.nmap
sudo: true
strict: false
address: 192.168.0.0/24

---
# an nmap scan specifying ports and classifying results to an inventory group
plugin: community.general.nmap
address: 192.168.0.0/24
exclude: 192.168.0.1, web.example.com
port: 22, 443
groups:
  web_servers: "ports | selectattr('port', 'equalto', '443')"
"""

import os
import re

from subprocess import Popen, PIPE

from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path

from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.general.nmap'
    find_host = re.compile(r'^Nmap scan report for ([\w,.,-]+)(?: \(([\w,.,:,\[,\]]+)\))?')
    find_port = re.compile(r'^(\d+)/(\w+)\s+(\w+)\s+(\w+)')

    def __init__(self):
        self._nmap = None
        super(InventoryModule, self).__init__()

    def _populate(self, hosts):
        # Use constructed if applicable
        strict = self.get_option('strict')

        for host in hosts:
            host = make_unsafe(host)
            hostname = host['name']
            self.inventory.add_host(hostname)
            for var, value in host.items():
                self.inventory.set_variable(hostname, var, value)

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), host, hostname, strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), host, hostname, strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host, hostname, strict=strict)

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            file_name, ext = os.path.splitext(path)

            if not ext or ext in C.YAML_FILENAME_EXTENSIONS:
                valid = True

        return valid

    def parse(self, inventory, loader, path, cache=True):

        try:
            self._nmap = get_bin_path('nmap')
        except ValueError as e:
            raise AnsibleParserError(f'nmap inventory plugin requires the nmap cli tool to work: {e}')

        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)

        self._read_config_data(path)

        cache_key = self.get_cache_key(path)

        # cache may be True or False at this point to indicate if the inventory is being refreshed
        # get the user's cache option too to see if we should save the cache if it is changing
        user_cache_setting = self.get_option('cache')

        # read if the user has caching enabled and the cache isn't being refreshed
        attempt_to_read_cache = user_cache_setting and cache
        # update if the user has caching enabled and the cache is being refreshed; update this value to True if the cache has expired below
        cache_needs_update = user_cache_setting and not cache

        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True

        if not user_cache_setting or cache_needs_update:
            # setup command
            cmd = [self._nmap]

            if self.get_option('sudo'):
                cmd.insert(0, 'sudo')

            if self.get_option('port'):
                cmd.append('-p')
                cmd.append(self.get_option('port'))

            if not self.get_option('ports'):
                cmd.append('-sP')

            if self.get_option('ipv4') and not self.get_option('ipv6'):
                cmd.append('-4')
            elif self.get_option('ipv6') and not self.get_option('ipv4'):
                cmd.append('-6')
            elif not self.get_option('ipv6') and not self.get_option('ipv4'):
                raise AnsibleParserError('One of ipv4 or ipv6 must be enabled for this plugin')

            if self.get_option('exclude'):
                cmd.append('--exclude')
                cmd.append(','.join(self.get_option('exclude')))

            if self.get_option('dns_resolve'):
                cmd.append('-n')

            if self.get_option('dns_servers'):
                cmd.append('--dns-servers')
                cmd.append(','.join(self.get_option('dns_servers')))

            if self.get_option('udp_scan'):
                cmd.append('-sU')

            if self.get_option('icmp_timestamp'):
                cmd.append('-PP')

            if self.get_option('open'):
                cmd.append('--open')

            if not self.get_option('use_arp_ping'):
                cmd.append('--disable-arp-ping')

            cmd.append(self.get_option('address'))
            try:
                # execute
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    raise AnsibleParserError(f'Failed to run nmap, rc={p.returncode}: {to_native(stderr)}')

                # parse results
                host = None
                ip = None
                ports = []
                results = []

                try:
                    t_stdout = to_text(stdout, errors='surrogate_or_strict')
                except UnicodeError as e:
                    raise AnsibleParserError(f'Invalid (non unicode) input returned: {e}')

                for line in t_stdout.splitlines():
                    hits = self.find_host.match(line)
                    if hits:
                        if host is not None and ports:
                            results[-1]['ports'] = ports

                        # if dns only shows arpa, just use ip instead as hostname
                        if hits.group(1).endswith('.in-addr.arpa'):
                            host = hits.group(2)
                        else:
                            host = hits.group(1)

                        # if no reverse dns exists, just use ip instead as hostname
                        if hits.group(2) is not None:
                            ip = hits.group(2)
                        else:
                            ip = hits.group(1)

                        if host is not None:
                            # update inventory
                            results.append(dict())
                            results[-1]['name'] = host
                            results[-1]['ip'] = ip
                            ports = []
                        continue

                    host_ports = self.find_port.match(line)
                    if host is not None and host_ports:
                        ports.append({'port': host_ports.group(1),
                                      'protocol': host_ports.group(2),
                                      'state': host_ports.group(3),
                                      'service': host_ports.group(4)})
                        continue

                # if any leftovers
                if host and ports:
                    results[-1]['ports'] = ports

            except Exception as e:
                raise AnsibleParserError(f"failed to parse {to_native(path)}: {e} ")

        if cache_needs_update:
            self._cache[cache_key] = results

        self._populate(results)

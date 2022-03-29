# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
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
            required: True
            choices: ['nmap', 'community.general.nmap']
        address:
            description: Network IP or range of IPs to scan, you can use a simple range (10.2.2.15-25) or CIDR notation.
            required: True
        exclude:
            description: list of addresses to exclude
            type: list
        ports:
            description: Enable/disable scanning for open ports
            type: boolean
            default: True
        ipv4:
            description: use IPv4 type addresses
            type: boolean
            default: True
        ipv6:
            description: use IPv6 type addresses
            type: boolean
            default: True
    notes:
        - At least one of ipv4 or ipv6 is required to be True, both can be True, but they cannot both be False.
        - 'TODO: add OS fingerprinting'
'''
EXAMPLES = '''
# inventory.config file in YAML format
plugin: community.general.nmap
strict: False
address: 192.168.0.0/24
'''

import os
import re

from subprocess import Popen, PIPE

from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_native, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.general.nmap'
    find_host = re.compile(r'^Nmap scan report for ([\w,.,-]+)(?: \(([\w,.,:,\[,\]]+)\))?')
    find_port = re.compile(r'^(\d+)/(\w+)\s+(\w+)\s+(\w+)')

    def __init__(self):
        self._nmap = None
        super(InventoryModule, self).__init__()

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            file_name, ext = os.path.splitext(path)

            if not ext or ext in C.YAML_FILENAME_EXTENSIONS:
                valid = True

        return valid

    def parse(self, inventory, loader, path, cache=False):

        try:
            self._nmap = get_bin_path('nmap')
        except ValueError as e:
            raise AnsibleParserError('nmap inventory plugin requires the nmap cli tool to work: {0}'.format(to_native(e)))

        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)

        self._read_config_data(path)

        # setup command
        cmd = [self._nmap]
        if not self._options['ports']:
            cmd.append('-sP')

        if self._options['ipv4'] and not self._options['ipv6']:
            cmd.append('-4')
        elif self._options['ipv6'] and not self._options['ipv4']:
            cmd.append('-6')
        elif not self._options['ipv6'] and not self._options['ipv4']:
            raise AnsibleParserError('One of ipv4 or ipv6 must be enabled for this plugin')

        if self._options['exclude']:
            cmd.append('--exclude')
            cmd.append(','.join(self._options['exclude']))

        cmd.append(self._options['address'])
        try:
            # execute
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise AnsibleParserError('Failed to run nmap, rc=%s: %s' % (p.returncode, to_native(stderr)))

            # parse results
            host = None
            ip = None
            ports = []

            try:
                t_stdout = to_text(stdout, errors='surrogate_or_strict')
            except UnicodeError as e:
                raise AnsibleParserError('Invalid (non unicode) input returned: %s' % to_native(e))

            for line in t_stdout.splitlines():
                hits = self.find_host.match(line)
                if hits:
                    if host is not None:
                        self.inventory.set_variable(host, 'ports', ports)

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
                        self.inventory.add_host(host)
                        self.inventory.set_variable(host, 'ip', ip)
                        ports = []
                    continue

                host_ports = self.find_port.match(line)
                if host is not None and host_ports:
                    ports.append({'port': host_ports.group(1), 'protocol': host_ports.group(2), 'state': host_ports.group(3), 'service': host_ports.group(4)})
                    continue

                # TODO: parse more data, OS?

            # if any leftovers
            if host and ports:
                self.inventory.set_variable(host, 'ports', ports)

        except Exception as e:
            raise AnsibleParserError("failed to parse %s: %s " % (to_native(path), to_native(e)))

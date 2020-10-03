# Copyright (C) 2020  Florent Madiot <scodeman@scode.io>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: multipass
    plugin_type: inventory
    author: 
      - Florent Madiot (@scodeman)
    version_added: 1.2.0
    short_description: canonical/multipass inventory source
    description:
        - Get inventory hosts from the local multipass installation.
        - Uses a YAML configuration file with a valid YAML extension.
        - The C(inventory_hostname) is always the 'Name' of the multipass instance.
    extends_documentation_fragment:
      - constructed
      - inventory_cache
    requirements:
      - multipass CLI installed
    options:
        plugin:
            description: token that ensures this is a source file for the 'multipass' plugin.
            required: True
            choices: ['multipass', 'community.general.multipass']
        running_only:
            description: toggles showing all vms vs only those currently running
            type: boolean
            default: False
'''
EXAMPLES = '''
# inventory config file in YAML format
plugin: community.general.multipass

'''

import os
import json

from subprocess import Popen, PIPE
from json.decoder import JSONDecodeError

from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.general.multipass'

    def __init__(self):
        self._multipass = None
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
            self._multipass = get_bin_path('multipass')
        except ValueError as e:
            raise AnsibleParserError('multipass inventory plugin requires the multipass cli tool to work: {0}'.format(to_native(e)))

        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)
        # config and options
        self._read_config_data(path)
        running = self.get_option('running_only')

        # setup command
        cmd = [self._multipass]
        cmd.append('info')
        cmd.append('--format')
        cmd.append('json')
        cmd.append('--all')
        try:
            # execute
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise AnsibleParserError('Failed to run multipass, rc=%s: %s' % (p.returncode, to_native(stderr)))

            # parse results
            try:
                data = json.loads(stdout)
            except JSONDecodeError as e:
                raise AnsibleParserError('Invalid json input returned: %s' % to_native(e))

            group = 'multipass'
            self.inventory.add_group(group)

            for host, hostinfo in data.get('info', {}).items():
                # All or running only
                if running and hostinfo['state'] != 'Running':
                    continue
                # Extract IP
                ip = None
                if len(hostinfo['ipv4']):
                    ip = hostinfo['ipv4'][0].strip()

                # Set inventory
                self.inventory.add_host(host)
                self.inventory.add_child(group, host)
                self.inventory.set_variable(host, 'ip', ip)
                self.inventory.set_variable(host, 'ansible_host', ip)
                # TODO: extract more data

        except Exception as e:
            raise AnsibleParserError("failed to parse %s: %s " % (to_native(path), to_native(e)))

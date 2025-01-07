# -*- coding: utf-8 -*-

# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: iocage
    short_description: iocage inventory source
    version_added: 10.2.0
    author:
        - Vladimir Botka (@vbotka)
    requirements:
        - iocage >= 1.8
    description:
        - Get inventory hosts from the iocage jail manager running on O(host).
        - By default, O(host) is V(localhost). If O(host) is not V(localhost) it
          is expected that the user running Ansible on the controller can
          connect to the O(host) account O(user) with SSH non-interactively and
          execute the command C(iocage list).
        - Uses a configuration file as an inventory source, it must end
          in C(.iocage.yml) or C(.iocage.yaml).
    extends_documentation_fragment:
        - ansible.builtin.constructed
        - ansible.builtin.inventory_cache
    options:
        plugin:
            description:
              - The name of this plugin, it should always be set to
                V(community.general.iocage) for this plugin to recognize
                it as its own.
            required: true
            choices: ['community.general.iocage']
            type: str
        host:
            description: The IP/hostname of the C(iocage) host.
            type: str
            default: localhost
        user:
            description:
              - C(iocage) user.
                It is expected that the O(user) is able to connect to the
                O(host) with SSH and execute the command C(iocage list).
                This option is not required if O(host) is V(localhost).
            type: str
        get_properties:
            description:
              - Get jails' properties.
                Creates dictionary C(iocage_properties) for each added host.
            type: boolean
            default: false
        env:
            description: O(user)'s environment on O(host).
            type: dict
            default: {}
    notes:
      - You might want to test the command C(ssh user@host iocage list -l) on
        the controller before using this inventory plugin with O(user) specified
        and with O(host) other than V(localhost).
      - If you run this inventory plugin on V(localhost) C(ssh) is not used.
        In this case, test the command C(iocage list -l).
      - This inventory plugin creates variables C(iocage_*) for each added host.
      - The values of these variables are collected from the output of the
        command C(iocage list -l).
      - The names of these variables correspond to the output columns.
      - The column C(NAME) is used to name the added host.
'''

EXAMPLES = '''
# file name must end with iocage.yaml or iocage.yml
plugin: community.general.iocage
host: 10.1.0.73
user: admin

# user is not required if iocage is running on localhost (default)
plugin: community.general.iocage

# run cryptography without legacy algorithms
plugin: community.general.iocage
host: 10.1.0.73
user: admin
env:
  CRYPTOGRAPHY_OPENSSL_NO_LEGACY: 1

# enable cache
plugin: community.general.iocage
host: 10.1.0.73
user: admin
env:
  CRYPTOGRAPHY_OPENSSL_NO_LEGACY: 1
cache: true

# see inventory plugin ansible.builtin.constructed
plugin: community.general.iocage
host: 10.1.0.73
user: admin
env:
  CRYPTOGRAPHY_OPENSSL_NO_LEGACY: 1
cache: true
strict: false
compose:
  ansible_host: iocage_ip4
  release: iocage_release | split('-') | first
groups:
  test: inventory_hostname.startswith('test')
keyed_groups:
  - prefix: distro
    key: iocage_release
  - prefix: state
    key: iocage_state
'''

import re
import os
from subprocess import Popen, PIPE

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display

display = Display()


def _parse_ip4(ip4):
    if ip4 == '-':
        return ip4
    return re.split('\\||/', ip4)[1]


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using iocage as source. '''

    NAME = 'community.general.iocage'
    IOCAGE = '/usr/local/bin/iocage'

    def __init__(self):
        super(InventoryModule, self).__init__()

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('iocage.yaml', 'iocage.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "iocage.yaml" nor "iocage.yml"')
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)
        cache_key = self.get_cache_key(path)

        user_cache_setting = self.get_option('cache')
        attempt_to_read_cache = user_cache_setting and cache
        cache_needs_update = user_cache_setting and not cache

        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        if not attempt_to_read_cache or cache_needs_update:
            results = self.get_inventory(path)
        if cache_needs_update:
            self._cache[cache_key] = results

        self.populate(results)

    def get_inventory(self, path):
        host = self.get_option('host')
        env = self.get_option('env')
        get_properties = self.get_option('get_properties')

        cmd = []
        my_env = os.environ.copy()
        if host == 'localhost':
            my_env.update({str(k): str(v) for k, v in env.items()})
        else:
            user = self.get_option('user')
            cmd.append("ssh")
            cmd.append(f"{user}@{host}")
            cmd.extend([f"{k}={v}" for k, v in env.items()])
        cmd.append(self.IOCAGE)

        cmd_list = cmd.copy()
        cmd_list.append('list')
        cmd_list.append('--header')
        cmd_list.append('--long')
        try:
            p = Popen(cmd_list, stdout=PIPE, stderr=PIPE, env=my_env)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise AnsibleError(f'Failed to run cmd={cmd_list}, rc={p.returncode}, stderr={to_native(stderr)}')

            try:
                t_stdout = to_text(stdout, errors='surrogate_or_strict')
            except UnicodeError as e:
                raise AnsibleError(f'Invalid (non unicode) input returned: {e}') from e

        except Exception as e:
            raise AnsibleParserError(f'Failed to parse {to_native(path)}: {e}') from e

        results = {'_meta': {'hostvars': {}}}
        self.get_jails(t_stdout, results)

        if get_properties:
            for hostname, host_vars in results['_meta']['hostvars'].items():
                cmd_get_properties = cmd.copy()
                cmd_get_properties.append("get")
                cmd_get_properties.append("--all")
                cmd_get_properties.append(f"{hostname}")
                try:
                    p = Popen(cmd_get_properties, stdout=PIPE, stderr=PIPE, env=my_env)
                    stdout, stderr = p.communicate()
                    if p.returncode != 0:
                        raise AnsibleError(
                            f'Failed to run cmd={cmd_get_properties}, rc={p.returncode}, stderr={to_native(stderr)}')

                    try:
                        t_stdout = to_text(stdout, errors='surrogate_or_strict')
                    except UnicodeError as e:
                        raise AnsibleError(f'Invalid (non unicode) input returned: {e}') from e

                except Exception as e:
                    raise AnsibleError(f'Failed to get properties: {e}') from e

                self.get_properties(t_stdout, results, hostname)

        return results

    def get_jails(self, t_stdout, results):
        jails = [x.split() for x in t_stdout.splitlines()]
        for jail in jails:
            iocage_name = jail[1]
            results['_meta']['hostvars'][iocage_name] = {}
            results['_meta']['hostvars'][iocage_name]['iocage_jid'] = jail[0]
            results['_meta']['hostvars'][iocage_name]['iocage_boot'] = jail[2]
            results['_meta']['hostvars'][iocage_name]['iocage_state'] = jail[3]
            results['_meta']['hostvars'][iocage_name]['iocage_type'] = jail[4]
            results['_meta']['hostvars'][iocage_name]['iocage_release'] = jail[5]
            results['_meta']['hostvars'][iocage_name]['iocage_ip4'] = _parse_ip4(jail[6])
            results['_meta']['hostvars'][iocage_name]['iocage_ip6'] = jail[7]
            results['_meta']['hostvars'][iocage_name]['iocage_template'] = jail[8]
            results['_meta']['hostvars'][iocage_name]['iocage_basejail'] = jail[9]

    def get_properties(self, t_stdout, results, hostname):
        properties = dict([x.split(':', 1) for x in t_stdout.splitlines()])
        results['_meta']['hostvars'][hostname]['iocage_properties'] = properties

    def populate(self, results):
        strict = self.get_option('strict')

        for hostname, host_vars in results['_meta']['hostvars'].items():
            self.inventory.add_host(hostname, group='all')
            for var, value in host_vars.items():
                self.inventory.set_variable(hostname, var, value)
            self._set_composite_vars(self.get_option('compose'), host_vars, hostname, strict=True)
            self._add_host_to_composed_groups(self.get_option('groups'), host_vars, hostname, strict=strict)
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host_vars, hostname, strict=strict)

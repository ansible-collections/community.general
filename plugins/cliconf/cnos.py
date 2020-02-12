# (C) 2017 Red Hat Inc.
# Copyright (C) 2017 Lenovo.
#
# GNU General Public License v3.0+
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Contains CLIConf Plugin methods for CNOS Modules
# Lenovo Networking
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
cliconf: cnos
short_description: Use cnos cliconf to run command on Lenovo CNOS platform
description:
  - This cnos plugin provides low level abstraction apis for
    sending and receiving CLI commands from Lenovo CNOS network devices.
'''

import re
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils._text import to_bytes, to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'cnos'
        reply = self.get('show sys-info')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        host = self.get('show hostname')
        hostname = to_text(host, errors='surrogate_or_strict').strip()
        if data:
            device_info['network_os_version'] = self.parse_version(data)
            device_info['network_os_model'] = self.parse_model(data)
            device_info['network_os_hostname'] = hostname

        return device_info

    def parse_version(self, data):
        for line in data.split('\n'):
            line = line.strip()
            match = re.match(r'System Software Revision (.*?)',
                             line, re.M | re.I)
            if match:
                vers = line.split(':')
                ver = vers[1].strip()
                return ver
        return "NA"

    def parse_model(self, data):
        for line in data.split('\n'):
            line = line.strip()
            match = re.match(r'System Model (.*?)', line, re.M | re.I)
            if match:
                mdls = line.split(':')
                mdl = mdls[1].strip()
                return mdl
        return "NA"

    @enable_mode
    def get_config(self, source='running', format='text', flags=None):
        if source not in ('running', 'startup'):
            msg = "fetching configuration from %s is not supported"
            return self.invalid_params(msg % source)
        if source == 'running':
            cmd = 'show running-config'
        else:
            cmd = 'show startup-config'
        return self.send_command(cmd)

    @enable_mode
    def edit_config(self, candidate=None, commit=True,
                    replace=None, comment=None):
        resp = {}
        results = []
        requests = []
        if commit:
            self.send_command('configure terminal')
            for line in to_list(candidate):
                if not isinstance(line, Mapping):
                    line = {'command': line}

                cmd = line['command']
                if cmd != 'end' and cmd[0] != '!':
                    results.append(self.send_command(**line))
                    requests.append(cmd)

            self.send_command('end')
        else:
            raise ValueError('check mode is not supported')

        resp['request'] = requests
        resp['response'] = results
        return resp

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        return json.dumps(result)

    def set_cli_prompt_context(self):
        """
        Make sure we are in the operational cli mode
        :return: None
        """
        if self._connection.connected:
            out = self._connection.get_prompt()

            if out is None:
                raise AnsibleConnectionFailure(message=u'cli prompt is not identified from the last received'
                                                       u' response window: %s' % self._connection._last_recv_window)

            if to_text(out, errors='surrogate_then_replace').strip().endswith(')#'):
                self._connection.queue_message('vvvv', 'In Config mode, sending exit to device')
                self._connection.send_command('exit')
            else:
                self._connection.send_command('enable')

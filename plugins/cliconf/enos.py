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
# Contains CLIConf Plugin methods for ENOS Modules
# Lenovo Networking
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
cliconf: enos
short_description: Use enos cliconf to run command on Lenovo ENOS platform
description:
  - This enos plugin provides low level abstraction apis for
    sending and receiving CLI commands from Lenovo ENOS network devices.
'''

import re
import json

from itertools import chain

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'enos'
        reply = self.get('show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'^Software Version (.*?) ', data, re.M | re.I)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'^Lenovo RackSwitch (\S+)', data, re.M | re.I)
        if match:
            device_info['network_os_model'] = match.group(1)

        match = re.search(r'^(.+) uptime', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)
        else:
            device_info['network_os_hostname'] = "NA"

        return device_info

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
    def edit_config(self, command):
        for cmd in chain(['configure terminal'], to_list(command), ['end']):
            self.send_command(cmd)

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

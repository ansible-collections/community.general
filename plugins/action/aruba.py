#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import copy

from ansible import constants as C
from ansible_collections.ansible.netcommon.plugins.action.network import ActionModule as ActionNetworkModule
from ansible_collections.community.general.plugins.module_utils.network.aruba.aruba import aruba_provider_spec
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import load_provider
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionNetworkModule):

    def run(self, tmp=None, task_vars=None):
        del tmp  # tmp no longer has any effect

        module_name = self._task.action.split('.')[-1]
        self._config_module = True if module_name == 'aruba_config' else False

        if self._play_context.connection != 'local':
            return dict(
                failed=True,
                msg='invalid connection specified, expected connection=local, '
                    'got %s' % self._play_context.connection
            )

        provider = load_provider(aruba_provider_spec, self._task.args)

        pc = copy.deepcopy(self._play_context)
        pc.connection = 'network_cli'
        pc.network_os = 'aruba'
        pc.remote_addr = provider['host'] or self._play_context.remote_addr
        pc.port = int(provider['port'] or self._play_context.port or 22)
        pc.remote_user = provider['username'] or self._play_context.connection_user
        pc.password = provider['password'] or self._play_context.password
        pc.private_key_file = provider['ssh_keyfile'] or self._play_context.private_key_file
        command_timeout = int(provider['timeout'] or C.PERSISTENT_COMMAND_TIMEOUT)

        display.vvv('using connection plugin %s (was local)' % pc.connection, pc.remote_addr)
        connection = self._shared_loader_obj.connection_loader.get('persistent', pc, sys.stdin, task_uuid=self._task._uuid)
        connection.set_options(direct={'persistent_command_timeout': command_timeout})

        socket_path = connection.run()
        display.vvvv('socket_path: %s' % socket_path, pc.remote_addr)
        if not socket_path:
            return {'failed': True,
                    'msg': 'unable to open shell. Please see: ' +
                           'https://docs.ansible.com/ansible/network_debug_troubleshooting.html#unable-to-open-shell'}

        task_vars['ansible_socket'] = socket_path

        if self._play_context.become_method == 'enable':
            self._play_context.become = False
            self._play_context.become_method = None

        result = super(ActionModule, self).run(task_vars=task_vars)
        return result

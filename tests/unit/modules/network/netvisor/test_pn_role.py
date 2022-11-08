# Copyright: (c) 2018, Pluribus Networks
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules.network.netvisor import pn_role
from ansible_collections.community.general.tests.unit.modules.utils import set_module_args
from ..nvos_module import TestNvosModule


class TestRoleModule(TestNvosModule):

    module = pn_role

    def setUp(self):
        self.mock_run_nvos_commands = patch('ansible_collections.community.general.plugins.modules.network.netvisor.pn_role.run_cli')
        self.run_nvos_commands = self.mock_run_nvos_commands.start()

        self.mock_run_check_cli = patch('ansible_collections.community.general.plugins.modules.network.netvisor.pn_role.check_cli')
        self.run_check_cli = self.mock_run_check_cli.start()

    def tearDown(self):
        self.mock_run_nvos_commands.stop()
        self.run_check_cli.stop()

    def run_cli_patch(self, module, cli, state_map):
        if state_map['present'] == 'role-create':
            results = dict(
                changed=True,
                cli_cmd=cli
            )
        elif state_map['absent'] == 'role-delete':
            results = dict(
                changed=True,
                cli_cmd=cli
            )
        elif state_map['update'] == 'role-modify':
            results = dict(
                changed=True,
                cli_cmd=cli
            )
        module.exit_json(**results)

    def load_fixtures(self, commands=None, state=None, transport='cli'):
        self.run_nvos_commands.side_effect = self.run_cli_patch
        if state == 'present':
            self.run_check_cli.return_value = False
        if state == 'absent':
            self.run_check_cli.return_value = True
        if state == 'update':
            self.run_check_cli.return_value = True

    def test_role_create(self):
        set_module_args({'pn_cliswitch': 'sw01', 'pn_name': 'foo',
                         'pn_scope': 'local', 'pn_access': 'read-only', 'state': 'present'})
        result = self.execute_module(changed=True, state='present')
        expected_cmd = ' switch sw01 role-create name foo  scope local access read-only'
        self.assertEqual(result['cli_cmd'], expected_cmd)

    def test_role_delete(self):
        set_module_args({'pn_cliswitch': 'sw01', 'pn_name': 'foo',
                         'state': 'absent'})
        result = self.execute_module(changed=True, state='absent')
        expected_cmd = ' switch sw01 role-delete name foo '
        self.assertEqual(result['cli_cmd'], expected_cmd)

    def test_role_update(self):
        set_module_args({'pn_cliswitch': 'sw01', 'pn_name': 'foo',
                         'pn_access': 'read-write', 'pn_sudo': True, 'pn_shell': True, 'state': 'update'})
        result = self.execute_module(changed=True, state='update')
        expected_cmd = ' switch sw01 role-modify name foo  access read-write shell  sudo '
        self.assertEqual(result['cli_cmd'], expected_cmd)

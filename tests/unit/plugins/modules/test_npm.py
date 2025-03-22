#
# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.plugins.modules import npm
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args


class NPMModuleTestCase(ModuleTestCase):
    module = npm

    def setUp(self):
        super(NPMModuleTestCase, self).setUp()
        ansible_module_path = "ansible_collections.community.general.plugins.modules.npm.AnsibleModule"
        self.mock_run_command = patch('%s.run_command' % ansible_module_path)
        self.module_main_command = self.mock_run_command.start()
        self.mock_get_bin_path = patch('%s.get_bin_path' % ansible_module_path)
        self.get_bin_path = self.mock_get_bin_path.start()
        self.get_bin_path.return_value = '/testbin/npm'

    def tearDown(self):
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        super(NPMModuleTestCase, self).tearDown()

    def module_main(self, exit_exc):
        with self.assertRaises(exit_exc) as exc:
            self.module.main()
        return exc.exception.args[0]

    def test_present(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'present'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'install', '--global', 'coffee-script'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_missing(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'present',
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"missing" : true}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'install', '--global', 'coffee-script'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_version(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'present',
            'version': '2.5.1'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'install', '--global', 'coffee-script@2.5.1'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_version_update(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'present',
            'version': '2.5.1'
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"version" : "2.5.0"}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'install', '--global', 'coffee-script@2.5.1'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_version_exists(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'present',
            'version': '2.5.1'
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"version" : "2.5.1"}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertFalse(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_absent(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'absent'
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"version" : "2.5.1"}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'uninstall', '--global', 'coffee-script'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_absent_version(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'absent',
            'version': '2.5.1'
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"version" : "2.5.1"}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'uninstall', '--global', 'coffee-script'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_absent_version_different(self):
        with set_module_args({
            'name': 'coffee-script',
            'global': 'true',
            'state': 'absent',
            'version': '2.5.1'
        }):
            self.module_main_command.side_effect = [
                (0, '{"dependencies": {"coffee-script": {"version" : "2.5.0"}}}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'list', '--json', '--long', '--global'], check_rc=False, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
            call(['/testbin/npm', 'uninstall', '--global', 'coffee-script'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_package_json(self):
        with set_module_args({
            'global': 'true',
            'state': 'present'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'install', '--global'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_package_json_production(self):
        with set_module_args({
            'production': 'true',
            'global': 'true',
            'state': 'present',
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'install', '--global', '--production'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_package_json_ci(self):
        with set_module_args({
            'ci': 'true',
            'global': 'true',
            'state': 'present'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'ci', '--global'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

    def test_present_package_json_ci_production(self):
        with set_module_args({
            'ci': 'true',
            'production': 'true',
            'global': 'true',
            'state': 'present'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/npm', 'ci', '--global', '--production'], check_rc=True, cwd=None, environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'}),
        ])

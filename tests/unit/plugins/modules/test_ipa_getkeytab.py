#
# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.plugins.modules import ipa_getkeytab
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args


class IPAKeytabModuleTestCase(ModuleTestCase):
    module = ipa_getkeytab

    def setUp(self):
        super(IPAKeytabModuleTestCase, self).setUp()
        ansible_module_path = "ansible_collections.community.general.plugins.modules.ipa_getkeytab.AnsibleModule"
        self.mock_run_command = patch('%s.run_command' % ansible_module_path)
        self.module_main_command = self.mock_run_command.start()
        self.mock_get_bin_path = patch('%s.get_bin_path' % ansible_module_path)
        self.get_bin_path = self.mock_get_bin_path.start()
        self.get_bin_path.return_value = '/testbin/ipa_getkeytab'

    def tearDown(self):
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        super(IPAKeytabModuleTestCase, self).tearDown()

    def module_main(self, exit_exc):
        with self.assertRaises(exit_exc) as exc:
            self.module.main()
        return exc.exception.args[0]

    def test_present(self):
        with set_module_args({
            'path': '/tmp/test.keytab',
            'principal': 'HTTP/freeipa-dc02.ipa.test',
            'ipa_host': 'freeipa-dc01.ipa.test',
            'state': 'present'
        }):
            self.module_main_command.side_effect = [
                (0, '{}', ''),
            ]

            result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/ipa_getkeytab',
                  '--keytab', '/tmp/test.keytab',
                  '--server', 'freeipa-dc01.ipa.test',
                  '--principal', 'HTTP/freeipa-dc02.ipa.test'
                  ],
                 check_rc=True,
                 environ_update={'LC_ALL': 'C', 'LANGUAGE': 'C'}
                 ),
        ])

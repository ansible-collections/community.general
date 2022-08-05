#
# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.plugins.modules.packaging.os import rpm_ostree_pkg
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args)


class RpmOSTreeModuleTestCase(ModuleTestCase):
    module = rpm_ostree_pkg

    def setUp(self):
        super(RpmOSTreeModuleTestCase, self).setUp()
        ansible_module_path = "ansible_collections.community.general.plugins.modules.packaging.os.rpm_ostree_pkg.AnsibleModule"
        self.mock_run_command = patch('%s.run_command' % ansible_module_path)
        self.module_main_command = self.mock_run_command.start()
        self.mock_get_bin_path = patch('%s.get_bin_path' % ansible_module_path)
        self.get_bin_path = self.mock_get_bin_path.start()
        self.get_bin_path.return_value = '/testbin/rpm-ostree'

    def tearDown(self):
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        super(RpmOSTreeModuleTestCase, self).tearDown()

    def module_main(self, exit_exc):
        with self.assertRaises(exit_exc) as exc:
            self.module.main()
        return exc.exception.args[0]

    def test_present(self):
        set_module_args({'name': 'nfs-utils', 'state': 'present'})
        self.module_main_command.side_effect = [
            (0, '', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.assertEqual(['nfs-utils'], result['packages'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/rpm-ostree', 'install', '--allow-inactive', '--idempotent', '--unchanged-exit-77', 'nfs-utils']),
        ])

    def test_present_unchanged(self):
        set_module_args({'name': 'nfs-utils', 'state': 'present'})
        self.module_main_command.side_effect = [
            (77, '', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertFalse(result['changed'])
        self.assertEqual(0, result['rc'])
        self.assertEqual(['nfs-utils'], result['packages'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/rpm-ostree', 'install', '--allow-inactive', '--idempotent', '--unchanged-exit-77', 'nfs-utils']),
        ])

    def test_present_failed(self):
        set_module_args({'name': 'nfs-utils', 'state': 'present'})
        self.module_main_command.side_effect = [
            (1, '', ''),
        ]

        result = self.module_main(AnsibleFailJson)

        self.assertFalse(result['changed'])
        self.assertEqual(1, result['rc'])
        self.assertEqual(['nfs-utils'], result['packages'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/rpm-ostree', 'install', '--allow-inactive', '--idempotent', '--unchanged-exit-77', 'nfs-utils']),
        ])

    def test_absent(self):
        set_module_args({'name': 'nfs-utils', 'state': 'absent'})
        self.module_main_command.side_effect = [
            (0, '', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.assertEqual(['nfs-utils'], result['packages'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/rpm-ostree', 'uninstall', '--allow-inactive', '--idempotent', '--unchanged-exit-77', 'nfs-utils']),
        ])

    def test_absent_failed(self):
        set_module_args({'name': 'nfs-utils', 'state': 'absent'})
        self.module_main_command.side_effect = [
            (1, '', ''),
        ]

        result = self.module_main(AnsibleFailJson)

        self.assertFalse(result['changed'])
        self.assertEqual(1, result['rc'])
        self.assertEqual(['nfs-utils'], result['packages'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/rpm-ostree', 'uninstall', '--allow-inactive', '--idempotent', '--unchanged-exit-77', 'nfs-utils']),
        ])

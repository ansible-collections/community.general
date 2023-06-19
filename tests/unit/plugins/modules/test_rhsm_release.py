# Copyright (c) 2018, Sean Myers <sean.myers@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import call, patch
from ansible_collections.community.general.plugins.modules import rhsm_release
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args)


class RhsmRepositoryReleaseModuleTestCase(ModuleTestCase):
    module = rhsm_release

    SUBMAN_KWARGS = dict(check_rc=True, expand_user_and_vars=False)

    def setUp(self):
        super(RhsmRepositoryReleaseModuleTestCase, self).setUp()

        # Mainly interested that the subscription-manager calls are right
        # based on the module args, so patch out run_command in the module.
        # returns (rc, out, err) structure
        self.mock_run_command = patch('ansible_collections.community.general.plugins.modules.rhsm_release.'
                                      'AnsibleModule.run_command')
        self.module_main_command = self.mock_run_command.start()

        # Module does a get_bin_path check before every run_command call
        self.mock_get_bin_path = patch('ansible_collections.community.general.plugins.modules.rhsm_release.'
                                       'AnsibleModule.get_bin_path')
        self.get_bin_path = self.mock_get_bin_path.start()
        self.get_bin_path.return_value = '/testbin/subscription-manager'

        # subscription-manager needs to be run as root
        self.mock_os_getuid = patch('ansible_collections.community.general.plugins.modules.rhsm_release.'
                                    'os.getuid')
        self.os_getuid = self.mock_os_getuid.start()
        self.os_getuid.return_value = 0

    def tearDown(self):
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        self.mock_os_getuid.stop()
        super(RhsmRepositoryReleaseModuleTestCase, self).tearDown()

    def module_main(self, exit_exc):
        with self.assertRaises(exit_exc) as exc:
            self.module.main()
        return exc.exception.args[0]

    def test_release_set(self):
        # test that the module attempts to change the release when the current
        # release is not the same as the user-specific target release
        set_module_args({'release': '7.5'})
        self.module_main_command.side_effect = [
            # first call, get_release: returns different version so set_release is called
            (0, '7.4', ''),
            # second call, set_release: just needs to exit with 0 rc
            (0, '', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.assertEqual('7.5', result['current_release'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/subscription-manager', 'release', '--show'], **self.SUBMAN_KWARGS),
            call(['/testbin/subscription-manager', 'release', '--set', '7.5'], **self.SUBMAN_KWARGS),
        ])

    def test_release_set_idempotent(self):
        # test that the module does not attempt to change the release when
        # the current release matches the user-specified target release
        set_module_args({'release': '7.5'})
        self.module_main_command.side_effect = [
            # first call, get_release: returns same version, set_release is not called
            (0, '7.5', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertFalse(result['changed'])
        self.assertEqual('7.5', result['current_release'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/subscription-manager', 'release', '--show'], **self.SUBMAN_KWARGS),
        ])

    def test_release_unset(self):
        # test that the module attempts to change the release when the current
        # release is not the same as the user-specific target release
        set_module_args({'release': None})
        self.module_main_command.side_effect = [
            # first call, get_release: returns version so set_release is called
            (0, '7.5', ''),
            # second call, set_release: just needs to exit with 0 rc
            (0, '', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertTrue(result['changed'])
        self.assertIsNone(result['current_release'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/subscription-manager', 'release', '--show'], **self.SUBMAN_KWARGS),
            call(['/testbin/subscription-manager', 'release', '--unset'], **self.SUBMAN_KWARGS),
        ])

    def test_release_unset_idempotent(self):
        # test that the module attempts to change the release when the current
        # release is not the same as the user-specific target release
        set_module_args({'release': None})
        self.module_main_command.side_effect = [
            # first call, get_release: returns no version, set_release is not called
            (0, 'Release not set', ''),
        ]

        result = self.module_main(AnsibleExitJson)

        self.assertFalse(result['changed'])
        self.assertIsNone(result['current_release'])
        self.module_main_command.assert_has_calls([
            call(['/testbin/subscription-manager', 'release', '--show'], **self.SUBMAN_KWARGS),
        ])

    def test_release_insane(self):
        # test that insane values for release trigger fail_json
        insane_value = 'this is an insane release value'
        set_module_args({'release': insane_value})

        result = self.module_main(AnsibleFailJson)

        # also ensure that the fail msg includes the insane value
        self.assertIn(insane_value, result['msg'])

    def test_release_matcher(self):
        # throw a few values at the release matcher -- only sane_values should match
        sane_values = ['1Server', '1Client', '10Server', '1.10', '10.0', '9']
        insane_values = [
            '6server',    # lowercase 's'
            '100Server',  # excessively long 'x' component
            '100.100',    # excessively long 'x' and 'y' components
            '+.-',        # illegal characters
        ]

        matches = self.module.release_matcher.findall(' '.join(sane_values + insane_values))

        # matches should be returned in the same order they were parsed,
        # so sorting shouldn't be necessary here
        self.assertEqual(matches, sane_values)

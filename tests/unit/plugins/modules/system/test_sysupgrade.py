# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase
from ansible_collections.community.general.plugins.modules.system import sysupgrade


class TestSysupgradeModule(ModuleTestCase):

    def setUp(self):
        super(TestSysupgradeModule, self).setUp()
        self.module = sysupgrade
        self.mock_get_bin_path = (patch('ansible.module_utils.basic.AnsibleModule.get_bin_path'))
        self.get_bin_path = self.mock_get_bin_path.start()

    def tearDown(self):
        super(TestSysupgradeModule, self).tearDown()
        self.mock_get_bin_path.stop()

    def test_upgrade_success(self):
        """ Upgrade was successful """

        rc = 0
        stdout = """
            SHA256.sig   100% |*************************************|  2141       00:00
            Signature Verified
            INSTALL.amd64 100% |************************************| 43512       00:00
            base67.tgz   100% |*************************************|   238 MB    02:16
            bsd          100% |*************************************| 18117 KB    00:24
            bsd.mp       100% |*************************************| 18195 KB    00:17
            bsd.rd       100% |*************************************| 10109 KB    00:14
            comp67.tgz   100% |*************************************| 74451 KB    00:53
            game67.tgz   100% |*************************************|  2745 KB    00:03
            man67.tgz    100% |*************************************|  7464 KB    00:04
            xbase67.tgz  100% |*************************************| 22912 KB    00:30
            xfont67.tgz  100% |*************************************| 39342 KB    00:28
            xserv67.tgz  100% |*************************************| 16767 KB    00:24
            xshare67.tgz 100% |*************************************|  4499 KB    00:06
            Verifying sets.
            Fetching updated firmware.
            Will upgrade on next reboot
        """
        stderr = ""

        with patch.object(basic.AnsibleModule, "run_command") as run_command:
            run_command.return_value = (rc, stdout, stderr)
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])

    def test_upgrade_failed(self):
        """ Upgrade failed """

        rc = 1
        stdout = ""
        stderr = "sysupgrade: need root privileges"

        with patch.object(basic.AnsibleModule, "run_command") as run_command_mock:
            run_command_mock.return_value = (rc, stdout, stderr)
            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()
            self.assertTrue(result.exception.args[0]['failed'])
            self.assertIn('need root', result.exception.args[0]['msg'])

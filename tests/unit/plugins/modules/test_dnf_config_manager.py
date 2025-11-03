# Copyright (c) 2023, Andrew Hyatt <andy@hyatt.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from unittest.mock import patch, call
from ansible_collections.community.general.plugins.modules import dnf_config_manager as dnf_config_manager_module
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

# Return value on all-default arguments
mock_repolist_crb_enabled = """Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install
DNF version: 4.14.0
cachedir: /var/cache/dnf
Last metadata expiration check: 1:20:49 ago on Fri 22 Dec 2023 06:05:13 PM UTC.
Repo-id            : appstream
Repo-name          : AlmaLinux 9 - AppStream
Repo-status        : enabled
Repo-revision      : 1703240474
Repo-updated       : Fri 22 Dec 2023 10:21:14 AM UTC
Repo-pkgs          : 5,897
Repo-available-pkgs: 5,728
Repo-size          : 9.5 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/AppStream/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : appstream-debuginfo
Repo-name          : AlmaLinux 9 - AppStream - Debug
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-debug
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : appstream-source
Repo-name          : AlmaLinux 9 - AppStream - Source
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-source
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : baseos
Repo-name          : AlmaLinux 9 - BaseOS
Repo-status        : enabled
Repo-revision      : 1703240561
Repo-updated       : Fri 22 Dec 2023 10:22:41 AM UTC
Repo-pkgs          : 1,244
Repo-available-pkgs: 1,244
Repo-size          : 1.3 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/BaseOS/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : baseos-debuginfo
Repo-name          : AlmaLinux 9 - BaseOS - Debug
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos-debug
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : baseos-source
Repo-name          : AlmaLinux 9 - BaseOS - Source
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos-source
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh
Repo-name          : Copr repo for dracut-crypt-ssh owned by uriesk
Repo-status        : enabled
Repo-revision      : 1698291016
Repo-updated       : Thu 26 Oct 2023 03:30:16 AM UTC
Repo-pkgs          : 4
Repo-available-pkgs: 4
Repo-size          : 102 k
Repo-baseurl       : https://download.copr.fedorainfracloud.org/results/uriesk/dracut-crypt-ssh/epel-9-x86_64/
Repo-expire        : 172,800 second(s) (last: Fri 22 Dec 2023 06:05:10 PM UTC)
Repo-filename      : /etc/yum.repos.d/_copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh.repo

Repo-id            : crb
Repo-name          : AlmaLinux 9 - CRB
Repo-status        : enabled
Repo-revision      : 1703240590
Repo-updated       : Fri 22 Dec 2023 10:23:10 AM UTC
Repo-pkgs          : 1,730
Repo-available-pkgs: 1,727
Repo-size          : 13 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/crb
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/CRB/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-crb.repo

Repo-id            : rpmfusion-nonfree-updates
Repo-name          : RPM Fusion for EL 9 - Nonfree - Updates
Repo-status        : enabled
Repo-revision      : 1703248251
Repo-tags          : binary-x86_64
Repo-updated       : Fri 22 Dec 2023 12:30:53 PM UTC
Repo-pkgs          : 65
Repo-available-pkgs: 65
Repo-size          : 944 M
Repo-metalink      : http://mirrors.rpmfusion.org/metalink?repo=nonfree-el-updates-released-9&arch=x86_64
  Updated          : Fri 22 Dec 2023 06:05:13 PM UTC
Repo-baseurl       : http://uvermont.mm.fcix.net/rpmfusion/nonfree/el/updates/9/x86_64/ (33 more)
Repo-expire        : 172,800 second(s) (last: Fri 22 Dec 2023 06:05:13 PM UTC)
Repo-filename      : /etc/yum.repos.d/rpmfusion-nonfree-updates.repo
Total packages: 28,170
"""

mock_repolist_crb_disabled = """Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install
DNF version: 4.14.0
cachedir: /var/cache/dnf
Last metadata expiration check: 1:20:49 ago on Fri 22 Dec 2023 06:05:13 PM UTC.
Repo-id            : appstream
Repo-name          : AlmaLinux 9 - AppStream
Repo-status        : enabled
Repo-revision      : 1703240474
Repo-updated       : Fri 22 Dec 2023 10:21:14 AM UTC
Repo-pkgs          : 5,897
Repo-available-pkgs: 5,728
Repo-size          : 9.5 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/AppStream/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : appstream-debuginfo
Repo-name          : AlmaLinux 9 - AppStream - Debug
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-debug
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : appstream-source
Repo-name          : AlmaLinux 9 - AppStream - Source
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-source
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : baseos
Repo-name          : AlmaLinux 9 - BaseOS
Repo-status        : enabled
Repo-revision      : 1703240561
Repo-updated       : Fri 22 Dec 2023 10:22:41 AM UTC
Repo-pkgs          : 1,244
Repo-available-pkgs: 1,244
Repo-size          : 1.3 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/BaseOS/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : baseos-debuginfo
Repo-name          : AlmaLinux 9 - BaseOS - Debug
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos-debug
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : baseos-source
Repo-name          : AlmaLinux 9 - BaseOS - Source
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/baseos-source
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-baseos.repo

Repo-id            : copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh
Repo-name          : Copr repo for dracut-crypt-ssh owned by uriesk
Repo-status        : enabled
Repo-revision      : 1698291016
Repo-updated       : Thu 26 Oct 2023 03:30:16 AM UTC
Repo-pkgs          : 4
Repo-available-pkgs: 4
Repo-size          : 102 k
Repo-baseurl       : https://download.copr.fedorainfracloud.org/results/uriesk/dracut-crypt-ssh/epel-9-x86_64/
Repo-expire        : 172,800 second(s) (last: Fri 22 Dec 2023 06:05:10 PM UTC)
Repo-filename      : /etc/yum.repos.d/_copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh.repo

Repo-id            : crb
Repo-name          : AlmaLinux 9 - CRB
Repo-status        : disabled
Repo-revision      : 1703240590
Repo-updated       : Fri 22 Dec 2023 10:23:10 AM UTC
Repo-pkgs          : 1,730
Repo-available-pkgs: 1,727
Repo-size          : 13 G
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/crb
Repo-baseurl       : http://mirror.cogentco.com/pub/linux/almalinux/9.3/CRB/x86_64/os/ (9 more)
Repo-expire        : 86,400 second(s) (last: Fri 22 Dec 2023 06:05:11 PM UTC)
Repo-filename      : /etc/yum.repos.d/almalinux-crb.repo

Repo-id            : rpmfusion-nonfree-updates
Repo-name          : RPM Fusion for EL 9 - Nonfree - Updates
Repo-status        : enabled
Repo-revision      : 1703248251
Repo-tags          : binary-x86_64
Repo-updated       : Fri 22 Dec 2023 12:30:53 PM UTC
Repo-pkgs          : 65
Repo-available-pkgs: 65
Repo-size          : 944 M
Repo-metalink      : http://mirrors.rpmfusion.org/metalink?repo=nonfree-el-updates-released-9&arch=x86_64
  Updated          : Fri 22 Dec 2023 06:05:13 PM UTC
Repo-baseurl       : http://uvermont.mm.fcix.net/rpmfusion/nonfree/el/updates/9/x86_64/ (33 more)
Repo-expire        : 172,800 second(s) (last: Fri 22 Dec 2023 06:05:13 PM UTC)
Repo-filename      : /etc/yum.repos.d/rpmfusion-nonfree-updates.repo
Total packages: 28,170
"""

mock_repolist_no_status = """Repo-id            : appstream-debuginfo
Repo-name          : AlmaLinux 9 - AppStream - Debug
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-debug
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo

Repo-id            : appstream-source
Repo-name          : AlmaLinux 9 - AppStream - Source
Repo-status        : disabled
Repo-mirrors       : https://mirrors.almalinux.org/mirrorlist/9/appstream-source
Repo-expire        : 86,400 second(s) (last: unknown)
Repo-filename      : /etc/yum.repos.d/almalinux-appstream.repo
"""

mock_repolist_status_before_id = """
Repo-id            : appstream-debuginfo
Repo-status        : disabled
Repo-status        : disabled
"""

expected_repo_states_crb_enabled = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "crb",
        "rpmfusion-nonfree-updates",
    ],
}

expected_repo_states_crb_disabled = {
    "disabled": ["appstream-debuginfo", "appstream-source", "baseos-debuginfo", "baseos-source", "crb"],
    "enabled": [
        "appstream",
        "baseos",
        "copr:copr.fedorainfracloud.org:uriesk:dracut-crypt-ssh",
        "rpmfusion-nonfree-updates",
    ],
}

call_get_repo_states = call(["/usr/bin/dnf", "repolist", "--all", "--verbose"], check_rc=True)
call_disable_crb = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-disabled", "crb"], check_rc=True)
call_enable_crb = call(["/usr/bin/dnf", "config-manager", "--assumeyes", "--set-enabled", "crb"], check_rc=True)


class TestDNFConfigManager(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_run_command = patch("ansible.module_utils.basic.AnsibleModule.run_command")
        self.run_command = self.mock_run_command.start()
        self.mock_path_exists = patch("os.path.exists")
        self.path_exists = self.mock_path_exists.start()
        self.path_exists.return_value = True
        self.module = dnf_config_manager_module

    def tearDown(self):
        super().tearDown()
        self.mock_run_command.stop()
        self.mock_path_exists.stop()

    def set_command_mock(self, execute_return=(0, "", ""), execute_side_effect=None):
        self.run_command.reset_mock()
        self.run_command.return_value = execute_return
        self.run_command.side_effect = execute_side_effect

    def execute_module(self, failed=False, changed=False):
        if failed:
            result = self.failed()
            self.assertTrue(result["failed"])
        else:
            result = self.changed(changed)
            self.assertEqual(result["changed"], changed)

        return result

    def failed(self):
        with self.assertRaises(AnsibleFailJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertTrue(result["failed"])
        return result

    def changed(self, changed=False):
        with self.assertRaises(AnsibleExitJson) as exc:
            self.module.main()

        result = exc.exception.args[0]
        self.assertEqual(result["changed"], changed)
        return result

    def test_get_repo_states(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, mock_repolist_crb_enabled, ""))
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(calls=[call_get_repo_states, call_get_repo_states], any_order=False)

    def test_enable_disabled_repo(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, mock_repolist_crb_disabled, ""), (0, "", ""), (0, mock_repolist_crb_enabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_disabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], ["crb"])
        expected_calls = [call_get_repo_states, call_enable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_enable_disabled_repo_check_mode(self):
        with set_module_args({"name": ["crb"], "state": "enabled", "_ansible_check_mode": True}):
            side_effects = [(0, mock_repolist_crb_disabled, ""), (0, mock_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["changed_repos"], ["crb"])
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_disable_enabled_repo(self):
        with set_module_args({"name": ["crb"], "state": "disabled"}):
            side_effects = [(0, mock_repolist_crb_enabled, ""), (0, "", ""), (0, mock_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=True)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_disabled)
        self.assertEqual(result["changed_repos"], ["crb"])
        expected_calls = [call_get_repo_states, call_disable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

    def test_crb_already_enabled(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, mock_repolist_crb_enabled, ""), (0, mock_repolist_crb_enabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(changed=False)
        self.assertEqual(result["repo_states_pre"], expected_repo_states_crb_enabled)
        self.assertEqual(result["repo_states_post"], expected_repo_states_crb_enabled)
        self.assertEqual(result["changed_repos"], [])
        self.run_command.assert_has_calls(calls=[call_get_repo_states, call_get_repo_states], any_order=False)

    def test_get_repo_states_fail_no_status(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, mock_repolist_no_status, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed another repo id before next status")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_get_repo_states_fail_status_before_id(self):
        with set_module_args({}):
            self.set_command_mock(execute_return=(0, mock_repolist_status_before_id, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf repolist parse failure: parsed status before repo id")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_failed__unknown_repo_id(self):
        with set_module_args({"name": ["fake"]}):
            self.set_command_mock(execute_return=(0, mock_repolist_crb_disabled, ""))
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "did not find repo with ID 'fake' in dnf repolist --all --verbose")
        self.run_command.assert_has_calls(calls=[call_get_repo_states], any_order=False)

    def test_failed_state_change_ineffective(self):
        with set_module_args({"name": ["crb"], "state": "enabled"}):
            side_effects = [(0, mock_repolist_crb_disabled, ""), (0, "", ""), (0, mock_repolist_crb_disabled, "")]
            self.set_command_mock(execute_side_effect=side_effects)
            result = self.execute_module(failed=True)
        self.assertEqual(result["msg"], "dnf config-manager failed to make 'crb' enabled")
        expected_calls = [call_get_repo_states, call_enable_crb, call_get_repo_states]
        self.run_command.assert_has_calls(calls=expected_calls, any_order=False)

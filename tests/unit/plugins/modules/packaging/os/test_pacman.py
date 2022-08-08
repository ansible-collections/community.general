# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys


from ansible.module_utils import basic
from ansible_collections.community.general.tests.unit.compat import mock, unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    exit_json,
    fail_json,
)

from ansible_collections.community.general.plugins.modules.packaging.os import pacman
from ansible_collections.community.general.plugins.modules.packaging.os.pacman import (
    Package,
    VersionTuple,
)

import pytest
import json


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


# This inventory data is tightly coupled with the inventory test and the mock_valid_inventory fixture
valid_inventory = {
    "installed_pkgs": {
        "file": "5.41-1",
        "filesystem": "2021.11.11-1",
        "findutils": "4.8.0-1",
        "gawk": "5.1.1-1",
        "gettext": "0.21-1",
        "grep": "3.7-1",
        "gzip": "1.11-1",
        "pacman": "6.0.1-2",
        "pacman-mirrorlist": "20211114-1",
        "sed": "4.8-1",
        "sqlite": "3.36.0-1",
    },
    "installed_groups": {
        "base-devel": set(["gawk", "grep", "file", "findutils", "pacman", "sed", "gzip", "gettext"])
    },
    "available_pkgs": {
        "acl": "2.3.1-1",
        "amd-ucode": "20211027.1d00989-1",
        "archlinux-keyring": "20211028-1",
        "argon2": "20190702-3",
        "attr": "2.5.1-1",
        "audit": "3.0.6-5",
        "autoconf": "2.71-1",
        "automake": "1.16.5-1",
        "b43-fwcutter": "019-3",
        "gawk": "5.1.1-1",
        "grep": "3.7-1",
        "sqlite": "3.37.0-1",
        "sudo": "1.9.8.p2-3",
    },
    "available_groups": {
        "base-devel": set(
            [
                "libtool",
                "gawk",
                "which",
                "texinfo",
                "fakeroot",
                "grep",
                "findutils",
                "autoconf",
                "gzip",
                "pkgconf",
                "flex",
                "patch",
                "groff",
                "m4",
                "bison",
                "gcc",
                "gettext",
                "make",
                "file",
                "pacman",
                "sed",
                "automake",
                "sudo",
                "binutils",
            ]
        ),
        "some-group": set(["libtool", "sudo", "binutils"]),
    },
    "upgradable_pkgs": {
        "sqlite": VersionTuple(current="3.36.0-1", latest="3.37.0-1"),
    },
    "pkg_reasons": {
        "file": "explicit",
        "filesystem": "explicit",
        "findutils": "explicit",
        "gawk": "explicit",
        "gettext": "explicit",
        "grep": "explicit",
        "gzip": "explicit",
        "pacman": "explicit",
        "pacman-mirrorlist": "dependency",
        "sed": "explicit",
        "sqlite": "explicit",
    },
}

empty_inventory = {
    "installed_pkgs": {},
    "available_pkgs": {},
    "installed_groups": {},
    "available_groups": {},
    "upgradable_pkgs": {},
    "pkg_reasons": {},
}


class TestPacman:
    @pytest.fixture(autouse=True)
    def run_command(self, mocker):
        self.mock_run_command = mocker.patch.object(basic.AnsibleModule, "run_command", autospec=True)

    @pytest.fixture
    def mock_package_list(self, mocker):
        return mocker.patch.object(pacman.Pacman, "package_list", autospec=True)

    @pytest.fixture(autouse=True)
    def common(self, mocker):
        self.mock_module = mocker.patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
            get_bin_path=get_bin_path,
        )

    @pytest.fixture
    def mock_empty_inventory(self, mocker):
        inv = empty_inventory
        return mocker.patch.object(pacman.Pacman, "_build_inventory", return_value=inv)

    @pytest.fixture
    def mock_valid_inventory(self, mocker):
        return mocker.patch.object(pacman.Pacman, "_build_inventory", return_value=valid_inventory)

    def test_fail_without_required_args(self):
        with pytest.raises(AnsibleFailJson) as e:
            set_module_args({})
            pacman.main()
        assert e.match(r"one of the following is required")

    def test_success(self, mock_empty_inventory):
        set_module_args({"update_cache": True})  # Simplest args to let init go through
        P = pacman.Pacman(pacman.setup_module())
        with pytest.raises(AnsibleExitJson) as e:
            P.success()

    def test_fail(self, mock_empty_inventory):
        set_module_args({"update_cache": True})
        P = pacman.Pacman(pacman.setup_module())

        args = dict(
            msg="msg", stdout="something", stderr="somethingelse", cmd=["command", "with", "args"], rc=1
        )
        with pytest.raises(AnsibleFailJson) as e:
            P.fail(**args)

        assert all(item in e.value.args[0] for item in args)

    @pytest.mark.parametrize(
        "expected, run_command_side_effect, raises",
        [
            (
                # Regular run
                valid_inventory,
                [
                    [  # pacman --query
                        0,
                        """file 5.41-1
                        filesystem 2021.11.11-1
                        findutils 4.8.0-1
                        gawk 5.1.1-1
                        gettext 0.21-1
                        grep 3.7-1
                        gzip 1.11-1
                        pacman 6.0.1-2
                        pacman-mirrorlist 20211114-1
                        sed 4.8-1
                        sqlite 3.36.0-1
                        """,
                        "",
                    ],
                    (  # pacman --query --group
                        0,
                        """base-devel file
                        base-devel findutils
                        base-devel gawk
                        base-devel gettext
                        base-devel grep
                        base-devel gzip
                        base-devel pacman
                        base-devel sed
                        """,
                        "",
                    ),
                    (  # pacman --sync --list
                        0,
                        """core acl 2.3.1-1 [installed]
                        core amd-ucode 20211027.1d00989-1
                        core archlinux-keyring 20211028-1 [installed]
                        core argon2 20190702-3 [installed]
                        core attr 2.5.1-1 [installed]
                        core audit 3.0.6-5 [installed: 3.0.6-2]
                        core autoconf 2.71-1
                        core automake 1.16.5-1
                        core b43-fwcutter 019-3
                        core gawk 5.1.1-1 [installed]
                        core grep 3.7-1 [installed]
                        core sqlite 3.37.0-1 [installed: 3.36.0-1]
                        code sudo 1.9.8.p2-3
                        """,
                        "",
                    ),
                    (  # pacman --sync --group --group
                        0,
                        """base-devel autoconf
                        base-devel automake
                        base-devel binutils
                        base-devel bison
                        base-devel fakeroot
                        base-devel file
                        base-devel findutils
                        base-devel flex
                        base-devel gawk
                        base-devel gcc
                        base-devel gettext
                        base-devel grep
                        base-devel groff
                        base-devel gzip
                        base-devel libtool
                        base-devel m4
                        base-devel make
                        base-devel pacman
                        base-devel patch
                        base-devel pkgconf
                        base-devel sed
                        base-devel sudo
                        base-devel texinfo
                        base-devel which
                        some-group libtool
                        some-group sudo
                        some-group binutils
                        """,
                        "",
                    ),
                    (  # pacman --query --upgrades
                        0,
                        """sqlite 3.36.0-1 -> 3.37.0-1
                        systemd 249.6-3 -> 249.7-2 [ignored]
                        """,
                        "",
                    ),
                    (  # pacman --query --explicit
                        0,
                        """file 5.41-1
                        filesystem 2021.11.11-1
                        findutils 4.8.0-1
                        gawk 5.1.1-1
                        gettext 0.21-1
                        grep 3.7-1
                        gzip 1.11-1
                        pacman 6.0.1-2
                        sed 4.8-1
                        sqlite 3.36.0-1
                        """,
                        "",
                    ),
                    (  # pacman --query --deps
                        0,
                        """pacman-mirrorlist 20211114-1
                        """,
                        "",
                    ),
                ],
                None,
            ),
            (
                # All good, but call to --query --upgrades return 1. aka nothing to upgrade
                # with a pacman warning
                empty_inventory,
                [
                    (0, "", ""),
                    (0, "", ""),
                    (0, "", ""),
                    (0, "", ""),
                    (
                        1,
                        "",
                        "warning: config file /etc/pacman.conf, line 34: directive 'TotalDownload' in section 'options' not recognized.",
                    ),
                    (0, "", ""),
                    (0, "", ""),
                ],
                None,
            ),
            (
                # failure
                empty_inventory,
                [
                    (0, "", ""),
                    (0, "", ""),
                    (0, "", ""),
                    (0, "", ""),
                    (
                        1,
                        "partial\npkg\\nlist",
                        "some warning",
                    ),
                    (0, "", ""),
                    (0, "", ""),
                ],
                AnsibleFailJson,
            ),
        ],
    )
    def test_build_inventory(self, expected, run_command_side_effect, raises):
        self.mock_run_command.side_effect = run_command_side_effect

        set_module_args({"update_cache": True})
        if raises:
            with pytest.raises(raises):
                P = pacman.Pacman(pacman.setup_module())
                P._build_inventory()
        else:
            P = pacman.Pacman(pacman.setup_module())
            assert P._build_inventory() == expected

    @pytest.mark.parametrize("check_mode_value", [True, False])
    def test_upgrade_check_empty_inventory(self, mock_empty_inventory, check_mode_value):
        set_module_args({"upgrade": True, "_ansible_check_mode": check_mode_value})
        P = pacman.Pacman(pacman.setup_module())
        with pytest.raises(AnsibleExitJson) as e:
            P.run()
        self.mock_run_command.call_count == 0
        out = e.value.args[0]
        assert "packages" not in out
        assert not out["changed"]
        assert "diff" not in out

    def test_update_db_check(self, mock_empty_inventory):
        set_module_args({"update_cache": True, "_ansible_check_mode": True})
        P = pacman.Pacman(pacman.setup_module())

        with pytest.raises(AnsibleExitJson) as e:
            P.run()
        self.mock_run_command.call_count == 0
        out = e.value.args[0]
        assert "packages" not in out
        assert out["changed"]

    @pytest.mark.parametrize(
        "module_args,expected_calls,changed",
        [
            (
                {},
                [
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'a\nb\nc', ''),
                    (["pacman", "--sync", "--refresh"], {'check_rc': False}, 0, 'stdout', 'stderr'),
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'b\na\nc', ''),
                ],
                False,
            ),
            (
                {"force": True},
                [
                    (["pacman", "--sync", "--refresh", "--refresh"], {'check_rc': False}, 0, 'stdout', 'stderr'),
                ],
                True,
            ),
            (
                {"update_cache_extra_args": "--some-extra args"},  # shlex test
                [
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'a\nb\nc', ''),
                    (["pacman", "--sync", "--refresh", "--some-extra", "args"], {'check_rc': False}, 0, 'stdout', 'stderr'),
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'a changed\nb\nc', ''),
                ],
                True,
            ),
            (
                {"force": True, "update_cache_extra_args": "--some-extra args"},
                [
                    (["pacman", "--sync", "--refresh", "--some-extra", "args", "--refresh"], {'check_rc': False}, 0, 'stdout', 'stderr'),
                ],
                True,
            ),
            (
                # Test whether pacman --sync --list is not called more than twice
                {"upgrade": True},
                [
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'core foo 1.0.0-1 [installed]', ''),
                    (["pacman", "--sync", "--refresh"], {'check_rc': False}, 0, 'stdout', 'stderr'),
                    (["pacman", "--sync", "--list"], {'check_rc': True}, 0, 'core foo 1.0.0-1 [installed]', ''),
                    # The following is _build_inventory:
                    (["pacman", "--query"], {'check_rc': True}, 0, 'foo 1.0.0-1', ''),
                    (["pacman", "--query", "--groups"], {'check_rc': True}, 0, '', ''),
                    (["pacman", "--sync", "--groups", "--groups"], {'check_rc': True}, 0, '', ''),
                    (["pacman", "--query", "--upgrades"], {'check_rc': False}, 0, '', ''),
                    (["pacman", "--query", "--explicit"], {'check_rc': True}, 0, 'foo 1.0.0-1', ''),
                    (["pacman", "--query", "--deps"], {'check_rc': True}, 0, '', ''),
                ],
                False,
            ),
        ],
    )
    def test_update_db(self, module_args, expected_calls, changed):
        args = {"update_cache": True}
        args.update(module_args)
        set_module_args(args)

        self.mock_run_command.side_effect = [
            (rc, stdout, stderr) for expected_call, kwargs, rc, stdout, stderr in expected_calls
        ]
        with pytest.raises(AnsibleExitJson) as e:
            P = pacman.Pacman(pacman.setup_module())
            P.run()

        self.mock_run_command.assert_has_calls([
            mock.call(mock.ANY, expected_call, **kwargs) for expected_call, kwargs, rc, stdout, stderr in expected_calls
        ])
        out = e.value.args[0]
        assert out["cache_updated"] == changed
        assert out["changed"] == changed

    @pytest.mark.parametrize(
        "check_mode_value, run_command_data, upgrade_extra_args",
        [
            # just check
            (True, None, None),
            (
                # for real
                False,
                {
                    "args": ["pacman", "--sync", "--sysupgrade", "--quiet", "--noconfirm"],
                    "return_value": [0, "stdout", "stderr"],
                },
                None,
            ),
            (
                # with extra args
                False,
                {
                    "args": [
                        "pacman",
                        "--sync",
                        "--sysupgrade",
                        "--quiet",
                        "--noconfirm",
                        "--some",
                        "value",
                    ],
                    "return_value": [0, "stdout", "stderr"],
                },
                "--some value",
            ),
        ],
    )
    def test_upgrade(self, mock_valid_inventory, check_mode_value, run_command_data, upgrade_extra_args):
        args = {"upgrade": True, "_ansible_check_mode": check_mode_value}
        if upgrade_extra_args:
            args["upgrade_extra_args"] = upgrade_extra_args
        set_module_args(args)

        if run_command_data and "return_value" in run_command_data:
            self.mock_run_command.return_value = run_command_data["return_value"]

        P = pacman.Pacman(pacman.setup_module())

        with pytest.raises(AnsibleExitJson) as e:
            P.run()
        out = e.value.args[0]

        if check_mode_value:
            self.mock_run_command.call_count == 0

        if run_command_data and "args" in run_command_data:
            self.mock_run_command.assert_called_with(mock.ANY, run_command_data["args"], check_rc=False)
            assert out["stdout"] == "stdout"
            assert out["stderr"] == "stderr"

        assert len(out["packages"]) == 1 and "sqlite" in out["packages"]
        assert out["changed"]
        assert out["diff"]["before"] and out["diff"]["after"]

    def test_upgrade_fail(self, mock_valid_inventory):
        set_module_args({"upgrade": True})
        self.mock_run_command.return_value = [1, "stdout", "stderr"]
        P = pacman.Pacman(pacman.setup_module())

        with pytest.raises(AnsibleFailJson) as e:
            P.run()
        self.mock_run_command.call_count == 1
        out = e.value.args[0]
        assert out["failed"]
        assert out["stdout"] == "stdout"
        assert out["stderr"] == "stderr"

    @pytest.mark.parametrize(
        "state, pkg_names, expected, run_command_data, raises",
        [
            # regular packages, no resolving required
            (
                "present",
                ["acl", "attr"],
                [Package(name="acl", source="acl"), Package(name="attr", source="attr")],
                None,
                None,
            ),
            (
                # group expansion
                "present",
                ["acl", "some-group", "attr"],
                [
                    Package(name="acl", source="acl"),
                    Package(name="binutils", source="binutils"),
                    Package(name="libtool", source="libtool"),
                    Package(name="sudo", source="sudo"),
                    Package(name="attr", source="attr"),
                ],
                None,
                None,
            ),
            (
                # <repo>/<pkgname> format -> call to pacman to resolve
                "present",
                ["community/elixir"],
                [Package(name="elixir", source="community/elixir")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            ["pacman", "--sync", "--print-format", "%n", "community/elixir"],
                            check_rc=False,
                        )
                    ],
                    "side_effect": [(0, "elixir", "")],
                },
                None,
            ),
            (
                # catch all -> call to pacman to resolve (--sync and --upgrade)
                "present",
                ["somepackage-12.3-x86_64.pkg.tar.zst"],
                [
                    Package(
                        name="somepackage",
                        source="somepackage-12.3-x86_64.pkg.tar.zst",
                        source_is_URL=True,
                    )
                ],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--sync",
                                "--print-format",
                                "%n",
                                "somepackage-12.3-x86_64.pkg.tar.zst",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--upgrade",
                                "--print-format",
                                "%n",
                                "somepackage-12.3-x86_64.pkg.tar.zst",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(1, "", "nope"), (0, "somepackage", "")],
                },
                None,
            ),
            (
                # install a package that doesn't exist. call pacman twice and give up
                "present",
                ["unknown-package"],
                [],
                {
                    # no call validation, since it will fail
                    "side_effect": [(1, "", "nope"), (1, "", "stillnope")],
                },
                AnsibleFailJson,
            ),
            (
                # Edge case: resolve a pkg that doesn't exist when trying to remove it (state == absent).
                # will fallback to file + url format but not complain since it is already not there
                # Can happen if a pkg is removed for the repos  (or if a repo is disabled/removed)
                "absent",
                ["unknown-package-to-remove"],
                [],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            ["pacman", "--sync", "--print-format", "%n", "unknown-package-to-remove"],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            ["pacman", "--upgrade", "--print-format", "%n", "unknown-package-to-remove"],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(1, "", "nope"), (1, "", "stillnope")],
                },
                None,  # Doesn't fail
            ),
        ],
    )
    def test_package_list(
        self, mock_valid_inventory, state, pkg_names, expected, run_command_data, raises
    ):
        set_module_args({"name": pkg_names, "state": state})
        P = pacman.Pacman(pacman.setup_module())
        P.inventory = P._build_inventory()
        if run_command_data:
            self.mock_run_command.side_effect = run_command_data["side_effect"]

        if raises:
            with pytest.raises(raises):
                P.package_list()
        else:
            assert sorted(P.package_list()) == sorted(expected)
            if run_command_data:
                assert self.mock_run_command.mock_calls == run_command_data["calls"]

    @pytest.mark.parametrize("check_mode_value", [True, False])
    @pytest.mark.parametrize(
        "name, state, package_list",
        [
            (["already-absent"], "absent", [Package("already-absent", "already-absent")]),
            (["grep"], "present", [Package("grep", "grep")]),
        ],
    )
    def test_op_packages_nothing_to_do(
        self, mock_valid_inventory, mock_package_list, check_mode_value, name, state, package_list
    ):
        set_module_args({"name": name, "state": state, "_ansible_check_mode": check_mode_value})
        mock_package_list.return_value = package_list
        P = pacman.Pacman(pacman.setup_module())
        with pytest.raises(AnsibleExitJson) as e:
            P.run()
        out = e.value.args[0]
        assert not out["changed"]
        assert "packages" in out
        assert "diff" not in out
        self.mock_run_command.call_count == 0

    @pytest.mark.parametrize(
        "module_args, expected_packages, package_list_out, run_command_data, raises",
        [
            (
                # remove pkg: Check mode -- call to print format but that's it
                {"_ansible_check_mode": True, "name": ["grep"], "state": "absent"},
                ["grep-version"],
                [Package("grep", "grep")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--print-format",
                                "%n-%v",
                                "grep",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(0, "grep-version", "")],
                },
                AnsibleExitJson,
            ),
            (
                # remove pkg for real now -- with 2 packages
                {"name": ["grep", "gawk"], "state": "absent"},
                ["grep-version", "gawk-anotherversion"],
                [Package("grep", "grep"), Package("gawk", "gawk")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--print-format",
                                "%n-%v",
                                "grep",
                                "gawk",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            ["pacman", "--remove", "--noconfirm", "--noprogressbar", "grep", "gawk"],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [
                        (0, "grep-version\ngawk-anotherversion", ""),
                        (0, "stdout", "stderr"),
                    ],
                },
                AnsibleExitJson,
            ),
            (
                # remove pkg   force + extra_args
                {
                    "name": ["grep"],
                    "state": "absent",
                    "force": True,
                    "extra_args": "--some --extra arg",
                },
                ["grep-version"],
                [Package("grep", "grep")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--some",
                                "--extra",
                                "arg",
                                "--nodeps",
                                "--nodeps",
                                "--print-format",
                                "%n-%v",
                                "grep",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--some",
                                "--extra",
                                "arg",
                                "--nodeps",
                                "--nodeps",
                                "grep",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [
                        (0, "grep-version", ""),
                        (0, "stdout", "stderr"),
                    ],
                },
                AnsibleExitJson,
            ),
            (
                # remove pkg -- Failure to list
                {"name": ["grep"], "state": "absent"},
                ["grep-3.7-1"],
                [Package("grep", "grep")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--print-format",
                                "%n-%v",
                                "grep",
                            ],
                            check_rc=False,
                        )
                    ],
                    "side_effect": [
                        (1, "stdout", "stderr"),
                    ],
                },
                AnsibleFailJson,
            ),
            (
                # remove pkg -- Failure to remove
                {"name": ["grep"], "state": "absent"},
                ["grep-3.7-1"],
                [Package("grep", "grep")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--remove",
                                "--noconfirm",
                                "--noprogressbar",
                                "--print-format",
                                "%n-%v",
                                "grep",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            ["pacman", "--remove", "--noconfirm", "--noprogressbar", "grep"],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [
                        (0, "grep", ""),
                        (1, "stdout", "stderr"),
                    ],
                },
                AnsibleFailJson,
            ),
            (
                # install pkg: Check mode
                {"_ansible_check_mode": True, "name": ["sudo"], "state": "present"},
                ["sudo"],
                [Package("sudo", "sudo")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "--print-format",
                                "%n %v",
                                "sudo",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(0, "sudo version", "")],
                },
                AnsibleExitJson,
            ),
            (
                # Install pkgs: one regular, one already installed, one file URL and one https URL
                {
                    "name": [
                        "sudo",
                        "grep",
                        "./somepackage-12.3-x86_64.pkg.tar.zst",
                        "http://example.com/otherpkg-1.2-x86_64.pkg.tar.zst",
                    ],
                    "state": "present",
                },
                ["otherpkg", "somepackage", "sudo"],
                [
                    Package("sudo", "sudo"),
                    Package("grep", "grep"),
                    Package("somepackage", "./somepackage-12.3-x86_64.pkg.tar.zst", source_is_URL=True),
                    Package(
                        "otherpkg",
                        "http://example.com/otherpkg-1.2-x86_64.pkg.tar.zst",
                        source_is_URL=True,
                    ),
                ],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "--print-format",
                                "%n %v",
                                "sudo",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--upgrade",
                                "--print-format",
                                "%n %v",
                                "./somepackage-12.3-x86_64.pkg.tar.zst",
                                "http://example.com/otherpkg-1.2-x86_64.pkg.tar.zst",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "sudo",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--upgrade",
                                "./somepackage-12.3-x86_64.pkg.tar.zst",
                                "http://example.com/otherpkg-1.2-x86_64.pkg.tar.zst",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [
                        (0, "sudo version", ""),
                        (0, "somepackage 12.3\notherpkg 1.2", ""),
                        (0, "", ""),
                        (0, "", ""),
                    ],
                },
                AnsibleExitJson,
            ),
            (
                # install pkg, extra_args
                {"name": ["sudo"], "state": "present", "extra_args": "--some --thing else"},
                ["sudo"],
                [Package("sudo", "sudo")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--some",
                                "--thing",
                                "else",
                                "--sync",
                                "--print-format",
                                "%n %v",
                                "sudo",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--some",
                                "--thing",
                                "else",
                                "--sync",
                                "sudo",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(0, "sudo version", ""), (0, "", "")],
                },
                AnsibleExitJson,
            ),
            (
                # latest pkg: Check mode
                {"_ansible_check_mode": True, "name": ["sqlite"], "state": "latest"},
                ["sqlite"],
                [Package("sqlite", "sqlite")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "--print-format",
                                "%n %v",
                                "sqlite",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(0, "sqlite new-version", "")],
                },
                AnsibleExitJson,
            ),
            (
                # latest pkg -- one already latest
                {"name": ["sqlite", "grep"], "state": "latest"},
                ["sqlite"],
                [Package("sqlite", "sqlite")],
                {
                    "calls": [
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "--print-format",
                                "%n %v",
                                "sqlite",
                            ],
                            check_rc=False,
                        ),
                        mock.call(
                            mock.ANY,
                            [
                                "pacman",
                                "--noconfirm",
                                "--noprogressbar",
                                "--needed",
                                "--sync",
                                "sqlite",
                            ],
                            check_rc=False,
                        ),
                    ],
                    "side_effect": [(0, "sqlite new-version", ""), (0, "", "")],
                },
                AnsibleExitJson,
            ),
        ],
    )
    def test_op_packages(
        self,
        mock_valid_inventory,
        mock_package_list,
        module_args,
        expected_packages,
        package_list_out,
        run_command_data,
        raises,
    ):
        set_module_args(module_args)
        self.mock_run_command.side_effect = run_command_data["side_effect"]
        mock_package_list.return_value = package_list_out

        P = pacman.Pacman(pacman.setup_module())
        with pytest.raises(raises) as e:
            P.run()
        out = e.value.args[0]

        assert self.mock_run_command.mock_calls == run_command_data["calls"]
        if raises == AnsibleExitJson:
            assert out["packages"] == expected_packages
            assert out["changed"]
            assert "packages" in out
            assert "diff" in out
        else:
            assert out["stdout"] == "stdout"
            assert out["stderr"] == "stderr"

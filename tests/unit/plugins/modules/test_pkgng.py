# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.module_utils import basic
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import pkgng

PACKAGE_FILE = "/tmp/mymeta-1.2.pkg"
PACKAGE_NAME = "mymeta"


@pytest.fixture
def run_command(mocker):
    mocker.patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    )
    mocker.patch.object(basic.AnsibleModule, "get_bin_path", return_value="/testbin/pkg")
    return mocker.patch.object(basic.AnsibleModule, "run_command")


def called_commands(run_command):
    # dir_arg is None when rootdir/chroot/jail are not used; the real
    # run_command ignores None args, so filter them out for comparison
    return [[arg for arg in call.args[0] if arg is not None] for call in run_command.call_args_list]


def test_install_from_package_file(run_command):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (0, f"{PACKAGE_NAME}\n", ""),  # pkg query -F <file> %n
        (0, "", ""),  # pkg update
        (1, "", ""),  # pkg info (package not yet installed)
        (0, f"[1/1] Installing {PACKAGE_NAME}-1.2...\n", ""),  # pkg install
        (0, "", ""),  # pkg info (verify package is installed)
    ]

    with set_module_args({"name": PACKAGE_FILE}):
        with pytest.raises(AnsibleExitJson) as exc:
            pkgng.main()

    result = exc.value.args[0]
    assert result["changed"]
    assert "installed 1 package" in result["msg"]
    assert called_commands(run_command) == [
        ["/testbin/pkg", "-v"],
        ["/testbin/pkg", "query", "-F", PACKAGE_FILE, "%n"],
        ["/testbin/pkg", "update"],
        ["/testbin/pkg", "info", "-g", "-e", PACKAGE_NAME],
        ["/testbin/pkg", "install", "-g", "-y", PACKAGE_FILE],
        ["/testbin/pkg", "info", "-g", "-e", PACKAGE_NAME],
    ]


def test_install_from_package_file_already_installed(run_command):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (0, f"{PACKAGE_NAME}\n", ""),  # pkg query -F <file> %n
        (0, "", ""),  # pkg update
        (0, "", ""),  # pkg info (package already installed)
    ]

    with set_module_args({"name": PACKAGE_FILE}):
        with pytest.raises(AnsibleExitJson) as exc:
            pkgng.main()

    result = exc.value.args[0]
    assert not result["changed"]
    assert "package(s) already present" in result["msg"]
    assert called_commands(run_command) == [
        ["/testbin/pkg", "-v"],
        ["/testbin/pkg", "query", "-F", PACKAGE_FILE, "%n"],
        ["/testbin/pkg", "update"],
        ["/testbin/pkg", "info", "-g", "-e", PACKAGE_NAME],
    ]


def test_install_from_unreadable_package_file(run_command):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (70, "", f"pkg: unable to read {PACKAGE_FILE}"),  # pkg query -F <file> %n
    ]

    with set_module_args({"name": PACKAGE_FILE}):
        with pytest.raises(AnsibleFailJson) as exc:
            pkgng.main()

    result = exc.value.args[0]
    assert result["msg"].startswith(f"failed to obtain package name from file {PACKAGE_FILE}")


@pytest.mark.parametrize("state", ["latest", "absent"])
def test_package_file_with_unsupported_state_fails(run_command, state):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
    ]

    with set_module_args({"name": PACKAGE_FILE, "state": state}):
        with pytest.raises(AnsibleFailJson) as exc:
            pkgng.main()

    result = exc.value.args[0]
    assert result["msg"] == f"state={state} is not supported for local package files: {PACKAGE_FILE}"
    assert called_commands(run_command) == [["/testbin/pkg", "-v"]]


@pytest.mark.parametrize("name", ["zsh", "shells/zsh"])
def test_install_by_name_does_not_query_file(run_command, tmp_path, monkeypatch, name):
    # A file with the same name as the package in the current directory must not matter
    monkeypatch.chdir(tmp_path)
    (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / name).touch()
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (0, "", ""),  # pkg update
        (0, "", ""),  # pkg info (package already installed)
    ]

    with set_module_args({"name": name}):
        with pytest.raises(AnsibleExitJson) as exc:
            pkgng.main()

    result = exc.value.args[0]
    assert not result["changed"]
    assert called_commands(run_command) == [
        ["/testbin/pkg", "-v"],
        ["/testbin/pkg", "update"],
        ["/testbin/pkg", "info", "-g", "-e", name],
    ]


def test_pkg_is_run_with_stdin_fed_and_closed(run_command):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (0, "", ""),  # pkg update
        (0, "", ""),  # pkg info (package already installed)
    ]

    with set_module_args({"name": PACKAGE_NAME}):
        with pytest.raises(AnsibleExitJson):
            pkgng.main()

    # Every pkg invocation gets something on stdin, which run_command closes
    # right after writing it, so an interactive question takes its default
    # answer instead of blocking the task forever.
    assert [call.kwargs.get("data") for call in run_command.call_args_list[1:]] == ["\n", "\n"]


def test_annotate_keeps_its_own_stdin_payload(run_command):
    run_command.side_effect = [
        (0, "1.18.4", ""),  # pkg -v
        (0, "", ""),  # pkg update
        (0, "", ""),  # pkg info (package already installed)
        (0, "", ""),  # pkg info -A (annotation not present yet)
        (0, "", ""),  # pkg annotate
    ]

    with set_module_args({"name": PACKAGE_NAME, "annotation": "+vendor=acme"}):
        with pytest.raises(AnsibleExitJson):
            pkgng.main()

    # The default stdin must not displace the annotation value, which pkg reads
    # from stdin as well.
    annotate_call = run_command.call_args_list[-1]
    assert "annotate" in annotate_call.args[0]
    assert annotate_call.kwargs["data"] == "acme"

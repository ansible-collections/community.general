# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import golang_package


@pytest.mark.parametrize(
    "package,expected",
    [
        ("golang.org/x/tools/cmd/stringer", "stringer"),
        ("github.com/golangci/golangci-lint/cmd/golangci-lint", "golangci-lint"),
        ("github.com/GoogleCloudPlatform/cloud-sql-proxy/v2", "cloud-sql-proxy"),
        ("github.com/GoogleCloudPlatform/cloud-sql-proxy/v3", "cloud-sql-proxy"),
        ("github.com/foo/bar/v10", "bar"),
        ("github.com/GoogleCloudPlatform/cloud-sql-proxy/v2/", "cloud-sql-proxy"),
        ("github.com/foo/bar/v2/cmd/baz", "baz"),
        ("stringer", "stringer"),
        ("v2", "v2"),
        ("", ""),
    ],
)
def test_get_binary_name(package, expected):
    assert golang_package.Go._get_binary_name(package) == expected


def test_get_installed_major_version(mocker, tmp_path):
    from ansible.module_utils import basic

    gobin = tmp_path / "bin"
    gobin.mkdir()
    binary = gobin / "cloud-sql-proxy"
    binary.touch()

    pkg_name = "github.com/GoogleCloudPlatform/cloud-sql-proxy/v2"

    mock_module = mocker.MagicMock(spec=basic.AnsibleModule)
    mock_module.check_mode = False
    mock_module.get_bin_path.return_value = "/usr/bin/go"
    mock_module.run_command.return_value = (
        0,
        f"/bin/cloud-sql-proxy: go1.22.0\n\tpath\t{pkg_name}\n\tmod\t{pkg_name}\tv2.8.0\th1:abc\n",
        "",
    )

    go = golang_package.Go(
        mock_module,
        executable=None,
        name=[pkg_name],
        state="present",
        version=None,
    )
    go._gobin = str(gobin)

    installed = go.get_installed()
    assert installed == {pkg_name: "v2.8.0"}


def test_is_outdated_major_version(mocker, tmp_path):
    from ansible.module_utils import basic

    gobin = tmp_path / "bin"
    gobin.mkdir()
    binary = gobin / "cloud-sql-proxy"
    binary.touch()

    pkg_name = "github.com/GoogleCloudPlatform/cloud-sql-proxy/v2"

    mock_module = mocker.MagicMock(spec=basic.AnsibleModule)
    mock_module.check_mode = False
    mock_module.get_bin_path.return_value = "/usr/bin/go"

    go = golang_package.Go(
        mock_module,
        executable=None,
        name=[pkg_name],
        state="latest",
        version=None,
    )
    go._gobin = str(gobin)

    mocker.patch.object(
        go,
        "_get_binary_info",
        return_value={"path": pkg_name, "version": "v2.8.0", "mod_path": pkg_name},
    )
    mocker.patch.object(go, "_get_latest_version", return_value="v2.9.0")

    assert go.is_outdated(pkg_name) is True

    mocker.patch.object(go, "_get_latest_version", return_value="v2.8.0")
    assert go.is_outdated(pkg_name) is False


def test_uninstall_major_version(mocker, tmp_path):
    from ansible.module_utils import basic

    gobin = tmp_path / "bin"
    gobin.mkdir()
    binary = gobin / "cloud-sql-proxy"
    binary.touch()

    pkg_name = "github.com/GoogleCloudPlatform/cloud-sql-proxy/v2"

    mock_module = mocker.MagicMock(spec=basic.AnsibleModule)
    mock_module.check_mode = False
    mock_module.get_bin_path.return_value = "/usr/bin/go"

    go = golang_package.Go(
        mock_module,
        executable=None,
        name=[pkg_name],
        state="absent",
        version=None,
    )
    go._gobin = str(gobin)

    assert binary.exists()
    go.uninstall([pkg_name])
    assert not binary.exists()


def test_main_idempotent_with_major_version(mocker, tmp_path):
    from ansible.module_utils import basic
    from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
        AnsibleExitJson,
        exit_json,
        fail_json,
    )

    mocker.patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    )

    gobin = tmp_path / "bin"
    gobin.mkdir()
    binary = gobin / "cloud-sql-proxy"
    binary.touch()

    pkg_name = "github.com/GoogleCloudPlatform/cloud-sql-proxy/v2"

    mocker.patch.object(basic.AnsibleModule, "get_bin_path", return_value="/usr/bin/go")
    run_command = mocker.patch.object(basic.AnsibleModule, "run_command")
    # 1. env GOBIN -> str(gobin)
    # 2. version -m <binary> -> version output
    run_command.side_effect = [
        (0, str(gobin) + "\n", ""),
        (
            0,
            f"/bin/cloud-sql-proxy: go1.22.0\n\tpath\t{pkg_name}\n\tmod\t{pkg_name}\tv2.8.0\th1:abc\n",
            "",
        ),
    ]

    with set_module_args({"name": [pkg_name], "state": "present"}):
        with pytest.raises(AnsibleExitJson) as exc:
            golang_package.main()
        assert exc.value.args[0]["changed"] is False

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock, call, patch

import pytest
from ansible.module_utils import basic
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import timezone


def create_module(*, name=None, hwclock=None):
    module = Mock()
    module.argument_spec = {"hwclock": {}, "name": {}}
    module.params = {"hwclock": hwclock, "name": name}

    paths = {
        "cp": "/usr/bin/cp",
        "dpkg-reconfigure": "/usr/sbin/dpkg-reconfigure",
        "ln": "/usr/bin/ln",
    }

    def get_bin_path(binary, required=False):
        path = paths.get(binary)
        if required and path is None:
            raise RuntimeError(f"Failed to find required executable {binary}")
        return path

    module.get_bin_path.side_effect = get_bin_path
    return module


@patch.object(timezone.os.path, "isfile", return_value=True)
@patch.object(timezone.platform, "system", return_value="Linux")
def test_name_does_not_require_hwclock(system_mock, isfile_mock):
    module = create_module(name="Etc/UTC")

    tz = timezone.Timezone(module)

    assert isinstance(tz, timezone.NosystemdTimezone)
    assert tz.update_hwclock is None
    assert call("hwclock", required=False) in module.get_bin_path.call_args_list


@patch.object(timezone.platform, "system", return_value="Linux")
def test_hwclock_requires_executable(system_mock):
    module = create_module(hwclock="UTC")

    with pytest.raises(RuntimeError, match="required executable hwclock"):
        timezone.Timezone(module)

    assert call("hwclock", required=True) in module.get_bin_path.call_args_list


@pytest.fixture
def timedatectl(mocker, tmp_path):
    """Fake a working timedatectl, reporting and changing the timezone kept in ``state``."""
    state = {"name": "Etc/UTC"}

    def run_command(args, **kwargs):
        if isinstance(args, list) and args[1] == "set-timezone":
            state["name"] = args[2]
            return 0, "", ""
        return 0, f"Time zone: {state['name']} (UTC, +0000)\nRTC in local TZ: no\n", ""

    real_isfile = timezone.os.path.isfile
    mocker.patch.object(
        timezone.os.path,
        "isfile",
        side_effect=lambda path: path.startswith("/usr/share/zoneinfo/") or real_isfile(path),
    )
    mocker.patch.object(timezone.platform, "system", return_value="Linux")
    mocker.patch.object(timezone.SystemdTimezone, "timezone_file", str(tmp_path / "timezone"))
    mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)
    mocker.patch.object(basic.AnsibleModule, "get_bin_path", side_effect=lambda name, *a, **kw: f"/usr/bin/{name}")
    state["run_command"] = mocker.patch.object(basic.AnsibleModule, "run_command", side_effect=run_command)
    return state


def run_module(args):
    with set_module_args(args):
        with pytest.raises(AnsibleExitJson) as result:
            timezone.main()
    return result.value.args[0]


def set_timezone_calls(timedatectl):
    return [c for c in timedatectl["run_command"].call_args_list if "set-timezone" in c.args[0]]


@pytest.mark.parametrize(
    "current, file_content, before",
    [
        pytest.param("Etc/UTC", "Etc/UTC\n", "Etc/UTC", id="both_differ"),
        pytest.param("Europe/London", "Etc/UTC\n", "Etc/UTC", id="only_file_differs"),
        pytest.param("Europe/London", "", "n/a", id="empty_file"),
    ],
)
def test_systemd_updates_timezone_file(timedatectl, tmp_path, current, file_content, before):
    timedatectl["name"] = current
    timezone_file = tmp_path / "timezone"
    timezone_file.write_text(file_content)

    result = run_module({"name": "Europe/London"})

    assert result["changed"] is True
    assert result["diff"]["before"]["name"] == before
    assert result["diff"]["after"]["name"] == "Europe/London"
    assert timedatectl["name"] == "Europe/London"
    assert timezone_file.read_text() == "Europe/London\n"


def test_systemd_does_not_create_timezone_file(timedatectl, tmp_path):
    result = run_module({"name": "Europe/London"})

    assert result["changed"] is True
    assert timedatectl["name"] == "Europe/London"
    assert not (tmp_path / "timezone").exists()


def test_systemd_unchanged_when_in_sync(timedatectl, tmp_path):
    timedatectl["name"] = "Europe/London"
    timezone_file = tmp_path / "timezone"
    timezone_file.write_text("Europe/London\n")

    result = run_module({"name": "Europe/London"})

    assert result["changed"] is False
    assert set_timezone_calls(timedatectl) == []
    assert timezone_file.read_text() == "Europe/London\n"


def test_systemd_check_mode_does_not_write_timezone_file(timedatectl, tmp_path):
    timedatectl["name"] = "Europe/London"
    timezone_file = tmp_path / "timezone"
    timezone_file.write_text("Etc/UTC\n")

    result = run_module({"name": "Europe/London", "_ansible_check_mode": True})

    assert result["changed"] is True
    assert set_timezone_calls(timedatectl) == []
    assert timezone_file.read_text() == "Etc/UTC\n"

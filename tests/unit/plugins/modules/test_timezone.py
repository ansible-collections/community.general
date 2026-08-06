# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock, call, patch

import pytest

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

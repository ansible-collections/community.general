# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.lookup.onepassword import OnePass


@pytest.fixture
def fake_op(mocker):
    def _fake_op(version):
        mocker.patch(
            "ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase.get_current_version",
            return_value=version,
        )
        op = OnePass()
        op._config._config_file_path = "/home/jin/.op/config"
        mocker.patch.object(op._cli, "_run")

        return op

    return _fake_op


@pytest.fixture
def opv1(fake_op):
    return fake_op("1.17.2")


@pytest.fixture
def opv2(fake_op):
    return fake_op("2.27.2")

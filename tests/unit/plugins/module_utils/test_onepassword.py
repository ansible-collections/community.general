# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os

import pytest

from ansible_collections.community.general.plugins.module_utils.onepassword import OnePasswordConfig


@pytest.fixture
def os_expanduser(mocker):
    def _os_expanduser(path):
        return path.replace("~", "/home/testuser")

    mocker.patch("os.path.expanduser", side_effect=_os_expanduser)


@pytest.fixture
def exists(mocker):
    def _exists(path):
        if "op/" in path:
            return True

        return os.path.exists(path)


def test_op_config(mocker, os_expanduser):
    mocker.patch("os.path.exists", side_effect=[False, True])
    op_config = OnePasswordConfig()

    assert op_config.config_file_path == "/home/testuser/.config/op/config"


def test_op_no_config(mocker, os_expanduser):
    mocker.patch("os.path.exists", return_value=False)
    op_config = OnePasswordConfig()

    assert op_config.config_file_path is None

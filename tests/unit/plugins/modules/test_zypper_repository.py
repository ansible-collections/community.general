# Copyright (c) 2026, Harshvardhan Sharma <harshvardhan.sharma@suse.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.community.general.plugins.modules import zypper_repository

BASEPRODUCT = """<?xml version="1.0" encoding="UTF-8"?>
<product schemeversion="0">
  <vendor>openSUSE</vendor>
  <name>Leap</name>
  <version>16.0</version>
  <release>0</release>
</product>
"""

RPM_QUERY = ["rpm", "-q", "--qf", "%{version}", "-f", "/etc/os-release"]


@pytest.fixture
def module():
    module = MagicMock()
    module.run_command.return_value = (0, "16.0+leap", "")
    return module


def test_get_releasever_from_baseproduct(tmp_path, monkeypatch, module):
    baseproduct = tmp_path / "baseproduct"
    baseproduct.write_text(BASEPRODUCT)
    monkeypatch.setattr(zypper_repository, "BASEPRODUCT_FILE", str(baseproduct))

    assert zypper_repository.get_releasever(module) == "16.0"
    module.run_command.assert_not_called()


@pytest.mark.parametrize(
    "content",
    [None, "not xml", "<product><name>Leap</name></product>"],
    ids=["missing", "malformed", "no-version"],
)
def test_get_releasever_falls_back_to_rpm(tmp_path, monkeypatch, module, content):
    baseproduct = tmp_path / "baseproduct"
    if content is not None:
        baseproduct.write_text(content)
    monkeypatch.setattr(zypper_repository, "BASEPRODUCT_FILE", str(baseproduct))

    assert zypper_repository.get_releasever(module) == "16.0+leap"
    module.run_command.assert_called_once_with(RPM_QUERY, check_rc=True)

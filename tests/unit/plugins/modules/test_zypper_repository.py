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


ADDREPO_PREFIX = ["/usr/bin/zypper", "--quiet", "--non-interactive", "addrepo", "--check"]


@pytest.fixture
def addrepo_module():
    module = MagicMock()
    module.get_bin_path.return_value = "/usr/bin/zypper"
    module.run_command.return_value = (0, "", "")
    return module


@pytest.mark.parametrize(
    "raw_repo_gpgcheck, allow_unsigned_metadata, expected",
    [
        ("0", True, False),
        ("", True, True),
        ("0", False, True),
        ("", False, False),
    ],
    ids=["explicit-allowed", "not-set-wanted", "set-not-wanted", "not-set-not-wanted"],
)
def test_repo_changes_allow_unsigned_metadata(module, raw_repo_gpgcheck, allow_unsigned_metadata, expected):
    realrepo = {"alias": "r", "url": "http://x/", "gpgcheck": "1", "raw_repo_gpgcheck": raw_repo_gpgcheck}
    repocmp = {"alias": "r", "url": "http://x/", "gpgcheck": "1", "allow_unsigned_metadata": allow_unsigned_metadata}

    assert zypper_repository._repo_changes(module, realrepo, repocmp) is expected


@pytest.mark.parametrize(
    "repodata, version, flag, warned",
    [
        ({"gpgcheck": "1", "allow_unsigned_metadata": True}, "1.14.93", "--gpgcheck-allow-unsigned-repo", False),
        ({"gpgcheck": "1", "allow_unsigned_metadata": False}, "1.14.93", "--gpgcheck", False),
        ({"gpgcheck": "1"}, "1.14.93", "--gpgcheck", False),
        ({"gpgcheck": "0", "allow_unsigned_metadata": False}, "1.14.93", "--no-gpgcheck", False),
        ({"gpgcheck": "1", "allow_unsigned_metadata": True}, "1.13.31", "--gpgcheck", True),
    ],
    ids=["allowed", "strict", "unset", "disabled", "old-zypper"],
)
def test_addmodify_repo_gpgcheck_flags(addrepo_module, repodata, version, flag, warned):
    repodata = dict(
        {"alias": "r", "url": "http://x/", "name": "", "priority": None, "enabled": "1", "autorefresh": "1"}, **repodata
    )

    zypper_repository.addmodify_repo(addrepo_module, repodata, None, zypper_repository.LooseVersion(version))

    cmd = addrepo_module.run_command.call_args[0][0]
    assert cmd[: len(ADDREPO_PREFIX)] == ADDREPO_PREFIX
    assert flag in cmd
    assert len([c for c in cmd if c.startswith("--gpgcheck") or c == "--no-gpgcheck"]) == 1
    assert addrepo_module.warn.called is warned

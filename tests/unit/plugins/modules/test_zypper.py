# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules.zypper import split_name_version

NAME_VERSION = [
    ("nmap", ("nmap", "")),
    ("docker>=1.10", ("docker", ">=1.10")),
    ("apache=2.4", ("apache", "=2.4")),
    ("foo>1", ("foo", ">1")),
    # https://github.com/ansible-collections/community.general/issues/6564
    ("crash-kmp-default<7.2.1_k4.12.14_122.127", ("crash-kmp-default", "<7.2.1_k4.12.14_122.127")),
    ("crash-kmp-default<=7.2.1_k4.12.14_122.127-8.19.2", ("crash-kmp-default", "<=7.2.1_k4.12.14_122.127-8.19.2")),
    ("pkg=1:2.3.4-5.el8", ("pkg", "=1:2.3.4-5.el8")),
]


@pytest.mark.parametrize("name, expected", NAME_VERSION, ids=lambda x: x if isinstance(x, str) else "")
def test_split_name_version(name, expected):
    prefix, pname, version = split_name_version(name)
    assert (pname, version) == expected
    assert prefix == ""


PREFIXED_NAME_VERSION = [
    ("-nmap", ("-", "nmap", "")),
    ("~nmap", ("-", "nmap", "")),
    ("+docker>=1.10", ("+", "docker", ">=1.10")),
]


@pytest.mark.parametrize("name, expected", PREFIXED_NAME_VERSION, ids=lambda x: x if isinstance(x, str) else "")
def test_split_name_version_with_prefix(name, expected):
    assert split_name_version(name) == expected

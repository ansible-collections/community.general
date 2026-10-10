# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules import zfs

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(zfs, __name__, mocks=[RunCommandMock])


@pytest.mark.parametrize(
    "prop, value, expected",
    [
        ("volblocksize", "4k", "4096"),
        ("volblocksize", "4K", "4096"),
        ("volblocksize", "4096", "4096"),
        ("volblocksize", 4096, "4096"),
        ("volsize", "4G", "4294967296"),
        ("volsize", "4GB", "4294967296"),
        ("volsize", "4GiB", "4294967296"),
        ("volsize", "1.5G", "1610612736"),
        ("recordsize", "512B", "512"),
        ("quota", "none", "none"),
        ("refreservation", "auto", "auto"),
        ("volsize", None, None),
        ("compression", "4k", "4k"),
    ],
)
def test_normalize_value(prop, value, expected):
    assert zfs.normalize_value(prop, value) == expected

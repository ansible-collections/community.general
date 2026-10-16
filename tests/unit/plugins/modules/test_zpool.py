# Copyright (c) 2026, Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from ansible_collections.community.general.plugins.modules import zpool

from .uthelper import RunCommandMock, UTHelper

SYMLINKS = {
    "/dev/disk/by-id/ata-DISK_B": "/dev/sdb",
    "/dev/disk/by-id/ata-DISK_B-part1": "/dev/sdb1",
    "/dev/disk/by-id/ata-DISK_D": "/dev/sdd",
}

DEVICES = {"/dev/sdb", "/dev/sdb1", "/dev/sdc", "/dev/sdd"} | set(SYMLINKS)


class FakePath(PurePosixPath):
    def exists(self):
        return str(self) in DEVICES

    def resolve(self):
        return FakePath(SYMLINKS.get(str(self), str(self)))


@pytest.fixture(autouse=True)
def fake_devices(mocker):
    mocker.patch.object(zpool, "Path", FakePath)


UTHelper.from_module(zpool, __name__, mocks=[RunCommandMock])

# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules import xbps

from .uthelper import RunCommandMock, UTHelper


@pytest.fixture(autouse=True)
def patch_os_path_exists(mocker):
    mocker.patch("os.path.exists", return_value=True)


UTHelper.from_module(xbps, __name__, mocks=[RunCommandMock])

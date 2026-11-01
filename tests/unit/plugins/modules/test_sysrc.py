# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os

import pytest

from ansible_collections.community.general.plugins.modules import sysrc

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(sysrc, __name__, mocks=[RunCommandMock])


@pytest.fixture(autouse=True)
def rc_conf_exists(mocker):
    real_exists = os.path.exists
    mocker.patch.object(sysrc.os.path, "exists", side_effect=lambda path: path == "/etc/rc.conf" or real_exists(path))

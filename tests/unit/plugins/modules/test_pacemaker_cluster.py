# Author: Dexter Le (dextersydney2001@gmail.com)
# Largely adapted from test_redhat_subscription by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Dexter Le (dextersydney2001@gmail.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.module_utils import _pacemaker
from ansible_collections.community.general.plugins.modules import pacemaker_cluster

from .uthelper import RunCommandMock, UTHelper


@pytest.fixture(autouse=True)
def _pacemaker_json_capable(mocker):
    """All pacemaker_cluster module tests behave as if ``pcs`` supports JSON output.

    The version-probe / plaintext-fallback dispatch is exhaustively unit-tested
    in ``tests/unit/plugins/module_utils/test__pacemaker.py``; module-level
    tests should not have to mock ``pcs --version`` for every scenario.
    """
    mocker.patch.object(
        _pacemaker.PacemakerRunner,
        "_probe_version",
        return_value="0.11.7",
    )


UTHelper.from_module(pacemaker_cluster, __name__, mocks=[RunCommandMock])

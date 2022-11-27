# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.plugins.modules import proxmox_snap_info
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def test_proxmox_snap_info_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        proxmox_snap_info.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']

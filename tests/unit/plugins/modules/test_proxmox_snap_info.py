# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from datetime import timedelta
import time

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.plugins.modules import proxmox_snap
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args
from ansible_collections.community.general.plugins.modules import proxmox_snap_info

SNAPS = [

    {'description': '',
     'name': 'snapshot_3days_old',
     'parent': 'xyz',
     'snaptime': int(time.time() - timedelta(3).total_seconds()),
     'vmstate': 0},
    {'description': '',
     'name': 'snapshot_2days_old',
     'parent': 'xyyz',
     'snaptime': int(time.time() - timedelta(2).total_seconds()),
     'vmstate': 0},
    {'description': '',
     'name': 'snapshot_1days_old',
     'parent': 'xyyz',
     'snaptime': int(time.time() - timedelta(1).total_seconds()),
     'vmstate': 0},
    {'description': '',
     'name': 'veryold',
     'parent': 'before_automated_upgrade',
     'snaptime': 1669907928,
     'vmstate': 0},
    {'description': 'You are here!',
     'digest': 'd8ed9284b2b32a3f0ae3eb925b43599f56b59078',
     'name': 'current',
     'parent': 'snapshot_2022-12-11',
     'running': 1}]

ALL_SNAP_LIST = ['snapshot_3days_old', 'snapshot_2days_old', 'snapshot_1days_old', 'veryold']
SNAP_2d_LIST = ['snapshot_3days_old', 'snapshot_2days_old', 'veryold']
SNAP_SNAPNAME_LIST = ['snapshot_3days_old', 'snapshot_2days_old', 'snapshot_1days_old']


def test_proxmox_snap_info_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        proxmox_snap_info.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


@patch('ansible_collections.community.general.plugins.modules.proxmox_snap_info.get_proxmox_snapshotlist', return_value=SNAPS)
def test_snapshot_get(mocker, capfd):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "getsnapshots": True,
                     "timeout": "1",
                     "_ansible_check_mode": True})

    proxmox_utils.HAS_PROXMOXER = True
    with pytest.raises(SystemExit) as results:
        proxmox_snap_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)["results"] == ALL_SNAP_LIST


@patch('ansible_collections.community.general.plugins.modules.proxmox_snap_info.get_proxmox_snapshotlist', return_value=SNAPS)
def test_proxmox_snap_info_getsnapshots_older_than_2days(mocker, capfd):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "getsnapshots": True,
                     "older_than": 2,
                     "timeout": "1",
                     "_ansible_check_mode": True})

    proxmox_utils.HAS_PROXMOXER = True
    with pytest.raises(SystemExit) as results:
        proxmox_snap_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)["results"] == SNAP_2d_LIST


@patch('ansible_collections.community.general.plugins.modules.proxmox_snap_info.get_proxmox_snapshotlist', return_value=SNAPS)
def test_proxmox_snap_info_getsnapshots_only_snaps_with_name(mocker, capfd):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "getsnapshots": True,
                     "snapname": "snapshot_",
                     "timeout": "1",
                     "_ansible_check_mode": True})

    proxmox_utils.HAS_PROXMOXER = True
    with pytest.raises(SystemExit) as results:
        proxmox_snap_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)["results"] == SNAP_SNAPNAME_LIST

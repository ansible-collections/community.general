# -*- coding: utf-8 -*-
#
# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_snap
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args


def get_resources(type):
    return [{"diskwrite": 0,
             "vmid": 100,
             "node": "localhost",
             "id": "lxc/100",
             "maxdisk": 10000,
             "template": 0,
             "disk": 10000,
             "uptime": 10000,
             "maxmem": 10000,
             "maxcpu": 1,
             "netin": 10000,
             "type": "lxc",
             "netout": 10000,
             "mem": 10000,
             "diskread": 10000,
             "cpu": 0.01,
             "name": "test-lxc",
             "status": "running"}]


def fake_api(mocker):
    r = mocker.MagicMock()
    r.cluster.resources.get = MagicMock(side_effect=get_resources)
    return r


def test_proxmox_snap_without_argument(capfd):
    set_module_args({})
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_create_snapshot_check_mode(connect_mock, capfd, mocker):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "state": "present",
                     "snapname": "test",
                     "timeout": "1",
                     "force": True,
                     "_ansible_check_mode": True})
    proxmox_utils.HAS_PROXMOXER = True
    connect_mock.side_effect = lambda: fake_api(mocker)
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    assert not json.loads(out)['changed']


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_remove_snapshot_check_mode(connect_mock, capfd, mocker):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "state": "absent",
                     "snapname": "test",
                     "timeout": "1",
                     "force": True,
                     "_ansible_check_mode": True})
    proxmox_utils.HAS_PROXMOXER = True
    connect_mock.side_effect = lambda: fake_api(mocker)
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    assert not json.loads(out)['changed']


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_rollback_snapshot_check_mode(connect_mock, capfd, mocker):
    set_module_args({"hostname": "test-lxc",
                     "api_user": "root@pam",
                     "api_password": "secret",
                     "api_host": "127.0.0.1",
                     "state": "rollback",
                     "snapname": "test",
                     "timeout": "1",
                     "force": True,
                     "_ansible_check_mode": True})
    proxmox_utils.HAS_PROXMOXER = True
    connect_mock.side_effect = lambda: fake_api(mocker)
    with pytest.raises(SystemExit) as results:
        proxmox_snap.main()

    out, err = capfd.readouterr()
    assert not err
    output = json.loads(out)
    assert not output['changed']
    assert output['msg'] == "Snapshot test does not exist"

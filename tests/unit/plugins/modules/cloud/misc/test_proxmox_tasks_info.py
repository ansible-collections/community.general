# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Andreas Botzner (@paginabianca) <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Proxmox Tasks module unit tests.
# The API responses used in these tests were recorded from PVE version 6.4-8

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_tasks_info
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args
from ansible_collections.community.general.plugins.module_utils import proxmox

NODE = 'node01'
TASK_UPID = 'UPID:iaclab-01-01:000029DD:1599528B:6108F068:srvreload:networking:root@pam:'
TASKS = [
    {
        "endtime": 1629092710,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 3539,
        "pstart": 474062216,
        "starttime": 1629092709,
        "status": "OK",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:00000DD3:1C419D88:6119FB65:srvreload:networking:root@pam:",
        "user": "root@pam"
    },
    {
        "endtime": 1627975785,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 10717,
        "pstart": 362369675,
        "starttime": 1627975784,
        "status": "command 'ifreload -a' failed: exit code 1",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:000029DD:1599528B:6108F068:srvreload:networking:root@pam:",
        "user": "root@pam"
    },
    {
        "endtime": 1627975503,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 6778,
        "pstart": 362341540,
        "starttime": 1627975503,
        "status": "OK",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:00001A7A:1598E4A4:6108EF4F:srvreload:networking:root@pam:",
        "user": "root@pam"
    }
]
EXPECTED_TASKS = [
    {
        "endtime": 1629092710,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 3539,
        "pstart": 474062216,
        "starttime": 1629092709,
        "status": "OK",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:00000DD3:1C419D88:6119FB65:srvreload:networking:root@pam:",
        "user": "root@pam",
        "failed": False
    },
    {
        "endtime": 1627975785,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 10717,
        "pstart": 362369675,
        "starttime": 1627975784,
        "status": "command 'ifreload -a' failed: exit code 1",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:000029DD:1599528B:6108F068:srvreload:networking:root@pam:",
        "user": "root@pam",
        "failed": True
    },
    {
        "endtime": 1627975503,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 6778,
        "pstart": 362341540,
        "starttime": 1627975503,
        "status": "OK",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:00001A7A:1598E4A4:6108EF4F:srvreload:networking:root@pam:",
        "user": "root@pam",
        "failed": False
    }
]

EXPECTED_SINGLE_TASK = [
    {
        "endtime": 1627975785,
        "id": "networking",
        "node": "iaclab-01-01",
        "pid": 10717,
        "pstart": 362369675,
        "starttime": 1627975784,
        "status": "command 'ifreload -a' failed: exit code 1",
        "type": "srvreload",
        "upid": "UPID:iaclab-01-01:000029DD:1599528B:6108F068:srvreload:networking:root@pam:",
        "user": "root@pam",
        "failed": True
    },
]


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_without_required_parameters(connect_mock, capfd, mocker):
    set_module_args({})
    with pytest.raises(SystemExit):
        proxmox_tasks_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']


def mock_api_tasks_response(mocker):
    m = mocker.MagicMock()
    g = mocker.MagicMock()
    m.nodes = mocker.MagicMock(return_value=g)
    g.tasks.get = mocker.MagicMock(return_value=TASKS)
    return m


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_get_tasks(connect_mock, capfd, mocker):
    set_module_args({'api_host': 'proxmoxhost',
                     'api_user': 'root@pam',
                     'api_password': 'supersecret',
                     'node': NODE})

    connect_mock.side_effect = lambda: mock_api_tasks_response(mocker)
    proxmox_utils.HAS_PROXMOXER = True

    with pytest.raises(SystemExit):
        proxmox_tasks_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert len(json.loads(out)['proxmox_tasks']) != 0
    assert not json.loads(out)['changed']


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_get_single_task(connect_mock, capfd, mocker):
    set_module_args({'api_host': 'proxmoxhost',
                     'api_user': 'root@pam',
                     'api_password': 'supersecret',
                     'node': NODE,
                     'task': TASK_UPID})

    connect_mock.side_effect = lambda: mock_api_tasks_response(mocker)
    proxmox_utils.HAS_PROXMOXER = True

    with pytest.raises(SystemExit):
        proxmox_tasks_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert len(json.loads(out)['proxmox_tasks']) == 1
    assert json.loads(out)
    assert not json.loads(out)['changed']


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_get_non_existent_task(connect_mock, capfd, mocker):
    set_module_args({'api_host': 'proxmoxhost',
                     'api_user': 'root@pam',
                     'api_password': 'supersecret',
                     'node': NODE,
                     'task': 'UPID:nonexistent'})

    connect_mock.side_effect = lambda: mock_api_tasks_response(mocker)
    proxmox_utils.HAS_PROXMOXER = True

    with pytest.raises(SystemExit):
        proxmox_tasks_info.main()
    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)['failed']
    assert 'proxmox_tasks' not in json.loads(out)
    assert not json.loads(out)['changed']
    assert json.loads(
        out)['msg'] == 'Task: UPID:nonexistent does not exist on node: node01.'

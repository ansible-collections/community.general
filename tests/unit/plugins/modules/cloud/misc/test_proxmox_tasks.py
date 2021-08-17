# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Andreas Botzner (@paginabianca) <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Proxmox Tasks module unit tests.
# The API responses used in these tests were recorded from PVE version 6.4-8

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json
import pprint

from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_tasks_info
from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args
from ansible_collections.community.general.plugins.module_utils import proxmox

NODE = 'node01'
UPID = 'UPID:iaclab-01-01:000029DD:1599528B:6108F068:srvreload:networking:root@pam:'
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


def get_resources(type):
    return TASKS


def fake_api():
    r = MagicMock()
    r.nodes.tasks.get = MagicMock(side_effect=get_resources)
    return r


# class TestProxmoxTasks(ModuleTestCase):

#     def setUp(self):
#         super(TestProxmoxTasks, self).setUp()
#         self.module = proxmox_tasks_info

#     def tearDown(self):
#         super(TestProxmoxTasks, self).tearDown()

#     def test_without_required_parameters(self):
#         """Failure must occurs when all parameters are missing"""
#         with self.assertRaises(AnsibleFailJson):
#             set_module_args({})
#             self.module.main()

    # @patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAPI')
    # def test_get_tasks_info(self, proxmox_api_mock, capfd):
    #     set_module_args({'api_host': 'proxmoxhost',
    #                      'api_user': 'root@pam',
    #                      'api_password': 'supersecret',
    #                      'node': NODE})
    #     proxmox_api_mock.nodes.tasks.get = MagicMock(side_effect=get_resources)
    #     with self.assertRaises(AnsibleExitJson) as result:
    #         self.module.main()
    #     out, err = capfd.readouterr()
    #     pprint.pp(out)
    #     pprint.pp(result.exception.args)
    #     proxmox_api_mock.assert_called_once()
    #     pprint.pp(proxmox_api_mock.mock_calls)
    #     self.assertFalse(result.exception.args[0]['changed'])
    #     self.assertEqual(
    #         result.exception.args[0]['proxmox_tasks'], EXPECTED_TASKS)
    #     assert False

#     @patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAPI')
#     def test_get_single_tasks_info(self, proxmox_api_mock):
#         set_module_args({'api_host': 'proxmoxhost',
#                          'api_user': 'root@pam',
#                          'api_password': 'supersecret',
#                          'node': NODE,
#                          'task': UPID})
#         # create_api_mock = fake_api()
#         # proxmox_api_mock.return_value = create_api_mock
#         proxmox_api_mock.nodes.tasks.get = MagicMock(side_effect=get_resources)
#         with self.assertRaises(AnsibleExitJson) as result:
#             self.module.main()
#         pprint.pp(result)
#         proxmox_api_mock.assert_called_once()
#         pprint.pp(proxmox_api_mock.mock_calls)
#         # create_api_mock.assert_called_once()
#         self.assertFalse(result.exception.args[0]['changed'])
#         self.assertEqual(
#             result.exception.args[0]['proxmox_tasks'], EXPECTED_SINGLE_TASK)
#         # create_downtime_mock.assert_called_once_with(downtime)
#         assert False


@patch('ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect')
def test_get_tasks(connect_mock, capfd, mocker):
    set_module_args({'api_host': 'proxmoxhost',
                     'api_user': 'root@pam',
                     'api_password': 'supersecret',
                     'node': NODE})

    connect_mock.nodes.tasks.get.return_value = TASKS

    with pytest.raises(SystemExit):
        proxmox_tasks_info.main()
    out, err = capfd.readouterr()
    pprint.pp("[connect_mock] CALLS calls")
    pprint.pp(connect_mock.call_args_list)
    pprint.pp(out)
    out = out.split('\n\n')[1]
    # pprint.pp(out)
    assert not err
    assert json.loads(out)['changed'] is False
    assert False

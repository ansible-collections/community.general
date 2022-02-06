# -*- coding: utf-8 -*-
# Copyright (c) 2022, Masayoshi Mizuma <msys.mizuma@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args, AnsibleFailJson, AnsibleExitJson
from ansible_collections.community.general.tests.unit.compat.mock import patch

from ansible_collections.community.general.plugins.modules.storage.pmem import pmem as pmem_module

# goal_plain: the mock return value of pmem_run_command with:
# impctl create -goal MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal_plain = """The following configuration will be applied:
SocketID | DimmID | MemorySize | AppDirect1Size | AppDirect2Size
==================================================================
0x0000   | 0x0001 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
0x0000   | 0x0011 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
0x0001   | 0x1001 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
0x0001   | 0x1011 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
Do you want to continue? [y/n] Error: Invalid data input."""

# goal_plain_sk0: the mock return value of pmem_run_command with:
# ipmctl create -goal -socket 0 MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal_plain_sk0 = """The following configuration will be applied:
SocketID | DimmID | MemorySize | AppDirect1Size | AppDirect2Size
==================================================================
0x0000   | 0x0001 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
0x0000   | 0x0011 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
Do you want to continue? [y/n] Error: Invalid data input."""

# goal_plain_sk1: the mock return value of pmem_run_command with:
# ipmctl create -goal -socket 1 MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal_plain_sk1 = """The following configuration will be applied:
SocketID | DimmID | MemorySize | AppDirect1Size | AppDirect2Size
==================================================================
0x0001   | 0x1001 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
0x0001   | 0x1011 | 88.000 GiB | 12.000 GiB     | 0.000 GiB
Do you want to continue? [y/n] Error: Invalid data input."""

# goal: the mock return value of pmem_run_command with:
# ipmctl create -u B -o nvmxml -force -goal -socket 0 MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal = """<?xml version="1.0"?>
<ConfigGoalList>
  <ConfigGoal>
    <SocketID>0x0000</SocketID>
    <DimmID>0x0001</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
  <ConfigGoal>
    <SocketID>0x0000</SocketID>
    <DimmID>0x0011</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
</ConfigGoalList>"""

# goal_sk0: the mock return value of pmem_run_command with:
# ipmctl create -u B -o nvmxml -force -goal -socket 0 MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal_sk0 = """<?xml version="1.0"?>
<ConfigGoalList>
  <ConfigGoal>
    <SocketID>0x0000</SocketID>
    <DimmID>0x0001</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
  <ConfigGoal>
    <SocketID>0x0001</SocketID>
    <DimmID>0x0011</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
</ConfigGoalList>"""

# goal_sk1: the mock return value of pmem_run_command with:
# ipmctl create -u B -o nvmxml -force -goal -socket 1 MemoryMode=70 Reserved=20 PersistentMemoryType=AppDirect
goal_sk1 = """<?xml version="1.0"?>
<ConfigGoalList>
  <ConfigGoal>
    <SocketID>0x0001</SocketID>
    <DimmID>0x1001</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
  <ConfigGoal>
    <SocketID>0x0001</SocketID>
    <DimmID>0x1011</DimmID>
    <MemorySize>94489280512 B</MemorySize>
    <AppDirect1Size>12884901888 B</AppDirect1Size>
    <AppDirect2Size>0 B</AppDirect2Size>
  </ConfigGoal>
</ConfigGoalList>"""

# dimmlist: the mock return value of pmem_run_command with:
# ipmctl show -d Capacity -u B -o nvmxml -dimm
dimmlist = """<?xml version="1.0"?>
<DimmList>
 <Dimm>
  <DimmID>0x0001</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
 <Dimm> <DimmID>0x0011</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
 <Dimm>
  <DimmID>0x1001</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
 <Dimm> <DimmID>0x1011</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
</DimmList>"""

# dimmlist_sk0: the mock return value of pmem_run_command with:
# ipmctl show -d Capacity -u B -o nvmxml -dimm -socket 0
dimmlist_sk0 = """<?xml version="1.0"?>
<DimmList>
 <Dimm>
  <DimmID>0x0001</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
 <Dimm> <DimmID>0x0011</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
</DimmList>"""

# dimmlist_sk1: the mock return value of pmem_run_command with:
# ipmctl show -d Capacity -u B -o nvmxml -dimm -socket 1
dimmlist_sk1 = """<?xml version="1.0"?>
<DimmList>
 <Dimm>
  <DimmID>0x1001</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
 <Dimm> <DimmID>0x1011</DimmID>
  <Capacity>135744782336 B</Capacity>
 </Dimm>
</DimmList>"""

# show_skt: the mock return value of pmem_run_command with:
# ipmctl show -o nvmxml -socket
show_skt = """<?xml version="1.0"?>
<SocketList>
 <Socket>
  <SocketID>0x0000</SocketID>
  <MappedMemoryLimit>1024.000 GiB</MappedMemoryLimit>
  <TotalMappedMemory>400.000 GiB</TotalMappedMemory>
 </Socket>
 <Socket>
  <SocketID>0x0001</SocketID>
  <MappedMemoryLimit>1024.000 GiB</MappedMemoryLimit>
  <TotalMappedMemory>400.000 GiB</TotalMappedMemory>
 </Socket>
</SocketList>"""


class TestPmem(ModuleTestCase):
    def setUp(self):
        super(TestPmem, self).setUp()
        self.module = pmem_module

        self.mock_run_command = (patch('ansible.module_utils.basic.AnsibleModule.run_command'))
        self.mock_get_bin_path = (patch('ansible.module_utils.basic.AnsibleModule.get_bin_path'))

        self.run_command = self.mock_run_command.start()
        self.get_bin_path = self.mock_get_bin_path.start()

        self.mock_pmem_is_dcpmm_installed = (patch(
            'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_is_dcpmm_installed', return_value=""))
        self.mock_pmem_init_env = (patch(
            'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_init_env', return_value=""))

        self.pmem_is_dcpmm_installed = self.mock_pmem_is_dcpmm_installed.start()
        self.pmem_init_env = self.mock_pmem_init_env.start()

    def tearDown(self):
        super(TestPmem, self).tearDown()
        self.mock_get_bin_path.stop()
        self.mock_run_command.stop()
        self.mock_pmem_is_dcpmm_installed.stop()
        self.mock_pmem_init_env.stop()

    def result_check(self, result, socket, appdirect, memmode, reserved):
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertTrue(result.exception.args[0]['reboot_required'])

        test_result = result.exception.args[0]['result']

        if socket:
            maxIndex = 1
        else:
            maxIndex = 0

        for i in range(0, maxIndex):
            self.assertAlmostEqual(test_result[i]['AppDirect'], appdirect[i])
            self.assertAlmostEqual(test_result[i]['MemoryMode'], memmode[i])
            self.assertAlmostEqual(test_result[i]['Reserved'], reserved[i])
            if socket:
                self.assertAlmostEqual(test_result[i]['Socket'], i)

    def test_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            pmem_module.main()

    def test_fail_when_AppDirect_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'AppDirect': 10,
            })
            pmem_module.main()

    def test_fail_when_MemosyMode_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'MemoryMode': 70,
            })
            pmem_module.main()

    def test_fail_when_Reserved_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'Reserved': 10,
            })
            pmem_module.main()

    def test_fail_when_AppDirect_MemoryMode_Reserved_total_not_100(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'AppDirect': 10,
                'MemoryMode': 70,
                'Reserved': 10,
            })
            pmem_module.main()

    def test_when_AppDirect_MemoryMode(self):
        set_module_args({
            'AppDirect': 10,
            'MemoryMode': 70,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_when_AppDirect_MemoryMode_Reserved(self):
        set_module_args({
            'AppDirect': 10,
            'MemoryMode': 70,
            'Reserved': 20,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_when_AppDirect_NotInterleaved_MemoryMode_Reserved(self):
        set_module_args({
            'AppDirect': 10,
            'AppDirectInterleaved': False,
            'MemoryMode': 70,
            'Reserved': 20,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_fail_when_Socket_id_AppDirect(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'Socket': [
                    {
                        'id': 0,
                        'AppDirect': 10,
                    },
                    {
                        'id': 1,
                        'AppDirect': 10,
                    },
                ],
            })
            pmem_module.main()

    def test_fail_when_Socket0_id_MemoryMode_Socket1_id_AppDirect(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'Socket': [
                    {
                        'id': 0,
                        ' MemoryMode': 70,
                    },
                    {
                        'id': 1,
                        'AppDirect': 10,
                    },
                ],
            })
            pmem_module.main()

    def test_fail_when_Socket0_without_id(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'Socket': [
                    {
                        'AppDirect': 10,
                        'MemoryMode': 70,
                    },
                    {
                        'id': 1,
                        'AppDirect': 10,
                        'MemoryMode': 70,
                    },
                ],
            })
            pmem_module.main()

    def test_when_Socket0_and_1_AppDirect_MemoryMode(self):
        set_module_args({
            'Socket': [
                {
                    'id': 0,
                    'AppDirect': 10,
                    'MemoryMode': 70,
                },
                {
                    'id': 1,
                    'AppDirect': 10,
                    'MemoryMode': 70,
                },
            ],
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[
                    show_skt, goal_plain_sk0, goal_sk0, dimmlist_sk0, goal_plain_sk1, goal_sk1, dimmlist_sk1]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(
                result, True, [12884901888, 12884901888], [94489280512, 94489280512], [164115382272, 164115382272])

    def test_when_Socket0_and_1_AppDirect_MemoryMode_Reserved(self):
        set_module_args({
            'Socket': [
                {
                    'id': 0,
                    'AppDirect': 10,
                    'MemoryMode': 70,
                    'Reserved': 20,
                },
                {
                    'id': 1,
                    'AppDirect': 10,
                    'MemoryMode': 70,
                    'Reserved': 20,
                },
            ],
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[
                    show_skt, goal_plain_sk0, goal_sk0, dimmlist_sk0, goal_plain_sk1, goal_sk1, dimmlist_sk1]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(
                result, True, [12884901888, 12884901888], [94489280512, 94489280512], [164115382272, 164115382272])

    def test_when_Socket0_AppDirectNotInterleaved_MemoryMode_Reserved_Socket1_AppDirect_MemoryMode_Reserved(self):
        set_module_args({
            'Socket': [
                {
                    'id': 0,
                    'AppDirect': 10,
                    'AppDirectInterleaved': False,
                    'MemoryMode': 70,
                    'Reserved': 20,
                },
                {
                    'id': 1,
                    'AppDirect': 10,
                    'MemoryMode': 70,
                    'Reserved': 20,
                },
            ],
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[
                    show_skt, goal_plain_sk0, goal_sk0, dimmlist_sk0, goal_plain_sk1, goal_sk1, dimmlist_sk1]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(
                result, True, [12884901888, 12884901888], [94489280512, 94489280512], [164115382272, 164115382272])

# -*- coding: utf-8 -*-
# Copyright (c) 2022, Masayoshi Mizuma <msys.mizuma@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json

pytest.importorskip('xmltodict')

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

# ndctl_region: the mock return value of pmem_run_command with:
# ndctl list -R
ndctl_region = """[
  {
    "dev":"region1",
    "size":51539607552,
    "align":16777216,
    "available_size":50465865728,
    "max_available_extent":50465865728,
    "type":"pmem",
    "iset_id":4694373484956518536,
    "persistence_domain":"memory_controller"
  },
  {
    "dev":"region0",
    "size":51539607552,
    "align":16777216,
    "available_size":51539607552,
    "max_available_extent":51539607552,
    "type":"pmem",
    "iset_id":4588538894081362056,
    "persistence_domain":"memory_controller"
  }
]"""

# ndctl_region_empty: the mock return value of pmem_run_command with:
# ndctl list -R
ndctl_region_empty = ""

# ndctl_without_size: the mock return value of pmem_run_command with:
# ndctl create-namespace -t pmem -m sector
ndctl_create_without_size = """{
  "dev":"namespace1.0",
  "mode":"sector",
  "size":"47.95 GiB (51.49 GB)",
  "uuid":"1aca23a5-941c-4f4a-9d88-e531f0b5a27e",
  "sector_size":4096,
  "blockdev":"pmem1s"
}"""

# ndctl_list_N: the mock return value of pmem_run_command with:
# ndctl list -N
ndctl_list_N = """[
  {
    "dev":"namespace1.0",
    "mode":"sector",
    "size":51488243712,
    "uuid":"1aca23a5-941c-4f4a-9d88-e531f0b5a27e",
    "sector_size":4096,
    "blockdev":"pmem1s"
  }
]"""

# ndctl_result_1G: the mock return value of pmem_run_command with:
# ndctl create-namespace -t pmem -m sector -s 1073741824
ndctl_create_1G = """{
  "dev":"namespace0.0",
  "mode":"sector",
  "size":"1021.97 MiB (1071.62 MB)",
  "uuid":"5ba4e51b-3028-4b06-8495-b6834867a9af",
  "sector_size":4096,
  "blockdev":"pmem0s"
}"""

# ndctl_result_640M: the mock return value of pmem_run_command with:
# ndctl create-namespace -t pmem -m raw -s 671088640
ndctl_create_640M = """{
  "dev":"namespace1.0",
  "mode":"raw",
  "size":"640.00 MiB (671.09 MB)",
  "uuid":"5ac1f81d-86e6-4f07-9460-8c4d37027f7a",
  "sector_size":512,
  "blockdev":"pmem1"
}"""

# ndctl_list_N_tow_namespaces: the mock return value of pmem_run_command with:
# ndctl list -N
ndctl_list_N_two_namespaces = """[
  {
    "dev":"namespace1.0",
    "mode":"sector",
    "size":1071616000,
    "uuid":"afcf050d-3a8b-4f48-88a5-16d7c40ab2d8",
    "sector_size":4096,
    "blockdev":"pmem1s"
  },
  {
    "dev":"namespace1.1",
    "mode":"raw",
    "size":671088640,
    "uuid":"fb704339-729b-4cc7-b260-079f2633d84f",
    "sector_size":512,
    "blockdev":"pmem1.1"
  }
]"""


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
            self.assertAlmostEqual(test_result[i]['appdirect'], appdirect[i])
            self.assertAlmostEqual(test_result[i]['memorymode'], memmode[i])
            self.assertAlmostEqual(test_result[i]['reserved'], reserved[i])
            if socket:
                self.assertAlmostEqual(test_result[i]['socket'], i)

    def result_check_ns(self, result, namespace):
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertFalse(result.exception.args[0]['reboot_required'])

        test_result = result.exception.args[0]['result']
        expected = json.loads(namespace)

        for i, result in enumerate(test_result):
            self.assertEqual(result['dev'], expected[i]['dev'])
            self.assertEqual(result['size'], expected[i]['size'])

    def test_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            pmem_module.main()

    def test_fail_when_appdirect_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'appdirect': 10,
            })
            pmem_module.main()

    def test_fail_when_MemosyMode_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'memorymode': 70,
            })
            pmem_module.main()

    def test_fail_when_reserved_only(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'reserved': 10,
            })
            pmem_module.main()

    def test_fail_when_appdirect_memorymode_reserved_total_not_100(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'appdirect': 10,
                'memorymode': 70,
                'reserved': 10,
            })
            pmem_module.main()

    def test_when_appdirect_memorymode(self):
        set_module_args({
            'appdirect': 10,
            'memorymode': 70,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_when_appdirect_memorymode_reserved(self):
        set_module_args({
            'appdirect': 10,
            'memorymode': 70,
            'reserved': 20,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_when_appdirect_notinterleaved_memorymode_reserved(self):
        set_module_args({
            'appdirect': 10,
            'appdirect_interleaved': False,
            'memorymode': 70,
            'reserved': 20,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[goal_plain, goal, dimmlist]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check(result, False, [25769803776], [188978561024], [328230764544])

    def test_fail_when_socket_id_appdirect(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'socket': [
                    {
                        'id': 0,
                        'appdirect': 10,
                    },
                    {
                        'id': 1,
                        'appdirect': 10,
                    },
                ],
            })
            pmem_module.main()

    def test_fail_when_socket0_id_memorymode_socket1_id_appdirect(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'socket': [
                    {
                        'id': 0,
                        ' memorymode': 70,
                    },
                    {
                        'id': 1,
                        'appdirect': 10,
                    },
                ],
            })
            pmem_module.main()

    def test_fail_when_socket0_without_id(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'socket': [
                    {
                        'appdirect': 10,
                        'memorymode': 70,
                    },
                    {
                        'id': 1,
                        'appdirect': 10,
                        'memorymode': 70,
                    },
                ],
            })
            pmem_module.main()

    def test_when_socket0_and_1_appdirect_memorymode(self):
        set_module_args({
            'socket': [
                {
                    'id': 0,
                    'appdirect': 10,
                    'memorymode': 70,
                },
                {
                    'id': 1,
                    'appdirect': 10,
                    'memorymode': 70,
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

    def test_when_socket0_and_1_appdirect_memorymode_reserved(self):
        set_module_args({
            'socket': [
                {
                    'id': 0,
                    'appdirect': 10,
                    'memorymode': 70,
                    'reserved': 20,
                },
                {
                    'id': 1,
                    'appdirect': 10,
                    'memorymode': 70,
                    'reserved': 20,
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

    def test_when_socket0_appdirect_notinterleaved_memorymode_reserved_socket1_appdirect_memorymode_reserved(self):
        set_module_args({
            'socket': [
                {
                    'id': 0,
                    'appdirect': 10,
                    'appdirect_interleaved': False,
                    'memorymode': 70,
                    'reserved': 20,
                },
                {
                    'id': 1,
                    'appdirect': 10,
                    'memorymode': 70,
                    'reserved': 20,
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

    def test_fail_when_namespace_without_mode(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '1GB',
                        'type': 'pmem',
                    },
                    {
                        'size': '2GB',
                        'type': 'blk',
                    },
                ],
            })
            pmem_module.main()

    def test_fail_when_region_is_empty(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '1GB',
                        'type': 'pmem',
                        'mode': 'sector',
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region_empty]):
                pmem_module.main()

    def test_fail_when_namespace_invalid_size(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '1XXX',
                        'type': 'pmem',
                        'mode': 'sector',
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region]):
                pmem_module.main()

    def test_fail_when_size_is_invalid_alignment(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '400MB',
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                    {
                        'size': '500MB',
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region]):
                pmem_module.main()

    def test_fail_when_blk_is_unsupported_type(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '4GB',
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                    {
                        'size': '5GB',
                        'type': 'blk',
                        'mode': 'sector'
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region]):
                pmem_module.main()

    def test_fail_when_size_isnot_set_to_multiple_namespaces(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                    {
                        'size': '500GB',
                        'type': 'blk',
                        'mode': 'sector'
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region]):
                pmem_module.main()

    def test_fail_when_size_of_namespace_over_available(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'namespace': [
                    {
                        'size': '400GB',
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                    {
                        'size': '500GB',
                        'type': 'pmem',
                        'mode': 'sector'
                    },
                ],
            })
            with patch(
                    'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                    side_effect=[ndctl_region]):
                pmem_module.main()

    def test_when_namespace0_without_size(self):
        set_module_args({
            'namespace': [
                {
                    'type': 'pmem',
                    'mode': 'sector'
                },
            ],
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[ndctl_region, ndctl_create_without_size, ndctl_list_N]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check_ns(result, ndctl_list_N)

    def test_when_namespace0_with_namespace_append(self):
        set_module_args({
            'namespace': [
                {
                    'size': '640MB',
                    'type': 'pmem',
                    'mode': 'raw'
                },
            ],
            'namespace_append': True,
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[ndctl_region, ndctl_create_640M, ndctl_list_N_two_namespaces]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check_ns(result, ndctl_list_N_two_namespaces)

    def test_when_namespace0_1GiB_pmem_sector_namespace1_640MiB_pmem_raw(self):
        set_module_args({
            'namespace': [
                {
                    'size': '1GB',
                    'type': 'pmem',
                    'mode': 'sector'
                },
                {
                    'size': '640MB',
                    'type': 'pmem',
                    'mode': 'raw',
                },
            ],
        })
        with patch(
                'ansible_collections.community.general.plugins.modules.storage.pmem.pmem.PersistentMemory.pmem_run_command',
                side_effect=[ndctl_region, ndctl_create_1G, ndctl_create_640M, ndctl_list_N_two_namespaces]):
            with self.assertRaises(AnsibleExitJson) as result:
                pmem_module.main()
            self.result_check_ns(result, ndctl_list_N_two_namespaces)

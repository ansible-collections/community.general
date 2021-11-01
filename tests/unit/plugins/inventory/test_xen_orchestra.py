# -*- coding: utf-8 -*-
# Copyright (c) 2020, Jeffrey van Pelt <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# The API responses used in these tests were recorded from PVE version 6.2.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.xen_orchestra import InventoryModule

objects = {
    'vms': {
        '8900449d-44a2-e5f5-f692-a110c758b351':
            {
                'type': 'VM',
                'addresses': {},
                'CPUs': {'max': 4, 'number': 4}, 'current_operations': {},
                'memory': {'dynamic': [8589934592, 8589934592], 'static': [134217728, 8589934592], 'size': 8589934592},
                'installTime': 1626873121, 'name_description': '', 'name_label': 'XCP-NG lab',
                'os_version': {}, 'parent': '45b83446-23e8-f623-56d7-ea4eb55c2818', 'power_state': 'Running', 'hasVendorDevice': False,
                'snapshots': ['45b83446-23e8-f623-56d7-ea4eb55c2818', 'e46a28eb-b069-7a5b-91ef-1b2f002e6c78', '52ae0c8b-7be8-9eb1-f2d1-f37f806f2429'], 'startDelay': 0, 'startTime': 1633076244, 'secureBoot': False, 'tags': [],
                'VIFs': ['7a8a9d85-a547-db0a-f101-be9bb16e94a1'], 'virtualizationMode': 'hvm', 'xenTools': False, 'managementAgentDetected': False, 'pvDriversDetected': False, '$container': '222d8594-9426-468a-ad69-7a6f02330fa3',
                '$VBDs': ['2c0525d1-15b0-6c5a-10e7-a86418aa42cc', 'aa56c52b-63cc-49c1-1fd4-81ed330685d8'],
                'VGPUs': [],
                '$VGPUs': [],
                'vga': 'cirrus', 'videoram': 4,
                'id': '8900449d-44a2-e5f5-f692-a110c758b351',
                'uuid': '8900449d-44a2-e5f5-f692-a110c758b351',
                '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
            },
        '0e64588-2bea-2d82-e922-881654b0a48f':
            {
                'type': 'VM',
                'addresses': {},
                'auto_poweron': False,
                'CPUs': {'max': 1, 'number': 1}, 'current_operations': {},
                'expNestedHvm': False,
                'high_availability': '',
                'memory': {'dynamic': [1073741824, 2147483648], 'static': [536870912, 4294967296], 'size': 2147483648},
                'installTime': 1599049252,
                'name_description': '',
                'name_label': 'rajaa - XS 7.1',
                'os_version': {},
                'parent': 'd3af89b2-d846-0874-6acb-031ccf11c560',
                'power_state': 'Halted',
                'hasVendorDevice': False,
                'snapshots': ['d3af89b2-d846-0874-6acb-031ccf11c560'],
                'startDelay': 0,
                'startTime': None,
                'secureBoot': False,
                'tags': [],
                'VIFs': ['889ea35b-a0f9-2d07-eacf-345d3e45664b'],
                'virtualizationMode': 'hvm',
                '$container': '355ee47d-ff4c-4924-3db2-fd86ae629676',
                '$VBDs': ['1131abdd-99f7-548f-c727-26fe7626f890', 'b21a2342-cc1d-38b0-ebb9-f2c22d5051c5'],
                'VGPUs': [],
                '$VGPUs': [],
                'vga': 'std',
                'videoram': '8',
                'id': '0e645898-2bea-2d82-e922-881654b0a48f',
                'uuid': '0e645898-2bea-2d82-e922-881654b0a48f',
                '$pool': '355ee47d-ff4c-4924-3db2-fd86ae629676',
                '$poolId': '355ee47d-ff4c-4924-3db2-fd86ae629676'
            },
        'b0d25e70-019d-6182-2f7c-b0f5d8ef9331':
            {
                'type': 'VM',
                'addresses': {'0/ipv4/0': '192.168.1.55', '1/ipv4/0': '10.0.90.1'},
                'auto_poweron': False,
                'CPUs': {'max': 4, 'number': 4},
                'current_operations': {},
                'expNestedHvm': False, 'mainIpAddress': '192.168.1.55',
                'memory': {'dynamic': [2147483648, 2147483648], 'static': [134217728, 2147483648], 'size': 2147483648},
                'installTime': None,
                'name_description': '',
                'name_label': 'SamTest PfSense',
                'os_version': {'name': 'FreeBSD 11.3-STABLE', 'uname': '11.3-STABLE', 'distro': 'FreeBSD'},
                'power_state': 'Halted',
                'hasVendorDevice': False,
                'snapshots': [],
                'startDelay': 0,
                'startTime': None,
                'secureBoot': False,
                'tags': [],
                'VIFs': ['92e4825d-78c8-a2db-925e-d934059942f5', '5ffc904e-6b15-fe6e-c1da-efe9168ff0c0'],
                'virtualizationMode': 'hvm',
                '$container': '355ee47d-ff4c-4924-3db2-fd86ae629676',
                '$VBDs': ['2e318246-1248-5035-8aa1-bee8672a09fe', 'a41cf8ef-01b2-9899-6a6d-1e35e026ae3b'],
                'VGPUs': [],
                '$VGPUs': [],
                'vga': 'cirrus',
                'videoram': 4,
                'coresPerSocket': 4,
                'id': 'b0d25e70-019d-6182-2f7c-b0f5d8ef9331',
                'uuid': 'b0d25e70-019d-6182-2f7c-b0f5d8ef9331',
                '$pool': '355ee47d-ff4c-4924-3db2-fd86ae629676',
                '$poolId': '355ee47d-ff4c-4924-3db2-fd86ae629676'
            }
    },
    'pools': {
            '3d315997-73bd-5a74-8ca7-289206cb03ab': {
                'current_operations': {},
                'HA_enabled': False,
                'master': '222d8594-9426-468a-ad69-7a6f02330fa3',
                'tags': [],
                'name_description': '',
                'name_label': 'Storage Lab',
                'xosanPackInstallationTime': None,
                'cpus': {'cores': 120, 'sockets': 6},
                'zstdSupported': True,
                'id': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                'type': 'pool',
                'uuid': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'},
            'bb538461-80ce-c712-1083-699dd8b8163f': {
                'current_operations': {},
                'default_SR': '63b86645-2fc2-2497-8e58-1dcd7c86939b',
                'HA_enabled': False,
                'master': 'b181faa0-e9c4-4e26-a029-463d726a63c0',
                'tags': [],
                'name_description': '',
                'name_label': 'runx prod',
                'xosanPackInstallationTime': None,
                'otherConfig': {'memory-ratio-hvm': '0.25', 'memory-ratio-pv': '0.25'},
                'cpus': {'cores': 4, 'sockets': 4},
                'zstdSupported': True,
                'id': 'bb538461-80ce-c712-1083-699dd8b8163f',
                'type': 'pool',
                'uuid': 'bb538461-80ce-c712-1083-699dd8b8163f',
                '$pool': 'bb538461-80ce-c712-1083-699dd8b8163f',
                '$poolId': 'bb538461-80ce-c712-1083-699dd8b8163f'
            },
            '682fdbf8-df62-e0d9-3f3c-266624e092d1': {
                'current_operations': {},
                'default_SR': '040ad5c2-d9a6-bd98-fd38-97807d24d4fb',
                'HA_enabled': False,
                'master': 'a450c97c-4b40-482f-afc9-86153e6135cd',
                'tags': [],
                'name_description': '',
                'name_label': 'runx prod 2',
                'xosanPackInstallationTime': None,
                'otherConfig': {'memory-ratio-hvm': '0.25', 'memory-ratio-pv': '0.25'},
                'cpus': {'cores': 2, 'sockets': 2},
                'zstdSupported': True,
                'id': '682fdbf8-df62-e0d9-3f3c-266624e092d1',
                'type': 'pool',
                'uuid': '682fdbf8-df62-e0d9-3f3c-266624e092d1',
                '$pool': '682fdbf8-df62-e0d9-3f3c-266624e092d1',
                '$poolId': '682fdbf8-df62-e0d9-3f3c-266624e092d1'
            },
    },
    'hosts': {
        'c96ec4dd-28ac-4df4-b73c-4371bd202728': {
            'CPUs': {
                'cpu_count': '40',
                'socket_count': '2', 'vendor': 'GenuineIntel', 'speed': '1699.998', 'modelname': 'Intel(R) Xeon(R) CPU E5-2650L v2 @ 1.70GHz',
                'family': '6', 'model': '62', 'stepping': '4'
            },
            'address': '172.16.210.14',
            'build': 'release/stockholm/master/7',
            'chipset_info': {'iommu': True},
            'enabled': True,
            'controlDomain': 'bc557b9a-9c97-4829-87c1-6765b857e9e5',
            'cpus': {'cores': 40, 'sockets': 2},
            'current_operations': {},
            'hostname': 'r620-s1',
            'iscsiIqn': 'iqn.2020-03.com.example:d71399bd', 'zstdSupported': True,
            'license_server': {'address': 'localhost', 'port': '27000'},
            'license_expiry': None,
            'logging': {},
            'name_description': 'Default install',
            'name_label': 'R620-S1',
            'memory': {'usage': 45283590144, 'size': 137391292416},
            'multipathing': False,
            'patches': [],
            'powerOnMode': '',
            'power_state': 'Running',
            'startTime': 1625749690, 'supplementalPacks': [], 'agentStartTime': 1625749776, 'rebootRequired': False, 'tags': [], 'version': '8.2.0', 'productBrand': 'XCP-ng', 'hvmCapable': True, 'certificates': [],
            'id': 'c96ec4dd-28ac-4df4-b73c-4371bd202728',
            'type': 'host',
                    'uuid': 'c96ec4dd-28ac-4df4-b73c-4371bd202728', '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab', '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
        },
        'ddcd3461-7052-4f5e-932c-e1ed75c192d6': {
            'CPUs': {
                'cpu_count': '40',
                'socket_count': '2',
                'vendor': 'GenuineIntel',
                'speed': '1700.007', 'modelname': 'Intel(R) Xeon(R) CPU E5-2650L v2 @ 1.70GHz',
                'family': '6',
                'model': '62',
                'stepping': '4'
            },
            'address': '172.16.210.16',
            'build': 'release/stockholm/master/7',
            'chipset_info': {'iommu': True}, 'enabled': True, 'controlDomain': 'e9e1922f-ca2b-4259-9e0a-9b11277e276d',
            'cpus': {'cores': 40, 'sockets': 2},
            'current_operations': {},
            'hostname': 'r620-s3',
            'iscsiIqn': 'iqn.2020-03.com.example:964057e9', 'zstdSupported': True,
            'name_description': 'Default install',
            'name_label': 'R620-S3',
            'memory': {'usage': 10636521472, 'size': 137391292416}, 'multipathing': False,
            'powerOnMode': '', 'power_state': 'Running', 'startTime': 1625154580, 'supplementalPacks': [],
            'agentStartTime': 1635336654, 'rebootRequired': False, 'tags': [], 'version': '8.2.0', 'productBrand': 'XCP-ng', 'hvmCapable': True,
            'certificates': [],
            'id': '222d8594-9426-468a-ad69-7a6f02330fa3',
            'type': 'host',
                    'uuid': '222d8594-9426-468a-ad69-7a6f02330fa3',
                    '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab', '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
        }
    }
}


@ pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.xen_orchestra.yml') is False


def test_populate(inventory):
    inventory._populate(objects)
    print(inventory.inventory.serialize())

    assert 'foo' in inventory.inventory.groups

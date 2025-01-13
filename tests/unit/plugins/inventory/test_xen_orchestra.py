# -*- coding: utf-8 -*-
# Copyright (c) 2020, Jeffrey van Pelt <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The API responses used in these tests were recorded from PVE version 6.2.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.xen_orchestra import InventoryModule

objects = {
    'vms': {
        '0e64588-2bea-2d82-e922-881654b0a48f':
            {
                'type': 'VM',
                'addresses': {},
                'CPUs': {'max': 4, 'number': 4},
                'memory': {'dynamic': [1073741824, 2147483648], 'static': [536870912, 4294967296], 'size': 2147483648},
                'name_description': '',
                'name_label': 'XCP-NG lab 2',
                'os_version': {},
                'parent': 'd3af89b2-d846-0874-6acb-031ccf11c560',
                'power_state': 'Running',
                'tags': [],
                'id': '0e645898-2bea-2d82-e922-881654b0a48f',
                'uuid': '0e645898-2bea-2d82-e922-881654b0a48f',
                '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$container': '222d8594-9426-468a-ad69-7a6f02330fa3'
            },
        'b0d25e70-019d-6182-2f7c-b0f5d8ef9331':
            {
                'type': 'VM',
                'addresses': {'0/ipv4/0': '192.168.1.55', '1/ipv4/0': '10.0.90.1'},
                'CPUs': {'max': 4, 'number': 4},
                'mainIpAddress': '192.168.1.55',
                'memory': {'dynamic': [2147483648, 2147483648], 'static': [134217728, 2147483648], 'size': 2147483648},
                'name_description': '',
                'name_label': 'XCP-NG lab 3',
                'os_version': {'name': 'FreeBSD 11.3-STABLE', 'uname': '11.3-STABLE', 'distro': 'FreeBSD'},
                'power_state': 'Halted',
                'tags': [],
                'id': 'b0d25e70-019d-6182-2f7c-b0f5d8ef9331',
                'uuid': 'b0d25e70-019d-6182-2f7c-b0f5d8ef9331',
                '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab',
                '$container': 'c96ec4dd-28ac-4df4-b73c-4371bd202728',
            }
    },
    'pools': {
        '3d315997-73bd-5a74-8ca7-289206cb03ab': {
            'master': '222d8594-9426-468a-ad69-7a6f02330fa3',
            'tags': [],
            'name_description': '',
            'name_label': 'Storage Lab',
            'cpus': {'cores': 120, 'sockets': 6},
            'id': '3d315997-73bd-5a74-8ca7-289206cb03ab',
            'type': 'pool',
            'uuid': '3d315997-73bd-5a74-8ca7-289206cb03ab',
            '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
            '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
        }
    },
    'hosts': {
        'c96ec4dd-28ac-4df4-b73c-4371bd202728': {
            'type': 'host',
            'uuid': 'c96ec4dd-28ac-4df4-b73c-4371bd202728',
            'enabled': True,
            'CPUs': {
                'cpu_count': '40',
                'socket_count': '2',
                'vendor': 'GenuineIntel',
                'speed': '1699.998',
                'modelname': 'Intel(R) Xeon(R) CPU E5-2650L v2 @ 1.70GHz',
                'family': '6',
                'model': '62',
                'stepping': '4'
            },
            'address': '172.16.210.14',
            'build': 'release/stockholm/master/7',
            'cpus': {'cores': 40, 'sockets': 2},
            'hostname': 'r620-s1',
            'name_description': 'Default install',
            'name_label': 'R620-S1',
            'memory': {'usage': 45283590144, 'size': 137391292416},
            'power_state': 'Running',
            'tags': [],
            'version': '8.2.0',
            'productBrand': 'XCP-ng',
            'id': 'c96ec4dd-28ac-4df4-b73c-4371bd202728',
            '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
            '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
        },
        '222d8594-9426-468a-ad69-7a6f02330fa3': {
            'type': 'host',
            'uuid': '222d8594-9426-468a-ad69-7a6f02330fa3',
            'enabled': True,
            'CPUs': {
                'cpu_count': '40',
                'socket_count': '2',
                'vendor': 'GenuineIntel',
                'speed': '1700.007',
                'modelname': 'Intel(R) Xeon(R) CPU E5-2650L v2 @ 1.70GHz',
                'family': '6',
                'model': '62',
                'stepping': '4'
            },
            'address': '172.16.210.16',
            'build': 'release/stockholm/master/7',
            'cpus': {'cores': 40, 'sockets': 2},
            'hostname': 'r620-s2',
            'name_description': 'Default install',
            'name_label': 'R620-S2',
            'memory': {'usage': 10636521472, 'size': 137391292416},
            'power_state': 'Running',
            'tags': ['foo', 'bar', 'baz'],
            'version': '8.2.0',
            'productBrand': 'XCP-ng',
            'id': '222d8594-9426-468a-ad69-7a6f02330fa3',
            '$pool': '3d315997-73bd-5a74-8ca7-289206cb03ab',
            '$poolId': '3d315997-73bd-5a74-8ca7-289206cb03ab'
        }
    }
}


def get_option(option):
    if option == 'groups':
        return {}
    elif option == 'keyed_groups':
        return []
    elif option == 'compose':
        return {}
    elif option == 'strict':
        return False
    else:
        return None


def serialize_groups(groups):
    return list(map(str, groups))


@pytest.fixture(scope="module")
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.xen_orchestra.yml') is False


def test_populate(inventory, mocker):
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory._populate(objects)
    actual = sorted(inventory.inventory.hosts.keys())
    expected = sorted(['c96ec4dd-28ac-4df4-b73c-4371bd202728', '222d8594-9426-468a-ad69-7a6f02330fa3',
                       '0e64588-2bea-2d82-e922-881654b0a48f', 'b0d25e70-019d-6182-2f7c-b0f5d8ef9331'])

    assert actual == expected

    # Host with ip assertions
    host_with_ip = inventory.inventory.get_host(
        'b0d25e70-019d-6182-2f7c-b0f5d8ef9331')
    host_with_ip_vars = host_with_ip.vars

    assert host_with_ip_vars['ansible_host'] == '192.168.1.55'
    assert host_with_ip_vars['power_state'] == 'halted'
    assert host_with_ip_vars['type'] == 'VM'

    assert host_with_ip in inventory.inventory.groups['with_ip'].hosts

    # Host without ip
    host_without_ip = inventory.inventory.get_host(
        '0e64588-2bea-2d82-e922-881654b0a48f')
    host_without_ip_vars = host_without_ip.vars

    assert host_without_ip_vars['ansible_host'] is None
    assert host_without_ip_vars['power_state'] == 'running'

    assert host_without_ip in inventory.inventory.groups['without_ip'].hosts

    assert host_with_ip in inventory.inventory.groups['xo_host_r620_s1'].hosts
    assert host_without_ip in inventory.inventory.groups['xo_host_r620_s2'].hosts

    r620_s1 = inventory.inventory.get_host(
        'c96ec4dd-28ac-4df4-b73c-4371bd202728')
    r620_s2 = inventory.inventory.get_host(
        '222d8594-9426-468a-ad69-7a6f02330fa3')

    assert r620_s1.vars['address'] == '172.16.210.14'
    assert r620_s1.vars['tags'] == []
    assert r620_s2.vars['address'] == '172.16.210.16'
    assert r620_s2.vars['tags'] == ['foo', 'bar', 'baz']

    storage_lab = inventory.inventory.groups['xo_pool_storage_lab']

    # Check that hosts are in their corresponding pool
    assert r620_s1 in storage_lab.hosts
    assert r620_s2 in storage_lab.hosts

    # Check that hosts are in their corresponding pool
    assert host_without_ip in storage_lab.hosts
    assert host_with_ip in storage_lab.hosts

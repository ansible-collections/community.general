# -*- coding: utf-8 -*-
# Copyright (c) 2020, FELDSAM s.r.o. - FeldHost™ <support@feldhost.cz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The API responses used in these tests were recorded from OpenNebula version 5.10.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from collections import OrderedDict
import json
import os

import pytest

from ansible import constants as C
from ansible.inventory.data import InventoryData
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader
from ansible_collections.community.internal_test_tools.tests.unit.mock.path import mock_unfrackpath_noop

from ansible_collections.community.general.plugins.inventory.opennebula import InventoryModule


original_exists = os.path.exists
original_access = os.access


def exists_mock(path, exists=True):
    def exists(f):
        if to_native(f) == path:
            return exists
        return original_exists(f)

    return exists


def access_mock(path, can_access=True):
    def access(f, m, *args, **kwargs):
        if to_native(f) == path:
            return can_access
        return original_access(f, m, *args, **kwargs)  # pragma: no cover

    return access


class HistoryEntry(object):
    def __init__(self):
        self.SEQ = '384'
        self.HOSTNAME = 'sam-691-sam'
        self.HID = '10'
        self.CID = '0'
        self.DS_ID = '100'
        self.VM_MAD = 'kvm'
        self.TM_MAD = '3par'
        self.ACTION = '0'


class HistoryRecords(object):
    def __init__(self):
        self.HISTORY = [HistoryEntry()]


@pytest.fixture
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.opennebula.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.opennebula.yml') is False


def get_vm_pool_json():
    with open('tests/unit/plugins/inventory/fixtures/opennebula_inventory.json', 'r') as json_file:
        jsondata = json.load(json_file)

    data = type('pyone.bindings.VM_POOLSub', (object,), {'VM': []})()

    for fake_server in jsondata:
        data.VM.append(type('pyone.bindings.VMType90Sub', (object,), fake_server)())

    return data


def get_vm_pool():
    data = type('pyone.bindings.VM_POOLSub', (object,), {'VM': []})()

    vm = type('pyone.bindings.VMType90Sub', (object,), {
        'DEPLOY_ID': 'one-7157',
        'ETIME': 0,
        'GID': 132,
        'GNAME': 'CSApparelVDC',
        'HISTORY_RECORDS': HistoryRecords(),
        'ID': 7157,
        'LAST_POLL': 1632762935,
        'LCM_STATE': 3,
        'MONITORING': {},
        'NAME': 'sam-691-sam',
        'RESCHED': 0,
        'SNAPSHOTS': [],
        'STATE': 3,
        'STIME': 1632755245,
        'TEMPLATE': OrderedDict({
            'NIC': OrderedDict({
                'AR_ID': '0',
                'BRIDGE': 'onebr80',
                'BRIDGE_TYPE': 'linux',
                'CLUSTER_ID': '0',
                'IP': '172.22.4.187',
                'MAC': '02:00:ac:16:04:bb',
                'MTU': '8192',
                'NAME': 'NIC0',
                'NETWORK': 'Private Net CSApparel',
                'NETWORK_ID': '80',
                'NETWORK_UNAME': 'CSApparelVDC-admin',
                'NIC_ID': '0',
                'PHYDEV': 'team0',
                'SECURITY_GROUPS': '0',
                'TARGET': 'one-7157-0',
                'VLAN_ID': '480',
                'VN_MAD': '802.1Q'
            })
        }),
        'USER_TEMPLATE': OrderedDict({
            'HYPERVISOR': 'kvm',
            'INPUTS_ORDER': '',
            'LOGO': 'images/logos/centos.png',
            'MEMORY_UNIT_COST': 'MB',
            'SCHED_REQUIREMENTS': 'CLUSTER_ID="0"'
        })
    })()
    data.VM.append(vm)

    vm = type('pyone.bindings.VMType90Sub', (object,), {
        'DEPLOY_ID': 'one-327',
        'ETIME': 0,
        'GID': 0,
        'GNAME': 'oneadmin',
        'HISTORY_RECORDS': [],
        'ID': 327,
        'LAST_POLL': 1632763543,
        'LCM_STATE': 3,
        'MONITORING': {},
        'NAME': 'zabbix-327',
        'RESCHED': 0,
        'SNAPSHOTS': [],
        'STATE': 3,
        'STIME': 1575410106,
        'TEMPLATE': OrderedDict({
            'NIC': [
                OrderedDict({
                    'AR_ID': '0',
                    'BRIDGE': 'onerb.103',
                    'BRIDGE_TYPE': 'linux',
                    'IP': '185.165.1.1',
                    'IP6_GLOBAL': '2000:a001::b9ff:feae:aa0d',
                    'IP6_LINK': 'fe80::b9ff:feae:aa0d',
                    'MAC': '02:00:b9:ae:aa:0d',
                    'NAME': 'NIC0',
                    'NETWORK': 'Public',
                    'NETWORK_ID': '7',
                    'NIC_ID': '0',
                    'PHYDEV': 'team0',
                    'SECURITY_GROUPS': '0',
                    'TARGET': 'one-327-0',
                    'VLAN_ID': '100',
                    'VN_MAD': '802.1Q'
                }),
                OrderedDict({
                    'AR_ID': '0',
                    'BRIDGE': 'br0',
                    'BRIDGE_TYPE': 'linux',
                    'CLUSTER_ID': '0',
                    'IP': '192.168.1.1',
                    'MAC': '02:00:c0:a8:3b:01',
                    'NAME': 'NIC1',
                    'NETWORK': 'Management',
                    'NETWORK_ID': '11',
                    'NIC_ID': '1',
                    'SECURITY_GROUPS': '0',
                    'TARGET': 'one-327-1',
                    'VN_MAD': 'bridge'
                })
            ]
        }),
        'USER_TEMPLATE': OrderedDict({
            'HYPERVISOR': 'kvm',
            'INPUTS_ORDER': '',
            'LABELS': 'Oracle Linux',
            'LOGO': 'images/logos/centos.png',
            'MEMORY_UNIT_COST': 'MB',
            'SAVED_TEMPLATE_ID': '29'
        })
    })()
    data.VM.append(vm)

    vm = type('pyone.bindings.VMType90Sub', (object,), {
        'DEPLOY_ID': 'one-107',
        'ETIME': 0,
        'GID': 0,
        'GNAME': 'oneadmin',
        'HISTORY_RECORDS': [],
        'ID': 107,
        'LAST_POLL': 1632764186,
        'LCM_STATE': 3,
        'MONITORING': {},
        'NAME': 'gitlab-107',
        'RESCHED': 0,
        'SNAPSHOTS': [],
        'STATE': 3,
        'STIME': 1572485522,
        'TEMPLATE': OrderedDict({
            'NIC': OrderedDict({
                'AR_ID': '0',
                'BRIDGE': 'onerb.103',
                'BRIDGE_TYPE': 'linux',
                'IP': '185.165.1.3',
                'IP6_GLOBAL': '2000:a001::b9ff:feae:aa03',
                'IP6_LINK': 'fe80::b9ff:feae:aa03',
                'MAC': '02:00:b9:ae:aa:03',
                'NAME': 'NIC0',
                'NETWORK': 'Public',
                'NETWORK_ID': '7',
                'NIC_ID': '0',
                'PHYDEV': 'team0',
                'SECURITY_GROUPS': '0',
                'TARGET': 'one-107-0',
                'VLAN_ID': '100',
                'VN_MAD': '802.1Q'
            })
        }),
        'USER_TEMPLATE': OrderedDict({
            'HYPERVISOR': 'kvm',
            'INPUTS_ORDER': '',
            'LABELS': 'Gitlab,Centos',
            'LOGO': 'images/logos/centos.png',
            'MEMORY_UNIT_COST': 'MB',
            'SCHED_REQUIREMENTS': 'ID="0" | ID="1" | ID="2"',
            'SSH_PORT': '8822'
        })
    })()
    data.VM.append(vm)

    return data


options_base_test = {
    'api_url': 'https://opennebula:2633/RPC2',
    'api_username': 'username',
    'api_password': 'password',
    'api_authfile': '~/.one/one_auth',
    'hostname': 'v4_first_ip',
    'group_by_labels': True,
    'filter_by_label': None,
}


# given a dictionary `opts_dict`, return a function that behaves like ansible's inventory get_options
def mk_get_options(opts_dict):
    def inner(opt):
        return opts_dict.get(opt, False)
    return inner


def test_get_connection_info(inventory, mocker):
    inventory.get_option = mocker.MagicMock(side_effect=mk_get_options(options_base_test))

    auth = inventory._get_connection_info()
    assert (auth.username and auth.password)


def test_populate_constructable_templating(mocker):
    inventory_filename = '/fake/opennebula.yml'

    mocker.patch.object(InventoryModule, '_get_vm_pool', side_effect=get_vm_pool_json)
    mocker.patch('ansible_collections.community.general.plugins.inventory.opennebula.HAS_PYONE', True)
    mocker.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    mocker.patch('os.path.exists', exists_mock(inventory_filename))
    mocker.patch('os.access', access_mock(inventory_filename))

    # the templating engine is needed for the constructable groups/vars
    # so give that some fake data and instantiate it.
    C.INVENTORY_ENABLED = ['community.general.opennebula']
    inventory_file = {inventory_filename: r'''
---
plugin: community.general.opennebula
api_url: https://opennebula:2633/RPC2
api_username: username
api_password: password
api_authfile: '~/.one/one_auth'
hostname: v4_first_ip
group_by_labels: true
compose:
  is_linux: GUEST_OS == 'linux'
filter_by_label: bench
groups:
  benchmark_clients: TGROUP.endswith('clients')
  lin: is_linux == true
keyed_groups:
  - key: TGROUP
    prefix: tgroup
'''}
    im = InventoryManager(loader=DictDataLoader(inventory_file), sources=inventory_filename)

    # note the vm_pool (and json data file) has four hosts,
    # but the options above asks ansible to filter one out
    assert len(get_vm_pool_json().VM) == 4
    assert set([vm.NAME for vm in get_vm_pool_json().VM]) == set([
        'terraform_demo_00',
        'terraform_demo_01',
        'terraform_demo_srv_00',
        'bs-windows',
    ])
    assert set(im._inventory.hosts) == set(['terraform_demo_00', 'terraform_demo_01', 'terraform_demo_srv_00'])

    host_demo00 = im._inventory.get_host('terraform_demo_00')
    host_demo01 = im._inventory.get_host('terraform_demo_01')
    host_demosrv = im._inventory.get_host('terraform_demo_srv_00')

    assert 'benchmark_clients' in im._inventory.groups
    assert 'lin' in im._inventory.groups
    assert im._inventory.groups['benchmark_clients'].hosts == [host_demo00, host_demo01]
    assert im._inventory.groups['lin'].hosts == [host_demo00, host_demo01, host_demosrv]

    # test group by label:
    assert 'bench' in im._inventory.groups
    assert 'foo' in im._inventory.groups
    assert im._inventory.groups['bench'].hosts == [host_demo00, host_demo01, host_demosrv]
    assert im._inventory.groups['serv'].hosts == [host_demosrv]
    assert im._inventory.groups['foo'].hosts == [host_demo00, host_demo01]

    # test `compose` transforms GUEST_OS=Linux to is_linux == True
    assert host_demo00.get_vars()['GUEST_OS'] == 'linux'
    assert host_demo00.get_vars()['is_linux'] is True

    # test `keyed_groups`
    assert im._inventory.groups['tgroup_bench_clients'].hosts == [host_demo00, host_demo01]
    assert im._inventory.groups['tgroup_bench_server'].hosts == [host_demosrv]


def test_populate(inventory, mocker):
    # bypass API fetch call
    inventory._get_vm_pool = mocker.MagicMock(side_effect=get_vm_pool)
    inventory.get_option = mocker.MagicMock(side_effect=mk_get_options(options_base_test))
    inventory._populate()

    # get different hosts
    host_sam = inventory.inventory.get_host('sam-691-sam')
    host_zabbix = inventory.inventory.get_host('zabbix-327')
    host_gitlab = inventory.inventory.get_host('gitlab-107')

    # test if groups exists
    assert 'Gitlab' in inventory.inventory.groups
    assert 'Centos' in inventory.inventory.groups
    assert 'Oracle_Linux' in inventory.inventory.groups

    # check if host_zabbix is in Oracle_Linux group
    group_oracle_linux = inventory.inventory.groups['Oracle_Linux']
    assert group_oracle_linux.hosts == [host_zabbix]

    # check if host_gitlab is in Gitlab and Centos group
    group_gitlab = inventory.inventory.groups['Gitlab']
    group_centos = inventory.inventory.groups['Centos']
    assert group_gitlab.hosts == [host_gitlab]
    assert group_centos.hosts == [host_gitlab]

    # check IPv4 address
    assert '172.22.4.187' == host_sam.get_vars()['v4_first_ip']

    # check IPv6 address
    assert '2000:a001::b9ff:feae:aa0d' == host_zabbix.get_vars()['v6_first_ip']

    # check ansible_hosts
    assert '172.22.4.187' == host_sam.get_vars()['ansible_host']
    assert '185.165.1.1' == host_zabbix.get_vars()['ansible_host']
    assert '185.165.1.3' == host_gitlab.get_vars()['ansible_host']

    # check for custom ssh port
    assert '8822' == host_gitlab.get_vars()['ansible_port']

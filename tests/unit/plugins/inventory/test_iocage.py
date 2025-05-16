# -*- coding: utf-8 -*-

# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import yaml

from ansible.inventory.data import InventoryData
from ansible.template import Templar
from ansible_collections.community.general.plugins.inventory.iocage import InventoryModule


@pytest.fixture
def inventory():
    inv = InventoryModule()
    inv.inventory = InventoryData()
    inv.templar = Templar(None)
    inv.jails = load_txt_data('tests/unit/plugins/inventory/fixtures/iocage_jails.txt')
    inv.js_ok = load_yml_data('tests/unit/plugins/inventory/fixtures/iocage_jails.yml')
    prpts_101 = load_txt_data('tests/unit/plugins/inventory/fixtures/iocage_properties_test_101.txt')
    prpts_102 = load_txt_data('tests/unit/plugins/inventory/fixtures/iocage_properties_test_102.txt')
    prpts_103 = load_txt_data('tests/unit/plugins/inventory/fixtures/iocage_properties_test_103.txt')
    inv.prpts = {'test_101': prpts_101, 'test_102': prpts_102, 'test_103': prpts_103}
    inv.ps_ok = load_yml_data('tests/unit/plugins/inventory/fixtures/iocage_properties.yml')
    inv.ok = load_yml_data('tests/unit/plugins/inventory/fixtures/iocage_inventory.yml')
    return inv


def load_txt_data(path):
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s


def load_yml_data(path):
    f = open(path, 'r')
    d = yaml.safe_load(f)
    f.close()
    return d


def get_option(option):
    groups = {}
    groups['test'] = "inventory_hostname.startswith('test')"

    if option == 'groups':
        return groups
    elif option == 'keyed_groups':
        return []
    elif option == 'compose':
        return {}
    elif option == 'strict':
        return False
    else:
        return None


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.iocage.yml') is False


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.iocage.yml"
    file.touch()
    assert inventory.verify_file(str(file))


def test_get_jails(inventory):
    results = {'_meta': {'hostvars': {}}}
    inventory.get_jails(inventory.jails, results)
    assert results == inventory.js_ok


def test_get_properties(inventory):
    results = {'_meta': {'hostvars': {}}}
    inventory.get_jails(inventory.jails, results)
    for hostname, host_vars in results['_meta']['hostvars'].items():
        inventory.get_properties(inventory.prpts[hostname], results, hostname)
    assert results == inventory.ps_ok


def test_populate(inventory, mocker):
    results = {'_meta': {'hostvars': {}}}
    inventory.get_jails(inventory.jails, results)
    for hostname, host_vars in results['_meta']['hostvars'].items():
        inventory.get_properties(inventory.prpts[hostname], results, hostname)
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory.populate(results)

    # test
    hosts = ('test_101', 'test_102', 'test_103')
    vars = ('iocage_basejail', 'iocage_boot', 'iocage_ip4', 'iocage_ip6', 'iocage_properties',
            'iocage_release', 'iocage_state', 'iocage_template', 'iocage_type')

    # test host_vars
    for host in hosts:
        h = inventory.inventory.get_host(host)
        for var in vars:
            assert inventory.ok['all']['children']['test']['hosts'][host][var] == h.get_vars()[var]

    # test groups
    test_101_info = inventory.inventory.get_host('test_101')
    test_102_info = inventory.inventory.get_host('test_102')
    test_103_info = inventory.inventory.get_host('test_103')
    g = inventory.inventory.groups['test']
    assert g.hosts == [test_101_info, test_102_info, test_103_info]

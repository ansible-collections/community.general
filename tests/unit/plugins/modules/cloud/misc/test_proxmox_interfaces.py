# -*- coding: utf-8 -*-
# Copyright (c) 2021, Andreas Botzner <andreas@botzner.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Proxmox Interface/s modules unit tests.
# The API responses used in these tests were recorded from PVE version 6.4-8

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.general.plugins.module_utils import proxmox_interfaces as proxmox_utils
from ansible_collections.community.general.plugins.modules.cloud.misc import proxmox_interfaces
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock

NODE = 'node01'


def test_map_interface_args(capfd, mocker):
    module = mocker.MagicMock()
    params = {'name': 'vmbr0',
              'type': 'bridge',
              'autostart': True,
              'mtu': 20000,
              'netmask6': 64,
              'vlan_id': 4000,
              'address': None,
              'address6': None,
              'bond_primary': None,
              'bond_mode': None,
              'bond_xmit_hash_policy': None,
              'bridge_vlan_ports': None,
              'bridge_ports': None,
              'cidr': None,
              'cidr6': None,
              'gateway': None,
              'gateway6': None,
              'comments': None,
              'netmask': None,
              'ovs_tag': None,
              'ovs_bonds': None,
              'ovs_bridge': None,
              'ovs_options': None,
              'ovs_ports': None,
              'slaves': None,
              'vlan_raw_device': None}
    expected = {'iface': 'vmbr0',
                'type': 'bridge',
                'autostart': '1',
                'mtu': 20000,
                'netmask6': 64,
                'vlan-id': 4000}
    module.params = params
    ret = proxmox_utils.proxmox_map_interface_args(module.params)
    print(ret)
    assert expected == ret


def test_check_no_doublicates(capfd, mocker):
    module = mocker.MagicMock()
    params = {'config': [{'name': 'vmbr0', 'type': 'bridge'},
                         {'name': 'vmrb1', 'type': 'bridge'}]}

    module.params = params
    module.fail_json.assert_not_called()
    proxmox_utils.check_doublicates(module)
    module.fail_json.assert_not_called()


def test_check_doublicates(capfd, mocker):
    module = mocker.MagicMock()
    iface = 'vmbr0'
    params = {'config': [{'name': iface, 'type': 'bridge'},
                         {'name': iface, 'type': 'bridge'}]}

    module.params = params
    proxmox_utils.check_doublicates(module)
    module.fail_json.assert_called_once_with(
        msg="Interface {0} can only be present once in list".format(iface))

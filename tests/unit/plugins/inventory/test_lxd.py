# Copyright (c) 2021, Frank Dornheim <dornheim@posteo.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import annotations

import pytest

from ansible.inventory.data import InventoryData
from ansible_collections.community.general.plugins.inventory.lxd import InventoryModule


HOST_COMPARATIVE_DATA = {
    "ansible_connection": "ssh",
    "ansible_host": "10.98.143.199",
    "ansible_lxd_os": "ubuntu",
    "ansible_lxd_release": "focal",
    "ansible_lxd_profile": ["default"],
    "ansible_lxd_state": "running",
    "ansible_lxd_location": "Berlin",
    "ansible_lxd_vlan_ids": {"my-macvlan": 666},
    "inventory_hostname": "vlantest",
    "inventory_hostname_short": "vlantest",
}
GROUP_COMPARATIVE_DATA = {
    "all": [],
    "ungrouped": [],
    "testpattern": ["vlantest"],
    "vlan666": ["vlantest"],
    "locationBerlin": ["vlantest"],
    "osUbuntu": ["vlantest"],
    "releaseFocal": ["vlantest"],
    "releaseBionic": [],
    "profileDefault": ["vlantest"],
    "profileX11": [],
    "netRangeIPv4": ["vlantest"],
    "netRangeIPv6": ["vlantest"],
}
GROUP_Config = {
    "testpattern": {"type": "pattern", "attribute": "test"},
    "vlan666": {"type": "vlanid", "attribute": 666},
    "locationBerlin": {"type": "location", "attribute": "Berlin"},
    "osUbuntu": {"type": "os", "attribute": "ubuntu"},
    "releaseFocal": {"type": "release", "attribute": "focal"},
    "releaseBionic": {"type": "release", "attribute": "bionic"},
    "profileDefault": {"type": "profile", "attribute": "default"},
    "profileX11": {"type": "profile", "attribute": "x11"},
    "netRangeIPv4": {"type": "network_range", "attribute": "10.98.143.0/24"},
    "netRangeIPv6": {"type": "network_range", "attribute": "fd42:bd00:7b11:2167:216:3eff::/96"},
}


@pytest.fixture
def inventory():
    inv = InventoryModule()
    inv.inventory = InventoryData()

    # Test Values
    inv.data = inv.load_json_data("tests/unit/plugins/inventory/fixtures/lxd_inventory.atd")  # Load Test Data
    inv.groupby = GROUP_Config
    inv.prefered_instance_network_interface = "eth"
    inv.prefered_instance_network_family = "inet"
    inv.filter = "running"
    inv.dump_data = False
    inv.type_filter = "both"

    return inv


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.lxd.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file("foobar.lxd.yml") is False


def test_build_inventory_hosts(inventory):
    """Load example data and start the inventoryto test the host generation.

    After the inventory plugin has run with the test data, the result of the host is checked."""
    inventory._populate()
    generated_data = inventory.inventory.get_host("vlantest").get_vars()

    eq = True
    for key, value in HOST_COMPARATIVE_DATA.items():
        if generated_data[key] != value:
            eq = False
    assert eq


def test_build_inventory_groups(inventory):
    """Load example data and start the inventory to test the group generation.

    After the inventory plugin has run with the test data, the result of the host is checked."""
    inventory._populate()
    generated_data = inventory.inventory.get_groups_dict()

    eq = True
    for key, value in GROUP_COMPARATIVE_DATA.items():
        if generated_data[key] != value:
            eq = False
    assert eq


def test_build_inventory_groups_with_no_groupselection(inventory):
    """Load example data and start the inventory to test the group generation with groupby is none.

    After the inventory plugin has run with the test data, the result of the host is checked."""
    inventory.groupby = None
    inventory._populate()
    generated_data = inventory.inventory.get_groups_dict()
    group_comparative_data = {"all": [], "ungrouped": []}

    eq = True
    print(f"data: {generated_data}")
    for key, value in group_comparative_data.items():
        if generated_data[key] != value:
            eq = False
    assert eq

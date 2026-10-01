# Copyright 2020 Orion Poplawski <orion@nwra.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.inventory.data import InventoryData
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.loader import inventory_loader

from ansible_collections.community.general.plugins.inventory.cobbler import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


PROFILES = [{"name": "web", "parent": None}]
SYSTEMS = [
    {
        "name": "host1",
        "hostname": "host1",
        "profile": "web",
        "interfaces": {},
        "mgmt_classes": [],
        "owners": [],
        "status": "",
    }
]


@pytest.fixture
def server(mocker):
    server = mocker.patch("ansible_collections.community.general.plugins.inventory.cobbler.xmlrpc_client.Server")
    server.return_value.get_profiles.return_value = PROFILES
    server.return_value.get_systems.return_value = SYSTEMS
    return server.return_value


def _parse(tmp_path, config):
    path = tmp_path / "test.cobbler.yml"
    path.write_text(config)
    plugin = inventory_loader.get("community.general.cobbler")
    inventory = InventoryData()
    plugin.parse(inventory, DataLoader(), str(path))
    return plugin, inventory


def test_parse_without_cache(tmp_path, server):
    plugin, inventory = _parse(tmp_path, "plugin: community.general.cobbler\nurl: http://cobbler/cobbler_api\n")
    assert not hasattr(plugin, "_cache")
    assert "host1" in inventory.hosts
    assert "cobbler_web" in inventory.groups


def test_parse_with_cache(tmp_path, server):
    config = (
        "plugin: community.general.cobbler\n"
        "url: http://cobbler/cobbler_api\n"
        "cache: true\n"
        "cache_plugin: ansible.builtin.jsonfile\n"
        f"cache_connection: {tmp_path / 'cache'}\n"
    )
    plugin, inventory = _parse(tmp_path, config)
    plugin.update_cache_if_changed()
    assert "host1" in inventory.hosts

    server.reset_mock()
    plugin, inventory = _parse(tmp_path, config)
    server.get_profiles.assert_not_called()
    server.get_systems.assert_not_called()
    assert "host1" in inventory.hosts


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.cobbler.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file("foobar.cobbler.yml") is False

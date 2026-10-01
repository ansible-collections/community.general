# Copyright 2020 Orion Poplawski <orion@nwra.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.inventory.cobbler import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_parse_loads_cache_plugin(mocker):
    options = {"url": "http://cobbler/cobbler_api", "cache_plugin": "memory"}
    plugin = InventoryModule()
    mocker.patch.object(plugin, "_read_config_data")
    mocker.patch.object(plugin, "get_option", side_effect=options.get)
    server = mocker.patch("ansible_collections.community.general.plugins.inventory.cobbler.xmlrpc_client.Server")
    server.return_value.get_profiles.return_value = []
    server.return_value.get_systems.return_value = []
    plugin.parse(mocker.MagicMock(), None, "dummy.cobbler.yml")
    assert plugin._cache[plugin.cache_key] == {"profiles": [], "systems": []}


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.cobbler.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file("foobar.cobbler.yml") is False

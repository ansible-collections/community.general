# Copyright (c) 2025 Stéphane Graber <stgraber@stgraber.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible.inventory.data import InventoryData
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
from ansible_collections.community.general.plugins.inventory.incus import (
    InventoryModule,
)


@pytest.fixture(scope="module")
def inventory():
    plugin = InventoryModule()
    plugin.inventory = InventoryData()
    plugin.templar = Templar(loader=DataLoader())
    return plugin


def test_verify_file_yml(tmp_path, inventory):
    file = tmp_path / "foobar.incus.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_yaml(tmp_path, inventory):
    file = tmp_path / "foobar.incus.yaml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config_yml(inventory):
    assert inventory.verify_file("foobar.incus.yml") is False


def test_verify_file_bad_config_yaml(inventory):
    assert inventory.verify_file("foobar.incus.yaml") is False


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file("foobar.wrongcloud.yml") is False


def get_option(option):
    if option == "default_groups":
        return True

    if option == "remotes":
        return ["r1", "r2", "r3:proj1", "r3:proj2"]

    if option == "filters":
        return ["status=running"]

    if option == "host_fqdn":
        return True

    if option == "host_domain":
        return "example.net"

    return False


def _make_host(name):
    entry = {}
    entry["name"] = name

    for prop in (
        "architecture",
        "config",
        "description",
        "devices",
        "ephemeral",
        "expanded_config",
        "expanded_devices",
        "location",
        "profiles",
        "status",
        "type",
    ):
        entry[prop] = ""

    return entry


def run_incus(*args):
    if args == ("project", "list", "r1:"):
        return [{"name": "default"}]

    if args == ("project", "list", "r2:"):
        return [{"name": "foo"}]

    if args == ("list", "r1:", "--project", "default", "status=running"):
        return [_make_host("c1")]

    if args == ("list", "r2:", "--project", "foo", "status=running"):
        return [_make_host("c2")]

    if args == ("list", "r3:", "--project", "proj1", "status=running"):
        return [_make_host("c3")]

    if args == ("list", "r3:", "--project", "proj2", "status=running"):
        return [_make_host("c4"), _make_host("c5")]

    return []


def test_build_inventory(inventory, mocker):
    inventory.get_option = mocker.MagicMock(side_effect=get_option)
    inventory._run_incus = mocker.MagicMock(side_effect=run_incus)
    inventory.populate()

    c1 = inventory.inventory.get_host("c1.default.r1.example.net")
    assert c1
    assert "ansible_incus_status" in c1.get_vars()

    c2 = inventory.inventory.get_host("c2.foo.r2.example.net")
    assert c2
    assert "ansible_incus_status" in c2.get_vars()

    c3 = inventory.inventory.get_host("c3.proj1.r3.example.net")
    assert c3
    assert "ansible_incus_status" in c3.get_vars()

    c4 = inventory.inventory.get_host("c4.proj2.r3.example.net")
    assert c4
    assert "ansible_incus_status" in c4.get_vars()

    c5 = inventory.inventory.get_host("c5.proj2.r3.example.net")
    assert c5
    assert "ansible_incus_status" in c5.get_vars()

    assert len(inventory.inventory.groups["all"].hosts) == 5
    assert len(inventory.inventory.groups["incus"].child_groups) == 3
    assert len(inventory.inventory.groups["incus_r1"].child_groups) == 1
    assert len(inventory.inventory.groups["incus_r2"].child_groups) == 1
    assert len(inventory.inventory.groups["incus_r3"].child_groups) == 2
    assert len(inventory.inventory.groups["incus_r3_proj1"].hosts) == 1
    assert len(inventory.inventory.groups["incus_r3_proj2"].hosts) == 2

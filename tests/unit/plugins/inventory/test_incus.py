# Copyright (c) 2025 Stéphane Graber <stgraber@stgraber.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
from ansible_collections.community.general.plugins.inventory.incus import (
    InventoryModule,
)


@pytest.fixture(scope="module")
def inventory():
    plugin = InventoryModule()
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

# Copyright 2018 Luke Murphy <lukewm@riseup.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

linode_apiv4 = pytest.importorskip("linode_api4")

from ansible.errors import AnsibleError
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
from ansible_collections.community.general.plugins.inventory.linode import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    plugin = InventoryModule()
    plugin.templar = Templar(loader=DataLoader())
    return plugin


def test_missing_access_token_lookup(inventory):
    loader = DataLoader()
    inventory._options = {"access_token": None}
    with pytest.raises(AnsibleError) as error_message:
        inventory._build_client(loader)
        assert "Could not retrieve Linode access token" in error_message


def test_verify_file_yml(tmp_path, inventory):
    file = tmp_path / "foobar.linode.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_yaml(tmp_path, inventory):
    file = tmp_path / "foobar.linode.yaml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config_yml(inventory):
    assert inventory.verify_file("foobar.linode.yml") is False


def test_verify_file_bad_config_yaml(inventory):
    assert inventory.verify_file("foobar.linode.yaml") is False


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file("foobar.wrongcloud.yml") is False

# -*- coding: utf-8 -*-

# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.inventory.iocage import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_init_cache(inventory):
    inventory._init_cache()
    assert inventory._cache[inventory.cache_key] == {}


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.iocage.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.iocage.yml') is False

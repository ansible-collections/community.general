# -*- coding: utf-8 -*-
# Copyright 2020 Orion Poplawski <orion@nwra.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import sys

from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.inventory.cobbler import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_init_cache(inventory):
    inventory._init_cache()
    assert inventory._cache[inventory.cache_key] == {}


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.cobbler.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.cobbler.yml') is False

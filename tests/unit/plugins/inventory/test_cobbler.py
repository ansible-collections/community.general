# -*- coding: utf-8 -*-

# Copyright 2020 Orion Poplawski <orion@nwra.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

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


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.cobber.yml') is False

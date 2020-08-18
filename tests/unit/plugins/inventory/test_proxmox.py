# -*- coding: utf-8 -*-
# Copyright (c) 2020, Robert Kaussow <mail@thegeeklab.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.inventory.proxmox import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.proxmox.yml') is False

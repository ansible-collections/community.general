# Copyright (c) 2020 Shay Rybak <shay.rybak@stackpath.com>
# Copyright (c) 2020 Ansible Project
# GNGeneral Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.errors import AnsibleError, AnsibleParserError
from ansible_collections.community.general.plugins.inventory.stackpath_compute import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_get_stack_slugs(inventory):
    stacks = [
        {
            'status': 'ACTIVE',
            'name': 'test1',
            'id': 'XXXX',
            'updatedAt': '2020-07-08T01:00:00.000000Z',
            'slug': 'test1',
            'createdAt': '2020-07-08T00:00:00.000000Z',
            'accountId': 'XXXX'
        }, {
            'status': 'ACTIVE',
            'name': 'test2',
            'id': 'XXXX',
            'updatedAt': '2019-10-22T18:00:00.000000Z',
            'slug': 'test2',
            'createdAt': '2019-10-22T18:00:00.000000Z',
            'accountId': 'XXXX'
        }, {
            'status': 'DISABLED',
            'name': 'test3',
            'id': 'XXXX',
            'updatedAt': '2020-01-16T20:00:00.000000Z',
            'slug': 'test3',
            'createdAt': '2019-10-15T13:00:00.000000Z',
            'accountId': 'XXXX'
        }, {
            'status': 'ACTIVE',
            'name': 'test4',
            'id': 'XXXX',
            'updatedAt': '2019-11-20T22:00:00.000000Z',
            'slug': 'test4',
            'createdAt': '2019-11-20T22:00:00.000000Z',
            'accountId': 'XXXX'
        }
    ]
    inventory._get_stack_slugs(stacks)
    assert len(inventory.stack_slugs) == 4
    assert inventory.stack_slugs == [
        "test1",
        "test2",
        "test3",
        "test4"
    ]

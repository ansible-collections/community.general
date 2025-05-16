# -*- coding: utf-8 -*-
# Copyright 2018 Luke Murphy <lukewm@riseup.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import sys

linode_apiv4 = pytest.importorskip('linode_api4')
mandatory_py_version = pytest.mark.skipif(
    sys.version_info < (2, 7),
    reason='The linode_api4 dependency requires python2.7 or higher'
)


from ansible.errors import AnsibleError, AnsibleParserError
from ansible.parsing.dataloader import DataLoader
from ansible_collections.community.general.plugins.inventory.linode import InventoryModule


@pytest.fixture(scope="module")
def inventory():
    return InventoryModule()


def test_missing_access_token_lookup(inventory):
    loader = DataLoader()
    inventory._options = {'access_token': None}
    with pytest.raises(AnsibleError) as error_message:
        inventory._build_client(loader)
        assert 'Could not retrieve Linode access token' in error_message


def test_verify_file(tmp_path, inventory):
    file = tmp_path / "foobar.linode.yml"
    file.touch()
    assert inventory.verify_file(str(file)) is True


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('foobar.linode.yml') is False

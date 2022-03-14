# -*- coding: utf-8 -*-

# Copyright 2018 Luke Murphy <lukewm@riseup.net>
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

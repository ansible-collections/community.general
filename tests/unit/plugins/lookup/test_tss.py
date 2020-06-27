# -*- coding: utf-8 -*-
# (c) 2020, Adam Migus <adam@migus.org>
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

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.unittest import TestCase
from ansible_collections.community.general.tests.unit.compat.mock import (
    patch,
    MagicMock,
)
from ansible_collections.community.general.plugins.lookup import tss
from ansible.plugins.loader import lookup_loader


class MockSecretServer(MagicMock):
    RESPONSE = '{"foo":"bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class TestLookupModule(TestCase):
    def setUp(self):
        tss.sdk_is_missing = False
        self.lookup = lookup_loader.get("community.general.tss")

    @patch(
        "ansible_collections.community.general.plugins.lookup.tss.LookupModule.Client",
        MockSecretServer(),
    )
    def test_get_secret_json(self):
        self.assertListEqual(
            [MockSecretServer.RESPONSE],
            self.lookup.run(
                [1],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy",}
            ),
        )

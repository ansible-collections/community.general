# -*- coding: utf-8 -*-
# (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
    RESPONSE = '{"foo": "bar"}'

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
                **{"base_url": "dummy", "username": "dummy", "password": "dummy", }
            ),
        )

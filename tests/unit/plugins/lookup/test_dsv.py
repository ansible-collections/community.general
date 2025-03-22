# -*- coding: utf-8 -*-
# Copyright (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import (
    patch,
    MagicMock,
)
from ansible_collections.community.general.plugins.lookup import dsv
from ansible.plugins.loader import lookup_loader


class MockSecretsVault(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class TestLookupModule(TestCase):
    def setUp(self):
        dsv.sdk_is_missing = False
        self.lookup = lookup_loader.get("community.general.dsv")

    @patch(
        "ansible_collections.community.general.plugins.lookup.dsv.LookupModule.Client",
        MockSecretsVault(),
    )
    def test_get_secret_json(self):
        self.assertListEqual(
            [MockSecretsVault.RESPONSE],
            self.lookup.run(
                ["/dummy"],
                [],
                **{"tenant": "dummy", "client_id": "dummy", "client_secret": "dummy", }
            ),
        )

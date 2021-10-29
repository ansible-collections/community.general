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
from ansible_collections.community.general.plugins.lookup import revbitspss
from ansible.plugins.loader import lookup_loader


class MockSecretsVault(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class TestLookupModule(TestCase):
    def setUp(self):
        revbitspss.sdk_is_missing = None
        self.lookup = lookup_loader.get("community.general.revbitspss")

    @patch(
        "ansible_collections.community.general.plugins.lookup.revbitspss.LookupModule.Client",
        MockSecretsVault(),
    )
    def test_get_secret_json(self):
        self.assertListEqual(
            [MockSecretsVault.RESPONSE],
            self.lookup.run(
                secret_ids=['dummy'],
                base_url='https://server-url-here',
                api_key='api-key-here'
            ),
        )

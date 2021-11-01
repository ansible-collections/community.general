# -*- coding: utf-8 -*-
# (c) 2020, RevBits <info@revbits.com>
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
    RESPONSE = '{"dockerhub": "mP1fD4kY9oG3jI2d"}'

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
                secret_ids=['dockerhub'],
                base_url='https://pam.revbits.net',
                api_key='a0fbb87ea84c07278dfa9d3e25d3af414a7eb61ebdfc4301cf030851481d60291bf81daf604e5652b3111300ab0d8812887736366e109291e4e806892f36e378'
            ),
        )

# -*- coding: utf-8 -*-
# Copyright: (c) 2021, RevBits <info@revbits.com>
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.unittest import TestCase
from ansible_collections.community.general.tests.unit.compat.mock import (
    patch,
    MagicMock,
)
from ansible_collections.community.general.plugins.lookup import revbitspss
from ansible.plugins.loader import lookup_loader


class MockPamSecrets(MagicMock):
    RESPONSE = 'dummy value'

    def get_pam_secret(self, path):
        return self.RESPONSE


class TestLookupModule(TestCase):
    def setUp(self):
        revbitspss.ANOTHER_LIBRARY_IMPORT_ERROR = None
        self.lookup = lookup_loader.get("community.general.revbitspss")

    @patch(
        "ansible_collections.community.general.plugins.lookup.revbitspss.LookupModule.Client",
        MockPamSecrets(),
    )
    def test_get_pam_secret(self):
        terms = ['dummy secret']
        variables = []
        kwargs = {
            "base_url": 'https://dummy.url',
            "api_key": 'dummy'
        }
        self.assertListEqual(
            [{'dummy secret': 'dummy value'}],
            self.lookup.run(terms, variables, **kwargs)
        )

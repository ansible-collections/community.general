# -*- coding: utf-8 -*-
# Copyright (c) 2023, Poh Wei Sheng <weisheng-p@hotmail.sg>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import (
    patch,
    MagicMock,
    mock_open
)
from ansible.plugins.loader import lookup_loader


class MockJWT(MagicMock):
    def encode(self, payload, key, alg):
        return 'Foobar'


class MockResponse(MagicMock):
    response_token = 'Bar'

    def read(self):
        return json.dumps({
            "token": self.response_token,
        }).encode('utf-8')


class TestLookupModule(unittest.TestCase):

    def test_get_token(self):
        with patch.multiple("ansible_collections.community.general.plugins.lookup.github_app_access_token",
                            open=mock_open(read_data="foo_bar"),
                            open_url=MagicMock(return_value=MockResponse()),
                            jwk_from_pem=MagicMock(return_value='private_key'),
                            jwt_instance=MockJWT(),
                            HAS_JWT=True):
            lookup = lookup_loader.get('community.general.github_app_access_token')
            self.assertListEqual(
                [MockResponse.response_token],
                lookup.run(
                    [],
                    key_path="key",
                    app_id="app_id",
                    installation_id="installation_id",
                    token_expiry=600
                )
            )

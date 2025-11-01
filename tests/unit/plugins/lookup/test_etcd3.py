#
# Copyright (c) 2020, SCC France, Eric Belhomme <ebelhomme@fr.scc.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from ansible_collections.community.general.plugins.lookup import etcd3
from ansible.plugins.loader import lookup_loader


class FakeKVMetadata:
    def __init__(self, keyvalue, header):
        self.key = keyvalue
        self.create_revision = ""
        self.mod_revision = ""
        self.version = ""
        self.lease_id = ""
        self.response_header = header


class FakeEtcd3Client(MagicMock):
    def get_prefix(self, key):
        for i in range(1, 4):
            yield self.get(f"{key}_{i}")

    def get(self, key):
        return (f"{key} value", FakeKVMetadata(key, None))


class TestLookupModule(unittest.TestCase):
    def setUp(self):
        etcd3.HAS_ETCD = True
        self.lookup = lookup_loader.get("community.general.etcd3")

    @patch("ansible_collections.community.general.plugins.lookup.etcd3.etcd3_client", FakeEtcd3Client())
    def test_key(self):
        expected_result = [{"key": "a_key", "value": "a_key value"}]
        self.assertListEqual(expected_result, self.lookup.run(["a_key"], []))

    @patch("ansible_collections.community.general.plugins.lookup.etcd3.etcd3_client", FakeEtcd3Client())
    def test_key_prefix(self):
        expected_result = [
            {"key": "a_key_1", "value": "a_key_1 value"},
            {"key": "a_key_2", "value": "a_key_2 value"},
            {"key": "a_key_3", "value": "a_key_3 value"},
        ]
        self.assertListEqual(expected_result, self.lookup.run(["a_key"], [], **{"prefix": True}))

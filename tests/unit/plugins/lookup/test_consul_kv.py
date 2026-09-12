# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from ansible.plugins.loader import lookup_loader


def _entry(value, key="somekey"):
    return {"Key": key, "Value": None if value is None else _b64(value)}


def _b64(value):
    import base64

    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


def _response(entries):
    response = MagicMock()
    response.read.return_value = json.dumps(entries).encode("utf-8")
    return response


def _not_found():
    return HTTPError("http://localhost:8500/v1/kv/somekey", 404, "Not Found", {}, None)


class TestLookupModule(unittest.TestCase):
    def setUp(self):
        self.lookup = lookup_loader.get("community.general.consul_kv")

    def test_simple_lookup(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response([_entry("somevalue")]),
        ) as open_url:
            result = self.lookup.run(["somekey"])
        self.assertEqual(result, ["somevalue"])
        args, kwargs = open_url.call_args
        self.assertEqual(args[0], "http://localhost:8500/v1/kv/somekey")
        self.assertEqual(kwargs["headers"], {})

    def test_token_sets_header(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response([_entry("somevalue")]),
        ) as open_url:
            self.lookup.run(["somekey token=mytoken"])
        self.assertEqual(open_url.call_args.kwargs["headers"], {"X-Consul-Token": "mytoken"})

    def test_recurse_returns_multiple_values(self):
        entries = [_entry("v1", "prefix/a"), _entry("v2", "prefix/b")]
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response(entries),
        ) as open_url:
            result = self.lookup.run(["prefix recurse=true"])
        self.assertEqual(result, ["v1", "v2"])
        self.assertIn("recurse=true", open_url.call_args.args[0])

    def test_missing_key_returns_empty_list(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            side_effect=_not_found(),
        ):
            result = self.lookup.run(["somekey"])
        self.assertEqual(result, [])

    def test_null_value_default_empty_value(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response([_entry(None)]),
        ):
            result = self.lookup.run(["somekey"])
        self.assertEqual(result, ["None"])

    def test_null_value_python_none(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response([_entry(None)]),
        ):
            result = self.lookup.run(["somekey"], empty_value="python_none")
        self.assertEqual(result, [None])

    def test_url_option_overrides_host_port_scheme(self):
        with patch(
            "ansible_collections.community.general.plugins.lookup.consul_kv.open_url",
            return_value=_response([_entry("somevalue")]),
        ) as open_url:
            self.lookup.run(["somekey"], url="https://consul.example.com:9500")
        self.assertEqual(open_url.call_args.args[0], "https://consul.example.com:9500/v1/kv/somekey")

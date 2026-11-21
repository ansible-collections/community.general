# Copyright (c) 2026, Uman Shahzad (@UmanShahzad)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules.internetdata_info import InternetDataInfo

INTERNETDATA_DATA = {
    "ip": "8.8.8.8",
    "is_bogon": False,
    "is_tor": False,
    "is_relay": False,
    "is_anycast": True,
    "location": {"continent": "NA", "country": "US", "country_name": "United States"},
    "asn": {"asn": 15169, "name": "Google LLC", "domain": "google.com", "prefix": "8.8.8.0/24"},
    "company": {"name": "Google LLC", "domain": "google.com"},
    "hostname": "dns.google",
    "abuse": {"email": "network-abuse@google.com"},
}

FETCH_URL = "ansible_collections.community.general.plugins.modules.internetdata_info.fetch_url"


def mock_module(params):
    module = Mock()
    module.params = {"timeout": 10, "ip": None, "api_key": None, **params}
    module.from_json.side_effect = json.loads
    return module


def mock_response(status=200):
    response = Mock()
    response.read.return_value = json.dumps(INTERNETDATA_DATA)
    return response, {"status": status}


class TestInternetDataInfo(unittest.TestCase):
    def test_get_ip_data_with_ip(self):
        module = mock_module({"ip": "8.8.8.8"})
        with patch(FETCH_URL) as mock_fetch_url:
            mock_fetch_url.return_value = mock_response()
            result = InternetDataInfo(module).get_ip_data()

            self.assertEqual(result["location"]["country"], "US")
            self.assertEqual(result["asn"]["asn"], 15169)
            mock_fetch_url.assert_called_once_with(
                module, "https://api.internetdata.io/8.8.8.8", headers={"Accept": "application/json"}, timeout=10
            )

    def test_get_ip_data_of_own_address(self):
        module = mock_module({})
        with patch(FETCH_URL) as mock_fetch_url:
            mock_fetch_url.return_value = mock_response()
            InternetDataInfo(module).get_ip_data()

            mock_fetch_url.assert_called_once_with(
                module, "https://api.internetdata.io/myip", headers={"Accept": "application/json"}, timeout=10
            )

    def test_get_ip_data_with_api_key(self):
        module = mock_module({"ip": "8.8.8.8", "api_key": "secret"})
        with patch(FETCH_URL) as mock_fetch_url:
            mock_fetch_url.return_value = mock_response()
            InternetDataInfo(module).get_ip_data()

            headers = mock_fetch_url.call_args.kwargs["headers"]
            self.assertEqual(headers["Authorization"], "Bearer secret")

    def test_get_ip_data_fails_on_http_error(self):
        module = mock_module({"ip": "8.8.8.8"})
        module.fail_json.side_effect = SystemExit
        with patch(FETCH_URL) as mock_fetch_url:
            mock_fetch_url.return_value = mock_response(status=429)
            with self.assertRaises(SystemExit):
                InternetDataInfo(module).get_ip_data()
            self.assertIn("429", module.fail_json.call_args.kwargs["msg"])

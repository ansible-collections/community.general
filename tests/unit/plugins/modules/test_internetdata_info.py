# Copyright (c) 2026, Uman Shahzad (@UmanShahzad)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from ansible_collections.community.general.plugins.modules import internetdata_info
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


def make_module(**params):
    module = Mock()
    module.params = {"timeout": 10, "ip": None, "api_key": None, **params}
    module.from_json.side_effect = json.loads
    module.fail_json.side_effect = SystemExit
    return module


@pytest.fixture
def fetch_url(monkeypatch):
    response = Mock()
    response.read.return_value = json.dumps(INTERNETDATA_DATA)
    fetch = Mock(return_value=(response, {"status": 200}))
    monkeypatch.setattr(internetdata_info, "fetch_url", fetch)
    return fetch


def test_get_ip_data_with_ip(fetch_url):
    module = make_module(ip="8.8.8.8")
    result = InternetDataInfo(module).get_ip_data()

    assert result["location"]["country"] == "US"
    assert result["asn"]["asn"] == 15169
    fetch_url.assert_called_once_with(
        module, "https://api.internetdata.io/8.8.8.8", headers={"Accept": "application/json"}, timeout=10
    )


def test_get_ip_data_of_own_address(fetch_url):
    module = make_module()
    InternetDataInfo(module).get_ip_data()

    fetch_url.assert_called_once_with(
        module, "https://api.internetdata.io/myip", headers={"Accept": "application/json"}, timeout=10
    )


def test_get_ip_data_with_api_key(fetch_url):
    InternetDataInfo(make_module(ip="8.8.8.8", api_key="secret")).get_ip_data()

    assert fetch_url.call_args.kwargs["headers"]["Authorization"] == "Bearer secret"


def test_get_ip_data_fails_on_http_error(fetch_url):
    fetch_url.return_value = (None, {"status": 429})
    module = make_module(ip="8.8.8.8")

    with pytest.raises(SystemExit):
        InternetDataInfo(module).get_ip_data()
    assert "429" in module.fail_json.call_args.kwargs["msg"]

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

from ansible_collections.community.general.plugins.modules.ipbase_info import IpbaseInfo
import unittest
from unittest.mock import Mock


IPBASE_DATA = {
    "response": b"""
{
  "data": {
    "ip": "1.1.1.1",
    "hostname": "one.one.one.one",
    "type": "v4",
    "range_type": {
      "type": "PUBLIC",
      "description": "Public address"
    },
    "connection": {
      "asn": 13335,
      "organization": "Cloudflare, Inc.",
      "isp": "APNIC Research and Development",
      "range": "1.1.1.1/32"
    },
    "location": {
      "geonames_id": 5332870,
      "latitude": 34.053611755371094,
      "longitude": -118.24549865722656,
      "zip": "90012",
      "continent": {
        "code": "NA",
        "name": "North America",
        "name_translated": "North America"
      },
      "country": {
        "alpha2": "US",
        "alpha3": "USA",
        "calling_codes": [
          "+1"
        ],
        "currencies": [
          {
            "symbol": "$",
            "name": "US Dollar",
            "symbol_native": "$",
            "decimal_digits": 2,
            "rounding": 0,
            "code": "USD",
            "name_plural": "US dollars"
          }
        ],
        "emoji": "...",
        "ioc": "USA",
        "languages": [
          {
            "name": "English",
            "name_native": "English"
          }
        ],
        "name": "United States",
        "name_translated": "United States",
        "timezones": [
          "America/New_York",
          "America/Detroit",
          "America/Kentucky/Louisville",
          "America/Kentucky/Monticello",
          "America/Indiana/Indianapolis",
          "America/Indiana/Vincennes",
          "America/Indiana/Winamac",
          "America/Indiana/Marengo",
          "America/Indiana/Petersburg",
          "America/Indiana/Vevay",
          "America/Chicago",
          "America/Indiana/Tell_City",
          "America/Indiana/Knox",
          "America/Menominee",
          "America/North_Dakota/Center",
          "America/North_Dakota/New_Salem",
          "America/North_Dakota/Beulah",
          "America/Denver",
          "America/Boise",
          "America/Phoenix",
          "America/Los_Angeles",
          "America/Anchorage",
          "America/Juneau",
          "America/Sitka",
          "America/Metlakatla",
          "America/Yakutat",
          "America/Nome",
          "America/Adak",
          "Pacific/Honolulu"
        ],
        "is_in_european_union": false,
        "fips": "US",
        "geonames_id": 6252001,
        "hasc_id": "US",
        "wikidata_id": "Q30"
      },
      "city": {
        "fips": "644000",
        "alpha2": null,
        "geonames_id": 5368753,
        "hasc_id": null,
        "wikidata_id": "Q65",
        "name": "Los Angeles",
        "name_translated": "Los Angeles"
      },
      "region": {
        "fips": "US06",
        "alpha2": "US-CA",
        "geonames_id": 5332921,
        "hasc_id": "US.CA",
        "wikidata_id": "Q99",
        "name": "California",
        "name_translated": "California"
      }
    },
    "tlds": [
      ".us"
    ],
    "timezone": {
      "id": "America/Los_Angeles",
      "current_time": "2023-05-04T04:30:28-07:00",
      "code": "PDT",
      "is_daylight_saving": true,
      "gmt_offset": -25200
    },
    "security": {
      "is_anonymous": false,
      "is_datacenter": false,
      "is_vpn": false,
      "is_bot": false,
      "is_abuser": true,
      "is_known_attacker": true,
      "is_proxy": false,
      "is_spam": false,
      "is_tor": false,
      "is_icloud_relay": false,
      "threat_score": 100
    },
    "domains": {
      "count": 10943,
      "domains": [
        "eliwise.academy",
        "accountingprose.academy",
        "pistola.academy",
        "1and1-test-ntlds-fr.accountant",
        "omnergy.africa"
      ]
    }
  }
}
"""
}


class TestIpbase(unittest.TestCase):
    def test_info(
        self,
    ):
        "test the json data extraction"

        params = {
            "ip": "1.1.1.1",
            "apikey": "aaa",
            "hostname": True,
            "language": "de",
        }
        module = Mock()
        module.params = params

        data = json.loads(IPBASE_DATA["response"].decode("utf-8"))

        IpbaseInfo._get_url_data = Mock()
        IpbaseInfo._get_url_data.return_value = data
        jenkins_plugin = IpbaseInfo(module)

        json_data = jenkins_plugin.info()

        self.maxDiff = None
        self.assertDictEqual(json_data, data)

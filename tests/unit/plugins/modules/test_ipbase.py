# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.plugins.modules.ipbase_info import IpbaseInfo


def pass_function(*args, **kwargs):
    pass


IPBASE_DATA = {
    "result": b"""
{
  "data": {
    "as_name": "Cloudflare, Inc.",
    "as_number": 13335,
    "city": "Los Angeles",
    "continent": "North America",
    "continent_code": "NA",
    "country": "United States",
    "country_code": "US",
    "hostname": "one.one.one.one",
    "ip": "1.1.1.1",
    "is_in_european_union": false,
    "latitude": 34.053611755371094,
    "longitude": -118.24549865722656,
    "region": "California",
    "region_code": "US-CA",
    "timezone": "America/Los_Angeles",
    "zip": "90012"
  }
}
""",
    "response": b"""
{
  "data": {
    "ip": "1.1.1.1",
    "hostname": null,
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


def test_info(mocker):
    "test the json data extraction"

    params = {
        "ip": "1.1.1.1",
        "apikey": "aaa"
    }
    module = mocker.Mock()
    module.params = params

    IpbaseInfo._get_url_data = mocker.Mock()
    IpbaseInfo._get_url_data.return_value = str(IPBASE_DATA['response'])
    jenkins_plugin = IpbaseInfo(module)

    json_data = jenkins_plugin.info()

    result = json.load(IPBASE_DATA['result'])

    assert json_data == result

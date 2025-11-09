#!/usr/bin/python
#
# Copyright (c) 2023, Dominik Kukacka <dominik.kukacka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: "ipbase_info"
version_added: "7.0.0"
short_description: "Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API"
description:
  - Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API.
author: "Dominik Kukacka (@dominikkukacka)"
extends_documentation_fragment:
  - "community.general.attributes"
  - "community.general.attributes.info_module"
options:
  ip:
    description:
      - The IP you want to get the info for. If not specified the API detects the IP automatically.
    type: str
  apikey:
    description:
      - The API key for the request if you need more requests.
    type: str
  hostname:
    description:
      - If the O(hostname) parameter is set to V(true), the API response contains the hostname of the IP.
    type: bool
    default: false
  language:
    description:
      - An ISO Alpha 2 Language Code for localizing the IP data.
    type: str
    default: "en"
notes:
  - Check U(https://ipbase.com/) for more information.
"""

EXAMPLES = r"""
- name: "Get IP geolocation information of the primary outgoing IP"
  community.general.ipbase_info:
  register: my_ip_info

- name: "Get IP geolocation information of a specific IP"
  community.general.ipbase_info:
    ip: "8.8.8.8"
  register: my_ip_info


- name: "Get IP geolocation information of a specific IP with all other possible parameters"
  community.general.ipbase_info:
    ip: "8.8.8.8"
    apikey: "xxxxxxxxxxxxxxxxxxxxxx"
    hostname: true
    language: "de"
  register: my_ip_info
"""

RETURN = r"""
data:
  description: "JSON parsed response from ipbase.com. Please refer to U(https://ipbase.com/docs/info) for the detailed structure
    of the response."
  returned: success
  type: dict
  sample:
    {
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
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from urllib.parse import urlencode


USER_AGENT = "ansible-community.general.ipbase_info/0.1.0"
BASE_URL = "https://api.ipbase.com/v2/info"


class IpbaseInfo:
    def __init__(self, module):
        self.module = module

    def _get_url_data(self, url):
        response, info = fetch_url(
            self.module,
            url,
            force=True,
            timeout=10,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )

        if info["status"] != 200:
            self.module.fail_json(msg=f"The API request to ipbase.com returned an error status code {info['status']}")
        else:
            try:
                content = response.read()
                result = self.module.from_json(content.decode("utf8"))
            except ValueError:
                self.module.fail_json(msg=f"Failed to parse the ipbase.com response: {url} {content}")
            else:
                return result

    def info(self):
        ip = self.module.params["ip"]
        apikey = self.module.params["apikey"]
        hostname = self.module.params["hostname"]
        language = self.module.params["language"]

        url = BASE_URL

        params = {}
        if ip:
            params["ip"] = ip

        if apikey:
            params["apikey"] = apikey

        if hostname:
            params["hostname"] = 1

        if language:
            params["language"] = language

        if params:
            url += f"?{urlencode(params)}"

        return self._get_url_data(url)


def main():
    module_args = dict(
        ip=dict(type="str", no_log=False),
        apikey=dict(type="str", no_log=True),
        hostname=dict(type="bool", no_log=False, default=False),
        language=dict(type="str", no_log=False, default="en"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    ipbase = IpbaseInfo(module)
    module.exit_json(**ipbase.info())


if __name__ == "__main__":
    main()

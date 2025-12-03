#!/usr/bin/python

# Copyright (c) 2025, IP2Location <support@ip2location.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: ip2location_info
short_description: Retrieve IP geolocation information of a host's IP address
version_added: 12.2.0
description:
  - Gather IP geolocation information of a host's IP address using the keyless U(api.ip2location.io) API.
author: "IP2Location (@ip2location)"
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  ip:
    description:
      - IP address to retrieve geolocation information.
    type: str
  timeout:
    description:
      - HTTP connection timeout in seconds.
    default: 10
    type: int
  http_agent:
    description:
      - Set HTTP user agent.
    default: "ansible-ip2location-info-module/0.0.1"
    type: str
notes:
  - This module uses the keyless endpoint which has usage limits.
    Check U(https://www.ip2location.io/ip2location-documentation) for more information.
"""

EXAMPLES = r"""
# Retrieve geolocation data of a host's IP address
- name: Get IP geolocation data
  community.general.ip2location_info:
  register: result

- name: Show some information
  ansible.builtin.debug:
    msg: "{{ result.ip }} is located in {{ result.country_code }} ({{ result.country_name }})"
"""

RETURN = r"""
record:
  description: Dictionary of IP geolocation information for the IP address.
  returned: changed
  type: complex
  contains:
    ip:
      description: "Public IP address of a host."
      type: str
      sample: "8.8.8.8"
    country_code:
      description: ISO 3166-1 alpha-2 country code.
      type: str
      sample: "US"
    country_name:
      description: Country name based on ISO 3166.
      type: str
      sample: "United States of America"
    region_name:
      description: State or province name.
      type: str
      sample: "California"
    city_name:
      description: City name.
      type: str
      sample: "Mountain View"
    latitude:
      description: Latitude of the city.
      type: float
      sample: 37.3860
    longitude:
      description: Longitude of the city.
      type: float
      sample: -122.0838
    zip_code:
      description: ZIP/Postal code.
      type: str
      sample: "94035"
    time_zone:
      description: UTC time zone (with DST supported).
      type: str
      sample: "-08:00"
    asn:
      description: Autonomous system number (ASN).
      type: str
      sample: "15169"
    as:
      description: Autonomous system (AS) name.
      type: str
      sample: "Google LLC"
    is_proxy:
      description: Whether is a proxy or not.
      type: bool
      sample: false
"""

import typing as t

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

USER_AGENT = "ansible-ip2location-info-module/0.0.1"


class Ip2LocationInfo:
    def __init__(self, module: AnsibleModule) -> None:
        self.url = "https://api.ip2location.io/"
        self.timeout = module.params.get("timeout")
        self.ip = module.params.get("ip")
        self.module = module

    def get_geo_data(self) -> dict[str, t.Any]:
        url = self.url
        if self.ip:
            url += f"?ip={self.ip}"

        response, info = fetch_url(
            self.module,
            url,
            timeout=self.timeout,
        )
        if info["status"] != 200:
            self.module.fail_json(
                msg=f"Could not get {url} page, check for connectivity! HTTP Status: {info['status']}"
            )

        try:
            content = response.read()
            result = self.module.from_json(content)
        except Exception as exc:
            self.module.fail_json(
                msg=f"Failed to parse the ip2location.io response from {url}: {exc}", read_content=content
            )
        else:
            return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            http_agent=dict(default=USER_AGENT),
            timeout=dict(type="int", default=10),
            ip=dict(type="str"),
        ),
        supports_check_mode=True,
    )

    ip2location_info = Ip2LocationInfo(module)
    ip2location_info_result = {"changed": False}
    ip2location_info_result.update(ip2location_info.get_geo_data())
    module.exit_json(**ip2location_info_result)


if __name__ == "__main__":
    main()

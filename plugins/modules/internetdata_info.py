#!/usr/bin/python

# Copyright (c) 2026, Uman Shahzad (@UmanShahzad)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: internetdata_info
short_description: Retrieve location, ASN and company information of an IP address from InternetData
version_added: 14.1.0
description:
  - Gather the country, autonomous system, company, hostname and network flags of an IP address
    using the U(https://api.internetdata.io) API.
  - Without O(ip), the address looked up is the public IP address of the host running the module.
author: "Uman Shahzad (@UmanShahzad)"
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  ip:
    description:
      - IP address to look up. Defaults to the public IP address of the host running the module.
    type: str
  api_key:
    description:
      - InternetData API key, sent as a Bearer token.
      - Not needed for the fields this module documents; a key on a paid plan adds city, region and coordinates.
    type: str
  timeout:
    description:
      - HTTP connection timeout in seconds.
    default: 10
    type: int
  http_agent:
    description:
      - Set HTTP user agent.
    default: "ansible-internetdata-info-module/0.0.1"
    type: str
notes:
  - Lookups without O(api_key) need no account.
    See U(https://internetdata.io/terms#no-key) and U(https://docs.internetdata.io/api) for more information.
"""

EXAMPLES = r"""
- name: Get information about the host's public IP address
  community.general.internetdata_info:
  register: result

- name: Get information about another IP address
  community.general.internetdata_info:
    ip: 8.8.8.8
  register: result

- name: Show some information
  ansible.builtin.debug:
    msg: "{{ result.ip }} is in {{ result.location.country_name }}, announced by AS{{ result.asn.asn }} ({{ result.asn.name }})"
"""

RETURN = r"""
ip:
  description: The IP address looked up.
  type: str
  returned: success
  sample: "8.8.8.8"
location:
  description: Where the address is.
  type: dict
  returned: success
  sample:
    continent: "NA"
    continent_name: "North America"
    country: "US"
    country_name: "United States"
    timezone: "America/Los_Angeles"
    currency_code: "USD"
asn:
  description: The autonomous system announcing the address.
  type: dict
  returned: when the address is announced
  sample:
    asn: 15169
    name: "Google LLC"
    domain: "google.com"
    type: "hosting"
    prefix: "8.8.8.0/24"
    country: "US"
    rpki_status: "valid"
company:
  description: The company using the address.
  type: dict
  returned: when known
  sample:
    name: "Google LLC"
    domain: "google.com"
hostname:
  description: The reverse DNS name of the address.
  type: str
  returned: when the address has one
  sample: "dns.google"
abuse:
  description: Where to report abuse from the address.
  type: dict
  returned: when known
  sample:
    email: "network-abuse@google.com"
is_tor:
  description: Whether the address is a Tor exit node.
  type: bool
  returned: success
  sample: false
is_relay:
  description: Whether the address is a privacy relay egress, such as iCloud Private Relay.
  type: bool
  returned: success
  sample: false
is_anycast:
  description: Whether the address is anycast.
  type: bool
  returned: success
  sample: true
is_bogon:
  description: Whether the address is private, reserved or otherwise not routable on the internet.
  type: bool
  returned: success
  sample: false
"""

import typing as t

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

USER_AGENT = "ansible-community.general.internetdata_info"


class InternetDataInfo:
    def __init__(self, module: AnsibleModule) -> None:
        self.url = "https://api.internetdata.io/"
        self.timeout = module.params["timeout"]
        self.ip = module.params["ip"]
        self.api_key = module.params["api_key"]
        self.module = module

    def get_ip_data(self) -> dict[str, t.Any]:
        url = self.url + (self.ip if self.ip else "myip")
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response, info = fetch_url(
            self.module,
            url,
            headers=headers,
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
                msg=f"Failed to parse the InternetData response from {url}: {exc}", read_content=content
            )
        else:
            return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            http_agent=dict(default=USER_AGENT),
            timeout=dict(type="int", default=10),
            ip=dict(type="str"),
            api_key=dict(type="str", no_log=True),
        ),
        supports_check_mode=True,
    )

    internetdata_info = InternetDataInfo(module)
    module.exit_json(**internetdata_info.get_ip_data())


if __name__ == "__main__":
    main()

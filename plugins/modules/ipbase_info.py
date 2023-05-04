#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Dominik Kukacka <dominik.kukacka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ipbase_info
version_added: 7.0.0
short_description: Retrieve IP geolocation and other facts of a host's IP address
description:
  - "Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API"
author: "Dominik Kukacka (@dominikkukacka)"
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  ip:
    description:
      - "The IP you want to get the info for."
    required: false
    default: "The primary outgoing IP address of the host."
    type: str
  apikey:
    description:
      - "The api key for the request if you need more requests."
    required: false
    type: str
notes:
  - "Check U(https://ipbase.com/) for more information."
'''

EXAMPLES = '''
- name: "Get IP geolocation information of the primary outgoing IP"
  community.general.ipbase_info:
  register: my_ip_info

- name: "Get IP geolocation information of a specific IP
  community.general.ipbase_info:
    ip: "8.8.8.8"
  register: my_ip_info
'''

RETURN = '''
---
data:
  ip:
    description: "Public IP address of the host."
    type: str
    sample: "1.1.1.1"
  hostname:
    description: "The hostname of the IP address."
    type: str
    sample: "one.one.one.one"
  continent_code:
    description: The ISO 3166-1 alpha-2 continent code."
    type: str
    sample: "NA"
  continent_name:
    description: "The continent name."
    type: str
    sample: "North America"
  country_code:
    description: "The ISO 3166-1 alpha-2 country code."
    type: str
    sample: "US"
  country_name:
    description: "The country name."
    type: str
    sample: "United States"
  is_in_european_union:
    description: "Is the country in the European Union?"
    type: bool
    sample: true
  region_code:
    description: "The ISO 3166-2 alpha-2 region code."
    type: str
    sample: "US-CA"
  region_name:
    description: "The state or province name."
    type: str
    sample: "California"
  city_name:
    description: "The city name."
    type: str
    sample: "Los Angeles"
  latitude:
    description: "The latitude of the location."
    type: float
    sample: 34.053611755371094
  longitude:
    description: "The longitude of the location."
    type: float
    sample: -118.24549865722656
  as_name:
    description: "The autonomous system name (AS name)"
    type: str
    sample: "Cloudflare, Inc."
  as_number:
    description: "The autonomous system number (ASN)"
    type: int
    sample: 13335
  zip:
    description: "The zip code."
    type: str
    sample: "90012"
  timezone:
    description: "The timezone ID."
    type: str
    sample: "America/Los_Angeles"
'''
from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.urls import fetch_url


USER_AGENT = 'ansible-ipbase-module/0.1.0'
BASE_URL = 'https://api.ipbase.com/v2/info?hostname=1'


class IpbaseFacts(object):

    def __init__(self, module):
        self.module = module

    def info(self, ip, apikey):
        url = BASE_URL
        if ip:
            url += '&ip=' + str(ip)

        if apikey:
            url += '&apikey=' + str(apikey)

        response, info = fetch_url(
            self.module,
            url,
            force=True,
            timeout=10,
            headers={
                'Accept': 'application/json',
                'User-Agent': USER_AGENT,
            })

        if (info['status'] != 200):
            self.module.fail_json(msg='The API request to ipbase.com returned an error status code {0}'.format(info['status']))
        else:
            try:
                content = response.read()
                parsedData = self.module.from_json(content.decode('utf8'))

                result = dict(
                    ip=parsedData['data']['ip'],
                    hostname=parsedData['data']['hostname'],
                    continent=parsedData['data']['location']['continent']['name'],
                    continent_code=parsedData['data']['location']['continent']['code'],
                    country=parsedData['data']['location']['country']['name'],
                    country_code=parsedData['data']['location']['country']['alpha2'],
                    is_in_european_union=parsedData['data']['location']['country']['is_in_european_union'],
                    region=parsedData['data']['location']['region']['name'],
                    region_code=parsedData['data']['location']['region']['alpha2'],
                    city=parsedData['data']['location']['city']['name'],
                    zip=parsedData['data']['location']['zip'],
                    latitude=parsedData['data']['location']['latitude'],
                    longitude=parsedData['data']['location']['longitude'],
                    timezone=parsedData['data']['timezone']['id'],
                    as_name=parsedData['data']['connection']['organization'],
                    as_number=parsedData['data']['connection']['asn'],
                )

            except ValueError:
                self.module.fail_json(
                    msg='Failed to parse the ipbase.com response: '
                    '{0} {1}'.format(url, content))
            else:
                return dict(data=result)


def main():
    module_args = dict(
        ip=dict(type='str', required=False, no_log=False),
        apikey=dict(type='str', required=False, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    ip = module.params['ip']
    apikey = module.params['apikey']

    ipbase = IpbaseFacts(module)
    module.exit_json(**ipbase.info(ip, apikey))


if __name__ == '__main__':
    main()

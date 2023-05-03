#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Dominik Kukacka <dominik.kukacka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type


DOCUMENTATION = '''
---
module: ipbase_facts
short_description: Retrieve IP geolocation and other facts of a host's IP address
description:
  - "Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API"
author: "Dominik Kukacka (@dominikkukacka)"
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.facts
  - community.general.attributes.facts_module
options:
  http_agent:
    description:
      - Set http user agent
    required: false
    default: "ansible-ipbase-module/0.0.1"
    type: str
notes:
  - "Check http://ipbase.com/ for more information"
'''

EXAMPLES = '''
# Retrieve IP geolocation and other facts of a host's IP address
- name: Get IP geolocation information
  community.general.ipbase_facts:
'''

RETURN = '''
ansible_facts:
  description: "Dictionary of ip facts for a host's IP address"
  returned: changed
  type: complex
  contains:
    ip:
      description: "Public IP address of the host"
      type: str
      sample: "1.1.1.1"
    hostname:
      description: The hostname of the IP address
      type: str
      sample: "one.one.one.one"
    continent_code:
      description: ISO 3166-1 alpha-2 continent code
      type: str
      sample: "NA"
    continent_name:
      description: The continent name
      type: str
      sample: "North America"
    country_code:
      description: ISO 3166-1 alpha-2 country code
      type: str
      sample: "US"
    country_name:
      description: The country name
      type: str
      sample: "United States"
    is_in_european_union:
      description: Is the country in the European Union?
      type: bool
      sample: true
    region_code:
      description: ISO 3166-2 alpha-2 region code
      type: str
      sample: "US-CA"
    region_name:
      description: State or province name
      type: str
      sample: "California"
    city_name:
      description: City name
      type: str
      sample: "Los Angeles"
    latitude:
      description: Latitude of the location
      type: float
      sample: 34.053611755371094
    longitude:
      description: Longitude of the location
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
      description: Zip code
      type: str
      sample: "90012"
    timezone:
      description: "Timezone ID"
      type: str
      sample: "America/Los_Angeles"
'''


USER_AGENT = 'ansible-ipbase-module/0.0.1'
BASE_URL = 'https://api.ipbase.com/v2/info?hostname=1'


class IpbaseFacts(object):

    def __init__(self, module):
        self.module = module

    def info(self):
        response, info = fetch_url(
            self.module, BASE_URL, force=True, timeout=10)

        try:
            info['status'] == 200
        except AssertionError:
            self.module.fail_json(msg='Could not get {0} page, '
                                  'check for connectivity!'.format(BASE_URL))
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
                    '{0} {1}'.format(BASE_URL, content))
            else:
                return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            http_agent=dict(default=USER_AGENT),
            timeout=dict(type='int', default=10),
        ),
        supports_check_mode=True,
    )

    ipbase = IpbaseFacts(module)
    ipbase_result = dict(
        changed=False,
        ansible_facts=ipbase.info()
    )
    module.exit_json(**ipbase_result)


if __name__ == '__main__':
    main()

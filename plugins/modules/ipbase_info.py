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
    type: str
  apikey:
    description:
      - "The apikey for the request if you need more requests."
    required: false
    type: str
notes:
  - "Check U(https://ipbase.com/) for more information."
'''

EXAMPLES = '''
- name: "Get IP geolocation information of the primary outgoing IP"
  community.general.ipbase_info:
  register: my_ip_info

- name: "Get IP geolocation information of a specific IP"
  community.general.ipbase_info:
    ip: "8.8.8.8"
  register: my_ip_info
'''

RETURN = '''
data:
    description: "The data retrieved from ipbase.com."
    returned: success
    type: dict
    sample: {
        "as_name": "T-Mobile Austria GmbH",
        "as_number": 8412,
        "city": "Vienna",
        "continent": "Europe",
        "continent_code": "EU",
        "country": "Austria",
        "country_code": "AT",
        "hostname": "81-223-100.100.static.upcbusiness.at",
        "ip": "81.223.100.100",
        "is_in_european_union": true,
        "latitude": 48.1861686706543,
        "longitude": 16.403240203857422,
        "region": "Vienna",
        "region_code": "AT-9",
        "timezone": "Europe/Vienna",
        "zip": "1030"
    }
'''

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.urls import fetch_url


USER_AGENT = 'ansible-ipbase-module/0.1.0'
BASE_URL = 'https://api.ipbase.com/v2/info?hostname=1'


class IpbaseFacts(object):

    def __init__(self, module):
        self.module = module

    def _get_url_data(self, url):
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
                result = self.module.from_json(content.decode('utf8'))
            except ValueError:
                self.module.fail_json(
                    msg='Failed to parse the ipbase.com response: '
                    '{0} {1}'.format(url, content))
            else:
                return result

    def info(self, ip, apikey):
        url = BASE_URL
        if ip:
            url += '&ip=' + str(ip)

        if apikey:
            url += '&apikey=' + str(apikey)

        response = self._get_url_data(url)

        result = dict(
            ip=response['data']['ip'],
            hostname=response['data']['hostname'],
            continent=response['data']['location']['continent']['name'],
            continent_code=response['data']['location']['continent']['code'],
            country=response['data']['location']['country']['name'],
            country_code=response['data']['location']['country']['alpha2'],
            is_in_european_union=response['data']['location']['country']['is_in_european_union'],
            region=response['data']['location']['region']['name'],
            region_code=response['data']['location']['region']['alpha2'],
            city=response['data']['location']['city']['name'],
            zip=response['data']['location']['zip'],
            latitude=response['data']['location']['latitude'],
            longitude=response['data']['location']['longitude'],
            timezone=response['data']['timezone']['id'],
            as_name=response['data']['connection']['organization'],
            as_number=response['data']['connection']['asn'],
        )

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

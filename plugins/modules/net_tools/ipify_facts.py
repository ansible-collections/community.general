#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2015, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: ipify_facts
short_description: Retrieve the public IP of your internet gateway
description:
  - If behind NAT and need to know the public IP of your internet gateway.
author:
- René Moser (@resmo)
options:
  api_url:
    description:
      - URL of the ipify.org API service.
      - C(?format=json) will be appended per default.
    type: str
    default: https://api.ipify.org/
  timeout:
    description:
      - HTTP connection timeout in seconds.
    type: int
    default: 10
  validate_certs:
    description:
      - When set to C(NO), SSL certificates will not be validated.
    type: bool
    default: yes
notes:
  - Visit https://www.ipify.org to get more information.
'''

EXAMPLES = r'''
# Gather IP facts from ipify.org
- name: Get my public IP
  community.general.ipify_facts:

# Gather IP facts from your own ipify service endpoint with a custom timeout
- name: Get my public IP
  community.general.ipify_facts:
    api_url: http://api.example.com/ipify
    timeout: 20
'''

RETURN = r'''
---
ipify_public_ip:
  description: Public IP of the internet gateway.
  returned: success
  type: str
  sample: 1.2.3.4
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.common.text.converters import to_text


class IpifyFacts(object):

    def __init__(self):
        self.api_url = module.params.get('api_url')
        self.timeout = module.params.get('timeout')

    def run(self):
        result = {
            'ipify_public_ip': None
        }
        (response, info) = fetch_url(module=module, url=self.api_url + "?format=json", force=True, timeout=self.timeout)

        if not response:
            module.fail_json(msg="No valid or no response from url %s within %s seconds (timeout)" % (self.api_url, self.timeout))

        data = json.loads(to_text(response.read()))
        result['ipify_public_ip'] = data.get('ip')
        return result


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            api_url=dict(type='str', default='https://api.ipify.org/'),
            timeout=dict(type='int', default=10),
            validate_certs=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    ipify_facts = IpifyFacts().run()
    ipify_facts_result = dict(changed=False, ansible_facts=ipify_facts)
    module.exit_json(**ipify_facts_result)


if __name__ == '__main__':
    main()

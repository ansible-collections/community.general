#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: vultr_account_info
short_description: Get information about the Vultr account.
description:
  - Get infos about account balance, charges and payments.
author: "René Moser (@resmo)"
extends_documentation_fragment:
- community.general.vultr

'''

EXAMPLES = r'''
- name: Get Vultr account infos
  vultr_account_info:
  register: result

- name: Print the infos
  debug:
    var: result.vultr_account_info
'''

RETURN = r'''
---
vultr_api:
  description: Response from Vultr API with a few additions/modification
  returned: success
  type: complex
  contains:
    api_account:
      description: Account used in the ini file to select the key
      returned: success
      type: str
      sample: default
    api_timeout:
      description: Timeout used for the API requests
      returned: success
      type: int
      sample: 60
    api_retries:
      description: Amount of max retries for the API requests
      returned: success
      type: int
      sample: 5
    api_retry_max_delay:
      description: Exponential backoff delay in seconds between retries up to this max delay value.
      returned: success
      type: int
      sample: 12
      version_added: '2.9'
    api_endpoint:
      description: Endpoint used for the API requests
      returned: success
      type: str
      sample: "https://api.vultr.com"
vultr_account_info:
  description: Response from Vultr API
  returned: success
  type: complex
  contains:
    balance:
      description: Your account balance.
      returned: success
      type: float
      sample: -214.69
    pending_charges:
      description: Charges pending.
      returned: success
      type: float
      sample: 57.03
    last_payment_date:
      description: Date of the last payment.
      returned: success
      type: str
      sample: "2017-08-26 12:47:48"
    last_payment_amount:
      description: The amount of the last payment transaction.
      returned: success
      type: float
      sample: -250.0
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.vultr import (
    Vultr,
    vultr_argument_spec,
)


class AnsibleVultrAccountInfo(Vultr):

    def __init__(self, module):
        super(AnsibleVultrAccountInfo, self).__init__(module, "vultr_account_info")

        self.returns = {
            'balance': dict(convert_to='float'),
            'pending_charges': dict(convert_to='float'),
            'last_payment_date': dict(),
            'last_payment_amount': dict(convert_to='float'),
        }

    def get_account_info(self):
        return self.api_query(path="/v1/account/info")


def main():
    argument_spec = vultr_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    account_info = AnsibleVultrAccountInfo(module)
    result = account_info.get_result(account_info.get_account_info())
    module.exit_json(**result)


if __name__ == '__main__':
    main()

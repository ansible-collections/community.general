#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2018, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: digital_ocean_account_info
short_description: Gather information about DigitalOcean User account
description:
    - This module can be used to gather information about User account.
    - This module was called C(digital_ocean_account_facts) before Ansible 2.9. The usage did not change.
author: "Abhijeet Kasurde (@Akasurde)"

requirements:
  - "python >= 2.6"

extends_documentation_fragment:
- community.general.digital_ocean.documentation

'''


EXAMPLES = '''
- name: Gather information about user account
  digital_ocean_account_info:
    oauth_token: "{{ oauth_token }}"
'''


RETURN = '''
data:
    description: DigitalOcean account information
    returned: success
    type: dict
    sample: {
        "droplet_limit": 10,
        "email": "testuser1@gmail.com",
        "email_verified": true,
        "floating_ip_limit": 3,
        "status": "active",
        "status_message": "",
        "uuid": "aaaaaaaaaaaaaa"
    }
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    rest = DigitalOceanHelper(module)

    response = rest.get("account")
    if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'account' information due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=response.json["account"])


def main():
    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec)
    if module._name in ('digital_ocean_account_facts', 'community.general.digital_ocean_account_facts'):
        module.deprecate("The 'digital_ocean_account_facts' module has been renamed to 'digital_ocean_account_info'", version='2.13')
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()

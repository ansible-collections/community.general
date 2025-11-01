#!/usr/bin/python
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: online_user_info
short_description: Gather information about Online user
description:
  - Gather information about the user.
author:
  - "Remy Leone (@remyleone)"
extends_documentation_fragment:
  - community.general.online
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: Gather Online user info
  community.general.online_user_info:
  register: result

- ansible.builtin.debug:
    msg: "{{ result.online_user_info }}"
"""

RETURN = r"""
online_user_info:
  description:
    - Response from Online API.
    - 'For more details please refer to: U(https://console.online.net/en/api/).'
  returned: success
  type: dict
  sample:
    {
      "company": "foobar LLC",
      "email": "foobar@example.com",
      "first_name": "foo",
      "id": 42,
      "last_name": "bar",
      "login": "foobar"
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.online import (
    Online,
    OnlineException,
    online_argument_spec,
)


class OnlineUserInfo(Online):
    def __init__(self, module):
        super().__init__(module)
        self.name = "api/v1/user"


def main():
    module = AnsibleModule(
        argument_spec=online_argument_spec(),
        supports_check_mode=True,
    )

    try:
        module.exit_json(online_user_info=OnlineUserInfo(module).get_resources())
    except OnlineException as exc:
        module.fail_json(msg=exc.message)


if __name__ == "__main__":
    main()

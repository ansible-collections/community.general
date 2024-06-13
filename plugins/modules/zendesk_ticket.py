#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Luis Valle (levalle232@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

REQUESTS_IMP_ERR = None
try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAVE_REQUESTS = False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True, aliases=['user']),
            password=dict(type='str', required=True, aliases=['password']),
            state=dict(type='str',required=True, default='present',
                       choices=['present', 'absent', 'update'], default='present'),
            body=dict(type='str', required=False, default='')
            severity=dict(type='str', required=False, default="Normal")
        ),
        supports_check_mode=False
    )
    if not HAVE_REQUESTS:
        module.fail_json(msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR)


if __name__ == '__main__':
    main()

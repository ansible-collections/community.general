#!/usr/bin/python
# coding: utf-8

# Copyright (c) 2018, Jan Christian Grünhage <jan.christian@gruenhage.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
author: "Jan Christian Grünhage (@jcgruenhage)"
module: matrix
short_description: Send notifications to matrix
description:
  - This module sends HTML formatted notifications to matrix rooms.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  msg_plain:
    type: str
    description:
      - Plain text form of the message to send to matrix, usually markdown.
    required: true
  msg_html:
    type: str
    description:
      - HTML form of the message to send to matrix.
    required: true
  room_id:
    type: str
    description:
      - ID of the room to send the notification to.
    required: true
  hs_url:
    type: str
    description:
      - URL of the homeserver, where the CS-API is reachable.
    required: true
  token:
    type: str
    description:
      - Authentication token for the API call. If provided, O(user_id) and O(password) are not required.
  user_id:
    type: str
    description:
      - The user ID of the user.
  password:
    type: str
    description:
      - The password to log in with.
requirements:
  - matrix-client (Python library)
"""

EXAMPLES = r"""
- name: Send matrix notification with token
  community.general.matrix:
    msg_plain: "**hello world**"
    msg_html: "<b>hello world</b>"
    room_id: "!12345678:server.tld"
    hs_url: "https://matrix.org"
    token: "{{ matrix_auth_token }}"

- name: Send matrix notification with user_id and password
  community.general.matrix:
    msg_plain: "**hello world**"
    msg_html: "<b>hello world</b>"
    room_id: "!12345678:server.tld"
    hs_url: "https://matrix.org"
    user_id: "ansible_notification_bot"
    password: "{{ matrix_auth_password }}"
"""

RETURN = r"""
"""
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

MATRIX_IMP_ERR = None
try:
    from matrix_client.client import MatrixClient
except ImportError:
    MATRIX_IMP_ERR = traceback.format_exc()
    matrix_found = False
else:
    matrix_found = True


def run_module():
    module_args = dict(
        msg_plain=dict(type='str', required=True),
        msg_html=dict(type='str', required=True),
        room_id=dict(type='str', required=True),
        hs_url=dict(type='str', required=True),
        token=dict(type='str', no_log=True),
        user_id=dict(type='str'),
        password=dict(type='str', no_log=True),
    )

    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[['password', 'token']],
        required_one_of=[['password', 'token']],
        required_together=[['user_id', 'password']],
        supports_check_mode=True
    )

    if not matrix_found:
        module.fail_json(msg=missing_required_lib('matrix-client'), exception=MATRIX_IMP_ERR)

    if module.check_mode:
        return result

    # create a client object
    client = MatrixClient(module.params['hs_url'])
    if module.params['token'] is not None:
        client.api.token = module.params['token']
    else:
        client.login(module.params['user_id'], module.params['password'], sync=False)

    # make sure we are in a given room and return a room object for it
    room = client.join_room(module.params['room_id'])
    # send an html formatted messages
    room.send_html(module.params['msg_html'], module.params['msg_plain'])

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

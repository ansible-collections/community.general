#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2012, Jim Richardson <weaselkeeper@gmail.com>
# Copyright (c) 2019, Bernd Arnold <wopfel@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pushover
short_description: Send notifications via U(https://pushover.net)
description:
   - Send notifications via pushover, to subscriber list of devices, and email
     addresses. Requires pushover app on devices.
notes:
   - You will require a pushover.net account to use this module. But no account
     is required to receive messages.
options:
  msg:
    type: str
    description:
      - What message you wish to send.
    required: true
  app_token:
    type: str
    description:
      - Pushover issued token identifying your pushover app.
    required: true
  user_key:
    type: str
    description:
      - Pushover issued authentication key for your user.
    required: true
  title:
    type: str
    description:
      - Message title.
    required: false
  pri:
    type: str
    description:
      - Message priority (see U(https://pushover.net) for details).
    required: false
    default: '0'
    choices: [ '-2', '-1', '0', '1', '2' ]
  device:
    type: str
    description:
      - A device the message should be sent to. Multiple devices can be specified, separated by a comma.
    required: false
    version_added: 1.2.0

author:
  - "Jim Richardson (@weaselkeeper)"
  - "Bernd Arnold (@wopfel)"
'''

EXAMPLES = '''
- name: Send notifications via pushover.net
  community.general.pushover:
    msg: '{{ inventory_hostname }} is acting strange ...'
    app_token: wxfdksl
    user_key: baa5fe97f2c5ab3ca8f0bb59
  delegate_to: localhost

- name: Send notifications via pushover.net
  community.general.pushover:
    title: 'Alert!'
    msg: '{{ inventory_hostname }} has exploded in flames, It is now time to panic'
    pri: 1
    app_token: wxfdksl
    user_key: baa5fe97f2c5ab3ca8f0bb59
  delegate_to: localhost

- name: Send notifications via pushover.net to a specific device
  community.general.pushover:
    msg: '{{ inventory_hostname }} has been lost somewhere'
    app_token: wxfdksl
    user_key: baa5fe97f2c5ab3ca8f0bb59
    device: admins-iPhone
  delegate_to: localhost
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import fetch_url


class Pushover(object):
    ''' Instantiates a pushover object, use it to send notifications '''
    base_uri = 'https://api.pushover.net'

    def __init__(self, module, user, token):
        self.module = module
        self.user = user
        self.token = token

    def run(self, priority, msg, title, device):
        ''' Do, whatever it is, we do. '''

        url = '%s/1/messages.json' % (self.base_uri)

        # parse config
        options = dict(user=self.user,
                       token=self.token,
                       priority=priority,
                       message=msg)

        if title is not None:
            options = dict(options,
                           title=title)

        if device is not None:
            options = dict(options,
                           device=device)

        data = urlencode(options)

        headers = {"Content-type": "application/x-www-form-urlencoded"}
        r, info = fetch_url(self.module, url, method='POST', data=data, headers=headers)
        if info['status'] != 200:
            raise Exception(info)

        return r.read()


def main():

    module = AnsibleModule(
        argument_spec=dict(
            title=dict(type='str'),
            msg=dict(required=True),
            app_token=dict(required=True, no_log=True),
            user_key=dict(required=True, no_log=True),
            pri=dict(required=False, default='0', choices=['-2', '-1', '0', '1', '2']),
            device=dict(type='str'),
        ),
    )

    msg_object = Pushover(module, module.params['user_key'], module.params['app_token'])
    try:
        response = msg_object.run(module.params['pri'], module.params['msg'], module.params['title'], module.params['device'])
    except Exception:
        module.fail_json(msg='Unable to send msg via pushover')

    module.exit_json(msg='message sent successfully: %s' % response, changed=False)


if __name__ == '__main__':
    main()

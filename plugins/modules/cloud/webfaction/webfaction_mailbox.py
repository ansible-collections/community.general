#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Quentin Stafford-Fraser and Andy Baker
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Create webfaction mailbox using Ansible and the Webfaction API

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: webfaction_mailbox
short_description: Add or remove mailboxes on Webfaction
description:
    - Add or remove mailboxes on a Webfaction account. Further documentation at https://github.com/quentinsf/ansible-webfaction.
author: Quentin Stafford-Fraser (@quentinsf)
notes:
    - >
      You can run playbooks that use this on a local machine, or on a Webfaction host, or elsewhere, since the scripts use the remote webfaction API.
      The location is not important. However, running them on multiple hosts I(simultaneously) is best avoided. If you don't specify I(localhost) as
      your host, you may want to add C(serial: 1) to the plays.
    - See `the webfaction API <https://docs.webfaction.com/xmlrpc-api/>`_ for more info.
options:

    mailbox_name:
        description:
            - The name of the mailbox
        required: true
        type: str

    mailbox_password:
        description:
            - The password for the mailbox
        required: true
        type: str

    state:
        description:
            - Whether the mailbox should exist
        choices: ['present', 'absent']
        default: "present"
        type: str

    login_name:
        description:
            - The webfaction account to use
        required: true
        type: str

    login_password:
        description:
            - The webfaction password to use
        required: true
        type: str
'''

EXAMPLES = '''
  - name: Create a mailbox
    community.general.webfaction_mailbox:
      mailbox_name="mybox"
      mailbox_password="myboxpw"
      state=present
      login_name={{webfaction_user}}
      login_password={{webfaction_passwd}}
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import xmlrpc_client


webfaction = xmlrpc_client.ServerProxy('https://api.webfaction.com/')


def main():

    module = AnsibleModule(
        argument_spec=dict(
            mailbox_name=dict(required=True),
            mailbox_password=dict(required=True, no_log=True),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            login_name=dict(required=True),
            login_password=dict(required=True, no_log=True),
        ),
        supports_check_mode=True
    )

    mailbox_name = module.params['mailbox_name']
    site_state = module.params['state']

    session_id, account = webfaction.login(
        module.params['login_name'],
        module.params['login_password']
    )

    mailbox_list = [x['mailbox'] for x in webfaction.list_mailboxes(session_id)]
    existing_mailbox = mailbox_name in mailbox_list

    result = {}

    # Here's where the real stuff happens

    if site_state == 'present':

        # Does a mailbox with this name already exist?
        if existing_mailbox:
            module.exit_json(changed=False,)

        positional_args = [session_id, mailbox_name]

        if not module.check_mode:
            # If this isn't a dry run, create the mailbox
            result.update(webfaction.create_mailbox(*positional_args))

    elif site_state == 'absent':

        # If the mailbox is already not there, nothing changed.
        if not existing_mailbox:
            module.exit_json(changed=False)

        if not module.check_mode:
            # If this isn't a dry run, delete the mailbox
            result.update(webfaction.delete_mailbox(session_id, mailbox_name))

    else:
        module.fail_json(msg="Unknown state specified: {0}".format(site_state))

    module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()

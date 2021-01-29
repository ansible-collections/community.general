#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2015, Brian Coca <bcoca@ansible.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: jabber
short_description: Send a message to jabber user or chat room
description:
   - Send a message to jabber
options:
  user:
    type: str
    description:
      - User as which to connect
    required: true
  password:
    type: str
    description:
      - password for user to connect
    required: true
  to:
    type: str
    description:
      - user ID or name of the room, when using room use a slash to indicate your nick.
    required: true
  msg:
    type: str
    description:
      - The message body.
    required: true
  host:
    type: str
    description:
      - host to connect, overrides user info
  port:
    type: int
    description:
      - port to connect to, overrides default
    default: 5222
  encoding:
    type: str
    description:
      - message encoding

# informational: requirements for nodes
requirements:
    - python xmpp (xmpppy)
author: "Brian Coca (@bcoca)"
'''

EXAMPLES = '''
- name: Send a message to a user
  community.general.jabber:
    user: mybot@example.net
    password: secret
    to: friend@example.net
    msg: Ansible task finished

- name: Send a message to a room
  community.general.jabber:
    user: mybot@example.net
    password: secret
    to: mychaps@conference.example.net/ansiblebot
    msg: Ansible task finished

- name: Send a message, specifying the host and port
  community.general.jabber:
    user: mybot@example.net
    host: talk.example.net
    port: 5223
    password: secret
    to: mychaps@example.net
    msg: Ansible task finished
'''

import time
import traceback

HAS_XMPP = True
XMPP_IMP_ERR = None
try:
    import xmpp
except ImportError:
    XMPP_IMP_ERR = traceback.format_exc()
    HAS_XMPP = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native


def main():

    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True),
            password=dict(required=True, no_log=True),
            to=dict(required=True),
            msg=dict(required=True),
            host=dict(required=False),
            port=dict(required=False, default=5222, type='int'),
            encoding=dict(required=False),
        ),
        supports_check_mode=True
    )

    if not HAS_XMPP:
        module.fail_json(msg=missing_required_lib('xmpppy'), exception=XMPP_IMP_ERR)

    jid = xmpp.JID(module.params['user'])
    user = jid.getNode()
    server = jid.getDomain()
    port = module.params['port']
    password = module.params['password']
    try:
        to, nick = module.params['to'].split('/', 1)
    except ValueError:
        to, nick = module.params['to'], None

    if module.params['host']:
        host = module.params['host']
    else:
        host = server
    if module.params['encoding']:
        xmpp.simplexml.ENCODING = module.params['encoding']

    msg = xmpp.protocol.Message(body=module.params['msg'])

    try:
        conn = xmpp.Client(server, debug=[])
        if not conn.connect(server=(host, port)):
            module.fail_json(rc=1, msg='Failed to connect to server: %s' % (server))
        if not conn.auth(user, password, 'Ansible'):
            module.fail_json(rc=1, msg='Failed to authorize %s on: %s' % (user, server))
        # some old servers require this, also the sleep following send
        conn.sendInitPresence(requestRoster=0)

        if nick:  # sending to room instead of user, need to join
            msg.setType('groupchat')
            msg.setTag('x', namespace='http://jabber.org/protocol/muc#user')
            join = xmpp.Presence(to=module.params['to'])
            join.setTag('x', namespace='http://jabber.org/protocol/muc')
            conn.send(join)
            time.sleep(1)
        else:
            msg.setType('chat')

        msg.setTo(to)
        if not module.check_mode:
            conn.send(msg)
        time.sleep(1)
        conn.disconnect()
    except Exception as e:
        module.fail_json(msg="unable to send msg: %s" % to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=False, to=to, user=user, msg=msg.getBody())


if __name__ == '__main__':
    main()

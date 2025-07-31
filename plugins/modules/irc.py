#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Jan-Piet Mens <jpmens () gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: irc
short_description: Send a message to an IRC channel or a nick
description:
  - Send a message to an IRC channel or a nick. This is a very simplistic implementation.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  server:
    type: str
    description:
      - IRC server name/address.
    default: localhost
  port:
    type: int
    description:
      - IRC server port number.
    default: 6667
  nick:
    type: str
    description:
      - Nickname to send the message from. May be shortened, depending on server's NICKLEN setting.
    default: ansible
  msg:
    type: str
    description:
      - The message body.
    required: true
  topic:
    type: str
    description:
      - Set the channel topic.
  color:
    type: str
    description:
      - Text color for the message.
    default: "none"
    choices:
      - none
      - white
      - black
      - blue
      - green
      - red
      - brown
      - purple
      - orange
      - yellow
      - light_green
      - teal
      - light_cyan
      - light_blue
      - pink
      - gray
      - light_gray
    aliases: [colour]
  channel:
    type: str
    description:
      - Channel name. One of nick_to or channel needs to be set. When both are set, the message is sent to both of them.
  nick_to:
    type: list
    elements: str
    description:
      - A list of nicknames to send the message to. One of nick_to or channel needs to be set. When both are defined, the
        message is sent to both of them.
  key:
    type: str
    description:
      - Channel key.
  passwd:
    type: str
    description:
      - Server password.
  timeout:
    type: int
    description:
      - Timeout to use while waiting for successful registration and join messages, this is to prevent an endless loop.
    default: 30
  use_tls:
    description:
      - Designates whether TLS/SSL should be used when connecting to the IRC server.
      - O(use_tls) is available since community.general 8.1.0, before the option was exlusively called O(use_ssl). The latter
        is now an alias of O(use_tls).
      - B(Note:) for security reasons, you should always set O(use_tls=true) and O(validate_certs=true) whenever possible.
      - The default of this option changed to V(true) in community.general 10.0.0.
    type: bool
    default: true
    aliases:
      - use_ssl
  part:
    description:
      - Designates whether user should part from channel after sending message or not. Useful for when using a mock bot and
        not wanting join/parts between messages.
    type: bool
    default: true
  style:
    type: str
    description:
      - Text style for the message. Note italic does not work on some clients.
    choices: ["bold", "underline", "reverse", "italic", "none"]
    default: none
  validate_certs:
    description:
      - If set to V(false), the SSL certificates are not validated.
      - This should always be set to V(true). Using V(false) is unsafe and should only be done if the network between between
        Ansible and the IRC server is known to be safe.
      - B(Note:) for security reasons, you should always set O(use_tls=true) and O(validate_certs=true) whenever possible.
      - The default of this option changed to V(true) in community.general 10.0.0.
    type: bool
    default: true
    version_added: 8.1.0

# informational: requirements for nodes
requirements: [socket]
author:
  - "Jan-Piet Mens (@jpmens)"
  - "Matt Martz (@sivel)"
"""

EXAMPLES = r"""
- name: Send a message to an IRC channel from nick ansible
  community.general.irc:
    server: irc.example.net
    use_tls: true
    validate_certs: true
    channel: '#t1'
    msg: Hello world

- name: Send a message to an IRC channel
  local_action:
    module: irc
    port: 6669
    server: irc.example.net
    use_tls: true
    validate_certs: true
    channel: '#t1'
    msg: 'All finished at {{ ansible_date_time.iso8601 }}'
    color: red
    nick: ansibleIRC

- name: Send a message to an IRC channel
  local_action:
    module: irc
    port: 6669
    server: irc.example.net
    use_tls: true
    validate_certs: true
    channel: '#t1'
    nick_to:
      - nick1
      - nick2
    msg: 'All finished at {{ ansible_date_time.iso8601 }}'
    color: red
    nick: ansibleIRC
"""

# ===========================================
# IRC module support methods.
#

import re
import socket
import ssl
import time
import traceback

from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible.module_utils.basic import AnsibleModule


def send_msg(msg, server='localhost', port='6667', channel=None, nick_to=None, key=None, topic=None,
             nick="ansible", color='none', passwd=False, timeout=30, use_tls=False, validate_certs=True,
             part=True, style=None):
    '''send message to IRC'''
    nick_to = [] if nick_to is None else nick_to

    colornumbers = {
        'white': "00",
        'black': "01",
        'blue': "02",
        'green': "03",
        'red': "04",
        'brown': "05",
        'purple': "06",
        'orange': "07",
        'yellow': "08",
        'light_green': "09",
        'teal': "10",
        'light_cyan': "11",
        'light_blue': "12",
        'pink': "13",
        'gray': "14",
        'light_gray': "15",
    }

    stylechoices = {
        'bold': "\x02",
        'underline': "\x1F",
        'reverse': "\x16",
        'italic': "\x1D",
    }

    try:
        styletext = stylechoices[style]
    except Exception:
        styletext = ""

    try:
        colornumber = colornumbers[color]
        colortext = "\x03" + colornumber
    except Exception:
        colortext = ""

    message = styletext + colortext + msg

    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if use_tls:
        kwargs = {}
        if validate_certs:
            try:
                context = ssl.create_default_context()
                kwargs["server_hostname"] = server
            except AttributeError:
                raise Exception('Need at least Python 2.7.9 for SSL certificate validation')
        else:
            if getattr(ssl, 'PROTOCOL_TLS', None) is not None:
                # Supported since Python 2.7.13
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            else:
                context = ssl.SSLContext()
            context.verify_mode = ssl.CERT_NONE
        irc = context.wrap_socket(irc, **kwargs)
    irc.connect((server, int(port)))

    if passwd:
        irc.send(to_bytes('PASS %s\r\n' % passwd))
    irc.send(to_bytes('NICK %s\r\n' % nick))
    irc.send(to_bytes('USER %s %s %s :ansible IRC\r\n' % (nick, nick, nick)))
    motd = ''
    start = time.time()
    while 1:
        motd += to_native(irc.recv(1024))
        # The server might send back a shorter nick than we specified (due to NICKLEN),
        #  so grab that and use it from now on (assuming we find the 00[1-4] response).
        match = re.search(r'^:\S+ 00[1-4] (?P<nick>\S+) :', motd, flags=re.M)
        if match:
            nick = match.group('nick')
            break
        elif time.time() - start > timeout:
            raise Exception('Timeout waiting for IRC server welcome response')
        time.sleep(0.5)

    if channel:
        if key:
            irc.send(to_bytes('JOIN %s %s\r\n' % (channel, key)))
        else:
            irc.send(to_bytes('JOIN %s\r\n' % channel))

        join = ''
        start = time.time()
        while 1:
            join += to_native(irc.recv(1024))
            if re.search(r'^:\S+ 366 %s %s :' % (nick, channel), join, flags=re.M | re.I):
                break
            elif time.time() - start > timeout:
                raise Exception('Timeout waiting for IRC JOIN response')
            time.sleep(0.5)

        if topic is not None:
            irc.send(to_bytes('TOPIC %s :%s\r\n' % (channel, topic)))
            time.sleep(1)

    if nick_to:
        for nick in nick_to:
            irc.send(to_bytes('PRIVMSG %s :%s\r\n' % (nick, message)))
    if channel:
        irc.send(to_bytes('PRIVMSG %s :%s\r\n' % (channel, message)))
    time.sleep(1)
    if part:
        if channel:
            irc.send(to_bytes('PART %s\r\n' % channel))
        irc.send(to_bytes('QUIT\r\n'))
        time.sleep(1)
    irc.close()

# ===========================================
# Main
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server=dict(default='localhost'),
            port=dict(type='int', default=6667),
            nick=dict(default='ansible'),
            nick_to=dict(type='list', elements='str'),
            msg=dict(required=True),
            color=dict(default="none", aliases=['colour'], choices=["white", "black", "blue",
                                                                    "green", "red", "brown",
                                                                    "purple", "orange", "yellow",
                                                                    "light_green", "teal", "light_cyan",
                                                                    "light_blue", "pink", "gray",
                                                                    "light_gray", "none"]),
            style=dict(default="none", choices=["underline", "reverse", "bold", "italic", "none"]),
            channel=dict(),
            key=dict(no_log=True),
            topic=dict(),
            passwd=dict(no_log=True),
            timeout=dict(type='int', default=30),
            part=dict(type='bool', default=True),
            use_tls=dict(type='bool', default=True, aliases=['use_ssl']),
            validate_certs=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
        required_one_of=[['channel', 'nick_to']]
    )

    server = module.params["server"]
    port = module.params["port"]
    nick = module.params["nick"]
    nick_to = module.params["nick_to"]
    msg = module.params["msg"]
    color = module.params["color"]
    channel = module.params["channel"]
    topic = module.params["topic"]
    if topic and not channel:
        module.fail_json(msg="When topic is specified, a channel is required.")
    key = module.params["key"]
    passwd = module.params["passwd"]
    timeout = module.params["timeout"]
    use_tls = module.params["use_tls"]
    part = module.params["part"]
    style = module.params["style"]
    validate_certs = module.params["validate_certs"]

    try:
        send_msg(msg, server, port, channel, nick_to, key, topic, nick, color, passwd, timeout, use_tls, validate_certs, part, style)
    except Exception as e:
        module.fail_json(msg="unable to send to IRC: %s" % to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=False, channel=channel, nick=nick,
                     msg=msg)


if __name__ == '__main__':
    main()

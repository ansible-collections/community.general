#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: campfire
short_description: Send a message to Campfire
description:
   - Send a message to Campfire.
   - Messages with newlines will result in a "Paste" message being sent.
options:
  subscription:
    type: str
    description:
      - The subscription name to use.
    required: true
  token:
    type: str
    description:
      - API token.
    required: true
  room:
    type: str
    description:
      - Room number to which the message should be sent.
    required: true
  msg:
    type: str
    description:
      - The message body.
    required: true
  notify:
    type: str
    description:
      - Send a notification sound before the message.
    required: false
    choices: ["56k", "bell", "bezos", "bueller", "clowntown",
              "cottoneyejoe", "crickets", "dadgummit", "dangerzone",
              "danielsan", "deeper", "drama", "greatjob", "greyjoy",
              "guarantee", "heygirl", "horn", "horror",
              "inconceivable", "live", "loggins", "makeitso", "noooo",
              "nyan", "ohmy", "ohyeah", "pushit", "rimshot",
              "rollout", "rumble", "sax", "secret", "sexyback",
              "story", "tada", "tmyk", "trololo", "trombone", "unix",
              "vuvuzela", "what", "whoomp", "yeah", "yodel"]

# informational: requirements for nodes
requirements: [ ]
author: "Adam Garside (@fabulops)"
'''

EXAMPLES = '''
- name: Send a message to Campfire
  community.general.campfire:
    subscription: foo
    token: 12345
    room: 123
    msg: Task completed.

- name: Send a message to Campfire
  community.general.campfire:
    subscription: foo
    token: 12345
    room: 123
    notify: loggins
    msg: Task completed ... with feeling.
'''

try:
    from html import escape as html_escape
except ImportError:
    # Python-3.2 or later
    import cgi

    def html_escape(text, quote=True):
        return cgi.escape(text, quote)

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def main():

    module = AnsibleModule(
        argument_spec=dict(
            subscription=dict(required=True),
            token=dict(required=True, no_log=True),
            room=dict(required=True),
            msg=dict(required=True),
            notify=dict(required=False,
                        choices=["56k", "bell", "bezos", "bueller",
                                 "clowntown", "cottoneyejoe",
                                 "crickets", "dadgummit", "dangerzone",
                                 "danielsan", "deeper", "drama",
                                 "greatjob", "greyjoy", "guarantee",
                                 "heygirl", "horn", "horror",
                                 "inconceivable", "live", "loggins",
                                 "makeitso", "noooo", "nyan", "ohmy",
                                 "ohyeah", "pushit", "rimshot",
                                 "rollout", "rumble", "sax", "secret",
                                 "sexyback", "story", "tada", "tmyk",
                                 "trololo", "trombone", "unix",
                                 "vuvuzela", "what", "whoomp", "yeah",
                                 "yodel"]),
        ),
        supports_check_mode=False
    )

    subscription = module.params["subscription"]
    token = module.params["token"]
    room = module.params["room"]
    msg = module.params["msg"]
    notify = module.params["notify"]

    URI = "https://%s.campfirenow.com" % subscription
    NSTR = "<message><type>SoundMessage</type><body>%s</body></message>"
    MSTR = "<message><body>%s</body></message>"
    AGENT = "Ansible/1.2"

    # Hack to add basic auth username and password the way fetch_url expects
    module.params['url_username'] = token
    module.params['url_password'] = 'X'

    target_url = '%s/room/%s/speak.xml' % (URI, room)
    headers = {'Content-Type': 'application/xml',
               'User-agent': AGENT}

    # Send some audible notification if requested
    if notify:
        response, info = fetch_url(module, target_url, data=NSTR % html_escape(notify), headers=headers)
        if info['status'] not in [200, 201]:
            module.fail_json(msg="unable to send msg: '%s', campfire api"
                             " returned error code: '%s'" %
                                 (notify, info['status']))

    # Send the message
    response, info = fetch_url(module, target_url, data=MSTR % html_escape(msg), headers=headers)
    if info['status'] not in [200, 201]:
        module.fail_json(msg="unable to send msg: '%s', campfire api"
                         " returned error code: '%s'" %
                             (msg, info['status']))

    module.exit_json(changed=True, room=room, msg=msg, notify=notify)


if __name__ == '__main__':
    main()

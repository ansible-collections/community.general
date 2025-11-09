#!/usr/bin/python
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: campfire
short_description: Send a message to Campfire
description:
  - Send a message to Campfire.
  - Messages with newlines result in a "Paste" message being sent.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
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
    choices:
      - 56k
      - bell
      - bezos
      - bueller
      - clowntown
      - cottoneyejoe
      - crickets
      - dadgummit
      - dangerzone
      - danielsan
      - deeper
      - drama
      - greatjob
      - greyjoy
      - guarantee
      - heygirl
      - horn
      - horror
      - inconceivable
      - live
      - loggins
      - makeitso
      - noooo
      - nyan
      - ohmy
      - ohyeah
      - pushit
      - rimshot
      - rollout
      - rumble
      - sax
      - secret
      - sexyback
      - story
      - tada
      - tmyk
      - trololo
      - trombone
      - unix
      - vuvuzela
      - what
      - whoomp
      - yeah
      - yodel

# informational: requirements for nodes
requirements: []
author: "Adam Garside (@fabulops)"
"""

EXAMPLES = r"""
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
"""

from html import escape as html_escape

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def main():
    module = AnsibleModule(
        argument_spec=dict(
            subscription=dict(required=True),
            token=dict(required=True, no_log=True),
            room=dict(required=True),
            msg=dict(required=True),
            notify=dict(
                choices=[
                    "56k",
                    "bell",
                    "bezos",
                    "bueller",
                    "clowntown",
                    "cottoneyejoe",
                    "crickets",
                    "dadgummit",
                    "dangerzone",
                    "danielsan",
                    "deeper",
                    "drama",
                    "greatjob",
                    "greyjoy",
                    "guarantee",
                    "heygirl",
                    "horn",
                    "horror",
                    "inconceivable",
                    "live",
                    "loggins",
                    "makeitso",
                    "noooo",
                    "nyan",
                    "ohmy",
                    "ohyeah",
                    "pushit",
                    "rimshot",
                    "rollout",
                    "rumble",
                    "sax",
                    "secret",
                    "sexyback",
                    "story",
                    "tada",
                    "tmyk",
                    "trololo",
                    "trombone",
                    "unix",
                    "vuvuzela",
                    "what",
                    "whoomp",
                    "yeah",
                    "yodel",
                ]
            ),
        ),
        supports_check_mode=False,
    )

    subscription = module.params["subscription"]
    token = module.params["token"]
    room = module.params["room"]
    msg = module.params["msg"]
    notify = module.params["notify"]

    URI = f"https://{subscription}.campfirenow.com"
    NSTR = "<message><type>SoundMessage</type><body>%s</body></message>"
    MSTR = "<message><body>%s</body></message>"
    AGENT = "Ansible/1.2"

    # Hack to add basic auth username and password the way fetch_url expects
    module.params["url_username"] = token
    module.params["url_password"] = "X"

    target_url = f"{URI}/room/{room}/speak.xml"
    headers = {"Content-Type": "application/xml", "User-agent": AGENT}

    # Send some audible notification if requested
    if notify:
        response, info = fetch_url(module, target_url, data=NSTR % html_escape(notify), headers=headers)
        if info["status"] not in [200, 201]:
            module.fail_json(
                msg=f"unable to send msg: '{notify}', campfire api returned error code: '{info['status']}'"
            )

    # Send the message
    response, info = fetch_url(module, target_url, data=MSTR % html_escape(msg), headers=headers)
    if info["status"] not in [200, 201]:
        module.fail_json(msg=f"unable to send msg: '{msg}', campfire api returned error code: '{info['status']}'")

    module.exit_json(changed=True, room=room, msg=msg, notify=notify)


if __name__ == "__main__":
    main()

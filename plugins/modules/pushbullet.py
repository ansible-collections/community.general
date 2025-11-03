#!/usr/bin/python
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
author: "Willy Barro (@willybarro)"
requirements: [pushbullet.py]
module: pushbullet
short_description: Sends notifications to Pushbullet
description:
  - This module sends push notifications through Pushbullet to channels or devices.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  api_key:
    type: str
    description:
      - Push bullet API token.
    required: true
  channel:
    type: str
    description:
      - The channel TAG you wish to broadcast a push notification, as seen on the "My Channels" > "Edit your channel" at Pushbullet
        page.
  device:
    type: str
    description:
      - The device NAME you wish to send a push notification, as seen on the Pushbullet main page.
  push_type:
    type: str
    description:
      - Thing you wish to push.
    default: note
    choices: ["note", "link"]
  title:
    type: str
    description:
      - Title of the notification.
    required: true
  body:
    type: str
    description:
      - Body of the notification, for example details of the fault you are alerting.
  url:
    type: str
    description:
      - URL field, used when O(push_type=link).
notes:
  - Requires C(pushbullet.py) Python package on the remote host. You can install it through C(pip) with C(pip install pushbullet.py).
  - See U(https://github.com/randomchars/pushbullet.py).
"""

EXAMPLES = r"""
- name: Sends a push notification to a device
  community.general.pushbullet:
    api_key: "ABC123abc123ABC123abc123ABC123ab"
    device: "Chrome"
    title: "You may see this on Google Chrome"

- name: Sends a link to a device
  community.general.pushbullet:
    api_key: ABC123abc123ABC123abc123ABC123ab
    device: Chrome
    push_type: link
    title: Ansible Documentation
    body: https://docs.ansible.com/

- name: Sends a push notification to a channel
  community.general.pushbullet:
    api_key: ABC123abc123ABC123abc123ABC123ab
    channel: my-awesome-channel
    title: "Broadcasting a message to the #my-awesome-channel folks"

- name: Sends a push notification with title and body to a channel
  community.general.pushbullet:
    api_key: ABC123abc123ABC123abc123ABC123ab
    channel: my-awesome-channel
    title: ALERT! Signup service is down
    body: Error rate on signup service is over 90% for more than 2 minutes
"""

import traceback

PUSHBULLET_IMP_ERR = None
try:
    from pushbullet import PushBullet
    from pushbullet.errors import InvalidKeyError, PushError
except ImportError:
    PUSHBULLET_IMP_ERR = traceback.format_exc()
    pushbullet_found = False
else:
    pushbullet_found = True

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


# ===========================================
# Main
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(type="str", required=True, no_log=True),
            channel=dict(type="str"),
            device=dict(type="str"),
            push_type=dict(type="str", default="note", choices=["note", "link"]),
            title=dict(type="str", required=True),
            body=dict(type="str"),
            url=dict(type="str"),
        ),
        mutually_exclusive=(["channel", "device"],),
        supports_check_mode=True,
    )

    api_key = module.params["api_key"]
    channel = module.params["channel"]
    device = module.params["device"]
    push_type = module.params["push_type"]
    title = module.params["title"]
    body = module.params["body"]
    url = module.params["url"]

    if not pushbullet_found:
        module.fail_json(msg=missing_required_lib("pushbullet.py"), exception=PUSHBULLET_IMP_ERR)

    # Init pushbullet
    try:
        pb = PushBullet(api_key)
        target = None
    except InvalidKeyError:
        module.fail_json(msg="Invalid api_key")

    # Checks for channel/device
    if device is None and channel is None:
        module.fail_json(msg="You need to provide a channel or a device.")

    # Search for given device
    if device is not None:
        devices_by_nickname = {}
        for d in pb.devices:
            devices_by_nickname[d.nickname] = d

        if device in devices_by_nickname:
            target = devices_by_nickname[device]
        else:
            module.fail_json(
                msg="Device '%s' not found. Available devices: '%s'" % (device, "', '".join(devices_by_nickname.keys()))
            )

    # Search for given channel
    if channel is not None:
        channels_by_tag = {}
        for c in pb.channels:
            channels_by_tag[c.channel_tag] = c

        if channel in channels_by_tag:
            target = channels_by_tag[channel]
        else:
            module.fail_json(
                msg="Channel '%s' not found. Available channels: '%s'" % (channel, "', '".join(channels_by_tag.keys()))
            )

    # If in check mode, exit saying that we succeeded
    if module.check_mode:
        module.exit_json(changed=False, msg="OK")

    # Send push notification
    try:
        if push_type == "link":
            target.push_link(title, url, body)
        else:
            target.push_note(title, body)
        module.exit_json(changed=False, msg="OK")
    except PushError as e:
        module.fail_json(msg=f"An error occurred, Pushbullet's response: {e}")

    module.fail_json(msg="An unknown error has occurred")


if __name__ == "__main__":
    main()

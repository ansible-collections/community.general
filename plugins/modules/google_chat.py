#!/usr/bin/python

# Copyright (c) 2026, Tom Scholz <tomscholz@outlook.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: google_chat
short_description: Send Google Chat notifications
version_added: "13.1.0"
description:
  - Sends notifications to a Google Chat space using an incoming webhook.
  - Incoming webhooks are one-way. They send messages but cannot receive or respond to them.
author:
  - Tom Scholz (@tomscholz)
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  space:
    type: str
    required: true
    description:
      - The identifier of the Chat space to post to, taken from the incoming webhook URL.
      - For a webhook URL of the form C(https://chat.googleapis.com/v1/spaces/AAAA/messages?key=...&token=...),
        this is the C(AAAA) part.
  key:
    type: str
    required: true
    description:
      - The C(key) request parameter from the incoming webhook URL.
      - Keep this value secret as it grants the ability to post to the space.
  token:
    type: str
    required: true
    description:
      - The C(token) request parameter from the incoming webhook URL.
      - Keep this value secret as it grants the ability to post to the space.
  text:
    type: str
    required: true
    description:
      - The text of the message to send.
      - 'Emoji must be supplied as Unicode characters (for example V(🚀)). The Chat API does not
        render C(:shortcode:) style emoji in plain text messages as they appear as literal text.'
  thread_key:
    type: str
    description:
      - An arbitrary key used to start or reply to a message thread.
      - When set, O(create_new_thread) controls the behavior when the thread is not found.
  create_new_thread:
    type: bool
    default: true
    description:
      - Controls behavior when O(thread_key) is set but no matching thread exists.
      - When V(true), a new thread is started if no matching thread is found.
      - When V(false), the message is only posted if a matching thread already exists, otherwise it fails.
      - Only used when O(thread_key) is set.
seealso:
  - name: Google Chat incoming webhooks
    description: Google's reference for sending messages to Chat with incoming webhooks.
    link: https://developers.google.com/workspace/chat/quickstart/webhooks
"""

EXAMPLES = r"""
- name: Send a notification to Google Chat
  community.general.google_chat:
    space: SPACE_ID
    key: KEY
    token: TOKEN
    text: '{{ inventory_hostname }} completed'
  delegate_to: localhost

- name: Start a thread
  community.general.google_chat:
    space: SPACE_ID
    key: KEY
    token: TOKEN
    text: 'Starting a thread'
    thread_key: 'deploy-2026-06-01'
    create_new_thread: true

# Post each deploy step into a single thread. The first message creates the thread
# with create_new_thread=true. Follow-ups use create_new_thread=false so they only
# post if the opening message went through, rather than leaving orphan threads.
# Note: webhooks are rate-limited to 1 request per second per space.
- name: Announce deploy start (starts the thread)
  community.general.google_chat:
    space: "{{ chat_space }}"
    key: "{{ chat_key }}"
    token: "{{ chat_token }}"
    text: "🚀 Starting deploy of *{{ app_version | default('latest') }}* to {{ inventory_hostname }}"
    thread_key: "{{ deploy_thread }}"
    create_new_thread: true
  delegate_to: localhost
  run_once: true
  # deploy_thread is defined once for the play, for example:
  #   deploy_thread: "deploy-{{ inventory_hostname }}-{{ ansible_date_time.iso8601_basic_short }}"

- name: Report a step into the same thread
  community.general.google_chat:
    space: "{{ chat_space }}"
    key: "{{ chat_key }}"
    token: "{{ chat_token }}"
    text: "✅ Step 1/3 – code checked out"
    thread_key: "{{ deploy_thread }}"
    create_new_thread: false
  delegate_to: localhost
  run_once: true

# Wrap risky tasks so a failure posts to the same thread before a play aborts.
- name: Deploy with failure notification
  block:
    - name: Restart service
      ansible.builtin.systemd:
        name: app
        state: restarted

    - name: Report success
      community.general.google_chat:
        space: "{{ chat_space }}"
        key: "{{ chat_key }}"
        token: "{{ chat_token }}"
        text: "🎉 Deploy to {{ inventory_hostname }} complete"
        thread_key: "{{ deploy_thread }}"
        create_new_thread: false
      delegate_to: localhost
      run_once: true
  rescue:
    - name: Report failure into the thread
      community.general.google_chat:
        space: "{{ chat_space }}"
        key: "{{ chat_key }}"
        token: "{{ chat_token }}"
        text: "❌ Deploy to {{ inventory_hostname }} *failed* – {{ ansible_failed_task.name }}"
        thread_key: "{{ deploy_thread }}"
        create_new_thread: false
      delegate_to: localhost
      run_once: true

    - name: Re-raise the failure
      ansible.builtin.fail:
        msg: "Deploy failed at {{ ansible_failed_task.name }}"
"""

RETURN = r"""
name:
  description: Resource name of the created message, returned by the Chat API.
  returned: success
  type: str
  sample: "spaces/AAAA/messages/BBBB.BBBB"
thread_name:
  description: Resource name of the thread the message belongs to.
  returned: when the response includes a thread
  type: str
  sample: "spaces/AAAA/threads/CCCC"
"""

import typing as t
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

BASE_URL = "https://chat.googleapis.com/v1/spaces"

if t.TYPE_CHECKING:
    Payload = dict[str, t.Any]
    Response = dict[str, t.Any]


def build_payload(text: str, thread_key: str | None) -> Payload:
    payload: Payload = {"text": text}

    if thread_key is not None:
        payload["thread"] = {"threadKey": thread_key}
    return payload


def build_url(space: str, key: str, token: str, thread_key: str | None, create_new_thread: bool) -> str:
    params = {"key": key, "token": token}
    if thread_key is not None:
        params["messageReplyOption"] = (
            "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD" if create_new_thread else "REPLY_MESSAGE_OR_FAIL"
        )
    return f"{BASE_URL}/{space}/messages?{urlencode(params)}"


def do_notify(module: AnsibleModule, url: str, payload: Payload) -> Response:
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
    }
    data = module.jsonify(payload)
    response, info = fetch_url(module=module, url=url, headers=headers, method="POST", data=data)

    if info["status"] != 200:
        body = info.get("body")
        if hasattr(body, "decode"):
            body = body.decode("utf-8", errors="replace")
        module.fail_json(
            msg=f"Failed to send message to Google Chat (HTTP {info['status']}): {body or info.get('msg')}"
        )

    return module.from_json(response.read())


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            space=dict(type="str", required=True),
            key=dict(type="str", required=True, no_log=True),
            token=dict(type="str", required=True, no_log=True),
            text=dict(type="str", required=True),
            thread_key=dict(type="str", no_log=False),
            create_new_thread=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=True)

    payload = build_payload(module.params["text"], module.params["thread_key"])
    url = build_url(
        module.params["space"],
        module.params["key"],
        module.params["token"],
        module.params["thread_key"],
        module.params["create_new_thread"],
    )

    response = do_notify(module, url, payload)

    result = {"changed": True}
    if "name" in response:
        result["name"] = response["name"]
    if isinstance(response.get("thread"), dict) and "name" in response["thread"]:
        result["thread_name"] = response["thread"]["name"]

    module.exit_json(**result)


if __name__ == "__main__":
    main()

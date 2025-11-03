#!/usr/bin/python
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: typetalk
short_description: Send a message to typetalk
description:
  - Send a message to typetalk using typetalk API.
deprecated:
  removed_in: 13.0.0
  why: The typetalk service will be discontinued on Dec 2025. See U(https://nulab.com/blog/company-news/typetalk-sunsetting/).
  alternative: There is none.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  client_id:
    type: str
    description:
      - OAuth2 client ID.
    required: true
  client_secret:
    type: str
    description:
      - OAuth2 client secret.
    required: true
  topic:
    type: int
    description:
      - Topic ID to post message.
    required: true
  msg:
    type: str
    description:
      - Message body.
    required: true
requirements: [json]
author: "Takashi Someda (@tksmd)"
"""

EXAMPLES = r"""
- name: Send a message to typetalk
  community.general.typetalk:
    client_id: 12345
    client_secret: 12345
    topic: 1
    msg: install completed
"""

import json
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, ConnectionError


def do_request(module, url, params, headers=None):
    data = urlencode(params)
    if headers is None:
        headers = dict()
    headers = dict(
        headers,
        **{
            "User-Agent": "Ansible/typetalk module",
        },
    )
    r, info = fetch_url(module, url, data=data, headers=headers)
    if info["status"] != 200:
        exc = ConnectionError(info["msg"])
        exc.code = info["status"]
        raise exc
    return r


def get_access_token(module, client_id, client_secret):
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "topic.post",
    }
    res = do_request(module, "https://typetalk.com/oauth2/access_token", params)
    return json.load(res)["access_token"]


def send_message(module, client_id, client_secret, topic, msg):
    """
    send message to typetalk
    """
    try:
        access_token = get_access_token(module, client_id, client_secret)
        url = f"https://typetalk.com/api/v1/topics/{topic}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        do_request(module, url, {"message": msg}, headers)
        return True, {"access_token": access_token}
    except ConnectionError as e:
        return False, e


def main():
    module = AnsibleModule(
        argument_spec=dict(
            client_id=dict(required=True),
            client_secret=dict(required=True, no_log=True),
            topic=dict(required=True, type="int"),
            msg=dict(required=True),
        ),
        supports_check_mode=False,
    )

    if not json:
        module.fail_json(msg="json module is required")

    client_id = module.params["client_id"]
    client_secret = module.params["client_secret"]
    topic = module.params["topic"]
    msg = module.params["msg"]

    res, error = send_message(module, client_id, client_secret, topic, msg)
    if not res:
        module.fail_json(msg=f"fail to send message with response code {error.code}")

    module.exit_json(changed=True, topic=topic, msg=msg)


if __name__ == "__main__":
    main()

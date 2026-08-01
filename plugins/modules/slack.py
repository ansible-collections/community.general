#!/usr/bin/python

# Copyright (c) 2026, Maksym Bakurevych <maxim.bakurevy@gmail.com>
# Copyright (c) 2020, Lee Goolsbee <lgoolsbee@atlassian.com>
# Copyright (c) 2020, Michal Middleton <mm.404@icloud.com>
# Copyright (c) 2017, Steve Pletcher <steve@steve-pletcher.com>
# Copyright (c) 2016, René Moser <mail@renemoser.net>
# Copyright (c) 2015, Stefan Berggren <nsg@nsg.cc>
# Copyright (c) 2014, Ramon de la Fuente <ramon@delafuente.nl>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: slack
short_description: Send Slack notifications
description:
  - The M(community.general.slack) module sends notifications to U(http://slack.com) using the Incoming WebHook integration.
author: "Ramon de la Fuente (@ramondelafuente)"
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  domain:
    type: str
    description:
      - "When using new format 'Webhook token' and WebAPI tokens: this can be V(slack.com) or V(slack-gov.com) and is ignored
        otherwise."
      - "When using old format 'Webhook token': Slack (sub)domain for your environment without protocol. (For example V(example.slack.com).)
        in Ansible 1.8 and beyond, this is deprecated and may be ignored. See token documentation for information."
  token:
    type: str
    description:
      - Slack integration token. This authenticates you to the Slack service. Make sure to use the correct type of token,
        depending on what method you use.
      - 'Webhook token: Prior to Ansible 1.8, a token looked like V(3Ffe373sfhRE6y42Fg3rvf4GlK). In Ansible 1.8 and above,
        Ansible adapts to the new Slack API where tokens look like V(G922VJP24/D921DW937/3Ffe373sfhRE6y42Fg3rvf4GlK). If tokens
        are in the new format then Slack ignores any value of domain except V(slack.com) or V(slack-gov.com). If the token
        is in the old format the domain is required. Ansible has no control of when Slack is going to remove the old API.
        When Slack does that the old format is going to cease working. B(Please keep in mind the tokens are not the API tokens
        but are the webhook tokens.) In Slack these are found in the webhook URL which are obtained under the apps and integrations.
        The incoming webhooks can be added in that area. In some cases this may be locked by your Slack admin and you must
        request access. It is there that the incoming webhooks can be added. The key is on the end of the URL given to you
        in that section.'
      - "WebAPI token: Slack WebAPI requires a personal, bot or work application token. These tokens start with V(xoxp-),
        V(xoxb-) or V(xoxa-), for example V(xoxb-1234-56789abcdefghijklmnopqrstuvwxyz). WebAPI token is required if you intend to receive
        thread_id. See Slack's documentation (U(https://api.slack.com/docs/token-types)) for more information."
    required: true
  msg:
    type: str
    description:
      - Message to send. Note that the module does not handle escaping characters. Plain-text angle brackets and ampersands
        should be converted to HTML entities (for example C(&) to C(&amp;)) before sending. See Slack's documentation
        (U(https://api.slack.com/docs/message-formatting))
        for more.
  channel:
    type: str
    description:
      - Channel to send the message to. If absent, the message goes to the channel selected for the O(token).
  thread_id:
    description:
      - Optional. Timestamp of parent message to thread this message, see U(https://api.slack.com/docs/message-threading).
    type: str
  message_id:
    description:
      - Optional. Message ID to edit, instead of posting a new message.
      - If supplied O(channel) must be in form of C(C0xxxxxxx). use C({{ slack_response.channel }}) to get RV(ignore:channel)
        from previous task run.
      - The token needs history scope to get information on the message to edit (C(channels:history,groups:history,mpim:history,im:history)).
      - Corresponds to C(ts) in the Slack API (U(https://api.slack.com/messaging/modifying)).
    type: str
    version_added: 1.2.0
  username:
    type: str
    description:
      - This is the sender of the message.
    default: "Ansible"
  icon_url:
    type: str
    description:
      - URL for the message sender's icon.
    default: https://docs.ansible.com/favicon/favicon.ico
  icon_emoji:
    type: str
    description:
      - Emoji for the message sender. See Slack documentation for options.
      - If O(icon_emoji) is set, O(icon_url) is not used.
  link_names:
    type: int
    description:
      - Automatically create links for channels and usernames in O(msg).
    default: 1
    choices:
      - 1
      - 0
  parse:
    type: str
    description:
      - Setting for the message parser at Slack.
    choices:
      - 'full'
      - 'none'
  validate_certs:
    description:
      - If V(false), SSL certificates are not validated. This should only be used on personally controlled sites using self-signed
        certificates.
    type: bool
    default: true
  color:
    type: str
    description:
      - Allow text to use default colors - use the default of V(normal) to not send a custom color bar at the start of the
        message.
      - Allowed values for color can be one of V(normal), V(good), V(warning), V(danger), any valid 3 digit or 6 digit hex
        color value.
    default: 'normal'
  attachments:
    type: list
    elements: dict
    description:
      - Define a list of attachments. This list mirrors the Slack JSON API.
      - For more information, see U(https://api.slack.com/docs/attachments).
  blocks:
    description:
      - Define a list of blocks. This list mirrors the Slack JSON API.
      - For more information, see U(https://api.slack.com/block-kit).
    type: list
    elements: dict
    version_added: 1.0.0
  prepend_hash:
    type: str
    description:
      - Setting for automatically prepending a V(#) symbol on the passed in O(channel).
      - The V(auto) method prepends a V(#) unless O(channel) starts with one of V(#), V(@), V(C0), V(GF), V(G0), V(CP). These
        prefixes only cover a small set of the prefixes that should not have a V(#) prepended. Since an exact condition which
        O(channel) values must not have the V(#) prefix is not known, the value V(auto) for this option is deprecated in the
        future. It is best to explicitly set O(prepend_hash=always) or O(prepend_hash=never) to obtain the needed behavior.
      - Before community.general 12.0.0, the default was V(auto). It has been deprecated since community.general 10.2.0.
      - Note that V(auto) will be deprecated in a future version.
      # TODO: Deprecate 'auto' in community.general 13.0.0
    default: never
    choices:
      - 'always'
      - 'never'
      - 'auto'
    version_added: 6.1.0
  files:
    type: list
    elements: dict
    description:
      - A list of files to be uploaded to Slack.
      - >
        Each list item should be a dictionary containing O(files[].path)
        (absolute or relative path to the file) and optionally
        O(files[].name) (the filename as it will appear in Slack).
      - If O(msg), O(attachments), or O(blocks) are provided, the files are attached as a reply to that message (creating a thread).
      - If no message content is provided, the files are uploaded as a standalone post in the specified O(channel).
      - "Note: File uploading requires a WebAPI token (starting with V(xoxb-) or V(xoxp-))."
      - "It does not work with standard Incoming Webhook URLs (the ones with tokens like V(T.../B.../...) )."
      - The app must have C(files:write) and C(chat:write) scopes in your Slack App settings and must be invited to the channel.
    suboptions:
      path:
        type: path
        required: true
        description:
          - The local path to the file to be uploaded.
      name:
        type: str
        description:
          - The name of the file as it should appear in Slack.
          - If not provided, the base name of the С(path) will be used.
    version_added: 13.1.0
  fail_on_file_error:
    type: bool
    description:
      - If V(true), the module fails if a file is missing or encounters an upload error.
      - If V(false), the module issues a warning and continue processing the next file.
    default: true
    version_added: 13.1.0
"""

EXAMPLES = r"""
- name: Send notification message via Slack
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} completed'
  delegate_to: localhost

- name: Send notification message via Slack all options
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} completed'
    channel: '#ansible'
    thread_id: '1539917263.000100'
    username: 'Ansible on {{ inventory_hostname }}'
    icon_url: http://www.example.com/some-image-file.png
    link_names: 0
    parse: 'none'
  delegate_to: localhost

- name: Insert a color bar in front of the message for visibility purposes and use the default webhook icon and name configured
    in Slack
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} is alive!'
    color: good
    username: ''
    icon_url: ''

- name: Insert a color bar in front of the message with valid hex color value
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: 'This message uses color in hex value'
    color: '#00aacc'
    username: ''
    icon_url: ''

- name: Use the attachments API
  community.general.slack:
    token: thetoken/generatedby/slack
    attachments:
      - text: Display my system load on host A and B
        color: '#ff00dd'
        title: System load
        fields:
          - title: System A
            value: "load average: 0,74, 0,66, 0,63"
            short: true
          - title: System B
            value: 'load average: 5,16, 4,64, 2,43'
            short: true

- name: Use the blocks API
  community.general.slack:
    token: thetoken/generatedby/slack
    blocks:
      - type: section
        text:
          type: mrkdwn
          text: |-
            *System load*
            Display my system load on host A and B
      - type: context
        elements:
          - type: mrkdwn
            text: |-
              *System A*
              load average: 0,74, 0,66, 0,63
          - type: mrkdwn
            text: |-
              *System B*
              load average: 5,16, 4,64, 2,43

- name: Send a message with a link using Slack markup
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: We sent this message using <https://www.ansible.com|Ansible>!

- name: Send a message with angle brackets and ampersands
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: This message has &lt;brackets&gt; &amp; ampersands in plain text.

- name: Initial Threaded Slack message
  community.general.slack:
    channel: '#ansible'
    token: xoxb-1234-56789abcdefghijklmnopqrstuvwxyz
    msg: 'Starting a thread with my initial post.'
  register: slack_response
- name: Add more info to thread
  community.general.slack:
    channel: '#ansible'
    token: xoxb-1234-56789abcdefghijklmnopqrstuvwxyz
    thread_id: "{{ slack_response['ts'] }}"
    color: good
    msg: 'And this is my threaded response!'

- name: Send a message to be edited later on
  community.general.slack:
    token: thetoken/generatedby/slack
    channel: '#ansible'
    msg: Deploying something...
  register: slack_response
- name: Edit message
  community.general.slack:
    token: thetoken/generatedby/slack
    # The 'channel' option does not accept the channel name. It must use the 'channel_id',
    # which can be retrieved for example from 'slack_response' from the previous task.
    channel: "{{ slack_response.channel }}"
    msg: Deployment complete!
    message_id: "{{ slack_response.ts }}"
- name: Send file to Slack
  community.general.slack:
    token: "xoxb-1234-56789abcdefghijklmnopqrstuvwxyz"
    channel: "channel-id"
    fail_on_file_error: false # Optional, defaults to true
    # If you want to sent message to channel without threads,
    # you dont need to use msg parameter
    msg: "Here is the file you asked for"
    files:
      - path: "./first.py" # file in your os
        # File name in Slack. If not provided, it will be the same as path,
        # so in this case "first.py":
        name: "test_report.py"
      - path: "./test_file.txt"
        name: "test_report.txt"
- name: Send file to Slack threads
  community.general.slack:
    token: "xoxb-1234-56789abcdefghijklmnopqrstuvwxyz"
    channel: "channel-id"
    thread_id: "thread-id" # if you want to send file to a specific thread
    files:
      - path: "./first.py" # file in your os
        # File name in Slack. If not provided, it will be the same as path,
        # so in this case "first.py":
        name: "test_report.py"
"""
import os
import re
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

# Escaping quotes and apostrophes to avoid ending string prematurely in ansible call.
# We do not escape other characters used as Slack metacharacters (e.g. &, <, >).
escape_table = {
    '"': '"',
    "'": "'",
}


def is_valid_hex_color(color_choice):
    return bool(re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", color_choice))


def escape_quotes(text):
    """Backslash any quotes within text."""
    return "".join(escape_table.get(c, c) for c in text)


def recursive_escape_quotes(obj, keys):
    """Recursively escape quotes inside supplied keys inside block kit objects"""
    if isinstance(obj, dict):
        escaped = {}
        for k, v in obj.items():
            if isinstance(v, str) and k in keys:
                escaped[k] = escape_quotes(v)
            else:
                escaped[k] = recursive_escape_quotes(v, keys)
    elif isinstance(obj, list):
        escaped = [recursive_escape_quotes(v, keys) for v in obj]
    else:
        escaped = obj
    return escaped


def build_payload_for_slack(
    text,
    channel,
    thread_id,
    username,
    icon_url,
    icon_emoji,
    link_names,
    parse,
    color,
    attachments,
    blocks,
    message_id,
    prepend_hash,
):
    payload = {}
    if color == "normal" and text is not None:
        payload = dict(text=escape_quotes(text))
    elif text is not None:
        # With a custom color we have to set the message as attachment, and explicitly turn markdown parsing on for it.
        payload = dict(attachments=[dict(text=escape_quotes(text), color=color, mrkdwn_in=["text"])])
    if channel is not None:
        if prepend_hash == "auto":
            if channel.startswith(("#", "@", "C0", "GF", "G0", "CP")):
                payload["channel"] = channel
            else:
                payload["channel"] = f"#{channel}"
        elif prepend_hash == "always":
            payload["channel"] = f"#{channel}"
        elif prepend_hash == "never":
            payload["channel"] = channel
    if thread_id is not None:
        payload["thread_ts"] = thread_id
    if username is not None:
        payload["username"] = username
    if icon_emoji is not None:
        payload["icon_emoji"] = icon_emoji
    else:
        payload["icon_url"] = icon_url
    if link_names is not None:
        payload["link_names"] = link_names
    if parse is not None:
        payload["parse"] = parse
    if message_id is not None:
        payload["ts"] = message_id

    if attachments is not None:
        if "attachments" not in payload:
            payload["attachments"] = []

    if attachments is not None:
        attachment_keys_to_escape = [
            "title",
            "text",
            "author_name",
            "pretext",
            "fallback",
        ]
        for attachment in attachments:
            for key in attachment_keys_to_escape:
                if key in attachment:
                    attachment[key] = escape_quotes(attachment[key])

            if "fallback" not in attachment:
                attachment["fallback"] = attachment["text"]

            payload["attachments"].append(attachment)

    if blocks is not None:
        block_keys_to_escape = ["text", "alt_text"]
        payload["blocks"] = recursive_escape_quotes(blocks, block_keys_to_escape)

    return payload


def validate_slack_domain(domain):
    return domain if domain in ("slack.com", "slack-gov.com") else "slack.com"


def get_slack_message(module, domain, token, channel, ts):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    qs = urlencode(
        {
            "channel": channel,
            "ts": ts,
            "limit": 1,
            "inclusive": "true",
        }
    )
    domain = validate_slack_domain(domain)
    url = f"https://{domain}/api/conversations.history?{qs}"
    response, info = fetch_url(module=module, url=url, headers=headers, method="GET")
    if info["status"] != 200:
        module.fail_json(msg="failed to get slack message")
    data = module.from_json(response.read())
    if data.get("ok") is False:
        module.fail_json(msg=f"failed to get slack message: {data}")
    if len(data["messages"]) < 1:
        module.fail_json(msg=f"no messages matching ts: {ts}")
    if len(data["messages"]) > 1:
        module.fail_json(msg=f"more than 1 message matching ts: {ts}")
    return data["messages"][0]


def do_notify_slack(module, domain, token, payload):
    use_webapi = False
    if token.count("/") >= 2:
        # New style webhook token
        domain = validate_slack_domain(domain)
        slack_uri = f"https://hooks.{domain}/services/{token}"
    elif re.match(r"^xox[abp]-\S+$", token):
        domain = validate_slack_domain(domain)
        slack_uri = f"https://{domain}/api/{'chat.update' if 'ts' in payload else 'chat.postMessage'}"
        use_webapi = True
    else:
        if not domain:
            module.fail_json(
                msg="Slack has updated its webhook API. You need to specify a token of the form "
                "XXXX/YYYY/ZZZZ in your playbook"
            )
        slack_uri = f"https://{domain}/services/hooks/incoming-webhook?token={token}"

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
    }
    if use_webapi:
        headers["Authorization"] = f"Bearer {token}"

    data = module.jsonify(payload)
    response, info = fetch_url(module=module, url=slack_uri, headers=headers, method="POST", data=data)

    if info["status"] != 200:
        if use_webapi:
            obscured_incoming_webhook = slack_uri
        else:
            obscured_incoming_webhook = f"https://hooks.{domain}/services/[obscured]"
        module.fail_json(msg=f" failed to send {data} to {obscured_incoming_webhook}: {info['msg']}")

    # each API requires different handling
    if use_webapi:
        return module.from_json(response.read())
    else:
        return {"webhook": "ok"}


def upload_slack_files(module, token, channel, files, thread_ts=None, fail_on_file_error=True):
    if not files:
        return {"ok": False, "msg": "No files provided"}

    uploaded_ids = []
    headers = {"Authorization": f"Bearer {token}"}

    for f_item in files:
        f_path = f_item["path"]
        f_name = f_item["name"] or os.path.basename(f_path)

        if not os.path.exists(f_path):
            error_msg = f"File {f_path} not found."
            if fail_on_file_error:
                module.fail_json(msg=error_msg)
            else:
                module.warn(f"{error_msg} Skipping.")
                continue

        file_size = os.path.getsize(f_path)
        url_get = f"https://slack.com/api/files.getUploadURLExternal?filename={f_name}&length={file_size}"

        resp, info = fetch_url(module, url_get, headers=headers, method="GET")

        if info["status"] != 200:
            module.fail_json(
                msg=f"Failed to get upload URL for {f_name}. Slack API endpoint returned HTTP {info['status']}.",
                details=info.get("msg", "No HTTP error message provided"),
            )

        res = module.from_json(resp.read())

        if not res.get("ok"):
            error_code = res.get("error", "unknown_error")
            fatal_errors = ["invalid_auth", "unknown_method", "missing_scope", "account_inactive"]
            if error_code in fatal_errors:
                module.fail_json(
                    msg=f"Fatal Slack API error occurred for {f_name}. Operation aborted.", error=error_code
                )
            module.warn(f"Slack API error for {f_name}: {error_code}")
            continue

        try:
            with open(f_path, "rb") as f:
                file_data = f.read()

            u_resp, u_info = fetch_url(
                module,
                res["upload_url"],
                data=file_data,
                method="POST",
                headers={"Content-Type": "application/octet-stream"},
            )

            if u_info["status"] != 200:
                module.warn(f"Failed to upload bits for {f_name}. Status: {u_info['status']}")
                continue

        except Exception as e:
            module.warn(f"Failed to upload bits for {f_name}: {e}")
            continue

        uploaded_ids.append({"id": res["file_id"], "title": f_name})

    if uploaded_ids:
        completion_payload = {"files": uploaded_ids, "channel_id": channel, "initial_comment": "Attached Files:"}

        if thread_ts:
            completion_payload["thread_ts"] = thread_ts

        f_url = "https://slack.com/api/files.completeUploadExternal"
        final_headers = headers.copy()
        final_headers["Content-Type"] = "application/json; charset=utf-8"

        resp, info = fetch_url(
            module, f_url, headers=final_headers, method="POST", data=module.jsonify(completion_payload)
        )

        if info["status"] != 200:
            return {"ok": False, "msg": f"Failed to complete upload. Status: {info['status']}"}

        return module.from_json(resp.read())

    return {"ok": False, "msg": "No files were successfully uploaded"}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(type="str"),
            token=dict(type="str", required=True, no_log=True),
            msg=dict(type="str"),
            channel=dict(type="str"),
            thread_id=dict(type="str"),
            username=dict(type="str", default="Ansible"),
            icon_url=dict(type="str", default="https://docs.ansible.com/favicon/favicon.ico"),
            icon_emoji=dict(type="str"),
            link_names=dict(type="int", default=1, choices=[0, 1]),
            parse=dict(type="str", choices=["none", "full"]),
            validate_certs=dict(default=True, type="bool"),
            color=dict(type="str", default="normal"),
            attachments=dict(type="list", elements="dict"),
            blocks=dict(type="list", elements="dict"),
            message_id=dict(type="str"),
            prepend_hash=dict(type="str", choices=["always", "never", "auto"], default="never"),
            fail_on_file_error=dict(type="bool", default=True),
            files=dict(
                type="list",
                elements="dict",
                options=dict(
                    path=dict(type="path", required=True),
                    name=dict(type="str"),
                ),
            ),
        ),
        supports_check_mode=True,
    )

    domain = module.params["domain"]
    token = module.params["token"]
    text = module.params["msg"]
    channel = module.params["channel"]
    thread_id = module.params["thread_id"]
    username = module.params["username"]
    icon_url = module.params["icon_url"]
    icon_emoji = module.params["icon_emoji"]
    link_names = module.params["link_names"]
    parse = module.params["parse"]
    color = module.params["color"]
    attachments = module.params["attachments"]
    blocks = module.params["blocks"]
    message_id = module.params["message_id"]
    prepend_hash = module.params["prepend_hash"]
    fail_on_file_error = module.params["fail_on_file_error"]
    files = module.params["files"]
    is_webhook = re.match(r"^T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+$", token)
    is_api_token = re.match(r"^xox[bpa]-", token)
    if not (is_webhook or is_api_token):
        module.fail_json(
            msg="The token provided is not a valid Slack token. "
            "Webhooks should look like T.../B.../X... and "
            "API tokens should start with xoxb-, xoxp-, or xoxa-."
        )
    color_choices = ["normal", "good", "warning", "danger"]
    if color not in color_choices and not is_valid_hex_color(color):
        module.fail_json(
            msg=f"Color value specified should be either one of {color_choices} or any valid hex value with length 3 or 6."
        )

    changed = True

    # if updating an existing message, we can check if there's anything to update
    if message_id is not None:
        changed = False
        msg = get_slack_message(module, domain, token, channel, message_id)
        for key in ("icon_url", "icon_emoji", "link_names", "color", "attachments", "blocks"):
            if msg.get(key) != module.params.get(key):
                changed = True
                break
        # if check mode is active, we shouldn't do anything regardless.
        # if changed=False, we don't need to do anything, so don't do it.
        if module.check_mode or not changed:
            module.exit_json(changed=changed, ts=msg["ts"], channel=msg["channel"])
    elif module.check_mode:
        module.exit_json(changed=changed)

    payload = build_payload_for_slack(
        text,
        channel,
        thread_id,
        username,
        icon_url,
        icon_emoji,
        link_names,
        parse,
        color,
        attachments,
        blocks,
        message_id,
        prepend_hash,
    )

    has_message_content = bool(text or attachments or blocks)
    slack_response = {}
    is_success = False

    if has_message_content:
        slack_response = do_notify_slack(module, domain, token, payload)
        # Check success for both WebAPI (ok: true) and incoming webhooks
        # (webhook: ok)
        is_success = slack_response.get("ok") or slack_response.get("webhook") == "ok"
    else:
        is_success = True

    file_upload_res = None
    if files and is_success:
        target_channel = slack_response.get("channel") or channel
        target_thread = slack_response.get("ts") or thread_id

        file_upload_res = upload_slack_files(
            module, token, target_channel, files, thread_ts=target_thread, fail_on_file_error=fail_on_file_error
        )

        # If sending only files, overall success depends on the upload result
        if not has_message_content:
            is_success = file_upload_res.get("ok", False)

    if is_success:
        # Exit with plain OK from WebHook, since we don't have more information
        # If we get 200 from webhook, the only answer is OK
        if "ok" not in slack_response and slack_response.get("webhook") == "ok" and not files:
            module.exit_json(msg="OK", changed=True)

        result = {
            "changed": True,
            "api": slack_response if has_message_content else {"status": "files_only_upload"},
            "payload": module.jsonify(payload) if has_message_content else None,
        }

        if file_upload_res:
            result["files_upload"] = file_upload_res

        if "ts" in slack_response:
            result.update({"ts": slack_response["ts"], "channel": slack_response["channel"]})
        elif file_upload_res and "files" in file_upload_res:
            result.update({"channel": channel})

        module.exit_json(**result)
    else:
        error_msg = slack_response.get("error") or (file_upload_res.get("msg") if file_upload_res else "Unknown error")
        module.fail_json(msg="Slack operation failed", error=error_msg)


if __name__ == "__main__":
    main()

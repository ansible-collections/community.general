#!/usr/bin/python

# Copyright (c) 2015, Matt Makai <matthew.makai@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: sendgrid
short_description: Sends an email with the SendGrid API
description:
  - Sends an email with a SendGrid account through their API, not through the SMTP service.
notes:
  - This module is non-idempotent because it sends an email through the external API. It is idempotent only in the case that
    the module fails.
  - Like the other notification modules, this one requires an external dependency to work. In this case, you need an active
    SendGrid account.
  - In order to use O(api_key), O(cc), O(bcc), O(attachments), O(from_name), O(html_body), and O(headers) you must C(pip install
    sendgrid).
requirements:
  - sendgrid Python library 1.6.22 or lower (Sendgrid API V2 supported)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  username:
    type: str
    description:
      - Username for logging into the SendGrid account.
      - It is only required if O(api_key) is not supplied.
  password:
    type: str
    description:
      - Password that corresponds to the username.
      - It is only required if O(api_key) is not supplied.
  from_address:
    type: str
    description:
      - The address in the "from" field for the email.
    required: true
  to_addresses:
    type: list
    elements: str
    description:
      - A list with one or more recipient email addresses.
    required: true
  subject:
    type: str
    description:
      - The desired subject for the email.
    required: true
  api_key:
    type: str
    description:
      - Sendgrid API key to use instead of username/password.
  cc:
    type: list
    elements: str
    description:
      - A list of email addresses to cc.
  bcc:
    type: list
    elements: str
    description:
      - A list of email addresses to bcc.
  attachments:
    type: list
    elements: path
    description:
      - A list of relative or explicit paths of files you want to attach (7MB limit as per SendGrid docs).
  from_name:
    type: str
    description:
      - The name you want to appear in the from field, for example V(John Doe).
  html_body:
    description:
      - Whether the body is HTML content that should be rendered.
    type: bool
    default: false
  headers:
    type: dict
    description:
      - A dict to pass on as headers.
  body:
    type: str
    description:
      - The e-mail body content.
    required: true
author: "Matt Makai (@makaimc)"
"""

EXAMPLES = r"""
- name: Send an email to a single recipient that the deployment was successful
  community.general.sendgrid:
    username: "{{ sendgrid_username }}"
    password: "{{ sendgrid_password }}"
    from_address: "ansible@mycompany.com"
    to_addresses:
      - "ops@mycompany.com"
    subject: "Deployment success."
    body: "The most recent Ansible deployment was successful."
  delegate_to: localhost

- name: Send an email to more than one recipient that the build failed
  community.general.sendgrid:
    username: "{{ sendgrid_username }}"
    password: "{{ sendgrid_password }}"
    from_address: "build@mycompany.com"
    to_addresses:
      - "ops@mycompany.com"
      - "devteam@mycompany.com"
    subject: "Build failure!."
    body: "Unable to pull source repository from Git server."
  delegate_to: localhost
"""

# =======================================
# sendgrid module support methods
#
import os
import traceback
from urllib.parse import urlencode

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

SENDGRID_IMP_ERR = None
try:
    import sendgrid

    HAS_SENDGRID = True
except ImportError:
    SENDGRID_IMP_ERR = traceback.format_exc()
    HAS_SENDGRID = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.urls import fetch_url


def post_sendgrid_api(
    module,
    username,
    password,
    from_address,
    to_addresses,
    subject,
    body,
    api_key=None,
    cc=None,
    bcc=None,
    attachments=None,
    html_body=False,
    from_name=None,
    headers=None,
):
    if not HAS_SENDGRID:
        SENDGRID_URI = "https://api.sendgrid.com/api/mail.send.json"
        AGENT = "Ansible"
        data = {"api_user": username, "api_key": password, "from": from_address, "subject": subject, "text": body}
        encoded_data = urlencode(data)
        to_addresses_api = ""
        for recipient in to_addresses:
            recipient = to_bytes(recipient, errors="surrogate_or_strict")
            to_addresses_api += f"&to[]={recipient}"
        encoded_data += to_addresses_api

        headers = {
            "User-Agent": AGENT,
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        return fetch_url(module, SENDGRID_URI, data=encoded_data, headers=headers, method="POST")
    else:
        # Remove this check when adding Sendgrid API v3 support
        if LooseVersion(sendgrid.version.__version__) > LooseVersion("1.6.22"):
            module.fail_json(msg="Please install sendgrid==1.6.22 or lower since module uses Sendgrid V2 APIs.")

        if api_key:
            sg = sendgrid.SendGridClient(api_key)
        else:
            sg = sendgrid.SendGridClient(username, password)

        message = sendgrid.Mail()
        message.set_subject(subject)

        for recip in to_addresses:
            message.add_to(recip)

        if cc:
            for recip in cc:
                message.add_cc(recip)
        if bcc:
            for recip in bcc:
                message.add_bcc(recip)

        if headers:
            message.set_headers(headers)

        if attachments:
            for f in attachments:
                name = os.path.basename(f)
                message.add_attachment(name, f)

        if from_name:
            message.set_from(f"{from_name} <{from_address}.")
        else:
            message.set_from(from_address)

        if html_body:
            message.set_html(body)
        else:
            message.set_text(body)

        return sg.send(message)


# =======================================
# Main
#


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(),
            password=dict(no_log=True),
            api_key=dict(no_log=True),
            bcc=dict(type="list", elements="str"),
            cc=dict(type="list", elements="str"),
            headers=dict(type="dict"),
            from_address=dict(required=True),
            from_name=dict(),
            to_addresses=dict(required=True, type="list", elements="str"),
            subject=dict(required=True),
            body=dict(required=True),
            html_body=dict(default=False, type="bool"),
            attachments=dict(type="list", elements="path"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["api_key", "password"], ["api_key", "username"]],
        required_together=[["username", "password"]],
    )

    username = module.params["username"]
    password = module.params["password"]
    api_key = module.params["api_key"]
    bcc = module.params["bcc"]
    cc = module.params["cc"]
    headers = module.params["headers"]
    from_name = module.params["from_name"]
    from_address = module.params["from_address"]
    to_addresses = module.params["to_addresses"]
    subject = module.params["subject"]
    body = module.params["body"]
    html_body = module.params["html_body"]
    attachments = module.params["attachments"]

    sendgrid_lib_args = [api_key, bcc, cc, headers, from_name, html_body, attachments]

    if any(lib_arg is not None for lib_arg in sendgrid_lib_args) and not HAS_SENDGRID:
        reason = (
            "when using any of the following arguments: api_key, bcc, cc, headers, from_name, html_body, attachments"
        )
        module.fail_json(msg=missing_required_lib("sendgrid", reason=reason), exception=SENDGRID_IMP_ERR)

    response, info = post_sendgrid_api(
        module,
        username,
        password,
        from_address,
        to_addresses,
        subject,
        body,
        attachments=attachments,
        bcc=bcc,
        cc=cc,
        headers=headers,
        html_body=html_body,
        api_key=api_key,
    )

    if not HAS_SENDGRID:
        if info["status"] != 200:
            module.fail_json(msg=f"unable to send email through SendGrid API: {info['msg']}")
    else:
        if response != 200:
            module.fail_json(msg=f"unable to send email through SendGrid API: {info['message']}")

    module.exit_json(msg=subject, changed=False)


if __name__ == "__main__":
    main()

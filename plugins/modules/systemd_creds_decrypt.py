#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: systemd_creds_decrypt
short_description: Systemd's systemd-creds decrypt plugin
description:
    - This module decrypts input using systemd's systemd-creds decrypt.
author:
    - Thomas Sjögren (@konstruktoid)
version_added: '10.2.0'
options:
    name:
        description:
            - The credential name to validate the embedded credential name.
        type: str
        required: false
    newline:
        description:
            - Whether to add a trailing newline character to the end of the output,
              if not present.
        type: bool
        required: false
    secret:
        description:
            - The secret to decrypt.
        type: str
        required: true
    timestamp:
        description:
            - The timestamp to use to validate the V(not-after) timestamp that
              was used during encryption.
            - Takes a timestamp specification in the format described in
              V(systemd.time(7\\)).
        type: str
        required: false
    transcode:
        description:
            - Whether to transcode the output before showing it.
        type: str
        choices: [ base64, unbase64, hex, unhex ]
        required: false
    user:
        description:
            - A user name or numeric UID when decrypting from a specific user context.
            - If set to the special string V(self) it sets the user to the user
              of the calling process.
            - Requires C(systemd) 256 or later.
        type: str
        required: false
notes:
  - C(systemd-creds) requires C(systemd) 250 or later.
"""

EXAMPLES = """
- name: Decrypt secret
  community.general.systemd_creds_decrypt:
    name: db
    secret: "WhQZht+JQJax1aZemmGLxmAAAA..."
  register: decrypted_secret

- name: Print the decrypted secret
  ansible.builtin.debug:
    msg: "{{ decrypted_secret }}"
"""


from ansible.module_utils.basic import AnsibleModule


def main():
    """Encrypt secret using systemd-creds."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False),
            newline=dict(type="bool", required=False),
            secret=dict(type="str", required=True, no_log=True),
            timestamp=dict(type="str", required=False),
            transcode=dict(
                type="str",
                choices=["base64", "unbase64", "hex", "unhex"],
                required=False,
            ),
            user=dict(type="str", required=False),
        ),
        supports_check_mode=True,
    )

    cmd = module.get_bin_path("systemd-creds", required=True)

    name = module.params["name"]
    newline = module.params["newline"]
    secret = module.params["secret"]
    timestamp = module.params["timestamp"]
    transcode = module.params["transcode"]
    user = module.params["user"]

    decrypt_cmd = [cmd, "decrypt"]
    if name:
        decrypt_cmd.append("--name=" + name)
    else:
        decrypt_cmd.append("--name=")
    if newline:
        decrypt_cmd.append("--newline=" + newline)
    else:
        decrypt_cmd.append("--newline=auto")
    if timestamp:
        decrypt_cmd.append("--timestamp=" + timestamp)
    if transcode:
        decrypt_cmd.append("--transcode=" + transcode)
    if user:
        decrypt_cmd.append("--uid=" + user)
    decrypt_cmd.extend(["-", "-"])

    rc, stdout, stderr = module.run_command(decrypt_cmd, data=secret)

    module.exit_json(
        changed=False,
        msg=stdout,
        rc=rc,
        stderr=stderr,
    )


if __name__ == "__main__":
    main()

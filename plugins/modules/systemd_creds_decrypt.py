#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: systemd_creds_decrypt
short_description: C(systemd)'s C(systemd-creds decrypt) plugin
description:
  - This module decrypts input using C(systemd)'s C(systemd-creds decrypt).
author:
  - Thomas Sjögren (@konstruktoid)
version_added: '10.2.0'
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: N/A
    details:
      - This action does not modify state.
options:
  name:
    description:
      - The credential name to validate the embedded credential name.
    type: str
    required: false
  newline:
    description:
      - Whether to add a trailing newline character to the end of the output, if not present.
    type: bool
    required: false
    default: false
  secret:
    description:
      - The secret to decrypt.
    type: str
    required: true
  timestamp:
    description:
      - The timestamp to use to validate the V(not-after) timestamp that was used during encryption.
      - Takes a timestamp specification in the format described in V(systemd.time(7\)).
    type: str
    required: false
  transcode:
    description:
      - Whether to transcode the output before returning it.
    type: str
    choices: [base64, unbase64, hex, unhex]
    required: false
  user:
    description:
      - A user name or numeric UID when decrypting from a specific user context.
      - If set to the special string V(self) it sets the user to the user of the calling process.
      - Requires C(systemd) 256 or later.
    type: str
    required: false
notes:
  - C(systemd-creds) requires C(systemd) 250 or later.
"""

EXAMPLES = r"""
- name: Decrypt secret
  community.general.systemd_creds_decrypt:
    name: db
    secret: "WhQZht+JQJax1aZemmGLxmAAAA..."
  register: decrypted_secret

- name: Print the decrypted secret
  ansible.builtin.debug:
    msg: "{{ decrypted_secret }}"
"""

RETURN = r"""
value:
  description:
    - The decrypted secret.
    - Note that Ansible only supports returning UTF-8 encoded strings. If the decrypted secret is binary data, or a string
      encoded in another way, use O(transcode=base64) or O(transcode=hex) to circument this restriction. You then need to
      decode the data when using it, for example using the P(ansible.builtin.b64decode#filter) filter.
  type: str
  returned: always
  sample: "access_token"
"""


from ansible.module_utils.basic import AnsibleModule


def main():
    """Decrypt secret using systemd-creds."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            newline=dict(type="bool", default=False),
            secret=dict(type="str", required=True, no_log=True),
            timestamp=dict(type="str"),
            transcode=dict(type="str", choices=["base64", "unbase64", "hex", "unhex"]),
            user=dict(type="str"),
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
    decrypt_cmd.append("--newline=" + ("yes" if newline else "no"))
    if timestamp:
        decrypt_cmd.append("--timestamp=" + timestamp)
    if transcode:
        decrypt_cmd.append("--transcode=" + transcode)
    if user:
        decrypt_cmd.append("--uid=" + user)
    decrypt_cmd.extend(["-", "-"])

    rc, stdout, stderr = module.run_command(decrypt_cmd, data=secret, binary_data=True)

    module.exit_json(
        changed=False,
        value=stdout,
        rc=rc,
        stderr=stderr,
    )


if __name__ == "__main__":
    main()
